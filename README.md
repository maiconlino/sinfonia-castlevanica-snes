# SinfonIA Castlevânica Futurística · SNES

Adaptação nativa do jogo de navegador criado para Maicon Lino. Este projeto produz um cartucho homebrew de Super Nintendo, com programa 65C816, gráficos 4bpp, áudio SPC700/S-DSP e progresso em SRAM. A ROM não precisa de navegador, JavaScript, internet, cadastro ou BIOS externa.

Aurel Vesper entra no Castelo de Véspera, onde o Regente Nulo aprisionou as memórias dos mortos. Entre vitrais, bibliotecas, jardins e máquinas, ele reúne os três selos para devolver às vozes a liberdade e ao castelo o amanhecer.

## Jogar

Abra `build/sinfonia-castlevanica.sfc` em um emulador de SNES. A versão foi executada no Snes9x 1.63, usando seu núcleo libretro. Configure o controle do jogador 1 no emulador.

Na abertura, **Start** inicia uma campanha. **Select** continua o progresso do cartucho quando existe um salvamento válido. Uma nova campanha não apaga imediatamente a SRAM, mas um salvamento posterior substitui a campanha anterior: há um único espaço de gravação.

| Controle SNES | Ação |
|---|---|
| Direcional esquerdo/direito | Mover |
| B | Pular; segundo salto depois de obter Asas da Vigília |
| Y, manter pressionado | Atacar com a espada |
| A | Lançar a magia equipada |
| X | Usar o consumível equipado |
| L | Esquiva rápida |
| R | Trocar rapidamente entre espadas adquiridas |
| Select | Alternar humano, lobo, morcego e névoa já desbloqueados |
| Cima, próximo de uma porta | Entrar; os requisitos e a forma precisam ser atendidos |
| Cima, próximo do altar central | Curar, recuperar magia e gravar o progresso |
| Start | Pausar e abrir o inventário |

Nas formas voadoras, **B ou Cima** sobe; **Baixo** desce. As transformações consomem magia e acabam quando ela se esgota. O lobo corre mais rápido. A névoa evita dano e permite passar pelas grades que exigem sua relíquia.

No inventário, **Cima/Baixo** escolhe um item possuído e **A** equipa. **Select** alterna equipamentos, atlas, loja e ajuda. **B ou Start** retorna ao jogo. Na loja, **A** compra o item selecionado, somente em um santuário. No atlas, **X** viaja para um santuário ativado depois da vitória na Biblioteca, quando o jogador também está em um santuário. **Y** no menu salva e recupera vida e magia quando o local permite.

Portas estão distribuídas na parte inferior das salas; aproxime-se e pressione Cima. Ataque as grades suspeitas para revelar passagens secretas. Use o atlas para conferir as saídas descobertas. A arma suprema exige três fragmentos, a névoa e a vitória no Túmulo do Vento.

## Conteúdo da adaptação

- 8 regiões, 60 salas conectadas e 10 chefes, sendo 2 opcionais.
- 60 tipos de itens: 12 espadas, 8 armaduras, 10 acessórios, 8 relíquias, 6 magias, 6 consumíveis e 10 chaves.
- Sabre comum no início. Crissaegrim como recompensa do chefe secreto final de sua rota.
- Armas com cadência e alcance diferentes, projéteis, interrupção, congelamento, condução elétrica e rajadas espectrais.
- Lobo espectral, morcego e névoa digital; salto duplo, respiração aquática, desaceleração temporal e proteção de aurora como relíquias.
- Experiência, níveis, moeda, equipamentos, poções, loja, mapas, segredos, atalhos e viagem entre santuários.
- Final da campanha e retorno à exploração depois dos créditos.
- 11 arranjos musicais nativos: oito ambientes, chefe, chefe final e vitória, além de seis efeitos sonoros.

Esta é uma **adaptação do conteúdo e da jogabilidade ao SNES**, com motor novo. As salas usam telas de 256 × 224, conectadas por portas; a geometria ampla e os efeitos do navegador foram redesenhados. Arte, animações, timbres, números de combate e parte dos efeitos foram simplificados. O grafo da campanha, os itens e a progressão principal vêm dos dados do projeto web. Não é uma reprodução visual pixel a pixel da versão publicada.

