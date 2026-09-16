.a16
.i16
LoadBossArt:
 lda boss
 xba
 asl
 asl
 asl
 clc
 adc #.loword(BossArtR3)
 sta src
 lda #.bankbyte(BossArtR3)
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
 lda boss
 asl
 asl
 asl
 asl
 asl
 clc
 adc #.loword(BossPalR3)
 sta $4302
 lda #32
 sta $4305
 sep #$20
 .a8
 lda #.bankbyte(BossPalR3)
 sta $4304
 stz $4300
 lda #$22
 sta $4301
 lda #$e0
 sta $2121
 lda #1
 sta $420b
 rep #$20
 .a16
 rts
DrawBossR3:
 stz bossquad
@quad:
 lda bossquad
 and #1
 asl
 asl
 asl
 asl
 asl
 clc
 adc bossx
 sec
 sbc #16
 sta sx
 lda bossquad
 and #2
 asl
 asl
 asl
 asl
 clc
 adc bossy
 sec
 sbc #16
 sta sy
 lda bossquad
 asl
 tax
 lda BossQuadTiles,x
 sta stile
 lda #$3c
 sta sattr
 lda #1
 sta ssize
 jsr AddSprite
 inc bossquad
 lda bossquad
 cmp #4
 jne @quad
 stz ssize
 ; A visible mark previews roots or a falling projectile instead of a teleport hit.
 lda bosswarn
 jeq @done
 lda bosswarnx
 sta sx
 lda #173
 sta sy
 lda #460
 sta stile
 lda #$32
 sta sattr
 jsr AddSprite
@done:rts
UpdateBossR3:
 lda bosshp
 jeq @done
 inc bossage
 lda bosshp
 asl
 cmp bossmax
 jcs :+
 lda #1
 sta bossphase
: lda bosstimer
 jeq :+
 dec bosstimer
: lda bosswarn
 jeq :+
 dec bosswarn
: lda boss
 asl
 tax
 jsr (BossLogicTable,x)
 lda bossx
 cmp #24
 jcs :+
 lda #24
: cmp #208
 jcc :+
 lda #208
: sta bossx
 lda bossx
 sec
 sbc px
 jsr Abs
 cmp #35
 jcs @orbit
 lda bossy
 sec
 sbc py
 jsr Abs
 cmp #43
 jcs @orbit
 lda region
 clc
 adc #16
 jsr HurtPlayer
@orbit:
 lda orbit
 jeq @done
 lda frame
 and #31
 jne @done
 lda bossx
 sec
 sbc px
 jsr Abs
 cmp #50
 jcs @done
 lda #12
 jsr HitBoss
@done:rts
; Shared helpers do not define the pattern. Each guardian has its own state logic.
BossAim:
 lda px
 cmp bossx
 jcs :+
 lda #$ffff
 sta bossdir
 rts
: lda #1
 sta bossdir
 rts
BossStep:
 ; A positive speed, direction was locked at the start of the lunge.
 sta t5
 lda bossdir
 jpl :+
 lda t5
 eor #$ffff
 inc a
 sta t5
: lda bossx
 clc
 adc t5
 sta bossx
 rts
BossSin:
 lda bossage
 lsr
 lsr
 and #31
 asl
 tax
 lda WaveR3,x
 rts
BossResetTimer:
 ; A is normal cooldown. Second phase trims one quarter without changing time base.
 sta t5
 lda bossphase
 jeq :+
 lda t5
 lsr
 lsr
 sta t4
 lda t5
 sec
 sbc t4
 sta t5
: lda t5
 sta bosstimer
 inc bosscycle
 rts
ShotFromBoss:
 lda bossx
 clc
 adc #16
 sta t2
 lda bossy
 clc
 adc #16
 sta t3
 rts
BossGroundWave:
 jsr ShotFromBoss
 lda #170
 sta t3
 stz t1
 jsr BossAim
 lda bossdir
 asl
 clc
 adc bossdir
 sta t0
 lda #0
 jsr SpawnBossShot
 rts
BossFan:
 jsr ShotFromBoss
 lda #2
 sta t1
 lda #$fffe
 sta t0
 lda #1
 jsr SpawnBossShot
 stz t0
 lda #1
 jsr SpawnBossShot
 lda #2
 sta t0
 lda #1
 jsr SpawnBossShot
 rts
; 0. Sacristan: grounded, locks direction, wind-up then a continuous hammer charge.
BossSacristan:
 lda #136
 sta bossy
 lda bossmove
 jeq @ready
 dec bossmove
 lda #2
 jsr BossStep
 rts
