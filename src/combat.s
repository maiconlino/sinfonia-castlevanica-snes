.a16
.i16
Interact:
 lda bosshp
 jne @done
 lda py
 cmp #132
 jcc @done
 ldx room
 lda f:room_type,x
 and #1
 jeq @done
 lda px
 sec
 sbc #110
 jsr Abs
 cmp #20
 jcs @done
 jsr Rest
@done:rts
TestRequirement:
 and #$ff
 cmp #255
 jeq @yes
 sta messageitem
 asl
 tay
 lda inventory,y
 jeq @no
 lda messageitem
 cmp #32
 jne @bat
 lda form
 cmp #1
 jne @no
 jmp @yes
@bat:
 cmp #34
 jne @mist
 lda form
 cmp #2
 jne @no
 jmp @yes
@mist:
 cmp #35
 jne @yes
 lda form
 cmp #3
 jne @no
@yes:sec
 rts
@no:clc
 rts
Abs:
 jpl :+
 eor #$ffff
 inc
: rts
Rest:
 lda room
 sta checkpoint
 asl
 tax
 lda #1
 sta shrines,x
 lda maxhp
 sta hp
 lda maxmp
 sta mp
 stz auroraused
 lda inventory+88
 cmp #3
 jcs :+
 lda #3
 sta inventory+88
: jsr SaveGame
 lda #4
 sta messageid
 lda #150
 sta message
 lda #4
 jsr SFX
 rts
CollectItems:
 lda bosshp
 jne @done
 lda py
 cmp #128
 jcc @done
 stz itemidx
@loop:
 lda room
 asl
 tax
 lda itemidx
 asl
 tay
 lda looted,x
 and BitMasks,y
 jne @next
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
 jeq @next
 sta t4
 ldx itemidx
 lda f:pickup_x,x
 and #$ff
 sec
 sbc px
 sec
 sbc #8
 jsr Abs
 sta t0
 lda #16
 sta t1
 lda accessory
 cmp #23
 jne :+
 lda #40
 sta t1
: lda t0
 cmp t1
 jcs @next
 lda room
 asl
 tax
 lda itemidx
 asl
 tay
 lda looted,x
 ora BitMasks,y
 sta looted,x
 lda t4
 jsr Obtain
@next:
 inc itemidx
 lda itemidx
 cmp #3
 jcc @loop
@done:rts
Obtain:
 sta messageitem
 tax
 lda f:item_kind,x
 and #$ff
 sta t0
 txa
 asl
 tax
 lda t0
 cmp #5
 jeq @consumable
 lda #1
 sta inventory,x
 jmp @message
@consumable:
 lda inventory,x
 cmp #9
 jcs @message
 inc inventory,x
@message:
 lda #1
 sta messageid
 lda #150
 sta message
 lda #4
 jsr SFX
 rts
UsePotion:
 lda potion
 asl
 tax
 lda inventory,x
 jeq @done
 lda potion
 cmp #49
 jne @consume
 lda bosshp
 jne @done
@consume:
 dec inventory,x
 lda potion
 cmp #44
 jne @greater
 lda maxhp
 lsr
 lsr
 sta t0
 lda accessory
 cmp #20
 jne @heal
 lda t0
 lsr
 lsr
 clc
 adc t0
 sta t0
 jmp @heal
@greater:
 cmp #45
 jne @mana
 lda maxhp
 lsr
 sta t0
 jmp @heal
@mana:
 cmp #46
 jne @elixir
 lda maxmp
 lsr
 clc
 adc mp
 sta mp
 jmp @recalc
@elixir:
 cmp #47
 jne @cleanse
 lda maxhp
 sta hp
 lda maxmp
 sta mp
 jmp @recalc
@cleanse:
 cmp #48
 jne @return
 lda #180
 sta inv
 stz bulletlife
 jmp @recalc
@return:
 lda checkpoint
 sta room
 lda #$ffff
 sta lastroom
 jsr EnterRoom
 jmp @recalc
@heal:
 lda hp
 clc
 adc t0
 sta hp
@recalc:
 jsr Recalculate
 lda #4
 jsr SFX
@done:rts
SwordAttack:
 lda attackcd
 jne @done
 lda form
 cmp #3
 jeq @done
 ldx weapon
 lda f:sword_attack_frames,x
 and #$ff
 sta attackcd
 lda accessory
 cmp #24
 jne :+
 dec attackcd
 dec attackcd
 dec attackcd
: lda #10
 sta attack
 lda #1
 jsr SFX
 ; Secrets are revealed at their physical side opening, not at old door x positions.
 jsr RevealEdgeSecret
@targets:
 lda #0
 sta loopidx