O cadastro, o salvamento em nuvem e o painel administrativo pertencem à versão web. No SNES, o progresso fica no arquivo de SRAM mantido pelo emulador, geralmente `.srm`. Não existem estatísticas online. Salve em um santuário e encerre o emulador normalmente para que ele grave esse arquivo. O emulador pode também oferecer save states, que são um mecanismo separado.

A duração de 4 a 6 horas planejada anteriormente para o jogo de navegador **não foi aferida nem garantida nesta adaptação**. Sessões em hardware físico também não foram executadas.

## Compilar a ROM

Requisitos: Python 3 e `ca65`/`ld65` do cc65 disponíveis no PATH. Os binários dos gráficos, da música e dos dados já acompanham o projeto, portanto Pillow não é necessário para a compilação normal.

```sh
python3 tools/build.py
```

Ou:

```sh
make
```

O resultado é `build/sinfonia-castlevanica.sfc`. O script interrompe a compilação em caso de erro, gera mapa e símbolos, verifica o tamanho da ROM e recalcula checksum e complemento. É possível definir `CA65` e `LD65` com caminhos explícitos para as ferramentas.

A compilação de referência usou cc65, tag V2.19, commit `555282497c3ecf8b313d87d5973093af19c35bd5`. O programa interno dessa tag identifica-se como V2.18. Código do compilador: https://github.com/cc65/cc65

## Regenerar todos os assets

O desenho dos pixels é produzido por Python e Pillow; o código de áudio e de campanha usa apenas a biblioteca padrão do Python. As composições de origem estão em `tools/original_scores.json`.

```sh
python3 -m pip install -r requirements-assets.txt
python3 tools/build_content.py
python3 tools/generate_graphics.py
python3 tools/build_audio.py
python3 tests/validate_graphics.py
python3 tools/build.py
```

A reconstrução completa dos gráficos, da campanha, do áudio e da ROM foi conferida por SHA-256, com resultado idêntico ao build sem regeneração.

## Estrutura

| Caminho | Responsabilidade |
|---|---|
| `src/main.s` | Inicialização, PPU, DMA, controle, movimento, salas e personagem |
| `src/combat.s` | Combate, inimigos, chefes, magia, itens e portas |
| `src/render.s` | Sprites, HUD, abertura, final e envio de comandos sonoros |
| `src/menu_save.s` | Inventário, mapa, loja, viagem e validação de SRAM |
| `src/audio.s` | Upload e comunicação CPU/SPC700 |
| `src/rom_data.s` | Organização dos assets e cabeçalho do cartucho |
| `tools/build_audio.py` | Driver SPC700 autoral, assembler pequeno, BRR e sequências |
| `tools/generate_graphics.py` | Pixel art autoral e conversão para tiles/paletas SNES |
| `tools/build_content.py` | Compilação e validação das tabelas da campanha |
| `assets/data.json` | Fonte integral dos dados da campanha original |
| `lorom.cfg` | Mapa de memória e bancos da ROM |
| `docs/` | Relatórios e documentação da adaptação |

## Cartucho

- ROM LoROM de 1 MiB, sem cabeçalho extra de copiador.
- Região NTSC, funcionamento nominal de aproximadamente 60 Hz.
- SRAM de 8 KiB com assinatura, versão, tamanho, checksum e complemento.
- Gráficos em Mode 1, BG1 4bpp, sprites de 16/32 pixels.
- Áudio nativo, quatro vozes musicais e uma voz de efeitos, oito timbres BRR autorais.
- Nenhum chip de expansão, download, servidor ou jogo comercial é necessário.

## Créditos e origem

Projeto e direção: Maicon Lino. Adaptação, programação, composição e pixel art: trabalho desenvolvido com Astra. Os arquivos criativos e o motor deste cartucho são originais deste projeto. Não incluem ROM, sprites, amostras, música ou código de Castlevania ou de outro jogo comercial. O código do emulador e do compilador não está incorporado à ROM.

Veja `docs/VALIDATION.md` para distinguir testes de execução, cenários instrumentados e limites de compatibilidade.
