; Responsive movement, 8.8 fixed-point velocity and fractional accumulation.
; px/py and saved-state layout remain unchanged for SRAM compatibility.
MovePlayer:
 lda py
 sta prevy
 inc animtick
 lda grounded
 jeq @air
 lda #6
 sta coyote
 jmp @buffer
@air:
 lda coyote
 jeq @buffer
 dec coyote
@buffer:
 lda jumpbuf
 jeq :+
 dec jumpbuf
: lda pressed
 and #JOY_B
 jeq @speed
 lda #6
 sta jumpbuf
@speed:
 lda #$0240
 sta t0
 lda form
 cmp #1
 jne :+
 lda #$0340
 sta t0
: lda accessory
 cmp #28
 jne :+
 lda t0
 clc
 adc #$0040
 sta t0
: lda armor
 cmp #13
 jne @dash
 lda t0
 clc
 adc #$0020
 sta t0
@dash:
 lda pressed
 and #JOY_L
 jeq @move
 lda dashcd
 jne @move
 lda #12
 sta dash
 lda #45
 sta dashcd
 lda #18
 sta inv
@move:
 lda dash
 jeq @input
 lda #$0540
 ldx face
 jeq @setvx
 eor #$ffff
 inc
 jmp @setvx
@input:
 lda pad
 and #(JOY_LEFT|JOY_RIGHT)
 cmp #(JOY_LEFT|JOY_RIGHT)
 jeq @brake
 cmp #JOY_LEFT
 jeq @left
 cmp #JOY_RIGHT
 jeq @right
@brake:
 lda vx
 jeq @integratex
 jmi @brakeleft
 sec
 sbc #$0080
 jpl @setvx
 lda #0
 jmp @setvx
@brakeleft:
 clc
 adc #$0080
 jmi @setvx
 lda #0
 jmp @setvx
@left:
 lda #1
 sta face
 lda t0
 eor #$ffff
 inc
 sta t1
 lda vx
 sec
 sbc #$0060
 jpl @setvx
 cmp t1
 jcs @setvx
 lda t1
 jmp @setvx
@right:
 stz face
 lda vx
 clc
 adc #$0060
 jmi @setvx
 cmp t0
 jcc @setvx
 lda t0
@setvx:
 sta vx
@integratex:
 lda px
 xba
 ora xfrac
 clc
 adc vx
 pha
 and #$00ff
 sta xfrac
 pla
 xba
 and #$00ff
 cmp #8
 jcs :+
 lda #8
 stz xfrac
 stz vx
: cmp #232
 jcc :+
 lda #232
 stz xfrac
 stz vx
: sta px
 lda form
 cmp #2
 jcs @fly
 lda jumpbuf
 jeq @gravity
 lda coyote
 jne @groundjump
 lda inventory+62
 jeq @gravity
 lda jumps
 cmp #2
 jcs @gravity
 lda #2
 sta jumps
 jmp @jump
@groundjump:
 lda #1
 sta jumps
@jump:
 stz grounded
 stz coyote
 stz jumpbuf
 stz yfrac
 lda #$f9c0
 sta vy
 lda #2
 jsr SFX
@gravity:
 ; Releasing B cuts upward speed, permitting short and full-height jumps.
 lda pad
 and #JOY_B
 jne @acceleratey
 lda vy
 jpl @acceleratey
 cmp #$fd80
 jcs @acceleratey
 lda #$fd80
 sta vy
@acceleratey:
 lda vy
 clc
 adc #$0058
 jmi @setvy
 cmp #$0700
 jcc @setvy
 lda #$0700
@setvy:
 sta vy
 jmp @integratey
@fly:
 stz jumps
 stz jumpbuf
 lda #$0080
 sta vy
 lda pad
 and #JOY_DOWN
 jeq :+
 lda #$0200
 sta vy
: lda pad
 and #(JOY_B|JOY_UP)
 jeq @integratey
 lda #$fe80
 sta vy
@integratey:
 stz grounded
 lda py
 xba
 ora yfrac
 clc
 adc vy
 pha
 and #$00ff
 sta yfrac
 pla
 xba
 and #$00ff
 cmp #40
 jcs :+
 lda #40
 stz vy
 stz yfrac
: sta py
 cmp #152
 jcc @platforms
 lda #152
 sta py
 jsr LandPlayer
@platforms:
 lda form
 cmp #2
 jcs @done
 lda vy
 jmi @done
 lda prevy
 cmp #105
 jcs @upper
 lda py
 cmp #104
 jcc @upper
 lda room
 and #1
 jeq :+
 lda #64
 jmp :++
: lda #48
: sta t0
 lda px
 clc
 adc #12
 cmp t0
 jcc @upper
 lda t0
 clc
 adc #56
 cmp px
 jcc @upper
 lda #104
 sta py
 jsr LandPlayer
@upper:
 lda prevy
 cmp #73
 jcs @done
 lda py
 cmp #72
 jcc @done
 lda px
 cmp #224
 jcs @done
 cmp #156
 jcc @done
 lda #72
 sta py
 jsr LandPlayer
@done:
 rts
LandPlayer:
 stz vy
 stz yfrac
 stz jumps
 lda #1
 sta grounded
 rts
