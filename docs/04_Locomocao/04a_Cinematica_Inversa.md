# 04a — Cinemática Inversa (IK)

## Índice
1. Objetivo
2. Escolha de abordagem: analítica vs. numérica
3. Modelo geométrico da perna (recap de `03b`)
4. Derivação do IK analítico (3 GDL)
5. Tratamento de pontos inalcançáveis
6. Implementação — linguagem e estrutura do nó
7. Integração com a interface já definida (`01b`)
8. Validação numérica
9. Riscos e mitigação
10. Critérios de sucesso
11. Testes necessários
12. O que fica para depois (gait, múltiplas pernas)

---

## 1. Objetivo

Especificar o algoritmo que o nó `leg_kinematics` (pacote `aracne_leg_kinematics`, interface já definida em `01b_Contratos_de_Interface_ROS2.md`) deve implementar: dado um ponto alvo (x, y, z) para a pata, calcular os 3 ângulos de junta (coxa, fêmur, tíbia).

## 2. Escolha de Abordagem: Analítica vs. Numérica

**Decisão: solução analítica (closed-form), não numérica (ex.: Jacobiano iterativo / CCD).**

**Justificativa:** com apenas 3 GDL em cadeia serial planar-ish (configuração perna de aranha/hexápode clássica: coxa gira no plano horizontal, fêmur+tíbia formam um braço 2-link no plano vertical), existe solução geométrica fechada — mais rápida, determinística, sem risco de não-convergência ou mínimos locais, e mais fácil de validar unitariamente (comparar contra fórmula, não contra tolerância de convergência).

Solução numérica fica reservada como alternativa **apenas se** o Mark futuro introduzir uma perna com geometria não-planar ou mais GDL que quebre a decomposição abaixo — decisão a revisitar explicitamente nesse momento, não antes.

## 3. Modelo Geométrico da Perna (recap de `03b`)

- `coxa_length` (L1): gira em torno do eixo Z (planta baixa)
- `femur_length` (L2) e `tibia_length` (L3): formam um manipulador 2-link no plano vertical, após a rotação da coxa

Esta decomposição em "1 GDL horizontal + 2 GDL verticais" é exatamente o que torna a solução analítica simples: resolve-se a coxa separadamente, depois um problema clássico de "2-link planar IK" para fêmur/tíbia.

## 4. Derivação do IK Analítico

Dado o alvo (x, y, z) relativo a `leg1_base_link`:

**Passo 1 — ângulo da coxa (θ1):**
```
θ1 = atan2(y, x)
```

**Passo 2 — reduzir ao plano vertical:**
```
r = sqrt(x² + y²) - L1        # distância horizontal restante, após a coxa
 d = sqrt(r² + z²)             # distância direta até o alvo, no plano do fêmur/tíbia
```

**Passo 3 — verificar alcançabilidade (antes de prosseguir):**
```
se d > (L2 + L3) OU d < |L2 - L3|:
    retornar success=false, error="ponto fora do alcance"
```

**Passo 4 — ângulo da tíbia (θ3), via lei dos cossenos:**
```
cos(θ3) = (d² - L2² - L3²) / (2 * L2 * L3)
θ3 = -acos(cos(θ3))          # sinal negativo: convenção "joelho para trás", conforme 03b
```

**Passo 5 — ângulo do fêmur (θ2):**
```
α = atan2(z, r)
β = acos((L2² + d² - L3²) / (2 * L2 * d))
θ2 = α + β
```

Esta é a forma clássica de IK 2-link, aplicada após a decomposição do Passo 1-2. A convenção de sinal exata (joelho para frente vs. para trás) deve bater com a definição de eixos e limites de junta já fixada em `03b` — validado no Passo de testes (§10).

## 5. Tratamento de Pontos Inalcançáveis

Consistente com o contrato `ComputeIK.srv` definido em `01b`: quando o ponto está fora do alcance (Passo 3), o serviço retorna `success=false` com `error_message` descritivo — **nunca** retorna um ângulo calculado com `NaN` ou clampado silenciosamente. Decisão de projeto: falhar de forma explícita é sempre preferível a mover a perna para uma posição não solicitada.

## 6. Implementação — Linguagem e Estrutura do Nó

**Decisão: C++**, não Python, para este nó — apesar de a Visão Geral reservar Python para "módulos de alto nível". Justificativa específica: `leg_kinematics` fica no caminho direto de controle de junta (roda a cada ciclo de controle, potencialmente >100Hz quando o Mark II tiver gait), então se qualifica como "módulo de baixo nível/tempo real" conforme já definido em `00_Visao_Geral §5`. Também elimina retrabalho: já nasce na linguagem que vai ser usada quando este nó precisar rodar embarcado.

