"""
E4.2 SEQUENTIAL TARGETS — Static Test Suite

Tests validate:
1. IK computation for candidate targets (using solver math directly)
2. Joint angle finitude and limit compliance
3. Target sequence structure (list format, command ordering)
4. Invalid control case rejection at IK layer
5. Sequence sanity checks (non-empty, correct joint count)

Does NOT:
- Move the robot
- Start Gazebo or ROS runtime
- Publish targets to bridge
- Execute FollowJointTrajectory actions
- Use ActionClient

Static validation only. Runtime sequence will be manual.
"""

import pytest
import math
import sys
from pathlib import Path

# Assume we can import aracne_leg_kinematics from ROS build
# If not available during static test, we replicate the solver locally


class IKSolver:
    """Local IK implementation (mirrors aracne_leg_kinematics::solve_ik)."""
    
    def __init__(self, l1=0.05, l2=0.09, l3=0.11):
        self.l1 = l1  # coxa
        self.l2 = l2  # femur
        self.l3 = l3  # tibia
    
    def solve(self, x, y, z):
        """
        Solve IK for 3-DOF leg.
        Returns (success, [theta1, theta2, theta3], error_msg).
        """
        theta1 = math.atan2(y, x)
        r = math.sqrt(x * x + y * y) - self.l1
        d = math.sqrt(r * r + z * z)
        
        if d > (self.l2 + self.l3) or d < abs(self.l2 - self.l3):
            return False, [0, 0, 0], f"unreachable (d={d:.4f})"
        
        cos_theta3 = (d * d - self.l2 * self.l2 - self.l3 * self.l3) / (2.0 * self.l2 * self.l3)
        cos_theta3 = max(-1.0, min(1.0, cos_theta3))
        theta3 = -math.acos(cos_theta3)
        
        alpha = math.atan2(z, r)
        cos_beta = (self.l2 * self.l2 + d * d - self.l3 * self.l3) / (2.0 * self.l2 * d)
        cos_beta = max(-1.0, min(1.0, cos_beta))
        beta = math.acos(cos_beta)
        theta2 = alpha + beta
        
        return True, [theta1, theta2, theta3], ""


# Geometry
L1 = 0.05  # coxa
L2 = 0.09  # femur
L3 = 0.11  # tibia

# Joint limits (radians)
JOINT_LIMITS = {
    "coxa": (-1.57, 1.57),
    "femur": (-0.78, 1.57),
    "tibia": (-2.09, 0.0),
}

CANONICAL_JOINT_NAMES = [
    "leg1_coxa_joint",
    "leg1_femur_joint",
    "leg1_tibia_joint",
]

# Target candidates (Cartesian positions)
TARGETS = {
    "A": {"x": 0.15, "y": 0.00, "z": -0.08, "expected_angles": [0.0000, 0.3281, -1.7639]},
    "B": {"x": 0.17, "y": 0.00, "z": -0.05, "expected_angles": [0.0000, 0.5921, -1.7382]},
    "C": {"x": 0.10, "y": 0.10, "z": -0.08, "expected_angles": [0.7854, 0.3376, -1.8492]},
    "D": {"x": 0.08, "y": 0.00, "z": -0.12, "expected_angles": [0.0000, -0.2873, -1.8209]},
}

# Invalid control case
INVALID_TARGET = {"x": 0.35, "y": 0.00, "z": -0.08, "reason": "unreachable"}

# Test sequence order
TEST_SEQUENCE = ["A", "B", "INVALID", "C", "D"]


# ===========================================================================
# Fixtures
# ===========================================================================

@pytest.fixture
def ik_solver():
    """Provide IK solver instance."""
    return IKSolver(l1=L1, l2=L2, l3=L3)


@pytest.fixture
def targets():
    """Provide targets dict."""
    return TARGETS


@pytest.fixture
def invalid_target():
    """Provide invalid target."""
    return INVALID_TARGET


