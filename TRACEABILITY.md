# WAYLAND — Matriz de Rastreabilidade do Mark I

## Status do Lote A

| ID | Requisito | Documento de origem | Pacote | Arquivo principal | Teste | Evidência | Status | Lote |
|---|---|---|---|---|---|---|---|---|
| R-M1-001 | Pacote teleop com sistema de build coerente | LOTES/LOTE_A.md | `aracne_teleop` | `package.xml`, `CMakeLists.txt` | `colcon build` | Build concluído | VALIDADO | A |
| R-M1-002 | Biblioteca IK segura e reutilizável internamente | LOTES/LOTE_A.md | `aracne_leg_kinematics` | `CMakeLists.txt`, `ik_solver.hpp` | `colcon build` | Build concluído | VALIDADO | A |
| R-M1-003 | IkResult sem memória indefinida | LOTES/LOTE_A.md | `aracne_leg_kinematics` | `ik_solver.hpp`, `leg_kinematics_node.cpp` | `colcon test` | Testes passam | VALIDADO | A |

## Status do Lote B (concluído)

| ID | Requisito | Documento de origem | Pacote | Arquivo principal | Teste | Evidência | Status | Lote |
|---|---|---|---|---|---|---|---|---|
| R-M1-B01 | Controller manager não duplicado no launch | LOTES/LOTE_B.md | `aracne_bringup` | `launch/mark1.launch.py` | `colcon build` | `ros2_control_node` independente removido; controller manager único fornecido pelo `gz_ros2_control` | VALIDADO | B |
| R-M1-B02 | `aracne_bringup` compilável sem `find_package` de pacotes Python | LOTES/LOTE_B.md | `aracne_bringup` | `CMakeLists.txt` | `colcon build` | Removidos `find_package(launch REQUIRED)`/`find_package(launch_ros REQUIRED)`; `launch`/`launch_ros` mantidos como `exec_depend` no `package.xml` | VALIDADO | B |
| R-M1-B03 | Xacro processa e gera URDF válido (3 juntas) | LOTES/LOTE_B.md | `aracne_description` | `urdf/aracne.xacro`, `urdf/leg.xacro` | `xacro` + `check_urdf` | `xacro` PASS; `check_urdf` PASS; cadeia `base→coxa→femur→tibia`; estrutura de macro corrigida (`<robot>` raiz + `$(arg ...)`) | VALIDADO | B |
| R-M1-B04 | `ros2_control` único no URDF (sem duplicação de hardware plugin) | LOTES/LOTE_B.md | `aracne_description` | `urdf/aracne.xacro` | `xacro` | `<ros2_control>` único (1 ocorrência); `<ros2_control>` interno do plugin removido | VALIDADO | B |
| R-M1-B05 | Hardware plugin e plugin Gazebo compatíveis com gz_ros2_control Jazzy/Harmonic | LOTES/LOTE_B.md | `aracne_description` | `urdf/aracne.xacro` | inspeção da instalação | `gz_ros2_control/GazeboSimSystem` + `libgz_ros2_control-system.so` + `gz_ros2_control::GazeboSimROS2ControlPlugin` confirmados no pacote `ros-jazzy-gz-ros2-control` 1.2.19 e na doc oficial Jazzy | VALIDADO | B |

### Evidências — Lote B / B.1

**Validação Xacro + URDF (B1.1, B1.3, B1.4):**
```
source /opt/ros/jazzy/setup.bash
xacro src/aracne_description/urdf/aracne.xacro -o /tmp/wayland_b1.urdf
check_urdf /tmp/wayland_b1.urdf
```
Resultado: `xacro` PASS; `check_urdf` PASS — `Successfully Parsed XML`, cadeia `leg1_base_link → leg1_coxa_link → leg1_femur_link → leg1_tibia_link`; `<ros2_control>` único (1 ocorrência).

**Integração gz_ros2_control instalada (B1.2):**
```
dpkg -l | grep gz-ros2-control   -> ros-jazzy-gz-ros2-control 1.2.19-1noble
/opt/ros/jazzy/lib/libgz_ros2_control-system.so
/opt/ros/jazzy/share/gz_ros2_control/gz_hardware_plugins.xml
   -> class name "gz_ros2_control/GazeboSimSystem"
strings libgz_ros2_control-system.so -> gz_ros2_control::GazeboSimROS2ControlPlugin
```
Hardware plugin `gz_ros2_control/GazeboSimSystem`; plugin Gazebo `libgz_ros2_control-system.so` / `gz_ros2_control::GazeboSimROS2ControlPlugin` — compatíveis com Jazzy + Harmonic (conforme documentação oficial do branch `jazzy`).

