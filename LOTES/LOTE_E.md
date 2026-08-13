# Lote E — Controlled Motion Pipeline (Mark I)

> Documento histórico. Descreve o trabalho do **Lote E / E3** como foi executado, em um momento em que a visão futura do projeto era a arquitetura de uma perna (Mark I) como baseline. Os fatos abaixo são derivados exclusivamente dos registros validados em `TRACEABILITY.md` (`Status do Lote E`), `CHANGELOG.md` (`Lote E / E3`) e `CURRENT_STATUS.md`.

## Objetivo

Fechar o **primeiro pipeline ponta-a-ponta de movimento controlado** da Mark I em simulação:

```
LegTarget
→ leg_kinematics_node
→ /aracne/leg/joint_angles
→ joint_trajectory_bridge
→ FollowJointTrajectory
→ joint_trajectory_controller
→ ros2_control
→ Gazebo
→ /joint_states
```

Garantindo, por padrão, um comportamento **seguro por construção** (SAFE OFF) e um mecanismo de **ARM/DISARM em runtime** que não emite comando por si só.

## Escopo do Lote E (E1 / E2 / E3)

- **E1/E2** — pré-requisitos e definição do pipeline de movimento controlado (registrados nas etapas correspondentes).
- **E3** — fechamento documental + auditoria de consistência do bridge de trajetória e do primeiro movimento controlado validado.

## Entregas implementadas e validadas

### `joint_trajectory_bridge` (novo)

- Adapter entre a saída de IK (`/aracne/leg/joint_angles`, `sensor_msgs/msg/JointState`) e o `FollowJointTrajectory` do `joint_trajectory_controller`.
- `enabled` com default **`False` (SAFE OFF)** — enquanto desabilitado, apenas valida e loga, **nunca envia action goal**.
- Validações de **nomes**, **posições**, **finitude** (NaN/Inf) e **limites articulares**.
- Política **REJECT** (nunca `clamp`) para targets fora dos limites.
- **one-active-goal-at-a-time** (sem fila/encadeamento/preemption).
- Envio assíncrono (`send_goal_async`) e tratamento do resultado (ACCEPTED/REJECTED/SUCCEEDED/ABORTED/CANCELED).
- **ARM/DISARM em runtime** via `ros2 param set` (`add_on_set_parameters_callback` valida somente; `add_post_set_parameters_callback` sincroniza `self._enabled` e loga `command bridge ARMED`/`DISARMED`).
- Garantia **ARM != command**: ARM por si só **não** envia goal nem reutiliza target; somente um novo `JointState` recebido após o ARM produz goal.
- Instanciado em `mark1.launch.py` com `enabled=False`, `trajectory_duration=2.0` e `controller_action=/joint_trajectory_controller/follow_joint_trajectory`.
- Dependência direta `rcl_interfaces` (expressa no `package.xml`).

### Teleop

- `teleop_node.py`: **removida** a publicação automática via `create_timer(...)` — o teleop permanece inerte até uma fonte real de intenção do operador.

## Validação (runtime, fornecida pelo operador)

- Boot com `joint_trajectory_bridge` DISARMED (`enabled=False`); `ros2 param get ... enabled` → `False`.
- ARM em runtime → `command bridge ARMED`; **nenhum** movimento apenas por ARM.
- Target cartesiano único: `x=0.15, y=0.00, z=-0.08, leg_id=leg1`.
- IK resultante aproximada: `[0.0000, 0.3281, -1.7639]`.
- `sending FollowJointTrajectory goal ... [0.0000, 0.3281, -1.7639]` → `goal ACCEPTED` → `goal SUCCEEDED`.
- Feedback final em `/joint_states` aproximado: `[0, 0.32807, -1.76391]`; velocidades ~0.
- Controllers (`joint_trajectory_controller` e `joint_state_broadcaster`) permaneceram **active** durante o teste.
- DISARM confirmado (`enabled=False`).
- `py_compile`: PASS.
- `colcon build --packages-select aracne_teleop aracne_bringup`: PASS.

## Dívidas / débitos remanescentes conhecidos

- Envolvem itens de ambiente e warnings já registrados em `TECH_DEBT.md` (ex.: overlay/`AMENT_PREFIX_PATH`, `GZ_SIM_SYSTEM_PLUGIN_PATH`, KDL root inertia, controller update period, `controller_manager` "Enforcing command limits is disabled/ignored", esforço `.nan`). Nenhuma delas foi resolvida por este fechamento.
- O pipeline ponta-a-ponta de movimento, que era a dívida **TD-010**, foi **validado e encerrado** neste Lote E.

---

_Nota posterior — visão futura: após o fechamento do Lote E, a visão de futuro do projeto foi redefinida para **robótica mórfica biomimética** (plataforma terrestre hexápode/felino com coluna de rigidez variável). O resultado técnico deste lote **permanece válido como baseline** (Mark I / bancada de validação de controle); as novas diretrizes não retroagem o que está registrado aqui.