@enemy:
 ldx loopidx
 lda enemyhp,x
 jeq @next
 lda enemyx,x
 sta t0
 lda enemyy,x
 sta t1
 jsr SwordRange
 jcc @next
 lda damage
 sta t2
 lda weapon
 cmp #11
 jne :+
 asl t2
: jsr HitEnemy
 ldx loopidx
 lda weapon
 cmp #2
 jeq @stun
 cmp #5
 jne @next
@stun:
 lda #90
 sta enemycool,x
@next:
 inc loopidx
 inc loopidx
 lda loopidx
 cmp #8
 jcc @enemy
 lda bosshp
 jeq @projectile
 lda bossx
 sta t0
 lda bossy
 sta t1
 jsr SwordRange
 jcc @projectile
 lda damage
 jsr HitBoss
@projectile:
 lda weapon
 cmp #3
 jeq @shot
 cmp #6
 jeq @shot
 cmp #9
 jeq @shot
 cmp #10
 jeq @shot
 cmp #11
 jeq @shot
 cmp #8
 jne @done
 ; Magnetic blade conducts damage to a second nearby foe.
 ldx #0
@chain:
 lda enemyhp,x
 jeq @chainnext
 lda enemyx,x
 sec
 sbc px
 jsr Abs
 cmp #80
 jcs @chainnext
 stx loopidx
 lda damage
 lsr
 sta t2
 jsr HitEnemy
 ldx loopidx
@chainnext:
 inx
 inx
 cpx #8
 jne @chain
 jmp @done
@shot:
 lda shotlife
 jne @done
 jsr StartShot
 lda damage
 sta shotdamage
 lda weapon
 cmp #6
 jne @done
 lda #$ffff
 sta shotdy
@done:rts
SwordRange:
 lda t1
 sec
 sbc py
 jsr Abs
 cmp #48
 jcs @no
 lda t0
 sec
 sbc px
 sta t1
 lda face
 jne @left
 lda t1
 jmi @behind
 cmp reach
 jcc @yes
 cmp #38
 jcc @yes
 jmp @no
@behind:
 cmp #$fff4
 jcs @yes
 jmp @no
@left:
 lda t1
 jmi @leftdist
 cmp #12
 jcc @yes
 jmp @no
@leftdist:
 jsr Abs
 cmp reach
 jcc @yes
@no:clc
 rts
@yes:sec
 rts
HitEnemy:
 ldx loopidx
 lda enemyhp,x
 sec
 sbc t2
 jcc @dead
 jeq @dead
 sta enemyhp,x
 lda #6
 sta enemystun,x
 rts
@dead:
 stz enemyhp,x
 inc kills
 lda gold
 clc
 adc #12
 sta gold
 lda xp
 clc
 adc #15
 sta xp
 cmp #90
 jcc @done
 sec
 sbc #90
 sta xp
 lda level
 cmp #35
 jcs @done
 inc level
 jsr Recalculate
 lda maxhp
 sta hp
@done:rts
HitBoss:
 pha
 lda bosshit
 jne @skip
 pla
 sta t2
 lda bosshp
 jeq @done
 sec
 sbc t2
 jcc @dead
 jeq @dead
 sta bosshp
 lda #9
 sta bosshit
 rts
@skip:pla
@done:rts
@dead:
 stz bosshp
 stz bulletlife
 ldx #0
@clearshots:
 stz bplife,x
 inx
 inx
 cpx #16
 jne @clearshots
 lda boss
 asl
 tax
 lda #1
 sta defeated,x
 inc level
 lda gold
 clc
 adc #150
 sta gold
 lda #0
 sta itemidx
@rewards:
 lda boss
 asl
 clc
 adc boss
 clc
 adc itemidx
 tax
 lda f:boss_rewards,x
 and #$ff
 cmp #255
 jeq @next
 jsr Obtain
@next:
 inc itemidx
 lda itemidx
 cmp #3
 jcc @rewards
 lda room
 asl
 tax
 lda #7
 sta looted,x
 jsr Recalculate
 lda maxhp
 sta hp
 lda maxmp
 sta mp
 lda #5
 jsr SFX
 lda boss
 cmp #7
 jne @save
 lda #1
 sta finished
 jsr SaveGame
 lda #3
 sta mode
 jsr EndingScreen
 rts
@save:
 jsr SaveGame
 jsr RoomMusic
 rts
CastSpell:
 lda magiccd
 jne @done
 ldx spell
 lda f:item_mana_cost,x
 and #$ff
 sta t0
 lda armor
 cmp #14
 jne :+
 lda t0
 lsr
 lsr
 sta t1
 lda t0
 sec
 sbc t1
 sta t0
: lda mp
 cmp t0
 jcc @done
 sec
 sbc t0
 sta mp
 lda #40
 sta magiccd
 lda inventory+72
 jeq :+
 lda #180
 sta slow
