; SinfonIA Castlevanica Futuristica - native SNES homebrew
; 65C816, LoROM, Mode 1, 16/32 pixel OBJ, SPC700, battery SRAM.
.setcpu "65816"
.smart
.include "longbranch.inc"

JOY_B=$8000
JOY_Y=$4000
JOY_SELECT=$2000
JOY_START=$1000
JOY_UP=$0800
JOY_DOWN=$0400
JOY_LEFT=$0200
JOY_RIGHT=$0100
JOY_A=$0080
JOY_X=$0040
JOY_L=$0020
JOY_R=$0010
MAP=$1000
OAM=$0200
SRAM=$700000

.segment "ZEROPAGE"
frame: .res 2
pad: .res 2
pressed: .res 2
oldpad: .res 2
mode: .res 2
region: .res 2
oldregion: .res 2
face: .res 2
vy: .res 2
jumps: .res 2
form: .res 2
inv: .res 2
attack: .res 2
attackcd: .res 2
magiccd: .res 2
dash: .res 2
dashcd: .res 2
slow: .res 2
orbit: .res 2
maxhp: .res 2
maxmp: .res 2
damage: .res 2
reach: .res 2
boss: .res 2
bosshp: .res 2
bossmax: .res 2
bossx: .res 2
bossphase: .res 2
bosstimer: .res 2
bosscycle: .res 2
bosshit: .res 2
bulletx: .res 2
bullety: .res 2
bulletdx: .res 2
bulletdy: .res 2
bulletlife: .res 2
shotx: .res 2
shoty: .res 2
shotdx: .res 2
shotdy: .res 2
shotlife: .res 2
shotdamage: .res 2
message: .res 2
messageid: .res 2
messageitem: .res 2
lastroom: .res 2
menuitem: .res 2
menupage: .res 2
spritecount: .res 2
sx: .res 2
sy: .res 2
stile: .res 2
sattr: .res 2
ssize: .res 2
t0: .res 2
t1: .res 2
t2: .res 2
t3: .res 2
t4: .res 2
t5: .res 2
ptr: .res 3
src: .res 3
textpos: .res 2
textcolor: .res 2
loopidx: .res 2
exitidx: .res 2
itemidx: .res 2
savedvalid: .res 2
soundseq: .res 2
soundcmd: .res 2
soundarg: .res 2
soundready: .res 2
prevy: .res 2
respawn: .res 2
vx: .res 2
xsub: .res 2
ysub: .res 2
grounded: .res 2
coyote: .res 2
jumpbuffer: .res 2
walkphase: .res 2
hero_frame: .res 2
hero_cache: .res 2
hero_dma_row: .res 2


.segment "STATE"
state_begin:
room: .res 2
checkpoint: .res 2
px: .res 2
py: .res 2
hp: .res 2
mp: .res 2
gold: .res 2
level: .res 2
xp: .res 2
weapon: .res 2
armor: .res 2
accessory: .res 2
spell: .res 2
potion: .res 2
finished: .res 2
kills: .res 2
deaths: .res 2
playseconds: .res 2
auroraused: .res 2
inventory: .res 120
visited: .res 120
secrets: .res 120
looted: .res 120
defeated: .res 20
shrines: .res 120
state_end:
STATE_SIZE=state_end-state_begin

.segment "WORK"
enemyx: .res 8
enemyy: .res 8
enemyhp: .res 8
enemycool: .res 8
enemykind: .res 8

.segment "CODE"
.a8
.i8
Reset:
 sei
 clc
 xce
 rep #$38
 .a16
 .i16
 ldx #$1fff
 txs
 lda #0
 tcd
 sep #$20
 .a8
 pha
 plb
 lda #$80
 sta $2100
 stz $4200
 stz $420b
 stz $420c
 rep #$20
 .a16
 lda #0
 ldx #$0000
