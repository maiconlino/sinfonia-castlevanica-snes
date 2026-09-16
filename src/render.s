.a16
.i16
DrawGame:
 lda mode
 cmp #1
 jeq :+
 rts
: jsr SelectHeroFrame
 jsr ClearOAM
 lda #$30
 sta sattr
 stz ssize
 lda inv
 jeq @hero
 lda frame
 and #4
 jne @enemies
@hero:
 lda px
 sta sx
 lda py
 sta sy
 lda form
 jeq @human
 cmp #1
 jeq @wolf
 cmp #2
 jeq @bat
 lda #128
 jmp @animal
@wolf:lda #64
 jmp @animal
@bat:lda #72
@animal:
 sta stile
 lda frame
 and #8
 jeq :+
 lda stile
 clc
 adc #4
 sta stile
: lda #1
 sta ssize
 lda sy
 clc
 adc #16
 sta sy
 lda face
 jeq :+
 lda #$70
 sta sattr
: jsr AddSprite
 stz ssize
 jmp @enemies
@human:
 lda px
 sec
 sbc #8
 sta sx
 lda py
 sec
 sbc #16
 sta sy
 lda #$3e
 sta sattr
 lda face
 jeq :+
 lda #$7e
 sta sattr
: stz stile
 lda #1
 sta ssize
 jsr AddSprite
 stz ssize
 lda sy
 clc
 adc #32
 sta sy
 lda #64
 sta stile
 lda face
 jeq :+
 lda #66
 sta stile
: jsr AddSprite
 lda sx
 clc
 adc #16
 sta sx
 lda #66
 sta stile
 lda face
 jeq :+
 lda #64
 sta stile
: jsr AddSprite
@enemies:
 lda #$30
 sta sattr
 stz ssize
 stz loopidx
@each:
 ldx loopidx
 lda enemyhp,x
 jeq @next
 lda enemyx,x
 sta sx
 lda enemyy,x
 sta sy
 lda enemykind,x
 asl
 tax
 lda f:EnemyTiles,x
 sta stile
 jsr AddSprite
 ldx loopidx
 lda enemykind,x
 cmp #1
 beq @next
 lda stile
 clc
 adc #32
 sta stile
 lda sy
 clc
 adc #16
 sta sy
 jsr AddSprite
@next:
 inc loopidx
 inc loopidx
 lda loopidx
 cmp #8
 jcc @each
 lda bosshp
 jeq @attacks
 lda bossx
 sta sx
 lda #136
 sta sy
 lda boss
 asl
 tax
 lda f:BossTiles,x
 sta stile
 lda #1
 sta ssize
 lda #$30
 sta sattr
 lda bosstimer
 cmp #30
 jcs :+
 lda frame
 and #4
 jeq :+
 lda #$32
 sta sattr
: lda bosshit
 jeq :+
 lda #$34
 sta sattr
: jsr AddSprite
 stz ssize
@attacks:
 lda #$30
 sta sattr
 lda attack
 jeq @shot
 lda px
 clc
 adc #14
 sta sx
 lda face
 jeq :+
 lda px
 sec
 sbc #25
 sta sx
 lda #$70
 sta sattr
: lda py
 clc
 adc #4
 sta sy
 lda #448
 sta stile
 lda frame
 and #4
 jeq :+
 lda #452
 sta stile
: lda #1
 sta ssize
 jsr AddSprite
 lda weapon
 cmp #11
 jne @shot
 lda sy
 sec
 sbc #10
 sta sy
 lda sx
 clc
 adc #15
 sta sx
 jsr AddSprite
@shot:
 stz ssize
 lda shotlife
 jeq @bullet
 lda shotx
 sta sx
 lda shoty
 sta sy
 lda #456
 sta stile
 lda #$30
 sta sattr
 jsr AddSprite
@bullet:
 lda bulletlife
 jeq @orbit
 lda bulletx
 sta sx
 lda bullety
 sta sy
 lda #460
 sta stile
 lda #$32
 sta sattr
 jsr AddSprite
@orbit:
 lda orbit
 jeq @items
 lda frame
 lsr
 and #15
 asl
 tax
 lda f:OrbitX,x
 clc
 adc px
 sta sx
 lda f:OrbitY,x
 clc
 adc py
 sta sy
 lda #456
 sta stile
 lda #$30
 sta sattr
 jsr AddSprite
@items:
 ; Pickups are native BG tiles, erased after collection.
 stz itemidx
