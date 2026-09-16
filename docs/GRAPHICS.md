# SinfonIA, arte nativa de Super Nintendo

Assets originais desenhados por código Python para o porte SNES. Não contêm sprites, cenários nem dados extraídos de Castlevania ou de ROMs comerciais.

## Reprodução

Requer Python 3 e Pillow:

```sh
python generate_graphics.py
python validate_graphics.py
```

Os arquivos em `assets/` já estão gerados. A ROM só depende dos binários `.chr`, `.map`, `.pal` e dos números de tiles, não precisa de Python ou Pillow em execução.

## VRAM sugerida

| Conteúdo | Endereço em bytes | Endereço em palavras | Tamanho |
|---|---:|---:|---:|
| BG1 CHR da região | 0x0000 | 0x0000 | 32768 |
| OBJ CHR compartilhado | 0x8000 | 0x4000 | 16384 |
| BG1 tilemap | 0xC000 | 0x6000 | 2048 |

`bg_region0.chr` até `bg_region7.chr` contêm tiles nativos 4bpp de 8x8. Cada byte de mapa representa metade de uma palavra little endian: bits0..9 são o tile; o mapa fornecido usa banco de paleta0, sem flips nem prioridade. São32x32 entradas, das quais28linhas visíveis em256x224.

Cada região tem paleta16cores BGR555,32bytes. O banco0 de CGRAM recebe `bg_regionN.pal`. A cor0 é o fundo global, a15 é o marfim claro da fonte. `bg_palettes.pal` concatena as oito paletas opcionais.

## Tiles do cenário

Tiles0..95 representam ASCII32..127, portanto o tile de uma letra é seu códigoASCII menos32. A fonte5x7 usa célula8x8 e a cor15. Letras minúsculas têm o mesmo desenho das maiúsculas. Espaço é transparente.

Tiles96..127 são os blocos de jogo. Os nomes exatos estão em `assets/graphics.inc` e `assets/graphics-layout.json`. Destaques:97plataforma superior,98preenchimento,105grade,106espinho,107porta fechada,108porta aberta,110santuário,112baú,113espada,114coração,116chave,118barra cheia,119barra vazia.

Tiles128..1023 são reservados para os cenários da região. O mapa deve servir de base e os objetos/jogo devem ser sobrepostos a ele. Carregar outra região muda os desenhos128+ e a paleta, preservando os números dos tiles compartilhados.

Os oito ambientes: castelo medieval, biblioteca, jardim lunar, reservatório subterrâneo, forja, torre de relógios, observatório e coração da máquina. Há signos visuais próprios, além da mudança de cores.

## OBJ

`sprites.chr` contém512tiles4bpp,16KB. A folha corresponde a128x256pixels. **O stride das linhas de tiles é sempre16**. Use tamanho OBJ pequeno16x16 e grande32x32.

- Aurel:8frames16x32. Base do tile0,2,4,6,8,10,12,14. Cada frame usa duas peças16x16, a inferior com tile+32.
- Lobo:64/68; morcego72/76. Desenhos32x16, parte inferior transparente. Podem usar uma peça32x32 ou duas16x16lado a lado.
- Névoa:128/132,32x32.
- Guarda192, arqueiro194, sentinela196, besta198, chama200. São16x32, portanto duas peças16x16 com tile+32.
- Chefes:256,260,264,268,320,324,328,332,384,388. Cada um é32x32.
- Cortes448/452, projétil456, impacto460.32x16 com parte inferior transparente.

**Tiles256..511 exigem o bit0 do byte de atributo OBJ**, além do índice baixo de8bits. Não perca esse bit ao combinar paleta, prioridade e flip.

`sprites.pal` é a paleta principal16cores para CGRAM128..143. `sprite_palettes.pal` concatena oito bancos de16cores,256bytes, para CGRAM128..255. O banco0 mantém as cores do protagonista; os demais variam os acentos de inimigos/chefes por região. Índice0 sempre transparente em OBJ.

## Verificação realizada

`validate_graphics.py` decodifica os binários nativos4bpp e reconstitui os oito cenários a partir dos tilemaps, comparando os pixels com as fontes. Também valida os128tiles comuns, todos os frames do protagonista, todos os dez chefes e os limites das paletas BGR555. Essa verificação passou.

Os PNGs são previews para desenvolvimento e não entram na ROM. O gerador é completamente determinístico.