@clear:
 sta $0000,x
 inx
 inx
 cpx #$1f00
 jne @clear
 ; Screen and display registers.
 sep #$20
 .a8
 lda #$62
 sta $2101
 lda #1
 sta $2105
 lda #$60
 sta $2107
 stz $2108
 stz $2109
 stz $210a
 stz $210b
 stz $210c
 stz $210d
 stz $210d
 stz $210e
 stz $210e
 stz $211b
 stz $211b
 lda #$80
 sta $2115
 stz $2123
 stz $2124
 stz $2125
 stz $212e
 stz $212f
 stz $2130
 stz $2131
 stz $2133
 lda #$11
 sta $212c
 stz $212d
 lda #$e0
 sta $2132
 rep #$20
 .a16
 jsr AudioInit
 jsr LoadObjects
 lda #$ffff
 sta oldregion
 jsr CheckSave
 lda #0
 sta region
 jsr LoadRegion
 jsr TitleScreen
 lda #0
 sta mode
 sep #$20
 .a8
 lda #1
 sta $4200
 lda #15
 sta $2100
 rep #$20
 .a16
MainLoop:
 jsr WaitFrame
 jsr ReadPad
 jsr UploadFrame
 inc frame
 lda mode
 jeq TitleTick
 cmp #2
 jeq MenuTick
 cmp #3
 jeq EndingTick
 jsr GameTick
 jsr DrawGame
 jmp Present
TitleTick:
 lda pressed
 and #JOY_SELECT
 jeq @new
 lda savedvalid
 jeq @new
 jsr LoadSave
 lda #1
 sta mode
 lda #$ffff
 sta lastroom
 jsr EnterRoom
 jmp Present
@new:
 lda pressed
 and #(JOY_START|JOY_A|JOY_B)
 jeq Present
 jsr NewGame
 jmp Present
MenuTick:
 jsr UpdateMenu
 jmp Present
EndingTick:
 lda pressed
 and #(JOY_START|JOY_B|JOY_A)
 jeq Present
 lda checkpoint
 sta room
 lda #1
 sta mode
 lda #$ffff
 sta lastroom
 jsr EnterRoom
 jmp Present
Present:
 jmp MainLoop

; All callable routines enter/return A16 X16 DB=0.
WaitFrame:
 sep #$20
 .a8
@out: lda $4212
 jmi @out
@in: lda $4212
 jpl @in
@joy: lda $4212
 and #1
 jne @joy
 rep #$20
 .a16
 rts
ReadPad:
 lda $4218
 sta pad
 eor oldpad
 and pad
 sta pressed
 lda pad
 sta oldpad
 rts
UploadFrame:
 ; Call during VBlank after game tick. If tick ran long, wait for a new blank.
 sep #$20
 .a8
 lda $4212
 jmi @go
@wait: lda $4212
 jpl @wait
@go:
 stz $2102
 stz $2103
 stz $4300
 lda #$04
 sta $4301
 rep #$20
 .a16
 lda #OAM
 sta $4302
 lda #544
 sta $4305
 sep #$20
 .a8
 stz $4304
 lda #1
 sta $420b
 lda #$80
 sta $2115
 rep #$20
 .a16
 lda #$6000
 sta $2116
 lda #MAP
 sta $4302
 lda #2048
 sta $4305
 sep #$20
 .a8
 lda #1
 sta $4300
 lda #$18
 sta $4301
 stz $4304
 lda #1
 sta $420b
 rep #$20
 .a16
 jsr UploadHero
 rts
Blank:
 sep #$20
 .a8
 lda #$80
 sta $2100
 rep #$20
 .a16
 rts
Unblank:
 jsr WaitFrame
 jsr UploadFrame
 sep #$20
 .a8
 lda #15
 sta $2100
 rep #$20
 .a16
 rts
