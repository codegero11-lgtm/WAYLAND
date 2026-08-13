# 00 — Visão Geral do Projeto

**Codinome do projeto:** *Aracne* (proposta — substituível)
**Papel deste documento:** ponto de entrada da documentação. Define visão, filosofia, stack tecnológico (com justificativas) e a árvore completa de documentos que serão produzidos nos próximos ciclos.

---

## Índice

1. Objetivo Final (Mark Final)
2. Restrições de Arquitetura (o que não pode ser violado)
3. Filosofia de Engenharia
4. Inventário de Hardware
5. Stack Tecnológico — decisão e justificativa item a item
6. Contrato de Módulo (o "molde" que toda documentação de módulo deve seguir)
7. Árvore Completa da Documentação
8. Fluxo Simulação → Hardware Real
9. Próximos Documentos a Produzir

---

## 1. Objetivo Final (Mark Final)

Plataforma terrestre de **robótica mórfica biomimética**, capaz de alternar entre duas configurações principais:

1. **HEXAPOD STABILITY MODE ("Modo Aranha")**
   - 6 pernas ativas;
   - estabilidade estática extrema e redundância;
   - progressão em terreno severamente irregular / escombros / superfícies instáveis;
   - centro de massa baixo;
   - marcha estática/tripódica;
   - **coluna em estado rígido/travado** (prioridade: estabilidade e robustez).

2. **FELINE DYNAMIC MODE ("Modo Felino")**
   - 4 pernas primárias de locomoção;
   - 2 pernas centrais recolhidas/travadas;
   - alta mobilidade e corrida dinâmica;
   - saltos e pousos sucessivos (absorção de impacto);
   - **coluna em estado dinâmico/complacente**;
   - possibilidade de armazenamento/devolução de energia elástica (trote/galope/salto).

O conjunto de habilidades prevê:
- Navegação autônoma e mapeamento (SLAM)
- Reconhecimento de ambientes, pessoas e objetos (visão computacional)
- Comandos de voz + conversação via LLM local
- Sensoriamento diverso (IMU, LiDAR, câmeras, contato)
- **Transformação de morfologia 6↔4 entre os dois modos (MORPH TRANSITION)**

> **20 km/h** é uma **meta aspiracional de sistema** para o modo dinâmico — **NÃO** é um requisito congelado de atuador. Os requisitos físicos necessários (velocidades, torques, potência, energia) serão **derivados** antes de qualquer decisão de atuação.

> **Não existe mais objetivo de voo / módulo aéreo.** A direção é exclusivamente terrestre. A pasta de documentação `12_Modulo_Aereo_Futuro` permanece como legado **obsoleto** (sem deleção por ora); não deve ser usada como requisito ativo.

## 2. Restrições de Arquitetura (não-negociáveis)

Estas restrições existem para impedir que decisões de curto prazo (Mark I, Mark II) fechem portas para o Mark Final. Todo módulo novo será validado contra esta lista:

- **R1 — Independência funcional por versão:** cada Mark deve ligar, executar e demonstrar valor sozinho, sem depender de peças do Mark seguinte ainda não construídas.
- **R2 — Simulação antes de hardware:** nenhuma funcionalidade nova entra no robô físico sem antes existir e ser validada em Gazebo/RViz2.
- **R3 — Baixo acoplamento entre módulos:** comunicação entre módulos só via interfaces bem definidas (tópicos/serviços/ações ROS2), nunca por acesso direto a estado interno de outro módulo.
- **R4 — Nenhuma dependência proprietária crítica:** qualquer software fechado só pode ser usado se (a) for opcional e (b) existir um caminho open-source equivalente documentado.
- **R5 — Reserva Morfológica e Dinâmica:** nenhuma decisão de chassi, energia, computação ou atuação pode impedir: (a) uma **coluna de rigidez variável** (rígida↔complacente); (b) **compliance passiva ou ativa** em juntas/pernas; (c) **sensoriamento de contato** nas patas; (d) **atuação dinâmica** com reserva de torque/potência/velocidade; (e) a **transformação de morfologia 6↔4**, incluindo **pernas centrais recolhíveis/traváveis**; (f) **margem estrutural para impactos** (saltos/pousos); e (g) **margem energética e instrumentação** para o controle dinâmico (corrida/salto). A arquitetura deve reservar o envelope estrutural, energético e de interface para essas capacidades, **sem fixar mecanismo específico** nesta etapa.
- **R6 — Cada Mark é uma evolução, não um salto:** nenhuma versão pode introduzir mais de ~2 capacidades genuinamente novas por vez (regra prática de "incremento controlável").

## 3. Filosofia de Engenharia

