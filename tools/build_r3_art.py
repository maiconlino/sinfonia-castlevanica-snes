#!/usr/bin/env python3
"""Original indexed SNES pixel artwork for R3. No commercial game assets."""
from pathlib import Path
import math,json
from PIL import Image,ImageDraw
import generate_graphics as g
R=Path(__file__).resolve().parents[1];O=R/'assets'
# Shared structural shadows and highlights, followed by each guardian's own accents.
hexp=[
['0a0c18','101421','252334','41414e','686375','9a939e','d3c4bb','ead4b3','402b21','77502c','ab763d','e2b75e','fff1b6','874742','cc7057','fff4dc'],
['080c19','101326','292139','453555','685783','a693bd','d6cee8','f2e8dd','212853','414182','626bac','a397d1','e4d7ff','457eae','72c7e5','f3ffff'],
['070f18','111b27','293446','485151','637577','a0ab9b','d4e0c6','f2ede0','143933','245b47','479366','83c787','cff5b2','583c74','b374b9','fff5fa'],
['070e1c','111d2a','26364c','3e5969','5f8090','8ba6b6','c9d8df','e0eddf','153f4e','206278','368ea2','75cbce','b1f7e7','5c4173','ac79ac','f1ffff'],
['100e19','181622','363443','5a5151','877573','b6a198','d9c6b3','ffe4bc','492727','85442b','c66632','ef993d','ffe39e','8e3042','e65244','fff4d5'],
['0a0d1c','111728','343647','575869','7a7e90','a9b3b9','dadaca','f2eddb','3e3624','6f5a34','a18548','d3b777','f6ebb4','335b99','709bdd','effcff'],
['080d1e','171a34','342b52','524774','7975a0','aaa8c9','dbddeb','f5e7dc','292854','534778','7974ab','b7a0df','ecdbff','477f9f','82d4e9','ffffff'],
['100b1e','19122d','31254c','51406b','795b88','ae94af','dbc4d7','f2e1db','4c1238','84264f','bc3d63','e887ac','ffd0e0','37677f','71e9ee','ffffff'],
['0e0b1a','191627','333048','535065','837e91','b3a7b6','ddd0d6','f5e7df','46162d','812645','af3b4c','e65e66','ffcba1','856038','dbb263','fffbe5'],
['090d1c','151a2a','32394d','535e73','7c849b','b3b9c9','dce4ec','f4e9df','263557','415983','6c95b9','a8d0df','eaffff','655582','aa9cce','ffffff']]
pals=[[g.rgb(x) for x in h] for h in hexp]
def canvas():
 im=Image.new('P',(64,64),0);return im,ImageDraw.Draw(im)
def star(d,x,y,r,c):
 d.line((x-r,y,x+r,y),fill=c);d.line((x,y-r,x,y+r),fill=c);d.point((x-1,y-1),fill=15)
