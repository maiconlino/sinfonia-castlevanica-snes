#!/usr/bin/env python3
"""Controller-only campaign traversal for the native revision.

Reads WRAM for assertions and navigation feedback, but never writes it. The
controller knows the complete room graph. This is a regression test, not a human
playtime or enjoyment measurement. It deliberately avoids speedrun claims.
"""
from pathlib import Path
import json,sys,struct,collections,os
from headless import SNES
R=Path(__file__).resolve().parents[1]
T=json.loads((R/'assets/tables.json').read_text());L=json.loads((R/'build/labels.json').read_text())
OUT=R/'tests/results-v1.1';OUT.mkdir(exist_ok=True)
e=SNES(R/'build/sinfonia-castlevanica.sfc');actions=[];events=[]
def get(name,n=1):
    a=struct.unpack_from('<'+'H'*n,e.memory(),L[name]&65535)
    return a[0] if n==1 else list(a)
def run(frames=1,buttons=()):
    b=list(buttons)
    if actions and actions[-1]['buttons']==b:actions[-1]['frames']+=frames
    else:actions.append({'frames':frames,'buttons':b})
    e.run(frames,b)
    if len(e.audio)>1000000:e.audio.clear()
    if get('mode')==3 and get('finished'):return
    if get('deaths'):raise AssertionError(('death',get('room'),get('hp'),e.frame))
def tap(button):run(2,[button]);run(3)
def walk(x,limit=500,attack=True):
    for _ in range(limit):
        px=get('px');v=get('vx');v=v if v<32768 else v-65536;dx=x-px
        b=['Y'] if attack else []
        enemies=[(abs(ex-px),ex) for ex,ey,h in zip(get('enemyx',4),get('enemyy',4),get('enemyhp',4)) if h and abs(ey-get('py'))<34]
        danger=min(enemies,default=(999,0))
        if attack and danger[0]<40:
            want=0 if danger[1]>=px else 1
            if get('face')!=want:b.append('RIGHT' if want==0 else 'LEFT')
            if e.frame%61==0:b.append('A')
        else:
            if abs(dx)<=3 and abs(v)<128:run(3,b);return
            if abs(dx)>3 or dx*v<0:b.append('RIGHT' if dx>0 else 'LEFT')
        if get('hp')<get('maxhp')*.5 and get('inventory',60)[44] and e.frame%20==0:b.append('X')
        run(1,b)
    raise AssertionError(('cannot reach x',x,get('px'),get('room')))
def human():
    for _ in range(5):
        if get('form')==0:return
        tap('SELECT')
    raise AssertionError('Cannot return to human')
def equip(item):
    if not get('inventory',60)[item]:return
    tap('START')
    for _ in range(65):
        if get('menuitem')==item:break
        tap('DOWN')
    assert get('menuitem')==item,(item,get('menuitem'))
    tap('A');tap('B')
def upgrade():
    inv=get('inventory',60)
    candidates=[i for i in range(12) if inv[i]]
    best=max(candidates,key=lambda i:T['item_power'][i]/T['sword_attack_frames'][i]+(4 if i==11 else .6 if i in (3,6,9,10) else 0))
    for _ in range(12):
        if get('weapon')==best:break
        tap('R')
    armor=max((i for i in range(12,20) if inv[i]),key=lambda i:T['item_power'][i])
    if get('armor')!=armor:equip(armor)
def bossfight():
    if not get('bosshp'):return
    initial=get('boss');count=0
    while get('bosshp') and count<7000:
        x=get('px');bx=get('bossx');target=bx-32 if bx>50 else bx+30
        b=['Y']
        if abs(x-target)>3:b.append('RIGHT' if x<target else 'LEFT')
        if count%61==0:b.append('A')
        if get('hp')<get('maxhp')*.4 and get('inventory',60)[44] and count%20==0:b.append('X')
        run(1,b);count+=1
    assert not get('bosshp'),('boss stalled',initial,get('bosshp'))
    run(15)  # Let reward, audio and ending-screen work finish at an emulated frame boundary.
    events.append({'event':'boss','id':initial,'frames':count,'room':get('room'),'hp':get('hp')})
    if get('mode')==3:
        e.save_image(OUT/'ending.png',3)
        tap('START');run(30)