**Priorizar:** modularidade, baixo custo, impressão 3D, open source, reuso de componentes, manutenibilidade, documentação rigorosa, evolução incremental.

**Evitar:** dependências desnecessárias, soluções proprietárias fechadas, código monolítico, acoplamento forte entre módulos.

Isso se traduz em duas regras práticas de arquitetura de software:
- **Boundaries por pacote ROS2**: cada módulo (locomoção, visão, navegação, voz, etc.) vive em seu próprio pacote, com uma interface pública mínima (mensagens/serviços/ações customizados) e tudo mais privado.
- **Configuração > código**: parâmetros de hardware (dimensões de perna, número de pernas, portas seriais) ficam em arquivos YAML versionados, nunca hardcoded — isso é o que permite evoluir a plataforma sem reescrever lógica.

## 3.1. Arquitetura de Controle (direção futura)

A arquitetura de controle é planejada em **três camadas**:

- **Camada 1 — SAFETY / ACTUATION:** ARM/DISARM; E-stop físico futuro; watchdog; limites; proteção de corrente/temperatura; interlocks; health monitoring.
- **Camada 2 — MODEL-BASED CONTROL:** cinemática (IK); dinâmica; state estimation; controle de posição/torque/impedância; contato; estabilidade; controle determinístico.
- **Camada 3 — LEARNED LOCOMOTION:** Reinforcement Learning; sim-to-real; domain randomization.

**Políticas futuras (locomoção):**
- **PI-H — Hexapod Policy:** estabilidade, footholds, terreno irregular, redundância.
- **PI-F — Feline Policy:** trote, galope, corrida, coluna dinâmica, salto, pouso, energia elástica.
- **PI-M — Morph Policy:** transição 6↔4, gestão do centro de massa, recolhimento/liberação das pernas centrais, mudança de rigidez da coluna, estabilidade durante a transformação.

Acima delas, existirá futuramente um **MORPHOLOGY SUPERVISOR**, que decide se uma transição é permitida com base em velocidade, contato, postura, estado da coluna, temperatura, bateria, falhas e estabilidade.

> **Regra:** **RL não controla nem substitui a camada básica de safety/interlocks** (Camada 1 é determinística e soberana).

## 3.2. Simulação (política)

- **Gazebo Harmonic** (via `ros_gz`) permanece o **simulador principal de integração de sistema** ROS2 e validação sistêmica. Nada substitui o Gazebo nesta etapa.
- Futuros **candidatos complementares** (a avaliar, **sem decisão final**): **MuJoCo** (dinâmica rápida, contato, corrida/salto, experimentação) e **Isaac Gym / Isaac Lab** (treinamento RL massivamente paralelo, domain randomization, políticas PI-H/PI-F/PI-M).
- **Não** há adopção final de simulador e **não** se abandona o Gazebo.

## 3.3. Marks (política de evolução)

- **Mark I** = baseline biomecatrônico e bancada de validação de controle (uma perna simulada) — **válido e preservado.**
- **Mark II+** = **arquitetura em estudo**, a ser definida **depois** da derivação dos requisitos mecânicos, energéticos, de atuação e de transformação (morfologia 6↔4, coluna, compliance). **Não há** roadmap Mark II→VIII congelado.



## 4. Inventário de Hardware

**Disponível agora:**
| Recurso | Uso previsto |
|---|---|
| PC com GPU AMD RX 7800 XT | Simulação (Gazebo), treino/inferência leve, LLM local via Ollama |
| Ollama instalado | Módulo de conversação (LLM local) |
| VS Code | IDE principal |
| Unity | Alternativa/complemento de simulação (ver §5) |
| Impressora 3D Elegoo Mars (resina) | Peças estruturais de precisão — atenção: resina é mais frágil e mais lenta que FDM para peças estruturais grandes; considerar FDM complementar para peças de chassi |
| Celular Android antigo | Câmera + microfone + IMU embutido, via app de streaming (ex.: IP Webcam / DroidCam) — atua como "sensor pack" provisório barato no Mark I/II |

**Hardware futuro (por fases, detalhado no roadmap):** ESP32, servos, motores, LiDAR, IMU dedicado, baterias, drivers de motor, encoders.

⚠️ **Ponto de atenção técnico (AMD vs. ecossistema de visão/IA):** boa parte do ecossistema de visão computacional (YOLO, treino de modelos) é otimizado primariamente para CUDA (NVIDIA). Com RX 7800 XT, o caminho é ROCm (suporte Linux, maduro para inferência, mais instável para treino). Isso será formalizado no documento `06_IA` com plano B (inferência via CPU/ONNX ou uso de câmera com pré-processamento em edge) caso ROCm apresente atrito.

## 5. Stack Tecnológico — decisão e justificativa

