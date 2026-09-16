#!/usr/bin/env python3
"""Import the author's native source, verifying every transferred byte.

The bootstrap is only transport. The resulting commits contain normal readable
source, generated artwork, sound data, tests and playable ROMs.
"""
from pathlib import Path, PurePosixPath
import argparse, base64, hashlib, io, json, os, shutil, subprocess, tarfile, urllib.request

ROOT = Path(__file__).resolve().parents[1]
STAGE = Path(os.environ['RUNNER_TEMP']) / 'sinfonia-import'
PIN = '03279b5a541dd1b0c49c4b917920bd4249a76e56'
PUBLIC = 'https://raw.githubusercontent.com/maiconlino/sinfonia-castlevanica-futuristica/' + PIN + '/public/'

def digest(b):
    return hashlib.sha256(b).hexdigest()

def run(*args):
    subprocess.run(args, cwd=ROOT, check=True)

def unpack():
    manifest = json.loads((ROOT / '.import/transfer.json').read_text())
    parts = []
    for name, expected in manifest['parts'].items():
        data = (ROOT / '.import' / name).read_bytes()
        if digest(data) != expected:
            raise ValueError('Transfer part checksum mismatch: ' + name)
        parts.append(data.strip())
    data = base64.b64decode(b''.join(parts), validate=True)
    if len(data) != manifest['bytes'] or digest(data) != manifest['sha256']:
        raise ValueError('Archive checksum mismatch')
    STAGE.mkdir(parents=True, exist_ok=True)
    with tarfile.open(fileobj=io.BytesIO(data), mode='r:xz') as archive:
        for entry in archive.getmembers():
            name = PurePosixPath(entry.name)
            if name.is_absolute() or '..' in name.parts or not entry.isfile() or entry.size > 2_000_000:
                raise ValueError('Unsafe source archive entry')
            destination = STAGE / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(archive.extractfile(entry).read())
    payload = json.loads((STAGE / 'payload-manifest.json').read_text())
    for name, expected in payload['files'].items():
        if digest((STAGE / name).read_bytes()) != expected:
            raise ValueError('Source checksum mismatch: ' + name)
    print('Verified all nine parts, archive and', len(payload['files']), 'source files')

def public_json(filename, marker, expected):
    with urllib.request.urlopen(PUBLIC + filename, timeout=45) as response:
        data = response.read(5_000_000)
    if digest(data) != expected:
        raise ValueError('Pinned common data changed: ' + filename)
    text = data.decode('utf-8')
    position = text.index('{', text.index(marker))
    value, _ = json.JSONDecoder().raw_decode(text[position:])
    return value

def common_data():
    data = public_json('campaign-data.mjs', 'DATA', '1d4c7fff6f7c26e418737e8cbd2a886050c908d6694747024af97ff3d4527e35')
    scores = public_json('scores.js', 'SCORES', '53d688c5b15bf101d2a4e864f065a09cee9dba1a751f7c5c45c0cc50a4c3a72c')
    themes = ['castle','hauntedlibrary','mythicgarden','crypt','reservoir','giantclocktower','observatory','agicore','boss','finalboss','victory']
    outputs = {
        'assets/data.json': (json.dumps(data, indent=2, ensure_ascii=False).encode(), 'be5f735e7a6bf7691a6fc1679f382dee86101fc77199a66fd71ae696009fda42'),
        'tools/original_scores.json': (json.dumps({key:scores[key] for key in themes}, ensure_ascii=False, separators=(',', ':')).encode(), '2e6473c790c8a3cc649367c89f4601c406aa9ee89d797add58452a5fcc83dede')
    }
    for name, (raw, expected) in outputs.items():
        if digest(raw) != expected:
            raise ValueError('Common JSON serialization mismatch: ' + name)
        p = ROOT / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(raw)
    print('Recovered and verified original campaign data and all 11 scores')

def overlay(folder):
    for p in sorted((STAGE / folder).rglob('*')):
        if p.is_file():
            target = ROOT / p.relative_to(STAGE / folder)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(p, target)

def check_rom(which):
    manifest = json.loads((STAGE / 'payload-manifest.json').read_text())
    data = (ROOT / 'build/sinfonia-castlevanica.sfc').read_bytes()
    expected = manifest[which + '_rom_sha256']
    actual = digest(data)
    if actual != expected:
        raise ValueError(f'{which} ROM differs: expected {expected}, got {actual}')
    version = '1.0' if which == 'baseline' else '1.1'
    p = ROOT / 'dist' / ('sinfonia-castlevanica-snes-v' + version + '.smc')
    p.parent.mkdir(exist_ok=True)
    p.write_bytes(data)
    print(version, 'ROM verified, SHA256:', actual)

def commit(message):
    run('git', 'add', 'README.md', 'Makefile', 'lorom.cfg', 'requirements-assets.txt', '.gitignore', 'src', 'tools', 'tests', 'docs', 'assets', 'dist')
    run('git', 'add', '-f', 'build/sinfonia-castlevanica.sfc', 'build/labels.json', 'build/rom-info.json')
    run('git', 'commit', '-m', message)

def finish():
    # Test images and reports are generated from this exact ROM by the emulator.
    p = ROOT / 'dist/SHA256SUMS'
    p.write_text(''.join(digest(q.read_bytes()) + '  ' + q.name + '\n' for q in sorted(p.parent.glob('*.smc'))))
    shutil.copyfile(STAGE / 'payload-manifest.json', ROOT / 'docs/SOURCE-IMPORT-MANIFEST.json')
    tracked = subprocess.check_output(['git', 'ls-files', '.import'], cwd=ROOT, text=True).splitlines()
    if tracked:
        run('git', 'rm', '-r', '.import')
    commit('Release native v1.1: coherent doors, detailed actors and fractional movement, verified in Snes9x')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('step', choices=['baseline', 'revision', 'finish'])
    args = parser.parse_args()
    if args.step == 'baseline':
        unpack()
        overlay('baseline')
        common_data()
        run('make', 'assets', 'all')
        check_rom('baseline')
        commit('Preserve original native v1.0 source, artwork, music and bit-identical ROM')
    elif args.step == 'revision':
        overlay('revision')
        run('make', 'assets', 'all', 'check')
        check_rom('revision')
    else:
        finish()