; ROM source src; count t0; VRAM word address t1.
DMAVRAM:
 lda t1
 sta $2116
 lda src
 sta $4302
 lda t0
 sta $4305
 sep #$20
 .a8
 lda src+2
 sta $4304
 lda #1
 sta $4300
 lda #$18
 sta $4301
 lda #$80
 sta $2115
 lda #1
 sta $420b
 rep #$20
 .a16
 rts
LoadObjects:
 lda #$ffff
 sta hero_cache
 lda #.loword(ObjCHR)
 sta src
 lda #.bankbyte(ObjCHR)
 sta src+2
 lda #$4000
 sta t1
 lda #16384
 sta t0
 jsr DMAVRAM
 lda #.loword(ObjPal)
 sta $4302
 lda #256
 sta $4305
 sep #$20
 .a8
 lda #.bankbyte(ObjPal)
 sta $4304
 stz $4300
 lda #$22
 sta $4301
 lda #$80
 sta $2121
 lda #1
 sta $420b
 rep #$20
 .a16
 rts
LoadRegion:
 jsr Blank
 lda region
 asl
 tax
 lda f:RegionCHRBank,x
 sta src+2
 lda #$8000
 sta src
 lda #0
 sta t1
 lda #32768
 sta t0
 jsr DMAVRAM
 lda region
 asl
 asl
 asl
 asl
 asl
 clc
 adc #.loword(RegionPal)
 sta $4302
 lda #32
 sta $4305
 sep #$20
 .a8
 lda #.bankbyte(RegionPal)
 sta $4304
 stz $4300
 lda #$22
 sta $4301
 stz $2121
 lda #1
 sta $420b
 rep #$20
 .a16
 lda region
 sta oldregion
 rts
BaseMap:
 lda region
 xba
 asl
 asl
 asl
 clc
 adc #.loword(RegionMaps)
 sta src
 lda #.bankbyte(RegionMaps)
 sta src+2
 ldy #0
@copy:
 lda [src],y
 sta MAP,y
 iny
 iny
 cpy #2048
 jne @copy
 rts
ClearMap:
 lda #0
 ldx #0
@loop: sta MAP,x
 inx
 inx
 cpx #2048
 jne @loop
 rts
ClearOAM:
 lda #0
 sta spritecount
 ldx #0
@clear:
 lda #$f000
 sta OAM,x
 lda #0
 sta OAM+2,x
 inx
 inx
 inx
 inx
 cpx #512
 jne @clear
 ldx #0
@hi: sta OAM+512,x
 inx
 inx
 cpx #32
 jne @hi
 rts
; Add a sprite using sx,sy,stile(9bit),sattr,ssize(0=16,1=32).
AddSprite:
 lda spritecount
 cmp #100
 jcs @done
 asl
 asl
 tax
 lda sy
 xba
 and #$ff00
 sta t5
 lda sx
 and #$00ff
 ora t5
 sta OAM,x
 lda stile
 and #$0100
 xba
 ora sattr
 xba
 sta t5
 lda stile
 and #$ff
 ora t5
 sta OAM+2,x
 lda spritecount
 and #3
 asl
 tay
 lda ssize
 asl
 sta t5
 lda sx
 and #$0100
 xba
 ora t5
@shift: cpy #0
 jeq @placed
 asl
 dey
 jmp @shift
@placed:
 sta t5
 lda spritecount
 lsr
 lsr
 tax
 sep #$20
 .a8
 lda OAM+512,x
 ora t5
 sta OAM+512,x
 rep #$20
 .a16
 inc spritecount
@done: rts
; ptr=24bit string; textpos=VRAM map buffer byte offset; textcolor=attribute.
Print:
 ldy #0
 ldx textpos
@char:
 lda [ptr],y
 and #$ff
 jeq @done
 cmp #32
 jcc @done
 sec
 sbc #32
 ora textcolor
 sta MAP,x
 inx
 inx
 iny
 cpy #32
 jne @char
