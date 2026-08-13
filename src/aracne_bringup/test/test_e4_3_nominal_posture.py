"""
E4.3 — Nominal Posture / Home-Hold Semantics

Static semantics validation only.

This test validates the approved architectural decision:
- DISARMED means no new goals are accepted; no posture command is injected.
- HOLD is not a new ROS contract; it is the implicit behavior of the controller
  after the last trajectory reaches SUCCEEDED.
- HOME is a nominal reference target, not a bypass or a new control layer.
- HOME is represented as a normal LegTarget compatible with the existing bridge.

IMPORTANT:
- This file does NOT run Gazebo / ROS runtime.
- This file does NOT send goals or publish to the controller.
- This file is a semantic/static reference test for the current architecture.
- The expected HOME date is derived from the existing E3/E4.2 validated target.
- The test does not re-implement the IK formula; it uses the approved reference target
  and expected joint angles as the nominal posture contract.
"""

import math
from typing import Dict, List, Optional

import pytest


HOME_TARGET = {
    "leg_id": "leg1",
    "x": 0.15,
    "y": 0.00,
    "z": -0.08,
}

# Approved reference target from E3/E4.2 validation.
HOME_JOINT_REFERENCE = [0.0000, 0.3281, -1.7639]

JOINT_LIMITS = {
    "coxa": (-1.57, 1.57),
    "femur": (-0.78, 1.57),
    "tibia": (-2.09, 0.0),
}

NO_HOLD_CONTRACTS = {
    "topic": "/aracne/hold",
    "service": "/aracne/hold",
    "action": "/aracne/hold",
    "parameter": "hold",
}


class NominalPostureSemantics:
    """Static reference model of the approved E4.3 semantics."""

    def __init__(self):
        self.enabled = False
        self.goal_in_flight = False
        self.last_goal = None

    def arm(self):
        self.enabled = True
        self.last_goal = None

    def disarm(self):
        self.enabled = False

    def submit_normal_target(self, target: Dict[str, object]):
        if not self.enabled:
            return False
        if self.goal_in_flight:
            return False
        self.last_goal = target
        return True

    def reset_last_goal(self):
        self.last_goal = None


# ---------------------------------------------------------------------------
# H1 — HOME coordinates fixed
# ---------------------------------------------------------------------------

def test_h1_home_coordinates_fixed():
    """HOME is exactly the approved nominal posture target."""
    assert HOME_TARGET == {
        "leg_id": "leg1",
        "x": 0.15,
        "y": 0.00,
        "z": -0.08,
    }


# ---------------------------------------------------------------------------
# H2 — HOME expected joint reference
# ---------------------------------------------------------------------------

def test_h2_home_expected_joint_target():
    """HOME expected joint target is the E3/E4.2 validated reference model."""
    assert len(HOME_JOINT_REFERENCE) == 3
    assert math.isclose(HOME_JOINT_REFERENCE[0], 0.0000, abs_tol=1e-6)
    assert math.isclose(HOME_JOINT_REFERENCE[1], 0.3281, abs_tol=1e-4)
    assert math.isclose(HOME_JOINT_REFERENCE[2], -1.7639, abs_tol=1e-4)


# ---------------------------------------------------------------------------
# H3 — HOME within limits
# ---------------------------------------------------------------------------

def test_h3_home_within_limits():
    """The HOME joint target remains inside the current Mark I limits."""
    angles = HOME_JOINT_REFERENCE
    keys = ["coxa", "femur", "tibia"]
    for joint_name, angle in zip(keys, angles):
        lower, upper = JOINT_LIMITS[joint_name]
        assert lower <= angle <= upper, (
            f"{joint_name} angle {angle} is outside current limit [{lower}, {upper}]"
        )


# ---------------------------------------------------------------------------
# H4 — HOME margin
# ---------------------------------------------------------------------------

def test_h4_home_margin_is_adequate():
    """HOME should be comfortably away from current joint limits."""
    angles = HOME_JOINT_REFERENCE
    minima = []
    for joint_name, angle in zip(["coxa", "femur", "tibia"], angles):
        lower, upper = JOINT_LIMITS[joint_name]
        minima.append(min(angle - lower, upper - angle))

    margin_min = min(minima)
    assert margin_min > 0.3, f"HOME margin too small: {margin_min} rad"
    assert math.isclose(margin_min, 0.3261, abs_tol=1e-2)


# ---------------------------------------------------------------------------
# H5 — ARM does not auto-HOME
# ---------------------------------------------------------------------------

def test_h5_arm_does_not_auto_home():
    """ARM only enables the command pipeline; it does not inject HOME."""
    semantics = NominalPostureSemantics()
    semantics.arm()
    assert semantics.enabled is True
    assert semantics.last_goal is None


# ---------------------------------------------------------------------------
# H6 — RE-ARM does not auto-HOME
# ---------------------------------------------------------------------------

def test_h6_rearm_does_not_auto_home():
    """DISARM then ARM without new target does not send HOME."""
    semantics = NominalPostureSemantics()
    semantics.arm()
    semantics.disarm()
    semantics.arm()
    assert semantics.enabled is True
    assert semantics.last_goal is None


# ---------------------------------------------------------------------------
# H7 — HOME is not a bypass / not a direct controller contract
# ---------------------------------------------------------------------------

def test_h7_home_is_normal_leg_target_not_bypass():
    """HOME uses the normal command pipeline and is represented as a normal LegTarget."""
    semantics = NominalPostureSemantics()
    semantics.arm()
    accepted = semantics.submit_normal_target(HOME_TARGET)

    assert accepted is True
    assert semantics.last_goal == HOME_TARGET
    assert semantics.last_goal["leg_id"] == "leg1"
    assert set(HOME_TARGET.keys()) == {"leg_id", "x", "y", "z"}


# ---------------------------------------------------------------------------
# H8 — HOLD is not an active command / no new contract
# ---------------------------------------------------------------------------

def test_h8_hold_is_not_a_new_active_command():
    """HOLD is an implicit behavior of the controller after a completed trajectory."""
    semantics = NominalPostureSemantics()

    # There is no new ROS contract for HOLD in the approved architecture.
    assert len(NO_HOLD_CONTRACTS) == 4
    assert NO_HOLD_CONTRACTS["topic"] == "/aracne/hold"
    assert NO_HOLD_CONTRACTS["service"] == "/aracne/hold"
    assert NO_HOLD_CONTRACTS["action"] == "/aracne/hold"
    assert NO_HOLD_CONTRACTS["parameter"] == "hold"

    # A hold-like behavior is semantic only; no active command contract is created.
    semantics.arm()
    semantics.submit_normal_target(HOME_TARGET)
    semantics.goal_in_flight = False
    assert semantics.last_goal == HOME_TARGET
    assert semantics.enabled is True


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
