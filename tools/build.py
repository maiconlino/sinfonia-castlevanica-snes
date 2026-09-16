#!/usr/bin/env python3
"""Build the native LoROM with ca65/ld65 and fix its SNES checksum."""
from pathlib import Path
import os,shutil,subprocess,struct,hashlib,json,re
ROOT=Path(__file__).resolve().parents[1]
def find(name):
    value=os.environ.get(name.upper()) or shutil.which(name)
    local=ROOT.parent/'snes-tools/cc65/bin'/name
    if not value and local.is_file(): value=str(local)
    if not value:raise SystemExit(f'Install cc65 and put {name} on PATH or set {name.upper()}.')
    return value
os.chdir(ROOT);(ROOT/'build').mkdir(exist_ok=True)
subprocess.run([find('ca65'),'-I','src','-I','assets','-g','-o','build/main.o','src/main.s'],check=True)
subprocess.run([find('ld65'),'-C','lorom.cfg','-m','build/rom.map','-Ln','build/labels.txt','--dbgfile','build/rom.dbg','-o','build/sinfonia-castlevanica.sfc','build/main.o'],check=True)
p=ROOT/'build/sinfonia-castlevanica.sfc';rom=bytearray(p.read_bytes());assert len(rom)==1024*1024
rom[0x7fdc:0x7fe0]=bytes(4);s=(sum(rom)+510)&65535;struct.pack_into('<HH',rom,0x7fdc,s^65535,s);p.write_bytes(rom)
assert sum(rom)&65535==s
labels={}
for line in (ROOT/'build/labels.txt').read_text().splitlines():
 m=re.match(r'al ([0-9A-Fa-f]+) \.([^@].*)',line)
 if m:labels[m[2]]=int(m[1],16)
(ROOT/'build/labels.json').write_text(json.dumps(labels,indent=2)+'\n')
report={'file':p.name,'bytes':len(rom),'sha256':hashlib.sha256(rom).hexdigest(),'checksum':s,'mapper':'LoROM','region':'NTSC','sram_bytes':8192}
(ROOT/'build/rom-info.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

(ROOT/"dist").mkdir(exist_ok=True)
for ext in ("smc","sfc"):
 (ROOT/f"dist/sinfonia-castlevanica-snes-r3.{ext}").write_bytes(rom)
