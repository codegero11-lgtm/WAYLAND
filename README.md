# Projeto Aracne - Mark I

Repositório ROS2 para o robô Aracne Mark I, incluindo modelagem URDF/Xacro, cinemática inversa e bringup de simulação Gazebo.

## Organização

- `docs/` — documentação de arquitetura, requisitos e bringup.
- `src/aracne_description/` — robot description em Xacro/URDF e parâmetros de dimensões.
- `src/aracne_simulation/` — mundo Gazebo e bridge ROS <-> Ignition Gazebo.
- `src/aracne_leg_kinematics/` — pacote C++ com solver de cinemática inversa e nó ROS2.
- `src/aracne_teleop/` — pacote Python com nó de teleop simples.
- `src/aracne_bringup/` — launch file, configuração de controllers e bridge de teleop.
- `src/aracne_msgs/` — mensagens e serviços customizados.

## Requisitos

- ROS2 (Jazzy ou compatível com `ament_cmake`/`ament_python`)
- `ros_gz_bridge`
- `ros2_control` e `controller_manager`
- `xacro`
- Gazebo / Ignition Gazebo compatível

## Build

Execute a partir da raiz do repositório:

```bash
cd c:/WAYLAND
colcon build --symlink-install
```

Depois do build, carregue o ambiente:

```bash
. install/setup.bash
```

> No Windows PowerShell, use `.uild.ps1` ou `Set-ExecutionPolicy` se necessário para carregar o ambiente ROS2 local.

## Execução

O lançamento principal é feito por:

```bash
ros2 launch aracne_bringup mark1.launch.py
```

Esse launch inicia:

- mundo Gazebo Mark I (`aracne_simulation`)
- bridge `ros_gz_bridge`
- `ros2_control_node` com `joint_trajectory_controller`
- nó de cinemática inversa `aracne_leg_kinematics`
- nó de teleop `aracne_teleop`
- nó de ponte `aracne_bringup/teleop_bridge.py`

## Pacotes ROS2

- `aracne_msgs`: mensagens customizadas `TeleopCmd` e `LegTarget`, serviço `ComputeIK`.
- `aracne_description`: descrição da perna em Xacro, parâmetros de limite e comprimento.
- `aracne_simulation`: world SDF e configuração da bridge ROS.
- `aracne_leg_kinematics`: solver IK e nó para publicar ângulos de junta.
- `aracne_teleop`: publisher simples para comandos de teleop.
- `aracne_bringup`: orquestração de launch e integração com controllers.

## Uso básico

1. Build e source o workspace.
2. Lance o sistema com `ros2 launch aracne_bringup mark1.launch.py`.
3. Publicar em `/aracne/teleop/cmd` usando `aracne_msgs/TeleopCmd`.

Exemplo de comando ROS2:

```bash
ros2 topic pub /aracne/teleop/cmd aracne_msgs/msg/TeleopCmd "{delta_x: 0.05, delta_y: 0.0, delta_z: -0.02}"
```

## Observações

- O nó de teleop publica comandos de deslocamento para a perna.
- A `teleop_bridge` converte esses comandos em destino de perna (`LegTarget`).
- O nó de cinemática inversa resolve os ângulos de junta e publica em `/aracne/leg/joint_angles`.

## Próximos passos

- Adicionar mais pernas e controle de corpo completo.
- Refinar limites de junta e dinâmica de controle.
- Validar em simulação Gazebo com `ros2_control` e controllers reais.
