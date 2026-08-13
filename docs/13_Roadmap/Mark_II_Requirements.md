# Mark II — Requirement Envelope

## 1. Mission

The Mark II is defined as a terrestrial biomimetic morphing robot platform. This document does not declare an implemented design; it defines the engineering envelope that must be derived before hardware, battery, actuator, and control architecture are frozen.

The platform is intended to support two future operating modes:

- HEXAPOD STABILITY MODE
  - 6 members in use
  - severe terrain support
  - low center of mass
  - rigid or locked spine state

- FELINE DYNAMIC MODE
  - 4 main locomotor members
  - 2 central members retracted or locked
  - running, jumping, agile posture
  - compliant/dynamic spine state

- MORPH TRANSITION
  - 6 → 4 and 4 → 6 transitions
  - center-of-mass management
  - support polygon adjustment
  - structural stiffness changes across morphing states

Status: ASPIRATIONAL / PROVISIONAL. Not yet implemented; not yet hardware-frozen.

---

## 2. Aspirational targets

These values are DESIGN TARGET / ASPIRATIONAL TARGET and are not frozen requirements.

| Attribute | Target | Status |
|---|---:|---|
| Body length | ~1.0 to 1.5 m | ASPIRATIONAL |
| Maximum speed | up to ~20 km/h | ASPIRATIONAL |
| Horizontal jump | ~1.5 m | ASPIRATIONAL |
| Consecutive jumping | future capability | ASPIRATIONAL |
| Scale | feline / predator-like | ASPIRATIONAL |

These targets are meant to set an envelope for engineering trade studies, not a final design commitment.

---

## 3. Engineering variables to derive

The following variables are part of the Mark II requirement envelope. They must be derived before freezing hardware or control architecture.

### 3.1 Geometry

- body length: TBD
- body width: TBD
- body height: TBD
- leg segment lengths: TBD
- stance width: TBD
- ground clearance: TBD
- spine length: TBD
- spine articulation range: TBD

### 3.2 Mass

- total mass: TBD
- sprung mass: TBD
- unsprung mass: TBD
- battery mass: TBD
- actuator mass: TBD
- payload allowance: TBD

### 3.3 Actuation

- peak joint torque: TBD
- continuous joint torque: TBD
- peak angular velocity: TBD
- continuous angular velocity: TBD
- mechanical power: TBD
- electrical power: TBD
- torque density: TBD
- power density: TBD
- reflected inertia: TBD
- backdrivability: TBD

### 3.4 Energy

- nominal bus voltage: TBD
- peak current: TBD
- continuous current: TBD
- usable battery energy: TBD
- power burst capability: TBD
- expected runtime: TBD
- thermal budget: TBD

### 3.5 Dynamics

- target running speed: TBD
- stride length: TBD
- stride frequency: TBD
- jump distance: TBD
- jump height: TBD
- takeoff velocity: TBD
- landing velocity: TBD
- impact energy: TBD
- peak ground reaction force: TBD
- duty factor: TBD

### 3.6 Compliance

- passive compliance: TBD
- active compliance: TBD
- tendon/spring energy storage: TBD
- stiffness range: TBD
- damping requirements: TBD

### 3.7 Sensing

- IMU rate: TBD
- encoder resolution: TBD
- encoder update rate: TBD
- force sensing needs: TBD
- foot contact sensing: TBD
- current sensing: TBD
- temperature sensing: TBD

### 3.8 Control

- low-level control rate: TBD
- state estimation rate: TBD
- policy/control rate: TBD
- communication latency budget: TBD

Status: TO BE DERIVED in the Mark II envelope. No final values are frozen in this document.

---

## 4. Physics sanity check

### 4.1 Speed conversion

20 km/h = 20 / 3.6 = 5.56 m/s.

### 4.2 Jump estimate: simplified ballistic model

For a horizontal jump of 1.5 m, use:

