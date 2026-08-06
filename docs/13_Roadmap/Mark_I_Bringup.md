# 01c* — Bringup e Testes de Integração (Mark I)

*(nota de indexação: este documento fecha o Mark I; recomendo arquivá-lo como `13_Roadmap/Mark_I_Bringup.md`, complementando o `Mark_I.md` já produzido)*

## Índice
1. Objetivo
2. Pré-requisitos de ambiente (checklist)
3. Estrutura final do `aracne_bringup` (Mark I)
4. `mark1.launch.py` — especificação de ordem e dependência de nós
5. Checklist de verificação manual (smoke test)
6. Plano de testes de integração automatizados
7. Critério de "Mark I concluído"
8. Procedimento de troubleshooting (erros esperados)
9. Handoff para implementação (nota para o DeepSeek)

---

## 1. Objetivo

Este é o documento que amarra `01a` (arquitetura), `01b` (contratos), `03a`/`03b` (simulação) e `04a` (IK) em um sistema executável único, e define como validar que o Mark I está de fato completo — não "os módulos existem", mas "o sistema roda de ponta a ponta e atende aos critérios de sucesso".

## 2. Pré-requisitos de Ambiente (checklist)

Antes de tentar rodar qualquer coisa, confirmar:

- [ ] Ubuntu 24.04 LTS instalado nativamente (dual boot conforme decisão registrada)
- [ ] ROS2 Jazzy instalado e `source /opt/ros/jazzy/setup.bash` funcionando
- [ ] Gazebo Harmonic instalado, `gz sim` abre sem erro
- [ ] `ros_gz` (bridge) instalado para Jazzy
- [ ] Driver gráfico AMD (RX 7800 XT) funcional — validar com `glxinfo | grep "OpenGL renderer"` mostrando a GPU, não renderização por software
- [ ] `colcon` instalado, `aracne_ws` compila (`colcon build` sem erros)
- [ ] `xacro`, `ros2_control`, `ros2_controllers`, `gz_ros2_control` instalados

Esta lista é o que qualquer pessoa (você, ou o próprio DeepSeek antes de gerar código) deve confirmar antes de reportar qualquer bug — evita perder tempo depurando "bug" que na verdade é ambiente incompleto.

## 3. Estrutura Final do `aracne_bringup` (Mark I)

```
aracne_bringup/
├── launch/
│   └── mark1.launch.py
├── config/
│   ├── mark1_params.yaml       # agrega leg_dimensions.yaml + params de controle
│   └── bridge_mark1.yaml       # já definido em 03a
└── test/
    └── test_mark1_integration.py
```

## 4. `mark1.launch.py` — Especificação de Ordem e Dependência de Nós

Ordem obrigatória (dependência real entre os componentes, não arbitrária):

1. **Gazebo + mundo** (`aracne_simulation/launch/gazebo_mark1.launch.py`) — precisa existir antes de tudo, é onde o robô é carregado
2. **`ros_gz_bridge`** com `bridge_mark1.yaml` — precisa do Gazebo já rodando para encontrar os tópicos nativos
3. **`ros2_control_node`** + spawn do `joint_trajectory_controller` — precisa do robô carregado no Gazebo (via `gz_ros2_control`) para encontrar as interfaces de hardware
4. **`leg_kinematics_node`** — não depende dos anteriores para *iniciar*, mas só é útil com eles rodando
5. **`teleop_node`** — último, é a interface de entrada do usuário

Uso de `event_handler`/`TimerAction` no launch Python para garantir 1→2→3 em sequência (Gazebo demora a inicializar); 4 e 5 podem subir em paralelo após o passo 3.

## 5. Checklist de Verificação Manual (Smoke Test)

Sequência manual para confirmar que "está tudo vivo", antes de rodar testes automatizados:

1. `ros2 launch aracne_bringup mark1.launch.py`
2. Gazebo abre com a perna visível na bancada (`mark1_lab.sdf`)
3. `ros2 node list` mostra todos os nós esperados (bridge, controller manager, leg_kinematics, teleop)
4. `ros2 topic list` contém exatamente os tópicos definidos em `01b` para o Mark I — nenhum a mais, nenhum a menos
5. `ros2 service call /aracne/leg/compute_ik aracne_msgs/srv/ComputeIK "{x: 0.1, y: 0.0, z: -0.15}"` retorna `success: true` com ângulos plausíveis
6. Publicar manualmente em `/aracne/teleop/cmd` e observar a perna se mover em Gazebo

