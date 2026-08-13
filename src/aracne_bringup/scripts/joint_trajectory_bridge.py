#!/usr/bin/env python3
"""joint_trajectory_bridge

Command adapter between the IK output (desired joint angles) and the
JointTrajectoryController via the FollowJointTrajectory action.

Input : /aracne/leg/joint_angles   (sensor_msgs/msg/JointState)
        .name / .position are treated as DESIRED targets from IK,
        NOT as measured feedback. The real feedback stays on /joint_states.
Output: /joint_trajectory_controller/follow_joint_trajectory
        (control_msgs/action/FollowJointTrajectory)

Safety:
  - `enabled` defaults to False. While False the node only validates and
    logs; it NEVER sends an action goal (SAFE MODE).
  - One active goal at a time is allowed. No queue / preemption / cancel.
  - Targets outside the known joint limits are REJECTED (never clamped).
"""

import math

import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from rclpy.action import ActionClient
from rcl_interfaces.msg import SetParametersResult
from action_msgs.msg import GoalStatus
from control_msgs.action import FollowJointTrajectory
from sensor_msgs.msg import JointState
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

# ---------------------------------------------------------------------------
# Central table - not an independent source of truth.
#
# Mirror of the current Mark I URDF joint limits
# (as forwarded by joint_limits_* xacro args in mark1.launch.py).
# Units: radians.
# Not an independent source of truth.
# ---------------------------------------------------------------------------
JOINT_LIMITS = {
    "leg1_coxa_joint": (-1.57, 1.57),
    "leg1_femur_joint": (-0.78, 1.57),
    "leg1_tibia_joint": (-2.09, 0.0),
}

# Explicit command order (do not rely on msg.name ordering).
CANONICAL_JOINT_NAMES = [
    "leg1_coxa_joint",
    "leg1_femur_joint",
    "leg1_tibia_joint",
]

# Re-log interval for SAFE MODE "valid target but disabled" (Keeps log useful
# without flooding at the 1 Hz teleop rate).
_SAFE_LOG_INTERVAL_SEC = 10.0


