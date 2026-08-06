# Changelog — WAYLAND

## Unreleased

### Fixed

- `aracne_teleop`: removido `ament_python` e ajustado para `ament_cmake` com `install(PROGRAMS ...)`.
- `aracne_leg_kinematics`: `ik_solver` convertido para biblioteca `STATIC` e vinculado corretamente ao nó e aos testes.
- `IkResult`: inicialização segura com `success=false` e ângulos zerados; erro de serviço tratado sem expor ângulos inválidos.
- `aracne_bringup`: removido o `ros2_control_node` (`controller_manager`) independente do `launch/mark1.launch.py` — o controller manager duplicado é eliminado e passa a ser fornecido pelo plugin `gz_ros2_control` do Gazebo.
- `aracne_bringup`: removidos `find_package(launch REQUIRED)` e `find_package(launch_ros REQUIRED)` do `CMakeLists.txt`, resolvendo a falha de CMake que não localizava o `launchConfig.cmake`; `launch`/`launch_ros` continuam declarados como `exec_depend` no `package.xml`.

### Changed

- `aracne_leg_kinematics/test/test_ik_solver.cpp`: registro do teste com `ament_add_gtest` e validação de caso de alvo fora de alcance.
- `aracne_bringup/launch/mark1.launch.py`: script normalizado com Black (formatação apenas; nenhuma mudança de lógica além da remoção do nó duplicado).