def sweep():
    room=get('room');human();upgrade();bossfight()
    if get('room')!=room:return
    for x in (16,58,122,186,224):walk(x)
    for _ in range(110):run(1,['Y'])
    upgrade()
    if T['room_type'][room]&1:
        walk(110);tap('UP');run(5)
    events.append({'event':'room','id':room,'frame':e.frame,'hp':get('hp'),'owned':sum(bool(x) for x in get('inventory',60))})
    if room in (0,7,8,16,23,31,38,46,53):e.save_image(OUT/f'room-{room:02}.png',3)
def requirements(room,door):
    idx=room*4+door
    return [T['room_exit_req'+str(k)][idx] for k in range(4) if T['room_exit_req'+str(k)][idx]!=255]
def path_to_new(done):
    inv=get('inventory',60);start=get('room');q=collections.deque([(start,[])]);seen={start}
    while q:
        room,path=q.popleft()
        if room not in done:return path
        for door in range(4):
            target=T['room_exit_to'][room*4+door]
            if target==255 or target in seen or any(not inv[i] for i in requirements(room,door)):continue
            seen.add(target);q.append((target,path+[(door,target)]))
    return None

def enter(door,target):
    before=get('room');bossfight();human();req=requirements(before,door)
    walk(T['door_x'][door]);run(30,['Y'])
    desired=1 if 32 in req else 2 if 34 in req else 3 if 35 in req else 0
    for _ in range(5):
        if get('form')==desired:break
        tap('SELECT')
    for attempt in range(5):
        # Flying forms settle at the ground before a door can be used.
        run(60,['DOWN','Y'] if desired>=2 else ['Y'])
        run(2,['UP','Y']);run(20,['Y'])
        if get('room')==target:return
        if get('room')!=before:raise AssertionError(('wrong exit',before,door,target,get('room')))
    raise AssertionError(('exit blocked',before,door,target,get('px'),get('py'),req,get('form')))

try:
    run(180);tap('START');run(30)
    done=set()
    for iteration in range(100):
        room=get('room')
        if room not in done:sweep();done.add(room)
        route=path_to_new(done)
        if route is None:break
        for door,target in route:enter(door,target)
    summary={'controller_only':True,'memory_written':False,'emulator':e.info.library_name.decode()+' '+e.info.library_version.decode(),'frames':e.frame,'simulated_seconds':e.frame/e.av.timing.fps,'rooms':sum(bool(x) for x in get('visited',60)),'bosses':sum(bool(x) for x in get('defeated',10)),'item_types_owned':sum(bool(x) for x in get('inventory',60)),'finished':bool(get('finished')),'deaths':get('deaths'),'room_ids':sorted(done),'missing_items':[i for i,v in enumerate(get('inventory',60)) if not v]}
    (OUT/'controller-report.json').write_text(json.dumps(summary,indent=2)+'\n')
    (OUT/'controller-events.json').write_text(json.dumps(events,indent=2)+'\n')
    (OUT/'controller-inputs.json').write_text(json.dumps(actions,separators=(',',':'))+'\n')
    print(json.dumps(summary,indent=2))
    assert summary['rooms']==60 and summary['bosses']==10 and summary['finished'],summary
    # Persist bytes from the real SRAM, not a reconstructed save.
    (OUT/'controller-save.srm').write_bytes(e.memory(0))
except Exception:
    e.save_image(OUT/'failure.png',3)
    print('STATE',{n:get(n) for n in ('room','px','py','hp','form','mode','weapon','boss','bosshp','deaths')})
    print('EVENTS',events[-10:]);raise
finally:e.close()
