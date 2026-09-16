> Documento histórico da versão 1.0. Para a revisão atual, consulte REVISION_1.1.md.

# SinfonIA, áudio nativo de Super Nintendo

Este diretório contém um driver SPC700 original e os arranjos da trilha autoral do jogo de navegador. O driver e os instrumentos são novos. Não há música, samples, BIOS ou driver extraídos de jogos comerciais.

## Compilar

```sh
python3 build_audio.py
```

A compilação utiliza somente a biblioteca padrão do Python 3. O resultado `build/audio-driver.bin` tem 25.132 bytes. Inclua todos os bytes em uma única bancada LoROM, transfira o bloco para `$0200` da RAM do SPC700 pelo protocolo IPL e execute em `$0200`. O driver inicia a música do castelo e informa `$53` na porta CPU `$2143` quando pronto. `audio_cpu_ca65.s` fornece o uploader e o envio de comandos para integração. O driver não depende de processamento musical da CPU principal e funciona com temporização de áudio independente de PAL/NTSC.

## Comandos

Escreva o comando em `$2140`, o argumento em `$2141` e, por último, um contador de sequência incrementado em `$2142`. Antes do próximo envio, confira se a leitura de `$2142` corresponde à sequência anterior. O contador começa em zero e pode voltar naturalmente de 255 a zero. Não é necessário recomeçar a música a cada sala: envie o comando de tema apenas quando mudar de região ou iniciar/terminar um chefe.

| Comando | Argumento | Resultado |
|---|---|---|
| 1 | Tema 0 a 10 | Troca a música e começa do início |
| 2 | Efeito 1 a 6 | Toca efeito na quinta voz sem interromper a trilha |
| 3 | 1 / 0 | Silencia / restaura todo o áudio |

| Tema | Região |
|---|---|
| 0 | Castelo / catedral |
| 1 | Biblioteca assombrada |
| 2 | Jardim mítico |
| 3 | Cripta / subsolo |
| 4 | Reservatório |
| 5 | Torre do relógio |
| 6 | Observatório |
| 7 | Núcleo AGI |
| 8 | Chefes |
| 9 | Chefe final |
| 10 | Vitória |

| Efeito | Evento |
|---|---|
| 1 | Ataque |
| 2 | Pulo |
| 3 | Dano |
| 4 | Coleta / abertura |
| 5 | Chefe / impacto grave |
| 6 | Transformação |

## Arranjo e hardware

Quatro vozes são dedicadas à melodia, arpejo, baixo e nota grave do acorde. A quinta voz atende aos efeitos. As vozes restantes permanecem disponíveis. O arranjo conserva as notas e a estrutura das 11 composições autorais da campanha, com redução da polifonia e quantização em semicolcheias. O BPM é aproximado ao temporizador de 500 Hz, com menos de 1% de diferença nos temas atuais. Os oito timbres são formas de onda BRR geradas matematicamente, com envelopes e distribuição estéreo S-DSP. O eco é desativado para evitar escrita em memória usada pelo programa.

Os `.spc` gerados são snapshots adicionais da trilha, reproduzíveis em players SPC. Não são ROMs do jogo. O arquivo binário é código SPC700 real, acompanhado dos instrumentos, diretório de samples, tabelas de afinação e sequências musicais.

## Validação

```sh
python3 validate_audio.py
```

Esta verificação adicional requer `libgme` instalada. Ela executa os 11 programas SPC no emulador independente Game Music Emu e verifica áudio PCM estéreo não silencioso, ausência de erros do emulador e ausência de saturação. O arquivo `build/audio-test-results.json` registra os resultados. `build/castle-emulated-preview.wav` é áudio produzido pelo SPC emulado, e não uma aproximação feita por um sintetizador externo. A compilação da ROM e o protocolo CPU/SPC ainda precisam ser verificados no emulador SNES do projeto principal.

Referências primárias consultadas para instruções e execução: [núcleo SPC700 do Snes9x](https://github.com/snes9xgit/snes9x/tree/master/apu/bapu/smp), [API oficial Game Music Emu](https://github.com/libgme/game-music-emu/blob/master/gme/gme.h). A organização dos registros e o protocolo foram conferidos na documentação de engenharia reversa de eKid e Anomie, em [SPC700 Reference](https://wiki.superfamicom.org/spc700-reference).
