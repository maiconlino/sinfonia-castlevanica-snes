#!/usr/bin/env python3
"""Recover the two original JSON inputs from the same owner's public browser backup.
Checks canonical JSON hashes before accepting input; it never executes downloaded JS.
After recovery the final repository includes both files and rebuilds work offline.
"""
import urllib.request,json,hashlib,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE='https://raw.githubusercontent.com/maiconlino/sinfonia-castlevanica-futuristica/main/public/'
KEYS=['castle','hauntedlibrary','mythicgarden','crypt','reservoir','giantclocktower','observatory','agicore','boss','finalboss','victory']
def recover(filename,pattern,target,expected,keys=None):
    req=urllib.request.Request(BASE+filename,headers={'User-Agent':'SinfonIA-public-source-recovery'})
    text=urllib.request.urlopen(req,timeout=60).read().decode('utf-8')
    match=re.search(pattern,text)
    if not match:raise ValueError('Expected data declaration missing')
    value=json.JSONDecoder().raw_decode(text[match.end():].lstrip())[0]
    if keys:value={k:value[k] for k in keys}
    canonical=json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
    actual=hashlib.sha256(canonical).hexdigest()
    if actual!=expected:raise ValueError('Source JSON changed: '+actual)
    path=ROOT/target;path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
    print(target,actual)
recover('campaign-data.mjs',r'export\s+const\s+DATA\s*=', 'assets/data.json','28b72f755aaa3673d0c3c082cd0a18d8cd962092c3a5ed2b008993ea7479d28d')
recover('scores.js',r'export\s+const\s+SCORES\s*=', 'tools/original_scores.json','3f03a543fd4542d0dc3dde4c30497e123e43b15bae76499866a80e5c66c3b237',KEYS)
