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
| TD-001 | Validação de ponta a ponta do Gazebo e dos controllers (`ros2_control`, `joint_trajectory_controller`, `spawner`) ainda pendente | Pode bloquear Lote C | Alta | Lote B/C | Aberta |

## Observações

- A duplicação do controller manager (`ros2_control_node` independente no launch) foi **resolvida** durante o Lote B — o controller manager único agora é fornecido pelo `gz_ros2_control` no Gazebo. Esta parcela não é mais dívida.
- A TD-001 foi atualizada para refletir que resta validar o funcionamento de Ponta a ponta do Gazebo/controllers (não apenas a eliminação da duplicação).
- Nenhuma dívida técnica nova foi criada durante esta correção.
- Modificações pré-existentes fora do escopo não foram incluídas na entrega.

