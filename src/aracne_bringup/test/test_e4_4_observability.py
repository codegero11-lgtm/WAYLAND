"""E4.4 — Measurement & Observability Baseline

Static-only observability slice.

This file does not execute a ROS node or launch Gazebo. It provides the minimal
static reference implementation for the measurement contract requested in E4.4:
- signal availability audit
- metric definitions
- provisional tolerances
- NaN/invalid handling
- result/status classification
- timing calculations
- idle stability logic

The goal is to make the measurement baseline reproducible without introducing a
new ROS controller or a new runtime node.
"""

import math
from typing import Iterable, List, Optional, Sequence

import pytest


POSITION_TOLERANCE = 0.02
FINAL_VELOCITY_THRESHOLD = 0.05


OBSERVABLE_NOW = {
    "commanded_joint_position": "DERIVABLE_NOW",
    "actual_joint_position": "AVAILABLE_NOW",
    "absolute_joint_error": "DERIVABLE_NOW",
    "max_joint_error": "DERIVABLE_NOW",
    "final_joint_error": "DERIVABLE_NOW",
    "velocity": "AVAILABLE_NOW",
    "final_velocity": "DERIVABLE_NOW",
    "trajectory_nominal_duration": "DERIVABLE_NOW",
    "trajectory_observed_duration": "DERIVABLE_NOW",
    "goal_acceptance_latency": "DERIVABLE_NOW",
    "completion_latency": "DERIVABLE_NOW",
    "settling_time": "DERIVABLE_NOW",
    "overshoot": "DERIVABLE_NOW",
    "effort_torque": "NOT_AVAILABLE",
    "energy": "NOT_AVAILABLE",
    "actuator_temperature": "NOT_AVAILABLE",
    "impact_force": "NOT_AVAILABLE",
}


def final_position_error(actual: Sequence[float], expected: Sequence[float]) -> List[float]:
    if len(actual) != len(expected):
        raise ValueError("actual and expected sequences must have equal length")
    return [abs(float(a) - float(e)) for a, e in zip(actual, expected)]


def max_final_joint_error(errors: Sequence[float]) -> float:
    if not errors:
        raise ValueError("errors cannot be empty")
    return max(float(v) for v in errors)


def classify_goal_result(status: str) -> str:
    normalized = str(status).upper()
    allowed = {"SUCCEEDED", "ABORTED", "CANCELED", "REJECTED"}
    if normalized not in allowed:
        raise ValueError(f"unsupported goal result status: {status}")
    return normalized


def observed_duration_ns(goal_sent_ns: int, result_ns: int) -> int:
    if result_ns < goal_sent_ns:
        raise ValueError("result time must be >= goal sent time")
    return result_ns - goal_sent_ns


def final_velocity(samples: Sequence[float]) -> float:
    if not samples:
        raise ValueError("samples cannot be empty")
    return float(samples[-1])


def is_valid_sample(value: Optional[float]) -> bool:
    return value is not None and math.isfinite(float(value))


def classify_effort(value: Optional[float]) -> str:
    if value is None or not math.isfinite(float(value)):
        return "UNAVAILABLE"
    return "AVAILABLE"


def idle_stability(actual: Sequence[float], nominal: Sequence[float]) -> List[float]:
    if len(actual) != len(nominal):
        raise ValueError("actual and nominal sequences must have equal length")
    return [abs(float(a) - float(n)) for a, n in zip(actual, nominal)]


# ---------------------------------------------------------------------------
# O1 — metric definitions exist
# ---------------------------------------------------------------------------

def test_o1_metric_definitions_exist():
    assert isinstance(OBSERVABLE_NOW, dict)
    assert "actual_joint_position" in OBSERVABLE_NOW
    assert "absolute_joint_error" in OBSERVABLE_NOW
    assert "max_joint_error" in OBSERVABLE_NOW
    assert "goal_acceptance_latency" in OBSERVABLE_NOW
    assert "controller_health" not in OBSERVABLE_NOW


# ---------------------------------------------------------------------------
# O2 — position error calculation
# ---------------------------------------------------------------------------

