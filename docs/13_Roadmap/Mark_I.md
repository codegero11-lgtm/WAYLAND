# 13_Roadmap — Mark I

## Índice
1. Objetivo do Mark I
2. Por que começar aqui (justificativa do escopo)
3. Limitações explícitas
4. Hardware necessário
5. Software necessário
6. Estrutura de pacotes ROS2
7. Critérios de sucesso
8. Testes necessários
9. O que fica para o Mark II

---

## 1. Objetivo do Mark I

Construir e validar, **inteiramente em simulação**, uma **única perna** do robô octápode, com cinemática inversa funcional e controle de posição, mais o esqueleto de projeto (repositório, pacotes ROS2, pipeline de simulação) que todos os Marks seguintes vão reaproveitar.

Não é sobre o robô andar. É sobre provar a fundação: URDF parametrizável, IK correta, e o fluxo simulação→controle funcionando de ponta a ponta para 1 perna — porque se isso não funcionar para 1, não vai funcionar para 8.

## 2. Por que começar aqui (justificativa do escopo)

Aplicando a restrição R6 (evolução controlável): o Mark I introduz exatamente 2 capacidades novas:
- Modelagem/simulação de um membro articulado
- Cinemática inversa básica (posicionar a "pata" em um ponto XYZ alvo)

Não introduz: múltiplas pernas, gait, hardware real, visão, IA, voz, navegação. Cada uma dessas entra em um Mark posterior, isoladamente.

## 3. Limitações explícitas do Mark I

- Não existe robô físico — tudo roda em Gazebo
- Apenas 1 perna (3 graus de liberdade: coxa/fêmur/tíbia, configuração a definir em `02b`)
- Sem gait, sem locomoção, sem equilíbrio
- Sem visão, sem voz, sem IA, sem navegação
- Controle via teclado/GUI simples (teleoperação de teste), não autônomo

## 4. Hardware necessário

Nenhum hardware físico é necessário para o Mark I. Tudo roda no PC (RX 7800 XT) via Gazebo. O único "hardware" usado é o computador de desenvolvimento já disponível.

## 5. Software necessário

- Ubuntu (nativo ou WSL2 — a decidir e documentar em `01a`, pois WSL2 tem limitações conhecidas de GPU passthrough para Gazebo)
- ROS2 (Humble ou Jazzy — decisão em `01a`)
- Gazebo (via `ros_gz`)
- Pacote `xacro` para modelagem parametrizada
- `ros2_control` + um controller de posição (`joint_trajectory_controller`) para os 3 "servos simulados" da perna

## 6. Estrutura de pacotes ROS2 (proposta inicial)

```
aracne_ws/
└── src/
    ├── aracne_description/     # URDF/Xacro da perna, meshes
    ├── aracne_bringup/         # launch files, configs YAML
    ├── aracne_leg_kinematics/  # nó de IK (C++ ou Python, a decidir em 04a)
    └── aracne_teleop/          # controle manual de teste
```

Essa estrutura de pacotes é definitiva — Mark II apenas adiciona pacotes (`aracne_gait`, etc.), nunca reestrutura os existentes (consistente com R3).

## 7. Critérios de sucesso (mensuráveis)

- [ ] Perna carrega em Gazebo sem erros de URDF/física
- [ ] Nó de IK recebe um ponto alvo (x, y, z) via tópico/serviço e calcula os 3 ângulos de junta corretamente (erro < 2mm na simulação, validado por comparação com cálculo analítico)
- [ ] `joint_trajectory_controller` move a perna suavemente até o alvo, sem oscilação
- [ ] Todo o pipeline sobe com um único comando `ros2 launch`
- [ ] Parâmetros de dimensão da perna (comprimento de cada segmento) estão em YAML, não hardcoded

## 8. Testes necessários

- **Unitário:** função de IK testada contra casos conhecidos (posições alcançáveis e inalcançáveis)
- **Simulação:** sequência de 10 pontos-alvo distintos, validar que a perna alcança cada um dentro da tolerância
- **Integração:** subir o `bringup` completo do zero e confirmar que todos os nós ficam ativos (`ros2 node list`, `ros2 topic list`)

## 9. O que fica para o Mark II (não implementar agora)

- Réplica das 8 pernas no mesmo chassi
- Geração de gait (padrão de caminhada tripé, por exemplo)
- Primeiro esboço do chassi físico (mas ainda só em simulação)

---

*Próximo documento sugerido: `01_Arquitetura/01a_Arquitetura_de_Software.md`, detalhando a decisão Ubuntu nativo vs WSL2, versão do ROS2, e os contratos de mensagem entre os pacotes acima.*