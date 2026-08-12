# WAYLAND — Current Status

> Este arquivo representa o estado validado do Mark I após a conclusão do Lote C (spawn + controllers no Gazebo Harmonic).

## Identificação

- Projeto: WAYLAND
- Mark atual: Mark I
- Lote atual: Lote C (concluído) — aguardando próximo lote
- Último lote concluído: Lote C
- Marco atual: M2 — Spawn do Mark I no Gazebo + broadcasters/controllers ativos
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
| `joint_trajectory_controller` | OK (active) | `action_monitor_rate: 10.0`; load/config/activate confirmados |
| TF | OK | `leg1_base_link → leg1_coxa_link → leg1_femur_link → leg1_tibia_link`; `view_frames` ~20 Hz |
## Bloqueadores atuais

- `mark1_params.yaml`: `leg_kinematics_node` falha no parse (`Cannot have a value before ros__parameters`) — dívida técnica para lote seguinte.
- CRLF nos scripts `teleop_node.py` e `teleop_bridge.py` (`/usr/bin/env: 'python3\r'`) — dívida técnica.
- Bridge legado `/aracne/leg/joint_angles` (`ros_type_name`/`gz_type_name` incompleto) — não tratado deliberadamente.
- Overlay/`AMENT_PREFIX_PATH` exigindo source explícito de `local_setup.bash` — problema de ambiente documentado.
- `GZ_SIM_SYSTEM_PLUGIN_PATH=/opt/ros/jazzy/lib` necessário para `libgz_ros2_control-system.so`.
- Warning KDL (root link com inertia) e warning de controller update period (0.01 s) vs sim (0.001 s) — não bloqueiam.
## Próximo objetivo

- Próximo lote: resolver as dívidas remanescentes (mark1_params.yaml, CRLF, bridge legado, overlay) e, em seguida, pipeline de comando de junta (joint_states→IK→teleop) — recomendado após aprovação.

