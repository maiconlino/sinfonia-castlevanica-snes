; Native SNES menu and battery SRAM, included after main engine routines.
; Contract: every routine enters/returns A16, X16, DB=0. No private WRAM.
; Uses t0..t5, loopidx, itemidx, exitidx, ptr, textpos and textcolor freely.
; state_begin..state_end includes all permanent progress but no battle timers.
; SRAM layout: +0 magic, +2 second magic, +4 schema, +6 payload size,
; +8 rotating checksum, +10 complement, +12..15 reserved, +16 payload.
; Magic is written LAST. A torn/corrupt save is ignored. One save slot.
; All map entries and secret routes obey visited[] and secrets[] respectively.
; This is a textual atlas, not the scrolling geometry from the browser game.
.a16
.i16
SAVE_SCHEMA = 1
SAVE_PAYLOAD = 16
SAVE_MAGIC0 = $4353
SAVE_MAGIC1 = $3146

CheckSave:
 stz savedvalid
 lda f:SRAM
 cmp #SAVE_MAGIC0
 jne @invalid
 lda f:SRAM+2
 cmp #SAVE_MAGIC1
 jne @invalid
 lda f:SRAM+4
 cmp #SAVE_SCHEMA
 jne @invalid
 lda f:SRAM+6
 cmp #STATE_SIZE
 jne @invalid
 lda f:SRAM+8
 eor f:SRAM+10
 cmp #$ffff
 jne @invalid
 lda #$53c1
 sta t0
 ldx #0
@checksum:
 lda t0
 asl
 adc #0
 eor f:SRAM+SAVE_PAYLOAD,x
 clc
 adc #$9e37
 sta t0
 inx
 inx
 cpx #STATE_SIZE
 jcc @checksum
 lda t0
 cmp f:SRAM+8
 jne @invalid
 ; Checked before copying into WRAM: out-of-range IDs can never index ROM.
 lda f:SRAM+SAVE_PAYLOAD+(room-state_begin)
 cmp #60
 jcs @invalid
 lda f:SRAM+SAVE_PAYLOAD+(checkpoint-state_begin)
 cmp #60
 jcs @invalid
 lda f:SRAM+SAVE_PAYLOAD+(weapon-state_begin)
 cmp #12
 jcs @invalid
 lda f:SRAM+SAVE_PAYLOAD+(armor-state_begin)
 cmp #12
 jcc @invalid
 cmp #20
 jcs @invalid
 lda f:SRAM+SAVE_PAYLOAD+(accessory-state_begin)
 cmp #$ffff
 jeq @accessoryok
 cmp #20
 jcc @invalid
 cmp #30
 jcs @invalid
@accessoryok:
 lda f:SRAM+SAVE_PAYLOAD+(spell-state_begin)
 cmp #38
 jcc @invalid
 cmp #44
 jcs @invalid
 lda f:SRAM+SAVE_PAYLOAD+(potion-state_begin)
 cmp #44
 jcc @invalid
 cmp #50
 jcs @invalid
 lda f:SRAM+SAVE_PAYLOAD+(level-state_begin)
 jeq @invalid
 cmp #1000
 jcs @invalid
 lda #1
 sta savedvalid
 sec
 rts
@invalid:
 clc
 rts

SaveGame:
 ; Caller chooses when to save. Menu limits manual saves to sanctuaries.
 ; Other callers may persist a boss reward or completion immediately.
 lda #0
 sta f:SRAM
 sta f:SRAM+2
 stz savedvalid
 lda #$53c1
 sta t0
 ldx #0
@copy:
 lda state_begin,x
 sta f:SRAM+SAVE_PAYLOAD,x
 lda t0
 asl
 adc #0
 eor state_begin,x
 clc
 adc #$9e37
 sta t0
 inx
 inx
 cpx #STATE_SIZE
 jcc @copy
 lda #SAVE_SCHEMA
 sta f:SRAM+4
 lda #STATE_SIZE
 sta f:SRAM+6
 lda t0
 sta f:SRAM+8
 eor #$ffff
 sta f:SRAM+10
 lda #0
 sta f:SRAM+12
 sta f:SRAM+14
 lda #SAVE_MAGIC1
 sta f:SRAM+2
 lda #SAVE_MAGIC0
 sta f:SRAM
 jsr CheckSave
 rts

LoadSave:
 jsr CheckSave
 jcc @done
 ldx #0
