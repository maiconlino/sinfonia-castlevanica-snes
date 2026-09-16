#!/usr/bin/env python3
"""Compile automatic screen-edge routes without deleting any original graph edge.
The main spine uses ground-level left/right exits. Optional branches use ledges.
Slots: 0 left ground, 1 right ground, 2 left ledge, 3 right ledge.
"""
from pathlib import Path
import json
from collections import deque
R=Path(__file__).resolve().parents[1]
d=json.loads((R/'assets/data.json').read_text()); rooms=d['rooms']; by={r['id']:r for r in rooms}
q=deque([['C01']]); seen={'C01'}; spine=None
while q:
 p=q.popleft()
 if p[-1]=='H07': spine=p;break
 for e in by[p[-1]]['exits']:
  if e['secret'] or e['shortcut'] or by[e['to']]['type'] in ('optional','secret','secret_boss'):continue
  if e['to'] not in seen:seen.add(e['to']);q.append(p+[e['to']])
assert spine
route=[]; report=[]
for r in rooms:
 slots=[255]*4; edges=r['exits']; used=set()
 if r['id'] in spine:
  i=spine.index(r['id'])
  for slot,neighbor in [(0,spine[i-1] if i else None),(1,spine[i+1] if i+1<len(spine) else None)]:
   for j,e in enumerate(edges):
    if e['to']==neighbor: slots[slot]=j;used.add(j)
 for j,e in enumerate(edges):
  if j in used:continue
  if r['id'] in spine: preferred=[2,3,0,1]
  else:preferred=[0,1,2,3]
  for slot in preferred:
   if slots[slot]==255:slots[slot]=j;used.add(j);break
 assert set(slots)-{255}==set(range(len(edges)))
 route.extend(slots)
 report.append({'id':r['id'],'name':r['name'],'slots':[None if j==255 else {'exitIndex':j,**edges[j]} for j in slots]})
s='; Generated original graph -> screen-edge slots. 0/1 ground, 2/3 upper.\nedge_exit_index:\n'
for i in range(0,len(route),4):s+=' .byte '+','.join(map(str,route[i:i+4]))+'\n'
(R/'assets/routes.inc').write_text(s)
(R/'assets/routes.json').write_text(json.dumps({'spine':spine,'rooms':report},ensure_ascii=False,indent=2)+'\n')
print('Automatic edge routes:',len(rooms),'rooms,',sum(len(r['exits']) for r in rooms),'directed edges; main spine:',len(spine))
