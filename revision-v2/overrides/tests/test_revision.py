#!/usr/bin/env python3
"""Controller-only boot, movement, jumping, menu and SRAM regression for v2.

The test reads WRAM for assertions but never writes WRAM. Only the saved SRAM
payload is restored when opening a fresh emulation session, as a frontend does.
It does not claim testing on a physical console or all emulator configurations.
"""
from pathlib import Path
import json,struct,hashlib
from headless import SNES
ROOT=Path(__file__).resolve().parents[1]
LABELS=json.loads((ROOT/'build/labels.json').read_text())
OUT=ROOT/'build/qa';OUT.mkdir(exist_ok=True)

def read(e,label,n=1):
    value=struct.unpack_from('<'+'H'*n,e.memory(),LABELS[label])
    return value[0] if n==1 else list(value)
def new_game():
    e=SNES(ROOT/'build/sinfonia-castlevanica.sfc');e.run(100);e.run(1,['START']);e.run(100)
    assert read(e,'mode')==1 and read(e,'room')==0
    return e
def tap(e,key):e.run(1,[key]);e.run(1)
def walk_to(e,target):
    for _ in range(180):
        x=read(e,'px');vx=read(e,'vx');vx=vx if vx<32768 else vx-65536
        if abs(x-target)<=2:
            e.run(4)
            if abs(read(e,'px')-target)<=4:return
        e.run(1,['RIGHT' if x<target else 'LEFT'])
    raise AssertionError('Could not walk to target')
def jump_trace(hold):
    e=new_game();walk_to(e,16);e.run(20);trace=[]
    for f in range(85):
        e.run(1,['B'] if f<hold else [])
        trace.append(read(e,'py'))
    e.close();return trace

def main():
    e=new_game();e.save_image(OUT/'gameplay-v2.png',4)
    previous=read(e,'frame');positions=[];poses=set();delta=[]
    for _ in range(48):
        e.run(1,['RIGHT']);now=read(e,'frame')
        delta.append((now-previous)&65535);previous=now
        positions.append(read(e,'px'));poses.add(read(e,'heropose'))
    assert all(n==1 for n in delta),'Dropped logic update in walking test'
    assert set(range(2,10))<=poses,'Eight running poses were not rendered'
    assert all(a<=b for a,b in zip(positions,positions[1:])),positions
    start=read(e,'px');e.run(4,['LEFT']);assert read(e,'px')<start
    e.save_image(OUT/'running-v2.png',4)
    e.run(1,['B','LEFT']);e.run(14,['B','LEFT']);e.save_image(OUT/'jumping-v2.png',4)
    e.run(85);walk_to(e,112);tap(e,'UP')
    assert read(e,'savedvalid')==1
    saved=e.memory(0);assert len(saved)==8192
    inventory=read(e,'inventory',60);checkpoint=read(e,'checkpoint')
    tap(e,'START');assert read(e,'mode')==2
    oldframe=read(e,'frame');oldpx=read(e,'px');e.run(60)
    assert read(e,'px')==oldpx,'Menu failed to pause movement'
    e.save_image(OUT/'inventory-v2.png',3)
    tap(e,'START');assert read(e,'mode')==1
    summary=e.summary();e.close()
    e=SNES(ROOT/'build/sinfonia-castlevanica.sfc');e.set_memory(0,saved,kind=0);e.run(100)
    assert read(e,'savedvalid')==1
    tap(e,'SELECT');e.run(80)
    assert read(e,'mode')==1 and read(e,'checkpoint')==checkpoint
    assert read(e,'inventory',60)==inventory
    e.close()
    short=jump_trace(3);long=jump_trace(28)
    assert min(long)<min(short)-15,'Variable jump height not detected'
    assert long[-1]==short[-1]==152,'Character did not land on the floor'
    # Acceleration moves through more than one integral delta, but never jumps
    # multiple simulation frames at once during the tested 48-frame corridor.
    report={'passed':True,'rom_sha256':hashlib.sha256((ROOT/'build/sinfonia-castlevanica.sfc').read_bytes()).hexdigest(),
        'emulator':summary['core']+' '+summary['version'],'hardware_fps':summary['fps'],
        'logic_updates_per_emulated_frame':{'samples':48,'min':min(delta),'max':max(delta)},
        'observed_running_poses':sorted(poses),'direction_change':'passed',
        'jump_min_y':{'tap_3_frames':min(short),'hold_28_frames':min(long)},
        'menu_pause':True,'sram_restart_roundtrip':True,'audio_output_nonzero':summary['audio_nonzero'],
        'physical_hardware_tested':False,'wrapping_note':'Only SRAM restore writes memory; gameplay uses controller input.'}
    (ROOT/'build/regression-v2.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
