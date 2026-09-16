> Documento histórico da versão 1.0. Para a revisão atual, consulte REVISION_1.1.md.

# Validação da versão SNES

ROM: `sinfonia-castlevanica.sfc`, 1.048.576 bytes.

SHA-256: `cc4aed7fbadcf86426d81bafc3bb8dc9a67199bf2badad0f6e65a8b60be6b5a4`.

## Campanha completa, executada

A ROM foi executada no Snes9x 1.63, núcleo libretro, commit `890b5d445538fe790aa3add3d5702c80f551e0ae`. Primeiro um jogador automatizado leu o estado para escolher ações, sem escrever memória. Depois, um segundo teste repetiu somente a sequência registrada de botões, sem consultar o estado durante o jogo. Os dois chegaram ao mesmo quadro final.

Ambos os testes visitaram 60 salas, adquiriram os 60 tipos de itens e derrotaram os 10 chefes. Usaram as portas, transformações, ataques, magia, poções, altares, passagens secretas e o menu de equipamento reais. Nenhum cheat, edição de SRAM, alteração da WRAM ou save state foi usado para atravessar a campanha. O final foi exibido, com `finished=1` e `mode=3`.

A execução levou 43.400 frames, aproximadamente 12 minutos e 2 segundos de tempo simulado. O roteiro conhece o mapa e equipa automaticamente os itens mais fortes. Este número é uma evidência de que o jogo pode ser concluído, não uma estimativa de duração de uma primeira partida humana. A meta anterior de 4 a 6 horas não está comprovada para esta versão de salas compactas.

A sequência está em `tests/campaign-inputs.json`. Para reproduzir, instale/compile um núcleo Snes9x libretro e indique seu caminho:

```sh
SNES_CORE=/caminho/snes9x_libretro.so python3 tests/replay_campaign.py
```

O frontend original para os testes está em `tests/headless.py`. Ele usa ctypes; imagens opcionais usam Pillow e NumPy. Fontes do emulador, com sua licença própria: https://github.com/snes9xgit/snes9x

## Salvamento e menus

Testes específicos executaram o assembler de salvamento e verificaram assinatura, versão, tamanho, checksum, corrupção e limites de inventário. O teste integrado abriu a ROM, iniciou a campanha, salvou pelo menu no santuário, reiniciou o emulador com a SRAM salva e continuou pelo Select da tela de título.

Cenários controlados de teste também modificaram o estado para chegar rapidamente à loja, a várias magias e à viagem entre santuários. Esses cenários complementam o teste normal, não são apresentados como parte da campanha percorrida sem alterações. Os relatórios discriminam os casos.

## Áudio e gráficos

Os 11 temas e seis efeitos foram executados no processador SPC700 emulado. Os testes de áudio atravessaram os reinícios das faixas. A integração CPU/SPC executou o upload do driver, mudanças de ambiente, temas de chefes e efeitos durante combate. Houve áudio PCM real.

Os tiles 4bpp, mapas e paletas foram decodificados novamente e comparados com os pixels de origem. Os oito cenários, protagonista, fonte e dez chefes passaram. Capturas da ROM em execução foram inspecionadas.

## Integridade e reprodução

O cabeçalho tem exatamente 64 bytes. A ROM é LoROM NTSC de 1 MiB e declara 8 KiB de SRAM. Checksum/complemento, vetor de reset e posição dos bancos gráficos e de áudio passaram na validação.

A reconstrução de todos os assets e do programa gerou o mesmo SHA-256 da ROM distribuída. `python3 tests/validate_rom.py` verifica os principais invariantes do cartucho.

## Limites

Os testes não foram realizados em um Super Nintendo físico ou em flashcart. A compatibilidade efetivamente verificada é Snes9x 1.63/libretro. Outros emuladores compatíveis com LoROM podem funcionar, mas não foram testados neste trabalho. O teste automatizado não substitui uma avaliação humana de dificuldade, variedade ou duração.

A versão nativa redesenha salas, gráficos e efeitos, e usa SRAM local. Login, nuvem e estatísticas administrativas continuam pertencendo ao jogo de navegador.
