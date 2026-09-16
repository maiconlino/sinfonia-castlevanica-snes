"""Capture the controller-only first-route test as real emulator video and audio."""
from pathlib import Path
import json,subprocess,os
from headless import SNES
R=Path(__file__).resolve().parents[1];dest=R/'docs/r3'
e=SNES(R/'build/sinfonia-castlevanica.sfc')
p=subprocess.Popen(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pixel_format','rgb565le','-video_size','256x224','-framerate',str(e.av.timing.fps),'-i','pipe:0','-vf','scale=768:672:flags=neighbor','-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p',str(dest/'video-silent.mp4')],stdin=subprocess.PIPE)
for a in json.loads((dest/'first-route-buttons.json').read_text()):
 for _ in range(a['frames']):
  e.run(1,a['buttons'])
  p.stdin.write(e.image[2] if e.image else bytes(256*224*2))
p.stdin.close();assert p.wait()==0
e.save_audio(dest/'gameplay-audio.wav');e.close()
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(dest/'video-silent.mp4'),'-i',str(dest/'gameplay-audio.wav'),'-c:v','copy','-c:a','aac','-b:a','128k','-shortest','-movflags','+faststart',str(dest/'sinfonia-snes-r3-jogabilidade.mp4')],check=True)