# ===========================================================================
# Tests: Target Audit
# ===========================================================================

def test_e4_2_s01_target_a_reachable(ik_solver, targets):
    """Q1: Target A (E3 validated) is reachable and within limits."""
    target = targets["A"]
    success, angles, error = ik_solver.solve(target["x"], target["y"], target["z"])
    
    assert success, f"Target A should be reachable, got error: {error}"
    assert len(angles) == 3, f"Expected 3 joint angles, got {len(angles)}"


def test_e4_2_s02_target_a_finite(ik_solver, targets):
    """Q1: Target A angles are finite."""
    target = targets["A"]
    success, angles, _ = ik_solver.solve(target["x"], target["y"], target["z"])
    
    assert success
    for i, angle in enumerate(angles):
        assert math.isfinite(angle), f"Joint {i} angle {angle} is not finite"


def test_e4_2_s03_target_a_within_limits(ik_solver, targets):
    """Q1: Target A angles are within JOINT_LIMITS."""
    target = targets["A"]
    success, angles, _ = ik_solver.solve(target["x"], target["y"], target["z"])
    
    assert success
    limit_keys = ["coxa", "femur", "tibia"]
    for i, key in enumerate(limit_keys):
        lower, upper = JOINT_LIMITS[key]
        assert lower <= angles[i] <= upper, \
            f"{key} {angles[i]:.4f} out of [{lower:.4f}, {upper:.4f}]"


def test_e4_2_s04_target_b_reachable(ik_solver, targets):
    """Q1: Target B is reachable and within limits."""
    target = targets["B"]
    success, angles, error = ik_solver.solve(target["x"], target["y"], target["z"])
    
    assert success, f"Target B should be reachable, got error: {error}"


def test_e4_2_s05_target_b_within_limits(ik_solver, targets):
    """Q1: Target B angles are within JOINT_LIMITS."""
    target = targets["B"]
    success, angles, _ = ik_solver.solve(target["x"], target["y"], target["z"])
    
    assert success
    limit_keys = ["coxa", "femur", "tibia"]
    for i, key in enumerate(limit_keys):
        lower, upper = JOINT_LIMITS[key]
        assert lower <= angles[i] <= upper, \
            f"{key} {angles[i]:.4f} out of [{lower:.4f}, {upper:.4f}]"


def test_e4_2_s06_target_c_reachable(ik_solver, targets):
    """Q1: Target C (lateral) is reachable."""
    target = targets["C"]
    success, angles, error = ik_solver.solve(target["x"], target["y"], target["z"])
    
    assert success, f"Target C should be reachable, got error: {error}"


def test_e4_2_s07_target_c_within_limits(ik_solver, targets):
    """Q1: Target C angles are within JOINT_LIMITS."""
    target = targets["C"]
    success, angles, _ = ik_solver.solve(target["x"], target["y"], target["z"])
    
    assert success
    limit_keys = ["coxa", "femur", "tibia"]
    for i, key in enumerate(limit_keys):
        lower, upper = JOINT_LIMITS[key]
        assert lower <= angles[i] <= upper, \
            f"{key} {angles[i]:.4f} out of [{lower:.4f}, {upper:.4f}]"


def test_e4_2_s08_target_d_reachable(ik_solver, targets):
    """Q1: Target D (close reach) is reachable."""
    target = targets["D"]
    success, angles, error = ik_solver.solve(target["x"], target["y"], target["z"])
    
    assert success, f"Target D should be reachable, got error: {error}"


def test_e4_2_s09_target_d_within_limits(ik_solver, targets):
    """Q1: Target D angles are within JOINT_LIMITS."""
    target = targets["D"]
    success, angles, _ = ik_solver.solve(target["x"], target["y"], target["z"])
    
    assert success
    limit_keys = ["coxa", "femur", "tibia"]
    for i, key in enumerate(limit_keys):
        lower, upper = JOINT_LIMITS[key]
        assert lower <= angles[i] <= upper, \
            f"{key} {angles[i]:.4f} out of [{lower:.4f}, {upper:.4f}]"