@done:rts
PrintNumber:
 ; A unsigned0..9999, textpos; always 4 decimal positions.
 sta t3
 lda #0
 sta t4
 ldx textpos
 ldy #0
@digit:
 lda #0
 sta t2
@sub:
 lda t3
 cmp Decimal,y
 jcc @put
 sec
 sbc Decimal,y
 sta t3
 inc t2
 jmp @sub
@put:
 lda t2
 clc
 adc #16
 ora #$2000
 sta MAP,x
 inx
 inx
 iny
 iny
 cpy #8
 jne @digit
 rts
.macro TEXT label, row, col
 lda #.loword(label)
 sta ptr
 lda #.bankbyte(label)
 sta ptr+2
 lda #(row*64+col*2)
 sta textpos
 jsr Print
.endmacro
; Fixed 32 byte ASCII table, index A.
NameRoom:
 asl
 asl
 asl
 asl
 asl
 clc
 adc #.loword(room_name)
 sta ptr
 lda #.bankbyte(room_name)
 sta ptr+2
 jsr Print
 rts
NameItem:
 asl
 asl
 asl
 asl
 asl
 clc
 adc #.loword(item_name)
 sta ptr
 lda #.bankbyte(item_name)
 sta ptr+2
 jsr Print
 rts
TitleScreen:
 jsr BaseMap
 jsr ClearOAM
 lda #$2000
 sta textcolor
 TEXT Title1,4,5
 TEXT Title2,6,3
 TEXT Title3,7,8
 TEXT HeroLine,10,6
 TEXT StartLine,14,7
 lda savedvalid
 jeq @no
 TEXT ContinueLine,16,5
@no:
 TEXT Controls1,20,2
 TEXT Controls2,21,2
 TEXT Controls3,22,2
 TEXT CreditsLine,25,3
 jsr Unblank
 rts
NewGame:
 ldx #0
 lda #0
@clear: sta state_begin,x
 inx
 inx
 cpx #STATE_SIZE
 jcc @clear
 lda #1
 sta inventory
 sta inventory+24
 sta inventory+60
 sta inventory+76
 sta inventory+88
 sta level
 sta mode
 lda #3
 sta inventory+88
 lda #12
 sta armor
 lda #$ffff
 sta accessory
 sta lastroom
 lda #38
 sta spell
 lda #44
 sta potion
 jsr Recalculate
 lda maxhp
 sta hp
 lda maxmp
 sta mp
 lda #80
 sta px
 lda #152
 sta py
 jsr EnterRoom
 rts
Recalculate:
 lda level
 asl
 asl
 clc
 adc #116
 sta maxhp
 lda #80
 sta maxmp
 lda accessory
 cmp #22
 jne @mana
 lda #100
 sta maxmp
@mana:
 ldx weapon
 lda f:item_power,x
 and #$ff
 clc
 adc level
 sta damage
 lda accessory
 cmp #21
 jne @reach
 lda damage
 lsr
 lsr
 lsr
 clc
 adc damage
 sta damage
@reach:
 ldx weapon
 lda f:sword_reach,x
 and #$ff
 sta reach
 lda hp
 cmp maxhp
 jcc @mp
 lda maxhp
 sta hp
@mp:
 lda mp
 cmp maxmp
 jcc @done
 lda maxmp
 sta mp
@done:rts
EnterRoom:
 jsr Blank
 stz vx
 stz xsub
 stz ysub
 stz coyote
 stz jumpbuffer
 stz walkphase
 stz hero_frame
 lda #1
 sta grounded
 lda #0
 sta form
 sta vy
 sta jumps
 sta attack
 sta attackcd
 sta magiccd
 sta dash
 sta slow
 sta orbit
 sta shotlife
 sta bulletlife
 sta bosshp
 sta bosshit
 lda #90
 sta inv
 lda #80
 sta px
 lda #152
 sta py
 ldx room
 lda f:room_region,x
 and #$ff
 sta region
 cmp oldregion
 jeq @same
 jsr LoadRegion
