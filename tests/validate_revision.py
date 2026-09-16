#!/usr/bin/env python3
"""Native ROM regression checks for v1.1. Scenario setup writes are explicit.
Not a substitute for a human playthrough: frame/input/render/physics/save checks.
"""
from pathlib import Path
import sys,json,struct,hashlib
from collections import Counter
from PIL import Image
from headless import SNES
ROOT=Path(__file__).resolve().parents[1]
labels=json.loads((ROOT/'build/labels.json').read_text())
OUT=ROOT/'docs/revision-1.1';OUT.mkdir(parents=True,exist_ok=True)
e=SNES(ROOT/'build/sinfonia-castlevanica.sfc')
def value(n):return struct.unpack_from('<H',e.memory(),labels[n]&65535)[0]
def put(n,v):e.set_memory(labels[n]&65535,struct.pack('<H',v&65535))
def sample(n,buttons=()):
    out=[]
    for _ in range(n):
        e.run(1,buttons)
        out.append({k:value(k) for k in ('frame','px','py','vx','vy','grounded','hero_frame','hp')})
    return out
def setup(x=130,y=152):
    for n,v in dict(px=x,py=y,vx=0,vy=0,xfrac=0,yfrac=0,grounded=1,jumps=0,coyote=6,jumpbuf=0,inv=10000,attack=0,attackcd=0,pad=0,pressed=0,oldpad=0).items():put(n,v)
    # Controlled physics scenario: enemies cannot interfere with motion sampling.
    for i in range(4):e.set_memory(labels['enemyhp']+2*i,b'\0\0')
    e.run(2)
checks={};e.run(60);e.run(1,['START']);e.run(120)
checks['boot']=value('mode')==1
setup(70)
right=sample(38,['RIGHT']);stop=sample(10)
assert all((right[i]['frame']-right[i-1]['frame'])&65535==1 for i in range(1,len(right)))
assert len(set(x['hero_frame'] for x in right))==8
assert all(x['vx']==0 for x in stop[-4:])
checks['one_logic_tick_per_video_frame']=True
checks['eight_running_poses']=True
checks['subpixel_acceleration']=len(set(x['vx'] for x in right[:8]))>=5
checks['no_continuing_drift_after_release']=True
setup(132);short=sample(2,['B'])+sample(46)
setup(132);full=sample(46,['B'])
short_height=152-min(x['py'] for x in short);full_height=152-min(x['py'] for x in full)
assert short_height<full_height and 48<=full_height<=64,(short_height,full_height)
checks['variable_jump_height_pixels']={'tap':short_height,'hold':full_height}
# Coyote: launch after walking off the lower platform (scenario setup is explicit).
setup(104,104);put('coyote',6);put('grounded',0);e.run(1,['B'])
assert value('vy')&32768
checks['coyote_window']=True
# Jump buffering: press slightly before landing.
setup(132,148);put('grounded',0);put('coyote',0);put('vy',600);put('jumps',1)
e.run(1,['B']);trace=sample(5,['B']);assert any(x['vy']&32768 for x in trace)
checks['jump_buffer']=True
# Obtain double-jump relic only for this isolated input test.
setup();e.set_memory(labels['inventory']+62,b'\1\0');e.run(8,['B']);e.run(1);before=value('vy');e.run(1,['B']);assert value('jumps')==2 and value('vy')>32767
checks['double_jump']=True
# Re-create a clean session for screenshots and movement capture, no modified save.
e.close();e=SNES(ROOT/'build/sinfonia-castlevanica.sfc');e.run(60);e.run(1,['START']);e.run(120)
e.save_image(OUT/'gameplay.png',3)
frames=[]
for step in range(112):
    buttons=['RIGHT'] if step<52 else ['LEFT']
    if 22<=step<47:buttons+=['B']
    if 61<=step<92:buttons+=['Y']
    e.run(1,buttons)
    if step%3==0:
        temp=OUT/'frame.png';e.save_image(temp,2);frames.append(Image.open(temp).copy())
frames[0].save(OUT/'movement.gif',save_all=True,append_images=frames[1:],duration=50,loop=0,optimize=False)
(OUT/'frame.png').unlink(missing_ok=True)
e.save_audio(OUT/'gameplay.wav')
checks['audio_nonzero']=any(e.audio)
# Save through the starting shrine, then walk through its first door.
e.close();e=SNES(ROOT/'build/sinfonia-castlevanica.sfc');e.run(60);e.run(1,['START']);e.run(120)
def walk(target):
    for _ in range(220):
        x=value('px');v=value('vx');sv=v if v<32768 else v-65536
        if abs(x-target)<6 and abs(sv)<128:break
        e.run(1,['RIGHT'] if x<target-4 else ['LEFT'] if x>target+4 else [])
    e.run(8)
walk(110);e.run(1,['UP']);e.run(15)
sram=e.memory(0);checks['sram_written_by_shrine']=any(sram)
checks['state_bytes']=labels['state_end']-labels['state_begin']
assert checks['state_bytes']==0x292
walk(24);e.run(1,['UP']);e.run(50)
checks['door_enters_different_room']=value('room')==1
e.save_image(OUT/'next-room.png',3)
e.close();e=SNES(ROOT/'build/sinfonia-castlevanica.sfc');e.set_memory(0,sram,kind=0)
e.core.retro_reset();e.run(75);e.run(1,['SELECT']);e.run(30)
checks['continue_after_reset']=value('mode')==1 and value('room')==0
e.save_image(OUT/'shrine-continue.png',3)
assert checks['door_enters_different_room']
assert checks.get('sram_written_by_shrine') and checks.get('continue_after_reset'),checks
report={'version':'1.1','rom_sha256':hashlib.sha256((ROOT/'build/sinfonia-castlevanica.sfc').read_bytes()).hexdigest(),'emulator':e.summary(),'checks':checks,'limitations':['Controlled physics scenarios set RAM explicitly.','No full v1.1 campaign replay or physical console test claimed.']}
(OUT/'results.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));e.close()
