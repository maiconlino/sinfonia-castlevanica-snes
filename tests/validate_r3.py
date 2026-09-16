#!/usr/bin/env python3
"""R3 gameplay regressions. Isolated fixtures explicitly write WRAM.
The separate first_route_r3.py uses controller input only.
"""
from pathlib import Path
import struct,json,hashlib
from headless import SNES
R=Path(__file__).resolve().parents[1];L=json.loads((R/'build/labels.json').read_text());out=R/'docs/r3';out.mkdir(exist_ok=True)
T=json.loads((R/'assets/tables.json').read_text());D=json.loads((R/'assets/data.json').read_text())

def boot():
 e=SNES(R/'build/sinfonia-castlevanica.sfc');e.run(120);e.run(2,['START']);e.run(5);return e

def v(e,k):return struct.unpack_from('<H',e.memory(),L[k])[0]
def arr(e,k,n):return list(struct.unpack_from('<'+'H'*n,e.memory(),L[k]))
def put(e,k,value):e.set_memory(L[k],struct.pack('<H',value&65535))
def visit_fixture(e,room):
 put(e,'checkpoint',room);put(e,'hp',0);e.run(5);assert v(e,'room')==room

e=boot();checks={};vel=[];poses=set();delta=[];hero_missing=[]
# Six hundred active frames; direction alternates to remain in the initial room.
for n in range(600):
 old=v(e,'frame');e.run(1,['RIGHT' if (n//35)%2==0 else 'LEFT']);delta.append((v(e,'frame')-old)&65535)
 if n<6:vel.append(v(e,'vx'))
 poses.add(v(e,'hero_frame'))
 oam=e.memory()[0x200:0x200+12]
 if oam[1]==0xf0:hero_missing.append(n)
assert all(x==1 for x in delta),[(i,x) for i,x in enumerate(delta) if x!=1][:20]
assert not hero_missing
checks['continuous_movement']={'frames':600,'missing_logic_ticks':0,'missing_hero_frames':0,'initial_velocity_q8':vel,'running_poses':sorted(poses)}
# A stale SPC acknowledgment cannot block a frame anymore.
put(e,'audio_sequence',180);put(e,'pending_sfx',1);delta=[]
for n in range(100):
 old=v(e,'frame');e.run(1,['RIGHT'if n%40<20 else'LEFT']);delta.append((v(e,'frame')-old)&65535)
assert all(x==1 for x in delta)
checks['audio_ack_not_blocking']={'frames':100,'fixture':'WRAM audio_sequence deliberately mismatched','missing_logic_ticks':0};e.close()
# Natural forward transition and return. No positional writes.
e=boot();start=0
for n in range(180):
 e.run(1,['RIGHT'])
 if v(e,'room')!=start:break
assert v(e,'room')==1
for n in range(160):
 e.run(1,['LEFT'])
 if v(e,'room')==0:break
assert v(e,'room')==0
checks['side_crossing']={'right':True,'left_return':True,'up_button_used':False,'ram_writes':False};e.close()
# Test each ground enemy and bat in a controlled live room.
enemy=[]
for kind in range(4):
 e=boot();visit_fixture(e,1)
 for k in ('enemyhp','enemycool','enemystun','enemyfrac','enemyanim'):e.set_memory(L[k],bytes(8))
 e.set_memory(L['enemyhp'],struct.pack('<H',300));e.set_memory(L['enemyx'],struct.pack('<H',190));e.set_memory(L['enemyy'],struct.pack('<H',152));e.set_memory(L['enemykind'],struct.pack('<H',kind));put(e,'px',45);put(e,'inv',2000)
 xs=[];an=set()
 for n in range(100):e.run(1);xs.append(arr(e,'enemyx',4)[0]);an.add(arr(e,'enemyanim',4)[0])
 assert len(set(xs))>20,(kind,len(set(xs)))
 enemy.append({'kind':kind,'unique_x_positions':len(set(xs)),'animation_ticks':len(an),'passed':True});e.close()
checks['enemies']=enemy
# All 10 distinct bosses are activated by normal EnterRoom after a room fixture.
bosses=[]
for i,b in enumerate(D['bosses']):
 e=boot();room=T['boss_room'][i];visit_fixture(e,room);put(e,'inv',60000);put(e,'px',55)
 poses=set();shots=set();maxshots=0
 for n in range(330):
  e.run(1);poses.add((v(e,'bossx'),v(e,'bossy')))
  ls=arr(e,'bplife',8);dx=arr(e,'bpdx',8);dy=arr(e,'bpdy',8);sty=arr(e,'bpstyle',8)
  maxshots=max(maxshots,sum(bool(x)for x in ls))
  for j in range(8):
   if ls[j]:shots.add((dx[j],dy[j],sty[j]))
  if n==160:e.save_image(out/f'boss-{i:02}.png',3)
 assert v(e,'boss')==i and v(e,'bosshp')>0 and shots,(i,shots)
 put(e,'bosshp',max(1,v(e,'bossmax')//3));e.run(2);assert v(e,'bossphase')==1
 bosses.append({'name':b['name'],'id':i,'sprite_sha256':hashlib.sha256((R/'assets/bosses-r3.chr').read_bytes()[2048*i:2048*(i+1)]).hexdigest(),'distinct_positions':len(poses),'projectile_vectors':sorted(shots),'max_simultaneous_shots':maxshots,'second_phase':True});e.close()
assert len({x['sprite_sha256'] for x in bosses})==10
checks['bosses']=bosses
# Spell on SNES A costs mana and produces the equipped projectile.
e=boot();before=v(e,'mp');e.run(2,['A']);assert v(e,'mp')<before and v(e,'shotlife')>0
checks['starting_magic']={'name':D['items'][38]['name'],'button':'A','mana_before':before,'mana_after':v(e,'mp'),'projectile':True}
# Save via shrine input and reload only emulated battery memory, never a savestate.
for n in range(100):
 x=v(e,'px')
 if abs(x-110)<3:break
 e.run(1,['RIGHT'if x<110 else'LEFT'])
e.run(4);e.run(2,['UP']);assert v(e,'savedvalid')==1
saved=e.memory(0);e.close();e=SNES(R/'build/sinfonia-castlevanica.sfc');e.set_memory(0,saved,kind=0);e.run(120);assert v(e,'savedvalid')==1;e.run(2,['SELECT']);e.run(6);assert v(e,'mode')==1 and v(e,'room')==0
checks['battery_save_reload']=True
report={'version':'R3','rom_sha256':hashlib.sha256(e.rom_bytes).hexdigest(),'emulator':e.summary(),'checks':checks,'limitations':['Isolated audio/enemy/boss fixtures write WRAM explicitly.','The first-route test is controller-only and is reported separately.','No full R3 campaign completion claimed.','SUPER ZSNES and physical SNES have not been tested.']}
e.close();(out/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':True,'sha256':report['rom_sha256'],'moving_enemies':4,'unique_bosses':10,'continuous_frames':600,'side_crossings':True,'SRAM':True}))
