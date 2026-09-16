# SinfonIA Castlevânica Futurística, SNES

Jogo homebrew de ação e exploração de Maicon Lino. Esta é a revisão de movimento, personagem e portas de 16/09/2026.

## Jogar

Abra `dist/sinfonia-castlevanica-snes-r2.smc` em um emulador de Super Nintendo. A ROM `.sfc` contém os mesmos bytes. Start começa uma campanha e Select, na abertura, continua um salvamento. A versão de navegador fica em um [repositório separado](https://github.com/maiconlino/sinfonia-castlevanica-futuristica).

Direcional move; B pula; Y ataca; A usa magia; X usa o consumível selecionado; L esquiva; R troca a espada; Select alterna as formas conquistadas; Cima interage com porta e altar; Start abre o inventário. Soltar B cedo faz um salto curto. O salto duplo depende de conquistar a relíquia correspondente.

## O que foi corrigido

Personagem humano de 32 × 48 pixels com dezesseis poses, física subpixel com aceleração e frenagem, salto variável, portas e altar desenhados como objetos únicos. A arte do primeiro ambiente foi refinada. As transformações e a campanha original foram preservadas.

Há oito regiões, sessenta salas, dez chefes, sessenta tipos de itens, doze espadas e três transformações. A Crissaegrim não está equipada no início. O salvamento usa a bateria SRAM emulada, normalmente um arquivo `.srm`. Não há cadastro ou acesso à internet dentro da ROM.

## Compilar

Requisitos: Python 3, ca65 e ld65 do cc65. Os assets prontos permitem compilar sem instalar Pillow.

```sh
python3 tools/build.py
```

Para regenerar a arte, instale `requirements-assets.txt` e execute `tools/generate_graphics.py`. Os scripts `tools/build_content.py` e `tools/build_audio.py` regeneram a campanha e o áudio. `src/` contém o código nativo 65C816 e `tools/` inclui a geração do driver SPC700 e dos recursos gráficos.

## Testes e limites

A ROM foi executada no Snes9x 1.63. Um percurso automatizado por comandos do controle chegou ao final, visitou as sessenta salas, adquiriu os sessenta tipos de itens e venceu os dez chefes. A gravação foi repetida sem leitura de estado durante a partida e chegou ao mesmo final. Movimento, animação, checksum e persistência SRAM também foram testados.

[Detalhes, hashes e limites da revisão](docs/REVISAO-2.md). O teste não foi realizado em console físico. A duração humana de 4 a 6 horas não foi demonstrada; o percurso automatizado e otimizado levou aproximadamente 5 minutos e 29 segundos de tempo emulado. Trata-se de uma adaptação compacta.

Os documentos antigos preservam evidências da primeira ROM e identificam o hash correspondente. Eles não substituem os relatórios desta revisão.

Projeto independente, sem afiliação com Nintendo ou Konami. Não inclui ROMs comerciais, samples extraídos de jogos comerciais, credenciais ou dados de jogadores.