: lda #6
 jsr SFX
 lda spell
 cmp #43
 jne @orbit
 lda maxhp
 lsr
 lsr
 clc
 adc hp
 sta hp
 jsr Recalculate
 rts
@orbit:
 cmp #39
 jne @normal
 lda #360
 sta orbit
 rts
@normal:
 jsr StartShot
 ldx spell
 lda f:item_power,x
 and #$ff
 clc
 adc level
 clc
 adc #12
 sta shotdamage
 lda accessory
 cmp #29
 jne :+
 lda shotdamage
 clc
 adc #6
 sta shotdamage
: lda spell
 cmp #38
 jeq @done
 cmp #40
 jne :+
 lda #180
 sta slow
: cmp #42
 jne :+
 stz bulletlife
: stz loopidx
@aoe:
 ldx loopidx
 lda enemyhp,x
 jeq @aonext
 lda shotdamage
 sta t2
 jsr HitEnemy
@aonext:
 inc loopidx
 inc loopidx
 lda loopidx
 cmp #8
 jcc @aoe
 lda shotdamage
 jsr HitBoss
@done:rts
StartShot:
 lda px
 clc
 adc #8
 sta shotx
 lda py
 clc
 adc #16
 sta shoty
 lda #45
 sta shotlife
 stz shotdy
 lda #5
 sta shotdx
 lda face
 jeq @done
 lda #$fffb
 sta shotdx
@done:rts
.include "enemies_r3.s"
UpdateBoss:
 jmp UpdateBossR3
UpdateProjectiles:
 lda bulletlife
 jeq @shot
 dec bulletlife
 lda bulletx
 clc
 adc bulletdx
 sta bulletx
 cmp #250
 jcs @clear
 lda bullety
 clc
 adc bulletdy
 sta bullety
 cmp #184
 jcs @clear
 sec
 sbc py
 jsr Abs
 cmp #30
 jcs @shot
 lda bulletx
 sec
 sbc px
 sec
 sbc #8
 jsr Abs
 cmp #12
 jcs @shot
 lda region
 clc
 adc #13
 jsr HurtPlayer
@clear:stz bulletlife
@shot:
 lda shotlife
 jeq @done
 dec shotlife
 lda shotx
 clc
 adc shotdx
 sta shotx
 cmp #250
 jcs @killshot
 lda shoty
 clc
 adc shotdy
 sta shoty
 stz loopidx
@target:
 ldx loopidx
 lda enemyhp,x
 jeq @next
 lda enemyx,x
 sec
 sbc shotx
 jsr Abs
 cmp #20
 jcs @next
 lda enemyy,x
 sec
 sbc shoty
 jsr Abs
 cmp #24
 jcs @next
 lda shotdamage
 sta t2
 jsr HitEnemy
 stz shotlife
 jmp @boss
@next:
 inc loopidx
 inc loopidx
 lda loopidx
 cmp #8
 jcc @target
@boss:
 lda bosshp
 jeq @done
 lda bossx
 sec
 sbc shotx
 jsr Abs
 cmp #28
 jcs @done
 lda shoty
 sec
 sbc bossy
 jsr Abs
 cmp #52
 jcs @done
 lda shotdamage
 jsr HitBoss
 stz shotlife
@done:rts
@killshot:stz shotlife
 rts
HurtPlayer:
 sta t3
 lda inv
 jne @done
 lda form
 cmp #3
 jeq @done
 ldx armor
 lda f:item_power,x
 and #$ff
 sta t0
 lda t3
 sec
 sbc t0
 jpl :+
 lda #3
: cmp #3
 jcs :+
 lda #3
: sta t3
 lda accessory
 cmp #26
 jeq @resist
 cmp #25
 jne @hurt
@resist:
 lda t3
 lsr
 lsr
 sta t0
 lda t3
 sec
 sbc t0
 sta t3
@hurt:
 lda hp
 sec
 sbc t3
 jcc @fatal
 jeq @fatal
 sta hp
 jmp @inv
@fatal:
 lda inventory+74
 jeq @zero
 lda auroraused
 jne @zero
 inc auroraused
 lda #1
 sta hp
 jmp @inv
@zero:stz hp
@inv:
 lda #55
 sta inv
 lda armor
 cmp #18
 jne :+
 lda #90
 sta inv
: lda #3
 jsr SFX
@done:rts
PlayerDied:
 stz form
 inc deaths
 lda checkpoint
 sta room
 lda #$ffff
 sta lastroom
 jsr Recalculate
 lda maxhp
 sta hp
 lda maxmp
 sta mp
 lda inventory+88
 cmp #3
 jcs :+
 lda #3
 sta inventory+88
: jsr EnterRoom
 lda #6
 sta messageid
 lda #120
 sta message
 rts
