# Mark I Command Safety Semantics & State-Machine Formalization

**Document**: E4.1 Safety Semantics & State-Machine Hardening  
**Status**: Static validation and documentation (runtime motion validation pending)  
**Target platform**: Mark I (single leg, simulation-only)  
**Last updated**: 2026-08-13  

---

## 1. SAFE OFF — Default Disabled State

### Principle

The command bridge (`joint_trajectory_bridge`) boots with `enabled=False`, ensuring **SAFE OFF** by construction. No goal is ever transmitted to the action server until explicitly armed.

### Implementation

```python
# joint_trajectory_bridge.py line ~70
self.declare_parameter("enabled", False)
```

### Behavior

- **On boot**: `_enabled = False`
- **While disabled**: All valid JointState messages are validated structurally, but transmission is blocked
- **Log**: "SAFE MODE: valid target but disabled" (throttled to avoid flooding)
- **Next step to action**: Must explicitly ARM via parameter set

### Safety guarantee

SAFE OFF is **not optional**; it is the default state. Launching the bridge without explicit `enabled=true` parameter guarantees no goal transmission.

---

## 2. ARM — Enable Command Pipeline

### Principle

ARM (setting `enabled: false → true`) **is not a command**. It unlocks the ability to accept valid targets, but does not send a goal by itself.

### Distinction: ARM vs. Command

| Operation | Behavior | Sends Goal? | Replays Stale? |
|---|---|---|---|
| **ARM** (param set enabled=true) | Transitions state, allows processing | ❌ NO | ❌ NO |
| **Command** (JointState publish) | Requests movement if enabled | ✅ YES (if valid) | ❌ NO |

### Implementation

```python
# joint_trajectory_bridge.py lines ~138-155
def _on_parameters_applied(self, params):
    for p in params:
        if p.name != "enabled":
            continue
        new_value = bool(p.value)
        self._enabled = new_value
        self.get_logger().warn(
            "command bridge ARMED" if self._enabled
            else "command bridge DISARMED"
        )
        # NOTE: Does NOT send goal. Does NOT replay targets.
```

### Example Sequence

```
Timeline:

Boot:  enabled=false, target arrives → (SAFE MODE, rejected) → goal NOT sent

ros2 param set /joint_trajectory_bridge enabled true
→ Bridge transitions to enabled=true

Bridge does NOT send goal here.

ros2 topic pub /aracne/leg/joint_angles ...
→ JointState arrives (now enabled=true)
→ Validation checks pass
→ _send_goal() THEN called

Movement happens (if action server ready).
```

### Safety guarantee

ARM is **idempotent and safe**: calling it multiple times or followed by no action produces no unwanted goals.

---

## 3. DISARM — POLICY A (Mark I Choice)

### Principle

DISARM (setting `enabled: true → false`) means:

**"Stop accepting new commands"**

It does **not** mean:

**"Cancel the currently executing goal"**

### Policy A Semantics

| Scenario | Behavior |
|---|---|
| **DISARM while idle** (no in-flight goal) | `enabled=false`; new targets blocked |
| **DISARM while goal PENDING/ACTIVE** | `enabled=false`; current goal continues to completion; new targets blocked |
| **DISARM after goal result received** | `enabled=false`; cleanup proceeds normally; _goal_in_flight released |
| **RE-ARM later** | `enabled=true`; new targets can generate goals; old goal not replayed |

### Implementation

```python
# joint_trajectory_bridge.py lines ~148-149
def _on_joint_angles(self, msg: JointState):
    # ... validation ...
    if not self._enabled:
        # SAFE MODE: never send a goal.
        self._log_safe_mode_valid_target()
        return  # DISARM blocks new; does NOT cancel active

    # ... continue to _send_goal if enabled and valid ...
```

**Note on goal cancellation**: The bridge does NOT store `GoalHandle` and does NOT call `cancel_goal()`. If a goal is in-flight when DISARM occurs, the bridge simply stops accepting new targets. The active goal continues until the controller sends a result (or times out).

### Safety guarantee

DISARM is **fail-safe and non-destructive**: it prevents new goals but does not introduce unknown state (like a failed cancel request).

---

## 4. ARM ≠ Command — Re-emphasized

### Why This Matters

If ARM were treated as a command (i.e., sending a goal to a stale/cached target), the system would violate the principle:

> "Command = explicit JointState message"

