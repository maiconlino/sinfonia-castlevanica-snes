; Revision 2: fixed-point movement and native streaming metasprites.
; Positions in STATE remain integral for SRAM schema 1 compatibility.
.a16
.i16
ResetMotion:
 stz vx
 stz xfrac
 stz yfrac
 stz jumpbuffer
 stz animtick
 lda #6
 sta coyote
 stz heropose
 lda #$ffff
 sta heroloaded
 rts

MovePlayer:
 lda py
 sta prevy
 lda coyote
 jeq :+
 dec coyote
: lda jumpbuffer
 jeq :+
 dec jumpbuffer
: lda pressed
 and #JOY_B
 jeq :+
 lda #6
 sta jumpbuffer
: lda #$240
 sta t0
 lda form
 cmp #1
 jne :+
 lda #$340
 sta t0
: lda accessory
 cmp #28
 jne :+
 lda t0
 clc
 adc #$40
 sta t0
: lda armor
 cmp #13
 jne :+
 lda t0
 clc
 adc #$20
 sta t0
: lda pressed
 and #JOY_L
 jeq @directions
 lda dashcd
 jne @directions
 lda #12
 sta dash
 lda #45
 sta dashcd
 lda #18
 sta inv
@directions:
 lda dash
 jeq @input
 lda #$5c0
 sta vx
 lda face
 jeq @integrateX
 lda #$fa40
 sta vx
 jmp @integrateX
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
 jeq @integrateX
 jmi @brakeNegative
 cmp #$c0
 jcc @stop
 sec
 sbc #$c0
 sta vx
 jmp @integrateX
@brakeNegative:
 clc
 adc #$c0
 jpl @stop
 sta vx
 jmp @integrateX
@stop:
 stz vx
 stz xfrac
 jmp @integrateX
@left:
 lda #1
 sta face
 lda vx
 jmi :+
 stz vx
: lda vx
 sec
 sbc #$80
 sta vx
 jsr Abs
 cmp t0
 jcc @integrateX
 lda t0
 eor #$ffff
 inc
 sta vx
 jmp @integrateX
@right:
 stz face
 lda vx
 jpl :+
 stz vx
: lda vx
 clc
 adc #$80
 cmp t0
 jcc :+
 lda t0
: sta vx
@integrateX:
 lda vx
 jeq @jump
 inc animtick
 clc
 adc xfrac
 sta t2
 and #$ff
 sta xfrac
 lda t2
 xba
 and #$ff
 cmp #$80
 jcc :+
 ora #$ff00
: clc
 adc px
 cmp #8
 jcs :+
 lda #8
 stz vx
 stz xfrac
: cmp #232
 jcc :+
 lda #232
 stz vx
 stz xfrac
: sta px
@jump:
 lda form
 cmp #2
 jcs @fly
 lda jumpbuffer
 jeq @gravity
 lda coyote
 jne @beginJump
 lda inventory+62
 jeq @gravity
 lda jumps
 cmp #2
 jcs @gravity
 cmp #1
 jcs @beginJump
 inc jumps
@beginJump:
 inc jumps
 stz coyote
 stz jumpbuffer
 stz yfrac
 lda #$f900 ; -7.0 pixels/frame, integrated at 60 Hz
 sta vy
 lda #2
 jsr SFX
@gravity:
 ; Releasing B clips ascent. Holding it reaches higher ledges.
 lda pad
 and #JOY_B
 jne @accelerate
 lda vy
 jpl @accelerate
 cmp #$fd00
 jcs @accelerate
 lda #$fd00
 sta vy
@accelerate:
 lda vy
 clc
 adc #$40
 jmi :+
 cmp #$700
 jcc :+
 lda #$700
: sta vy
 jmp @integrateY
@fly:
 stz coyote
 lda #$80
 sta vy
 lda pad
 and #JOY_DOWN
 jeq :+
 lda #$200
 sta vy
: lda pad
 and #(JOY_UP|JOY_B)
 jeq @integrateY
 lda #$fe00
 sta vy
@integrateY:
 lda yfrac
 clc
 adc vy
 sta t2
 and #$ff
 sta yfrac
 lda t2
 xba
 and #$ff
 cmp #$80
 jcc :+
 ora #$ff00
: clc
 adc py
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
 jsr Landed
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
 jsr Landed
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
 jsr Landed
@done:
 rts
Landed:
 stz vy
 stz yfrac
 stz jumps
 lda #6
 sta coyote
 rts

UpdateHeroPose:
 lda dash
 jeq @attack
 lda #15
 jmp @set
@attack:
 lda attack
 jeq @air
 cmp #7
 jcs @windup
 cmp #4
 jcs @swing
 lda #12
 jmp @set
@windup:
 lda #10
 jmp @set
@swing:
 lda #11
 jmp @set
@air:
 lda coyote
 jne @walk
 lda vy
 jmi @up
 lda #14
 jmp @set
@up:
 lda #13
 jmp @set
