# Changelog — WAYLAND

## Unreleased

### Fixed

- `aracne_teleop`: removido `ament_python` e ajustado para `ament_cmake` com `install(PROGRAMS ...)`.
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

