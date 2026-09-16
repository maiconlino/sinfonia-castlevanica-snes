; R3 screen-edge navigation. All 140 original directed connections are retained.
; Main story uses floor-level left/right. Detours occupy left/right upper ledges.
.a16
.i16
ResolveEdge:
 lda room
 asl
 asl
 clc
 adc edgeslot
 tax
 lda f:edge_exit_index,x
 and #$ff
 cmp #255
 jeq @none
 sta exitidx
 lda room
 asl
 asl
 clc
 adc exitidx
 sta edgechosen
 sec
 rts
@none:clc
 rts
ChooseEdgeAtPlayer:
 stz edgeslot
 lda px
 cmp #120
 jcc :+
 inc edgeslot
: lda py
 cmp #124
 jcs @resolve
 inc edgeslot
 inc edgeslot
 jsr ResolveEdge
 jcs @done
 dec edgeslot
 dec edgeslot
@resolve:jsr ResolveEdge
@done:rts
CheckEdgeRequirements:
 ldx edgechosen
 lda f:room_exit_secret,x
 and #$ff
 jeq @requirements
 lda room
 asl
 tax
 lda exitidx
 asl
 tay
 lda secrets,x
 and BitMasks,y
 jeq @no
@requirements:
 ldx edgechosen
 lda f:room_exit_req0,x
 jsr TestRequirement
 jcc @no
 ldx edgechosen
 lda f:room_exit_req1,x
 jsr TestRequirement
 jcc @no
 ldx edgechosen
 lda f:room_exit_req2,x
 jsr TestRequirement
 jcc @no
 ldx edgechosen
 lda f:room_exit_req3,x
 jsr TestRequirement
 rts
@no:clc
 rts
CheckScreenEdges:
 lda edgecool
 jne @done
 lda px
 cmp #2
 jcc @left
 cmp #239
 jcc @done
 lda pad
 and #JOY_RIGHT
 jeq @done
 jmp @try
@left:
 lda pad
 and #JOY_LEFT
 jeq @done
@try:
 lda bosshp
 jne @bossblocked
 jsr ChooseEdgeAtPlayer
 jcc @done
 jsr CheckEdgeRequirements
 jcc @locked
 lda room
 sta edgefrom
 sta lastroom
 lda form
 sta arrivalform
 lda vx
 sta arrivalvx
 ldx edgechosen
 lda f:room_exit_to,x
 and #$ff
 sta room
 lda #1
 sta edgearrival
 jsr EnterRoom
 rts
@locked:
 lda #2
 sta messageid
 lda #65
 sta message
 lda #20
 sta edgecool
 rts
@bossblocked:
 lda #5
 sta messageid
 lda #60
 sta message
 lda #20
 sta edgecool
@done:rts
RevealEdgeSecret:
 lda px
 cmp #34
 jcc @try
 cmp #206
 jcc @done
@try:
 jsr ChooseEdgeAtPlayer
 jcc @done
 ldx edgechosen
 lda f:room_exit_secret,x
 and #$ff
 jeq @done
 lda room
 asl
 tax
 lda exitidx
 asl
 tay
 lda secrets,x
 and BitMasks,y
 jne @done
 lda secrets,x
 ora BitMasks,y
 sta secrets,x
 jsr RoomMap
 lda #3
 sta messageid
 lda #120
 sta message
@done:rts
LandEdgeLedges:
 lda form
 cmp #2
 jcs @done
 lda vy
 jmi @done
 lda prevy
 cmp #105
 jcs @done
 lda py
 cmp #104
 jcc @done
 lda #2
 sta edgeslot
 lda px
 cmp #48
 jcc @check
 cmp #196
 jcc @done
 inc edgeslot
@check:
 jsr ResolveEdge
 jcc @done
 lda #104
 sta py
 jsr LandPlayer
@done:rts
DrawEdgePassages:
 stz edgeslot
@each:
 jsr ResolveEdge
 jcc @next
 ; The central old door panels no longer exist. Draw one arch at the edge.
 lda #128
 sta t0
 ldx edgechosen
 lda f:room_exit_secret,x
 and #$ff
 jeq @position
 lda room
 asl
 tax
 lda exitidx
 asl
 tay
 lda secrets,x
 and BitMasks,y
 jne @position
 lda #168
 sta t0
@position:
 lda #18*64
 sta t1
 lda edgeslot
 cmp #2
 jcc :+
 lda #12*64
 sta t1
: lda edgeslot
 and #1
 jeq :+
 lda t1
 clc
 adc #28*2
 sta t1
: lda #5
 sta t2
@row:
 ldx t1
 ldy #4
@col:
 lda t0
 ora #$2000
 sta MAP,x
 inc t0
 inx
 inx
 dey
 jne @col
 lda t1
 clc
 adc #64
 sta t1
 dec t2
 jne @row
 lda edgeslot
 cmp #2
 jcc @next
 ldx #17*64
 lda edgeslot
 and #1
 jeq :+
 ldx #17*64+25*2
: ldy #7
 lda #97
@ledge:
 sta MAP,x
 inx
 inx
 dey
 jne @ledge
@next:
 inc edgeslot
 lda edgeslot
 cmp #4
 jcc @each
 rts

ApplyEdgeArrival:
 lda edgearrival
 jne :+
 rts
: lda arrivalform
 sta form
 stz edgeslot
@reciprocal:
 jsr ResolveEdge
 jcc @next
 ldx edgechosen
 lda f:room_exit_to,x
 and #$ff
 cmp edgefrom
 jeq @arrival
@next:
 inc edgeslot
 lda edgeslot
 cmp #4
 jcc @reciprocal
 stz edgeslot
@arrival:
 lda edgeslot
 and #1
 jne @arrive_right
 lda #14
 sta px
 lda #$0280
 sta vx
 stz face
 jmp @height
@arrive_right:
 lda #226
 sta px
 lda #$fd80
 sta vx
 lda #1
 sta face
@height:
 lda #152
 sta py
 lda edgeslot
 cmp #2
 jcc :+
 lda #104
 sta py
: lda #18
 sta edgecool
 lda #1
 sta grounded
 stz edgearrival
 rts

