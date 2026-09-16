"""Four distinct 32x32 enemy silhouettes with two native gait poses each."""
from PIL import ImageDraw
import generate_graphics as g

def enemy(kind,frame):
 im=g.img(32,32);d=ImageDraw.Draw(im);step=(-2 if frame else 2)
 if kind==3:
  d.polygon([(2,13),(8,10),(20,10),(23,5),(27,8),(31,11),(29,16),(23,16),(19,23),(7,22)],fill=3,outline=1)
  d.polygon([(22,9),(23,3),(26,7)],fill=5);d.polygon([(23,8),(27,8),(29,11),(25,12)],fill=4)
  d.point((27,10),fill=11);d.line((26,14,29,14),fill=6)
  d.polygon([(7,13),(1,9),(0,17),(7,20)],fill=4)
  d.line((11,21,9+step,29),fill=4,width=3);d.line((21,20,23-step,29),fill=5,width=3)
  for x in (9+step,23-step):d.line((x-1,30,x+3,30),fill=6)
  d.line((8,12,19,12),fill=5)
  return im
 # Back foot and a skirt of articulated iron plates.
 d.line([(15,23),(13-step,27),(12-step,30)],fill=2,width=4)
 d.line((10-step,31,15-step,31),fill=4)
 d.line([(21,23),(23+step,27),(23+step,30)],fill=3,width=4)
 d.line((22+step,31,27+step,31),fill=5)
 d.polygon([(10,12),(22,12),(25,22),(22,26),(12,25),(8,22)],fill=2,outline=1)
 d.polygon([(12,14),(21,14),(23,20),(20,24),(12,23)],fill=3)
 d.line((16,14,16,23),fill=5);d.line((18,14,18,23),fill=12)
 d.line((11,21,22,21),fill=1);d.point((17,21),fill=13)
 for x in (11,14,20,23):d.line((x,23,x,25),fill=4)
 # Helmet with raised brow, dark visor and a luminous eye slit.
 d.polygon([(11,10),(10,5),(13,2),(20,1),(23,5),(23,10),(20,13),(13,13)],fill=3,outline=1)
 d.polygon([(12,5),(14,3),(20,2),(21,5)],fill=5)
 d.line((12,6,23,6),fill=6);d.line((12,8,22,8),fill=1,width=2)
 d.line((19,8,22,8),fill=11);d.line((12,11,21,11),fill=4)
 d.line((21,10,21,12),fill=5)
 d.polygon([(8,12),(12,12),(14,16),(8,17),(5,15)],fill=4,outline=1)
 d.line((7,13,11,13),fill=6)
 d.polygon([(22,12),(26,13),(28,16),(24,19),(22,16)],fill=4,outline=1)
 d.point((25,14),fill=6)
 if kind==0:
  d.line((28,6,28,29),fill=12);d.line((29,6,29,29),fill=5)
  d.polygon([(28,0),(25,6),(29,5),(31,8),(31,4)],fill=5,outline=6)
  d.rectangle((25,19,28,21),fill=8)
 elif kind==1:
  d.arc((22,9,34,29),95,265,fill=12,width=2);d.line((26,11,26,28),fill=13)
  d.line((19,18,28,18),fill=5);d.point((29,18),fill=6)
 else:
  d.polygon([(3,17),(11,16),(12,25),(7,30),(2,26)],fill=2,outline=12)
  d.line((7,18,7,27),fill=14);d.line((4,21,10,21),fill=5)
  d.line((28,12,28,27),fill=5);d.point((28,11),fill=6)
 return im

def apply():
 # Decode the existing native sheet, then replace reserved regions only.
 raw=(g.OUT/'sprites.chr').read_bytes();im=g.img(128,256)
 for t in range(512):
  for y in range(8):
   for x in range(8):
    v=sum(((raw[t*32+(p//2)*16+y*2+p%2]>>(7-x))&1)<<p for p in range(4))
    im.putpixel(((t%16)*8+x,(t//16)*8+y),v)
 for kind,base in enumerate((192,200,136,392)):
  for frame in range(2):
   tile=base+frame*4;im.paste(enemy(kind,frame),((tile%16)*8,(tile//16)*8))
 (g.OUT/'sprites.chr').write_bytes(g.planar(im))
 g.palimg(im,g.spal).resize((512,1024),g.Image.Resampling.NEAREST).save(g.OUT/'sprites-preview.png')
if __name__=='__main__':apply()
