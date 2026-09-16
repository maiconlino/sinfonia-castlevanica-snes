; Original 65c816-side integration example for ca65.
; Place AudioBlob fully inside one LoROM bank ($xx8000-$xxFFFF).
; Call AudioBoot before enabling NMI. Runtime calls require DBR=$00, A8, X/Y16.
; AudioBoot returns C=0 success / C=1 unavailable (game may continue silently).
; AudioCommand: A=command, X=argument, returns C=0 accepted / C=1 timeout.
.setcpu "65816"
.a8
.i16

.segment "ZEROPAGE"
audio_sequence: .res 1
audio_ready: .res 1

.segment "CODE"
AudioBoot:
    php
    sei
    phb
    sep #$20
    rep #$10
    lda #$00
    pha
    plb
    stz audio_sequence
    stz audio_ready
    ldy #$FFFF
@boot_ready:
    lda $2140
    cmp #$AA
    jne @boot_again
    lda $2141
    cmp #$BB
    jeq @start_upload
@boot_again:
    dey
    jne @boot_ready
    jmp @failed
@start_upload:
    lda #$01
    sta $2141
    stz $2142
    lda #$02
    sta $2143
    lda #$CC
    sta $2140
    ldy #$FFFF
@start_ack:
    cmp $2140
    jeq @upload
    dey
    jne @start_ack
    jmp @failed
@upload:
    ldx #$0000
@next:
    lda f:AudioBlob,x
    sta $2141
    txa
    sta $2140
    ldy #$FFFF
@byte_ack:
    cmp $2140
    jeq @byte_done
    dey
    jne @byte_ack
    jmp @failed
@byte_done:
    inx
    cpx #(AudioBlobEnd-AudioBlob)
    jne @next
    ; Last counter was X-1. Termination token is last+2, never zero.
    stz $2141
    stz $2142
    lda #$02
    sta $2143
    txa
    inc a
    jne :+
    inc a
:
    sta $2140
    ldy #$FFFF
@driver_ready:
    lda $2143
    cmp #$53
    jeq @success
    dey
    jne @driver_ready
@failed:
    plb
    plp
    sec
    rts
@success:
    ; Driver cleared CPU input ports and initialized its expected sequence to 0.
    stz $2140
    stz $2141
    stz $2142
    lda #$01
    sta audio_ready
    plb
    plp
    clc
    rts

AudioCommand:
    pha
    lda audio_ready
    jeq @unavailable
    lda audio_sequence
    cmp $2142
    jeq @send
@unavailable:
    pla
    sec
    rts
@send:
    pla
    sta $2140
    txa
    sta $2141
    inc audio_sequence
    lda audio_sequence
    sta $2142
    clc
    rts

.segment "AUDIO"
AudioBlob:
    .incbin "assets/audio-driver.bin"
AudioBlobEnd:
.assert AudioBlobEnd-AudioBlob < $8000, error, "Audio must fit in one ROM bank"
