# Changelog — WAYLAND

## Unreleased

### Fixed

- `aracne_teleop`: removido `ament_python` e ajustado para `ament_cmake` com `install(PROGRAMS ...)`.
- `aracne_leg_kinematics`: `ik_solver` convertido para biblioteca `STATIC` e vinculado corretamente ao nó e aos testes.
- `IkResult`: inicialização segura com `success=false` e ângulos zerados; erro de serviço tratado sem expor ângulos inválidos.

### Changed

- `aracne_leg_kinematics/test/test_ik_solver.cpp`: registro do teste com `ament_add_gtest` e validação de caso de alvo fora de alcance.
