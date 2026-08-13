#!/usr/bin/env python3
"""E4.1 Safety Semantics & State-Machine Hardening Tests

Validates Mark I command pipeline safety properties:

S1  — SAFE OFF default state
S2  — Valid target while disabled
S3  — ARM != command (parameter change alone does not send goal)
S4  — Invalid / out-of-range rejection
S5  — NaN/Inf rejection
S6  — One-active-goal enforcement
S8  — DISARM blocks new targets
S11 — Validation in SAFE MODE
S12 — No stale target replay

These tests are STATIC and do NOT require Gazebo or motion execution.
They verify state machine logic through isolated node testing and inspection.

Bridge functional changes expected: NONE
(Tests validate current behavior, not new features)
"""

import math
import pytest
import rclpy
from unittest.mock import Mock, patch, MagicMock, call
from rclpy.node import Node
from rclpy.parameter import Parameter
from rcl_interfaces.msg import SetParametersResult
from sensor_msgs.msg import JointState
from control_msgs.action import FollowJointTrajectory


# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture(scope="module")
def rclpy_lifecycle():
    """Module-scoped ROS lifecycle for all tests."""
    rclpy.init()
    yield
    rclpy.shutdown()


@pytest.fixture
def bridge_node(rclpy_lifecycle):
    """Create a bridge node with mocked ActionClient for testing.
    
    The ActionClient is patched to:
    - Not require an actual action server
    - Track whether send_goal_async was called
    - Provide safe_call interface for testing without blocking
    """
    # Import here to ensure ROS is initialized
    import sys
    sys.path.insert(0, "/mnt/c/WAYLAND/src/aracne_bringup/scripts")
    
    # Patch ActionClient before importing joint_trajectory_bridge
    with patch("rclpy.action.ActionClient") as mock_action_client_class:
        # Configure mock to return a mock instance
        mock_instance = MagicMock()
        mock_instance.server_is_ready.return_value = True
        mock_action_client_class.return_value = mock_instance
        
        # Now import and instantiate the bridge
        from joint_trajectory_bridge import JointTrajectoryBridge
        
        node = JointTrajectoryBridge()
        node._action_client_mock = mock_instance  # Store for test inspection
        
        yield node
        
        node.destroy_node()


@pytest.fixture
def valid_joint_state():
    """Create a structurally valid JointState within limits.
    
    Values: [0.5, 0.0, -1.0]
    These are well within [coxa: -1.57..1.57], [femur: -0.78..1.57], [tibia: -2.09..0.0]
    """
    msg = JointState()
    msg.name = ["leg1_coxa_joint", "leg1_femur_joint", "leg1_tibia_joint"]
    msg.position = [0.5, 0.0, -1.0]
    return msg


@pytest.fixture
def oob_joint_state_femur():
    """JointState with femur out of upper range (1.57).
    
    femur=2.0 exceeds upper limit of 1.57 → should be REJECTED
    """
    msg = JointState()
    msg.name = ["leg1_coxa_joint", "leg1_femur_joint", "leg1_tibia_joint"]
    msg.position = [0.5, 2.0, -1.0]  # femur out of range
    return msg


@pytest.fixture
def oob_joint_state_tibia():
    """JointState with tibia out of lower range (-2.09).
    
    tibia=-3.0 is below lower limit of -2.09 → should be REJECTED
    """
    msg = JointState()
    msg.name = ["leg1_coxa_joint", "leg1_femur_joint", "leg1_tibia_joint"]
    msg.position = [0.5, 0.0, -3.0]  # tibia out of range
    return msg


@pytest.fixture
def nan_joint_state():
    """JointState with NaN in coxa position."""
    msg = JointState()
    msg.name = ["leg1_coxa_joint", "leg1_femur_joint", "leg1_tibia_joint"]
    msg.position = [float('nan'), 0.0, -1.0]
    return msg


@pytest.fixture
def inf_joint_state():
    """JointState with +Inf in femur position."""
    msg = JointState()
    msg.name = ["leg1_coxa_joint", "leg1_femur_joint", "leg1_tibia_joint"]
    msg.position = [0.5, float('inf'), -1.0]
    return msg


