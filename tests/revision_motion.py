#!/usr/bin/env python3
"""Input, VBlank cadence, animation, coherent doors and real SRAM regressions.

Normal motion and the route to the first boss use controller input only. SRAM
restoration explicitly loads previously saved bytes, as an emulator would.
"""
from pathlib import Path
import json,struct,sys
from headless import SNES
R=Path(__file__).resolve().parents[1];L=json.loads((R/'build/labels.json').read_text());OUT=R/'tests/results-v1.1';OUT.mkdir(exist_ok=True)
report={};captures=[]

def new():
    e=SNES(R/'build/sinfonia-castlevanica.sfc');e.run(180);e.run(2,['START']);e.run(35);return e

def read(e,name):return struct.unpack_from('<H',e.memory(),L[name]&65535)[0]
def close(e):e.close()
def frame_image(e):
    from PIL import Image
    import numpy as np
    w,h,buf=e.image
    pix=np.frombuffer(buf,dtype='<u2').reshape(h,w)
    rgb=np.stack([((pix>>11)&31)*255//31,((pix>>5)&63)*255//63,(pix&31)*255//31],axis=-1).astype(np.uint8)
    return Image.fromarray(rgb)

e=new();steps=[]
for i in range(10):
    e.run(1,['RIGHT']);steps.append({'x':read(e,'px'),'fraction':read(e,'xfrac'),'vx':read(e,'vx')})
assert [x['vx'] for x in steps]==[96,192,288,384,480,512,512,512,512,512],steps
x=read(e,'px');e.run(15);assert read(e,'vx')==0 and 0<=read(e,'px')-x<=5
report['acceleration_8_8']=steps;report['release_stops_without_sticky_input']=True
seen=set()
for i in range(50):e.run(1,['RIGHT']);seen.add(read(e,'heroframe'))
assert set(range(2,10)).issubset(seen),seen
report['all_eight_walk_poses_reached']=True
# Return along the floor. Take captures directly from the core, not art previews.
for i in range(96):
    e.run(1,['LEFT'] if i<50 else ['RIGHT','B'] if i<68 else ['RIGHT','Y'])
    if i%2==0:captures.append(frame_image(e))
e.save_image(OUT/'motion-frame.png',3)
start=read(e,'frame');e.run(600,['Y']);ticks=(read(e,'frame')-start)&65535
assert ticks==600,ticks
report['normal_ticks_per_600_emulated_frames']=ticks
close(e)
# Compare a very short jump against a full-height held jump in the starting room.
apex=[]
for hold in (1,40):
    e=new();minimum=152
    # Move off the lower platform's horizontal span to compare the same clear arc.
    e.run(28,['LEFT']);e.run(8)
    for i in range(70):
        e.run(1,['B'] if i<hold else [])
        minimum=min(minimum,read(e,'py'))
    apex.append(minimum)
    assert read(e,'py')==152 and read(e,'grounded')==1
    close(e)
assert apex[1]<apex[0]-25,apex
report['jump_apex_y_short_and_held']=apex
# Actual doors and first boss, with no WRAM mutation.
e=new()
def walk(x):
    for i in range(240):
        px=read(e,'px');vx=read(e,'vx');vx=vx if vx<32768 else vx-65536;dx=x-px
        if abs(dx)<=3 and abs(vx)<128:e.run(4);return
        b=[]
        if abs(dx)>3 or dx*vx<0:b=['RIGHT' if dx>0 else 'LEFT']
        e.run(1,b+['Y'])
    raise AssertionError('Walk failed')
for exit,target in ((0,1),(1,2),(1,4),(1,6),(1,7)):
    walk([24,88,152,216][exit]);e.run(2,['UP','Y']);e.run(24,['Y']);assert read(e,'room')==target
    if target==4:
        e.save_image(OUT/'chapel-revision.png',3)
        # 4 independent portals, each has 24 ordered pieces, not repeated doors.
        memory=e.memory()
        for door in range(4):
            values=[]
            for y in range(6):
                for x in range(4):values.append(struct.unpack_from('<H',memory,0x1000+(17+y)*64+4+door*16+x*2)[0])
            assert len(set(v&1023 for v in values))==24
            assert all((v&0x1c00)==0x1800 for v in values)
        report['coherent_door_parts']=True
        walk(110);e.run(2,['UP']);e.run(25);assert read(e,'savedvalid')==1
        saved=e.memory(0);(OUT/'chapel-test.srm').write_bytes(saved)
e.save_image(OUT/'first-boss-revision.png',3)
start=read(e,'frame')
for i in range(600):
    buttons=['Y']
    if read(e,'hp')<read(e,'maxhp')*.55 and i%20==0:buttons.append('X')
    e.run(1,buttons)
    if i==299:report['active_boss_ticks_per_first_300_frames']=(read(e,'frame')-start)&65535
ticks=(read(e,'frame')-start)&65535
assert 599<=ticks<=600,(ticks,read(e,'room'),read(e,'deaths'),read(e,'hp'))
assert report['active_boss_ticks_per_first_300_frames']==300
report['boss_sample_note']='600 frames include the boss defeat and the automatic SRAM save; a one-frame transition is allowed.'
report['boss_ticks_per_600_emulated_frames']=ticks
report['boss_active_during_cadence_test']=bool(read(e,'bosshp'))
close(e)
# Simulate closing and reopening an emulator with the saved SRAM bytes.
e=SNES(R/'build/sinfonia-castlevanica.sfc');e.set_memory(0,saved,kind=0);e.run(180);assert read(e,'savedvalid')==1
e.run(2,['SELECT']);e.run(60);assert read(e,'mode')==1 and read(e,'room')==4
report['sram_reloaded_in_fresh_emulator']=True;close(e)
report['emulator']='Snes9x 1.63 libretro';report['physical_console_tested']=False
(OUT/'motion-report.json').write_text(json.dumps(report,indent=2)+'\n')
if captures:
    from PIL import Image
    frames=[x.resize((512,448),Image.Resampling.NEAREST) for x in captures]
    frames[0].save(OUT/'movement-from-emulator.gif',save_all=True,append_images=frames[1:],duration=33,loop=0,optimize=False)
print(json.dumps(report,indent=2))
