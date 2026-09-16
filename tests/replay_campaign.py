#!/usr/bin/env python3
"""Reproduce the entire campaign using only recorded controller input."""
from pathlib import Path
import sys,json,struct,hashlib
from headless import SNES
root=Path(__file__).resolve().parents[1]
labels=json.loads((root/'build/labels.json').read_text())
e=SNES(root/'build/sinfonia-castlevanica.sfc')
for action in json.loads((root/'tests/campaign-inputs.json').read_text()):e.run(action['frames'],action['buttons'])
ram=e.memory()
def get(label,n=1):return list(struct.unpack_from('<'+'H'*n,ram,labels[label]))
assert get('finished')==[1]
assert get('mode')==[3]
assert sum(bool(x) for x in get('visited',60))==60
assert sum(bool(x) for x in get('defeated',10))==10
assert all(get('inventory',60))
assert get('deaths')==[0]
print(json.dumps(dict(e.summary(),completed=True,rooms=60,item_types=60,bosses=10,deaths=0),indent=2))
e.close()
