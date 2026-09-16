#!/usr/bin/env python3
"""Validate R3 native data placement, side connections and unique boss artwork."""
from pathlib import Path
import hashlib,json,struct,subprocess,sys
R=Path(__file__).resolve().parents[1]
subprocess.run([sys.executable,str(R/'tests/validate_rom.py')],check=True)
rom=(R/'build/sinfonia-castlevanica.sfc').read_bytes()
routes=json.loads((R/'assets/routes.json').read_text());data=json.loads((R/'assets/data.json').read_text())
assert len(routes['rooms'])==60 and len(routes['spine'])==48
edge_count=0
for r,old in zip(routes['rooms'],data['rooms']):
 assert r['id']==old['id']
 expected={e['to'] for e in old['exits']}; actual={e['to'] for e in r['slots'] if e}
 assert expected==actual,r['id'];edge_count+=len(actual)
seen=set();frames=[]
for i in range(10):
 raw=(R/f'assets/boss{i}-frames.chr').read_bytes()
 assert len(raw)==8192
 assert rom[(i+13)*32768:(i+13)*32768+8192]==raw
 digest=hashlib.sha256(raw).hexdigest();assert digest not in seen;seen.add(digest)
 count=len({raw[k:k+2048] for k in range(0,8192,2048)});assert count>=2
 frames.append(count)
assert len((R/'assets/boss-palettes.pal').read_bytes())==10*32
assert len(json.loads((R/'assets/audio-metadata.json').read_text())['themes'])==11
labels=json.loads((R/'build/labels.json').read_text());assert labels['state_end']-labels['state_begin']==658
report=dict(passed=True,rom_sha256=hashlib.sha256(rom).hexdigest(),rooms=60,directed_connections=edge_count,main_spine_rooms=48,bosses=10,boss_frame_slots=4,boss_unique_frames=frames,native_boss_size=[64,64],item_types=60,music_themes=11,sram_bytes=8192,saved_state_bytes=658)
p=R/'build/qa-r3/hardware.json';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
