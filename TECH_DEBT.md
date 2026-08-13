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
| TD-005 | Overlay: `source /mnt/c/WAYLAND/install/setup.bash` não adicionava todos os pacotes ao `AMENT_PREFIX_PATH`; foi necessário source explícito de `local_setup.bash` de `aracne_bringup`, `aracne_leg_kinematics`, `aracne_teleop`. | Sourcing parcial; nodes podem não ser encontrados | Média | Ambiente/próximo lote | Aberta |
| TD-006 | `libgz_ros2_control-system.so` exige `export GZ_SIM_SYSTEM_PLUGIN_PATH=/opt/ros/jazzy/lib` para ser localizado pelo spawn do Mark I. Sem workaround permanente no launch (por decisão de escopo). | gz_ros2_control não carrega sem env var | Média | Decisão consciente / documentar | Aberta |
| TD-007 | `robot_state_publisher` warning: KDL não suporta root link com inertia (`leg1_base_link`). Não bloqueia TF. | Warning cosmético | Baixa | Adiar | Aberta |
| TD-008 | Controller update period (0.01 s) mais lento que o Gazebo sim period (0.001 s). Não alterado (decisão de escopo). | Transientes de controle; não bloqueante | Baixa | Adiar | Aberta |
| TD-009 | `/joint_states` publica `effort` como `.nan` (interfaces atuais: state position/velocity, command position). Coerente com configuração; sem camada de esforço. | Não bloqueante; documentado | Baixa | Fora do escopo | Aberta |
| TD-011 | `controller_manager`: "Enforcing command limits is disabled. Command limits from URDF will be ignored." O controller manager não está aplicando os command limits do URDF; hoje as validações de limites são feitas pelo `joint_trajectory_bridge` (REJECT) e pela IK. | Sem camada de enforce de limites no controller; risco antes da evolução para hardware | Média | Antes de evolução para hardware | Aberta |
| TD-012 | E4.5 risk acceptance: `goal timeout / stuck goal` e `DISARM != E-STOP` permanecem documentados como riscos aceitos para Mark I em simulação, não como falhas resolvidas. Requer recovery/timeout robusto e E-STOP real antes de hardware. | Segurança e recuperação do ciclo de comando não estão fechados para operação física; mitigação atual é simulação-adequada | Média | Antes de hardware real | Aberta |
## Dívidas encerradas

| ID | Descrição | Resolvido em | Status |
|---|---|---|---|
| TD-B-01 | Duplicação do controller manager — `ros2_control_node` independente removido; controller manager único fornecido pelo `gz_ros2_control` | Lote B / B.1 | Encerrada |
| TD-B-02 | Integração estrutural `gz_ros2_control` com nomes desatualizados — hardware plugin e plugin Gazebo alinhados ao Jazzy/Harmonic (`GazeboSimSystem`, `libgz_ros2_control-system.so`, `GazeboSimROS2ControlPlugin`) | Lote B.1 | Encerrada |
| TD-B-03 | Xacro não processava por falha estrutural de macro/include (`leg_prefix` indefinido) — corrigido com `<robot>` raiz + `$(arg ...)` | Lote B.1 | Encerrada |
| TD-001 | Validação de ponta a ponta do Gazebo no runtime (spawn do Mark I, `robot_state_publisher`, broadcasters, ativação de controllers) | Lote C | Encerrada |
| TD-002 | `mark1_params.yaml` fora do formato ROS2 (`Cannot have a value before ros__parameters`) — estruturado em `leg_kinematics_node: ros__parameters:` | Lote D | Encerrada |
| TD-003 | CRLF nos scripts `teleop_node.py` e `teleop_bridge.py` (`python3\r`) — normalizado CRLF→LF | Lote D | Encerrada |
| TD-004 | Bridge legado `/aracne/leg/joint_angles` (falta `gz_type_name`; redundante; referência desatualizada) — entrada removida; `/clock` preservado | Lote D | Encerrada |
| TD-010 | Pipeline ponta-a-ponta de movimento **não comprovado** — validado no Lote E (E3): target → IK → joint angles → FollowJointTrajectory → goal ACCEPTED/SUCCEEDED → feedback coerente em `/joint_states` | Lote E | Encerrada |

## Observações

- A TD-001 foi encerrada: o núcleo de simulação do Mark I foi validado em runtime no Lote C (mundo abre, Mark I spawnado, `joint_state_broadcaster`/`joint_trajectory_controller` ativos, `/joint_states` e TF OK).
- As dívidas TD-002, TD-003 e TD-004 foram encerradas no Lote D (saneamento de parâmetros, CRLF e bridge legado). `/clock` e controllers permanecem ativos após o Lote D.
- As dívidas TD-005, TD-006, TD-007, TD-008, TD-009 e TD-011 **não** foram resolvidas por este fechamento — permanecem **Abertas**.
- A TD-010 (pipeline ponta-a-ponta de movimento) foi **validada e encerrada** no Lote E (E3).
- A TD-011 registra o warning do `controller_manager` ("Enforcing command limits is disabled/ignored"); não corrigido nesta etapa — a ser investigado antes da evolução para hardware.
- Nenhum warning (ex.: KDL, update period) foi resolvido apenas por ter aparecido no runtime — no fechamento documental não se corrigem warnings.
- Nenhuma dívida técnica foi registrada por causa de whitespace/formatação.
- Nenhuma dependência nova foi introduzida.

