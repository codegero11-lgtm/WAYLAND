# 03b — Modelo URDF/Xacro

## Índice
1. Objetivo
2. Por que Xacro e não URDF puro
3. Estrutura de arquivos
4. Definição cinemática da perna (Mark I)
5. Parametrização (YAML → Xacro)
6. Integração com `ros2_control`
7. Convenção de frames (`tf2`)
8. Preparação para Mark II (8 pernas) sem retrabalho
9. Riscos e mitigação
10. Critérios de sucesso
11. Testes necessários

---

## 1. Objetivo

Definir a descrição física (geometria, juntas, massas, inércias) da perna do Mark I de forma que:
- Sirva de base direta para as 8 pernas do Mark II (via parametrização, não cópia manual)
- Seja a mesma descrição usada depois no chassi físico real (mesmos nomes de junta/link, para não quebrar `01b`)

## 2. Por Que Xacro e Não URDF Puro

URDF puro não tem variáveis, loops nem macros — descrever 8 pernas idênticas exigiria copiar/colar XML 8 vezes, violando a filosofia de manutenibilidade do projeto. Xacro resolve isso com macros parametrizadas (`xacro:macro`), permitindo definir "uma perna" uma vez e instanciá-la N vezes com parâmetros diferentes (posição de montagem, espelhamento esquerda/direita).

## 3. Estrutura de Arquivos

```
aracne_description/
├── urdf/
│   ├── aracne.xacro           # arquivo raiz (Mark I: só a perna + base fixa)
│   ├── leg.xacro              # macro reutilizável da perna (usada 1x no Mark I, 8x no Mark II)
│   └── materials.xacro        # cores/materiais visuais
├── meshes/
│   └── (STL exportados da modelagem 3D, quando existirem — Mark I pode usar geometria primitiva)
└── config/
    └── leg_dimensions.yaml    # comprimentos de segmento, limites de junta
```

## 4. Definição Cinemática da Perna (Mark I)

3 graus de liberdade em cadeia serial, nomenclatura fixada aqui (usada em todo o projeto daqui em diante):

| Junta | Nome | Eixo | Tipo | Faixa (a calibrar) |
|---|---|---|---|---|
| Coxa (hip) | `leg1_coxa_joint` | Z (rotação horizontal) | revolute | -90° a +90° |
| Fêmur | `leg1_femur_joint` | Y (elevação) | revolute | -45° a +90° |
| Tíbia | `leg1_tibia_joint` | Y (extensão) | revolute | -120° a 0° |

Links: `leg1_base_link` → `leg1_coxa_link` → `leg1_femur_link` → `leg1_tibia_link` (a "pata" é a ponta do `tibia_link`, sem link adicional no Mark I — sensor de contato na pata fica para Mark futuro).

Geometria no Mark I: cilindros/caixas primitivas (não é preciso mesh 3D real ainda) — evita bloquear a simulação esperando modelagem 3D definitiva, que só faz sentido travar quando o chassi físico for desenhado (`02a_Chassi_e_Estrutura`).

## 5. Parametrização (YAML → Xacro)

`leg_dimensions.yaml`:
```yaml
leg:
  coxa_length: 0.05      # metros
  femur_length: 0.09
  tibia_length: 0.11
  joint_limits:
    coxa: {lower: -1.57, upper: 1.57}
    femur: {lower: -0.78, upper: 1.57}
    tibia: {lower: -2.09, upper: 0.0}
```

O `leg.xacro` lê esses valores como propriedades Xacro (`xacro:property`) carregadas via `$(find aracne_description)/config/leg_dimensions.yaml` no launch, nunca com números fixos direto no XML — esta é a mesma regra de "configuração > código" de `01a`, aplicada à geometria.

## 6. Integração com `ros2_control`

Tag `<ros2_control>` no Xacro define:
- 1 interface de comando por junta (`position`)
- 1 interface de estado por junta (`position`, `velocity`)
- Plugin de hardware: no Mark I, `gz_ros2_control/GazeboSimSystem` (simulado); no Mark futuro com hardware real, será trocado por um plugin customizado que fala com os servos via ESP32 — **sem alterar o restante do URDF**, só essa seção. Esse é exatamente o ponto de troca simulação→real descrito em `03c` (a produzir).

## 7. Convenção de Frames (`tf2`)

- `world` → `leg1_base_link` (fixo, junta tipo `fixed`) → cadeia da perna acima.
- Todo frame novo introduzido por sensores futuros (câmera, IMU, LiDAR) deve se ancorar em um link já existente nesta árvore — nunca criar uma árvore `tf` paralela.

## 8. Preparação para Mark II (8 pernas) Sem Retrabalho

O `leg.xacro` já é escrito como macro parametrizada por `prefix` (ex.: `leg1`, `leg2`...) e `mount_position`/`mount_yaw` (onde e com que rotação a perna se monta no chassi). No Mark I, `aracne.xacro` instancia a macro **uma única vez**. No Mark II, instancia 8 vezes com parâmetros de montagem diferentes — nenhuma mudança na macro em si, só no arquivo raiz. Isso é a aplicação concreta de R1: o Mark II reaproveita 100% do trabalho do Mark I.

## 9. Riscos e Mitigação

| Risco | Mitigação |
|---|---|
| Massas/inércias mal estimadas causando comportamento instável na simulação | Mark I usa geometria primitiva com densidade padrão de material plástico (~1.2 g/cm³); recalibrar quando o modelo 3D real existir |
| Limites de junta definidos "no chute" não corresponderem aos servos reais | Documentado explicitamente como placeholder a recalibrar em `02b_Atuadores_e_Servos`, nunca tratado como valor final |

## 10. Critérios de Sucesso

- [ ] `aracne.xacro` processa sem erro (`xacro aracne.xacro > /tmp/check.urdf` válido)
- [ ] Perna aparece corretamente articulada em Gazebo e RViz2 (mesma pose em ambos)
- [ ] Alterar um valor em `leg_dimensions.yaml` muda o tamanho da perna sem editar nenhum `.xacro`
- [ ] `ros2 control list_hardware_interfaces` mostra as 3 juntas com interface de posição

## 11. Testes Necessários

- **Unitário:** validação de sintaxe Xacro em CI (quando CI for formalizado)
- **Visual:** inspeção manual em RViz2 comparando com a tabela de graus de liberdade (§4)
- **Integração:** carregamento conjunto com `03a` (mundo Gazebo) de ponta a ponta

---

*Com `03a` e `03b` prontos, o Mark I tem toda a base de simulação especificada. Próximo documento sugerido: `04_Locomocao/04a_Cinematica_Inversa.md` — o algoritmo de IK que o nó `leg_kinematics` (já com interface definida em `01b`) precisa implementar.*
