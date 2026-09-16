# SinfonIA Castlevânica Futurística, SNES

Revisão visual e de movimento **2.0** da adaptação nativa de Maicon Lino. Programa 65C816, vídeo Mode 1 / 4bpp e áudio SPC700. Não usa navegador nem uma ROM comercial como base.

## Jogar

Abra **`roms/sinfonia-castlevanica-v2.smc`** em seu emulador de Super Nintendo. A distribuição também inclui `.sfc`, com os mesmos bytes, sem cabeçalho de copiador. Testes desta revisão: Snes9x 1.63, núcleo libretro, 256 × 224, NTSC. Não foi testada em console físico.

**Start** começa; **Select** na abertura continua um salvamento válido. Salve no altar de um santuário com **Cima**. Existe um slot de SRAM. Faça uma cópia do `.srm` antigo antes de trocar a ROM. Save states do emulador não são intercambiáveis entre versões do programa. O layout de SRAM da campanha foi mantido.

| Controle | Ação |
|---|---|
| Direcional | Mover |
| B | Pular; manter pressionado permite salto mais alto |
| Y, segurar | Atacar |
| A | Magia equipada |
| X | Consumível equipado |
| L | Esquiva |
| R | Alternar espadas adquiridas |
| Select | Alternar formas desbloqueadas |
| Cima | Entrar na porta ou usar o altar próximo |
| Start | Inventário, mapa, loja e pausa |

No menu, Cima/Baixo seleciona, A equipa, Select alterna páginas e B/Start retorna. Nas formas voadoras, B/Cima sobe e Baixo desce. Algumas portas exigem a forma correspondente, além da relíquia adquirida.

## O que mudou nesta revisão

* Protagonista com **32 × 48 pixels e 16 poses distintas**, incluindo oito poses de corrida, ataque, salto, queda, esquiva e repouso. O desenho não é a ampliação do sprite anterior.
* Movimento em ponto fixo 8.8, aceleração e frenagem curtas, salto de altura variável, buffer de salto e tolerância de seis quadros após deixar uma plataforma.
* Cada porta agora é **um arco de 24 × 40 pixels**, composto por 15 partes 8 × 8. Não é mais a repetição de uma porta inteira dentro de cada quadrado. Há estados aberto, fechado e parede secreta.
* Cenários reconstruídos em duas camadas nativas, com céu distante, parallax, quatro paletas por região, arquitetura própria e plataformas com extremidades diferentes.
* Personagem composto corretamente, sem sobreposição dos blocos de VRAM das transformações. O indicador de dano muda a paleta em vez de ocultar o herói por longos intervalos.
* HUD mais compacto, com barras de vida e magia.

Esta revisão não afirma equivalência artística com um jogo comercial como Super Mario World. Os inimigos e chefes ainda têm animação mais simples que a do protagonista. As salas continuam sendo telas conectadas, não um mapa contínuo com câmera lateral. A evolução visual não muda essas limitações estruturais.

## Campanha e validação

A campanha mantém 8 regiões, 60 salas, 10 chefes, 60 tipos de itens, 12 espadas, três transformações, loja, segredos, santuários e final. A espada suprema é uma recompensa avançada; não vem equipada no começo. Há 11 arranjos musicais e seis efeitos nativos.

A execução automatizada desta revisão visitou **60 salas**, derrotou **10 chefes**, terminou com **60 tipos de itens** e **zero mortes**, somente com comandos do controle. O teste lê o estado para navegar e fazer asserções, mas não escreve a memória do jogo. A rota usa conhecimento do mapa e não mede duração humana. A meta anterior de 4 a 6 horas não foi comprovada para esta adaptação compacta.

`tests/test_revision.py` também verifica inicialização, oito poses de corrida, reversão de direção, altura variável do salto, pausa e recuperação de SRAM em uma nova sessão do emulador. O teste de caminhada observou uma atualização de lógica em cada um de 48 quadros consecutivos; isso não é uma garantia de desempenho para todo emulador ou aparelho.

Os relatórios específicos desta revisão ficam em `build/*v2.json` e `docs/validation-v2/`. A versão original é preservada em `legacy/v1.0/`, recompilada com o mesmo SHA-256. Os documentos e sequências de comandos antigos descrevem a física anterior e não substituem os testes novos.

## Compilar

Instale Python 3 e as ferramentas `ca65` e `ld65` do cc65. Os arquivos binários de arte, áudio e campanha já acompanham o repositório.

```sh
python3 tools/build.py
```

O resultado é `build/sinfonia-castlevanica.sfc`. Para regenerar os recursos antes de compilar:

```sh
python3 -m pip install -r requirements-assets.txt
make assets
make
make check
```

Para testar com um núcleo libretro Snes9x compilado localmente:

```sh
export SNES_CORE=/caminho/snes9x_libretro.so
python3 tests/validate_graphics.py
python3 tests/test_revision.py
python3 tests/playthrough_v2.py
python3 tests/replay_revision.py
```

`CA65` e `LD65` podem apontar para executáveis fora do PATH. `tools/graphics_v2.py` gera a arte atual; `tools/generate_graphics.py` preserva os desenhos e utilitários originais, utilizados na reconstrução da versão anterior. `src/polish.s` contém movimento fracionário, composição do personagem e envio dos quadros de animação para VRAM.

## Separação da versão web

A versão para computador e celular está em outro repositório: **maiconlino/sinfonia-castlevanica-futuristica**. Contas, estatísticas e salvamento online não fazem parte de um cartucho SNES. Aqui o progresso é local, na SRAM administrada pelo emulador.

Projeto independente, sem afiliação com Nintendo ou Konami. Os desenhos e arranjos deste projeto não foram extraídos de jogos comerciais. Nenhuma senha, chave de API ou base de jogadores é necessária para compilar a ROM.