**Build dos 3 pacotes (B1.5):**
```
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install \
  --packages-select aracne_description aracne_simulation aracne_bringup

Starting >>> aracne_simulation
Starting >>> aracne_description
Finished <<< aracne_simulation [1.32s]
Starting >>> aracne_bringup
Finished <<< aracne_description [1.86s]
Finished <<< aracne_bringup [2.15s]
Summary: 3 packages finished [4.20s]
```
- `aracne_simulation`, `aracne_description`, `aracne_bringup` compilam.
- Nenhum warning relevante.

## Status do Lote C (concluído)

| ID | Requisito | Documento de origem | Pacote | Arquivo principal | Teste | Evidência | Status | Lote |
|---|---|---|---|---|---|---|---|---|
| R-M1-C01 | Eliminada dependência reversa `aracne_description → aracne_bringup` no URDF | LOTES/LOTE_C.md | `aracne_description`, `aracne_bringup` | `urdf/aracne.xacro`, `launch/mark1.launch.py` | `xacro` + `check_urdf` | `$(find aracne_bringup)` removido; `controllers_file` por argumento; `check_urdf` PASS | VALIDADO | C |
| R-M1-C02 | Mundo `mark1_lab` abre sem dependência externa | LOTES/LOTE_C.md | `aracne_simulation` | `worlds/mark1_lab.sdf` | runtime | ground plane local substituiu `model://ground_plane`; mundo abre | VALIDADO | C |
| R-M1-C03 | Mark I spawnado no Gazebo | LOTES/LOTE_C.md | `aracne_bringup` | `launch/mark1.launch.py` | runtime | `ros_gz_sim create` → "Entity creation successful"; modelo `mark1` visível | VALIDADO | C |
| R-M1-C04 | Bridge `/clock` GZ→ROS | LOTES/LOTE_C.md | `aracne_simulation` | `config/bridge_mark1.yaml` | runtime | `parameter_bridge` criou `/clock (gz.msgs.Clock) → /clock (rosgraph_msgs/msg/Clock)`; fim do "No clock received" | VALIDADO | C |
| R-M1-C05 | `joint_state_broadcaster` active | LOTES/LOTE_C.md | `aracne_bringup` | `launch/mark1.launch.py` | runtime | `ros2 control list_controllers` → `joint_state_broadcaster ... active` | VALIDADO | C |
| R-M1-C06 | `joint_trajectory_controller` active | LOTES/LOTE_C.md | `aracne_bringup` | `config/joint_trajectory_controller.yaml` | runtime | `action_monitor_rate: 10.0`; load/config/activate; `list_controllers` → active | VALIDADO | C |
| R-M1-C07 | `/joint_states` com as 3 juntas | LOTES/LOTE_C.md | `aracne_bringup` | `launch/mark1.launch.py` | runtime | `ros2 topic echo /joint_states --once` → `leg1_coxa_joint`, `leg1_femur_joint`, `leg1_tibia_joint` (position/velocity) | VALIDADO | C |
| R-M1-C08 | TF da perna | LOTES/LOTE_C.md | `aracne_bringup` | `launch/mark1.launch.py` | runtime | `/tf` → `leg1_base_link → leg1_coxa_link → leg1_femur_link → leg1_tibia_link`; `view_frames` ~20 Hz | VALIDADO | C |

### Evidências — Lote C

**Build de fechamento:**
```
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install \
  --packages-select aracne_description aracne_simulation aracne_bringup
Summary: 3 packages finished ...
```
`py_compile src/aracne_bringup/launch/mark1.launch.py` → PASS.

**Evidências de runtime (fornecidas pelo usuário):**
- `ros_gz_sim create` → "Entity creation successful".
- `Loading controller_manager`; `Successful initialization of hardware 'aracne_leg1_controller'`; `System Successfully configured!`; `Successful 'activate' of hardware ...`; `Resource Manager has been successfully initialized.`
- `Loaded joint_trajectory_controller`; `Configured and activated joint_trajectory_controller`; `Successfully switched controllers!`
- `ros2 control list_controllers` → `joint_trajectory_controller ... active`; `joint_state_broadcaster ... active`.
- `/joint_states` → 3 juntas (position/velocity).
- `/tf` e `view_frames` → cadeia base→coxa→femur→tibia (~20.312 Hz).

