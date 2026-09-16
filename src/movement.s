; Responsive 8.8 fixed-point physics. SRAM continues to store integer coordinates.
; The fractional accumulators live outside the persistent state layout.
.a16
.i16
MovePlayer:
 lda py
 sta prevy
 lda grounded
 jeq @coyote
 lda #6
 sta coyote
 jmp @buffer
@coyote:
 lda coyote
 jeq @buffer
 dec coyote
@buffer:
 lda jumpbuffer
 jeq :+
 dec jumpbuffer
: lda pressed
 and #JOY_B
 jeq @speed
 lda #6
 sta jumpbuffer
@speed:
 lda #$0280
 sta t0
 lda form
 cmp #1
 jne :+
 lda #$0300
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
 jeq @motion
 lda dashcd
 jne @motion
 lda #12
 sta dash
 lda #45
 sta dashcd
 lda #18
 sta inv
@motion:
 lda dash
 jeq @directions
 lda #$0500
 sta vx
 lda face
 jeq @integrate_x
 lda #$fb00
 sta vx
 jmp @integrate_x
@directions:
 lda pad
 and #(JOY_LEFT|JOY_RIGHT)
 cmp #(JOY_LEFT|JOY_RIGHT)
 jeq @friction
 cmp #JOY_LEFT
 jeq @left
 cmp #JOY_RIGHT
 jeq @right
@friction:
 lda vx
 jeq @integrate_x
 jmi @friction_left
 sec
 sbc #$00c0
 jpl :+
 lda #0
: sta vx
 jmp @integrate_x
@friction_left:
 clc
 adc #$00c0
 jmi :+
 lda #0
: sta vx
 jmp @integrate_x
@left:
 lda #1
 sta face
 lda t0
 eor #$ffff
 inc a
 sta t1
 lda vx
 sec
 sbc #$00c0
 cmp t1
 jpl :+
 lda t1
: sta vx
 jmp @integrate_x
@right:
 stz face
 lda vx
 clc
 adc #$00c0
 cmp t0
 jmi :+
 lda t0
: sta vx
@integrate_x:
 lda px
 xba
 and #$ff00
 ora xsub
 clc
 adc vx
 ; Signed carry-safe boundary clamping; never wraps left to the right side.
 sta t2
 lda vx
 jpl @positive_x
 lda t2
 cmp #$f800
 jcc @clamp_right
 lda #0
 sta t2
 stz vx
 jmp @store_x
@positive_x:
 lda t2
@clamp_right:
 cmp #$f000
 jcc @store_x
 lda #$f000
 sta t2
 stz vx
@store_x:
 lda t2
 pha
 and #$00ff
 sta xsub
 pla
 xba
 and #$00ff
 sta px
 lda vx
 jsr Abs
 clc
 adc walkphase
 sta walkphase
@jump:
 lda form
 cmp #2
 jcs @fly
 lda jumpbuffer
 jeq @release
 lda grounded
 ora coyote
 jne @groundjump
 lda inventory+62
 jeq @release
 lda jumps
 cmp #2
 jcs @release
 inc jumps
 jmp @launch
@groundjump:
 lda #1
 sta jumps
@launch:
 stz coyote
 stz grounded
 stz jumpbuffer
 stz ysub
 lda #$f9c0
 sta vy
 lda #2
 jsr SFX
@release:
 lda pad
 and #JOY_B
 jne @gravity
 lda vy
 jpl @gravity
 cmp #$fdc0
 jcs @gravity
 lda #$fdc0
 sta vy
@gravity:
 lda vy
 clc
 adc #$0040
 cmp #$0700
 jmi :+
 lda #$0700
: sta vy
 jmp @integrate_y
@fly:
 stz jumpbuffer
 lda #$0080
 sta vy
 lda pad
 and #JOY_DOWN
 jeq :+
 lda #$0200
 sta vy
: lda pad
 and #(JOY_B|JOY_UP)
 jeq @integrate_y
 lda #$fe00
 sta vy
@integrate_y:
 stz grounded
 lda py
 xba
 and #$ff00
 ora ysub
 clc
 adc vy
 cmp #$2800
 jcs :+
 lda #$2800
 stz vy
: pha
 and #$00ff
 sta ysub
 pla
 xba
 and #$00ff
 sta py
 cmp #152
 jcc @platforms
 lda #152
 sta py
 jsr LandPlayer
@platforms:
 jsr LandEdgeLedges
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
 stz ysub
 stz jumps
 lda #1
 sta grounded
 rts