### Consequence of Treating ARM as Command

❌ **Dangerous**: User sets `enabled=true` and a *previous* target retroactively executes.  
❌ **Non-obvious**: Parameter change triggers motion with no new ROS message.  
❌ **Hard to debug**: Where did the target come from?

### Mark I Choice

✅ **ARM only transitions state**. No automatic goal transmission. Every movement requires an explicit new JointState message.

---

## 5. ONE-ACTIVE-GOAL Guarantee

### Principle

The bridge never sends a second goal until the first one has completed (via action server result callback).

### Implementation

```python
# joint_trajectory_bridge.py
self._goal_in_flight = False  # Line ~82

def _on_joint_angles(self, msg: JointState):
    if self._goal_in_flight:
        self.get_logger().warn(
            "valid joint target received but a goal is already in flight "
            "(skipping - one active goal at a time)"
        )
        return  # Do not send

    # ... validation, enabled check ...
    self._send_goal(positions)

def _on_goal_result(self, future):
    # ... handle result ...
    self._goal_in_flight = False  # Release after result
```

### Guarantee

- **No queueing**: Second message while in-flight is ignored.
- **No preemption**: Active goal completes without cancellation (DISARM or new target).
- **Release path**: `_goal_in_flight` is set to `False` in all callback paths (success/exception/timeout-induced).

### Safety implication

one-active-goal prevents cascade/starvation scenarios: only one trajectory can execute at a time.

---

## 6. REJECT Policy — Limits & Validation

### Principle

Targets outside joint limits or structurally invalid are **REJECTED** (goal NOT sent). Never silently clamped.

### Validation Layers

| Layer | Check | Action if Invalid | Source |
|---|---|---|---|
| **Structure** | Exactly 3 joints; no duplicates | REJECT + log | bridge |
| **Finitude** | All positions are finite (not NaN/Inf) | REJECT + log | bridge |
| **Known names** | All names in CANONICAL_JOINT_NAMES | REJECT + log | bridge |
| **Limits** | Each position within [lower, upper] | REJECT + log | bridge + URDF |
| **Reachability** | IK can reach target (checked earlier in pipeline) | N/A in bridge | leg_kinematics |

### Current Joint Limits (Mark I)

```python
# joint_trajectory_bridge.py line ~33
JOINT_LIMITS = {
    "leg1_coxa_joint":   (-1.57,  1.57),  # ±90°
    "leg1_femur_joint":  (-0.78,  1.57),  # ~-45° to +90°
    "leg1_tibia_joint":  (-2.09,  0.0),   # ~-120° to 0°
}
```

### Example: Out-of-Range Rejection

```python
# Input: femur = 2.0 (exceeds upper limit 1.57)
# Bridge action:
if not (-0.78 <= 2.0 <= 1.57):
    # REJECT
    self.get_logger().error(
        f"... out-of-range ... goal NOT sent"
    )
    return None  # Validation fails
```

### Safety guarantee

Invalid targets are **not silent failures** (e.g., clamped); they are **logged and rejected**.

---

## 7. Limit Enforcement Matrix — Current Layers

### Sources of Limits

| Source | Scope | Enforced? | Notes |
|---|---|---|---|
| **URDF** (aracne.xacro) | Definition of structure/constraints | No (informational) | Hardware reality; controller_manager ignores |
| **Bridge** (joint_trajectory_bridge.py) | Transmission gate | ✅ YES (REJECT) | Mirrors URDF values; hardcoded comment says "not independent source of truth" |
| **IK solver** (ik_solver.cpp) | Reachability (before bridge) | Partial (reachability only) | Validates d vs L1+L2+L3; does NOT validate joint angles θ |
| **JointTrajectoryController** | Action goal validation | Unknown (needs investigation) | ROS2 controller; assumed to validate but no enforcement confirmed |
| **Hardware layer** (future) | Physical servo limits | Not applicable (simulation only) | Future real hardware will have independent enforcement |

### Current Gap (Acknowledged)

⚠️ **IK solver does not validate joint angle limits**. It can return θ values that technically violate URDF bounds if the inverse geometry produces them (e.g., coxa=2.0 if some path-dependent calculation reaches it).

**Mitigation**: Bridge catches these *after* IK, so bridge is the enforcement layer for Mark I.

**Future work (TD-011, not E4.1)**: Centralize limit sources or add explicit cross-layer consistency checks.