| Tecnologia | Decisão | Justificativa | Alternativa considerada |
|---|---|---|---|
| **ROS2** (Humble/Jazzy) | Adotar como espinha dorsal | Padrão de fato em robótica modular; dá pub/sub, ações, lifecycle nodes, e comunidade enorme para hexápodes/octápodes | MQTT customizado — descartado: reinventaria ferramentas que ROS2 já resolve (tf2, RViz2, launch, nav2) |
| **Python** | Módulos de alto nível (IA, visão, voz, comportamento) | Prototipagem rápida, ecossistema de ML/CV | — |
| **C++** | Módulos de tempo real/baixo nível (controle de servo, loops de IK) | Latência previsível, necessária para controle de perna em malha fechada | Python puro — descartado para controle de tempo real por latência do GIL |
| **PlatformIO + ESP32** | Firmware dos microcontroladores | PlatformIO padroniza build/debug multi-placa; ESP32 tem Wi-Fi/BLE nativo, custo baixo, dual-core | Arduino IDE puro — descartado, PlatformIO é superior para CI/versionamento |
| **Gazebo** (Harmonic, via ros_gz) | Simulador físico principal | Integração nativa com ROS2, física de contato para pernas, sensores simulados (câmera, LiDAR, IMU) | — |
| **Unity** | Uso **secundário**, não substituto do Gazebo | Útil para visualização rica, digital twin, e testes de UI/teleoperação; **não** deve ser fonte de verdade física porque a integração ROS2↔Unity é mais frágil que ros_gz | Descartar Unity como simulador primário — mantido como ferramenta de apoio (dashboard, gêmeo digital) |
| **RViz2** | Visualização/debug | Padrão ROS2 para tf, nuvens de pontos, mapas | — |
| **OpenCV** | Pré-processamento de imagem | Padrão, leve, roda bem em CPU | — |
| **YOLO** (Ultralytics, versão a definir) | Detecção de objetos/pessoas | Bom trade-off precisão/velocidade, exporta para ONNX (portável para ROCm/CPU) | — |
| **Whisper** | Reconhecimento de voz | Melhor custo/benefício open source para STT em português | Vosk — mais leve, cotado como *fallback* para hardware embarcado fraco |
| **Piper** | Síntese de voz (TTS) | Leve, roda local, boa qualidade em PT-BR | — |
| **Ollama** | LLM local (conversação) | Já instalado, boa integração com modelos abertos, API simples | — |
| **Docker** | Empacotamento de módulos (exceto firmware) | Reprodutibilidade entre PC de desenvolvimento e futura placa companion (ex.: Jetson/mini-PC) | — |
| **Nav2** *(adição sugerida)* | Stack de navegação autônoma sobre ROS2 | Não estava na lista original, mas é o padrão para SLAM + planejamento de trajetória; evita reinventar navegação | A avaliar: aceitar ou justificar alternativa quando chegarmos ao módulo `07_Navegacao` |

## 6. Contrato de Módulo

Todo documento de módulo (pastas `02` em diante) seguirá exatamente esta estrutura, para permitir que o DeepSeek implemente sem ambiguidade:

1. Objetivo
2. Responsabilidades (o que é e o que **não** é responsabilidade deste módulo)
3. Entradas (tópicos/serviços/ações ROS2 consumidos, com tipo de mensagem)
4. Saídas (idem, produzidos)
5. Tecnologias utilizadas
6. Dependências (outros módulos, bibliotecas, hardware)
7. Riscos técnicos e mitigação
8. Critérios de sucesso (testáveis, mensuráveis)
9. Testes necessários (unitário / integração / simulação / hardware)
10. Roadmap interno (o que existe no Mark I, o que entra no Mark II, etc.)

## 7. Árvore Completa da Documentação

```
Projeto_Aracne/
├── 00_Visao_Geral/                 ← este documento
├── 01_Arquitetura/
│   ├── 01a_Arquitetura_de_Software.md
│   ├── 01b_Contratos_de_Interface_ROS2.md
│   └── 01c_Convencoes_de_Nomenclatura.md
├── 02_Hardware/
│   ├── 02a_Chassi_e_Estrutura.md
│   ├── 02b_Atuadores_e_Servos.md
│   ├── 02c_Eletronica_e_Fiacao.md
│   └── 02d_Sensores.md
├── 03_Simulacao/
│   ├── 03a_Ambiente_Gazebo.md
│   ├── 03b_Modelo_URDF_Xacro.md
│   └── 03c_Pipeline_Sim2Real.md
├── 04_Locomocao/
│   ├── 04a_Cinematica_Inversa.md
│   ├── 04b_Geracao_de_Gait.md
n```