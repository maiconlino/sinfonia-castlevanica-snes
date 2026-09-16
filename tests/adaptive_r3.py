#!/usr/bin/env python3
"""Exercise the native campaign with real controller input and read-only WRAM feedback.
Never injects position, inventory, health, game flags, SRAM or save states.
Records controller input so the run can be replayed independently.
"""
import os,json,struct,time,collections,hashlib
from pathlib import Path
from headless import SNES
ROOT=Path(__file__).resolve().parents[1]
L=json.loads((ROOT/'build/labels.json').read_text());T=json.loads((ROOT/'assets/tables.json').read_text())
OUT=ROOT/'build/qa-r3';OUT.mkdir(parents=True,exist_ok=True)
e=SNES(ROOT/'build/sinfonia-castlevanica.sfc');actions=[];events=[];ever=set();start=time.monotonic()
ram=b''
def read():
 global ram
 ram=e.memory();ever.update(i for i,x in enumerate(values('inventory',60)) if x)
def values(k,n=1):return list(struct.unpack_from('<'+'H'*n,ram,L[k]))
def val(k):return values(k)[0]
def run(n=1,buttons=()):
 buttons=list(buttons)
 e.run(n,buttons)
 if actions and actions[-1]['buttons']==buttons:actions[-1]['frames']+=n
 else:actions.append({'frames':n,'buttons':buttons})
 read()
 if e.frame>280000:raise AssertionError('Bounded campaign test exceeded frame budget')
 if val('deaths'):raise AssertionError(f'Player died in room {val("room")}')
 if len(e.audio)>4_000_000:e.audio.clear()
def tap(b):run(1,[]);run(2,[b]);run(2,[])
def event(tag):
 o={k:val(k)for k in ['room','frame','hp','weapon','armor','accessory','spell','form','bosshp','finished','deaths']}
 o.update(tag=tag,emulator_frame=e.frame);events.append(o);print(o,flush=True)
def own(i):return values('inventory',60)[i]>0
def move_to(x,attack=True):
 for _ in range(220):
  d=x-val('px')
  if abs(d)<=2:run(5,['Y']if attack else []);return
  buttons=['RIGHT'if d>0 else'LEFT']
  if attack:buttons+=['Y']
  run(1,buttons)
 raise AssertionError(('Movement timeout',x,val('px'),val('room')))
def equip(items):
 items=[i for i in items if i is not None and own(i)]
 if not items:return
 tap('START');assert val('mode')==2
 for item in items:
  for _ in range(60):
   if val('menuitem')==item:break
   tap('RIGHT')
  assert val('menuitem')==item
  tap('A')
 tap('START');assert val('mode')==1

def best_equipment():
 weapons=[i for i in range(12)if own(i)]
 w=max(weapons,key=lambda i:(T['item_power'][i]+val('level'))/T['sword_attack_frames'][i])
 if own(11):w=11
 armor=max((i for i in range(12,20)if own(i)),key=lambda i:T['item_power'][i])
 acc=next((i for i in [26,25,21,20,22]if own(i)),None)
 spell=next((i for i in [41,40,38]if own(i)),38)
 choices=[]
 for name,target in [('weapon',w),('armor',armor),('accessory',acc),('spell',spell),('potion',44)]:
  if target is not None and val(name)!=target:choices.append(target)
 equip(choices)
def fight():
 for f in range(7500):
  boss=val('bosshp')
  es=values('enemyhp',4)
  if not boss and not any(es):run(5);return
  if boss:tx=val('bossx')+24
  else:
   alive=[i for i,hp in enumerate(es)if hp]
   tx=values('enemyx',4)[min(alive,key=lambda i:abs(values('enemyx',4)[i]-val('px')))]
  pos=val('px');desired=max(10,min(228,tx-33 if tx>50 else tx+33))
  buttons=['Y']
  if abs(desired-pos)>3:buttons+=['RIGHT'if desired>pos else'LEFT']
  elif (val('face')==1 and tx>pos)or(val('face')==0 and tx<pos):buttons+=['RIGHT'if tx>pos else'LEFT']
  if boss and val('bosssy')<109 and val('grounded') and f%20==0:buttons+=['B']
  if not boss and any(h and y<125 for h,y in zip(es,values('enemyy',4))) and val('grounded') and f%20==0:buttons+=['B']
  if f%43==0 and val('mp')>=8:buttons+=['A']
  if val('hp')*2<val('maxhp') and own(44) and f%4==0:buttons+=['X']
  run(1,buttons)
  if val('mode')==3:return
 raise AssertionError(('Combat timeout',val('room'),val('bosshp'),values('enemyhp',4)))
def changeform(target):
 for _ in range(5):
  if val('form')==target:return
  tap('SELECT')
 raise AssertionError(('Transformation failed',target,val('form')))
