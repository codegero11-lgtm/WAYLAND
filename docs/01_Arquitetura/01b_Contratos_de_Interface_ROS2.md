# 01b — Contratos de Interface ROS2

## Índice
1. Como usar este documento
2. Convenção de nomenclatura
3. Tabela viva de interfaces (por módulo)
4. Definições de mensagens customizadas (`aracne_msgs`)
5. Matriz de dependências entre módulos
6. Processo de mudança de contrato

---

## 1. Como Usar Este Documento

Este é um **documento vivo**: cada vez que um novo módulo (`04_Locomocao`, `05_Visao_Computacional`, etc.) for detalhado, a interface pública dele é adicionada aqui antes da implementação começar. Nenhum pacote pode publicar/assinar um tópico que não esteja listado nesta tabela — isso é o que torna R3 (baixo acoplamento) verificável, e não apenas uma intenção.

Estado atual: apenas os módulos do **Mark I** têm interface definida. As linhas dos módulos futuros aparecem como "placeholder" com o namespace reservado, para deixar claro onde cada um vai se encaixar.

## 2. Convenção de Nomenclatura

- Todo tópico/serviço/ação vive sob o namespace `/aracne/<modulo>/<nome>`.
- Tópicos: substantivos, `snake_case` (`/aracne/leg/joint_angles`).
- Serviços: verbo-ação, `snake_case` (`/aracne/leg/compute_ik`).
- Ações: gerúndio/processo longo, `snake_case` (`/aracne/nav/navigate_to_base`).
- QoS padrão: `reliable` + `volatile` para comandos; `best_effort` + `volatile` para streams de sensor de alta frequência (câmera, IMU) — exceções documentadas por módulo.

## 3. Tabela Viva de Interfaces

### Módulo `leg_kinematics` (pacote `aracne_leg_kinematics`) — ativo no Mark I

| Nome | Tipo | Direção | Mensagem | Descrição |
|---|---|---|---|---|
| `/aracne/leg/target_pose` | Tópico | IN | `aracne_msgs/LegTarget` | Ponto alvo (x, y, z) para a pata, em relação à origem do ombro da perna |
| `/aracne/leg/joint_angles` | Tópico | OUT | `sensor_msgs/JointState` | Ângulos calculados das 3 juntas (coxa/fêmur/tíbia), consumido pelo `ros2_control` |
| `/aracne/leg/compute_ik` | Serviço | IN/OUT | `aracne_msgs/ComputeIK` | Versão síncrona sob demanda do IK (retorna sucesso/falha + ângulos), usada em testes unitários e validação, sem precisar publicar em tópico |

### Módulo `teleop` (pacote `aracne_teleop`) — ativo no Mark I

| Nome | Tipo | Direção | Mensagem | Descrição |
|---|---|---|---|---|
| `/aracne/teleop/cmd` | Tópico | OUT | `aracne_msgs/TeleopCmd` | Comando manual de teste (delta x/y/z ou seleção de ponto pré-definido), gerado por teclado/GUI |

**Fluxo Mark I:** `teleop` publica em `/aracne/teleop/cmd` → um nó de bridge (dentro de `aracne_bringup`) traduz para `/aracne/leg/target_pose` → `leg_kinematics` calcula e publica `/aracne/leg/joint_angles` → `ros2_control` move a perna simulada.

---

### Placeholders — módulos futuros (namespace reservado, sem implementação)

| Módulo | Namespace reservado | Entra em |
|---|---|---|
| Locomoção (gait) | `/aracne/gait/*` | Mark II |
| Visão computacional | `/aracne/vision/*` | Mark futuro (após chassi físico + câmera) |
| IA / LLM local | `/aracne/dialogue/*` | Mark futuro |
| Navegação (Nav2) | `/aracne/nav/*` — provavelmente reaproveitando tópicos padrão do Nav2 (`/cmd_vel`, `/map`, etc.) em vez de reinventar | Mark futuro |
| Comandos de voz | `/aracne/voice/*` | Mark futuro |
| Energia/recarga | `/aracne/power/*` | Mark futuro |

> **Nota (arquitetural):** o antigo placeholder `/aracne/aerial/*` (módulo aéreo) foi **retirado** — não existe objetivo de voo. Interfaces mórficas futuras (`/aracne/morph/*`, `/aracne/spine/*`, `/aracne/mode/*`) **ainda não possuem contrato ROS definido** e permanecem **provisórias**; só serão adicionadas a esta tabela quando o módulo correspondente for detalhado.

Cada linha desta segunda tabela só "sobe" para a tabela principal (§3) quando o módulo correspondente for documentado em detalhe — evita definirmos interface para algo que ainda não foi pensado a fundo, o que costuma gerar retrabalho.

## 4. Definições de Mensagens Customizadas (`aracne_msgs`)

Especificação inicial (Mark I) — sintaxe `.msg`/`.srv`:

```
# LegTarget.msg
float64 x
float64 y
float64 z
string leg_id        # ex.: "leg1" — identifica a perna; papel morfológico futuro ainda SEM contrato ROS definido
```

```
# ComputeIK.srv
float64 x
float64 y
float64 z
---
bool success
float64[] joint_angles   # [coxa, femur, tibia] em radianos
string error_message     # preenchido só se success = false (ex.: "ponto fora do alcance")
```

```
# TeleopCmd.msg
float64 delta_x
float64 delta_y
float64 delta_z
```

Nota de design: `LegTarget` já inclui `leg_id` desde o Mark I, mesmo só existindo 1 perna — o identificador canônico atual é **`leg1`** (sem underscore), consistente com o código, URDF/xacro e testes. Isso evita quebrar a mensagem (e todo código que a consome) quando o número de pernas e sua organização morfológica forem definidos. É uma aplicação direta de R6/R1: pagar um custo mínimo agora para não ter que reescrever depois.

## 5. Matriz de Dependências entre Módulos

| Módulo | Depende de | Não depende de |
|---|---|---|
| `leg_kinematics` | `aracne_msgs` | `teleop`, Gazebo diretamente (só via tópicos) |
| `teleop` | `aracne_msgs` | `leg_kinematics` diretamente (só via tópicos) |
| `aracne_bringup` | Todos os pacotes de módulo (só para orquestrar launch) | — |

Esta matriz é o que garante R3 na prática: se alguém for adicionar um `#include`/`import` que não está listado aqui, é sinal de acoplamento indevido.

## 6. Processo de Mudança de Contrato

Regra para evitar que a "tabela viva" vire fonte de bugs silenciosos:

1. Nenhuma mensagem existente é alterada de forma incompatível (remover/renomear campo) sem versionar (`LegTarget` → `LegTargetV2`) — o consumidor antigo continua funcionando até ser migrado.
2. Toda adição de campo novo deve ter valor padrão sensato (não pode quebrar quem já publica a mensagem antiga).
3. Mudança de contrato = atualização obrigatória deste documento **no mesmo commit** que a mudança de código.

---

*Próximo documento sugerido: `03_Simulacao/03a_Ambiente_Gazebo.md` + `03b_Modelo_URDF_Xacro.md` — com as mensagens e o namespace já travados aqui, é o que falta para o Mark I sair do papel.*