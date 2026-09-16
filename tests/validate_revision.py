#!/usr/bin/env python3
"""Isolated controller tests; room/combat fixtures are explicitly marked.
These are not a claim of full human playthrough or physical-console validation.
"""
from pathlib import Path
import json,struct,collections,sys
from headless import SNES
R=Path(__file__).resolve().parents[1]; L=json.loads((R/'build/labels.json').read_text()); e=SNES(R/'build/sinfonia-castlevanica.sfc')
def get(k):return struct.unpack_from('<H',e.memory(),L[k])[0]
def put(k,v):e.set_memory(L[k],struct.pack('<H',v&65535))
def fixture(x=120,y=152):
    # Fixtures position the hero and disable enemy damage, without modifying ROM.
    put('px',x);put('py',y);put('vx',0);put('vy',0);put('xsub',0);put('ysub',0);put('grounded',1);put('jumps',0);put('coyote',5);put('jumpbuffer',0);put('inv',60000)
    e.set_memory(L['enemyhp'],bytes(8))
e.run(120);e.run(2,['START']);e.run(140);fixture()
report={};frames=[];xs=[];poses=[]
for i in range(45):
    old=get('frame');e.run(1,['RIGHT']);frames.append((get('frame')-old)&65535);xs.append(get('px'));poses.append(get('heroindex'))
assert all(d==1 for d in frames),frames
assert xs[:6]==sorted(xs[:6])
assert 1<max(poses)-min(poses)
report['right_movement']={'frame_increments':dict(collections.Counter(frames)),'first_8_positions':xs[:8],'animation_poses':sorted(set(poses))}
e.run(6,[]);assert get('vx')==0
report['release_stops_within_frames']=6
# Jump away from both elevated platforms.
def jump(hold):
    fixture(x=130);ys=[]
    for i in range(100):
        e.run(1,['B'] if i<hold else []);ys.append(get('py'))
    assert get('py')==152 and get('grounded')==1
    return 152-min(ys)
report['tap_jump_height_pixels']=jump(1)
report['held_jump_height_pixels']=jump(24)
assert report['held_jump_height_pixels']>report['tap_jump_height_pixels']+20
# Use the real sanctuary interaction to save; fixture only positions the player.
fixture(x=120);put('gold',321);e.run(1,['UP']);e.run(3,[])
saved=e.memory(0)
assert get('savedvalid')==1, 'Sanctuary did not produce valid SRAM'
report['sanctuary_save']={'valid':True,'gold':321}
# Use normal room transition with an unobstructed exit, no teleport through gates.
fixture(x=24);oldroom=get('room');e.run(1,['UP']);e.run(15,[]);newroom=get('room')
assert oldroom!=newroom
report['normal_door_transition']={'from':oldroom,'to':newroom}

e.save_image(str(R/'build/v2-refined.png'),scale=3)
report['core']=e.summary();report['limits']=['Controller fixtures, not a full campaign replay','No physical SNES test']
e.close()
e=SNES(R/'build/sinfonia-castlevanica.sfc')
e.set_memory(0,saved,kind=0)
e.run(120);e.run(2,['SELECT']);e.run(20,[])
assert get('gold')==321 and get('room')==0 and get('mode')==1
report['cold_boot_sram_restore']={'passed':True,'gold':get('gold'),'room':get('room')}
e.close()
(R/'build/revision-tests.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