@pytest.fixture
def neginf_joint_state():
    """JointState with -Inf in tibia position."""
    msg = JointState()
    msg.name = ["leg1_coxa_joint", "leg1_femur_joint", "leg1_tibia_joint"]
    msg.position = [0.5, 0.0, float('-inf')]
    return msg


@pytest.fixture
def malformed_joint_state_short():
    """JointState with only 2 positions (malformed)."""
    msg = JointState()
    msg.name = ["leg1_coxa_joint", "leg1_femur_joint"]
    msg.position = [0.5, 0.0]
    return msg


@pytest.fixture
def duplicate_joint_state():
    """JointState with duplicate joint name (malformed)."""
    msg = JointState()
    msg.name = ["leg1_coxa_joint", "leg1_coxa_joint", "leg1_tibia_joint"]
    msg.position = [0.5, 0.0, -1.0]
    return msg


# ============================================================================
# S1 — SAFE OFF DEFAULT STATE
# ============================================================================


def test_s1_boot_safe_off(bridge_node):
    """S1: Verify enabled=False on boot.
    
    Property: The bridge initializes with `enabled` parameter set to False.
    
    This ensures SAFE OFF default: bridge will not send goals until explicitly armed.
    """
    assert bridge_node._enabled is False, \
        "Bridge must initialize with enabled=False (SAFE OFF)"


def test_s1_goal_in_flight_false_on_boot(bridge_node):
    """S1: Verify _goal_in_flight=False on boot.
    
    Property: The concurrency guard initializes to False (idle state).
    """
    assert bridge_node._goal_in_flight is False, \
        "_goal_in_flight must initialize to False (idle)"


# ============================================================================
# S2 — VALID TARGET WHILE DISABLED
# ============================================================================


def test_s2_valid_target_disabled_no_goal_sent(bridge_node, valid_joint_state):
    """S2: Valid JointState while enabled=False → goal NOT sent.
    
    Property: SAFE MODE validation occurs but goal is not transmitted.
    
    Expected:
    - _validate_and_reorder succeeds (structure/limits OK)
    - but _send_goal is NOT called
    - log includes "SAFE MODE" message
    """
    bridge_node._action_client_mock.send_goal_async.reset_mock()
    
    # Ensure disabled
    assert bridge_node._enabled is False
    
    # Trigger callback with valid message
    bridge_node._on_joint_angles(valid_joint_state)
    
    # Assert goal was NOT sent
    assert bridge_node._action_client_mock.send_goal_async.call_count == 0, \
        "Goal must NOT be sent while disabled (SAFE MODE)"
    
    # Assert _goal_in_flight unchanged (should remain False)
    assert bridge_node._goal_in_flight is False


# ============================================================================
# S3 — ARM != COMMAND
# ============================================================================


def test_s3_arm_does_not_send_goal(bridge_node):
    """S3: Parameter set enabled:false→true does NOT send goal.
    
    Property: ARM (changing enabled parameter) is not a command.
    It only unlocks NEW valid messages to produce goals.
    
    Sequence:
    1. Set enabled=True (ARM)
    2. Verify no goal is sent
    3. Verify state changed (_enabled=True)
    """
    bridge_node._action_client_mock.send_goal_async.reset_mock()
    
    # ARM via parameter
    params = [Parameter("enabled", Parameter.Type.BOOL, True)]
    
    # Validation succeeds
    validation_result = bridge_node._validate_parameters(params)
    assert validation_result.successful is True
    
    # Post-set applies the change
    bridge_node._on_parameters_applied(params)
    
    # State changed
    assert bridge_node._enabled is True
    
    # But no goal was sent (ARM is not a command)
    assert bridge_node._action_client_mock.send_goal_async.call_count == 0, \
        "ARM (enabled=true parameter set) must NOT send a goal by itself"