### Safe Status for Mark I

✅ **SAFE**: Bridge validates limits and rejects. IK reachability check provides separate protection. Together they form adequate protection for simulation.

---

## 8. Timeout & Unknown Goal State — Risk Documentation

### Scenario

The action server for `FollowJointTrajectory` receives a goal, but:

1. The bridge never receives a response callback (`_on_goal_response`)
2. The bridge never receives a result callback (`_on_goal_result`)
3. The action server state is unknown (still executing? crashed? client lost?)

### Current Behavior

```python
# If response/result callbacks never fire:
self._goal_in_flight = True  # Set before send_goal_async
# ... no callback → _goal_in_flight REMAINS True ...
# Next target arrives:
if self._goal_in_flight:  # True
    return  # REJECT (one-active-goal guard)
```

### Safety Implication

| State | Risk | Mitigation |
|---|---|---|
| **in_flight=True, unknown server state** | Cannot send new goals; system appears frozen | ✅ Explicit safeguard: one-active-goal prevents cascade |
| **Auto-releasing in_flight=False** | Allowing new goal while old still executing | ❌ **UNSAFE** — not implemented |

### Known Safety Risk

❌ **If timeout occurs, the bridge enters a safe but non-recoverable state.**

- New goals cannot be sent (one-active-goal guard protects)
- Old goal state is unknown (might still executing, might crashed)
- Manual recovery needed (restart system or external clear)

### Current Mark I Status

✅ **Acceptable for simulation** because:
1. Gazebo usually does not timeout during short tests
2. Known risk is documented (here, in this file)
3. Guard prevents new goals (no cascade)

### Future Requirement (Not E4.1)

When timeout detection is implemented, the bridge must distinguish:

```
State machine (future):

IDLE
  ↓ send_goal_async()
GOAL_IN_FLIGHT (response received)
  ↓ timeout or goal completes
IDLE

OR (timeout scenario):

IDLE
  ↓ send_goal_async()
GOAL_STATE_UNKNOWN (no response after timeout)
  ↓ manual recovery or restart
IDLE or FAULT
```

**This state machine is NOT implemented in E4.1.**

### Why Not Auto-Release on Timeout?

❌ **Reason**: Releasing `_goal_in_flight=False` automatically would assume "server didn't execute," but you don't actually know. The goal might still be running in the controller.

If you release the flag and send a new goal:
- Old goal still executing (first leg movement)
- New goal transmitted (second leg movement)
- Concurrent execution = **UNSAFE**

✅ **Safer**: Keep flag True, block new goals, and require manual recovery (next phase).

---

## 9. E-STOP & CANCEL — Future Capability

### Not in Mark I

The bridge does **not**:
- Have a cancel button
- Implement E-STOP
- Support goal preemption
- Gracefully cancel an in-flight goal

### Why Deferred

E-STOP is a **discrete safety system** that should be separate from the regular control pipeline. Mark I demonstrates:

1. Structural safety (SAFE OFF default)
2. Validation (REJECT policy)
3. Concurrency safety (one-active-goal)

**E-STOP adds**: immediate discontinuation, independent of goal state.

### Future Design (Not Implemented)

```
E-STOP (future):

trigger E-STOP
  ↓
send cancel_goal (async)
  ↓ cancel response
set _goal_in_flight = False
broadcast "STOPPED" status
  ↓
New goals blocked until E-STOP cleared

OR (if hard stop):

Restart system / reboot controller.
```

### Mark I Placeholder

Bridge logs E-STOP as **not implemented**:

```python
# E-STOP = FUTURE
# Currently, manual intervention required if goal doesn't complete.
```

---

## 10. Summary — Safety Guarantees

| Guarantee | Mechanism | Threat Model | Status |
|---|---|---|---|
| **SAFE OFF** | enabled=False default | Accidental goal transmission | ✅ Implemented |
| **ARM ≠ Command** | ARM only toggles flag | Stale target replay | ✅ Implemented |
| **DISARM blocks new** | enabled check blocks transmission | New goals after disable | ✅ Implemented |
| **one-active-goal** | _goal_in_flight guard | Cascade/queue overflow | ✅ Implemented |
| **REJECT invalid** | Validation + no clamp | Malformed/out-of-range | ✅ Implemented |
| **Finite validation** | math.isfinite() checks | NaN/Inf corruption | ✅ Implemented |
| **Timeout non-recovery** | Known risk; documented | Unknown server state | ⚠️ Accepted (not E4.1) |
| **E-STOP** | N/A (not implemented) | Emergency discontinuation | ❌ Future |

