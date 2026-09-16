#!/usr/bin/env python3
"""R3 regression suite. Staged unit cases explicitly write WRAM; campaign replay does not.
Tests emulator-visible held inputs, pacing, movement, enemy activity and SRAM.
"""
from pathlib import Path
import json,struct,hashlib
from headless import SNES
R=Path(__file__).resolve().parents[1];L=json.loads((R/'build/labels.json').read_text());O=R/'build/qa-r3';O.mkdir(exist_ok=True)
e=SNES(R/'build/sinfonia-castlevanica.sfc');e.run(120);e.run(2,['START']);e.run(10)
def v(k):return struct.unpack_from('<H',e.memory(),L[k])[0]
def w(k,n):e.set_memory(L[k],struct.pack('<H',n&65535))
def tap(k):e.run(1);e.run(2,[k]);e.run(2)
result={'rom_sha256':hashlib.sha256(e.rom_bytes).hexdigest(),'core':e.info.library_name.decode(),'version':e.info.library_version.decode(),'unit_setup_writes_wram':True,'campaign_test':'adaptive_r3.py and replay_r3.py do not modify WRAM','super_zsnes_executed':False,'physical_hardware_tested':False}
assert v('mode')==1
vel=[];walk=set();deltas=[];pads=[]
for i in range(48):
 old=v('px');e.run(1,['RIGHT']);vel.append(v('vx'));walk.add(v('hero_frame'));deltas.append(v('px')-old);pads.append(v('pad'))
assert len(walk & set(range(2,10)))==8
assert all(x==256 for x in pads)
assert all(x in (2,3) for x in deltas[4:]),deltas
result['held_right']={'frames':48,'velocities_q8_first_6':vel[:6],'steady_pixel_steps':sorted(set(deltas[4:])),'zero_steps_after_acceleration':deltas[4:].count(0),'walking_poses':sorted(walk)}
e.run(6);assert v('vx')==0
w('px',180);w('xsub',0);w('walkphase',0)
ld=[]
for i in range(45):
 old=v('px');e.run(1,['LEFT']);ld.append(old-v('px'));assert v('pad')==512
assert all(x in (2,3) for x in ld[4:]),ld
result['held_left']={'steady_pixel_steps':sorted(set(ld[4:])),'zero_steps_after_acceleration':ld[4:].count(0)}
# Same key remains held across two rooms; no UP/interaction input is used.
e.run(8);w('px',210);w('py',152);w('vx',0);w('edgecool',0)
before=v('room');e.run(20,['RIGHT']);assert v('room')==1
x1=v('px');e.run(8,['RIGHT']);assert v('px')>x1
result['automatic_edges']={'right':True,'continued_held_input_after_arrival':True}
e.run(6);w('px',24);w('vx',0);w('edgecool',0);e.run(18,['LEFT']);assert v('room')==0
result['automatic_edges']['left']=True
# Sustained movement + attack + jumps with rapid reversals, no room loads.
w('edgecool',65000);w('px',120);w('hp',v('maxhp'));w('inv',65000)
missed=0;missing_sprite=0
for i in range(6000):
 before=v('logicalframes');bs=['RIGHT' if (i//40)%2==0 else 'LEFT','Y']
 if i%50<18:bs.append('B')
 if i%45==0:bs.append('A')
 e.run(1,bs)
 if (v('logicalframes')-before)&65535!=1:missed+=1
 if e.memory()[0x201]==240:missing_sprite+=1
 if len(e.audio)>2000000:e.audio.clear()
assert missed==0,missed
assert missing_sprite==0,missing_sprite
result['frame_pacing']={'video_frames':6000,'logical_updates':6000,'missed_updates':missed,'hero_hidden_frames':missing_sprite}
# Force unacknowledged audio sequence. Active logic must never spin waiting for SPC.
e.set_memory(L['audio_sequence'],b'\xad');w('soundcmd',0);w('soundready',1)
before=v('logicalframes');e.run(600,['Y']);assert (v('logicalframes')-before)&65535==600
result['stalled_audio_ack']={'frames':600,'logical_updates':600,'blocking_wait':False}
e.close()
# Fresh emulator instance for enemy archetypes, preserving normal PPU initialization.
e=SNES(R/'build/sinfonia-castlevanica.sfc');e.run(120);tap('START');e.run(10)
# Enter first hostile room by real control before arranging isolated archetype tests.
e.run(85,['RIGHT']);assert v('room')==1
activity=[]
for kind in (0,1,2,3):
 w('edgecool',65000);w('px',32);w('py',152);w('vx',0);w('inv',65000)
 for j in range(4):e.set_memory(L['enemyhp']+j*2,struct.pack('<H',100 if j==0 else 0))
 for name,value in [('enemykind',kind),('enemyx',180),('enemyy',152),('enemycool',60),('enemyfrac',0),('enemyhurt',0),('enemywindup',0)]:w(name,value)
 e.run(45);end=v('enemyx');assert end!=180,(kind,end)
 activity.append({'archetype':kind,'start_x':180,'end_x':end,'moved':True})
result['enemies']=activity
# Real altar save and restart/continue, not a save state.
w('edgecool',0);w('px',24);w('py',152);w('vx',0)
for j in range(4):e.set_memory(L['enemyhp']+j*2,b'\x00\x00')
e.run(18,['LEFT']);assert v('room')==0
e.run(8)
for _ in range(120):
 if abs(v('px')-110)<3:break
 e.run(1,['RIGHT' if v('px')<110 else 'LEFT'])
e.run(5);tap('UP');assert v('savedvalid')==1
saved=e.memory(0);state=(v('room'),v('level'),v('weapon'),v('hp'));e.close()
e=SNES(R/'build/sinfonia-castlevanica.sfc');e.set_memory(0,saved,0);e.run(120);tap('SELECT');e.run(10)
assert v('mode')==1 and (v('room'),v('level'),v('weapon'),v('hp'))==state
result['sram']={'altar_save':True,'restart_continue':True,'bytes':len(saved)}
e.close();result['passed']=True
(O/'regression.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
