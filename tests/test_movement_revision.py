#!/usr/bin/env python3
"""Controller-driven input, pose, frame pacing and SRAM continuation tests."""
from pathlib import Path
import json,struct,hashlib
from headless import SNES
root=Path(__file__).resolve().parents[1];L=json.loads((root/'build/labels.json').read_text());out=root/'build/qa-revision';out.mkdir(parents=True,exist_ok=True)
e=SNES(root/'build/sinfonia-castlevanica.sfc')
def v(k):return struct.unpack_from('<H',e.memory(),L[k])[0]
def press(k):e.run(2,[k]);e.run(2)
e.run(120);press('START');e.run(12);assert v('mode')==1
# Integer-pixel coordinates advance from a subpixel accumulator.
vel=[];poses=set();deltas=[]
for _ in range(32):
 old=v('frame');e.run(1,['RIGHT']);vel.append(v('vx'));poses.add(v('hero_frame'));deltas.append((v('frame')-old)&65535)
assert vel[:6]==[96,192,288,384,480,512],vel[:6]
assert len(poses&set(range(2,10)))==8,poses
assert all(d==1 for d in deltas)
e.run(5);assert v('vx')==0
# Walk past the lower platform so a jump ends on the original floor.
for _ in range(80):
 if 124<=v('px')<=128:break
 e.run(1,['LEFT'if v('px')>126 else'RIGHT'])
e.run(5)
# A held jump is significantly higher than a tap.
def jump(held):
 ys=[]
 for f in range(65):e.run(1,['B']if f<held else[]);ys.append(v('py'))
 return 152-min(ys)
short=jump(2);long=jump(30)
assert long>short+20,(short,long)
# Ten seconds of active play, every emulated frame advances exactly one game tick.
last=v('frame');skips=[]
for f in range(600):
 b=['Y']
 if f%120<35:b+=['B']
 e.run(1,b);current=v('frame');d=(current-last)&65535
 if d!=1:skips.append([f,d])
 last=current
assert not skips,skips
# Save through the altar's normal interaction.
e.run(5)
for _ in range(120):
 if abs(v('px')-110)<=2:break
 e.run(1,['LEFT'if v('px')>110 else'RIGHT'])
e.run(5);press('UP');assert v('savedvalid')==1
saved=e.memory(0);saved_room=v('room');e.close()
e=SNES(root/'build/sinfonia-castlevanica.sfc')
# SRAM injection here is solely the emulated battery-file loading operation.
e.set_memory(0,saved,kind=0);e.run(120);assert v('savedvalid')==1
press('SELECT');e.run(10);assert v('mode')==1 and v('room')==saved_room
result={'passed':True,'acceleration_q8':vel[:6],'walk_poses':sorted(poses),'tap_jump_height_pixels':short,'held_jump_height_pixels':long,'active_game_ticks':600,'missed_ticks_in_600_frames':len(skips),'sram_save_reload':True,'sram_bytes':len(saved),'rom_sha256':hashlib.sha256(e.rom_bytes).hexdigest(),'physical_console_tested':False}
(out/'movement-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));e.close()
