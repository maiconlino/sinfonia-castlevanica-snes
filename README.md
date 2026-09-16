# SinfonIA Castlevânica Futurística · SNES

Homebrew independente de ação e exploração para Super Nintendo. Projeto de Maicon Lino.

## Revisão 1.1

Esta revisão corrige a montagem das portas e altera a movimentação e a arte da adaptação. Não é apenas um arquivo .sfc renomeado: há mudanças no código 65C816 e nos recursos gráficos nativos.

- Portais de 32 × 40 pixels compostos por 20 partes de uma única imagem, sem repetir a porta inteira em cada tile.
- Protagonista redesenhado em uma tela de sprite de 32 × 48 pixels, com 16 quadros disponíveis: repouso, oito poses de corrida, salto e ataques. Quinze quadros são usados pela máquina de animação atual; o décimo sexto é reservado.
- Velocidade em ponto fixo 8.8, aceleração, frenagem e saltos de altura variável. Janela de tolerância de seis quadros para o salto e buffer de entrada de seis quadros.
- Camada BG2 com o ambiente atrás das partes transparentes dos portais em BG1, paletas adicionais e vitrais laterais.
- Guardas, sentinelas e arqueiros redesenhados com duas poses; morcegos e chefes preservam os desenhos anteriores.
- O personagem não desaparece intermitentemente durante a invulnerabilidade. Um brilho sinaliza o período final, sem interromper sua animação.
- Memória salva mantida com o mesmo leiaute de 658 bytes, em SRAM de 8 KiB.

A campanha e o áudio da versão anterior foram mantidos. As 60 salas, os 10 chefes e as tabelas de itens não foram substituídos por uma demo nova. A duração de 4 a 6 horas continua sem validação com jogadores.

## Jogar

Abra `release/sinfonia-castlevanica-snes-v1.1.smc` em um emulador de SNES. O mesmo conteúdo também é distribuído em `.sfc`. A ROM não utiliza cabeçalho de copiador.

| Botão | Ação |
|---|---|
| Direcional | Mover |
| B | Pular; segurar aumenta a altura; segundo salto após obter a relíquia |
| Y | Espada |
| A | Magia |
| X | Consumível |
| L | Esquiva |
| R | Trocar espada |
| Select | Transformação; continuar na tela de abertura |
| Cima | Porta ou altar |
| Start | Iniciar ou abrir o menu |

Nos altares, o jogo cura e grava o progresso no arquivo SRAM mantido pelo emulador. Faça cópia do `.srm` antes de trocar versões. Save states do emulador não são equivalentes a esse salvamento e não devem ser carregados entre ROMs diferentes.

## Compilar

Python 3 e `ca65`/`ld65` do cc65 são necessários. Os recursos binários estão incluídos no repositório após a importação/compilação automática.

```sh
python3 tools/build.py
```

Para reconstruir todos os recursos:

```sh
python3 -m pip install -r requirements-assets.txt
python3 tools/build_content.py
python3 tools/refine_graphics.py
python3 tools/build_audio.py
python3 tools/build.py
python3 tests/validate_graphics_v11.py
python3 tests/validate_rom.py
```

`tools/generate_graphics.py` preserva o gerador original, usado por `refine_graphics.py` como base. Executá-lo sozinho produz os gráficos antigos e não é o comando correto para reconstruir esta revisão.

## Testes realizados nesta revisão

Os resultados estão em `docs/revision-1.1/results.json`. Foram verificados boot, oito poses de corrida, atualização lógica por quadro de vídeo, aceleração fracionária, parada, salto curto/longo, tolerância, buffer, salto duplo, entrada por porta, áudio, gravação em altar e continuação após reset. Os testes unitários de física preparam cenários escrevendo RAM explicitamente; os testes de porta e altar utilizam comandos do controle.

O core utilizado foi Snes9x 1.63. Foram medidos saltos de 20 pixels (toque curto) e 54 pixels (botão mantido). Não se afirma uma nova conclusão integral da campanha 1.1 nem teste em console físico. O replay completo antigo pertence exclusivamente à ROM 1.0 e está no histórico/arquivo legado.

## Conteúdo e histórico

`legacy/v1.0` preserva as fontes originais e seus testes. O processo de importação recompila essa versão e verifica a ROM pelo SHA-256 de referência antes de construir a revisão atual. Não confunda os relatórios antigos com os desta revisão.

A versão de navegador é separada deste repositório. Não há cadastro, contas online nem painel administrativo dentro de um cartucho SNES.

Projeto sem afiliação com Nintendo ou Konami. Não inclui ROMs comerciais, músicas extraídas de jogos comerciais ou ferramentas proprietárias de desenvolvimento. Consulte o manual original em `docs/MANUAL-v1.0.md` para a descrição da campanha e do áudio.
