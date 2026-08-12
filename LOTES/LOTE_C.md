# Lote C — Spawn do Mark I no Gazebo Harmonic e Controllers

## Objetivo

Fazer o Mark I/perna aparecer fisicamente no Gazebo Harmonic, configurar o `robot_state_publisher`, o bridge (incluindo `/clock`), e spawnar/ativar os broadcasters e controllers fornecidos pelo `controller_manager` do `gz_ros2_control`.

## Escopo executado

1. **C1 — YAML de controllers**
   - Reestruturado o `joint_trajectory_controller.yaml` com `ros__parameters` por controller e `controller_manager` apenas com `type`.
   - Adicionado `command_interface: position` e `state_interfaces: position, velocity`.

2. **C2 — Fornecimento do arquivo de controllers via `<parameters>`**
   - Eliminada a dependência reversa/oculta (`$(find aracne_bringup)` dentro de `aracne_description`).
   - `aracne.xacro`: passou a receber o caminho por argumento `controllers_file` (`<parameters>$(arg controllers_file)</parameters>`).
   - `mark1.launch.py`: resolve o caminho via `controllers_path = PathJoinSubstitution([bringup_share, "config", "joint_trajectory_controller.yaml"])` e injeta `controllers_file:=`.

3. **C3 — Spawn do Mark I**
   - `robot_state_publisher` mínimo (publica `robot_description` reutilizando a Command existente; `use_sim_time: true`).
   - Spawn via `ros_gz_sim create` com `world="mark1_lab"`, `name="mark1"`, pose `(0, 0, 0.5, Y=0)`, lendo `/robot_description`.
   - Ordem por `TimerAction`: Gazebo → robot_state_publisher (3.0s) → spawn (5.0s) → bridge (6.0s) → JSB (7.0s) → JTC (8.0s).
   - Correção do ground plane: substituído `model://ground_plane` por um ground plane SDF local.
   - Correção do erro `executable 'spawner.py' not found` → `executable="spawner"`.
   - Configuração do bridge por `config_file` (em vez de arquivo de parâmetros ROS2 direto) + adição do bridge `/clock` (GZ_TO_ROS).

4. **C4 — joint_state_broadcaster e parity de controllers**
   - Adicionado segundo spawner para `joint_state_broadcaster` (t=7.0s).
   - Correção do tipo de `action_monitor_rate: 10.0`.

## Fora do escopo (adiados)

- `mark1_params.yaml` (falha de `leg_kinematics_node` no parse — dívida técnica).
- CRLF dos scripts `teleop_node.py` e `teleop_bridge.py`.
- Bridge legado `/aracne/leg/joint_angles` (entrada inválida sem `gz_type_name`). Não tratado deliberadamente.
- Overlay / `AMENT_PREFIX_PATH` (sourcing explícito dos `local_setup.bash`).
- `GZ_SIM_SYSTEM_PLUGIN_PATH` necessário para localizar `libgz_ros2_control-system.so`.
- Warning KDL (root link com inertia).
- Warning de controller update period (0.01 s) vs sim period (0.001 s).
- TF detalhado (parcialmente validado), teleop, IK.

## Validação de fechamento

```bash
python3 -m py_compile src/aracne_bringup/launch/mark1.launch.py   # PASS
colcon build --symlink-install \
  --packages-select aracne_description aracne_simulation aracne_bringup   # PASS (3 pkgs)
```

## Critérios de aceite (runtime fornecidos pelo usuário)

| Critério | Resultado |
|---|---|
| mark1_lab carrega | PASS |
| Mark I spawnado | PASS |
| gz_ros2_control inicializa | PASS |
| hardware das 3 juntas inicializa | PASS |
| joint_state_broadcaster active | PASS |
| joint_trajectory_controller active | PASS |
| /joint_states com as 3 juntas | PASS |
| TF base→coxa→femur→tibia | PASS |
| view_frames confirma a árvore (~20 Hz) | PASS |
| build dos pacotes pertinentes | PASS |

## Conclusão

Lote C concluído para o núcleo de simulação do Mark I. Dividendos técnicos e itens fora do escopo são transitados para o `TECH_DEBT.md` e para o próximo lote.
