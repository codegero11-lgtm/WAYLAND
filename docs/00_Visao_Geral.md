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

Robô octápode (8 pernas, inspiração aracnídea) capaz de:

- Locomoção em terrenos internos e externos
- Navegação autônoma e mapeamento (SLAM)
- Reconhecimento de ambientes, pessoas e objetos (visão computacional)
- Comandos de voz + conversação via LLM local
- Aprendizado incremental de novas tarefas
- Sensoriamento diverso (IMU, LiDAR, câmeras, contato)
- Retorno automático à base de recarga
- Execução de pequenas tarefas domésticas
- Capacidade eventual de pequenos saltos
- **Módulo de voo**: explicitamente fora do escopo inicial, mas a arquitetura precisa deixar um "encaixe" (interface de payload/expansão) para que ele possa ser adicionado anos depois sem reescrever locomoção, navegação, IA ou percepção.

## 2. Restrições de Arquitetura (não-negociáveis)

Estas restrições existem para impedir que decisões de curto prazo (Mark I, Mark II) fechem portas para o Mark Final. Todo módulo novo será validado contra esta lista:

- **R1 — Independência funcional por versão:** cada Mark deve ligar, executar e demonstrar valor sozinho, sem depender de peças do Mark seguinte ainda não construídas.
- **R2 — Simulação antes de hardware:** nenhuma funcionalidade nova entra no robô físico sem antes existir e ser validada em Gazebo/RViz2.
- **R3 — Baixo acoplamento entre módulos:** comunicação entre módulos só via interfaces bem definidas (tópicos/serviços/ações ROS2), nunca por acesso direto a estado interno de outro módulo.
- **R4 — Nenhuma dependência proprietária crítica:** qualquer software fechado só pode ser usado se (a) for opcional e (b) existir um caminho open-source equivalente documentado.
- **R5 — Reserva de payload para o módulo de voo:** desde o Mark que define o chassi definitivo, há um envelope de massa/energia/espaço reservado e não utilizado, para o futuro módulo aéreo.
- **R6 — Cada Mark é uma evolução, não um salto:** nenhuma versão pode introduzir mais de ~2 capacidades genuinamente novas por vez (regra prática de "incremento controlável").

## 3. Filosofia de Engenharia

**Priorizar:** modularidade, baixo custo, impressão 3D, open source, reuso de componentes, manutenibilidade, documentação rigorosa, evolução incremental.

**Evitar:** dependências desnecessárias, soluções proprietárias fechadas, código monolítico, acoplamento forte entre módulos.

Isso se traduz em duas regras práticas de arquitetura de software:
- **Boundaries por pacote ROS2**: cada módulo (locomoção, visão, navegação, voz, etc.) vive em seu próprio pacote, com uma interface pública mínima (mensagens/serviços/ações customizados) e tudo mais privado.
- **Configuração > código**: parâmetros de hardware (dimensões de perna, número de servos, portas seriais) ficam em arquivos YAML versionados, nunca hardcoded — isso é o que permite trocar Mark I por Mark II sem reescrever lógica.

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