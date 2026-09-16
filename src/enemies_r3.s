.a16
.i16
UpdateEnemies:
 stz loopidx
@each:
 ldx loopidx
 lda enemyhp,x
 jeq @next
 lda enemycool,x
 jeq :+
 dec enemycool,x
: lda enemystun,x
 jeq @choose
 dec enemystun,x
 jmp @contact
@choose:
 lda #192
 sta t0
 lda enemykind,x
 cmp #1
 jeq @bat
 cmp #2
 jeq @archer
 cmp #3
 jne @pursue
 ; Sentinel telegraphs a short forward lunge, then resumes a steady patrol.
 lda enemycool,x
 jne :+
 lda #100
 sta enemycool,x
: cmp #18
 jcs @pursue
 lda #$0240
 sta t0
 jmp @pursue
@bat:
 lda #$0120
 sta t0
 lda py
 sec
 sbc #12
 cmp enemyy,x
 jeq @pursue
 jcs :+
 dec enemyy,x
 jmp @pursue
: inc enemyy,x
 jmp @pursue
@archer:
 lda px
 sec
 sbc enemyx,x
 jsr Abs
 cmp #88
 jcs @pursue
 cmp #62
 jcs @fire
 ; Archers retreat to restore bow range, rather than standing still.
 lda #$0080
 sta t0
 lda px
 cmp enemyx,x
 jcs @moveleft
 jmp @moveright
@pursue:
 lda px
 cmp enemyx,x
 jcc @moveleft
@moveright:
 stz enemyfacing,x
 jmp @integrate
@moveleft:
 lda #1
 sta enemyfacing,x
 lda t0
 eor #$ffff
 inc a
 sta t0
@integrate:
 lda slow
 jeq :+
 lda t0
 cmp #$8000
 ror
 sta t0
: lda enemyx,x
 xba
 and #$ff00
 ora enemyfrac,x
 clc
 adc t0
 cmp #$0e00
 jcs :+
 lda #$0e00
: cmp #$e000
 jcc :+
 lda #$e000
: pha
 and #255
 sta enemyfrac,x
 pla
 xba
 and #255
 sta enemyx,x
 inc enemyanim,x
@fire:
 lda enemykind,x
 cmp #2
 jne @contact
 lda enemycool,x
 jne @contact
 lda bulletlife
 jne @contact
 lda #105
 sta enemycool,x
 lda enemyx,x
 sta bulletx
 lda enemyy,x
 clc
 adc #10
 sta bullety
 lda #100
 sta bulletlife
 stz bulletdy
 lda #2
 sta bulletdx
 lda px
 cmp bulletx
 jcs @contact
 lda #$fffe
 sta bulletdx
@contact:
 ldx loopidx
 lda enemyx,x
 sec
 sbc px
 jsr Abs
 cmp #16
 jcs @orb
 lda enemyy,x
 sec
 sbc py
 jsr Abs
 cmp #27
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
