# Revisão R3, circulação pelas bordas e combate

Data: 16/09/2026. Base: R2 verificada, SHA-256 `57d02a02c1346b2380707635c6c88be04cd50c781d34259d9f39e6c8be11d38f`.
ROM R3: `f2ed7037fb8773cafcad4ddfb42b8c8ef4389302d4e88aaf786a7cf42020a4ec`.

## Correções principais

Leitura serial mantida de todos os botões a cada quadro, sem depender da repetição de teclas ou da janela de início da leitura automática. Fila de áudio não bloqueante, com prioridade para mudanças de música. Remoção do desaparecimento integral do protagonista durante invulnerabilidade. Transferência parcial de 512 bytes do mapa em quadros comuns. Movimento e animação sincronizados com deslocamento, inclusive durante golpes em movimento. Todos os quatro arquétipos de inimigo se deslocam; os três terrestres agora têm comportamento de aproximação ou recuo e preparação de golpes.

## Navegação

As conexões já existentes foram reposicionadas para esquerda ou direita, no chão ou em plataformas elevadas. Caminhar até a borda atravessa a passagem quando seus requisitos estão atendidos. Cima serve somente ao altar. O trajeto principal fica no chão. Os segredos ainda exigem descoberta; as relíquias e chaves continuam bloqueando o acesso prematuro. Chefes fecham as saídas até a vitória. A R3 não implementa rolagem contínua de câmera entre salas.

## Chefes diferentes

| Chefe | Identidade visual | Padrão implementado |
|---|---|---|
| Sacristão de Bronze | Guardião pesado, armadura e martelo bronzeados | Três ondas baixas de impacto e avanço na segunda fase |
| Abadessa dos Índices | Véu, coroa e páginas flutuantes | Flutuação e leque de páginas com velocidades verticais diferentes |
| Jardineiro de Vidro | Árvore cristalina com núcleo brilhante | Raízes com indicação prévia no chão e raiz adicional na segunda fase |
| Leviatã do Reservatório | Serpente articulada, barbatanas e mandíbula | Investida horizontal seguida de projéteis aquáticos |
| Fundidor de Ecos | Fornalha, chaminés e grelhas incandescentes | Bombas em arco sujeitas à gravidade |
| Relojoeiro Cego | Relógio com dentes, ponteiros e pêndulo | Engrenagens que revertem a direção durante a trajetória |
| Astrônoma Vazia | Astrolábio e manto estrelado | Marcações seguidas de estrelas cadentes, com ataque adicional na segunda fase |
| Regente Nulo | Núcleo mecânico, trono e circuitos | Alterna padrões anteriores e acrescenta investida na segunda fase |
| Cavaleiro da Última Brasa | Duelista, capa de brasa e espada longa | Salto durante a investida e ataque de lâmina |
| A Espada sem Dono | Espada central flutuante e ecos laterais | Investida aérea e lâminas espectrais descendentes |

Os desenhos são 64 × 64, com paletas próprias. Cada chefe dispõe de quatro posições de animação; algumas posições reutilizam uma pose, conforme registrado no teste gráfico. Não são apenas variações de cor do mesmo desenho.

## Verificação da compilação final

Emulador executado: Snes9x 1.63, núcleo `921f9f7`, Linux x86-64. LoROM NTSC de 1 MiB, vídeo 256 × 224, SRAM de 8 KiB. Não foi testado no SUPER ZSNES nem em console físico.

* Hardware e dados: cabeçalho, checksum, bancos gráficos, áudio, 60 salas, 140 conexões, 60 tipos de itens e 10 conjuntos diferentes de gráficos de chefes.
* Direcional mantido: esquerda e direita sem passos de zero pixel depois da aceleração; oito poses de caminhada observadas.
* Passagem automática: esquerda, direita e continuidade do botão mantido depois da chegada.
* Temporização: 6.000 quadros ativos, 6.000 atualizações de lógica, nenhum desaparecimento integral do protagonista nesse trecho. Esse teste não inclui o custo de carregamento entre regiões.
* Áudio adversarial: 600 quadros com confirmação atrasada simulada, sem bloqueio da lógica.
* Inimigos: deslocamento verificado para os quatro arquétipos.
* Salvamento: altar, reinicialização do emulador e continuação da SRAM.
* Campanha: percurso completo por comandos do controle, 60 salas, 10 chefes, 60 tipos de itens, final exibido e nenhuma morte no percurso otimizado.
* Replay: repetição independente da gravação de botões, sem leitura de memória para decidir ações, com o mesmo final.

A campanha automatizada percorreu 30.389 quadros, aproximadamente 8 minutos e 26 segundos de tempo emulado, com conhecimento prévio do mapa. Isso verifica que a campanha pode ser concluída, não comprova duração humana de 4 a 6 horas nem equilíbrio final de dificuldade.

O teste de regressão prepara cenários por escrita de WRAM, explicitamente identificada em `regression.json`. O percurso completo não modifica a WRAM. O replay não usa realimentação da memória durante a partida. Relatórios e gravação de botões estão em `build/qa-r3/`.

## Proximidade com a web

Foram preservados a história, os dados de salas, armas, magias, recompensas e composições de origem. Os timbres, a geometria compacta das salas e os recursos gráficos são nativos do SNES. Esta revisão não é apresentada como reprodução idêntica da web ou de Castlevania: Symphony of the Night.
