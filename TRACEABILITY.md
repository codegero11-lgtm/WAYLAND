# WAYLAND — Matriz de Rastreabilidade do Mark I

## Status do Lote A

| ID | Requisito | Documento de origem | Pacote | Arquivo principal | Teste | Evidência | Status | Lote |
|---|---|---|---|---|---|---|---|---|
| R-M1-001 | Pacote teleop com sistema de build coerente | LOTES/LOTE_A.md | `aracne_teleop` | `package.xml`, `CMakeLists.txt` | `colcon build` | Build concluído | VALIDADO | A |
| R-M1-002 | Biblioteca IK segura e reutilizável internamente | LOTES/LOTE_A.md | `aracne_leg_kinematics` | `CMakeLists.txt`, `ik_solver.hpp` | `colcon build` | Build concluído | VALIDADO | A |
| R-M1-003 | IkResult sem memória indefinida | LOTES/LOTE_A.md | `aracne_leg_kinematics` | `ik_solver.hpp`, `leg_kinematics_node.cpp` | `colcon test` | Testes passam | VALIDADO | A |

## Status do Lote B (parcial)

| ID | Requisito | Documento de origem | Pacote | Arquivo principal | Teste | Evidência | Status | Lote |
|---|---|---|---|---|---|---|---|---|
| R-M1-B01 | Controller manager não duplicado no launch | LOTES/LOTE_B.md | `aracne_bringup` | `launch/mark1.launch.py` | `colcon build` | `ros2_control_node` independente removido; controller manager único fornecido pelo `gz_ros2_control` | VALIDADO | B |
| R-M1-B02 | `aracne_bringup` compilável sem `find_package` de pacotes Python | LOTES/LOTE_B.md | `aracne_bringup` | `CMakeLists.txt` | `colcon build` | Removidos `find_package(launch REQUIRED)`/`find_package(launch_ros REQUIRED)`; `launch`/`launch_ros` mantidos como `exec_depend` no `package.xml` | VALIDADO | B |

### Evidência — build de validação

```
wsl.exe -e bash -lc "cd /mnt/c/WAYLAND && source /opt/ros/jazzy/setup.bash && \
colcon build --symlink-install \
  --packages-select aracne_simulation aracne_description aracne_bringup"

Starting >>> aracne_simulation
Starting >>> aracne_description
Finished <<< aracne_simulation [1.34s]
Starting >>> aracne_bringup
Finished <<< aracne_description [1.87s]
Finished <<< aracne_bringup [9.75s]

Summary: 3 packages finished [11.8s]
```

- `aracne_simulation`, `aracne_description`, `aracne_bringup` compilam.
- Nenhum warning relevante.

## Observações

- O Lote B ainda **não está concluído**; apenas a parcela do controller manager duplicado foi validada.
- Demais requisitos do Lote B (estrutura de Xacro, juntas, geometria, `xacro`/`check_urdf`) seguem pendentes.
- A rastreabilidade do Lote A permanece válida.