@same:
 lda room
 asl
 tax
 lda #1
 sta visited,x
 ldx room
 lda f:room_boss,x
 and #$ff
 sta boss
 cmp #255
 jeq @normal
 asl
 tax
 lda defeated,x
 jne @normal
 lda boss
 asl
 tax
 lda f:boss_hp,x
 sta bosshp
 sta bossmax
 lda #184
 sta bossx
 lda #90
 sta bosstimer
 lda #0
 sta bosscycle
 sta bossphase
 lda room
 sta checkpoint
 lda maxhp
 sta hp
 lda maxmp
 sta mp
@normal:
 jsr SpawnEnemies
 jsr RoomMap
 jsr RoomMusic
 jsr DrawGame
 jsr Unblank
 rts
SpawnEnemies:
 ldx #0
 lda #0
@clear: sta enemyhp,x
 inx
 inx
 cpx #8
 jne @clear
 lda bosshp
 jne @done
 ldx room
 lda f:room_type,x
 and #1
 jne @done
 lda room
 and #3
 inc
 cmp #4
 jcc @count
 lda #3
@count:
 sta t0
 ldx #0
@spawn:
 txa
 asl
 asl
 asl
 asl
 clc
 adc #100
 sta enemyx,x
 lda #152
 sta enemyy,x
 lda region
 asl
 clc
 adc #24
 sta enemyhp,x
 lda #50
 sta enemycool,x
 txa
 lsr
 clc
 adc room
 and #3
 sta enemykind,x
 inx
 inx
 dec t0
 jne @spawn
@done:rts
RoomMap:
 jsr BaseMap
 ; Keep HUD and bottom line legible.
 ldx #0
 lda #0
@hud: sta MAP,x
 inx
 inx
 cpx #256
 jne @hud
 ldx #(25*64)
@foot: sta MAP,x
 inx
 inx
 cpx #(28*64)
 jne @foot
 ; The walking surface is tile row23, pixel184.
 ldx #(23*64)
 lda #96
@floor: sta MAP,x
 inx
 inx
 cpx #(24*64)
 jne @floor
 ; Elevated one-way platforms, two designs alternate by room.
 lda room
 and #1
 jeq @platformA
 ldx #(17*64+8*2)
 jmp @platform
@platformA: ldx #(17*64+6*2)
@platform:
 lda #97
 ldy #7
@pl: sta MAP,x
 inx
 inx
 dey
 jne @pl
 ldx #(13*64+21*2)
 ldy #7
@pl2: sta MAP,x
 inx
 inx
 dey
 jne @pl2
 ; Doors are ground-floor alcoves at x24,88,152,216.
 lda #0
 sta exitidx
@door:
 lda room
 asl
 asl
 clc
 adc exitidx
 tax
 lda f:room_exit_to,x
 and #$ff
 cmp #255
 jeq @next
 lda f:room_exit_secret,x
 and #$ff
 jeq @visible
 lda room
 asl
 tax
 ldy exitidx
 lda secrets,x
 and BitMasks,y ; index needs word offset, fixed in helper below
 ; Explicit bit test.
 lda exitidx
 asl
 tay
 lda secrets,x
 and BitMasks,y
 jne @visible
 lda #168
 jmp @tile
@visible:
 lda #128
@tile:
 ora #$2000
 sta t0
 lda exitidx
 asl
 asl
 asl
 asl
 clc
 adc #(18*64+1*2)
 sta t1
 lda #5
 sta t2
@doorrow:
 ldx t1
 ldy #4
@doorcol:
 lda t0
 sta MAP,x
 inc t0
 inx
 inx
 dey
 jne @doorcol
 lda t1
 clc
 adc #64
 sta t1
 dec t2
 jne @doorrow
