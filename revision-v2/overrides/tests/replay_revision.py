#!/usr/bin/env python3
"""Replay the v2 regression recording with controller input only."""
from pathlib import Path
import json,struct
from headless import SNES
root=Path(__file__).resolve().parents[1]
labels=json.loads((root/'build/labels.json').read_text())
e=SNES(root/'build/sinfonia-castlevanica.sfc')
for action in json.loads((root/'tests/campaign-inputs-v2.json').read_text()):
    e.run(action['frames'],action['buttons'])
    if len(e.audio)>16000000:e.audio.clear()
ram=e.memory()
def get(k,n=1):return list(struct.unpack_from('<'+'H'*n,ram,labels[k]))
assert get('finished')==[1] and get('mode')==[3]
assert all(get('visited',60)) and all(get('defeated',10)) and all(get('inventory',60))
assert get('deaths')==[0]
report=dict(e.summary(),completed=True,rooms=60,bosses=10,items=60,deaths=0)
(root/'build/replay-v2.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
e.close()
