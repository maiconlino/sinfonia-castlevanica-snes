#!/usr/bin/env python3
from pathlib import Path
import hashlib,struct,json
root=Path(__file__).resolve().parents[1];rom=(root/'build/sinfonia-castlevanica.sfc').read_bytes()
assert len(rom)==1048576
assert rom[0x7fc0:0x7fd5]==b'SINFONIA CASTLEVANICA'
assert rom[0x7fd5:0x7fdb]==bytes([0x20,2,10,3,1,0x33])
comp,check=struct.unpack_from('<HH',rom,0x7fdc);assert comp^check==65535;assert sum(rom)&65535==check
reset=struct.unpack_from('<H',rom,0x7ffc)[0];assert 0x8000<=reset<0xffc0
assert rom[reset-0x8000]==0x78 # SEI
for i in range(8):assert rom[(i+3)*32768:(i+4)*32768]==(root/f'assets/bg_region{i}.chr').read_bytes()
audio=(root/'assets/audio-driver.bin').read_bytes();assert rom[11*32768:11*32768+len(audio)]==audio
source=json.loads((root/'assets/data.json').read_text());assert len(source['rooms'])==60 and len(source['bosses'])==10 and len(source['items'])==60
print('PASS: header, LoROM layout, reset vector, checksum, all CHR banks, SPC blob and content counts.')
print('SHA256',hashlib.sha256(rom).hexdigest())
