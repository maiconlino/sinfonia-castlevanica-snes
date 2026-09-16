# Revisão 2, movimento e leitura visual

Data: 16/09/2026.

ROM testada: `57d02a02c1346b2380707635c6c88be04cd50c781d34259d9f39e6c8be11d38f`.

## Alterações implementadas

O protagonista humano passou de um desenho de 16 × 32 para poses de 32 × 48 pixels. São 16 poses: duas de repouso, oito de caminhada, três etapas de ataque, subida, queda e esquiva. Os pixels de cabelo, capa, roupa e espada são definidos na arte de origem e convertidos para o formato nativo 4bpp. A paleta própria do personagem usa 14 cores visíveis, além da transparência.

A composição do personagem usa um objeto de 32 × 32 e dois objetos de 16 × 16. Os gráficos são enviados à VRAM apenas quando a pose muda. A transferência respeita as dezesseis colunas da grade de tiles do SNES, evitando partes repetidas ou deslocadas. Ao transformar em animal, a região compartilhada do atlas é restaurada.

A física agora usa acumuladores de ponto fixo 8.8, aceleração de 0,375 pixel por quadro e frenagem de 0,5 pixel por quadro. O salto tem gravidade por quadro, altura variável ao soltar B, tolerância de seis quadros após sair de uma borda e armazenamento de seis quadros para um comando de salto dado pouco antes de aterrissar. A caminhada atinge 2 pixels por quadro sem equipamentos. As alterações não modificam o esquema ou a disposição do salvamento SRAM.

Cada porta visível é um arco contínuo de 32 × 40 pixels, composto por vinte tiles diferentes. A repetição da mesma miniatura de porta foi removida. As passagens secretas mantêm uma parede antes de serem reveladas. O altar também é uma composição única de 24 × 24 pixels. O primeiro ambiente recebeu colunas, cantaria e janelas mais detalhadas, preservando a paleta de dezesseis cores.

## Verificação realizada nesta ROM

Emulador: Snes9x 1.63, núcleo libretro identificado como `921f9f7`, Linux x86-64. Vídeo nativo de 256 × 224 e áudio estéreo não silencioso.

1. Conversão dos oito fundos e das dezesseis poses para tiles 4bpp, seguida de reconstrução dos pixels, sem divergência.
2. Cabeçalho, mapa LoROM, vetor de inicialização, bancos gráficos, áudio e checksum verificados.
3. Teste de seiscentos quadros de jogo ativo com ataque e salto: seiscentas atualizações, sem quadros de lógica perdidos nesse trecho. Não é uma medição em console físico nem uma garantia universal de desempenho.
4. Aceleração, frenagem, oito poses de caminhada, salto curto de 21 pixels e salto sustentado de 75 pixels verificados por comandos do controle.
5. Salvamento em altar e continuidade depois de reiniciar o emulador, usando o arquivo de SRAM como uma bateria emulada.
6. Campanha completa percorrida por comandos do controle: sessenta salas, dez chefes, sessenta tipos de itens adquiridos e final exibido, sem mortes.
7. Repetição independente da gravação dos botões, sem consultar a memória durante a partida, chegando ao mesmo final.

A execução adaptativa usa leitura de WRAM para decidir os comandos, mas não escreve estado do jogo, posições, inventário, vida, códigos de trapaça ou save states. A carga de SRAM é feita apenas no teste específico de persistência, como parte da emulação do arquivo de bateria.

O percurso automatizado completo teve 19.745 quadros, aproximadamente 5 minutos e 29 segundos de tempo emulado, com conhecimento antecipado do mapa. Não representa a duração de uma primeira partida humana e não comprova a meta de 4 a 6 horas. Esta continua sendo uma adaptação compacta, não uma reprodução de toda a complexidade visual e física de um jogo comercial de SNES.

Os relatórios antigos em `docs/` identificam a ROM de referência da primeira versão. Os relatórios e comandos da revisão atual estão em `build/qa-revision/` e acompanham o pacote de distribuição. Não atribuir resultados da primeira versão a esta ROM sem executar novamente o teste correspondente.

## Reproduzir

```sh
python3 tools/build_content.py
python3 tools/generate_graphics.py
python3 tools/build_audio.py
python3 tools/build.py
python3 tests/validate_graphics.py
python3 tests/validate_rom.py
SNES_CORE=/caminho/snes9x_libretro.so python3 tests/test_movement_revision.py
SNES_CORE=/caminho/snes9x_libretro.so python3 tests/adaptive_revision.py
SNES_CORE=/caminho/snes9x_libretro.so python3 tests/replay_revision.py
```

O emulador e o compilador não são distribuídos dentro do jogo. `ca65` e `ld65` podem ser localizados pelo PATH ou pelas variáveis `CA65` e `LD65`. A geração da arte exige Pillow. A ROM `.smc` distribuída contém exatamente os mesmos bytes da `.sfc`, sem cabeçalho externo de copiador.
