# WAYLAND — Matriz de Rastreabilidade do Mark I

## Status do Lote A

| ID | Requisito | Documento de origem | Pacote | Arquivo principal | Teste | Evidência | Status | Lote |
|---|---|---|---|---|---|---|---|---|
| R-M1-001 | Pacote teleop com sistema de build coerente | LOTES/LOTE_A.md | `aracne_teleop` | `package.xml`, `CMakeLists.txt` | `colcon build` | Build concluído | VALIDADO | A |
| R-M1-002 | Biblioteca IK segura e reutilizável internamente | LOTES/LOTE_A.md | `aracne_leg_kinematics` | `CMakeLists.txt`, `ik_solver.hpp` | `colcon build` | Build concluído | VALIDADO | A |
| R-M1-003 | IkResult sem memória indefinida | LOTES/LOTE_A.md | `aracne_leg_kinematics` | `ik_solver.hpp`, `leg_kinematics_node.cpp` | `colcon test` | Testes passam | VALIDADO | A |

## Observações

- A validação do Lote A foi concluída com build e testes passando.
- A rastreabilidade dos requisitos do Lote A está atualizada.
