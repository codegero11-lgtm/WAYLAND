# 03a — Ambiente de Simulação (Gazebo)

## Índice
1. Objetivo
2. Versão do Gazebo e integração com ROS2
3. Estrutura de pacotes de simulação
4. Mundo (world) do Mark I
5. Física e parâmetros de simulação
6. Bridge ROS2 ↔ Gazebo (`ros_gz`)
7. Sensores simulados (visão de futuro, sem implementar agora)
8. Fluxo de execução (launch)
9. Riscos e mitigação
10. Critérios de sucesso
11. Testes necessários

---

## 1. Objetivo

Definir o ambiente de simulação física que serve de base para **todos** os Marks — não só o Mark I. Este documento não é "simulação da perna", é "como o projeto simula qualquer coisa", para não ter que redefinir isso a cada Mark.

## 2. Versão do Gazebo e Integração com ROS2

**Decisão:** Gazebo Harmonic (versão atual do Gazebo "novo", ex-Ignition), integrado via `ros_gz` — pacote oficial de bridge para ROS2 Jazzy.

**Justificativa:** Jazzy e Gazebo Harmonic são a combinação recomendada oficialmente pela documentação do ROS2 para esta geração de LTS; usar o Gazebo Classic (11) seria adotar uma linha que já está em fim de vida.

## 3. Estrutura de Pacotes de Simulação

```
aracne_ws/src/
└── aracne_simulation/
    ├── worlds/
    │   └── mark1_lab.sdf          # mundo mínimo do Mark I
    ├── launch/
    │   └── gazebo_mark1.launch.py
    ├── config/
    │   └── bridge_mark1.yaml      # config do ros_gz_bridge (quais tópicos passam)
    └── models/                    # modelos SDF auxiliares (bancada, alvo visual, etc.)
```

Este pacote é **separado** de `aracne_description` (que guarda o URDF/Xacro do robô em si — ver `03b`). Justificativa: o mesmo robô (`aracne_description`) deve poder ser carregado em mundos diferentes sem duplicar a descrição do robô; e o mesmo mundo pode, futuramente, testar versões diferentes do robô lado a lado.

## 4. Mundo (World) do Mark I

Mundo propositalmente mínimo: `mark1_lab.sdf`
- Chão plano com física de contato/atrito definida (necessário para a pata "sentir" o chão nos Marks seguintes, mesmo que o Mark I não use isso ainda — a bancada da perna fica suspensa/fixa)
- Iluminação básica (necessária futuramente quando câmera simulada entrar em cena — nenhum retrabalho depois)
- Um ponto de fixação (`fixed_joint` a um `world_link`) onde a base da perna é montada, simulando a "bancada de testes" de uma perna isolada

Não incluído neste Mark: obstáculos, texturas realistas de terreno, múltiplas salas — isso é do escopo de Marks com navegação (`07_Navegacao`).

## 5. Física e Parâmetros de Simulação

| Parâmetro | Valor Mark I | Justificativa |
|---|---|---|
| Motor de física | `ode` (padrão Gazebo Harmonic) | Suficiente para simulação de junta com poucos graus de liberdade; DART fica reservado para quando o octápode completo (contato multi-perna) exigir mais estabilidade |
| Passo de simulação (`step size`) | 0.001s (1kHz) | Padrão recomendado para controle de junta com `ros2_control` sem instabilidade numérica |
| Real time factor alvo | 1.0 (tempo real) | Necessário porque o teleop do Mark I é interativo; simulações aceleradas (>1.0) ficam reservadas para treino/testes automatizados futuros |

Estes parâmetros são revisados (não necessariamente alterados) a cada Mark que adicione complexidade física — registrado em `03c_Pipeline_Sim2Real.md`.

## 6. Bridge ROS2 ↔ Gazebo (`ros_gz`)

O `ros_gz_bridge` traduz entre tópicos nativos do Gazebo (formato Gazebo Transport) e tópicos ROS2. Regra de projeto: **o bridge só expõe o que está listado em `01b_Contratos_de_Interface_ROS2.md`** — nenhum tópico interno do Gazebo vaza para o resto do sistema sem estar documentado ali primeiro.

`bridge_mark1.yaml` (conteúdo conceitual):
```yaml
# Mark I: só o necessário para joint states da perna
- ros_topic_name: "/aracne/leg/joint_angles"
  gz_topic_name: "/model/aracne_leg/joint_state"
  ros_type_name: "sensor_msgs/msg/JointState"
  direction: GZ_TO_ROS
```

## 7. Sensores Simulados (referência futura, não implementar agora)

Só para deixar registrado onde cada sensor vai entrar, sem implementar no Mark I:
- Câmera simulada (plugin `gz-sensors-camera`) → alimenta `05_Visao_Computacional`
- IMU simulada → alimenta futuro módulo de equilíbrio/gait avançado
- LiDAR simulado (`gz-sensors-gpu-lidar`) → alimenta `07_Navegacao`

## 8. Fluxo de Execução (launch)

```
ros2 launch aracne_bringup mark1.launch.py
```
que internamente sobe, nesta ordem:
1. `gazebo_mark1.launch.py` (mundo + robô carregado)
2. `ros_gz_bridge` com `bridge_mark1.yaml`
3. `ros2_control` + controller da perna
4. Nó de `leg_kinematics`
5. Nó de `teleop`

## 9. Riscos e Mitigação

| Risco | Mitigação |
|---|---|
| Driver gráfico AMD (RX 7800 XT) com problemas de renderização em Gazebo Harmonic no Ubuntu 24.04 | Validar `glxinfo`/Vulkan antes de instalar Gazebo; se houver problema, usar renderização por software (`ogre2` fallback) apenas para debug, sem travar o desenvolvimento |
| Passo de simulação a 1kHz gerar uso alto de CPU | Aceitável no Mark I (1 junta); reavaliar quando o octápode completo (24 juntas) estiver simulado |

## 10. Critérios de Sucesso

- [ ] `ros2 launch aracne_bringup mark1.launch.py` sobe o mundo `mark1_lab.sdf` com a perna visível em Gazebo
- [ ] `ros2 topic echo /aracne/leg/joint_angles` mostra dados vindos do Gazebo via bridge
- [ ] Real time factor se mantém próximo de 1.0 durante a operação

## 11. Testes Necessários

- **Integração:** subir o launch completo do zero em máquina limpa (checklist de dependências documentado em `01a`)
- **Regressão:** após qualquer mudança em `bridge_mark1.yaml`, confirmar que os tópicos de `01b` continuam sendo publicados com o tipo correto

---

*Próximo documento: `03b_Modelo_URDF_Xacro.md` — a descrição física da perna que este mundo carrega.*