def humanoid(d,x,y,robe=True):
 d.polygon([(x-8,y+16),(x-15,y+38),(x-18,y+48),(x+18,y+48),(x+10,y+21),(x+7,y+16)],fill=2,outline=4)
 for a in [-10,-6,0,6,11]:d.line((x+a//2,y+20,x+a,y+45),fill=3 if a%2 else 5)
 d.rectangle((x-4,y+6,x+5,y+15),fill=7);d.line((x-3,y+10,x+4,y+10),fill=1);d.point((x+3,y+10),fill=12)
 d.polygon([(x-8,y+9),(x-6,y),(x+6,y),(x+10,y+10),(x+8,y+28),(x+4,y+18),(x+5,y+5),(x-4,y+5),(x-5,y+20),(x-10,y+27)],fill=5,outline=6)
 d.line((x,y+18,x,y+35),fill=11);d.ellipse((x-2,y+27,x+2,y+31),fill=12)
def boss(i,f):
 im,d=canvas();bob=(0,-1,1,0)[f];pulse=12 if f in (1,2) else 11
 if i==0: # Bell/hammer knight with heavy bronze shoulders.
  x=31;y=9+bob
  d.polygon([(7,22),(12,16),(22,17),(39,17),(50,22),(49,53),(42,54),(38,44),(23,44),(17,57),(7,55)],fill=8,outline=10)
  d.polygon([(20,24),(43,24),(43,42),(37,48),(25,47),(18,40)],fill=9,outline=11)
  for k in [23,29,35,41]:d.line((k,27,k-1,41),fill=10)
  d.polygon([(21,13),(25,5),(37,5),(42,14)],fill=10,outline=12)
  d.rectangle((24,14,39,23),fill=3,outline=6);d.line((25,17,38,17),fill=1);d.line((32,17,37,17),fill=14)
  d.rectangle((20,46,27,60),fill=3,outline=5);d.rectangle((36,45,43,60),fill=4,outline=6)
  d.rectangle((17,58,28,62),fill=9,outline=11);d.rectangle((36,58,48,62),fill=9,outline=11)
  hy=8 if f==1 else (34 if f==2 else 20)
  d.line((52,hy,50,55),fill=10,width=3);d.rectangle((43,hy,62,hy+11),fill=9,outline=12)
  d.line((45,hy+2,59,hy+2),fill=11);d.line((47,hy+8,58,hy+8),fill=8)
 elif i==1: # Flying abbess with crown, scrolls and a wide veil.
  d.ellipse((12,0,49,37),outline=11);d.ellipse((15,3,46,34),outline=9)
  humanoid(d,31,9+bob)
  d.polygon([(18,22),(6,35),(2,52),(13,46),(18,60),(28,57),(31,34)],fill=8,outline=11)
  d.polygon([(43,21),(58,35),(62,50),(53,47),(47,61),(35,56),(32,35)],fill=8,outline=11)
  for x,y in [(4,22),(49,21),(6,53),(50,48)]:
   yy=y+(f%2)*2;d.rectangle((x,yy,x+9,yy+6),fill=7,outline=10);d.line((x+2,yy+2,x+7,yy+2),fill=9)
  d.polygon([(23,9),(23,2),(29,7),(31,0),(34,7),(40,2),(39,9)],fill=10,outline=12)
 elif i==2: # Glass tree, antlers, different silhouette and crystal-heart.
  for x,y in [(2,4),(11,1),(21,5),(44,1),(57,5),(63,17)]:
   d.line((31,32,x,y),fill=9,width=3);d.line((31,32,x,y),fill=11)
   d.polygon([(x,y),(min(63,x+7),y+3),(min(63,x+3),y+9)],fill=10,outline=12)
  d.polygon([(26,19),(37,19),(42,38),(50,54),(59,61),(42,57),(36,63),(28,55),(15,62),(5,60),(22,48)],fill=8,outline=10)
  for x in [26,30,34,38]:d.line((x,25,x-4,54),fill=11 if x==30 else 9)
  d.polygon([(32,24),(39,35),(32,46),(25,35)],fill=13,outline=14);d.line((32,27,32,42),fill=pulse)
  d.line((24,21,39,21),fill=1);d.point((28,22),fill=15);d.point((36,22),fill=15)
 elif i==3: # Long articulated serpent, fins, large jaw.
  points=[(6,52),(15,51),(22,43),(19,32),(25,21),(37,19),(45,27)]
  for n,(x,y) in enumerate(points):
   yy=y+(1 if (f+n)%3==0 else 0)
   d.ellipse((x-7,yy-7,x+7,yy+7),fill=8+n%3,outline=11)
   d.arc((x-5,yy-5,x+5,yy+5),50,270,fill=12)
   d.polygon([(x-2,yy-6),(x,yy-14),(x+4,yy-7)],fill=9,outline=11)
  d.polygon([(39,22),(46,15),(59,17),(63,24),(60,31),(47,35),(37,28)],fill=10,outline=12)
  d.polygon([(47,29),(61,25),(61,32),(52,37),(44,35)],fill=3,outline=11)
  for x in [50,55,60]:d.line((x,29,x,33),fill=15)
  d.rectangle((51,21,55,23),fill=14);d.point((54,21),fill=15)
 elif i==4: # Furnace golem, industrial stacks and exposed glowing vents.
  for x in [10,44]:d.rectangle((x,4,x+8,32),fill=3,outline=5);d.line((x+2,5,x+2,25),fill=6)
  d.polygon([(13,23),(49,23),(55,37),(51,52),(14,53),(8,40)],fill=3,outline=6)
  d.rectangle((18,28,45,48),fill=8,outline=10)
  for y in [31,36,41]:d.rectangle((21,y,42,y+2),fill=pulse);d.line((25,y,25,y+2),fill=8)
  d.rectangle((23,12,40,24),fill=4,outline=6);d.line((25,18,38,18),fill=14)
  for x in [16,40]:d.rectangle((x,50,x+9,62),fill=3,outline=5);d.rectangle((x-3,60,x+11,63),fill=4)
  hx=0 if f!=2 else 45;hy=29 if f!=1 else 8
  d.rectangle((hx,hy,hx+16,hy+13),fill=9,outline=11);d.line((hx+8,hy+10,11 if hx==0 else 48,52),fill=5,width=3)
  for x in [13,47]:star(d,x,7,2,14)
 elif i==5: # Clock automaton, not a humanoid recolor.
  g.gear(d,31,30,27,10);d.ellipse((11,10,51,50),fill=2,outline=11);d.ellipse((15,14,47,46),fill=8,outline=12)
  for a in range(12):
   x=round(31+math.sin(a*math.pi/6)*16);y=round(30-math.cos(a*math.pi/6)*16);d.rectangle((x,y,x+1,y+1),fill=12)
  a=(f*0.55);d.line((31,30,round(31+math.sin(a)*13),round(30-math.cos(a)*13)),fill=7,width=2)
  d.line((31,30,42,36),fill=14,width=2);d.ellipse((28,27,34,33),fill=15)
  d.line((31,49,31+(f-1)*4,59),fill=11,width=2);d.ellipse((25+(f-1)*4,55,37+(f-1)*4,63),fill=9,outline=12)
 elif i==6: # Astronomer, astrolabe, star mantle.
  d.ellipse((8,2,53,49),outline=10);d.arc((4,13,59,36),5,355,fill=11)
  humanoid(d,31,8+bob)
  for x,y in [(6,12),(53,8),(8,39),(55,44),(16,55),(46,57)]:star(d,x,y,3,12)
  d.line((56,15,52,61),fill=10,width=2);d.ellipse((48,7,61,20),fill=8,outline=11);star(d,55,13,4,15)
  for x,y in [(22,40),(35,47),(26,54),(41,37)]:d.point((x,y),fill=12)
 elif i==7: # Regent: mechanical throne/core, symmetric fan of circuits.
  for x in [4,12,20,44,52,60]:
   d.line((x,59,x,24,x+(5 if x<32 else -5),15),fill=9,width=2);d.rectangle((x-2,52,x+2,62),fill=3,outline=10)
  d.polygon([(22,14),(41,14),(46,30),(41,54),(23,54),(17,30)],fill=2,outline=11)
  d.polygon([(31,21),(43,35),(32,49),(20,35)],fill=9,outline=12);d.polygon([(32,27),(37,35),(32,42),(27,35)],fill=14,outline=15)
  d.polygon([(20,5),(25,9),(30,0),(35,9),(42,4),(40,16),(22,16)],fill=10,outline=12)
  d.line((27,19,37,19),fill=14)
  for y in range(26,50,7):d.line((5,y,16,y+4),fill=13);d.line((59,y,47,y+4),fill=13)
 elif i==8: # Lean duellist with long swept greatsword and ember cloak.
  humanoid(d,27,10+bob)
  d.polygon([(18,21),(8,36),(1,62),(19,54),(29,57),(21,35)],fill=8,outline=10)
  d.rectangle((22,50,28,62),fill=3);d.rectangle((35,49,40,62),fill=4);d.line((21,62,29,62),fill=6);d.line((34,62,44,62),fill=6)
  if f==1:d.line((40,38,54,3),fill=6,width=3);d.line((42,33,53,5),fill=12)
  elif f==2:d.line((37,34,63,30),fill=6,width=3);d.line((40,34,63,30),fill=12)
  else:d.line((40,46,52,16),fill=6,width=3);d.line((43,40,51,18),fill=12)
  d.line((34,42,46,47),fill=11,width=2)
 elif i==9: # Ownerless sword, very tall blade and spectral echoes.
  d.ellipse((5,4,57,57),outline=9);d.ellipse((9,8,53,53),outline=4)
  for x in [9,50]:
   d.polygon([(x,17),(x+3,23),(x+2,44),(x-1,44),(x-2,23)],fill=3,outline=5)
   d.line((x-5,43,x+6,43),fill=9)
  d.polygon([(31,0),(37,12),(34,44),(28,44),(25,12)],fill=5,outline=12)
  d.polygon([(31,3),(33,12),(31,41),(29,12)],fill=15)
  d.polygon([(18,42),(24,39),(31,43),(40,39),(45,42),(39,47),(24,47)],fill=10,outline=12)
  d.rectangle((29,47,33,58),fill=9,outline=11);d.ellipse((27,56,35,63),fill=10,outline=12)
  for x,y in [(7,6),(55,58),(45,2)]:star(d,x,y,2,12)
 if f==1: # bright anticipation, still same silhouette.
  for x,y in [(6,5),(56,10),(5,58)]:star(d,x,y,2,14)
 return im
# Produce bank-local 4-frame guardians. 64x64 frame = 2048 native bytes.
board=Image.new('RGB',(64*5,64*2),(8,10,22))
for i in range(10):
 frames=[boss(i,f) for f in range(4)]
 (O/f'boss{i}-frames.chr').write_bytes(b''.join(g.planar(im) for im in frames))
 sheet=Image.new('RGB',(256,64))
 for f,im in enumerate(frames):sheet.paste(g.palimg(im,pals[i]),(f*64,0))
 sheet.save(O/f'boss{i}-poses.png');board.paste(sheet.crop((0,0,64,64)),((i%5)*64,(i//5)*64))
(O/'boss-palettes.pal').write_bytes(b''.join(g.cgram(p) for p in pals));board.resize((960,384),Image.Resampling.NEAREST).save(O/'bosses-r3-preview.png')
# Recover indexed OBJ sheet from the regular generator, replace enemy strip and hazards.
def decode(raw,w,h):
 im=Image.new('P',(w,h),0);k=0
 for ty in range(0,h,8):
  for tx in range(0,w,8):
   t=raw[k:k+32];k+=32
   for y in range(8):
    for x in range(8):im.putpixel((tx+x,ty+y),sum(((t[(p//2)*16+y*2+p%2]>>(7-x))&1)<<p for p in range(4)))
 return im
sheet=decode((O/'sprites.chr').read_bytes(),128,256)
sheet.paste(0,(0,96,128,128))
for kind,j in [('guard',0),('archer',1),('sentinel',2)]:
 for f in range(2):
  im=g.enemy(kind);dr=ImageDraw.Draw(im);dr.rectangle((0,24,15,31),fill=0)
  # Separate alternating feet, knees and boot highlights.
  if not f:
   dr.line((5,24,3,28,1,30),fill=4,width=2);dr.line((10,24,12,27,13,30),fill=5,width=2);dr.line((0,31,4,31),fill=6);dr.line((11,31,15,31),fill=6)
  else:
   dr.line((5,24,8,28,10,30),fill=4,width=2);dr.line((10,24,7,27,5,30),fill=5,width=2);dr.line((9,31,13,31),fill=6);dr.line((3,31,7,31),fill=6)
  sheet.paste(im,(j*32+f*16,96))
# Eight 16x16 readable attack types, located outside dynamically streamed boss tiles.
for k in range(8):
 im=Image.new('P',(16,16),0);dr=ImageDraw.Draw(im)
 if k==0:
  dr.arc((-2,2,15,22),190,350,fill=12,width=3);dr.arc((1,5,14,20),190,350,fill=15,width=2)
 elif k==1:
  dr.polygon([(2,3),(10,1),(14,11),(5,14)],fill=7,outline=13)
  for y in [5,8,11]:dr.line((5,y,10,y-1),fill=9)
 elif k==2:
  dr.polygon([(3,15),(5,3),(8,8),(12,0),(13,15)],fill=14,outline=5);dr.line((7,15,9,5),fill=15)
 elif k==3:
  dr.ellipse((1,4,14,12),fill=14,outline=15);dr.line((3,7,12,7),fill=6)
 elif k==4:
  dr.polygon([(2,13),(6,5),(8,0),(14,10),(12,15),(5,15)],fill=11,outline=12);dr.ellipse((6,8,11,14),fill=15)
 elif k==5:g.gear(dr,8,8,7,12)
 elif k==6:star(dr,8,8,7,15);dr.ellipse((5,5,10,10),fill=14)
 elif k==7:
  dr.line((1,14,14,1),fill=15,width=2);dr.line((3,15,15,3),fill=14);dr.line((2,9,7,14),fill=12)
 sheet.paste(im,(k*16,192))
(O/'sprites.chr').write_bytes(g.planar(sheet))
# Open arch, no door leaves. Preserve the complete 20-tile matrix across regions.
arch=Image.new('P',(32,40),0);ad=ImageDraw.Draw(arch)
ad.polygon([(0,39),(0,13),(16,0),(31,13),(31,39)],fill=3,outline=5)
ad.polygon([(4,39),(4,15),(16,5),(27,15),(27,39)],fill=1,outline=10)
ad.line((7,38,7,17,16,9,24,17,24,38),fill=14)
for y in [19,27,35]:ad.line((0,y,4,y),fill=5);ad.line((27,y,31,y),fill=5)
archdata=g.planar(arch)
for r in range(8):
 p=O/f'bg_region{r}.chr';raw=bytearray(p.read_bytes());raw[128*32:148*32]=archdata;p.write_bytes(raw)
p=O/'bg_common.chr';raw=bytearray(p.read_bytes());raw[128*32:148*32]=archdata;p.write_bytes(raw)
print('R3 art: 10 distinct guardians x 4 poses, 6 terrestrial poses, 8 hazard designs, open arches.')
