# Changelog — WAYLAND

## Unreleased

### Lote C — Spawn do Mark I no Gazebo Harmonic e controllers

#### Added

- `mark1.launch.py`: `robot_state_publisher` mínimo (publica `robot_description` a partir da `Command` do xacro; `use_sim_time: true`).
- `mark1.launch.py`: spawn do Mark I via `ros_gz_sim create` (`world=mark1_lab`, `name=mark1`, pose `(0,0,0.5,Y=0)`, lendo `/robot_description`).
- `mark1.launch.py`: segundo spawner para `joint_state_broadcaster`.
- `bridge_mark1.yaml`: bridge `/clock` (GZ_TO_ROS, `rosgraph_msgs/msg/Clock` ↔ `gz.msgs.Clock`).
- `mark1.launch.py`: configuração do `parameter_bridge` via parâmetro `config_file` (em vez de passar o YAML como arquivo de parâmetros ROS2).

#### Changed

- `aracne.xacro`: a dependência reversa/oculta `$(find aracne_bringup)` foi removida; o caminho do arquivo de controllers agora chega por argumento `controllers_file` e é usado em `<parameters>$(arg controllers_file)</parameters>`.
- `mark1.launch.py`: `controllers_path` resolve o YAML de controllers via `FindPackageShare` e injeta `controllers_file:=` no xacro.
- `mark1.launch.py`: `executable` do spawner corrigido de `spawner.py` para `spawner`.
- `mark1.launch.py`: ordem de inicialização por `TimerAction` (Gazebo → robot_state_publisher → spawn → bridge → JSB → JTC).
- `mark1_lab.sdf`: `model://ground_plane` substituído por um ground plane SDF local.
- `joint_trajectory_controller.yaml`: `action_monitor_rate` corrigido de `10` para `10.0` (double).

#### Fixed

- Marcador do controller manager: `executable 'spawner.py' not found` → resolvido com `spawner`.
- `parameter_bridge` falhava ao carregar o YAML ("Sequences cannot be key") → corrigido via parâmetro `config_file`.

#### Validado (runtime)

- Mundo `mark1_lab` abre; Mark I spawnado ("Entity creation successful").
- `gz_ros2_control` carrega `controller_manager`; hardware `aracne_leg1_controller` configurado e ativado; 3 juntas.
- `joint_state_broadcaster` e `joint_trajectory_controller` ativos.
- `/joint_states` publica `leg1_coxa_joint`, `leg1_femur_joint`, `leg1_tibia_joint`.
- TF `leg1_base_link → leg1_coxa_link → leg1_femur_link → leg1_tibia_link`; `view_frames` ~20 Hz.
- Build dos 3 pacotes (`aracne_description`, `aracne_simulation`, `aracne_bringup`) PASS; `py_compile` PASS.

### Lote D — Saneamento do bridge legado, parâmetros do leg_kinematics_node e CRLF

#### Changed

- `aracne_bringup/config/mark1_params.yaml`: parâmetros reestruturados no formato ROS2 padrão (`leg_kinematics_node: ros__parameters: leg_dimensions:`) — corrige a falha de parse do `leg_kinematics_node` (D1).
- `aracne_teleop/scripts/teleop_node.py` e `aracne_bringup/scripts/teleop_bridge.py`: normalização CRLF → LF (conteúdo lógico preservado) (D2).
- `aracne_simulation/config/bridge_mark1.yaml`: removida a entrada legada `/aracne/leg/joint_angles` (GZ_TO_ROS), que não possuía `gz_type_name`, referenciava `/model/aracne_leg/...` desatualizado e poderia criar múltiplos publishers no tópico (D3). `/clock` preservado.

#### Fixed

- Shebang dos scripts de teleop quebrado por CRLF (`/usr/bin/env: 'python3\r'`) → eliminado pela normalização CRLF→LF (D2).
- `parameter_bridge` emitia `[BridgeConfig] ... both ros_type_name and gz_type_name must be set` → eliminado pela remoção da entrada legada (D3).

#### Added

- Nenhuma bridge nova foi adicionada.

#### Validado (runtime, pelo operador)