@copy:
 lda f:SRAM+SAVE_PAYLOAD,x
 sta state_begin,x
 inx
 inx
 cpx #STATE_SIZE
 jcc @copy
 jsr Recalculate
 sec
@done:
 rts

MenuScreen:
 jsr ClearMap
 jsr ClearOAM
 lda #$3c00
 sta textcolor
 TEXT MenuTitle,1,4
 lda menupage
 jeq @inventory
 cmp #1
 jeq @map
 cmp #2
 jeq @shop
 jsr MenuHelpScreen
 jmp @footer
@inventory:
 jsr MenuInventoryScreen
 jmp @footer
@map:
 jsr MenuMapScreen
 jmp @footer
@shop:
 jsr MenuShopScreen
@footer:
 TEXT MenuHP,24,2
 lda #(24*64+5*2)
 sta textpos
 lda hp
 jsr PrintNumber
 TEXT MenuMP,24,12
 lda #(24*64+15*2)
 sta textpos
 lda mp
 jsr PrintNumber
 TEXT MenuGold,25,2
 lda #(25*64+8*2)
 sta textpos
 lda gold
 jsr PrintNumber
 TEXT MenuLevel,25,16
 lda #(25*64+20*2)
 sta textpos
 lda level
 jsr PrintNumber
 TEXT MenuFooter,26,2
 TEXT MenuSaveHint,27,3
 rts

MenuInventoryScreen:
 TEXT MenuInventoryTitle,3,4
 TEXT MenuChosen,4,2
 lda #(5*64+2*2)
 sta textpos
 lda menuitem
 jsr NameItem
 TEXT MenuCount,7,2
 lda menuitem
 asl
 tax
 lda inventory,x
 pha
 lda #(7*64+14*2)
 sta textpos
 pla
 jsr PrintNumber
 TEXT MenuEquipHint,9,2
 TEXT MenuWeaponLabel,11,2
 lda #(12*64+2*2)
 sta textpos
 lda weapon
 jsr NameItem
 TEXT MenuArmorLabel,14,2
 lda #(15*64+2*2)
 sta textpos
 lda armor
 jsr NameItem
 TEXT MenuSpellLabel,17,2
 lda #(18*64+2*2)
 sta textpos
 lda spell
 jsr NameItem
 TEXT MenuAccessoryLabel,20,2
 lda accessory
 cmp #$ffff
 jeq @none
 lda #(21*64+2*2)
 sta textpos
 lda accessory
 jsr NameItem
 rts
@none:
 TEXT MenuNone,21,2
 rts

MenuMapScreen:
 TEXT MenuMapTitle,3,2
 ; menuitem is a previously visited room ID. Never print unseen room names.
 lda #(5*64+2*2)
 sta textpos
 lda menuitem
 jsr NameRoom
 TEXT MenuMapHint,7,2
 stz exitidx
@edge:
 lda menuitem
 asl
 asl
 clc
 adc exitidx
 tax
 lda f:room_exit_to,x
 and #$ff
 cmp #255
 jeq @next
 sta itemidx
 lda f:room_exit_secret,x
 and #$ff
 jeq @visible
 lda menuitem
 asl
 tax
 lda exitidx
 asl
 tay
 lda secrets,x
 and MenuBits,y
 jeq @next
@visible:
 ; Each discovered door gets a destination row and a gate-status row.
 lda exitidx
 asl
 clc
 adc #9
 asl
 asl
 asl
 asl
 asl
 asl
 clc
 adc #4
 sta textpos
 lda itemidx
 asl
 tax
 lda visited,x
 jeq @unknown
 lda itemidx
 jsr NameRoom
 jmp @status
@unknown:
 lda #.loword(MenuUnknownRoom)
 sta ptr
 lda #.bankbyte(MenuUnknownRoom)
 sta ptr+2
 jsr Print
@status:
 jsr MenuGateOpen
 php
 lda exitidx
 asl
 clc
 adc #10
 asl
 asl
 asl
 asl
 asl
 asl
 clc
 adc #6
 sta textpos
 plp
 jcc @locked
 lda #.loword(MenuGateFree)
 sta ptr
 lda #.bankbyte(MenuGateFree)
 sta ptr+2
 jmp @printstatus
@locked:
 lda #.loword(MenuGateLocked)
 sta ptr
 lda #.bankbyte(MenuGateLocked)
 sta ptr+2
@printstatus:
 jsr Print
@next:
 inc exitidx
 lda exitidx
 cmp #4
 jne @edge
 TEXT MenuTravelHint,19,2
 lda defeated+2
 jeq @travelLocked
 TEXT MenuTravelRule,20,2
 jmp @count
