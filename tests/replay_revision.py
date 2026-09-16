#!/usr/bin/env python3
"""Replay the revision campaign with no memory feedback until final assertions."""
from pathlib import Path
import json,struct,hashlib
from headless import SNES
root=Path(__file__).resolve().parents[1];out=root/'build/qa-revision'
labels=json.loads((root/'build/labels.json').read_text());e=SNES(root/'build/sinfonia-castlevanica.sfc')
for action in json.loads((out/'controller-inputs.json').read_text()):
 e.run(action['frames'],action['buttons'])
 if len(e.audio)>4_000_000:e.audio.clear()
ram=e.memory()
def get(name,n=1):return list(struct.unpack_from('<'+'H'*n,ram,labels[name]))
assert get('finished')==[1] and get('mode')==[3]
assert all(get('visited',60)) and all(get('defeated',10))
assert get('deaths')==[0]
result=dict(e.summary(),completed=True,memory_feedback_during_replay=False,rooms=60,bosses=10,deaths=0,rom_sha256=hashlib.sha256(e.rom_bytes).hexdigest())
(out/'replay-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));e.close()
