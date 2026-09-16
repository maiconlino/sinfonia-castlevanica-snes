#!/usr/bin/env python3
"""Adaptive, controller-only campaign regression for the native revision.

Reads symbols for assertions and path planning; never writes WRAM or SRAM.
Knowledge of the room graph makes this a test route, not a human duration test.
"""
from pathlib import Path
from collections import deque
import struct,json,hashlib,time
from headless import SNES, BUTTONS
ROOT=Path(__file__).resolve().parents[1]
T=json.loads((ROOT/'assets/tables.json').read_text())
L=json.loads((ROOT/'build/labels.json').read_text())
class Runner:
    def __init__(self):
        self.e=SNES(ROOT/'build/sinfonia-castlevanica.sfc');self.actions=[];self.regions=set();self.shots=[];self.step(110);self.tap('START');self.step(90)
    def read(self,key,n=1):
        v=struct.unpack_from('<'+'H'*n,self.e.memory(),L[key]);return v[0] if n==1 else list(v)
    def step(self,n=1,buttons=()):
        mask=buttons if isinstance(buttons,int) else sum(1<<BUTTONS[b] for b in buttons)
        if self.actions and self.actions[-1]['buttons']==mask:self.actions[-1]['frames']+=n
        else:self.actions.append({'frames':n,'buttons':mask})
        self.e.run(n,mask)
        if len(self.e.audio)>16000000:self.e.audio.clear()
        if self.e.frame>150000:raise AssertionError('Run exceeded safety frame budget')
    def tap(self,key):self.step(3,[key]);self.step(4)
    def heal(self):
        if self.read('hp')*2<self.read('maxhp') and self.read('inventory',60)[44]:
            self.tap('X')
    def to(self,target,attack=True):
        start_room=self.read('room')
        for _ in range(220):
            if self.read('room')!=start_room:raise AssertionError('Unexpected room transition / death while moving')
            x=self.read('px')
            if abs(x-target)<=2:
                self.step(4,['Y'] if attack else [])
                if abs(self.read('px')-target)<=4:return
            self.heal()
            self.step(1,(['Y'] if attack else [])+['RIGHT' if x<target else 'LEFT'])
        raise AssertionError(f'Cannot reach x={target}; actual={self.read("px")} y={self.read("py")}')
    def equip(self,item):
        if not self.read('inventory',60)[item]:return
        self.tap('START');assert self.read('mode')==2
        for _ in range(61):
            if self.read('menuitem')==item:break
            self.tap('DOWN')
        else:raise AssertionError('Inventory selection did not reach owned item')
        self.tap('A');self.tap('START');assert self.read('mode')==1
    def upgrade(self):
        inv=self.read('inventory',60)
        sword=max((i for i in range(12) if inv[i]),key=lambda i:(T['sword_power'][i]*(2 if i==11 else 1)/T['sword_attack_frames'][i],i))
        if sword!=self.read('weapon'):self.equip(sword)
        armor=max((i for i in range(12,20) if inv[i]),key=lambda i:(T['item_power'][i],i==19))
        if armor!=self.read('armor'):self.equip(armor)
        if inv[24] and self.read('accessory')!=24:self.equip(24)
        elif inv[20] and self.read('accessory')==65535:self.equip(20)
    def fight(self):
        boss=self.read('boss');start=self.e.frame;room=self.read('room')
        self.upgrade()
        while self.read('bosshp') and self.e.frame-start<2600:
            self.heal();x=self.read('px');bx=self.read('bossx');buttons=['Y']
            if x<bx-32:buttons+=['RIGHT']
            elif x>bx+30:buttons+=['LEFT']
            elif x<bx and self.read('face'):buttons+=['RIGHT']
            elif x>bx and not self.read('face'):buttons+=['LEFT']
            if self.read('magiccd')==0 and self.read('mp')>=8 and self.e.frame%5==0:buttons+=['A']
            self.step(1,buttons)
            if self.read('room')!=room:raise AssertionError(f'Died during boss {boss}')
        assert self.read('defeated',10)[boss],f'Boss {boss} did not finish'
        if self.read('mode')!=3:self.step(12)
    def clear_room(self):
        room=self.read('room');region=self.read('region')
        if region not in self.regions:
            self.regions.add(region);self.e.save_image(ROOT/f'build/qa/region-{region}-v2.png',3)
        if self.read('bosshp'):self.fight()
        if self.read('mode')==3:return
        for j in range(3):
            if T['room_items'][room*3+j]!=255 and not self.read('looted',60)[room]&(1<<j):self.to(T['pickup_x'][j]-8)
        self.upgrade()
        # Neutralise respawning ordinary foes without invincibility or HP writes.
        for _ in range(500):
            hp=self.read('enemyhp',4)
            if not any(hp):break
            self.heal();xs=self.read('enemyx',4);idx=next(i for i,v in enumerate(hp) if v)
            x=self.read('px');ex=xs[idx];buttons=['Y']
            if x<ex-24:buttons+=['RIGHT']
            elif x>ex+24:buttons+=['LEFT']
            elif x<ex and self.read('face'):buttons+=['RIGHT']
            elif x>ex and not self.read('face'):buttons+=['LEFT']
            self.step(1,buttons)
        if T['room_type'][room]&1:
            self.to(112);self.tap('UP');assert self.read('savedvalid')==1
    def edge_allowed(self,r,j,final=False):
        i=r*4+j;dest=T['room_exit_to'][i]
        if dest==255 or (dest==59 and not final):return False
        inv=self.read('inventory',60)
        return all(v==255 or inv[v] for v in (T[f'room_exit_req{k}'][i] for k in range(4)))
    def path(self,goals,final=False):
        q=deque([(self.read('room'),[])]);seen=set()
        while q:
            r,p=q.popleft()
            if r in seen:continue
            seen.add(r)
            if r in goals:return p
            for j in range(4):
                if self.edge_allowed(r,j,final):q.append((T['room_exit_to'][r*4+j],p+[(r,j)]))
        return None
    def exit(self,j):
        room=self.read('room');i=room*4+j;target=T['room_exit_to'][i]
        self.to(T['door_x'][j]-8)
        if T['room_exit_secret'][i]:
            for _ in range(80):
                if self.read('secrets',60)[room]&(1<<j):break
                self.step(1,['Y'])
            assert self.read('secrets',60)[room]&(1<<j),'Secret was not revealed by attack'
        requirements=[T[f'room_exit_req{k}'][i] for k in range(4)]
        form=3 if 35 in requirements else 2 if 34 in requirements else 1 if 32 in requirements else 0
        for _ in range(5):
            if self.read('form')==form:break
            self.tap('SELECT')
        assert self.read('form')==form,('form',form,self.read('mp'))
        self.step(2);self.tap('UP');self.step(3)
        assert self.read('room')==target,('door',room,j,target,self.read('room'),self.read('px'),self.read('py'),self.read('form'))
        self.clear_room()
    def execute(self):
        completed=set();self.clear_room()
        while len(completed)<59:
            completed.add(self.read('room'))
            if len(completed)==59:break
            route=self.path(set(range(59))-completed)
            if route is None:raise AssertionError(('No new reachable room',len(completed),sorted(set(range(59))-completed)))
            for r,j in route:
                assert self.read('room')==r;self.exit(j)
                completed.add(self.read('room'))
                print('visited',len(completed),'room',self.read('room'),'HP',self.read('hp'),'level',self.read('level'),flush=True)
        route=self.path({59},True);assert route
        for r,j in route:self.exit(j)
        assert self.read('finished')==1 and self.read('mode')==3
        self.e.save_image(ROOT/'build/qa/ending-v2.png',4)
        report={'passed':True,'completed':True,'rooms':sum(bool(v) for v in self.read('visited',60)),
            'bosses':sum(bool(v) for v in self.read('defeated',10)),
            'items_held':sum(bool(v) for v in self.read('inventory',60)),
            'deaths':self.read('deaths'),'frames':self.e.frame,'emulated_seconds':round(self.e.frame/self.e.av.timing.fps,2),
            'rom_sha256':hashlib.sha256(self.e.rom_bytes).hexdigest(),'wrapping':'Controller-only; WRAM read-only; known-map adaptive test route, not a human play time.'}
        assert report['rooms']==60 and report['bosses']==10
        (ROOT/'build/campaign-regression-v2.json').write_text(json.dumps(report,indent=2)+'\n')
        (ROOT/'tests/campaign-inputs-v2.json').write_text(json.dumps(self.actions,separators=(',',':'))+'\n')
        (ROOT/'build/qa/campaign-completed-v2.srm').write_bytes(self.e.memory(0))
        print(json.dumps(report,indent=2));self.e.close()
if __name__=='__main__':
    runner=Runner()
    try:runner.execute()
    except Exception:
        runner.e.save_image(ROOT/'build/qa/failure-v2.png',4)
        print('FAILURE STATE',{k:runner.read(k) for k in ['room','px','py','hp','mp','boss','bosshp','weapon','armor','form','deaths']},flush=True)
        runner.e.close();raise