## 6. Plano de Testes de Integração Automatizados

`test_mark1_integration.py` (usando `launch_testing`, padrão ROS2):

| Teste | O que valida |
|---|---|
| `test_all_nodes_alive` | Todos os nós do §4 aparecem em `ros2 node list` dentro de um timeout (ex.: 15s) |
| `test_topics_match_contract` | O conjunto de tópicos ativos é exatamente o subconjunto do Mark I listado em `01b` (detecta tanto tópico faltando quanto vazamento de tópico não documentado) |
| `test_ik_service_reachable_point` | Chamada ao `/aracne/leg/compute_ik` com ponto alcançável retorna `success=true` |
| `test_ik_service_unreachable_point` | Chamada com ponto fora do alcance retorna `success=false` com `error_message` não vazio |
| `test_target_to_joint_state_pipeline` | Publicar em `/aracne/leg/target_pose` resulta, dentro de um timeout, em mensagem correspondente em `/aracne/leg/joint_angles` com os ângulos esperados (comparado contra `ik_solver` chamado diretamente) |

## 7. Critério de "Mark I Concluído"

O Mark I só é considerado pronto quando **todos** os itens abaixo são verdadeiros simultaneamente (consolidando os critérios de sucesso espalhados em `01a`, `03a`, `03b`, `04a`):

- [ ] Checklist de ambiente (§2) 100% atendido
- [ ] Smoke test manual (§5) executado com sucesso
- [ ] Todos os testes automatizados (§6) passando
- [ ] Nenhum pacote viola a matriz de dependências de `01b §5` (revisão manual de imports)
- [ ] Documentação de `01b` atualizada se qualquer tópico/mensagem mudou durante a implementação (regra do processo de mudança de contrato)

## 8. Procedimento de Troubleshooting (erros esperados)

| Sintoma | Causa provável | Ação |
|---|---|---|
| Gazebo abre mas perna não aparece | Xacro não processado corretamente ou path de mesh errado | Rodar `xacro aracne.xacro` isoladamente e inspecionar erro |
| `ros2 topic list` não mostra `/aracne/leg/joint_angles` | Bridge mal configurado ou nome de tópico Gazebo divergente do `bridge_mark1.yaml` | Conferir nome exato do tópico nativo com `gz topic -l` |
| Perna se move de forma "invertida" ou colide com a base | Convenção de sinal do IK (`θ3` joelho para trás) não bate com os limites de junta do URDF | Revisar Passo 4 de `04a` contra os limites definidos em `03b §4` |
| Renderização falha / tela preta no Gazebo | Driver AMD com problema de Vulkan/OpenGL | Fallback `ogre2` por software, só para debug (ver risco já registrado em `03a §9`) |

## 9. Handoff Para Implementação (nota para o DeepSeek)

Este conjunto de documentos (`00`, `01a`, `01b`, `03a`, `03b`, `04a`, e este) é **suficiente e completo** para implementar o Mark I sem decisões de arquitetura pendentes. Ordem de implementação recomendada, que espelha a ordem de dependência real:

1. `aracne_msgs` (mensagens, `01b §4`)
2. `aracne_description` (URDF/Xacro, `03b`)
3. `aracne_simulation` (mundo Gazebo, `03a`)
4. `aracne_leg_kinematics` (IK, `04a`)
5. `aracne_teleop` (comando manual)
6. `aracne_bringup` (amarra tudo, este documento)

Qualquer decisão de implementação **não coberta explicitamente** nestes documentos (ex.: detalhe de formatação de código, escolha entre duas bibliotecas equivalentes para uma tarefa trivial) deve ser resolvida pelo bom senso do implementador, mas **nenhuma decisão de interface, nome de tópico, ou estrutura de pacote deve divergir** do que está aqui sem atualizar a documentação primeiro.

---

**Mark I: documentação completa.** Próximo passo é o `Mark II` (`13_Roadmap/Mark_II.md` + `04b_Geracao_de_Gait.md`, estendendo para as 8 pernas), quando você quiser seguir.
