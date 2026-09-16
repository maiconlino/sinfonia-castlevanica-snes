# SinfonIA Castlevânica Futurística, SNES 1.1

Jogo homebrew nativo para Super Nintendo, desenvolvido para Maicon Lino. Código 65C816, gráficos 4bpp, áudio SPC700, cartucho LoROM de 1 MiB e SRAM de 8 KiB. Não é uma página web encapsulada e não inclui ROM comercial.

## Jogar

Abra `dist/sinfonia-castlevanica-snes-v1.1.smc` no emulador. **Start** inicia; **Select** na abertura carrega o salvamento do cartucho. A extensão `.smc` contém os mesmos bytes nativos do `.sfc`, sem cabeçalho de copiador.

Use uma inicialização nova da ROM ao trocar de versão. Não restaure um save state da versão anterior, pois ele contém código e memória antigos. O progresso normal do cartucho usa o arquivo `.srm`, cujo nome base deve acompanhar o nome da ROM.

| Botão | Ação |
|---|---|
| Direcional | Andar; Cima interage com porta ou altar |
| B | Pular; manter pressionado aumenta a altura |
| Y | Atacar |
| A | Magia |
| X | Consumível selecionado |
| L | Esquiva |
| R | Próxima espada disponível |
| Select | Transformação desbloqueada |
| Start | Inventário e pausa |

A campanha mantém 60 salas em 8 regiões, 10 chefes, 60 tipos de itens, lobo, morcego e névoa. A Crissaegrim continua sendo uma recompensa avançada, não a arma inicial. Santuários, viagem, mapa, loja, segredos e encerramento permanecem implementados. Não há login ou administração na ROM.

## Revisão visual e de movimento

- Portas compostas corretamente: uma imagem de 32 × 48 pixels formada por 24 partes distintas, com versões aberta, fechada e secreta revelada.
- Personagem redesenhado em canvas de 32 × 48, com 16 poses, incluindo oito de corrida, salto, queda, pouso e ataque.
- Chefes redesenhados em canvas de 64 × 64, usando quatro sprites nativos de 32 × 32.
- Oito cenários retrabalhados, com mais nuances, relevos na pedra, madeira, metal, iluminação e paletas por bloco.
- Movimento com velocidades fracionárias 8.8, aceleração, desaceleração, gravidade gradual, salto variável e tolerância curta na borda da plataforma.
- Espera de confirmação do áudio reduzida para não prender a atualização normal do jogo.

As telas continuam tendo 256 × 224 pixels. Esta revisão não transforma o jogo em uma produção comercial nem acrescenta rolagem extensa às salas existentes. O acabamento e o balanceamento ainda podem evoluir.

## Compilar

Com Python 3, ca65 e ld65 no PATH:

```sh
python3 tools/build.py
```

Os assets já estão incluídos. Para regenerar tudo, use Python 3.11 ou superior:

```sh
python3 -m pip install -r requirements-assets.txt
make assets
make
make check
```

A ferramenta de referência é cc65 V2.19, commit `555282497c3ecf8b313d87d5973093af19c35bd5`. É possível definir `CA65` e `LD65` com os caminhos dos executáveis. `tools/build.py` gera `build/sinfonia-castlevanica.sfc` e recalcula checksum e complemento.

## Testes

Com um núcleo libretro Snes9x 1.63 compilado:

```sh
SNES_CORE=/caminho/snes9x_libretro.so python3 tests/revision_motion.py
SNES_CORE=/caminho/snes9x_libretro.so python3 tests/play_revision.py
```

Os resultados atuais estão em `tests/results-v1.1/`. O teste de campanha aplica somente botões do controle, lê a RAM para navegação e asserções e não escreve nela. Visitou as 60 salas, derrotou os 10 chefes, obteve os 60 tipos de itens e chegou ao final. O roteiro conhece o mapa e não mede a duração de uma primeira partida humana.

A duração de 4 a 6 horas não foi demonstrada. Não houve teste em um Super Nintendo físico. O teste automático não substitui avaliação humana de fluidez, dificuldade ou qualidade artística.

## Código e organização

`src/` contém o jogo nativo; `tools/` contém os geradores autorais; `assets/` contém dados, gráficos, paletas e música; `tests/` contém a instrumentação e os testes; `docs/REVISION_1.1.md` registra as alterações e limitações. Os documentos antigos em `docs/` são preservados como histórico da primeira versão.

A versão para navegador fica em um repositório separado: https://github.com/maiconlino/sinfonia-castlevanica-futuristica

Projeto independente, sem afiliação com Nintendo ou Konami. Nomes e referências de terceiros continuam pertencendo a seus titulares. As ferramentas externas cc65 e Snes9x possuem licenças próprias e não são incorporadas à ROM.