@travelLocked:
 TEXT MenuTravelLocked,20,2
@count:
 stz t0
 ldx #0
@rooms:
 lda visited,x
 jeq :+
 inc t0
: inx
 inx
 cpx #120
 jcc @rooms
 TEXT MenuDiscovered,22,2
 lda #(22*64+21*2)
 sta textpos
 lda t0
 jsr PrintNumber
 rts

; selected room + exitidx; carry set iff every non-255 requirement is owned.
; Caller ensures the secret route is discovered before describing it.
MenuGateOpen:
 lda menuitem
 asl
 asl
 clc
 adc exitidx
 sta t1
 tax
 lda f:room_exit_req0,x
 and #$ff
 jsr MenuOwnRequirement
 jcc @locked
 ldx t1
 lda f:room_exit_req1,x
 and #$ff
 jsr MenuOwnRequirement
 jcc @locked
 ldx t1
 lda f:room_exit_req2,x
 and #$ff
 jsr MenuOwnRequirement
 jcc @locked
 ldx t1
 lda f:room_exit_req3,x
 and #$ff
 jsr MenuOwnRequirement
 jcc @locked
 sec
 rts
@locked:
 clc
 rts
MenuOwnRequirement:
 cmp #255
 jeq @yes
 cmp #60
 jcs @no
 asl
 tax
 lda inventory,x
 jeq @no
@yes:
 sec
 rts
@no:
 clc
 rts

MenuShopScreen:
 TEXT MenuShopTitle,3,6
 jsr MenuAtShrine
 jcs @open
 TEXT MenuShopClosed1,7,2
 TEXT MenuShopClosed2,9,2
 rts
@open:
 TEXT MenuShopItem,5,2
 lda #(7*64+2*2)
 sta textpos
 lda menuitem
 jsr NameItem
 TEXT MenuPrice,10,2
 lda menuitem
 sec
 sbc #44
 asl
 tax
 lda f:MenuPrices,x
 pha
 lda #(10*64+12*2)
 sta textpos
 pla
 jsr PrintNumber
 TEXT MenuCount,12,2
 lda menuitem
 asl
 tax
 lda inventory,x
 pha
 lda #(12*64+14*2)
 sta textpos
 pla
 jsr PrintNumber
 TEXT MenuBuyHint,16,2
 TEXT MenuShopMax,18,2
 TEXT MenuShopRestore,20,2
 rts

MenuHelpScreen:
 TEXT MenuHelpTitle,3,9
 TEXT MenuHelp1,5,2
 TEXT MenuHelp2,7,2
 TEXT MenuHelp3,9,2
 TEXT MenuHelp4,11,2
 TEXT MenuHelp5,13,2
 TEXT MenuHelp6,15,2
 TEXT MenuHelp7,17,2
 TEXT MenuHelp8,19,2
 TEXT MenuHelp9,21,2
 rts

UpdateMenu:
 lda pressed
 and #(JOY_B|JOY_START)
 jeq @page
 lda #1
 sta mode
 jsr RoomMap
 jsr DrawGame
 rts
@page:
 lda pressed
 and #JOY_SELECT
 jeq @save
 inc menupage
 lda menupage
 cmp #4
 jcc :+
 stz menupage
: lda menupage
 jeq @inventoryPage
 cmp #1
 jeq @mapPage
 cmp #2
 jeq @shopPage
 jmp @refresh
@inventoryPage:
 lda weapon
 sta menuitem
 jmp @refresh
@mapPage:
 lda room
 sta menuitem
 jmp @refresh
@shopPage:
 lda #44
 sta menuitem
@refresh:
 jsr MenuScreen
 rts
@save:
 lda pressed
 and #JOY_Y
 jeq @move
 jsr MenuAtShrine
 jcc @saveUnavailable
 lda room
 sta checkpoint
 asl
 tax
 lda #1
 sta shrines,x
 jsr Recalculate
 lda maxhp
 sta hp
 lda maxmp
 sta mp
 stz auroraused
 jsr SaveGame
 jsr MenuScreen
 lda savedvalid
 jeq @saveFailed
 TEXT MenuSaved,22,2
 rts
@saveUnavailable:
 jsr MenuScreen
 TEXT MenuSaveOnlyShrine,22,2
 rts
@saveFailed:
 TEXT MenuSaveFailed,22,2
 rts
