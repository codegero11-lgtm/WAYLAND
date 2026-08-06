# WAYLAND — Current Status

> Este arquivo representa o estado validado do Mark I após a conclusão do Lote A.

## Identificação

- Projeto: WAYLAND
- Mark atual: Mark I
- Lote atual: Lote A
- Último lote concluído: Lote A
- Marco atual: M1 — Build e testes unitários estáveis
- Última atualização: 2026-08-06

## Ambiente

| Item | Status | Evidência |
|---|---|---|
| WSL2 | OK | `wsl.exe` disponível e ambiente acessível |
| ROS2 Jazzy | OK | Build/test usando `/opt/ros/jazzy/setup.bash` |
| colcon | OK | `colcon build --symlink-install` |
| Gazebo | Não validado | Fora do escopo do Lote A |
| ros2_control | Não validado | Fora do escopo do Lote A |

## Estado do software

| Área | Status | Observação |
|---|---|---|
| Build de pacotes básicos | OK | `aracne_msgs`, `aracne_leg_kinematics`, `aracne_teleop` compilam |
| Testes unitários | OK | `aracne_leg_kinematics`, `aracne_teleop` passam |
| `aracne_teleop` | OK | utiliza `ament_cmake` e `install(PROGRAMS ...)` |
| `ik_solver` | OK | biblioteca estática ligada ao nó e testes |
| `IkResult` | OK | inicialização segura e fluxo de erro tratado |

## Bloqueadores atuais

- Validação dos lotes seguintes (B, C, D, E) ainda não realizada.
- O repositório contém modificações pré-existentes fora do escopo do Lote A e não foram alteradas.

## Próximo objetivo

- Iniciar a análise do Lote B somente após aprovação explícita.