- x = v cos(θ) t
- y = v sin(θ) t - 0.5 g t^2
- range condition: x = 1.5 m at landing
- assume no aerodynamic losses and flat ground

The range formula is:

$$
R = \frac{v^2 \sin(2\theta)}{g}
$$

Thus,

$$
v = \sqrt{\frac{R g}{\sin(2\theta)}}
$$

For R = 1.5 m and g = 9.81 m/s^2, candidate launch angles give:

| Launch angle | Takeoff speed | Flight time | v_x | v_y |
|---|---:|---:|---:|---:|
| 30° | ~4.12 m/s | ~0.42 s | ~3.57 m/s | ~2.06 m/s |
| 45° | ~3.83 m/s | ~0.55 s | ~2.71 m/s | ~2.71 m/s |
| 60° | ~4.12 m/s | ~0.73 s | ~2.06 m/s | ~3.57 m/s |

### 4.3 Interpretation

These are first-order estimates only. They imply that the target jump remains physically plausible for a small-to-medium, agile morphing quadruped/feline-scale robot but would require:

- leg extension speed compatible with the chosen actuator architecture
- takeoff and landing energy handling within the actuator and structure envelope
- control timing and compliance for landing and impact absorption

This is not a structural analysis or final actuator selection. It is a demand estimate used to define the Mark II design envelope.

### 4.4 Impact of speed and jump on actuation

- Landing energy scales with mass and impact speed
- Short impact times imply large peak force demands
- A running platform at 20 km/h requires higher actuator bandwidth and compliant contacts than the single-leg Mark I baseline
- The Mark II likely needs variable stiffness and energy storage beyond rigid single-leg control

Status: PROVISIONAL / TO BE DERIVED.

---

## 5. Mass scenarios

Final mass is not known. A provisional set of exploratory scenarios is needed to bound design decisions.

### 5.1 Candidate scenarios

| Scenario | Mass range | Rationale |
|---|---:|---|
| LIGHT | 20–30 kg | compact feline-scale agile platform |
| MEDIUM | 30–45 kg | balanced mobility and payload |
| HEAVY | 45–60 kg | larger morphing or more protected platform |

These are provisional design envelopes for a 1–1.5 m morphing robot and are not final hardware decisions.

### 5.2 Energy and impact scale estimates

For a representative 20 km/h running condition, kinetic energy is:

$$
KE = \frac{1}{2} m v^2
$$

Using v = 5.56 m/s:

| Mass | Kinetic energy |
|---:|---:|
| 25 kg | ~194 J |
| 40 kg | ~310 J |
| 55 kg | ~425 J |

For a representative 0.4 m vertical hop:

$$
PE = m g h
$$

| Mass | Gravitational potential at 0.4 m |
|---:|---:|
| 25 kg | ~98 J |
| 40 kg | ~157 J |
| 55 kg | ~216 J |

Impact loads depend strongly on contact time. Assuming a 50–150 ms impact window for a dynamic landing:

$$
F \approx \frac{m \Delta v}{\Delta t}
$$

Representative force scale ranges:

| Mass | Approx. peak force range (assuming 50–150 ms contact) |
|---:|---:|
| 25 kg | ~900–2,800 N |
| 40 kg | ~1,500–4,500 N |
| 55 kg | ~2,000–6,000 N |

These are not structural FEA values; they are requirement-envelope estimates for actuator, contact, and compliance sizing.

Status: PROVISIONAL.

---

## 6. Actuator implications

The Mark II actuator architecture must eventually satisfy the force, power, compliance, and bandwidth demanded by both hexapod stability and feline dynamic motion.

### 6.1 Candidate conceptual classes

| Candidate class | Fit for static hexapod mode | Fit for dynamic feline mode | Notes |
|---|---|---|---|
| Conventional servo | Good for moderate speed, moderate force | Limited for high-impact agility | Simpler but often lower energy density |
| High-performance servo | Good | Moderate | Better power but limited compliance |
| QDD | Potentially strong | Strong candidate | Needs verification; still CANDIDATE |
| SEA | Good | Strong | Excellent compliance and impact tolerance |
| Custom BLDC reduction | Strong | Strong | Potentially best power density, requires integration work |