@move:
 lda pressed
 and #(JOY_UP|JOY_LEFT|JOY_DOWN|JOY_RIGHT)
 jeq @activate
 lda menupage
 cmp #3
 jeq @done
 lda pressed
 and #(JOY_UP|JOY_LEFT)
 jeq @forward
 lda #$ffff
 sta t0
 jmp @step
@forward:
 lda #1
 sta t0
@step:
 jsr MenuStep
 jsr MenuScreen
 rts
@activate:
 lda pressed
 and #JOY_X
 jeq @equip
 lda menupage
 cmp #1
 jne @equip
 jsr MenuFastTravel
 rts
@equip:
 lda pressed
 and #JOY_A
 jeq @done
 lda menupage
 jeq @equipItem
 cmp #2
 jeq @buyItem
 rts
@equipItem:
 jsr MenuEquip
 pha
 jsr Recalculate
 jsr MenuScreen
 pla
 jeq @equipped
 TEXT MenuPermanent,22,2
 rts
@equipped:
 TEXT MenuEquipped,22,2
 rts
@buyItem:
 jsr MenuBuy
 pha
 jsr MenuScreen
 pla
 jeq @bought
 cmp #1
 jeq @poor
 cmp #2
 jeq @full
 TEXT MenuSaveOnlyShrine,22,2
 rts
@bought:
 TEXT MenuBought,22,2
 rts
@poor:
 TEXT MenuPoor,22,2
 rts
@full:
 TEXT MenuFull,22,2
@done:
 rts

; t0 = +1 or -1. Only owned inventory items/visited rooms may be selected.
MenuStep:
 lda menupage
 cmp #2
 jeq @shop
 lda #60
 sta t1
@loop:
 lda menuitem
 clc
 adc t0
 jmi @last
 cmp #60
 jcc @candidate
 lda #0
 jmp @candidate
@last:
 lda #59
@candidate:
 sta menuitem
 asl
 tax
 lda menupage
 jeq @item
 lda visited,x
 jmp @test
@item:
 lda inventory,x
@test:
 jne @done
 dec t1
 jne @loop
@done:
 rts
@shop:
 lda menuitem
 clc
 adc t0
 cmp #44
 jcc @shopLast
 cmp #50
 jcc @shopFound
 lda #44
 jmp @shopFound
@shopLast:
 lda #49
@shopFound:
 sta menuitem
 rts

MenuEquip:
 lda menuitem
 asl
 tax
 lda inventory,x
 jeq @passive
 lda menuitem
 cmp #12
 jcc @weapon
 cmp #20
 jcc @armor
 cmp #30
 jcc @accessory
 cmp #38
 jcc @passive
 cmp #44
 jcc @spell
 cmp #50
 jcc @potion
@passive:
 lda #1
 rts
@weapon:
 sta weapon
 jmp @equipped
@armor:
 sta armor
 jmp @equipped
@accessory:
 sta accessory
 jmp @equipped
@spell:
 sta spell
 jmp @equipped
@potion:
 sta potion
@equipped:
 lda #0
 rts

; Carry set only while standing in a sanctuary without an active boss.
MenuAtShrine:
 lda bosshp
 jne @no
 ldx room
 lda f:room_type,x
 and #1
 jeq @no
 sec
 rts
@no:
 clc
 rts

; Return A: 0 bought, 1 insufficient gold, 2 full stack, 3 closed.
MenuBuy:
 jsr MenuAtShrine
 jcc @closed
 lda menuitem
 cmp #44
 jcc @closed
 cmp #50
 jcs @closed
 asl
 tax
 lda inventory,x
 cmp #9
 jcs @full
 lda menuitem
 sec
 sbc #44
 asl
 tax
 lda f:MenuPrices,x
 sta t0
 lda gold
 cmp t0
 jcc @poor
 sec
 sbc t0
 sta gold
 lda menuitem
 asl
 tax
 inc inventory,x
 lda #0
 rts
@poor:
 lda #1
 rts
@full:
 lda #2
 rts
@closed:
 lda #3
 rts

MenuFastTravel:
 ; Sanctuary-to-sanctuary travel only after defeating the Library boss.
 jsr MenuAtShrine
 jcc @unavailable
 lda defeated+2
 jeq @unavailable
 lda menuitem
 asl
 tax
 lda shrines,x
 jeq @unavailable
 lda visited,x
 jeq @unavailable
 ldx menuitem
 lda f:room_type,x
 and #1
 jeq @unavailable
 lda menuitem
 sta room
 sta checkpoint
 lda #$ffff
 sta lastroom
 lda #1
 sta mode
 jsr Recalculate
 lda maxhp
 sta hp
 lda maxmp
 sta mp
 stz auroraused
 jsr EnterRoom
 rts
