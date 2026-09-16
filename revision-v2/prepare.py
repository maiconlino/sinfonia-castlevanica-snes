#!/usr/bin/env python3
"""Prepare native v2 sources without relying on a long deleted-text hunk."""
from pathlib import Path
import os, shutil, subprocess, re
root=Path.cwd();temp=Path(os.environ['RUNNER_TEMP'])
stage=temp/'native-source';work=temp/'native-v2'
stage.mkdir()
shutil.copytree(root/'.source-import',stage/'.source-import')
subprocess.run(['python',str(stage/'.source-import/restore.py')],check=True,cwd=stage)
baseline=stage/'legacy/v1.0'
assert (baseline/'src/main.s').is_file()
shutil.copytree(baseline,work)
patch=(root/'revision-v2/engine.patch').read_text().replace('\n diff --git','\ndiff --git')
# The native routine is replaced wholesale in polish.s. Avoid transcription
# fragility in a 196-line removal by verifying and removing exact boundaries.
pattern=r'(?ms)^@@ -1122,202 \+1170,6 @@ TickTimers:\n.*?(?=^@@ )'
patch,count=re.subn(pattern,'',patch)
assert count==1,'Unexpected movement diff layout'
patchfile=temp/'native-v2.patch';patchfile.write_text(patch)
subprocess.run(['git','apply','--recount','--check',str(patchfile)],cwd=work,check=True)
subprocess.run(['git','apply','--recount',str(patchfile)],cwd=work,check=True)
p=work/'src/main.s';text=p.read_text()
assert text.count('\nMovePlayer:\n')==1 and text.count('\nCycleWeapon:\n')==1
start=text.index('\nMovePlayer:\n');end=text.index('\nCycleWeapon:\n',start)
assert 'lda #$fff8' in text[start:end] and 'sta prevy' in text[start:end]
p.write_text(text[:start]+text[end:])
for p in (root/'revision-v2/overrides').rglob('*'):
    if p.is_file():
        dest=work/p.relative_to(root/'revision-v2/overrides')
        dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
(work/'build/qa').mkdir(parents=True,exist_ok=True)
p=work/'tests/validate_rom.py'
text=re.sub(r'''Path\(['"]/workspace/scratch/404cd925307f/sinfonia-snes['"]\)''','Path(__file__).resolve().parents[1]',p.read_text())
assert '/workspace/scratch/' not in text
p.write_text(text)
(work/'requirements-assets.txt').write_text('Pillow==12.2.0\nnumpy==2.3.5\n')
(work/'docs/HISTORICO.md').write_text('# Documentação histórica\n\nDocumentos sem identificação v2 descrevem a versão original. Consulte README.md e docs/validation-v2 para arte, física e testes atuais.\n')
with open(os.environ['GITHUB_ENV'],'a') as out:out.write(f'BASELINE={baseline}\nNATIVE_V2={work}\n')
print('Prepared reviewed native v2 source. ROM checksum is verified in the next build step.')
