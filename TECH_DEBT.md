# WAYLAND — Technical Debt

## Regras

Toda dívida deve ter:

- ID;
- descrição;
- impacto;
- prioridade;
- resolver em;
- status.

## Dívidas atuais

| ID | Descrição | Impacto | Prioridade | Resolver em | Status |
|---|---|---|---|---|---|
| TD-002 | `mark1_params.yaml` não está no formato de parâmetros ROS2 padrão (`ros__parameters`): `leg_kinematics_node` falha no parse (`Cannot have a value before ros__parameters at line 2`). Requer definir o formato esperado pelo nó (parâmetros custom via `leg_dimensions:` ou wrapper `ros__parameters:`). | `leg_kinematics_node` não inicia no bringup | Alta | Próximo lote | Aberta |
| TD-003 | CRLF nos scripts Python `aracne_teleop/scripts/teleop_node.py` e `aracne_bringup/scripts/teleop_bridge.py` — shebang com `\r` causa `/usr/bin/env: 'python3\r': No such file or directory`. | teleop e bridge de teleop não iniciam | Alta | Próximo lote | Aberta |
| TD-004 | Bridge legado `/aracne/leg/joint_angles` no `bridge_mark1.yaml` está inválido (falta `gz_type_name` → "both ros_type_name and gz_type_name must be set"). Não afetou `/clock`; bridge de joint_angles não criado. | Joint states GZ→ROS não bridgados; entrada legada inválida | Média | Próximo lote | Aberta |
| TD-005 | Overlay: `source /mnt/c/WAYLAND/install/setup.bash` não adicionava todos os pacotes ao `AMENT_PREFIX_PATH`; foi necessário source explícito de `local_setup.bash` de `aracne_bringup`, `aracne_leg_kinematics`, `aracne_teleop`. | Sourcing parcial; nodes podem não ser encontrados | Média | Ambiente/próximo lote | Aberta |
| TD-006 | `libgz_ros2_control-system.so` exige `export GZ_SIM_SYSTEM_PLUGIN_PATH=/opt/ros/jazzy/lib` para ser localizado pelo spawn do Mark I. Sem workaround permanente no launch (por decisão de escopo). | gz_ros2_control não carrega sem env var | Média | Decisão consciente / documentar | Aberta |
| TD-007 | `robot_state_publisher` warning: KDL não suporta root link com inertia (`leg1_base_link`). Não bloqueia TF. | Warning cosmético | Baixa | Adiar | Aberta |
| TD-808 | Controller update period (0.01 s) mais lento que o Gazebo sim period (0.001 s). Não alterado (decisão de escopo). | Transientes de controle; não bloqueante | Baixa | Adiar | Aberta |
| TD-009 | `/joint_states` publica `effort` como `.nan` (interfaces atuais: state position/velocity, command position). Coerente com configuração; sem camada de esforço. | Não bloqueante; documentado | Baixa | Fora do escopo | Aberta |
## Dívidas encerradas

| ID | Descrição | Resolvido em | Status |
|---|---|---|---|
| TD-B-01 | Duplicação do controller manager — `ros2_control_node` independente removido; controller manager único fornecido pelo `gz_ros2_control` | Lote B / B.1 | Encerrada |
| TD-B-02 | Integração estrutural `gz_ros2_control` com nomes desatualizados — hardware plugin e plugin Gazebo alinhados ao Jazzy/Harmonic (`GazeboSimSystem`, `libgz_ros2_control-system.so`, `GazeboSimROS2ControlPlugin`) | Lote B.1 | Encerrada |
| TD-B-03 | Xacro não processava por falha estrutural de macro/include (`leg_prefix` indefinido) — corrigido com `<robot>` raiz + `$(arg ...)` | Lote B.1 | Encerrada |
| TD-001 | Validação de ponta a ponta do Gazebo no runtime (spawn do Mark I, `robot_state_publisher`, broadcasters, ativação de controllers) | Lote C | Encerrada |

## Observações

- A TD-001 foi encerrada: o núcleo de simulação do Mark I foi validado em runtime no Lote C (mundo abre, Mark I spawnado, `joint_state_broadcaster`/`joint_trajectory_controller` ativos, `/joint_states` e TF OK).
- As dívidas TD-002 a TD-009 refletem problemas observados em runtime que **não** foram corrigidos automaticamente e devem ser tratados no próximo lote.
- Nenhuma dívida técnica foi registrada por causa de whitespace/formatação.
- Nenhuma dependência nova foi introduzida.

