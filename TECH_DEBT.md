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
| TD-001 | Validação de ponta a ponta do Gazebo no runtime: rodar o sim, `spawn` do Mark I, `robot_state_publisher`, broadcasters, ativação de controllers (`joint_trajectory_controller`, `spawner`) | Pode bloquear o Lote C | Alta | Lote C | Aberta |

## Dívidas encerradas

| ID | Descrição | Resolvido em | Status |
|---|---|---|---|
| TD-B-01 | Duplicação do controller manager — `ros2_control_node` independente removido; controller manager único fornecido pelo `gz_ros2_control` | Lote B / B.1 | Encerrada |
| TD-B-02 | Integração estrutural `gz_ros2_control` com nomes desatualizados — hardware plugin e plugin Gazebo alinhados ao Jazzy/Harmonic (`GazeboSimSystem`, `libgz_ros2_control-system.so`, `GazeboSimROS2ControlPlugin`) | Lote B.1 | Encerrada |
| TD-B-03 | Xacro não processava por falha estrutural de macro/include (`leg_prefix` indefinido) — corrigido com `<robot>` raiz + `$(arg ...)` | Lote B.1 | Encerrada |

## Observações

- O **funcionamento do Gazebo em runtime** (spawn, controllers em execução) ainda **NÃO** está validado — permanece na TD-001 (Lote C).
- Nenhuma dívida técnica foi registrada por causa de whitespace/formatação.
- Nenhuma dívida técnica nova foi criada durante o fechamento do Lote B.1.
- Modificações pré-existentes fora do escopo não foram incluídas na entrega.

