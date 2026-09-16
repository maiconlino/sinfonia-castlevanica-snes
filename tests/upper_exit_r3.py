from pathlib import Path
import json,struct
from headless import SNES
R=Path(__file__).resolve().parents[1];L=json.loads((R/'build/labels.json').read_text());e=SNES(R/'build/sinfonia-castlevanica.sfc')
v=lambda k:struct.unpack_from('<H',e.memory(),L[k])[0]
actions=[]
def run(n=1,buttons=()):e.run(n,buttons);actions.append({'frames':n,'buttons':list(buttons)})
def move(x):
 for _ in range(100):
  d=x-v('px')
  if abs(d)<3:run(4);return
  run(1,['RIGHT'if d>0 else'LEFT'])
 raise AssertionError(('move',x,v('px'),v('py')))
try:
 run(150);run(2,['START']);run(5)
 for _ in range(270):
  if v('room')==4:break
  run(1,['RIGHT','Y'])
 assert v('room')==4
 move(78)
 run(30,['B']);run(38)
 print('lowerledge',v('px'),v('py'));assert v('py')==104
 run(1);run(38,['B','RIGHT']);run(25)
 print('upperledge',v('px'),v('py'));assert v('py')==72
 for _ in range(100):
  if v('room')==5:break
  run(1,['RIGHT'])
 assert v('room')==5,(v('room'),v('px'),v('py'))
 # Pick up the first optional new sword on the ground and equip via R.
 move(62);run(5);inv=struct.unpack_from('<60H',e.memory(),L['inventory']);assert inv[1]
 run(2,['R']);run(5);assert v('weapon')==1
 e.save_image(R/'docs/r3/optional-sword.png',3)
 report={'passed':True,'controller_only':True,'ram_writes':False,'upper_right_route':'C05 -> C06','required_up_button':False,'new_sword':'Rapieira Lunar','equipped_with':'R'}
 (R/'docs/r3/upper-route.json').write_text(json.dumps(report,indent=2));print(report)
finally:e.close()
