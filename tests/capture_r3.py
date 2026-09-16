#!/usr/bin/env python3
"""Record actual controller replay. Reads RAM to select clips; never changes game state."""
from pathlib import Path
import json, struct, subprocess, wave
import numpy as np
from headless import SNES
R=Path(__file__).resolve().parents[1]; out=R/'docs/r3'; out.mkdir(parents=True,exist_ok=True)
e=SNES(R/'build/sinfonia-castlevanica.sfc');labels=json.loads((R/'build/labels.json').read_text())
fps=e.av.timing.fps
writer=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pixel_format','rgb24','-video_size','256x224','-framerate',str(fps),'-i','-','-vf','scale=768:672:flags=neighbor','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p',str(out/'capture-silent.mp4')],stdin=subprocess.PIPE)
audio=bytearray();seen=set();boss_frames={};n=0
for action in json.loads((R/'build/qa-r3/controller-inputs.json').read_text()):
 for _ in range(action['frames']):
  e.audio.clear();e.run(1,action['buttons']);ram=e.memory()
  def v(name):return struct.unpack_from('<H',ram,labels[name])[0]
  b=v('boss');age=v('bossage');active=v('bosshp')>0 and b<10
  if active and 75<=age<=240:
   boss_frames[b]=boss_frames.get(b,0)+1
   if b not in seen and age>=100:
    e.save_image(out/f'boss-{b:02d}.png',3);seen.add(b)
  take=190<=e.frame<=1350 or (active and 75<=age<=240)
  if take:
   w,h,raw=e.image;a=np.frombuffer(raw,dtype='<u2').reshape(h,w)
   im=np.stack([((a>>11)&31)*255//31,((a>>5)&63)*255//63,(a&31)*255//31],axis=2).astype('uint8')
   writer.stdin.write(im.tobytes());audio.extend(e.audio);n+=1
writer.stdin.close();assert writer.wait()==0
with wave.open(str(out/'capture.wav'),'wb') as f:
 f.setnchannels(2);f.setsampwidth(2);f.setframerate(round(e.av.timing.sample_rate));f.writeframes(audio)
subprocess.run(['ffmpeg','-y','-loglevel','error','-i',str(out/'capture-silent.mp4'),'-i',str(out/'capture.wav'),'-c:v','copy','-c:a','aac','-b:a','128k','-shortest','-movflags','+faststart',str(out/'sinfonia-snes-r3-jogabilidade.mp4')],check=True)
(out/'capture-silent.mp4').unlink();(out/'capture.wav').unlink()
print(json.dumps({'captured_video_frames':n,'seconds':n/fps,'bosses_shown':sorted(seen),'boss_frames':boss_frames,'rom_sha256':__import__('hashlib').sha256(e.rom_bytes).hexdigest(),'memory_writes':False},indent=2))
e.close()