@walk:
 lda vx
 jeq @idle
 lda animtick
 lsr
 lsr
 and #7
 clc
 adc #2
 jmp @set
@idle:
 lda frame
 lsr
 lsr
 lsr
 lsr
 lsr
 and #1
@set:
 sta heropose
 rts

DrawHuman:
 jsr UpdateHeroPose
 stz ssize
 lda #$30
 sta sattr
 lda inv
 jeq :+
 lda frame
 and #4
 jeq :+
 lda #$32
 sta sattr
: lda face
 jeq :+
 lda sattr
 ora #$40
 sta sattr
: stz heropiece
@piece:
 lda heropiece
 asl
 tax
 lda f:HeroTileOffsets,x
 sta stile
 lda f:HeroYOffsets,x
 clc
 adc py
 sec
 sbc #16
 sta sy
 lda heropiece
 and #1
 eor face
 asl
 asl
 asl
 asl
 clc
 adc px
 sec
 sbc #8
 sta sx
 jsr AddSprite
 inc heropiece
 lda heropiece
 cmp #6
 jne @piece
 rts

; Only changed poses are uploaded, six 128-byte strips into a 16-tile stride.
; This preserves all neighbouring OBJ tiles and respects the native layout.
UploadHero:
 lda heropose
 cmp heroloaded
 jeq @done
 sta heroloaded
 sta t2
 asl
 clc
 adc t2
 xba
 clc
 adc #.loword(HeroFrames)
 sta src
 lda #.bankbyte(HeroFrames)
 sta src+2
 lda #128
 sta t0
 lda #$4000
 sta t1
 lda #6
 sta herorows
@row:
 jsr DMAVRAM
 lda src
 clc
 adc #128
 sta src
 lda t1
 clc
 adc #256
 sta t1
 dec herorows
 jne @row
@done:
 rts

LoadFarBackground:
 lda region
 and #3
 xba
 asl
 asl
 asl
 asl
 asl
 clc
 adc #$8000
 sta src
 lda region
 lsr
 lsr
 clc
 adc #14
 sta src+2
 lda #8192
 sta t0
 lda #$7000
 sta t1
 jsr DMAVRAM
 lda region
 xba
 asl
 asl
 asl
 clc
 adc #.loword(FarMaps)
 sta src
 lda #.bankbyte(FarMaps)
 sta src+2
 lda #2048
 sta t0
 lda #$6400
 sta t1
 jsr DMAVRAM
 rts

; Draw one 24-pixel-wide metatile, starting at tile t0, height t3.
; X is the upper-left map buffer byte offset. Uses t2 and t4.
DrawFixture:
@row:
 lda #3
 sta t2
@col:
 lda t0
 ora #$2800
 sta MAP,x
 inc t0
 inx
 inx
 dec t2
 jne @col
 txa
 clc
 adc #58
 tax
 dec t3
 jne @row
 rts

PrintNumber3:
 cmp #1000
 jcc :+
 lda #999
: sta t0
 lda #2
 sta t1
@digit:
 ldy t1
 lda Decimal,y
 sta t2
 stz t3
@sub:
 lda t0
 cmp t2
 jcc @put
 sec
 sbc t2
 sta t0
 inc t3
 jmp @sub
@put:
 lda t3
 clc
 adc #('0'-32)
 ora #$2c00
 ldx textpos
 sta MAP,x
 inc textpos
 inc textpos
 inc t1
 inc t1
 lda t1
 cmp #8
 jcc @digit
 rts

HeroTileOffsets: .word 0,2,32,34,64,66
HeroYOffsets: .word 0,0,16,16,32,32
AnimalTiles: .word 4,8,12,68,72,76

; A gated route has a single shut door until its items have been obtained.
; This read-only draw helper does not mutate messages, secrets, or inventory.
DoorArtTile:
 lda bosshp
 jne @closed
 lda room
 asl
 asl
 clc
 adc exitidx
 tax
 lda f:room_exit_req0,x
 jsr ArtRequirement
 jcc @closed
 lda f:room_exit_req1,x
 jsr ArtRequirement
 jcc @closed
 lda f:room_exit_req2,x
 jsr ArtRequirement
 jcc @closed
 lda f:room_exit_req3,x
 jsr ArtRequirement
 jcc @closed
 lda #128
 rts
@closed:
 lda #143
 rts
ArtRequirement:
 and #$ff
 cmp #255
 jeq @yes
 asl
 tay
 lda inventory,y
 jeq @no
@yes:
 sec
 rts
@no:
 clc
 rts
PrintNumber2:
 cmp #100
 jcc :+
 lda #99
: stz t0
@tens:
 cmp #10
 jcc @units
 sec
 sbc #10
 inc t0
 jmp @tens
@units:
 pha
 lda t0
 clc
 adc #('0'-32)
 ora #$2c00
 ldx textpos
 sta MAP,x
 pla
 clc
 adc #('0'-32)
 ora #$2c00
 sta MAP+2,x
 rts
