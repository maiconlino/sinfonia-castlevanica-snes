; Ten mechanically distinct native bosses and eight simultaneous telegraphed hazards.
.a16
.i16
ClearHazards:
 ldx #0
 lda #0
@loop:
 sta hazlife,x
 sta hazage,x
 inx
 inx
 cpx #16
 jne @loop
 rts
SpawnHazard:
 ; sx,sy position; t0,t1 signed velocity; t2 lifetime; t3 archetype.
 phx
 ldx #0
@slot:
 lda hazlife,x
 jeq @found
 inx
 inx
 cpx #16
 jcc @slot
 plx
 rts
@found:
 lda sx
 sta hazx,x
 lda sy
 sta hazy,x
 lda t0
 sta hazdx,x
 lda t1
 sta hazdy,x
 lda t2
 sta hazlife,x
 lda t3
 sta hazkind,x
 stz hazage,x
 plx
 rts
BossShotOrigin:
 lda bossx
 clc
 adc #24
 sta sx
 lda bosssy
 clc
 adc #26
 sta sy
 lda #2
 sta t0
 lda px
 cmp sx
 jcs :+
 lda #$fffe
 sta t0
: lda t0
 sta bossdx
 stz t1
 lda #110
 sta t2
 rts
UpdateBoss:
 lda bosshp
 jeq BossHazards
 inc bossage
 lda bosshp
 asl
 cmp bossmax
 jcs @phaseok
 lda bossphase
 jne @phaseok
 inc bossphase
 lda boss
 cmp #7
 jne @phaseok
 lda maxmp
 lsr
 clc
 adc mp
 sta mp
 jsr Recalculate
@phaseok:
 lda bossmove
 jeq @normalmove
 dec bossmove
 lda bossx
 clc
 adc bossdx
 cmp #12
 jcs :+
 lda #12
: cmp #190
 jcc :+
 lda #190
: sta bossx
 lda boss
 cmp #8
 jne @animate
 ; The ember knight jumps through a complete sine arc during his charge.
 lda bossmove
 and #15
 asl
 tax
 lda f:BossLeap,x
 sta bosssy
 jmp @animate
@normalmove:
 lda boss
 cmp #1
 jeq @float
 cmp #5
 jeq @float
 cmp #6
 jeq @float
 cmp #7
 jeq @float
 cmp #9
 jeq @float
 lda #120
 sta bosssy
 lda boss
 cmp #2
 jeq @animate
 lda bosstimer
 cmp #32
 jcc @animate
 lda bossage
 and #1
 jne @animate
 lda boss
 cmp #8
 jeq @walk
 lda bossage
 and #3
 jne @animate
@walk:
 lda px
 clc
 adc #8
 cmp bossx
 jcs @walkright
 lda bossx
 cmp #20
 jcc @animate
 dec bossx
 jmp @animate
@walkright:
 lda bossx
 cmp #180
 jcs @animate
 inc bossx
 jmp @animate
@float:
 lda bossage
 lsr
 lsr
 and #15
 asl
 tax
 lda f:BossBob,x
 sta bosssy
@animate:
 lda bossage
 lsr
 lsr
 lsr
 lsr
 and #1
 jeq :+
 lda #3
: sta bossanim
 lda bosstimer
 cmp #31
 jcs @timer
 lda #1
 sta bossanim
@timer:
 lda bosstimer
 jeq @fire
 dec bosstimer
 jmp BossContact
@fire:
 inc bosscycle
 lda boss
 asl
 tax
 lda f:BossCadence,x
 sta bosstimer
 lda bossphase
 jeq :+
 lda bosstimer
 sec
 sbc #25
 sta bosstimer
: lda #2
 sta bossanim
 jsr BossShotOrigin
 lda boss
 asl
 tax
 jmp (BossAttackTable,x)
BossAttackComplete:
 lda #3
 jsr SFX
BossContact:
 lda bossx
 clc
 adc #24
 sec
 sbc px
 jsr Abs
 cmp #31
 jcs @orb
 lda bosssy
 clc
 adc #24
 sec
 sbc py
 jsr Abs
 cmp #38
 jcs @orb
 lda region
 clc
 adc #15
 jsr HurtPlayer
@orb:
 lda orbit
 jeq BossHazards
 lda frame
 and #31
 jne BossHazards
 lda bossx
 sec
 sbc px
 jsr Abs
 cmp #55
 jcs BossHazards
 lda #12
 jsr HitBoss