@unavailable:
 jsr MenuScreen
 TEXT MenuTravelUnavailable,22,2
 rts

MenuBits: .word 1,2,4,8
MenuPrices: .word 40,130,65,420,30,25
MenuTitle: .asciiz "SINFONIA / ARQUIVO"
MenuInventoryTitle: .asciiz "EQUIPAMENTOS E ITENS"
MenuMapTitle: .asciiz "ATLAS DE SALAS VISITADAS"
MenuShopTitle: .asciiz "MERCADOR DE ECOS"
MenuHelpTitle: .asciiz "COMANDOS"
MenuChosen: .asciiz "ITEM SELECIONADO:"
MenuCount: .asciiz "QUANTIDADE:"
MenuEquipHint: .asciiz "A EQUIPA   CIMA/BAIXO: ITEM"
MenuWeaponLabel: .asciiz "ESPADA EQUIPADA:"
MenuArmorLabel: .asciiz "ARMADURA:"
MenuSpellLabel: .asciiz "MAGIA:"
MenuAccessoryLabel: .asciiz "ACESSORIO:"
MenuNone: .asciiz "NENHUM"
MenuMapHint: .asciiz "CIMA/BAIXO: SALA DESCOBERTA"
MenuUnknownRoom: .asciiz "DESTINO NAO EXPLORADO"
MenuGateFree: .asciiz "PASSAGEM LIBERADA"
MenuGateLocked: .asciiz "EXIGE RELIQUIA OU CHAVE"
MenuTravelHint: .asciiz "X: VIAJAR AO SANTUARIO"
MenuTravelRule: .asciiz "ENTRE SANTUARIOS ATIVADOS"
MenuTravelLocked: .asciiz "PODER DA BIBLIOTECA AUSENTE"
MenuDiscovered: .asciiz "SALAS DESCOBERTAS:"
MenuShopClosed1: .asciiz "O MERCADOR ESPERA EM"
MenuShopClosed2: .asciiz "QUALQUER SANTUARIO."
MenuShopItem: .asciiz "PRODUTO SELECIONADO:"
MenuPrice: .asciiz "PRECO:"
MenuBuyHint: .asciiz "A: COMPRAR   CIMA/BAIXO: ITEM"
MenuShopMax: .asciiz "LIMITE: 9 DE CADA PRODUTO"
MenuShopRestore: .asciiz "Y: DESCANSAR E SALVAR"
MenuHelp1: .asciiz "DIRECIONAL: MOVER / CIMA: AGIR"
MenuHelp2: .asciiz "B: PULAR   Y: ESPADA"
MenuHelp3: .asciiz "A: MAGIA   X: CONSUMIVEL"
MenuHelp4: .asciiz "L: ESQUIVA   R: TROCAR ESPADA"
MenuHelp5: .asciiz "SELECT: LOBO / MORCEGO / NEVOA"
MenuHelp6: .asciiz "START: PAUSA E EQUIPAMENTOS"
MenuHelp7: .asciiz "CORTE PAREDES SUSPEITAS."
MenuHelp8: .asciiz "CIMA: PORTAS E SANTUARIOS"
MenuHelp9: .asciiz "Y NO MENU: SALVAR NO SANTUARIO"
MenuHP: .asciiz "HP"
MenuMP: .asciiz "MP"
MenuGold: .asciiz "ECOS"
MenuLevel: .asciiz "NV"
MenuFooter: .asciiz "SELECT: PAGINA  B: VOLTAR"
MenuSaveHint: .asciiz "Y: SALVAR NO SANTUARIO"
MenuSaved: .asciiz "PROGRESSO SALVO NA SRAM"
MenuSaveOnlyShrine: .asciiz "SALVE APENAS NO SANTUARIO"
MenuSaveFailed: .asciiz "FALHA AO VERIFICAR A SRAM"
MenuEquipped: .asciiz "EQUIPAMENTO ATUALIZADO"
MenuPermanent: .asciiz "PODER OU CHAVE PERMANENTE"
MenuBought: .asciiz "COMPRA REALIZADA"
MenuPoor: .asciiz "ECOS INSUFICIENTES"
MenuFull: .asciiz "ESTOQUE CHEIO: LIMITE 9"
MenuTravelUnavailable: .asciiz "VIAGEM INDISPONIVEL AQUI"