### 6.2 Requirements to be satisfied

Actuator architecture must eventually be evaluated against:

- peak torque and continuous torque
- speed at load
- thermal burden
- backdrivability
- impact survival
- control bandwidth
- reflected inertia
- compliance compatibility

Status: QDD remains CANDIDATE, not frozen.

---

## 7. Battery / power implications

Before battery selection, several items must be derived.

At minimum:

- system voltage
- peak power
- average locomotion power
- peak burst duration
- regenerative handling
- peak current
- energy capacity
- thermal limits
- mass budget

The selection of battery chemistry and pack architecture must follow the envelope produced from the dynamic target, actuator loads, and timing of morphing transitions. No final product is selected in this phase.

Status: TO BE DERIVED.

---

## 8. Spine requirements

The future Mark II spine must support two distinct mechanical states.

### 8.1 RIGID state

For hexapod stability mode:

- rigid support during body-level stability
- lower body pitch/roll disturbance
- higher stiffness for static support

### 8.2 DYNAMIC / COMPLIANT state

For running and jumping:

- active or passive compliancy
- energy storage and release
- damping and torsional compliance
- impact absorption
- rapid stiffness transition

### 8.3 Requirements categories

- articulation DOF: TBD
- stiffness range: TBD
- lock mechanism: TBD
- energy storage contribution: TBD
- damping: TBD
- torsional stiffness: TBD
- bending stiffness: TBD
- impact survival: TBD
- transition time: TBD

Status: PROVISIONAL / TO BE DERIVED.

---

## 9. Morphing requirements

Morphing is central to the Mark II concept but not yet a frozen mechanism. The transition between 6 and 4 support states must be bounded before any design commitment.

Minimum requirements:

- acceptable transition time: TBD
- center-of-mass motion limits: TBD
- support polygon constraints: TBD
- allowed number of unsupported legs: TBD
- central-leg retract/lock semantics: TBD
- failure-safe morphology: TBD
- transition not requiring ballistic motion: TBD

This document defines the envelope, not the control logic or final mechanism.

Status: PROVISIONAL / TO BE DERIVED.

---

## 10. Simulation requirements

The Mark II simulation environment must eventually include more than the single-leg baseline from Mark I.

Required simulation features:

- multi-leg contact
- dynamic friction
- compliant contacts
- spine articulation
- actuator torque and speed limits
- battery and power constraints
- joint damping/friction
- landing impacts
- sensor latency/noise
- mass distribution

Current simulator status:

- Gazebo remains the current integration target
- MuJoCo and Isaac are candidate complementary environments
- migration decision is not finalized

Status: PROVISIONAL.

---

## 11. Requirement classification

Every requirement in this document is tagged using one of the following categories:

- FROZEN
- PROVISIONAL
- ASPIRATIONAL
- TO BE DERIVED
- DEFERRED

No ambiguous statements are allowed in the requirement set.

---

## 12. Requirement IDs

Requirement IDs follow a minimal project convention.

Examples:

- M2-GEO-001
- M2-MASS-001
- M2-ACT-001
- M2-ENE-001
- M2-DYN-001
- M2-SEN-001
- M2-CTL-001
- M2-SPN-001
- M2-MOR-001
- M2-SIM-001

This document uses a minimal set of requirements and does not create a large requirement tree.

### Mark II requirement set