def test_e4_2_s10_invalid_target_unreachable(ik_solver, invalid_target):
    """Q2: Invalid target (unreachable) is rejected by IK solver."""
    success, angles, error = ik_solver.solve(invalid_target["x"], invalid_target["y"], invalid_target["z"])
    
    assert not success, "Invalid target should not be reachable"
    assert error, f"Expected error message, got none"
    assert "unreachable" in error.lower(), f"Expected 'unreachable' in error, got: {error}"


# ===========================================================================
# Tests: Joint State Message Format
# ===========================================================================

def test_e4_2_s11_joint_names_canonical():
    """Q8: Canonical joint names are correct."""
    expected = [
        "leg1_coxa_joint",
        "leg1_femur_joint",
        "leg1_tibia_joint",
    ]
    assert CANONICAL_JOINT_NAMES == expected


def test_e4_2_s12_joint_count():
    """Q10: Exactly 3 joints."""
    assert len(CANONICAL_JOINT_NAMES) == 3


def test_e4_2_s13_sequence_structure():
    """Q9: Test sequence is valid."""
    assert len(TEST_SEQUENCE) > 0, "Test sequence should not be empty"
    assert "INVALID" in TEST_SEQUENCE, "Test sequence should include invalid case"
    
    # Sequence should be: valid, valid, invalid, valid, valid
    # This tests that we can interleave invalid targets without breaking state
    valid_count = sum(1 for t in TEST_SEQUENCE if t != "INVALID")
    invalid_count = sum(1 for t in TEST_SEQUENCE if t == "INVALID")
    
    assert valid_count >= 3, f"Expected at least 3 valid targets, got {valid_count}"
    assert invalid_count == 1, f"Expected 1 invalid target, got {invalid_count}"


# ===========================================================================
# Tests: Limit Compliance Across Sequence
# ===========================================================================

def test_e4_2_s14_all_valid_targets_within_limits(ik_solver, targets):
    """Q4: All valid targets have all joints within limits."""
    limit_keys = ["coxa", "femur", "tibia"]
    
    for target_id, target in targets.items():
        success, angles, _ = ik_solver.solve(target["x"], target["y"], target["z"])
        assert success, f"Target {target_id} should be reachable"
        
        for i, key in enumerate(limit_keys):
            lower, upper = JOINT_LIMITS[key]
            assert lower <= angles[i] <= upper, \
                f"Target {target_id}: {key} {angles[i]:.4f} out of [{lower:.4f}, {upper:.4f}]"


def test_e4_2_s15_all_valid_targets_finite(ik_solver, targets):
    """Q1: All valid targets have finite joint angles."""
    for target_id, target in targets.items():
        success, angles, _ = ik_solver.solve(target["x"], target["y"], target["z"])
        assert success
        
        for i, angle in enumerate(angles):
            assert math.isfinite(angle), \
                f"Target {target_id} joint {i} angle {angle} is not finite"


# ===========================================================================
# Tests: IK Accuracy (Tolerance)
# ===========================================================================

TOLERANCE_RAD = 0.01  # ~0.57 degrees


def test_e4_2_s16_target_a_ik_accuracy(ik_solver, targets):
    """Q8: Target A IK result matches expected angles (within tolerance)."""
    target = targets["A"]
    success, angles, _ = ik_solver.solve(target["x"], target["y"], target["z"])
    expected = target["expected_angles"]
    
    assert success
    for i, (actual, exp) in enumerate(zip(angles, expected)):
        assert abs(actual - exp) <= TOLERANCE_RAD, \
            f"Joint {i}: expected {exp:.4f}, got {actual:.4f}, diff={abs(actual-exp):.4f}"


