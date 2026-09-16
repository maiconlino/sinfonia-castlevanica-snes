.a16
.i16
; Physical room graph. No normal exit needs UP or an interior door.
CheckEdgeExit:
 lda edgecool
 jne @done
 lda bosshp
 jne @done
 lda px
 cmp #9
 jcc @left
 cmp #232
 jcc @done
 lda pad
 and #JOY_RIGHT
 jeq @done
 lda #1
 jmp @side
@left:
 lda pad
 and #JOY_LEFT
 jeq @done
 lda #0
@side:
 sta t2
 stz exitidx
@scan:
 lda room
 asl
 asl
 clc
 adc exitidx
 tax
 lda f:exit_side_r3,x
 and #255
 cmp t2
 jne @next
 lda f:exit_y_r3,x
 and #255
 sec
 sbc py
 jsr Abs
 cmp #20
 jcs @next
 lda f:room_exit_secret,x
 and #255
 jeq @gate
 lda room
 asl
 tax
 lda exitidx
 asl
 tay
 lda secrets,x
 and BitMasks,y
 jeq @done
@gate:
 lda room
 asl
 asl
 clc
 adc exitidx
 sta t4
 tax
 lda f:room_exit_req0,x
 jsr TestRequirement
 jcc @locked
 ldx t4
 lda f:room_exit_req1,x
 jsr TestRequirement
 jcc @locked
 ldx t4
 lda f:room_exit_req2,x
 jsr TestRequirement
 jcc @locked
 ldx t4
 lda f:room_exit_req3,x
 jsr TestRequirement
 jcc @locked
 lda vx
 sta carryvx
 lda form
 sta carryform
 ldx t4
 lda f:exit_dest_side_r3,x
 and #255
 sta entryside
 lda f:exit_dest_y_r3,x
 and #255
 sta entryheight
 lda #1
 sta edge_active
 lda room
 sta lastroom
 lda f:room_exit_to,x
 and #255
 sta room
 jsr EnterRoom
 stz edge_active
 lda #12
 sta edgecool
 lda #1
 sta enterededge
 rts
@locked:
 lda #2
 sta messageid
 lda #120
 sta message
 rts
@next:
 inc exitidx
 lda exitidx
 cmp #4
 jcc @scan
@done:rts
ApplyEdgeSpawn:
 lda entryside
 jeq @fromleft
 lda #220
 jmp @pos
@fromleft:
 lda #20
@pos:
 sta px
 lda entryheight
 sta py
 sta prevy
 lda carryvx
 sta vx
 lda carryform
 sta form
 lda #1
 sta grounded
 rts
DrawEdgeExits:
 stz exitidx
@each:
 lda room
 asl
 asl
 clc
 adc exitidx
 tax
 lda f:exit_side_r3,x
 and #255
 cmp #255
 jeq @next
 sta t2
 lda f:exit_y_r3,x
 and #255
 sec
 sbc #32
 lsr
 lsr
 lsr
 asl
 asl
 asl
 asl
 asl
 asl
 sta t1
 lda t2
 jeq :+
 lda t1
 clc
 adc #60
 sta t1
: lda #0
 sta t0
 lda f:room_exit_secret,x
 and #255
 jeq @opening
 lda room
 asl
 tax
 lda exitidx
 asl
 tay
 lda secrets,x
 and BitMasks,y
 jne @opening
 lda #126
 sta t0
@opening:
 lda #8
 sta t3
@row:
 ldx t1
 lda t0
 sta MAP,x
 sta MAP+2,x
 lda t1
 clc
 adc #64
 sta t1
 dec t3
 jne @row
 ; The sill leads directly into the adjoining room.
 ldx t1
 lda #97
 sta MAP,x
 sta MAP+2,x
@next:
 inc exitidx
 lda exitidx
 cmp #4
 jcc @each
 rts
RevealEdgeSecret:
 stz exitidx
@scan:
 lda room
 asl
 asl
 clc
 adc exitidx
 tax
 lda f:room_exit_secret,x
 and #255
 jeq @next
 lda f:exit_y_r3,x
 and #255
 sec
 sbc py
 jsr Abs
 cmp #26
 jcs @next
 lda f:exit_side_r3,x
 and #255
 jeq @left
 lda px
 cmp #202
 jcc @next
 lda face
 jne @next
 jmp @reveal
@left:
 lda px
 cmp #42
 jcs @next
 lda face
 jeq @next
@reveal:
 lda room
 asl
 tax
 lda exitidx
 asl
 tay
 lda secrets,x
 and BitMasks,y
 jne @next
 lda secrets,x
 ora BitMasks,y
 sta secrets,x
 jsr RoomMap
 lda #3
 sta messageid
 lda #120
 sta message
 rts
@next:
 inc exitidx
 lda exitidx
 cmp #4
 jcc @scan
 rts