def process():
 changeform(0);best_equipment();fight()
 if val('mode')==3:return
 for x in (56,120,184):move_to(x)
 best_equipment()
 if T['room_type'][val('room')]&1:
  move_to(110);tap('UP')
  # Buy ordinary potions through the real sanctuary shop.
  if val('gold')>=40 and values('inventory',60)[44]<6:
   tap('START');tap('SELECT');tap('SELECT')
   for _ in range(6):
    if values('inventory',60)[44]>=6 or val('gold')<40:break
    tap('A')
   tap('START')
 event('room-processed')

def reqs(r,j):return [T['room_exit_req'+str(k)][r*4+j]for k in range(4) if T['room_exit_req'+str(k)][r*4+j]!=255]
def path(goal):
 q=collections.deque([(val('room'),[])]);seen={val('room')}
 while q:
  r,p=q.popleft()
  if r==goal:return p
  for j in range(4):
   target=T['room_exit_to'][r*4+j]
   if target==255 or target in seen or target==59 and goal!=59:continue
   if not all(own(i) for i in reqs(r,j)):continue
   seen.add(target);q.append((target,p+[(r,j,target)]))
 raise AssertionError(('No valid route',val('room'),goal,sorted(ever)))
ROUTES=json.loads((ROOT/'assets/routes.json').read_text())['rooms']
def travel(goal):
 for old,j,target in path(goal):
  assert val('room')==old
  changeform(0)
  slot=next(i for i,x in enumerate(ROUTES[old]['slots']) if x and x['exitIndex']==j)
  right=slot&1;upper=slot>=2
  if not upper and val("py")<132:
   move_to(122)
   run(55)
  # Stage near the edge, not on the transition trigger itself.
  move_to(218 if right else 20)
  if upper:
   for f in range(100):
    bs=['B'] if f<22 else []
    run(1,bs)
    if val('py')==104 and val('grounded'):break
   assert val('py')==104,('Cannot reach ledge',old,slot,val('px'),val('py'))
  if T['room_exit_secret'][old*4+j]:run(36,['Y'])
  form=next((f for i,f in [(32,1),(34,2),(35,3)] if i in reqs(old,j)),0)
  changeform(form)
  for f in range(50):
   run(1,['RIGHT' if right else 'LEFT'])
   if val('room')!=old:break
  assert val('room')==target,('Edge failed',old,j,slot,target,val('room'),val('px'),val('py'),val('messageitem'),val('form'))
  run(8)
  if val('bosshp'):fight()
  if val('mode')==3:return
  fight()
  changeform(0)
  if T['room_type'][val('room')]&1:move_to(110);tap('UP')

try:
 run(180);tap('START');run(10);assert val('mode')==1
 event('start')
 targets=[0, 1, 2, 4, 6, 7, 8, 9, 10, 11, 12, 15, 16, 17, 18, 19, 21, 22, 23, 24, 25, 27, 28, 30, 31, 32, 33, 34, 36, 37, 38, 39, 40, 41, 42, 45, 46, 47, 48, 50, 51, 52, 53, 54, 55, 57, 58, 56, 3, 5, 20, 26, 29, 35, 43, 44, 14, 13, 49, 59]
 processed=set()
 for target in targets:
  if target in processed:continue
  if val('room')!=target:travel(target)
  if val('mode')!=3:process()
  processed.add(target)
  e.save_image(OUT/f'room-{target:02d}.png',2)
 assert val('finished')==1 and val('mode')==3
 assert all(values('visited',60)),values('visited',60)
 assert all(values('defeated',10)),values('defeated',10)
 assert len(ever)==60,(len(ever),set(range(60))-ever)
 result=dict(e.summary(),completed=True,visited_rooms=60,bosses_defeated=10,item_types_acquired=len(ever),deaths=val('deaths'),wall_seconds=time.monotonic()-start,rom_sha256=hashlib.sha256(e.rom_bytes).hexdigest(),memory_writes=False)
 e.save_image(OUT/'ending.png',3);(OUT/'final.srm').write_bytes(e.memory(0))
except BaseException as ex:
 result=dict(e.summary(),completed=False,error=repr(ex),state={k:val(k)for k in ['room','px','py','mode','hp','bosshp','deaths']})
 e.save_image(OUT/'failure.png',3)
 raise
finally:
 (OUT/'result.json').write_text(json.dumps(result,indent=2)+'\n')
 (OUT/'controller-inputs.json').write_text(json.dumps(actions,separators=(',',':'))+'\n')
 (OUT/'events.json').write_text(json.dumps(events,indent=2)+'\n')
 print(json.dumps(result,indent=2),flush=True);e.close()