@next:
 inc exitidx
 lda exitidx
 cmp #4
 jne @door
 ldx room
 lda f:room_type,x
 and #1
 jeq @notshrine
 lda #$20bc
 sta t0
 lda #(20*64+13*2)
 sta t1
 ldy #3
@altarrow:
 ldx t1
 lda t0
 sta MAP,x
 inc a
 sta MAP+2,x
 inc a
 sta MAP+4,x
 inc a
 sta t0
 lda t1
 clc
 adc #64
 sta t1
 dey
 jne @altarrow
@notshrine:
 lda #$2000
 sta textcolor
 lda #(3*64+2)
 sta textpos
 lda room
 jsr NameRoom
 TEXT Footer1,27,1
 rts
GameTick:
 lda pressed
 and #JOY_START
 jeq @play
 lda #2
 sta mode
 lda weapon
 sta menuitem
 lda #0
 sta menupage
 jsr MenuScreen
 rts
@play:
 jsr TickTimers
 jsr Recalculate
 lda pressed
 and #JOY_R
 jeq @form
 jsr CycleWeapon
@form:
 lda pressed
 and #JOY_SELECT
 jeq @heal
 jsr CycleForm
@heal:
 lda pressed
 and #JOY_X
 jeq @move
 jsr UsePotion
@move:
 jsr MovePlayer
 lda pressed
 and #JOY_UP
 jeq @combat
 jsr Interact
 lda mode
 cmp #1
 jne @done
@combat:
 lda pad
 and #JOY_Y
 jeq @magic
 jsr SwordAttack
@magic:
 lda pressed
 and #JOY_A
 jeq @enemy
 jsr CastSpell
@enemy:
 jsr UpdateEnemies
 jsr UpdateBoss
 jsr UpdateProjectiles
 jsr CollectItems
 lda hp
 jne @done
 jsr PlayerDied
@done:rts
TickTimers:
 ldx #inv
@timer:
 ; Timers are intentionally updated explicitly, never across non-timer fields.
 lda inv
 jeq :+
 dec inv
: lda attack
 jeq :+
 dec attack
: lda attackcd
 jeq :+
 dec attackcd
: lda magiccd
 jeq :+
 dec magiccd
: lda dash
 jeq :+
 dec dash
: lda dashcd
 jeq :+
 dec dashcd
: lda slow
 jeq :+
 dec slow
: lda orbit
 jeq :+
 dec orbit
: lda bosshit
 jeq :+
 dec bosshit
: lda message
 jeq :+
 dec message
: lda frame
 and #63
 jne @done
 inc playseconds
 lda form
 jeq @regen
 lda mp
 jeq @human
 sec
 sbc #3
 jpl @mp
 lda #0
@mp: sta mp
 jne @done
@human:
 stz form
 jmp @done
@regen:
 lda mp
 cmp maxmp
 jcs @hp
 inc mp
@hp:
 lda armor
 cmp #19
 jne @done
 lda hp
 cmp maxhp
 jcs @done
 inc hp
@done:rts
.include "movement.s"
CycleWeapon:
 ldx #12
@next:
 inc weapon
 lda weapon
 cmp #12
 jcc :+
 stz weapon
: lda weapon
 asl
 tay
 lda inventory,y
 jne @found
 dex
 jne @next
@found:
 lda weapon
 sta messageitem
 lda #1
 sta messageid
 lda #120
 sta message
 jsr Recalculate
 rts
CycleForm:
 lda #0
 sta t0
@next:
 inc form
 lda form
 cmp #4
 jcc :+
 stz form
: lda form
 jeq @found
 cmp #1
 jne @bat
 lda inventory+64
 jne @found
 jmp @next
@bat:
 cmp #2
 jne @mist
 lda inventory+68
 jne @found
 jmp @next
@mist:
 lda inventory+70
 jne @found
 jmp @next
@found:
 lda #6
 jsr SFX
 rts

.include "combat.s"
.include "render.s"
.include "menu_save.s"
.include "audio.s"
.include "rom_data.s"