| ID | Category | Requirement |
|---|---|---|
| M2-GEO-001 | ASPIRATIONAL | The Mark II shall target a body envelope in the 1.0–1.5 m class. |
| M2-MASS-001 | TO BE DERIVED | Total mass, sprung mass, and unsprung mass shall be derived before hardware freeze. |
| M2-ACT-001 | TO BE DERIVED | Peak torque, continuous torque, speed, and power envelopes shall be derived for the morphing platform. |
| M2-ENE-001 | TO BE DERIVED | Battery and power architecture shall be derived from locomotion, jump, and burst demands. |
| M2-DYN-001 | ASPIRATIONAL | The design target shall include running and jumping behavior up to approximately 20 km/h and 1.5 m horizontal jump. |
| M2-CMP-001 | TO BE DERIVED | Compliance and stiffness envelope shall be derived for rigid and dynamic spine states. |
| M2-SEN-001 | TO BE DERIVED | Sensing requirements shall include IMU, encoder, force/contact, current, and thermal observability. |
| M2-CTL-001 | TO BE DERIVED | Control loops, latency budgets, and state-estimation requirements shall be derived before final controller selection. |
| M2-SPN-001 | PROVISIONAL | The spine shall support both rigid and compliant dynamic states with explicit stiffness and lock semantics. |
| M2-MOR-001 | PROVISIONAL | Morphing between 6 and 4 support states shall be bounded by transition time, CoM, and support-polygon constraints. |
| M2-SIM-001 | PROVISIONAL | Simulation shall model multi-leg contact, impact, compliance, and battery/power constraints beyond the Mark I single-leg baseline. |
| M2-GAP-001 | DEFERRED | Gaps between Mark I capability and Mark II operation shall be closed incrementally and documented. |

### Category counts

- Frozen: 0
- Provisional: 4
- Aspirational: 2
- To Be Derived: 6
- Deferred: 1

Total: 13 requirements.

---

## 13. Mark I → Mark II gap table

| Mark I capability | Mark II need | Gap | Implication |
|---|---|---|---|
| 1-leg simulation | multi-leg dynamic locomotion | high | whole-body dynamics and coordination are required |
| position control | high-bandwidth dynamic actuation | high | actuator limits, compliance, and impact handling must be derived |
| rigid chassis | articulated variable-stiffness spine | high | flexible body mechanics and stiffness transitions are required |
| no valid torque feedback | force/power observability | high | sensing and estimation stack must improve |
| single-leg IK | whole-body / morphology-aware control | high | control architecture moves beyond single-member IK |
| Gazebo static baseline | dynamic multi-contact validation | high | environment and contact model must evolve |
| low-power simulation loop | power-bounded operation | medium | battery and thermal envelopes are needed |
| no morphing model | 6↔4 transition semantics | high | support geometry and transition control must be designed |
| no dynamic landing requirement | jump/impact tolerance | high | landing and compliance implications become critical |

---

## 14. Documentation location and scope

This document is intended to be the authoritative Mark II requirements envelope.

Recommended location:

- docs/13_Roadmap/Mark_II_Requirements.md

This is the preferred approach because it keeps the requirement set centralized and avoids scattering the same architecture envelope across multiple files.

Status: authoritative document for Mark II envelope.

---

## 15. Summary

This document establishes the Mark II requirement envelope without prematurely selecting hardware or architecture. The key principle is simple:

- do not freeze hardware yet
- do not implement Mark II motion yet
- do not claim a final design before deriving the physical envelope
- preserve the frozen Mark I baseline as a valid, separate foundation

The Mark II is not an extension of Mark I by count of legs; it is a new dynamic morphing architecture with distinct physical, control, and energy requirements.

---

## 16. Status

- Mission: ESTABLISHED
- Mark II requirement envelope: ESTABLISHED
- Hardware frozen: NO
- Ready for F2: YES, conditional on formal F2 scope definition only
- Mark I baseline unchanged: YES

---

## 17. F2 PRE-EDIT ARCHITECTURE DECISION

### Body Segmentation

The body should be organized as a three-module architecture rather than a single rigid shell:

- front module
- mid module
- rear module

This preserves a compact body envelope while allowing a distinct spine region and a clear support structure for 6-leg and 4-leg modes. The architecture is intentionally conceptual and not a final CAD definition.

### Spine DOF

Initial classification:

- pitch: REQUIRED
- roll: REQUIRED for side-to-side stabilization and dynamic landing compensation
- yaw: OPTIONAL / DEFERRED

Reasoning:

- pitch is important for body posture and gait timing
- roll is important for stability and dynamic contact transitions
- yaw is not required for the initial architecture envelope unless an explicit turning or aggressive body reorientation requirement is later derived

### Spine States

Documented conceptual states:

- SPINE_RIGID
- SPINE_DYNAMIC
- SPINE_TRANSITION

These are state labels for architecture discussion only; they are not implemented software enums or ROS messages.

### Leg Roles

Hexapod mode:

- LF, RF, LM, RM, LR, RR all active support / locomotion members

Quadruped mode:

- LF, RF, LR, RR = primary locomotor pair
- LM, RM = central retractable support / transition members

This is the preferred initial architecture: front and rear pairs provide a stable quadruped stance, while middle legs are used as morphing support members instead of primary locomotor members. This reduces front/rear overlap and keeps the center of mass more central to the support polygon.

### Middle-Leg Retraction Recommendation

Recommend a concept where LM and RM retract upward and inward along the body, then lock in a protected configuration. This is preferable over a purely lateral or fully distal fold because it reduces collision risk with front and rear legs while maintaining a clean body envelope.

### Morph Transition Sequence

The recommended conceptual sequence is:

1. establish stable support
2. lower or shift CoM if needed
3. unload middle legs
4. retract middle legs
5. lock middle legs
6. switch spine to dynamic mode
7. enter quadruped control mode

Reverse transition:

1. reduce aggressive dynamic motion
2. re-establish stable quadruped support
3. prepare spine for rigid state
4. unlock and deploy middle legs
5. confirm contact
6. redistribute load
7. enter hexapod mode

This sequence is a conceptual architecture plan, not an implementation plan.

### Failure-Safe Recommendation

Preferred policy: fail toward 6-leg support.

Reasoning:

- six-legged support provides greater stability margins
- it reduces the risk of falling when energy is lost during morphing
- it is safer than allowing a partial or unbalanced quadruped posture
- it is mechanically simpler and more robust under uncertain contact states

### Leg DOF Recommendation

Baseline recommendation:

- 3 DOF per leg as the baseline architecture
- 4th DOF is a candidate only if a specific stance or foot-placement requirement emerges
- compliant foot is preferred over adding a new leg DOF when the goal is to improve impact absorption and toe-off

This keeps complexity manageable while preserving dynamic capability and future morphing flexibility.

### Foot Architecture Direction

Preferred direction:

- passive compliant foot as the default candidate
- rigid foot only as a minimal baseline for static support
- multi-segment toe remains a candidate, not a required design

This reduces impact shock and provides better contact compliance without prematurely freezing a specific foot mechanism.

### Mass Distribution Principles

- keep battery near the body center
- keep computing and power electronics near the center of mass
- minimize distal mass in the legs
- keep actuator mass proximal when possible
- balance spine modules and retractable middle-leg hardware
- avoid placing heavy components far from the body center if that worsens morphing stability

### Future Interfaces

These are placeholders only and are intentionally not implemented as ROS contracts:

- morphology state
- spine stiffness state
- leg role assignment
- foot contact state
- body state estimate

Status: PLACEHOLDER / NOT IMPLEMENTED.

### Requirement IDs Proposed

- M2-MOR-002 — Morphology state definition for 6↔4 architecture
- M2-SPN-002 — Spine architecture and stiffness envelope
- M2-GEO-002 — Body segmentation and proportional body envelope
- M2-LEG-002 — Leg role assignment and retraction concept
- M2-CON-002 — Contact and foot architecture direction

Category: PROVISIONAL / TO BE DERIVED / DEFERRED; no frozen hardware claims.

### Files Proposed

- docs/13_Roadmap/Mark_II_Requirements.md

This is still the preferred single-source document; no new file is created unless the document becomes too large for practical review.

### Functional Changes

NONE expected

### Runtime

NONE

---