---

## 11. Testing & Validation Status

### Static Tests (E4.1 Slice)

✅ **Implemented**: `test_e4_1_safety_state_machine.py`

| Test | Property | Implementation |
|---|---|---|
| S1 | SAFE OFF default | ✅ Code inspection |
| S2 | Valid target while disabled | ✅ Mock callback |
| S3 | ARM ≠ command | ✅ Parameter transition |
| S4 | Out-of-range rejection | ✅ Limit validation |
| S5 | NaN/Inf rejection | ✅ Finitude checks |
| S6 | one-active-goal guard | ✅ State simulation |
| S8 | DISARM blocks new targets | ✅ State transition |
| S11 | Validation in SAFE MODE | ✅ Structure check |
| S12 | No stale replay | ✅ Caching test |

### Runtime Tests (Manual, Pending)

⏳ **S7 — DISARM during in-flight goal**: Requires actual motion setup; to be executed after static tests pass.

---

## 12. E4.4 — Measurement & Observability Baseline

### Current observability

The Mark I pipeline exposes the following signals today:

**AVAILABLE NOW**
- `/joint_states.position`
- `/joint_states.velocity`
- goal acceptance/rejection and `FollowJointTrajectory` result status
- controller active state (when the controller is published as active)
- timing derivable from `goal_sent` and final result timestamps

**DERIVABLE NOW**
- commanded joint position from the target/trajectory sent to the controller
- actual joint position from `/joint_states`
- absolute joint error = `abs(actual - expected)`
- max final joint error = `max(abs(error_i))`
- final joint velocity = last sample from `/joint_states.velocity`
- nominal trajectory duration = command/bridge duration
- observed completion duration = `result_time - goal_sent_time`
- completion latency and settling window can be derived from timestamped samples
- overshoot can be derived from peak position excursion over the nominal target during the observation window

**UNAVAILABLE / NOT VALID TODAY**
- `effort` in `/joint_states` is currently `nan` and is not treated as a valid measurement
- torque/effort at actuator output
- energy consumption
- actuator temperature
- impact force / GRF
- current, voltage, power, and mechanical/electrical power balance

### Provisional thresholds

- `PROVISIONAL POSITION TOLERANCE = 0.02 rad` per joint
- `PROVISIONAL FINAL VELOCITY THRESHOLD = 0.05 rad/s` (conservative bound derived from the current static baseline; not a final hardware requirement)

### Observability gap

The current system does not provide an objective measurement stack for:
- real torque
- energy draw
- thermal load
- impact force
- contact forces
- current/voltage and power
- dynamic QDD or model-based energy estimation

These are intentionally left out of E4.4.

### Implementation choice

No new ROS node or ROS contract was introduced for E4.4. The baseline is a static/analytical measurement contract using existing signals and action result metadata only.

---

## 13. Nominal Posture Semantics (E4.3)

### DISARMED

**DISARMED** means the bridge blocks new goals. It does not command any posture and does not cancel an already active goal.

- `enabled=false` is a safety gate
- no repositioning is triggered automatically
- no HOME command is launched from the parameter change
- no new goal is accepted while disabled

### HOLD

**HOLD** is not a new ROS contract in Mark I.

The current controller already holds the last commanded joint position after a goal reaches `SUCCEEDED`, provided no new command arrives. That is the implied runtime behavior, not a separate action/service.

### HOME

**HOME** is a nominal reference posture used as a safe, documented baseline when an experiment requires a known standard pose.

Approved nominal reference:

- Cartesian: `(0.15, 0.00, -0.08, leg1)`
- Joint target: `[0.0000, 0.3281, -1.7639]`

This target is treated as a normal `LegTarget` processed through the regular pipeline:

```
LegTarget
→ IK
→ joint_angles
→ bridge validation
→ FollowJointTrajectory
```

It does **not** bypass the bridge, and it does **not** execute automatically on ARM or RE-ARM.

### SAFE vs HOME

**SAFE** remains a safety concept: guarding the command pipeline, rejecting invalid targets, and preventing concurrency.

**HOME** is a nominal posture and a reference target. It is not automatically equivalent to a safe-state command.

### Runtime note

