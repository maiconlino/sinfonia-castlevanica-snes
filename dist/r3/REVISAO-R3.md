# SinfonIA SNES R3, exploração pelas bordas e combate

## O que mudou

As saídas são atravessadas caminhando até a extremidade esquerda ou direita. Não é preciso apertar Cima em uma porta. O mesmo grafo da campanha web foi preservado: 60 salas, 70 ligações de ida e volta, 10 chefes e 60 tipos de itens. Salas com bifurcações usam duas alturas nas laterais, o piso e uma galeria superior acessível por plataformas. Barreiras continuam respeitando chaves, transformações e passagens secretas. A chegada ocorre na abertura correspondente da outra sala.

A movimentação passou a responder mais rapidamente, com velocidade básica de 2,5 pixels por quadro, aceleração curta e frenagem curta. A animação de caminhada acompanha a distância percorrida. O protagonista permanece visível durante a invulnerabilidade. A comunicação sonora foi alterada para uma fila não bloqueante: um atraso na resposta do SPC700 não interrompe a lógica do jogo. Durante a partida, a transferência do mapa por quadro caiu de 2048 para 640 bytes; a transferência completa permanece nas trocas de sala e nos menus.

Os quatro tipos de inimigos se deslocam. Guardas perseguem, morcegos acompanham a altura, arqueiros ajustam a distância e sentinelas alternam aproximação e investida. Os três tipos terrestres receberam quatro poses de caminhada cada.

Os dez chefes receberam desenhos próprios de 64 × 64 pixels, paletas individuais e rotinas separadas. Sacristão: marreta, investida e onda baixa. Abadessa: movimento suspenso e páginas em leque. Jardineiro: raízes marcadas no chão. Leviatã: trajetória ondulada e bolhas. Fundidor: aproximação lenta, ondas e disparos. Relojoeiro: relógio móvel e disparos cardinais. Astrônoma: órbita alta e estrelas que caem. Regente: combina chuva, leques e investidas em etapas. Cavaleiro: perseguição rápida e estocadas. Espada sem Dono: lâmina flutuante e ventos diagonais. Há até oito projéteis de chefe ativos e uma segunda fase abaixo da metade da vida.

As composições nativas derivadas da versão web foram preservadas, sem substituir a música por silêncio. Não se promete reprodução idêntica de timbres e gráficos entre o navegador e o SNES. Esta continua sendo uma adaptação compacta.

## Como jogar

Direcional: andar. B: pular, segurar aumenta a altura. Y: espada. A: magia equipada. X: consumível. L: esquiva. R: alternar espadas adquiridas. Select: alternar formas adquiridas. Start: inventário. Cima: recuperar e salvar junto ao altar, não mudar de sala.

O primeiro chefe está no Tribunal de Bronze. Partindo da entrada, atravesse as saídas à direita no piso: Escadaria das Gárgulas, Galeria dos Retratos, Capela do Primeiro Eco, Ponte do Juramento, Tribunal de Bronze. Na Capela, a saída superior direita leva ao Arsenal dos Exilados e à Rapieira Lunar. A arma pode ser equipada com R depois de coletada.

Inimigos concedem 15 pontos de experiência. A cada 90 pontos, o personagem sobe de nível, até o limite da rotina de inimigos. Vencer um chefe também aumenta o nível. Níveis elevam vida máxima e dano. Há 12 espadas e seis magias. A magia inicial já está equipada, usa o botão A do controle SNES e consome MP. As letras do controle não correspondem necessariamente às letras do teclado, dependem do mapeamento no emulador.

## O que foi testado

Snes9x 1.63, núcleo libretro. Os relatórios de R3 ficam em `docs/r3`.

* `first_route_r3.py`: percurso da entrada ao primeiro chefe, combate e recompensas, exclusivamente por comandos do controle, sem alteração de RAM.
* `upper_exit_r3.py`: acesso à saída superior da Capela, passagem automática para o Arsenal, coleta da Rapieira Lunar e troca com R, exclusivamente pelo controle.
* `validate_r3.py`: 600 quadros de caminhada alternada sem perder atualizações de lógica ou ocultar o protagonista; ida e volta pelas bordas; movimento dos quatro inimigos; ativação, disparos e segunda fase dos dez chefes; magia inicial; gravação no altar e continuidade por SRAM. Os casos isolados de áudio, inimigos e chefes preparam o cenário explicitamente por escrita de RAM. Isso não é um teste de campanha inteira.

Não foi feita uma nova conclusão integral da campanha R3. Não houve teste no SUPER ZSNES nem em console físico. Nenhum teste garante ausência de lentidão em toda configuração de computador/emulador. A duração de 4 a 6 horas permanece sem validação.

## Salvar e trocar de versão

Use uma nova partida para avaliar R3. Faça backup de seu arquivo de bateria `.srm`. O leiaute de 658 bytes de estado persistente foi preservado, mas não carregue um save state de uma ROM antiga nesta ROM nova. A versão anterior não é sobrescrita pelos arquivos distribuídos de R3.