## 18. F2 ARCHITECTURE SUMMARY

The Mark II body architecture should be treated as a three-module articulated body with a variable-stiffness spine and six legs arranged into a stable hexapod support footprint that can morph into a quadruped operating mode by retracting and locking the middle legs. The front/rear leg pair is the preferred primary locomotor arrangement, while the middle pair remains a transition and support function in dynamic mode.

This architecture is deliberately not frozen hardware and does not define a final actuator, battery, foot, or control stack. It is a requirement-environment decision sufficient to guide F3 and later design tasks without prematurely selecting components.

### F2 decision status

- Morphology architecture: ESTABLISHED (conceptual)
- Spine architecture: ESTABLISHED (conceptual)
- Leg role architecture: ESTABLISHED (conceptual)
- Hardware frozen: NO
- ROS contract created: NO
- Runtime executed: NO

---

## 19. F2 GAP TABLE EXTENSION

| Mark I capability | Mark II need | Gap | Implication |
|---|---|---|---|
| single rigid base | articulated spine and three-body segmentation | high | body flexion and support distribution must be redefined |
| one leg | six independently managed legs | high | role assignment and support polygon logic are needed |
| no leg roles | dynamic leg role assignment | high | locomotion architecture must support mode-dependent roles |
| no morphology state | 6↔4 morphology | high | transition logic and safe fallback states are required |
| no retract mechanism | middle-leg retract/lock | high | morphology must include retracing and protected storage |
| no compliant body | variable stiffness spine | high | spine stiffness, lock, and damping must be derived |

---

## 20. FINAL F2 STATUS

- F2 = PASS
- MORPHOLOGY ARCHITECTURE = ESTABLISHED
- SPINE ARCHITECTURE = ESTABLISHED
- LEG ROLE ARCHITECTURE = ESTABLISHED
- HARDWARE FROZEN = NO
- READY FOR F3 = YES, pending F3-specific scope definition only

No functional code, no hardware selection, no ROS contract, and no runtime execution were introduced in this step.

---

## 21. F3 PRE-EDIT VERIFICATION DECISION

### Simulation Levels

The Mark II validation ladder should be structured as a progressive evidence model, not as a single proof step:

- SIM-L0 — STATIC MODEL
- SIM-L1 — SINGLE LEG
- SIM-L2 — SIX-LEG STATIC SUPPORT
- SIM-L3 — HEXAPOD LOCOMOTION
- SIM-L4 — SPINE ARTICULATION
- SIM-L5 — QUADRUPED LOCOMOTION
- SIM-L6 — MORPH TRANSITION 6↔4
- SIM-L7 — DYNAMIC LOCOMOTION
- SIM-L8 — JUMP / LANDING

This decomposition is preferred because it separates model validity, locomotion validity, spine validity, and morphing validity in a way that makes the hardware transition boundary explicit.

### Simulation Metrics

The future Mark II simulation stack must define metrics for:

- joint position error
- joint velocity
- joint acceleration
- body orientation
- body angular rate
- CoM position
- CoM velocity
- support polygon margin
- foot contact state
- slip
- ground reaction force
- peak landing force
- spine angle
- spine rate
- power
- energy
- actuator saturation
- collision events

Classification:

- REQUIRED: minimum metrics needed to validate trajectory, contact, and support stability
- RECOMMENDED: useful for debugging and model tuning
- FUTURE / HARDWARE DEPENDENT: metrics that require real hardware or bench validation

### Sensor Boundary

The simulation model must eventually provide a mapping between simulated signals and future hardware signals:

| Signal | Simulation source | Hardware source | Required for control? | Required for safety? | Status |
|---|---|---|---|---|---|
| joint encoder | model kinematics | encoder | yes | yes | TO BE DERIVED |
| IMU | rigid body state | IMU | yes | yes | TO BE DERIVED |
| foot contact | contact model | foot sensor / load cell | yes | yes | TO BE DERIVED |
| force/load | contact force model | load cell / strain | recommended | yes | FUTURE |
| motor current | actuator model | current sense | yes | yes | TO BE DERIVED |
| actuator temperature | thermal model | thermal sensor | recommended | yes | FUTURE |
| battery voltage/current | power model | BMS / sensor | yes | yes | TO BE DERIVED |
| spine position | model state | encoder / hall | yes | yes | TO BE DERIVED |
| morph lock state | model state | switch / encoder | yes | yes | TO BE DERIVED |

No commercial sensor choice is made in this phase.

### Simulation Fidelity Strategy

The simulation stack should be segmented by fidelity:

- KINEMATIC
- RIGID-BODY DYNAMIC
- CONTACT
- ACTUATOR
- COMPLIANCE
- ENERGY
- THERMAL

The principle is straightforward: a simplified model can be used for early design iteration, but it cannot be used as proof of real hardware validity without physical correlation.

### Hardware Validation Boundary

The simulation cannot prove the following real-world properties:

- actuator thermal behavior real
- backlash
- gearbox wear
- cable fatigue
- connector reliability
- real friction
- structural fatigue
- impact survivability
- battery sag
- peak current transient
- EMI
- encoder noise
- sensor drift
- manufacturing tolerance
- physical E-STOP effectiveness

These remain HARDWARE VALIDATION REQUIRED.

### Mark I Debt → Hardware Blockers

Inherited Mark I issues remain relevant to the Mark II hardware boundary even without re-auditing the Mark I pipeline. A conceptual mapping is:

| Issue | Classification |
|---|---|
| R1 — stuck goal / timeout | ACCEPTABLE IN EARLY SIMULATION |
| R2 — DISARM != E-STOP | MUST FIX BEFORE HIL |
| R3 — controller command limits disabled | MUST FIX BEFORE POWERED HARDWARE |
| R4 — joint-limit enforcement gap | MUST FIX BEFORE POWERED HARDWARE |
| R5 — duplicated limit sources | MUST FIX BEFORE HIL |
| R6 — no physical E-STOP | MUST FIX BEFORE POWERED HARDWARE |
| R7 — effort/torque unavailable | ACCEPTABLE IN EARLY SIMULATION |
| R8 — no thermal/current/impact observability | MUST FIX BEFORE DYNAMIC HARDWARE |
| TD-011 | MUST FIX BEFORE POWERED HARDWARE |
| TD-012 (if present in project docs) | MUST FIX BEFORE POWERED HARDWARE |

These are not marked RESOLVED; they remain risk items at the boundary of simulation-to-hardware transition.

### Hardware Gates

The future hardware progression should be organized around gates, not by assumptions. A practical first pass:

- HW-G0 — ARCHITECTURE READY
- HW-G1 — ACTUATOR BENCH READY
- HW-G2 — SINGLE LEG BENCH READY
- HW-G3 — LOW-POWER MULTI-LEG READY
- HW-G4 — TETHERED ROBOT READY
- HW-G5 — UNTETHERED STATIC READY
- HW-G6 — DYNAMIC LOCOMOTION READY
- HW-G7 — JUMP TEST READY

Each gate requires explicit entry evidence, exit evidence, and blockers.

### HIL / Bench Progression

The normal progression should remain:

SIL → HIL → ACTUATOR BENCH → SINGLE LEG → MULTI-LEG LOW POWER → FULL ROBOT

This establishes the boundary between simulation-based conception and physical validation without conflating the two.

### Power / Energy Validation

Before any dynamic hardware operation, the following must be measured or derived:

- nominal power
- peak power
- current transient
- regenerative energy
- battery sag
- thermal load
- energy per stride
- energy per jump
- landing energy

The F1 mass scenarios remain provisional and still do not authorize battery selection.

### Structural Validation

The future structural boundary must include:

- static load cases
- dynamic load cases
- landing load
- torsional spine load
- leg root load
- middle-leg retract loads
- fatigue
- safety factors

No FEA is performed in this documentation slice.

