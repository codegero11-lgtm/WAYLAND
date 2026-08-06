# Lote B — URDF, Xacro e ros2_control

## Objetivo

Produzir uma descrição válida e coerente da perna do Mark I.

## Escopo obrigatório

### 1. Estrutura de Xacro

- manter macro reutilizável da perna em `leg.xacro`;
- manter o nível de robô completo em `aracne.xacro`;
- mover `<ros2_control>` para o nível do robô completo;
- não duplicar o controller manager.

### 2. Juntas

Declarar três juntas controladas:

- coxa;
- fêmur;
- tíbia.

Para cada junta:

- `command_interface`: `position`;
- `state_interface`: `position`;
- `state_interface`: `velocity`;
- limites consistentes com o URDF.

### 3. Geometria

- corrigir rotação `rpy` dos cilindros;
- manter visual e collision coerentes;
- revisar origins;
- não alterar dimensões documentadas sem registrar.

### 4. Launch

- remover somente o `ros2_control_node` duplicado, se confirmado;
- não implementar ainda spawn, broadcasters ou controllers.

## Fora do escopo

- spawn no Gazebo;
- bridge;
- controller spawner;
- pipeline de comandos;
- teleop;
- JointTrajectory;
- testes de integração.

## Validação

```bash
xacro src/aracne_description/urdf/aracne.xacro > /tmp/wayland_mark1.urdf
check_urdf /tmp/wayland_mark1.urdf

colcon build --symlink-install \
  --packages-select aracne_description aracne_bringup
```

## Critérios de aceite

- Xacro processa;
- URDF é válido;
- três juntas existem;
- interfaces de controle existem;
- controller manager não está duplicado;
- geometria está orientada corretamente.

## Atualização obrigatória de rastreamento

Antes de declarar este lote concluído, atualize:

1. `CURRENT_STATUS.md`
   - lote concluído;
   - marco atingido;
   - evidências;
   - bloqueadores;
   - próximo objetivo.

2. `TRACEABILITY.md`
   - alterar os requisitos do lote para `VALIDADO`, `BLOQUEADO` ou `DÍVIDA TÉCNICA`;
   - preencher evidência real;
   - não marcar como concluído sem teste.

3. `CHANGELOG.md`
   - registrar mudanças relevantes.

4. `TECH_DEBT.md`
   - adicionar qualquer compromisso temporário;
   - fechar dívidas resolvidas.

## Entrega obrigatória

Ao final, fornecer:

- arquivos modificados;
- arquivos criados;
- diff resumido;
- comandos executados;
- resultado do build;
- resultado dos testes;
- evidências;
- pendências;
- hash do commit;
- confirmação de que os arquivos de rastreamento foram atualizados.

Parar ao concluir. Não iniciar o lote seguinte.
