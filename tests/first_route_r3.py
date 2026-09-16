from pathlib import Path
import json,struct,hashlib,time
from headless import SNES
R=Path(__file__).resolve().parents[1];L=json.loads((R/'build/labels.json').read_text());e=SNES(R/'build/sinfonia-castlevanica.sfc');out=R/'docs/r3';out.mkdir(exist_ok=True)
actions=[]
def v(k):return struct.unpack_from('<H',e.memory(),L[k])[0]
def values(k,n):return list(struct.unpack_from('<'+'H'*n,e.memory(),L[k]))
def run(n=1,b=()):
 e.run(n,b)
 if actions and actions[-1]['buttons']==list(b):actions[-1]['frames']+=n
 else:actions.append({'frames':n,'buttons':list(b)})
 if len(e.audio)>6000000:e.audio.clear()

def battle():
 for n in range(2400):
  hps=values('enemyhp',4)
  if not v('bosshp') and not any(hps):return
  if v('bosshp'):tx=v('bossx');ty=v('bossy')
  else:
   i=min((j for j,h in enumerate(hps) if h),key=lambda j:abs(values('enemyx',4)[j]-v('px')))
   tx=values('enemyx',4)[i];ty=values('enemyy',4)[i]
  x=v('px');dx=tx-x;buttons=['Y']
  if abs(dx)>27:buttons.append('RIGHT' if dx>0 else 'LEFT')
  elif (dx<0 and not v('face')) or (dx>0 and v('face')):buttons.append('RIGHT' if dx>0 else 'LEFT')
  if ty<v('py')-30 and n%65<35:buttons.append('B')
  if n%44==0:buttons.append('A')
  if v('hp')<50 and values('inventory',60)[44] and n%4==0:buttons.append('X')
  run(1,buttons)
  if v('deaths'):raise AssertionError(('death',v('room')))
 raise AssertionError(('battle timeout',v('room'),v('bosshp'),values('enemyhp',4),v('px'),v('py')))

try:
 run(150);run(2,['START']);run(5)
 route=[0,1,2,4,6,7]
 for i,room in enumerate(route):
  assert v('room')==room,(room,v('room'))
  if room==7:e.save_image(out/'first-boss-start.png',3)
  battle()
  print('cleared',room,'level',v('level'),'kills',v('kills'),'hp',v('hp'),flush=True)
  e.save_image(out/f'cleared-{room:02}.png',2)
  if i<len(route)-1:
   for n in range(180):
    if v('room')!=room:break
    run(1,['RIGHT'])
   assert v('room')==route[i+1],(room,v('room'))
 result={'passed':True,'controller_only':True,'ram_writes':False,'rooms':route,'first_boss_defeated':bool(values('defeated',10)[0]),'double_jump_reward':bool(values('inventory',60)[31]),'bronze_crest_reward':bool(values('inventory',60)[50]),'kills':v('kills'),'level':v('level'),'xp':v('xp'),'audio_nonzero':any(e.audio),'emulated_frames':e.frame,'rom_sha256':hashlib.sha256(e.rom_bytes).hexdigest()}
 assert result['first_boss_defeated'] and result['double_jump_reward']
 print(json.dumps(result,indent=2));(out/'first-route.json').write_text(json.dumps(result,indent=2));(out/'first-route-buttons.json').write_text(json.dumps(actions));
finally:e.close()