@pickup:
 lda itemidx
 asl
 asl
 asl
 asl
 clc
 adc #(22*64+8*2)
 tax
 lda #0
 sta MAP,x
 lda bosshp
 jne @pnext
 lda room
 asl
 tax
 lda itemidx
 asl
 tay
 lda looted,x
 and BitMasks,y
 jne @pnext
 lda room
 asl
 clc
 adc room
 clc
 adc itemidx
 tax
 lda f:room_items,x
 and #$ff
 cmp #255
 jeq @pnext
 lda itemidx
 asl
 asl
 asl
 asl
 clc
 adc #(22*64+8*2)
 tax
 lda #$2070
 sta MAP,x
@pnext:
 inc itemidx
 lda itemidx
 cmp #3
 jcc @pickup
 jsr DrawHUD
 rts
DrawHUD:
 lda #$2000
 sta textcolor
 TEXT HpLabel,0,1
 lda #6
 sta textpos
 lda hp
 jsr PrintNumber
 TEXT MpLabel,0,9
 lda #22
 sta textpos
 lda mp
 jsr PrintNumber
 TEXT LvLabel,0,17
 lda #38
 sta textpos
 lda level
 jsr PrintNumber
 TEXT GoldLabel,0,25
 lda #54
 sta textpos
 lda gold
 jsr PrintNumber
 lda #66
 sta textpos
 lda weapon
 jsr NameItem
 ; Full-width bars: twenty-four health cells on row2.
 lda hp
 sta t0
 lda maxhp
 lsr
 lsr
 lsr
 lsr
 sta t1
 lda #0
 sta t2
 ldx #(2*64+2)
@bar:
 lda t0
 cmp t1
 jcc @empty
 sec
 sbc t1
 sta t0
 lda #$2076
 jmp @put
@empty:
 lda #$2077
@put:
 sta MAP,x
 inx
 inx
 inc t2
 lda t2
 cmp #16
 jcc @bar
 lda form
 asl
 asl
 asl
 clc
 adc #.loword(FormNames)
 sta ptr
 lda #.bankbyte(FormNames)
 sta ptr+2
 lda #(2*64+42)
 sta textpos
 jsr Print
 ldx #(25*64)
 lda #0
@clear:
 sta MAP,x
 inx
 inx
 cpx #(27*64)
 jcc @clear
 lda bosshp
 jeq @message
 lda #(25*64+2)
 sta textpos
 lda boss
 asl
 asl
 asl
 asl
 asl
 clc
 adc #.loword(boss_name)
 sta ptr
 lda #.bankbyte(boss_name)
 sta ptr+2
 jsr Print
 lda #(26*64+2)
 sta textpos
 lda bosshp
 jsr PrintNumber
 lda bosstimer
 cmp #30
 jcs @message
 TEXT WarningLine,26,10
@message:
 lda message
 jeq @done
 lda messageid
 cmp #1
 jne @locked
 lda #(26*64+2)
 sta textpos
 lda messageitem
 jsr NameItem
 rts
@locked:
 cmp #2
 jne @secret
 TEXT NeedLine,25,1
 lda #(26*64+2)
 sta textpos
 lda messageitem
 jsr NameItem
 rts
@secret:
 cmp #3
 jne @save
 TEXT SecretLine,26,1
 rts
@save:
 cmp #4
 jne @boss
 TEXT SavedLine,26,1
 rts
@boss:
 cmp #5
 jne @died
 TEXT BossBlockedLine,26,1
 rts
@died:
 TEXT DeathLine,26,1
@done:rts
EndingScreen:
 jsr Blank
 jsr ClearMap
 jsr ClearOAM
 lda #$2000
 sta textcolor
 TEXT Ending1,3,3
 TEXT Ending2,6,2
 TEXT Ending3,8,2
 TEXT Ending4,10,2
 TEXT Ending5,12,2
 TEXT Ending6,14,2
 TEXT Ending7,17,3
 TEXT Ending8,19,3
 TEXT Ending9,23,2
 TEXT Ending10,25,2
 lda #10
 jsr Music
 jsr Unblank
 rts
AudioInit:
 lda #$ffff
 sta soundarg
 sep #$20
 .a8
 jsr AudioBoot
 rep #$20
 .a16
 rts
SFX:
 phx
 phy
 tax
 sep #$20
 .a8
 lda #2
 jsr AudioCommand
 rep #$20
 .a16
 ply
 plx
 rts
Music:
 cmp soundarg
 beq @same
 sta soundarg
 phx
 phy
 tax
 sep #$20
 .a8
 lda #1
 jsr AudioCommand
 rep #$20
 .a16
 ply
 plx
@same:rts
RoomMusic:
 lda region
 ldx bosshp
 jeq @play
 lda #8
 ldx boss
 cpx #7
 jne @play
 lda #9
@play:
 jsr Music
 rts
IRQ:
 rti

