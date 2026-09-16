; R3 enemies: all terrestrial archetypes move, turn, telegraph and attack.
UpdateEnemies:
 stz loopidx
@each:
 ldx loopidx
 stz enemymoving,x
 lda enemyhp,x
 jeq @next
 lda enemycool,x
 jeq :+
 dec enemycool,x
: lda enemyhurt,x
 jeq @decision
 dec enemyhurt,x
 jmp @contact
@decision:
 lda slow
 jeq :+
 lda frame
 and #1
 jne @contact
: lda px
 sec
 sbc enemyx,x
 sta t0
 lda #0
 sta enemyface,x
 lda t0
 jpl :+
 lda #1
 sta enemyface,x
: lda t0
 jsr Abs
 sta t1
 lda enemywindup,x
 jeq @choose
 dec enemywindup,x
 jne @contact
 lda t1
 cmp #40
 jcs @contact
 lda enemyy,x
 sec
 sbc py
 jsr Abs
 cmp #30
 jcs @contact
 lda region
 clc
 adc #12
 jsr HurtPlayer
 jmp @contact
@choose:
 lda enemykind,x
 cmp #1
 jeq @bat
 cmp #2
 jeq @archer
 ; Guards and sentinels approach in continuous subpixel steps.
 lda t1
 cmp #26
 jcc @melee
 lda #208
 sta t2
 lda enemykind,x
 cmp #3
 jne @towards
 lda #160
 sta t2
 jmp @towards
@melee:
 lda enemycool,x
 jne @contact
 lda #22
 sta enemywindup,x
 lda #70
 sta enemycool,x
 jmp @contact
@archer:
 lda enemycool,x
 jne @archermove
 lda bulletlife
 jne @archermove
 lda #95
 sta enemycool,x
 lda enemyx,x
 sta bulletx
 lda enemyy,x
 clc
 adc #10
 sta bullety
 lda #90
 sta bulletlife
 stz bulletdy
 lda #2
 sta bulletdx
 lda enemyface,x
 jeq @archermove
 lda #$fffe
 sta bulletdx
@archermove:
 lda #176
 sta t2
 lda t1
 cmp #100
 jcs @towards
 cmp #60
 jcc @retreat
 ; Step laterally even while waiting for the next shot.
 lda frame
 and #32
 jeq @towards
 jmp @retreat
@bat:
 lda #256
 sta t2
 lda py
 sec
 sbc #10
 cmp enemyy,x
 jcs :+
 dec enemyy,x
 jmp @towards
: inc enemyy,x
@towards:
 lda enemyface,x
 jeq @positive
 lda t2
 eor #$ffff
 inc a
 sta t2
 jmp @integrate
@retreat:
 lda enemyface,x
 jne @positive
 lda t2
 eor #$ffff
 inc a
 sta t2
@positive:
@integrate:
 lda enemyx,x
 xba
 and #$ff00
 ora enemyfrac,x
 clc
 adc t2
 cmp #$1000
 jcs :+
 lda #$1000
: cmp #$e000
 jcc :+
 lda #$e000
: pha
 and #$ff
 sta enemyfrac,x
 pla
 xba
 and #$ff
 sta enemyx,x
 lda #1
 sta enemymoving,x
@contact:
 ldx loopidx
 lda enemyx,x
 sec
 sbc px
 jsr Abs
 cmp #13
 jcs @orb
 lda enemyy,x
 sec
 sbc py
 jsr Abs
 cmp #25
 jcs @orb
 lda region
 clc
 adc #10
 jsr HurtPlayer
@orb:
 lda orbit
 jeq @next
 lda frame
 and #15
 jne @next
 ldx loopidx
 lda enemyx,x
 sec
 sbc px
 jsr Abs
 cmp #45
 jcs @next
 lda #10
 sta t2
 jsr HitEnemy
@next:
 inc loopidx
 inc loopidx
 lda loopidx
 cmp #8
 jcc @each
 rts
