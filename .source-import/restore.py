#!/usr/bin/env python3
"""Restore reviewed sources and verify the two shared game-data inputs.
After import, normal builds use the committed JSON and need no web recovery.
"""
import base64, hashlib, io, json, tarfile, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / '.source-import'
manifest = json.loads((HERE / 'manifest.json').read_text())
def digest(data):
    return hashlib.sha256(data).hexdigest()

parts = []
for part in manifest['parts']:
    data = (HERE / part['name']).read_bytes()
    assert digest(data) == part['sha256'], ('Source part checksum mismatch', part['name'], digest(data))
    parts.append(data.strip())
archive = base64.b64decode(b''.join(parts), validate=True)
assert digest(archive) == manifest['archive_sha256'], 'Archive checksum mismatch'
with tarfile.open(fileobj=io.BytesIO(archive), mode='r:xz') as tf:
    members = tf.getmembers()
    assert len(members) == manifest['files']
    for member in members:
        name = Path(member.name)
        assert member.isfile() and not name.is_absolute() and '..' not in name.parts
        assert name.parts[0] not in ('.git', '.github', '.source-import')
        target = ROOT / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(tf.extractfile(member).read())
print('Restored', len(members), 'verified source files')

origin = 'https://sinfonia-castlevanica-futuristica.maiconheverton.chatgpt.site/'
def public_json(filename, declaration):
    req = urllib.request.Request(origin + filename, headers={'User-Agent': 'SinfonIA reproducible source backup'})
    with urllib.request.urlopen(req, timeout=30) as response:
        assert response.geturl().startswith(origin), 'Unexpected redirect'
        raw = response.read(3000000)
    text = raw.decode('utf-8')
    start = text.index('{', text.index(declaration))
    return json.JSONDecoder().raw_decode(text[start:])[0], digest(raw)
def canonical_hash(data):
    return digest(json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode())

data, data_file_hash = public_json('campaign-data.mjs', 'export const DATA')
scores, score_file_hash = public_json('scores.js', 'export const SCORES')
themes = ['castle', 'hauntedlibrary', 'mythicgarden', 'crypt', 'reservoir', 'giantclocktower', 'observatory', 'agicore', 'boss', 'finalboss', 'victory']
scores = {key: scores[key] for key in themes}
expected = manifest['recovered_verified_data']
assert canonical_hash(data) == expected['data_sha256'], 'Campaign data changed; do not import silently'
assert canonical_hash(scores) == expected['scores_sha256'], 'Music data changed; do not import silently'
for root in (ROOT, ROOT / 'legacy/v1.0'):
    for path, value in (('assets/data.json', data), ('tools/original_scores.json', scores)):
        p = root / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
report = dict(origin=origin, recovered_public_files={'campaign-data.mjs': data_file_hash, 'scores.js': score_file_hash}, canonical_checksums=expected)
(ROOT / 'docs/import-provenance.json').write_text(json.dumps(report, indent=2) + '\n')
print('Shared campaign and original music match both native source revisions')