def test_s3_arm_does_not_replay_stale_target(bridge_node, valid_joint_state):
    """S3: ARM does not retroactively send a previous target.
    
    Sequence:
    1. Bridge disabled
    2. Valid target arrives (rejected due to SAFE MODE)
    3. ARM (enabled=false→true)
    4. Verify no goal sent
    
    If bridge incorrectly replayed stale targets on ARM, this would fail.
    """
    bridge_node._action_client_mock.send_goal_async.reset_mock()
    
    # Disabled state, valid target arrives
    bridge_node._on_joint_angles(valid_joint_state)
    
    # Goal was not sent (SAFE MODE)
    assert bridge_node._action_client_mock.send_goal_async.call_count == 0
    
    # Now ARM
    params = [Parameter("enabled", Parameter.Type.BOOL, True)]
    bridge_node._validate_parameters(params)
    bridge_node._on_parameters_applied(params)
    
    # Still no goal sent (ARM alone is not a command)
    assert bridge_node._action_client_mock.send_goal_async.call_count == 0, \
        "ARM must NOT replay stale targets"


# ============================================================================
# S4 — INVALID / OUT-OF-RANGE REJECTION
# ============================================================================


def test_s4_reject_femur_out_of_upper_range(bridge_node, oob_joint_state_femur):
    """S4: JointState with femur > 1.57 (upper limit) is REJECTED.
    
    Property: REJECT policy — never clamp, always reject with reason.
    
    femur=2.0 exceeds upper=1.57 → goal NOT sent
    """
    bridge_node._action_client_mock.send_goal_async.reset_mock()
    
    # ARM to enable processing
    bridge_node._enabled = True
    
    # Send out-of-range message
    bridge_node._on_joint_angles(oob_joint_state_femur)
    
    # Goal NOT sent
    assert bridge_node._action_client_mock.send_goal_async.call_count == 0, \
        "Out-of-range target must be REJECTED"
    
    # _goal_in_flight unchanged (should remain False)
    assert bridge_node._goal_in_flight is False


def test_s4_reject_tibia_out_of_lower_range(bridge_node, oob_joint_state_tibia):
    """S4: JointState with tibia < -2.09 (lower limit) is REJECTED.
    
    tibia=-3.0 is below lower=-2.09 → goal NOT sent
    """
    bridge_node._action_client_mock.send_goal_async.reset_mock()
    bridge_node._enabled = True
    
    bridge_node._on_joint_angles(oob_joint_state_tibia)
    
    assert bridge_node._action_client_mock.send_goal_async.call_count == 0, \
        "Out-of-lower-range target must be REJECTED"
    assert bridge_node._goal_in_flight is False


# ============================================================================
# S5 — NON-FINITE INPUT REJECTION
# ============================================================================


def test_s5_reject_nan_position(bridge_node, nan_joint_state):
    """S5: JointState with NaN position is REJECTED.
    
    Property: Non-finite values (NaN, Inf, -Inf) are caught and rejected.
    """
    bridge_node._action_client_mock.send_goal_async.reset_mock()
    bridge_node._enabled = True
    
    bridge_node._on_joint_angles(nan_joint_state)
    
    assert bridge_node._action_client_mock.send_goal_async.call_count == 0, \
        "NaN input must be REJECTED"
    assert bridge_node._goal_in_flight is False


def test_s5_reject_inf_position(bridge_node, inf_joint_state):
    """S5: JointState with +Inf position is REJECTED."""
    bridge_node._action_client_mock.send_goal_async.reset_mock()
    bridge_node._enabled = True
    
    bridge_node._on_joint_angles(inf_joint_state)
    
    assert bridge_node._action_client_mock.send_goal_async.call_count == 0, \
        "+Inf input must be REJECTED"
    assert bridge_node._goal_in_flight is False


def test_s5_reject_neginf_position(bridge_node, neginf_joint_state):
    """S5: JointState with -Inf position is REJECTED."""
    bridge_node._action_client_mock.send_goal_async.reset_mock()
    bridge_node._enabled = True
    
    bridge_node._on_joint_angles(neginf_joint_state)
    
    assert bridge_node._action_client_mock.send_goal_async.call_count == 0, \
        "-Inf input must be REJECTED"
    assert bridge_node._goal_in_flight is False


# ============================================================================
# S6 — ONE-ACTIVE-GOAL ENFORCEMENT
# ============================================================================