### Model Validation Principle

A simulation model becomes predictive only after parameters are correlated against physical measurements.

Before that point:

- simulation is a design and behavior validation tool
- simulation is not proof of hardware readiness

### Requirement Traceability

Proposed F3 IDs:

- M2-SIM-002 — simulation ladder and validation architecture
- M2-HW-001 — hardware transition boundary and gate progression
- M2-SEN-002 — sensor boundary and mapping to real hardware
- M2-SAF-001 — safety debt and hardware no-go classification
- M2-ENE-002 — power and energy validation envelope
- M2-STR-001 — structural validation requirements boundary

and each requirement must carry:

- ID
- classification
- requirement
- validation stage

No FROZEN status is introduced in this phase.

### Exit Criteria for Simulation

“Simulation complete” does not mean “Mark II fully implemented.” It only means that the following are satisfied:

- SIMULATION ARCHITECTURE READY
- STATIC MORPHOLOGY VALIDATED
- LOCOMOTION BASELINE VALIDATED
- MORPHING VALIDATED
- DYNAMIC ENVELOPE VALIDATED

Each stage must have independent evidence.

### No-Go Conditions for Hardware

Hardware progression must remain blocked while any of the following remain unresolved:

- no E-STOP
- no command limit enforcement
- unknown actuator current limits
- unknown thermal envelope
- no timeout/watchdog
- uncontrolled morphology transition
- unknown structural load margin
- no reliable joint feedback

This remains a documentation-only requirement and not an implementation plan.

### Documentation Structure Decision

The preferred documentation remains:

- [docs/13_Roadmap/Mark_II_Requirements.md](docs/13_Roadmap/Mark_II_Requirements.md)

This is still the single-source truth while the content remains manageable. A separate verification-plan file is not created yet because the current requirement set can remain in one document without duplicating content.

### Files Proposed

- [docs/13_Roadmap/Mark_II_Requirements.md](docs/13_Roadmap/Mark_II_Requirements.md)

### Functional Changes

NONE expected

### Runtime

NONE

---

## 22. F3 SIMULATION VERIFICATION ARCHITECTURE

The Mark II simulation effort should be treated as a staged verification ladder that ends at hardware readiness only after real physical evidence exists. The simulation levels are not equivalent to hardware proof. The simulation model is valid for design iteration, behavior exploration, and architecture gating only when the model is correlated against real measurements.

The result is an explicit boundary:

SIMULATION VALIDATED ≠ HARDWARE READY

This is the essential F3 concept and the key transition boundary for the future Mark II work.

### F3 decision status

- Simulation validation architecture: ESTABLISHED
- Hardware transition boundary: ESTABLISHED
- Hardware ready: NO
- Mark I baseline unchanged: YES
- Runtime executed: NO

---

## 23. F3 GAP TABLE EXTENSION

| Mark I capability | Mark II need | Gap | Implication |
|---|---|---|---|
| single-leg validation model | staged multi-level simulation ladder | high | design validation must be organized by evidence level |
| runtime safety only in controlled simulation | hardware gate discipline | high | simulation must not be mistaken for hardware proof |
| no morphology state | morphing validation requirements | high | support, CoM, and contact transitions must be tested in simulation first |
| no dynamic load map | landing and impact envelope | high | dynamic hardware validation remains separate from sim validation |
| no real actuator observability | power and thermal measurement boundary | high | hardware and bench testing remain required |
| no physical E-STOP | hardware-safe gates | high | no hardware migration without explicit safety gate |

---

## 24. FINAL F3 STATUS

- F3 = PASS
- SIMULATION VERIFICATION ARCHITECTURE = ESTABLISHED
- HARDWARE TRANSITION BOUNDARY = ESTABLISHED
- HARDWARE READY = NO
- READY FOR LOT F CLOSURE = YES

No functional code, no URDF/Xacro, no Gazebo launch, no ROS runtime, no hardware selection, and no git operations were introduced in this step.