## Status do Lote D (concluído)

| ID | Requisito | Documento de origem | Pacote | Arquivo principal | Teste | Evidência | Status | Lote |
|---|---|---|---|---|---|---|---|---|
| R-M1-D01 | `mark1_params.yaml` em formato ROS2 padrão para o `leg_kinematics_node` | LOTES/LOTE_D.md | `aracne_bringup` | `config/mark1_params.yaml` | runtime manual | `[INFO] [leg_kinematics_node-7]: process started ...`; falha de parse de `mark1_params.yaml` não ocorre mais | VALIDADO | D |
| R-M1-D02 | Scripts `teleop_node.py`/`teleop_bridge.py` sem CRLF e iniciando | LOTES/LOTE_D.md | `aracne_teleop`, `aracne_bringup` | `scripts/teleop_node.py`, `scripts/teleop_bridge.py` | estático + build + runtime | `git diff --ignore-cr-at-eol` vazio (lógica preservada); `file -b` sem CRLF; `py_compile` PASS; build PASS; `[INFO] [teleop_node.py-8]: process started ...` e `[INFO] [teleop_bridge.py-9]: process started ...`; erro `python3\r` não ocorre mais | VALIDADO | D |
| R-M1-D03 | Bridge legado `/aracne/leg/joint_angles` removido; `/clock` preservado | LOTES/LOTE_D.md | `aracne_simulation` | `config/bridge_mark1.yaml` | estático + build + runtime | `parameter_bridge` cria `/clock (gz.msgs.Clock) → /clock (rosgraph_msgs/msg/Clock)` sem `both ros_type_name and gz_type_name must be set`; entrada legada removida | VALIDADO | D |
| R-M1-D04 | Controllers e feedback preservados após Lote D | LOTES/LOTE_D.md | `aracne_bringup` | `launch/mark1.launch.py` | runtime manual | `ros2 control list_controllers` → `joint_trajectory_controller` e `joint_state_broadcaster` **active**; `/joint_states` Publisher count 1 | VALIDADO | D |

### Evidências — Lote D

**Validação estática (D2):**
```bash
file -b src/aracne_teleop/scripts/teleop_node.py src/aracne_bringup/scripts/teleop_bridge.py   # sem CRLF
git diff --ignore-cr-at-eol ...   # diff vazio = conteúdo lógico preservado
git diff --check escopado         # PASS
python3 -m py_compile ...         # PASS
```

**Validação de build:**
```bash
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install --packages-select aracne_simulation aracne_bringup
# Summary: 2 packages finished ...
```

**Evidências de runtime (fornecidas pelo operador):**
- `[INFO] [leg_kinematics_node-7]: process started ...`
- `[INFO] [teleop_node.py-8]: process started ...`; `[INFO] [teleop_bridge.py-9]: process started ...`
- `[ros_gz_bridge]: Creating GZ->ROS Bridge: [/clock (gz.msgs.Clock) -> /clock (rosgraph_msgs/msg/Clock)]`; sem `both ros_type_name and gz_type_name must be set`.
- `ros2 control list_controllers` → `joint_trajectory_controller ... active`; `joint_state_broadcaster ... active`.
- `/aracne/leg/joint_angles`: `sensor_msgs/msg/JointState`; **Publisher count: 1**; Subscription count: 0.
- `/joint_states`: `sensor_msgs/msg/JointState`; Publisher count: 1; Subscription count: 1; `leg1_coxa_joint`, `leg1_femur_joint`, `leg1_tibia_joint` (position/velocity).
- TF `leg1_base_link → leg1_coxa_link → leg1_femur_link → leg1_tibia_link`: sem regressão (cadeia validada em lote anterior, não atribuída ao D).

## Observações

- Lotes A, B, B.1, C e D do Mark I concluídos e validados.
- O Lote D resolveu: parse de `mark1_params.yaml` (D1), CRLF dos scripts Python (D2) e bridge legado `joint_angles` (D3).
- Problemas remanescentes (overlay/`AMENT_PREFIX_PATH`, `GZ_SIM_SYSTEM_PLUGIN_PATH`, warnings KDL/update-period, pipeline ponta-a-ponta de movimento) **não** são marcados como resolvidos — registrados em `TECH_DEBT.md`.
- A rastreabilidade dos Lotes A, B, B.1 e C permanece válida.