- `leg_kinematics_node`, `teleop_node.py` e `teleop_bridge.py` iniciam (`process started`), sem `python3\r` e sem falha de parse de `mark1_params.yaml`.
- `[ros_gz_bridge]` criou `/clock (gz.msgs.Clock) -> /clock (rosgraph_msgs/msg/Clock)`; a mensagem `both ros_type_name and gz_type_name must be set` **não** apareceu mais.
- `joint_trajectory_controller` e `joint_state_broadcaster` permanecem **active**.
- `/aracne/leg/joint_angles`: Publisher count 1 (`leg_kinematics_node`), Subscription count 0.
- `/joint_states`: Publisher count 1 (`joint_state_broadcaster`), Subscription count 1; três juntas (`leg1_coxa_joint`, `leg1_femur_joint`, `leg1_tibia_joint`).
- TF `leg1_base_link → leg1_coxa_link → leg1_femur_link → leg1_tibia_link`: sem regressão após o Lote D.
- Build `colcon --packages-select aracne_simulation aracne_bringup`: PASS (2 pkgs).

### Fixed (Lote B / B.1)

- `aracne_leg_kinematics`: `ik_solver` convertido para biblioteca `STATIC` e vinculado corretamente ao nó e aos testes.
- `IkResult`: inicialização segura com `success=false` e ângulos zerados; erro de serviço tratado sem expor ângulos inválidos.
- `aracne_bringup`: removido o `ros2_control_node` (`controller_manager`) independente do `launch/mark1.launch.py` — o controller manager duplicado é eliminado e passa a ser fornecido pelo plugin `gz_ros2_control` do Gazebo.
- `aracne_bringup`: removidos `find_package(launch REQUIRED)` e `find_package(launch_ros REQUIRED)` do `CMakeLists.txt`, resolvendo a falha de CMake que não localizava o `launchConfig.cmake`; `launch`/`launch_ros` continuam declarados como `exec_depend` no `package.xml`.

### Lote B.1 — fechamento URDF/ros2_control (Jazzy + Harmonic)

#### Fixed

- `aracne_description/urdf/leg.xacro`: corrigida a estrutura de include da macro — a macro agora é declarada dentro de `<robot xmlns:xacro="...">` como elemento raiz, permitindo que o `aracne.xacro` instancie `<xacro:leg>` sem o erro `name 'leg_prefix' is not defined`.
- `aracne_description/urdf/aracne.xacro`: valores de `xacro:arg` enviados à macro passam a usar `$(arg nome)` em vez de `${nome}`.
- `aracne_description/urdf/aracne.xacro`: removido o bloco `<ros2_control>` duplicado dentro do plugin Gazebo; mantido apenas o `<ros2_control>` principal no nível do robô.
- `aracne_description/urdf/aracne.xacro`: hardware plugin atualizado para `gz_ros2_control/GazeboSimSystem` (antigo `gz_ros2_control::GazeboSystem`, inexistente no pacote instalado).
- `aracne_description/urdf/aracne.xacro`: plugin Gazebo atualizado para `filename="libgz_ros2_control-system.so"` e `name="gz_ros2_control::GazeboSimROS2ControlPlugin"` (antigo `libgz_ros2_control_gazebo.so` / `name="gz_ros2_control"`).

#### Changed / Validado

- Integração `gz_ros2_control` confirmada como compatível com ROS2 Jazzy + Gazebo Harmonic (pacote `ros-jazzy-gz-ros2-control` 1.2.19; hardware plugin `gz_ros2_control/GazeboSimSystem`; plugin Gazebo `libgz_ros2_control-system.so`).
- Validação concluída: `xacro` PASS, `check_urdf` PASS (3 juntas; `ros2_control` único), build dos 3 pacotes PASS (`aracne_description`, `aracne_simulation`, `aracne_bringup`).

### Changed

- `aracne_leg_kinematics/test/test_ik_solver.cpp`: registro do teste com `ament_add_gtest` e validação de caso de alvo fora de alcance.
- `aracne_bringup/launch/mark1.launch.py`: script normalizado com Black (formatação apenas; nenhuma mudança de lógica além da remoção do nó duplicado).

