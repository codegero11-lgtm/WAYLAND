# WAYLAND — Current Status

> Este arquivo representa o estado validado do Mark I após a conclusão do Lote D (saneamento de parâmetros, CRLF e bridge legado).

## Identificação

- Projeto: WAYLAND
- Mark atual: Mark I
- Lote atual: Lote D (concluído) — aguardando próximo lote
- Último lote concluído: Lote D
- Marco atual: M3 — Mark I com saneamento de startup concluído (parâmetros, CRLF, bridge legado)
- Última atualização: 2026-08-12

## Ambiente

| Item | Status | Evidência |
|---|---|---|
| WSL2 | OK | `wsl.exe` disponível e ambiente acessível |
| ROS2 Jazzy | OK | Build/test usando `/opt/ros/jazzy/setup.bash` |
| colcon | OK | `colcon build --symlink-install` |
| Gazebo Harmonic (runtime) | OK (validado) | Mundo `mark1_lab` abre; Mark I spawnado via `ros_gz_sim create`; `controller_manager` do `gz_ros2_control` operacional |
| ros2_control | OK (runtime) | `joint_state_broadcaster` e `joint_trajectory_controller` ativos; hardware `aracne_leg1_controller` ativado; 3 juntas |
## Estado do software

| Área | Status | Observação |
|---|---|---|
| Build de pacotes (Lote C) | OK | `aracne_description`, `aracne_simulation`, `aracne_bringup` compilam |
| `py_compile` launch | OK | `mark1.launch.py` compila |
| Mundo `mark1_lab` | OK (local) | ground plane local substituiu `model://ground_plane` |
| Spawn do Mark I | OK | `ros_gz_sim create` com `world=mark1_lab`, `name=mark1`, via `/robot_description` |
| `robot_state_publisher` | OK | publica `robot_description` (Command do xacro) + TF |
| Bridge `/clock` | OK | `parameter_bridge` criou `/clock` (GZ→ROS); `controller_manager` parou de emitir "No clock received" |
| `joint_state_broadcaster` | OK (active) | 2º spawner (t=7.0s); publicado `/joint_states` com 3 juntas |
| `joint_trajectory_controller` | OK (active) | `action_monitor_rate: 10.0`; load/config/activate confirmados; continua active após Lote D |
| TF | OK | `leg1_base_link → leg1_coxa_link → leg1_femur_link → leg1_tibia_link`; `view_frames` ~20 Hz; sem regressão após Lote D |
| `leg_kinematics_node` | OK (runtime) | inicia após saneamento de `mark1_params.yaml` (D1); falha de parse eliminada |
| `teleop_node.py` | OK (runtime) | inicia após normalização CRLF (D2) |
| `teleop_bridge.py` | OK (runtime) | inicia após normalização CRLF (D2) |
| `/aracne/leg/joint_angles` | OK | `sensor_msgs/msg/JointState`; Publisher count: 1 (leg_kinematics_node); Subscription count: 0 |
| Erro CRLF (`python3\r`) | Eliminado | scripts de teleop em LF; startup limpo |
| Erro parsing bridge legado | Eliminado | entrada `joint_angles` removida em `bridge_mark1.yaml`; `parameter_bridge` sem "both ros_type_name and gz_type_name must be set"; `/clock` preservado |

## Bloqueadores atuais

- Elo ponta-a-ponta **AINDA NÃO validado**: `IK → comando aceito pelo JointTrajectoryController → movimento físico/simulado da perna → feedback coerente em /joint_states`. Pertence ao próximo estágio (Lote E).
- Overlay/`AMENT_PREFIX_PATH` exigindo source explícito de `local_setup.bash` — problema de ambiente documentado.
- `GZ_SIM_SYSTEM_PLUGIN_PATH=/opt/ros/jazzy/lib` necessário para `libgz_ros2_control-system.so`.
- Warning KDL (root link com inertia) e warning de controller update period (0.01 s) vs sim (0.001 s) — não bloqueiam.

## Próximo objetivo

- Próximo lote (Lote E): fechamento do primeiro pipeline de movimento da Mark I — `target_pose/IK → joint targets → JointTrajectoryController → gz_ros2_control → juntas no Gazebo → /joint_states`. O nome e a decomposição definitivos podem ser definidos após análise estática. Não implementado ainda.

