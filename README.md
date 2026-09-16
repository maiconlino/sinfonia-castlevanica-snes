# SinfonIA Castlevânica Futurística, SNES R3

Homebrew de Maicon Lino. Revisão jogável com transição automática pelas bordas, movimento mais responsivo, inimigos móveis e dez chefes redesenhados com comportamentos próprios.

Abra `dist/sinfonia-castlevanica-snes-r3.smc` no emulador. Start inicia a campanha. A identificação R3 aparece na abertura. As versões anteriores permanecem em seus próprios arquivos e branches.

[Notas, controles e limites dos testes](docs/REVISAO-R3.md)

## Compilar

Python 3 e ca65/ld65 do cc65. As ferramentas de referência foram cc65 V2.19 e Pillow 12.3.0. Com os recursos binários incluídos, basta:

```sh
python3 tools/build.py
```

Para reconstruir também os gráficos e os dados, respeite esta ordem:

```sh
python3 -m pip install Pillow==12.3.0 numpy
python3 tools/build_content.py
python3 tools/generate_graphics.py
python3 tools/build_r3_assets.py
python3 tools/build_audio.py
python3 tools/build.py
```

`generate_graphics.py` sozinho gera a base R2. O passo `build_r3_assets.py` aplica a arte e as saídas R3. Os desenhos dos chefes estão em `assets/source/bosses-r3-source.png`. O mapeamento físico das ligações está em `assets/source/room-ports-r3.json`.

## Testes de R3

Configure `SNES_CORE` com o caminho de um núcleo libretro Snes9x 1.63.

```sh
python3 tests/validate_r3.py
python3 tests/first_route_r3.py
python3 tests/upper_exit_r3.py
```

Os relatórios da revisão são gravados em `docs/r3/`. Relatórios e scripts de outras revisões não comprovam o funcionamento desta ROM. Ainda não há validação da campanha R3 inteira, do SUPER ZSNES ou de console físico. Não há garantia de que a duração da campanha corresponda à meta de 4 a 6 horas.

## Conteúdo preservado

O grafo de 60 salas, 60 tipos de itens, 12 espadas, seis magias, três transformações, dez chefes e os temas musicais são derivados da campanha web. A jogabilidade foi adaptada ao SNES, não reproduzida pixel a pixel. Contas online e ADM não fazem parte da ROM. O progresso é gravado em SRAM.

Projeto independente, sem afiliação com Nintendo ou Konami. Não inclui ROM comercial, dados pessoais de jogadores ou credenciais.