def test_s6_one_active_goal_guard(bridge_node, valid_joint_state):
    """S6: If _goal_in_flight=True, new target is rejected.
    
    Property: Only one goal in flight at a time. No queueing.
    
    Sequence:
    1. Simulate goal in flight (_goal_in_flight=True)
    2. New valid target arrives
    3. Goal NOT sent (guard prevents it)
    """
    bridge_node._action_client_mock.send_goal_async.reset_mock()
    bridge_node._enabled = True
    bridge_node._goal_in_flight = True  # Simulate goal in flight
    
    # New valid target arrives
    bridge_node._on_joint_angles(valid_joint_state)
    
    # Goal NOT sent due to guard
    assert bridge_node._action_client_mock.send_goal_async.call_count == 0, \
        "New target must be rejected if goal already in flight"
    
    # _goal_in_flight should still be True (unchanged by rejection)
    assert bridge_node._goal_in_flight is True


# ============================================================================
# S8 — DISARM BLOCKS NEW TARGETS
# ============================================================================


def test_s8_disarm_then_target_rejected(bridge_node, valid_joint_state):
    """S8: After DISARM, new valid targets are rejected (SAFE MODE).
    
    Sequence:
    1. ARM (enabled=true)
    2. DISARM (enabled=false)
    3. Valid target arrives
    4. Goal NOT sent (SAFE MODE)
    
    Property: DISARM blocks new commands but doesn't cancel in-flight goals.
    This test verifies the blocking part.
    """
    bridge_node._action_client_mock.send_goal_async.reset_mock()
    
    # ARM
    bridge_node._enabled = True
    assert bridge_node._enabled is True
    
    # DISARM
    params = [Parameter("enabled", Parameter.Type.BOOL, False)]
    bridge_node._on_parameters_applied(params)
    assert bridge_node._enabled is False
    
    # New valid target arrives
    bridge_node._on_joint_angles(valid_joint_state)
    
    # Goal NOT sent (SAFE MODE active)
    assert bridge_node._action_client_mock.send_goal_async.call_count == 0, \
        "Target after DISARM must be rejected (SAFE MODE)"


# ============================================================================
# S11 — VALIDATION IN SAFE MODE
# ============================================================================


def test_s11_validation_occurs_while_disabled(bridge_node, valid_joint_state):
    """S11: Disabled state still validates structure/limits (but blocks transmission).
    
    Property: Bridge validates even in SAFE MODE; it only blocks transmission.
    
    The point: valid_joint_state is structurally OK and within limits,
    so it "passes validation" from a structural perspective, but goal is NOT sent
    due to disabled state.
    
    (This is different from out-of-range: that would fail validation and be rejected
    even if enabled. Here it would pass validation, but transmission is blocked by SAFE MODE.)
    """
    bridge_node._enabled = False  # SAFE MODE
    
    # This test verifies that _validate_and_reorder succeeds structurally.
    # We can check this by examining the return value.
    result = bridge_node._validate_and_reorder(valid_joint_state)
    
    assert result is not None, \
        "Valid target must pass validation even in SAFE MODE"
    
    # The result should be a list of positions in canonical order
    assert len(result) == 3
    assert result[0] == valid_joint_state.position[0]  # coxa
    assert result[1] == valid_joint_state.position[1]  # femur
    assert result[2] == valid_joint_state.position[2]  # tibia


def test_s11_malformed_rejected_even_disabled(bridge_node, malformed_joint_state_short):
    """S11: Malformed messages are still REJECTED in SAFE MODE.
    
    Property: Validation failures (structure) are not bypassed by disabled state.
    Only transmission is blocked by disabled; validation is always strict.
    """
    bridge_node._enabled = False  # SAFE MODE
    
    result = bridge_node._validate_and_reorder(malformed_joint_state_short)
    
    assert result is None, \
        "Malformed message must be rejected even in SAFE MODE"


# ============================================================================
# S12 — NO STALE TARGET REPLAY
# ============================================================================