@ready:
 lda bosstimer
 jne @done
 jsr BossAim
 lda #22
 sta bossmove
 jsr BossGroundWave
 lda #112
 jsr BossResetTimer
@done:rts
; 1. Abbess: suspended orbit, three downward fans of pages.
BossAbbess:
 jsr BossSin
 clc
 adc #82
 sta bossy
 lda bossage
 lsr
 lsr
 lsr
 and #31
 asl
 tax
 lda WaveR3,x
 clc
 adc #158
 sta bossx
 lda bosstimer
 jne @done
 jsr BossFan
 lda #88
 jsr BossResetTimer
@done:rts
; 2. Gardener: anchored trunk; telegraphs roots under the player's position.
BossGardener:
 lda #178
 sta bossx
 lda #132
 sta bossy
 lda bosstimer
 cmp #30
 jne @fire
 lda px
 sta bosswarnx
 lda #30
 sta bosswarn
@fire:
 lda bosstimer
 jne @done
 lda bosswarnx
 sta t2
 lda #176
 sta t3
 stz t0
 lda #$fffd
 sta t1
 lda #2
 jsr SpawnBossShot
 lda t2
 sec
 sbc #24
 sta t2
 lda #2
 jsr SpawnBossShot
 lda t2
 clc
 adc #48
 sta t2
 lda #2
 jsr SpawnBossShot
 lda #125
 jsr BossResetTimer
@done:rts
; 3. Leviathan: swimming sine path across the arena; drifting bubbles.
BossLeviathan:
 jsr BossSin
 asl
 clc
 adc #118
 sta bossx
 lda bossage
 lsr
 and #31
 asl
 tax
 lda WaveR3,x
 clc
 adc #110
 sta bossy
 lda bosstimer
 jne @done
 jsr ShotFromBoss
 lda #1
 sta t1
 lda #2
 sta t0
 lda #1
 jsr SpawnBossShot
 lda #$fffe
 sta t0
 lda #1
 jsr SpawnBossShot
 lda #72
 jsr BossResetTimer
@done:rts
; 4. Founder: slow moving furnace with alternating floor waves and cannon bursts.
BossFounder:
 lda #136
 sta bossy
 lda bossage
 and #1
 jne @attack
 jsr BossAim
 lda #1
 jsr BossStep
@attack:
 lda bosstimer
 jne @done
 lda bosscycle
 and #1
 jeq @stomp
 jsr BossFan
 jmp @reset
@stomp:
 jsr BossGroundWave
@reset:
 lda #98
 jsr BossResetTimer
@done:rts
; 5. Clockmaker: moving clock, cardinal hands become projectiles.
BossClockmaker:
 jsr BossSin
 asl
 clc
 adc #118
 sta bossx
 lda #85
 sta bossy
 lda bosstimer
 jne @done
 jsr ShotFromBoss
 lda #3
 sta t0
 stz t1
 lda #3
 jsr SpawnBossShot
 lda #$fffd
 sta t0
 lda #3
 jsr SpawnBossShot
 stz t0
 lda #3
 sta t1
 lda #3
 jsr SpawnBossShot
 lda #$fffd
 sta t1
 lda #3
 jsr SpawnBossShot
 lda #100
 jsr BossResetTimer
@done:rts
; 6. Astronomer: high orbit and stars falling from marked ceiling positions.
BossAstronomer:
 jsr BossSin
 clc
 adc #130
 sta bossx
 lda bossage
 lsr
 and #31
 asl
 tax
 lda WaveR3,x
 clc
 adc #74
 sta bossy
 lda bosstimer
 cmp #25
 jne :+
 lda px
 sta bosswarnx
 lda #25
 sta bosswarn
: lda bosstimer
 jne @done
 jsr StarRain
 lda #95
 jsr BossResetTimer
@done:rts
StarRain:
 lda bosswarnx
 sta t2
 lda #40
 sta t3
 stz t0
 lda #3
 sta t1
 lda #3
 jsr SpawnBossShot
 lda t2
 clc
 adc #42
 sta t2
 lda #3
 jsr SpawnBossShot
 lda t2
 sec
 sbc #84
 sta t2
 lda #3
 jsr SpawnBossShot
 rts
; 7. Regent: three stages alternate blades, rain and a sustained horizontal attack.
BossRegent:
 jsr BossSin
 clc
 adc #94
 sta bossy
 lda bossmove
 jeq :+
 dec bossmove
 lda #3
 jsr BossStep
: lda bosstimer
 cmp #28
 jne :+
 lda px
 sta bosswarnx
 lda #28
 sta bosswarn
: lda bosstimer
 jne @done
 lda bosscycle
 and #3
 jeq @rain
 cmp #1
 jeq @dash
 jsr BossFan
 jsr BossGroundWave
 jmp @reset