BossHazards:
 jsr UpdateHazards
 rts
BossAttackTable:
 .word .loword(BronzeAttack),.loword(AbbessAttack),.loword(GardenerAttack),.loword(LeviathanAttack),.loword(FounderAttack),.loword(ClockAttack),.loword(AstronomerAttack),.loword(RegentAttack),.loword(KnightAttack),.loword(SwordBossAttack)
BronzeAttack:
 lda #172
 sta sy
 stz t1
 stz t3
 jsr SpawnHazard
 lda sx
 sec
 sbc bossdx
 sec
 sbc bossdx
 sec
 sbc bossdx
 sec
 sbc bossdx
 sta sx
 jsr SpawnHazard
 lda sx
 sec
 sbc bossdx
 sec
 sbc bossdx
 sec
 sbc bossdx
 sec
 sbc bossdx
 sta sx
 jsr SpawnHazard
 lda bossphase
 jeq :+
 lda #24
 sta bossmove
: jmp BossAttackComplete
AbbessAttack:
 lda #1
 sta t3
 lda #$ffff
 sta t1
 jsr SpawnHazard
 stz t1
 jsr SpawnHazard
 lda #1
 sta t1
 jsr SpawnHazard
 jmp BossAttackComplete
GardenerAttack:
 lda #2
 sta t3
 lda #100
 sta t2
 lda px
 sta sx
 sta bossaim
 lda #152
 sta sy
 stz t0
 stz t1
 jsr SpawnHazard
 lda px
 cmp #128
 jcc :+
 sec
 sbc #55
 jmp :++
: clc
 adc #55
: sta sx
 jsr SpawnHazard
 lda bossphase
 jeq :+
 lda #120
 sta sx
 jsr SpawnHazard
: jmp BossAttackComplete
LeviathanAttack:
 lda #36
 sta bossmove
 lda bossdx
 asl
 sta bossdx
 lda #3
 sta t3
 lda #148
 sta sy
 jsr SpawnHazard
 lda #165
 sta sy
 jsr SpawnHazard
 jmp BossAttackComplete
FounderAttack:
 lda #4
 sta t3
 lda #$fffd
 sta t1
 jsr SpawnHazard
 lda t0
 eor #$ffff
 inc a
 sta t0
 jsr SpawnHazard
 stz t0
 lda #$fffc
 sta t1
 jsr SpawnHazard
 jmp BossAttackComplete
ClockAttack:
 lda #5
 sta t3
 lda #100
 sta t2
 jsr SpawnHazard
 lda sy
 clc
 adc #35
 sta sy
 jsr SpawnHazard
 jmp BossAttackComplete
AstronomerAttack:
 lda #6
 sta t3
 lda #108
 sta t2
 stz t0
 stz t1
 lda px
 sta sx
 lda #45
 sta sy
 jsr SpawnHazard
 lda px
 cmp #128
 jcc :+
 sec
 sbc #48
 jmp :++
: clc
 adc #48
: sta sx
 jsr SpawnHazard
 lda bossphase
 jeq :+
 lda #120
 sta sx
 jsr SpawnHazard
: jmp BossAttackComplete
RegentAttack:
 lda bossphase
 jeq @pattern
 lda #22
 sta bossmove
 lda bossdx
 asl
 sta bossdx
@pattern:
 lda bosscycle
 and #3
 jeq AbbessAttack
 cmp #1
 jeq AstronomerAttack
 cmp #2
 jeq FounderAttack
 jmp BronzeAttack
KnightAttack:
 lda #16
 sta bossmove
 lda bossdx
 asl
 sta bossdx
 lda #7
 sta t3
 lda #160
 sta sy
 lda #65
 sta t2
 jsr SpawnHazard
 jmp BossAttackComplete
SwordBossAttack:
 lda #26
 sta bossmove
 lda bossdx
 asl
 sta bossdx
 lda #7
 sta t3
 lda px
 sta sx
 lda #80
 sta sy
 stz t0
 lda #2
 sta t1
 lda #90
 sta t2
 jsr SpawnHazard
 lda px
 cmp #128
 jcc :+
 sec
 sbc #48
 jmp :++
: clc
 adc #48
: sta sx
 jsr SpawnHazard
 jmp BossAttackComplete
UpdateHazards:
 stz hazindex