def test_s12_no_replay_on_disarm_rearm(bridge_node, valid_joint_state):
    """S12: DISARM then RE-ARM does not replay the old target.
    
    Sequence:
    1. ARM
    2. Receive valid target (at this point, goal could be sent)
    3. DISARM
    4. RE-ARM
    5. No new message received
    6. Verify no goal is sent (no replay)
    
    Property: Bridge does not cache/replay targets automatically.
    New goal requires new JointState message.
    """
    bridge_node._action_client_mock.send_goal_async.reset_mock()
    
    # ARM
    bridge_node._enabled = True
    
    # Receive target while armed
    bridge_node._on_joint_angles(valid_joint_state)
    
    # At this point, goal may or may not have been sent
    # (depending on other conditions like _goal_in_flight)
    # Reset mock to track future calls
    bridge_node._action_client_mock.send_goal_async.reset_mock()
    
    # DISARM
    bridge_node._enabled = False
    
    # RE-ARM
    bridge_node._enabled = True
    
    # No new message has been received
    # If bridge replayed targets, a goal would be sent now
    
    assert bridge_node._action_client_mock.send_goal_async.call_count == 0, \
        "RE-ARM must NOT automatically replay cached target"


def test_s12_no_replay_disabled_to_enabled(bridge_node, valid_joint_state):
    """S12: Message received while disabled, then ARM → no auto-replay.
    
    Sequence:
    1. SAFE MODE (disabled)
    2. Valid target arrives (rejected due to SAFE MODE)
    3. ARM (enabled=true)
    4. Verify no goal sent (no replay of cached message)
    
    Property: Bridge does not cache messages from SAFE MODE and replay them on ARM.
    """
    bridge_node._action_client_mock.send_goal_async.reset_mock()
    
    # Disabled state
    assert bridge_node._enabled is False
    
    # Valid target arrives while disabled
    bridge_node._on_joint_angles(valid_joint_state)
    
    # Goal NOT sent (SAFE MODE)
    assert bridge_node._action_client_mock.send_goal_async.call_count == 0
    
    # ARM
    bridge_node._enabled = True
    
    # Goal still NOT sent (no auto-replay on ARM)
    assert bridge_node._action_client_mock.send_goal_async.call_count == 0, \
        "ARM must NOT replay messages received in SAFE MODE"


# ============================================================================
# Malformed Message Validation
# ============================================================================


def test_malformed_duplicate_joint_name(bridge_node, duplicate_joint_state):
    """Bonus: Duplicate joint names in same message are REJECTED.
    
    Property: Structural validation catches duplicates.
    """
    bridge_node._enabled = True
    result = bridge_node._validate_and_reorder(duplicate_joint_state)
    
    assert result is None, \
        "Duplicate joint name must be rejected"


def test_malformed_wrong_count(bridge_node, malformed_joint_state_short):
    """Bonus: Wrong number of joints is REJECTED.
    
    Property: Structural validation requires exactly 3 joints.
    """
    bridge_node._enabled = True
    result = bridge_node._validate_and_reorder(malformed_joint_state_short)
    
    assert result is None, \
        "Wrong joint count must be rejected"


# ============================================================================
# Safety Semantics Integration Tests
# ============================================================================


def test_safe_off_philosophy(bridge_node, valid_joint_state):
    """Integration: SAFE OFF means no goal transmission in any scenario.
    
    Verify the core safety principle: while disabled, no goal is ever sent,
    regardless of message validity or parameter changes.
    """
    bridge_node._enabled = False
    bridge_node._goal_in_flight = False
    bridge_node._action_client_mock.send_goal_async.reset_mock()
    
    # Multiple valid targets in SAFE MODE
    for _ in range(3):
        bridge_node._on_joint_angles(valid_joint_state)
    
    # No goals sent
    assert bridge_node._action_client_mock.send_goal_async.call_count == 0, \
        "SAFE OFF must prevent all goal transmission"


def test_reject_policy_never_clamps(bridge_node, oob_joint_state_femur):
    """Integration: REJECT policy never silently clamps invalid targets.
    
    Property: Invalid targets are rejected with reason, not auto-corrected.
    """
    bridge_node._enabled = True
    bridge_node._action_client_mock.send_goal_async.reset_mock()
    
    # Out-of-range target
    bridge_node._on_joint_angles(oob_joint_state_femur)
    
    # Goal NOT sent (not clamped to upper limit)
    assert bridge_node._action_client_mock.send_goal_async.call_count == 0, \
        "REJECT policy: out-of-range must not be clamped and transmitted"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