BitMasks: .word 1,2,4,8
Decimal: .word 1000,100,10,1
RegionCHRBank: .word 3,4,5,6,7,8,9,10
EnemyTiles: .word 192,72,196,200
BossTiles: .word 256,260,264,268,320,324,328,332,384,388
OrbitX: .word 32,30,24,12,0,65524,65512,65506,65504,65506,65512,65524,0,12,24,30
OrbitY: .word 12,24,36,42,44,42,36,24,12,0,65526,65520,65518,65520,65526,0
FormNames: .byte "HUMANO",0,0,"LOBO",0,0,0,0,"MORCEGO",0,"NEVOA",0,0,0
Title1: .asciiz "SINFONIA"
Title2: .asciiz "CASTLEVANICA"
Title3: .asciiz "FUTURISTICA"
HeroLine: .asciiz "AUREL VESPER"
StartLine: .asciiz "START: NOVO JOGO"
ContinueLine: .asciiz "SELECT: CONTINUAR SRAM"
Controls1: .asciiz "Y ESPADA  B SALTO  A MAGIA"
Controls2: .asciiz "X POCAO L ESQUIVA R ESPADA"
Controls3: .asciiz "SELECT FORMA START MENU"
CreditsLine: .asciiz "MAICON LINO / ASTRA  2026"
Footer1: .asciiz "CIMA PORTA/ALTAR  START MENU"
HpLabel: .asciiz "V:"
MpLabel: .asciiz "M:"
LvLabel: .asciiz "N:"
GoldLabel: .asciiz "E:"
NeedLine: .asciiz "REQUER ITEM E FORMA:"
SecretLine: .asciiz "PASSAGEM SECRETA REVELADA!"
SavedLine: .asciiz "CURADO E SALVO NO CARTUCHO"
BossBlockedLine: .asciiz "DERROTE O GUARDIAO PRIMEIRO"
DeathLine: .asciiz "SEU ECO RETORNA AO ALTAR"
WarningLine: .asciiz "ATAQUE! ESQUIVE!"
Ending1: .asciiz "O PRIMEIRO AMANHECER"
Ending2: .asciiz "O REGENTE NULO SILENCIOU."
Ending3: .asciiz "AS VOZES AGORA ESCOLHEM:"
Ending4: .asciiz "PARTIR OU FICAR COMO ECOS."
Ending5: .asciiz "SUA MAE SE DESPEDE LIVRE."
Ending6: .asciiz "O CASTELO VOLTA A RESPIRAR."
Ending7: .asciiz "UMA LEMBRANCA PODE FICAR."
Ending8: .asciiz "UMA VIDA PRECISA SEGUIR."
Ending9: .asciiz "FIM / MAICON LINO E ASTRA"
Ending10: .asciiz "START: EXPLORAR OS SEGREDOS"

; Hero selection is separate from movement and keyed to the current action.
SelectHeroFrame:
 lda form
 jne @done
 lda dash
 jne @dash
 lda attack
 jeq @air
 cmp #6
 jcs @windup
 cmp #3
 jcs @swing
 lda #12
 jmp @store
@windup: lda #10
 jmp @store
@swing: lda #11
 jmp @store
@dash: lda #15
 jmp @store
@air:
 lda grounded
 jne @walk
 lda vy
 jmi @rise
 lda #14
 jmp @store
@rise: lda #13
 jmp @store
@walk:
 lda vx
 jeq @idle
 lda walkphase
 lsr
 lsr
 and #7
 clc
 adc #2
 jmp @store
@idle:
 lda frame
 lsr
 lsr
 lsr
 lsr
 lsr
 and #1
@store: sta hero_frame
@done: rts

; The OBJ grid has 16 tiles per row. Upload only the 4 tiles of each pose row.
; Normal frame cost is zero when the pose did not change; changed pose = 768 bytes.
UploadHero:
 lda mode
 cmp #1
 jne @done
 lda form
 jne @restore
 lda hero_frame
 cmp hero_cache
 jeq @done
 sta hero_cache
 xba
 sta t1
 asl
 clc
 adc t1
 clc
 adc #.loword(HeroFrames)
 sta src
 lda #.bankbyte(HeroFrames)
 sta src+2
 stz hero_dma_row
@row:
 lda hero_dma_row
 xba
 clc
 adc #$4000
 sta t1
 lda #128
 sta t0
 jsr DMAVRAM
 lda src
 clc
 adc #128
 sta src
 inc hero_dma_row
 lda hero_dma_row
 cmp #6
 jne @row
 rts
@restore:
 lda hero_cache
 cmp #$ffff
 jeq @done
 lda #$ffff
 sta hero_cache
 lda #.loword(ObjCHR)
 sta src
 lda #.bankbyte(ObjCHR)
 sta src+2
 lda #$4000
 sta t1
 lda #3072
 sta t0
 jsr DMAVRAM
@done:rts