@each:
 ldx hazindex
 lda hazlife,x
 jeq @next
 dec hazlife,x
 inc hazage,x
 lda hazkind,x
 cmp #2
 jeq @root
 cmp #6
 jeq @meteor
 cmp #4
 jeq @gravity
 cmp #5
 jne @move
 lda hazage,x
 cmp #42
 jne @move
 lda hazdx,x
 eor #$ffff
 inc a
 sta hazdx,x
 jmp @move
@gravity:
 lda hazage,x
 and #7
 jne @move
 inc hazdy,x
 jmp @move
@meteor:
 lda hazage,x
 cmp #30
 jcc @next
 lda #3
 sta hazdy,x
 jmp @move
@root:
 lda hazage,x
 cmp #30
 jcc @next
 jmp @hit
@move:
 lda hazx,x
 clc
 adc hazdx,x
 sta hazx,x
 cmp #248
 jcs @clear
 lda hazy,x
 clc
 adc hazdy,x
 sta hazy,x
 cmp #183
 jcs @clear
 cmp #30
 jcc @clear
@hit:
 lda hazx,x
 sec
 sbc px
 jsr Abs
 cmp #15
 jcs @next
 lda hazy,x
 sec
 sbc py
 jsr Abs
 cmp #28
 jcs @next
 lda region
 clc
 adc #12
 jsr HurtPlayer
 jmp @next
@clear: stz hazlife,x
@next:
 inc hazindex
 inc hazindex
 lda hazindex
 cmp #16
 jcc @each
 rts
DrawHazards:
 stz hazindex
@each:
 ldx hazindex
 lda hazlife,x
 jeq @next
 lda hazx,x
 sta sx
 lda hazy,x
 sta sy
 lda #$30
 sta sattr
 lda hazkind,x
 asl
 clc
 adc #384
 sta stile
 lda hazkind,x
 cmp #2
 jeq @tell
 cmp #6
 jne @sprite
@tell:
 lda hazage,x
 cmp #30
 jcs @sprite
 ; Harmless, flashing ground markers precede roots and falling constellations.
 lda frame
 and #4
 jne @next
 lda #176
 sta sy
 lda #398
 sta stile
@sprite:
 stz ssize
 jsr AddSprite
 ldx hazindex
 lda hazkind,x
 cmp #2
 jne @next
 lda hazage,x
 cmp #30
 jcc @next
 lda sy
 sec
 sbc #16
 sta sy
 jsr AddSprite
@next:
 inc hazindex
 inc hazindex
 lda hazindex
 cmp #16
 jcc @each
 rts
DrawBoss:
 lda bosshp
 jeq @done
 lda bossx
 sta sx
 lda bosssy
 sta sy
 ; Preserve the guardian palette on impact; attack sparks provide the feedback.
 lda #$32
 sta sattr
 lda #1
 sta ssize
 lda #256
 sta stile
 jsr AddSprite
 lda sx
 clc
 adc #32
 sta sx
 lda #260
 sta stile
 jsr AddSprite
 lda sy
 clc
 adc #32
 sta sy
 lda #324
 sta stile
 jsr AddSprite
 lda sx
 sec
 sbc #32
 sta sx
 lda #320
 sta stile
 jsr AddSprite
 stz ssize
@done:rts
UploadBoss:
 lda mode
 cmp #1
 jne @done
 lda bosshp
 jeq @done
 lda bossanim
 cmp bossloaded
 jeq @done
 sta bossloaded
 xba
 asl
 asl
 asl
 clc
 adc #$8000
 sta src
 lda boss
 clc
 adc #13
 sta src+2
 stz bossrow
@row:
 lda bossrow
 xba
 clc
 adc #$5000
 sta t1
 lda #256
 sta t0
 jsr DMAVRAM
 lda src
 clc
 adc #256
 sta src
 inc bossrow
 lda bossrow
 cmp #8
 jne @row
@done:rts
BossCadence: .word 135,120,155,130,145,140,145,125,110,100
BossBob: .word 104,106,109,111,112,111,109,106,104,101,98,96,95,96,98,101
BossLeap: .word 120,111,101,90,80,73,67,64,64,67,73,80,90,101,111,120

LoadBossPalette:
 lda bosshp
 jeq @done
 lda boss
 asl
 asl
 asl
 asl
 asl
 clc
 adc #.loword(BossPalettes)
 sta $4302
 lda #32
 sta $4305
 sep #$20
 .a8
 lda #.bankbyte(BossPalettes)
 sta $4304
 stz $4300
 lda #$22
 sta $4301
 lda #144
 sta $2121
 lda #1
 sta $420b
 rep #$20
 .a16
@done:rts