@rain:
 jsr StarRain
 jmp @reset
@dash:
 jsr BossAim
 lda #28
 sta bossmove
 jsr ShotFromBoss
 lda #$fffd
 sta t0
 stz t1
 lda #4
 jsr SpawnBossShot
@reset:
 lda #82
 jsr BossResetTimer
@done:rts
; 8. Mirror knight: rapid pursuit and short, telegraphed sword lunges.
BossDuelist:
 lda #136
 sta bossy
 lda bossmove
 jeq @approach
 dec bossmove
 lda #3
 jsr BossStep
 jmp @done
@approach:
 lda bosstimer
 cmp #24
 jcc @attack
 jsr BossAim
 lda #1
 jsr BossStep
@attack:
 lda bosstimer
 jne @done
 jsr BossAim
 lda #16
 sta bossmove
 jsr ShotFromBoss
 lda bossdir
 asl
 asl
 sta t0
 stz t1
 lda #4
 jsr SpawnBossShot
 lda #76
 jsr BossResetTimer
@done:rts
; 9. Tempest: hovering sword and four diagonal cutting winds.
BossTempest:
 jsr BossSin
 clc
 adc #88
 sta bossy
 lda bossage
 lsr
 lsr
 lsr
 and #31
 asl
 tax
 lda WaveR3,x
 asl
 clc
 adc #120
 sta bossx
 lda bosstimer
 jne @done
 jsr ShotFromBoss
 lda #2
 sta t0
 sta t1
 lda #4
 jsr SpawnBossShot
 lda #$fffe
 sta t0
 lda #4
 jsr SpawnBossShot
 lda #$fffe
 sta t0
 lda #$fffe
 sta t1
 lda #4
 jsr SpawnBossShot
 lda #2
 sta t0
 lda #4
 jsr SpawnBossShot
 lda #65
 jsr BossResetTimer
@done:rts
; Eight independent boss projectiles. A=visual class; t0/t1 velocity, t2/t3 origin.
SpawnBossShot:
 phx
 pha
 ldx #0
@slot:
 lda bplife,x
 jeq @found
 inx
 inx
 cpx #16
 jne @slot
 pla
 plx
 rts
@found:
 pla
 sta bpstyle,x
 lda #140
 sta bplife,x
 lda t2
 sta bpx,x
 lda t3
 sta bpy,x
 lda t0
 sta bpdx,x
 lda t1
 sta bpdy,x
 plx
 rts
UpdateBossShots:
 stz projectileidx
@each:
 ldx projectileidx
 lda bplife,x
 jeq @next
 dec bplife,x
 lda bpx,x
 clc
 adc bpdx,x
 sta bpx,x
 cmp #248
 jcs @clear
 lda bpy,x
 clc
 adc bpdy,x
 sta bpy,x
 cmp #184
 jcs @clear
 cmp #34
 jcc @clear
 lda bpx,x
 sec
 sbc px
 sec
 sbc #8
 jsr Abs
 cmp #13
 jcs @next
 lda bpy,x
 sec
 sbc py
 jsr Abs
 cmp #28
 jcs @next
 lda region
 clc
 adc #14
 jsr HurtPlayer
@clear:
 ldx projectileidx
 stz bplife,x
@next:
 inc projectileidx
 inc projectileidx
 lda projectileidx
 cmp #16
 jcc @each
 rts
DrawBossShots:
 stz projectileidx
@each:
 ldx projectileidx
 lda bplife,x
 jeq @next
 lda bpx,x
 sta sx
 lda bpy,x
 sta sy
 lda bpstyle,x
 and #1
 asl
 clc
 adc #$30
 sta sattr
 lda bpstyle,x
 cmp #4
 jne :+
 lda #448
 sta stile
 lda #1
 sta ssize
 jmp @draw
: lda #460
 sta stile
 stz ssize
@draw:
 jsr AddSprite
@next:
 inc projectileidx
 inc projectileidx
 lda projectileidx
 cmp #16
 jcc @each
 stz ssize
 rts
BossQuadTiles: .word 256,260,320,324
BossLogicTable: .word .loword(BossSacristan),.loword(BossAbbess),.loword(BossGardener),.loword(BossLeviathan),.loword(BossFounder),.loword(BossClockmaker),.loword(BossAstronomer),.loword(BossRegent),.loword(BossDuelist),.loword(BossTempest)
WaveR3: .word 0,5,10,15,19,22,25,27,28,27,25,22,19,15,10,5,0,65531,65526,65521,65517,65514,65511,65509,65508,65509,65511,65514,65517,65521,65526,65531
