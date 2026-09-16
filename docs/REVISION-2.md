# Revisão 2.0: testes e limites

## Alterações implementadas

- Personagem humano de 32 × 48, oito poses de caminhada, repouso, ataque, salto, queda e esquiva. Há 16 quadros no arquivo de gráficos; o quadro adicional de aterrissagem foi reservado, mas não possui estado próprio de animação no motor atual.
- Portas inteiras de 32 × 48 compostas por 24 tiles; várias saídas de uma sala ainda são várias portas, não fragmentos de uma porta.
- Oito cenários refeitos, subpaletas locais, HUD de duas linhas e remoção da faixa inferior permanente.
- Movimento 8.8, aceleração, frenagem, salto variável, buffer e tolerância de borda.
- A geometria e o conteúdo da campanha foram preservados; não foi adicionado scrolling horizontal entre salas.

## Testes automatizados

`tests/validate_rom.py`: cabeçalho, vetor, checksum, bancos CHR, driver de áudio e contagens de campanha.

`tests/validate_graphics.py`: reconstrução dos 16 quadros do herói, porta completa em todas as regiões, tamanhos, índices e valores de paleta válidos.

`tests/validate_revision.py`: Snes9x 1.63, controle de jogador 1; caminhada, frenagem, salto curto/longo, transição de porta, gravação e recuperação da SRAM após nova inicialização. O teste posiciona o personagem por fixtures na RAM e desativa o dano para isolar a física. Não altera a ROM. Resultados em `build/revision-tests.json`.

O teste de movimento detectou 45 atualizações consecutivas da simulação para 45 quadros executados. Isso não equivale a um benchmark de toda a campanha em console físico.

## Limites conhecidos

A reprodução automatizada da campanha antiga, dependente de tempos exatos, não chegou ao final depois da mudança da física. Portanto, não há confirmação de conclusão da campanha revisada inteira. Testes de balanceamento, duração real, animações de todos os inimigos e hardware físico continuam pendentes. A arte dos chefes e de parte dos inimigos conserva componentes da versão anterior.

Não é uma promessa de paridade visual ou de acabamento com jogos comerciais. Trata-se de uma revisão verificável do homebrew existente.