class JointTrajectoryBridge(Node):
    def __init__(self):
        super().__init__("joint_trajectory_bridge")

        # -- Parameters ----------------------------------------------------
        self.declare_parameter("enabled", False)
        self.declare_parameter("trajectory_duration", 2.0)
        self.declare_parameter(
            "controller_action",
            "/joint_trajectory_controller/follow_joint_trajectory",
        )

        self._enabled = self.get_parameter("enabled").value
        self._trajectory_duration = self.get_parameter("trajectory_duration").value
        self._controller_action_name = self.get_parameter("controller_action").value

        # -- Runtime software arm/disarm ----------------------------------
        # default stays False (SAFE OFF). Validation and state synchronization
        # are split: on-set only decides whether the change is acceptable;
        # post-set updates the internal state AFTER the change is accepted.
        # ARM is NOT a command: it only allows a NEW valid JointState received
        # after the transition to produce a goal.
        self.add_on_set_parameters_callback(self._validate_parameters)
        self.add_post_set_parameters_callback(self._on_parameters_applied)

        # -- Action client -------------------------------------------------
        # Created eagerly so that by the time enabled is flipped to true the
        # client exists. It does NOT wait/block while disabled.
        self._action_client = ActionClient(
            self, FollowJointTrajectory, self._controller_action_name
        )

        # -- Subscriber ----------------------------------------------------
        self._subscriber = self.create_subscription(
            JointState,
            "/aracne/leg/joint_angles",
            self._on_joint_angles,
            10,
        )

        # -- Concurrency state --------------------------------------------
        # IDLE -> (goal request in flight) -> GOAL_PENDING/ACTIVE -> result
        # -> back to IDLE. No queueing / no preemption.
        self._goal_in_flight = False
        self._last_safe_log_time = None

        self.get_logger().info(
            f"joint_trajectory_bridge started | enabled={self._enabled} | "
            f"trajectory_duration={self._trajectory_duration:.2f} | "
            f"action={self._controller_action_name}"
        )

    # ------------------------------------------------------------------
    # Runtime parameter handling (ARM/DISARM)
    # ------------------------------------------------------------------
    def _validate_parameters(self, params):
        """Only decide whether the parameter change may be accepted."""
        for p in params:
            if p.name == "enabled" and p.type_ != Parameter.Type.BOOL:
                return SetParametersResult(
                    successful=False,
                    reason="enabled must be a boolean (true/false)",
                )
        return SetParametersResult(successful=True)

    def _on_parameters_applied(self, params):
        """Synchronize internal state only after the change was accepted."""
        for p in params:
            if p.name != "enabled":
                continue
            new_value = bool(p.value)
            if new_value == self._enabled:
                continue
            self._enabled = new_value
            self.get_logger().warn(
                "command bridge ARMED" if self._enabled
                else "command bridge DISARMED"
            )

    # ------------------------------------------------------------------
    # Main entry
    # ------------------------------------------------------------------
    def _on_joint_angles(self, msg: JointState):
        positions = self._validate_and_reorder(msg)
        if positions is None:
            return  # rejected (logged by the validator)

        if not self._enabled:
            # SAFE MODE: never send a goal. Log without flooding.
            self._log_safe_mode_valid_target()
            return

        if self._goal_in_flight:
            self.get_logger().warn(
                "valid joint target received but a goal is already in flight "
                "(skipping - one active goal at a time)"
            )
            return

        if self._trajectory_duration <= 0.0:
            self.get_logger().error(
                f"trajectory_duration must be > 0 "
                f"(got {self._trajectory_duration:.2f}); goal NOT sent"
            )
            return

        # Action server availability (non-destructive, no blocking loop).
        if not self._action_client.server_is_ready():
            self.get_logger().warn(
                f"action server not available yet "
                f"({self._controller_action_name}); goal NOT sent"
            )
            return

        self._send_goal(positions)

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    def _validate_and_reorder(self, msg: JointState):
        """Validate structure + ranges, then return positions in canonical order.

        Rejects (None) with a clear log whenever the message is malformed or a
        target falls outside the joint limits. Never clamps.
        """
        if len(msg.name) != 3 or len(msg.position) != 3:
            self.get_logger().error(
                f"invalid JointState: expected exactly 3 joint names and 3 "
                f"positions (got {len(msg.name)} names, "
                f"{len(msg.position)} positions); goal NOT sent"
            )
            return None

        seen = set()
        positions = {}
        for name, value in zip(msg.name, msg.position):
            if name in seen:
                self.get_logger().error(
                    f"invalid JointState: duplicated joint name '{name}'; "
                    f"goal NOT sent"
                )
                return None
            seen.add(name)

            if name not in JOINT_LIMITS:
                self.get_logger().error(
                    f"invalid JointState: unknown joint '{name}'; "
                    f"expected {CANONICAL_JOINT_NAMES}; goal NOT sent"
                )
                return None

            if not math.isfinite(value):
                self.get_logger().error(
                    f"invalid JointState: non-finite/NaN/Inf position for "
                    f"'{name}' (value={value}); goal NOT sent"
                )
                return None

            positions[name] = value

        # Check all expected joints present (covered above by unknown check,
        # but keep explicit for clarity).
        missing = [n for n in CANONICAL_JOINT_NAMES if n not in positions]
        if missing:
            self.get_logger().error(
                f"invalid JointState: missing joints {missing}; goal NOT sent"
            )
            return None

        # Range validation (REJECT, never clamp).
        ordered = []
        for name in CANONICAL_JOINT_NAMES:
            value = positions[name]
            lower, upper = JOINT_LIMITS[name]
            if not (lower <= value <= upper):
                self.get_logger().error(
                    f"joint target OUT OF RANGE for '{name}': value="
                    f"{value:.4f} rad, limit=[{lower:.4f}, {upper:.4f}]; "
                    f"REJECTED (goal NOT sent)"
                )
                return None
            ordered.append(value)

        return ordered

    # ------------------------------------------------------------------
    # Goal sending
    # ------------------------------------------------------------------
    def _send_goal(self, ordered_positions):
        goal = FollowJointTrajectory.Goal()
        goal.trajectory = JointTrajectory()
        goal.trajectory.joint_names = list(CANONICAL_JOINT_NAMES)

        point = JointTrajectoryPoint()
        point.positions = ordered_positions

        sec = int(self._trajectory_duration)
        nsec = int((self._trajectory_duration - sec) * 1e9)
        point.time_from_start.sec = sec
        point.time_from_start.nanosec = nsec

        goal.trajectory.points.append(point)

        # Mark in-flight BEFORE send_goal_async so the window between
        # send_goal_async and goal_response counts as "in flight".
        self._goal_in_flight = True

        pos_str = ", ".join(f"{v:.4f}" for v in ordered_positions)
        self.get_logger().info(
            f"sending FollowJointTrajectory goal: target positions ["
            f"{pos_str}] (coxa, femur, tibia), "
            f"duration={self._trajectory_duration:.2f}s"
        )

        future = self._action_client.send_goal_async(
            goal, feedback_callback=self._on_feedback
        )
        future.add_done_callback(self._on_goal_response)

    # ------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------
    def _on_goal_response(self, future):
        try:
            goalfuture = future.result()
        except Exception as exc:  # keep ONE-ACTIVE-GOAL consistent on errors
            self.get_logger().error(
                f"exception while waiting for goal response: {exc}; "
                f"releasing in-flight state"
            )
            self._goal_in_flight = False
            return
        # `goalfuture` is AcceptedGoal/Rejected (the response of the server).
        if goalfuture is None:
            self.get_logger().error(
                "action server did not respond to goal (server likely "
                "unavailable); releasing in-flight state"
            )
            self._goal_in_flight = False
            return

        if not goalfuture.accepted:
            self.get_logger().error(
                "goal REJECTED by action server; releasing in-flight state"
            )
            self._goal_in_flight = False
            return

        self.get_logger().info("goal ACCEPTED by action server; waiting for result")
        result_future = goalfuture.get_result_async()
        result_future.add_done_callback(self._on_goal_result)

    def _on_goal_result(self, future):
        # Release the in-flight guard first so any error below never leaves
        # the bridge stuck in GOAL_PENDING/ACTIVE.
        self._goal_in_flight = False
        try:
            result = future.result()
        except Exception as exc:
            self.get_logger().error(
                f"exception while retrieving action result: {exc}; "
                f"releasing in-flight state"
            )
            return
        if result is None:
            self.get_logger().error("unexpected: no action result available")
            return
        status = result.status
        # status codes (GoalStatus): STATUS_SUCCEEDED=4, STATUS_ABORTED=6,
        # STATUS_CANCELED=5
        if status == GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().info("goal SUCCEEDED")
        elif status == GoalStatus.STATUS_ABORTED:
            self.get_logger().error("goal ABORTED by controller")
        elif status == GoalStatus.STATUS_CANCELED:
            self.get_logger().warn("goal CANCELED")
        else:
            self.get_logger().warn(
                f"goal finished with status code {status}"
            )

    def _on_feedback(self, _feedback_msg):
        # Not needed at this stage; feedback is not consumed to drive motion.
        pass

    # ------------------------------------------------------------------
    # SAFE MODE logging (rate-limited simply)
    # ------------------------------------------------------------------
    def _log_safe_mode_valid_target(self):
        now = self.get_clock().now().nanoseconds / 1e9
        if self._last_safe_log_time is None:
            self._last_safe_log_time = now
            self.get_logger().warn(
                "valid joint target received but command bridge is DISABLED "
                "(SAFE MODE) - no goal sent"
            )
            return
        if (now - self._last_safe_log_time) >= _SAFE_LOG_INTERVAL_SEC:
            self._last_safe_log_time = now
            self.get_logger().warn(
                "valid joint target received but command bridge is DISABLED "
                "(SAFE MODE) - no goal sent"
            )


def main(args=None):
    rclpy.init(args=args)
    node = JointTrajectoryBridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
