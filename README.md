# SinfonIA Castlevânica Futurística, SNES R3

Homebrew de ação e exploração de Maicon Lino. Esta revisão parte da R2 verificada e mantém o conteúdo da campanha web, mas troca a navegação por passagens nas bordas, corrige interrupções de movimento e diferencia os dez chefes.

## Jogar

Abra `dist/sinfonia-castlevanica-snes-r3.smc` em um emulador de Super Nintendo. A cópia `.sfc` contém os mesmos bytes. Start inicia uma partida; Select na abertura continua a SRAM gravada.

**Caminhe até a extremidade esquerda ou direita para atravessar a passagem. Não pressione Cima para mudar de sala.** O trajeto principal usa as passagens no nível do chão. Ramificações, atalhos e segredos podem ficar nas plataformas laterais elevadas. Requisitos de relíquias e chaves continuam valendo; passagens bloqueadas não são saídas livres. As arenas permanecem fechadas até derrotar o chefe.

| Botão do controle SNES | Ação |
|---|---|
| Esquerda / direita, segurar | Caminhar continuamente e atravessar passagens laterais |
| B | Pular; segurar para salto maior; segundo salto após obter a relíquia |
| Y | Espada; pode manter pressionado para repetir golpes |
| A | Magia equipada, Estilhaço Lunar disponível desde o início |
| X | Consumível equipado |
| L | Esquivar |
| R | Alternar entre espadas adquiridas |
| Select | Alternar formas desbloqueadas |
| Cima, perto do altar | Curar, recuperar magia e salvar |
| Start | Abrir o inventário e pausar |

No inventário: Cima/Baixo seleciona item; A equipa; Select alterna equipamentos, atlas, loja e ajuda; B ou Start retorna. As teclas A/D do computador são configurações do emulador, não nomes de botões lidos pela ROM. Configure-as como esquerda/direita do jogador 1, sem turbo.

## Primeiros passos, chefes e evolução

Para encontrar o primeiro chefe, siga as passagens direitas no chão: Portões da Névoa, Escadaria das Gárgulas, Galeria dos Retratos, Capela do Primeiro Eco, Ponte do Juramento, Tribunal de Bronze. O Sacristão de Bronze guarda essa arena. Descansar na Capela restaura os recursos.

Cada inimigo comum derrotado concede 15 de experiência. Ao juntar 90, o nível sobe automaticamente, consumindo esses 90 pontos. O teto dessa rotina é 35; chefes também concedem um nível. Vida máxima base: 140 no nível 1, mais 12 por nível. Magia máxima base: 100, mais 3 por nível. O acessório de reserva mágica acrescenta 20, sem reduzir a reserva adquirida por níveis.

Há 12 espadas, 6 magias e 60 tipos de itens no total. O jogo começa com o Sabre do Crepúsculo e o Estilhaço Lunar. A Rapieira Lunar está no Arsenal dos Exilados, uma ramificação da Capela. Equipe pelo inventário ou alterne armas já adquiridas com R. A Crissaegrim permanece uma recompensa secreta avançada. Lobo, morcego, névoa e salto duplo são conquistas da exploração e dos chefes, não estão todos liberados no início.

## O que a R3 muda

A entrada do controle agora é lida diretamente pelo registro serial do SNES, uma vez por quadro, com estado mantido. A rotina anterior podia consultar o resultado automático antes de a leitura ter começado. O envio de comandos ao SPC700 agora usa uma fila sem espera bloqueante: uma confirmação atrasada do áudio não segura o loop do jogo. O personagem deixou de desaparecer durante os quadros de invulnerabilidade.

O deslocamento usa ponto fixo 8.8, velocidade normal de 2,5 pixels por quadro, aceleração e frenagem de 0,75 pixel por quadro, oito poses de caminhada ligadas à distância percorrida e salto variável. A correção também evita que uma coordenada negativa perto da esquerda seja interpretada como saída pela direita. A transferência usual do mapa para a VRAM foi reduzida de 2.048 para 512 bytes por quadro, mantendo transferências completas quando a tela muda.