This section formalizes the semantics but does not claim runtime motion validation for HOME/HOLD yet.

---

## 14. E4.5 — Risk Acceptance & Closure Audit

### R1 — Goal timeout / stuck goal

This risk remains documented and accepted for Mark I simulation only.

Current state:
- `_goal_in_flight` blocks new goals while one goal is in flight
- callback success/failure paths release the guard
- if a future never resolves, the bridge may remain in an unknown but safe state for simulation purposes

Status: `ACCEPTED FOR MARK I SIMULATION`
Not status: `RESOLVED`

### R2 — DISARM Policy A

`DISARM` keeps the current semantics:
- blocks new goals
- does not cancel active goals
- does not equal E-STOP

Status: `ACCEPTED FOR MARK I SIMULATION`
Required before hardware: real E-STOP / cancel semantics and recovery policy

### R3 — Controller command limits disabled

The controller manager continues to warn that command limits are disabled and URDF command limits are ignored.

Current mitigation:
- bridge validates all incoming positions
- IK checks reachability
- explicit rejection path remains in place

Status: `ACCEPTED WITH MITIGATION FOR SIMULATION`
Required before hardware: controller-side enforcement or centralized limit layer

### R4 — IK joint-limit gap

IK validates reachability but does not guarantee the final joint angles are within the full URDF symbolic limit envelope in all possible internal paths.

Current mitigation:
- bridge validates joint limits before emitting the goal

Status: `ACCEPTED WITH MITIGATION FOR SIMULATION`
Not resolved

### R5 — duplicated URDF/bridge limits

The current Mark I baseline keeps limit values duplicated across URDF and bridge constants for runtime validation.

Status: `SYNCHRONIZED TODAY / DUPLICATED SOURCE`
This is recorded as a risk for future architecture hardening, not as a fix.

### R6 — no physical E-STOP

This remains a future capability, not a current implementation.

Status: `DEFERRED`
Required before higher-energy physical operation

### R7 — effort/torque unavailable or invalid

The current `/joint_states` effort data is invalid (`nan`) and not fit for runtime metric use.

Status: `ACCEPTED FOR MARK I SIMULATION`
This is an observability gap, not a solved sensor capability.

### R8 — no thermal/current/impact observability

No valid source exists today for thermal, current, power, or impact metrics.

Status: `DEFERRED`
Needed for hardware-sizing, battery, thermal, and dynamic evolution

### E4.5 closure rule

The E4 closure intentionally documents accepted simulation risks and defers hardware hardening. No risk is described as `RESOLVED` unless it is actually fixed with evidence.

---

## 15. Traceability

| Requirement | Document | Code | Test | Status |
|---|---|---|---|---|
| R-M1-E01 | SAFE OFF default | bridge.py line 70 | S1 | ✅ |
| R-M1-E02 | REJECT validation | bridge.py lines 200-227 | S4, S5, S11 | ✅ |
| R-M1-E03 | one-active-goal | bridge.py line 82, 150-153 | S6 | ✅ |
| R-M1-E04 | ARM ≠ command | bridge.py line 138-155 | S3 | ✅ |
| E4.1-01 | DISARM Policy A | bridge.py, this doc | S8 | ✅ |
| E4.1-02 | Timeout risk documented | Section 8 | Documentation | ✅ |
| E4.1-03 | Limit enforcement matrix | Section 7 | Documentation | ✅ |
| E4.3-01 | DISARM semantics | Section 12 | H5, H6 | ✅ |
| E4.3-02 | HOLD implicit | Section 12 | H8 | ✅ |
| E4.3-03 | HOME nominal posture | Section 12 | H1-H7 | ✅ |

---

## References

- [src/aracne_bringup/scripts/joint_trajectory_bridge.py](../../src/aracne_bringup/scripts/joint_trajectory_bridge.py) — Command bridge implementation
- [src/aracne_description/urdf/aracne.xacro](../../src/aracne_description/urdf/aracne.xacro) — Joint limit definitions
- [src/aracne_bringup/test/test_e4_1_safety_state_machine.py](../../src/aracne_bringup/test/test_e4_1_safety_state_machine.py) — E4.1 safety tests
- [LOTES/LOTE_E.md](../../LOTES/LOTE_E.md) — Lote E closure documentation

---

**Document end.** This file formalizes the safety semantics validated in E4.1 static tests. Runtime motion validation (S7) is pending manual execution.