def test_o2_position_error_calculation():
    actual = [0.10, -0.05, 1.20]
    expected = [0.12, 0.00, 1.15]
    error = final_position_error(actual, expected)
    assert error[0] == pytest.approx(0.02, rel=0, abs=1e-12)
    assert error[1] == pytest.approx(0.05, rel=0, abs=1e-12)
    assert error[2] == pytest.approx(0.05, rel=0, abs=1e-12)


# ---------------------------------------------------------------------------
# O3 — tolerance evaluation
# ---------------------------------------------------------------------------

def test_o3_tolerance_evaluation():
    assert POSITION_TOLERANCE == 0.02
    assert POSITION_TOLERANCE > 0.0

    errors = [0.010, 0.018, 0.022]
    assert max_final_joint_error(errors) == 0.022
    assert max_final_joint_error(errors) <= 0.02 + 1e-9 or max_final_joint_error(errors) > 0.02


# ---------------------------------------------------------------------------
# O4 — NaN effort classified unavailable
# ---------------------------------------------------------------------------

def test_o4_nan_effort_unavailable():
    assert classify_effort(None) == "UNAVAILABLE"
    assert classify_effort(float("nan")) == "UNAVAILABLE"
    assert classify_effort(float("inf")) == "UNAVAILABLE"
    assert classify_effort(0.25) == "AVAILABLE"


# ---------------------------------------------------------------------------
# O5 — result status classification
# ---------------------------------------------------------------------------

def test_o5_goal_result_classification():
    assert classify_goal_result("SUCCEEDED") == "SUCCEEDED"
    assert classify_goal_result("ABORTED") == "ABORTED"
    assert classify_goal_result("CANCELED") == "CANCELED"
    assert classify_goal_result("REJECTED") == "REJECTED"
    with pytest.raises(ValueError):
        classify_goal_result("UNKNOWN")


# ---------------------------------------------------------------------------
# O6 — timing calculation logic
# ---------------------------------------------------------------------------

def test_o6_timing_calculation_logic():
    goal_sent_ns = 1_000_000_000
    result_ns = 1_000_000_000 + 250_000_000
    assert observed_duration_ns(goal_sent_ns, result_ns) == 250_000_000


# ---------------------------------------------------------------------------
# O7 — max error calculation
# ---------------------------------------------------------------------------

def test_o7_max_error_calculation():
    errors = [0.003, 0.011, 0.018, 0.021]
    assert max_final_joint_error(errors) == 0.021


# ---------------------------------------------------------------------------
# O8 — idle stability comparison
# ---------------------------------------------------------------------------

def test_o8_idle_stability_comparison():
    actual = [0.100, 0.101, 0.099]
    nominal = [0.100, 0.100, 0.100]
    drift = idle_stability(actual, nominal)
    assert drift[0] == pytest.approx(0.0, abs=1e-12)
    assert drift[1] == pytest.approx(0.001, abs=1e-12)
    assert drift[2] == pytest.approx(0.001, abs=1e-12)


# ---------------------------------------------------------------------------
# O9 — invalid/missing samples rejected
# ---------------------------------------------------------------------------

def test_o9_invalid_or_missing_samples_rejected():
    assert is_valid_sample(0.0) is True
    assert is_valid_sample(float("nan")) is False
    assert is_valid_sample(None) is False

    with pytest.raises(ValueError):
        final_position_error([0.1], [0.2, 0.3])
    with pytest.raises(ValueError):
        max_final_joint_error([])
    with pytest.raises(ValueError):
        final_velocity([])


# ---------------------------------------------------------------------------
# O10 — NaN not interpreted as zero
# ---------------------------------------------------------------------------

def test_o10_nan_is_not_valid_zero():
    assert is_valid_sample(float("nan")) is False
    assert is_valid_sample(float("inf")) is False
    assert classify_effort(float("nan")) == "UNAVAILABLE"

    actual = [0.0, float("nan"), -0.02]
    expected = [0.0, 0.0, -0.02]
    errors = final_position_error(actual, expected)
    assert math.isnan(errors[1])


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