Guardas, arqueiros e sentinelas agora andam e reagem ao jogador. Arqueiros ajustam a distância antes de disparar. Ataques terrestres têm preparação própria. Morcegos mantêm voo, com desenho completo de suas asas.

As 60 salas mantêm as 140 conexões direcionadas da campanha. O percurso principal tem 48 salas e usa as bordas inferiores; as conexões restantes ocupam bordas em plataformas elevadas. A posição de chegada é calculada antes de reapresentar a tela, com uma pequena proteção contra voltar imediatamente à sala anterior.

Dez chefes receberam silhuetas e paletas próprias, desenhos nativos de 64 × 64 pixels e quatro posições de animação por chefe. Os padrões incluem ondas de martelo, páginas em leque, raízes sinalizadas no chão, investida aquática, bombas de fornalha, engrenagens que retornam, estrelas cadentes, combinações do Regente, duelo com salto e lâminas espectrais. Detalhes em `docs/REVISAO-R3.md`.

## Música e proximidade com a versão web

Foram preservadas as composições autorais de origem e os onze arranjos nativos, com trocas por região, chefes e vitória. O áudio é executado pelo SPC700/S-DSP; não depende de MIDI externo, navegador ou internet. Os timbres e a quantidade de vozes são da adaptação para SNES.

Esta versão não é visualmente idêntica à web nem ao jogo comercial de PS1. Mantém os dados da campanha, temas musicais, equipamentos e ações principais, mas as salas são telas compactas de 256 × 224. A troca por borda é automática, não uma câmera contínua percorrendo cenários extensos. Não existe garantia de 4 a 6 horas de duração.

## Compilar e verificar

Requer Python 3, ca65 e ld65 no PATH. O build de referência utiliza cc65 V2.19, commit `555282497c3ecf8b313d87d5973093af19c35bd5`. Os recursos binários estão incluídos. Para recompilar:

```sh
python3 tools/build.py
```

Para regenerar tudo a partir dos geradores e dados:

```sh
python3 -m pip install -r requirements-assets.txt numpy
make assets all
```

O gerador `tools/build_r3_art.py` deve ser executado depois de `tools/generate_graphics.py`. O segundo sozinho reconstrói a base gráfica anterior. `make assets` já aplica a sequência correta.

Para os testes, defina `SNES_CORE` com o caminho do núcleo libretro Snes9x 1.63, commit `921f9f7b83660eb44ad263022a57a4a029057c37`:

```sh
export SNES_CORE=/caminho/snes9x_libretro.so
make check
```

`tests/regression_r3.py` prepara cenários escrevendo WRAM explicitamente. Em contraste, `tests/adaptive_r3.py` percorre a campanha apenas com botões, lendo a memória para decidir o caminho sem alterá-la; `tests/replay_r3.py` repete os botões sem consultar a memória durante a partida. `tests/capture_r3.py` produz imagens e vídeo da ROM em execução, exigindo FFmpeg. Relatórios R3 ficam em `build/qa-r3/`. Testes e relatórios de revisões anteriores não constituem prova de validação da R3.

## Salvamento e compatibilidade

A SRAM continua com 8 KiB e o estado salvo mantém a disposição de 658 bytes. Os testes verificaram salvar em altar e continuar depois de reiniciar o emulador. Faça cópia do seu `.srm` antes de trocar de versão. Não carregue save states de outra ROM na R3. Para avaliar as mudanças, inicie uma partida nova.

A R3 foi testada no Snes9x 1.63, não foi executada no SUPER ZSNES nem em console físico. A experiência nessas plataformas ainda depende de validação. Este projeto não contém contas, cadastro ou ADM, que pertencem exclusivamente à versão web.

Projeto independente, sem afiliação com Nintendo ou Konami. Não inclui ROMs comerciais, imagens ou músicas extraídas de jogos comerciais, nem dados privados de jogadores.