Estrutura do pacote:
```
aracne_leg_kinematics/
├── include/aracne_leg_kinematics/
│   └── ik_solver.hpp        # função pura, sem dependência de ROS2 (testável isoladamente)
├── src/
│   ├── ik_solver.cpp        # implementação da matemática do §4
│   └── leg_kinematics_node.cpp   # wrapper ROS2: assina/publica tópicos, expõe serviço
└── test/
    └── test_ik_solver.cpp   # testes unitários (gtest)
```

Separação deliberada: `ik_solver` é uma função matemática pura (entrada: x,y,z,L1,L2,L3 → saída: ângulos ou erro), sem nenhuma dependência de ROS2. Isso permite testar a matemática isoladamente, sem precisar subir um nó/simulação — acelera drasticamente o ciclo de teste.

## 7. Integração com a Interface Já Definida (`01b`)

- `leg_kinematics_node` assina `/aracne/leg/target_pose` (`aracne_msgs/LegTarget`) → chama `ik_solver` → publica `/aracne/leg/joint_angles` (`sensor_msgs/JointState`).
- Expõe também `/aracne/leg/compute_ik` (`aracne_msgs/ComputeIK`) como forma síncrona, chamando a mesma função `ik_solver` internamente — **nenhuma duplicação de lógica** entre o caminho de tópico e o de serviço.

## 8. Validação Numérica

Antes de aceitar a implementação, validar contra casos conhecidos calculados manualmente (ou via script Python de referência, usado só para gerar os casos de teste, nunca em produção):
- Ponto na posição de repouso (perna esticada para baixo)
- Ponto no limite exato do alcance máximo (d = L2 + L3)
- Ponto inalcançável (d > L2 + L3) — deve retornar falha, não um número
- Ponto simétrico (θ1 negativo) — valida o `atan2` do Passo 1

## 9. Riscos e Mitigação

| Risco | Mitigação |
|---|---|
| Ambiguidade "joelho para frente/trás" gerar movimento contra-intuitivo ou colisão com o próprio corpo | Convenção de sinal fixada no Passo 4 e validada visualmente em Gazebo/RViz2 antes de aceitar o módulo como concluído |
| Erro de ponto flutuante perto dos limites de alcance (`acos` de valor ligeiramente >1 ou <-1) | Clamp defensivo do argumento de `acos`/`cos` ao intervalo [-1, 1] antes da chamada, com log de aviso se a correção for maior que uma tolerância pequena (ex.: 1e-6) |

## 10. Critérios de Sucesso

- [ ] `ik_solver` calcula corretamente os 5 casos de validação do §8 (erro < 1e-6 rad contra valor de referência)
- [ ] Serviço `/aracne/leg/compute_ik` retorna `success=false` com mensagem clara para pontos fora do alcance
- [ ] Perna em Gazebo se move suavemente até o ponto alvo publicado em `/aracne/leg/target_pose`, sem overshoot visível
- [ ] Nenhuma duplicação de código matemático entre o caminho de tópico e o de serviço

## 11. Testes Necessários

- **Unitário (gtest):** os 5 casos do §8, rodando sem ROS2/sem simulação
- **Integração:** publicar em `/aracne/teleop/cmd` com Gazebo rodando, confirmar movimento correto ponta-a-ponta
- **Regressão:** qualquer mudança futura em `03b` (novos comprimentos de segmento) deve rodar de novo os testes unitários com os novos `L1/L2/L3`

## 12. O Que Fica Para Depois

- Geração de trajetória contínua (interpolação entre pontos) — hoje o serviço só calcula IK de um ponto instantâneo; trajetórias suaves entram com o `joint_trajectory_controller` (já configurado em `03a`/`03b`), não neste nó.
- IK simultâneo para 8 pernas coordenadas — Mark II, reaproveitando esta mesma função `ik_solver` (parâmetros L1/L2/L3 já vêm do YAML por perna).
- Restrições de colisão perna-corpo — só relevante quando o chassi físico completo existir.

---

*Com `04a` pronto, o Mark I está com todos os módulos necessários documentados: arquitetura, contratos, simulação (mundo + URDF) e o algoritmo de IK. O que falta é o documento operacional de bringup/testes que amarra tudo (`aracne_bringup`), ou já podemos considerar a documentação do Mark I "pronta para implementação" pelo DeepSeek. Como quer seguir: (1) documento de bringup/testes de integração, ou (2) já avançar para `04b_Geracao_de_Gait.md` (Mark II)?*
