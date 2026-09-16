# Revisão 1.1, 16/09/2026

## Problemas encontrados

A composição da porta usava o mesmo tile para células diferentes, repetindo uma miniporta. O movimento horizontal era inteiro e a velocidade vertical mudava em degraus grandes. A resposta de áudio também podia manter a CPU em espera por tempo excessivo.

## Alterações

A porta passou a usar 24 tiles distintos em uma imagem de 32 × 48. As três variantes usam paleta própria e não revelam uma passagem secreta antes da descoberta. A interação passou a usar o mesmo centro da imagem. Uma sala com quatro conexões ainda mostra quatro portas, mas cada porta é agora uma imagem íntegra, não quatro miniportas repetidas.

A física usa velocidade e fração em ponto fixo 8.8, aceleração e atrito separados, gravidade de 0,25 pixel por atualização e salto de altura variável. O buffer de salto e a tolerância ao sair de bordas são de seis atualizações. O ponto inicial continua sendo `px=80, py=152`; o formato do salvamento persistente foi mantido.

O herói tem 16 poses em canvas 32 × 48. Cada pose é composta por seis objetos 16 × 16. Os chefes usam quatro objetos 32 × 32 por pose, formando 64 × 64. As trocas de pose enviam apenas os dados necessários à VRAM. Os cenários continuam sendo 4bpp nativos, agora com seleção de paleta por tile e relevo/nuances adicionais. A fonte foi afastada da borda superior em um pixel.

A confirmação do SPC deixou de bloquear por um laço de 0x4000 tentativas, usando uma consulta curta. Solicitações de música podem ser retomadas na próxima atualização. O teste não demonstrou perda de atualização durante os trechos normais medidos.

## Verificação desta revisão

- Checksum e complemento da ROM, mapeamento e limites dos bancos: aprovados.
- Oito mapas/paletas regenerados e comparação binária com os assets: aprovados.
- Reconstrução dos tiles de todas as portas, 16 poses humanas e 20 poses de chefes: aprovada.
- 600 atualizações em 600 frames em um trecho normal.
- 300 atualizações em 300 frames na amostra com chefe ativo.
- A amostra estendida de 600 frames, incluindo a derrota do chefe e o salvamento automático, teve 599 atualizações. Isso não foi mascarado como estabilidade perfeita em todas as transições.
- Salto curto e mantido produzem alturas diferentes; todas as oito poses de corrida foram atingidas; soltar o controle interrompe o movimento sem tecla presa.
- O SRAM salvo foi carregado em uma nova instância do emulador.
- Campanha completa por controle: 60 salas, 10 chefes, 60 tipos de itens, final, zero mortes na rota automática, sem escrita na RAM do jogo.

O teste de campanha levou 40536 frames emulados, aproximadamente 674,49 segundos. O controlador conhece antecipadamente o mapa e a progressão; esse número não é uma previsão de duração para jogadores. A antiga meta de 4 a 6 horas continua não demonstrada.

Ambiente: Snes9x 1.63 libretro, commit iniciado por `921f9f7`, com ca65/ld65 da tag V2.19. Não houve teste em console físico. Capturas em `tests/results-v1.1/` são da ROM em execução, não mockups.

## Escopo

Esta é uma revisão significativa de arte, composição e movimento, não uma recriação com o mesmo orçamento de arte e engenharia de um título comercial. As salas continuam compactas e sem rolagem contínua de um castelo gigante. Os testes automáticos comprovam estados e percursos, não avaliam diversão nem prometem ausência total de defeitos.