def test_e4_2_s17_target_b_ik_accuracy(ik_solver, targets):
    """Q8: Target B IK result matches expected angles."""
    target = targets["B"]
    success, angles, _ = ik_solver.solve(target["x"], target["y"], target["z"])
    expected = target["expected_angles"]
    
    assert success
    for i, (actual, exp) in enumerate(zip(angles, expected)):
        assert abs(actual - exp) <= TOLERANCE_RAD, \
            f"Joint {i}: expected {exp:.4f}, got {actual:.4f}, diff={abs(actual-exp):.4f}"


def test_e4_2_s18_target_c_ik_accuracy(ik_solver, targets):
    """Q8: Target C IK result matches expected angles."""
    target = targets["C"]
    success, angles, _ = ik_solver.solve(target["x"], target["y"], target["z"])
    expected = target["expected_angles"]
    
    assert success
    for i, (actual, exp) in enumerate(zip(angles, expected)):
        assert abs(actual - exp) <= TOLERANCE_RAD, \
            f"Joint {i}: expected {exp:.4f}, got {actual:.4f}, diff={abs(actual-exp):.4f}"


def test_e4_2_s19_target_d_ik_accuracy(ik_solver, targets):
    """Q8: Target D IK result matches expected angles."""
    target = targets["D"]
    success, angles, _ = ik_solver.solve(target["x"], target["y"], target["z"])
    expected = target["expected_angles"]
    
    assert success
    for i, (actual, exp) in enumerate(zip(angles, expected)):
        assert abs(actual - exp) <= TOLERANCE_RAD, \
            f"Joint {i}: expected {exp:.4f}, got {actual:.4f}, diff={abs(actual-exp):.4f}"


# ===========================================================================
# Tests: Bridge Safety Properties (No execution, just format checks)
# ===========================================================================

def test_e4_2_s20_valid_target_format():
    """Q9: Valid targets are properly structured for JointState transmission."""
    for target_id, target in TARGETS.items():
        assert "x" in target
        assert "y" in target
        assert "z" in target
        assert isinstance(target["x"], (int, float))
        assert isinstance(target["y"], (int, float))
        assert isinstance(target["z"], (int, float))


def test_e4_2_s21_all_angles_within_tight_bounds():
    """Q4: All computed angles respect STRICT joint limits (no clamping)."""
    ik = IKSolver(l1=L1, l2=L2, l3=L3)
    limit_keys = ["coxa", "femur", "tibia"]
    
    for target_id, target in TARGETS.items():
        success, angles, _ = ik.solve(target["x"], target["y"], target["z"])
        assert success
        
        for i, key in enumerate(limit_keys):
            lower, upper = JOINT_LIMITS[key]
            # Strict inequality: angle must be strictly within (no boundary touching)
            # For safety margin, require at least 1° from boundary
            margin_rad = 1.0 * math.pi / 180.0
            assert lower + margin_rad < angles[i] < upper - margin_rad, \
                f"Target {target_id}: {key} {angles[i]:.4f} too close to limits [{lower:.4f}, {upper:.4f}]"


# ===========================================================================
# Tests: State Coherence (Q9)
# ===========================================================================

def test_e4_2_s22_no_nan_in_sequence():
    """Q9: No NaN values in any target's computed joint angles."""
    ik = IKSolver(l1=L1, l2=L2, l3=L3)
    
    for target_id, target in TARGETS.items():
        success, angles, _ = ik.solve(target["x"], target["y"], target["z"])
        assert success
        
        for angle in angles:
            assert not math.isnan(angle), f"Target {target_id} contains NaN"


def test_e4_2_s23_no_inf_in_sequence():
    """Q9: No Inf values in any target's computed joint angles."""
    ik = IKSolver(l1=L1, l2=L2, l3=L3)
    
    for target_id, target in TARGETS.items():
        success, angles, _ = ik.solve(target["x"], target["y"], target["z"])
        assert success
        
        for angle in angles:
            assert not math.isinf(angle), f"Target {target_id} contains Inf"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
