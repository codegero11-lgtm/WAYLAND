# WAYLAND — Current Status

> Este arquivo representa o estado validado do Mark I após a conclusão do Lote B e do Lote B.1 (fechamento URDF/ros2_control).

## Identificação

- Projeto: WAYLAND
- Mark atual: Mark I
- Lote atual: Lote B.1 (concluído) — aguardando Lote C
- Último lote concluído: Lote B / Lote B.1
- Marco atual: M1 — Build e testes unitários estáveis
- Última atualização: 2026-08-06

## Ambiente

| Item | Status | Evidência |
|---|---|---|
| WSL2 | OK | `wsl.exe` disponível e ambiente acessível |
| ROS2 Jazzy | OK | Build/test usando `/opt/ros/jazzy/setup.bash` |
| colcon | OK | `colcon build --symlink-install` |
| Gazebo (runtime) | Não validado | Integração estrutural confirmada; rodagem não iniciada (bloqueante do Lote C) |
| ros2_control | Confirmado (estrutura) | Controller manager único; hardware plugin `gz_ros2_control/GazeboSimSystem` compatível com Jazzy/Harmonic |
## Estado do software

| Área | Status | Observação |
|---|---|---|
| Build de pacotes básicos | OK | `aracne_msgs`, `aracne_leg_kinematics`, `aracne_teleop` compilam |
| Testes unitários | OK | `aracne_leg_kinematics`, `aracne_teleop` passam |
| `aracne_teleop` | OK | utiliza `ament_cmake` e `install(PROGRAMS ...)` |
| `ik_solver` | OK | biblioteca estática ligada ao nó e testes |
| `IkResult` | OK | inicialização segura e fluxo de erro tratado |
| URDF/Xacro | CONCLUÍDO (B.1) | `xacro` processa (PASS); `check_urdf` PASS; 3 juntas; `ros2_control` único; estrutura corrigida (macro em `<robot>`, `$(arg ...)`) |
| Controller manager | OK (único) | `ros2_control_node` independente removido; único controller manager fornecido pelo `gz_ros2_control` do Gazebo |
| Integração gz_ros2_control | OK (Jazzy/Harmonic) | `libgz_ros2_control-system.so` + `gz_ros2_control::GazeboSimROS2ControlPlugin`; hardware `gz_ros2_control/GazeboSimSystem` |
| Build Lote B | OK | `aracne_simulation`, `aracne_description`, `aracne_bringup` compilam |

## Bloqueadores atuais

- Gazebo runtime e controllers ainda não validados (pertencem ao Lote C; dependem de spawn e configuração de controllers, fora do escopo do Lote B.1).
- O repositório contém modificações pré-existentes fora do escopo do Lote A e não foram alteradas.

## Próximo objetivo

- Lote C: spawn do Mark I no Gazebo Harmonic, `robot_state_publisher`, broadcasters e configuração de controllers (YAML/spawner). Não iniciado — aguarda aprovação.

