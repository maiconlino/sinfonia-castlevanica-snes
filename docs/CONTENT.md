> Documento histórico da versão 1.0. Para a revisão atual, consulte REVISION_1.1.md.

# Dados da campanha para SNES

`data.json` é uma serialização integral do `DATA` exportado pelo jogo web, sem alterar IDs, nomes, itens, grafo de salas ou requisitos. `tools/build_content.py` converte essa fonte para `data.inc` (ca65), `tables.json` (arrays idênticos para testes) e `validation.json`.

```sh
python3 tools/build_content.py
```

O gerador usa apenas a biblioteca padrão do Python. Aceita `--input`, `--output`, `--tables` e `--report`. Inclua `data.inc` no segmento `DATA`, banco 1. O engine pode acessar arrays com endereçamento longo (`f:room_region,x`) e X de 16 bits. O arquivo é determinístico; o relatório inclui hashes SHA-256 da fonte e do assembler.

## Contrato das tabelas

- IDs de sala 0 a 59, seguindo a ordem original. `ROOM_C01 = 0`, `ROOM_H07 = 59`.
- IDs de região 0 a 7, chefes 0 a 9, itens 0 a 59. Ausência = 255. Constantes `ROOM_*`, `REGION_*`, `BOSS_*`, `ITEM_*`, `EFFECT_*` são geradas.
- `room_region`, `room_type`, `room_boss`, `room_exit_count`: 60 bytes cada.
- Bits de `room_type`: 1 santuário/checkpoint, 2 chefe, 4 secreta, 8 opcional, 16 checkpoint na entrada do chefe.
- `room_exit_to`, `room_exit_secret`, `room_exit_flags` e `room_exit_req0` a `room_exit_req3`: 240 bytes cada. Índice = sala * 4 + slot. Slots sem porta têm destino 255. Requisitos ausentes = 255; todos os requisitos diferentes de 255 precisam estar no inventário.
- Bits de `room_exit_flags`: 1 secreta, 2 atalho, 4 mão única. O grafo original atual tem no máximo 4 portas por sala. A passagem O03/O04 possui 4 requisitos: três fragmentos e névoa digital.
- `room_item_count`: 60 bytes. `room_items`: 180 bytes, índice = sala * 3 + slot. Preenchimento = 255. **Itens em salas de chefe não devem ser coletados antes da vitória.**
- `boss_rewards`: 30 bytes, índice = chefe * 3 + slot. Recompensas repetem as que estão em `room_items` nas salas de chefe. O engine deve entregar apenas uma vez.
- `boss_hp`: 10 palavras de 16 bits. Demais tabelas de chefe, `boss_room`, `boss_region`, `boss_optional`, `boss_damage`, `boss_pattern`, usam bytes.
- `item_kind`, `item_power`, `item_effect`, `item_room`, `item_flags`, `item_mana_cost`, `item_max_stack`: 60 bytes cada. Categorias 0 espada, 1 armadura, 2 acessório, 3 relíquia, 4 magia, 5 consumível, 6 chave.
- Bits `item_flags`: 1 permanente, 2 arma suprema, 4 recompensa de chefe, 8 acumulável.
- `sword_power`, `sword_attack_frames`, `sword_reach`, `sword_effect`: 12 bytes cada. Os 12 primeiros IDs de itens são as espadas. `sword_speed_q8` usa 12 palavras Q8.8, preservando inclusive velocidade 2,8 da arma suprema.
- `room_name`, `region_name`, `item_name`, `boss_name`: strings ASCII em maiúsculas, até 28 caracteres, preenchidas com zero até **32 bytes**. O índice é ID * 32. Existem ainda tabelas `*_name_ptr` de ponteiros de 16 bits no mesmo banco, opcionais.
- `starting_items`: IDs 0, 12, 30, 38, 44, terminados em 255. `starting_owned` e `starting_counts`: 60 bytes. O jogador começa com sabre comum, casaco, esquiva, magia lunar e 3 poções. A arma suprema é o item 11, recompensa exclusiva do chefe secreto 9.

## Adaptação espacial proposta

O SNES usa salas de uma tela de 256 x 224 pixels. A geometria web não é preservada; o grafo e os bloqueios de progressão são. `door_x` contém 24, 88, 152, 216. Chão em Y=184, ponto inicial em X=112/Y=168 para um personagem de 16 pixels. `pickup_x` contém 64, 128, 192.

`room_platform_count`: 60 bytes. `room_platform_x/y/w`: 180 bytes, índice sala * 3 + plataforma. Y é a superfície superior de colisão. Plataformas de combate não bloqueiam acesso às portas pelo chão. Salas normais têm duas ou três plataformas, chefes duas, santuários nenhuma. Portas secretas podem ser reveladas por um golpe próximo, preservando os requisitos da passagem depois da descoberta.

`room_enemy_count`: 0 para santuários/chefes, 2 ou 3 nas demais. `room_enemy_kind`: variantes 0 a 3, sugeridas como sentinela, morcego, máquina e feiticeiro. `region_enemy_hp/damage`: 8 bytes cada. Vida/dano, plataformas e cadência de ataque são valores de adaptação, sujeitos ao teste de combate, não atributos transplantados do engine JavaScript.

## Validação executada

O grafo alcança 60 salas, permite obter os 60 itens e enfrentar os 10 chefes. O final é acessível sem qualquer sala secreta ou opcional, por um conjunto de 48 salas. Nenhum dos sete chefes de progressão pode ser ignorado para alcançar o Regente Nulo. A arma suprema exige conteúdo secreto e não faz parte do equipamento inicial.

A validação diferencia entrar em uma sala de chefe, derrotá-lo e receber a recompensa. Ela pressupõe que os combates encontrados podem ser vencidos. Não verifica equilíbrio, funcionamento em emulador, colisões de uma implementação futura nem duração da campanha. Consulte `validation.json` para as ondas de progressão e os limites do teste.
