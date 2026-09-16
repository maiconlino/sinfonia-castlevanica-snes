#!/usr/bin/env python3
"""Original SNES 4bpp art for SinfonIA. Pillow only, fully reproducible.
Tile/VRAM formats follow SNES PPU native planar bitplanes, LE BGR555 CGRAM.
All pixel art is authored in code below. No commercial assets or ROM content.
"""
from PIL import Image, ImageDraw
from pathlib import Path
import math, random, json, struct
OUT=Path(__file__).resolve().parents[1]/'assets'; OUT.mkdir(exist_ok=True)

def rgb(s): return tuple(bytes.fromhex(s))
# Every region keeps functional colors at stable indices. Palettes 0..7 are interchangeable.
base=['070916','0d1125','191a32','28243e','3c354d','685b71','1b425a','39758b','29202b','684735','b68d56','d5b5a4','a83862','7881b1','65d7db','f2e4c7']
regions=[
 ('castle','CASTELO DE VESPERA',{}),
 ('library','BIBLIOTECA', {1:'150e24',2:'281935',3:'3d2546',4:'654365',5:'92748d',6:'362850',7:'725298',14:'c394ef'}),
 ('gardens','JARDINS LUNARES',{1:'081b22',2:'162c30',3:'294239',4:'3b5a4e',5:'719287',6:'243e48',7:'4a868c',14:'99eac4',12:'d271a4'}),
 ('subsoil','SUBSOLO DAS VOZES',{1:'071820',2:'11272e',3:'1e3a43',4:'365a61',5:'678f92',6:'0e3e50',7:'176c83',14:'7fe3e1'}),
 ('forge','FORJA DE CINZAS',{1:'180e18',2:'2b1a24',3:'42242b',4:'674136',5:'9b7251',6:'4c251e',7:'995035',14:'ffbc69',12:'df6745'}),
 ('clockwork','TORRE DOS RELOGIOS',{1:'0b1222',2:'202430',3:'3a3540',4:'645741',5:'9d8757',6:'204b62',7:'447c98',14:'8bdbea'}),
 ('observatory','ULTIMO CEU',{1:'100d2b',2:'20183a',3:'34284e',4:'574367',5:'8b7e9e',6:'273b67',7:'5768a0',14:'b0cafa'}),
 ('core','CORACAO DA MAQUINA',{1:'170a1b',2:'291227',3:'451e38',4:'71334d',5:'a76379',6:'352544',7:'806087',14:'f3a6c8',12:'df3e66'}),
]
palettes=[]
for _,_,over in regions:
 p=[rgb(v) for v in base]
 for k,v in over.items():p[k]=rgb(v)
 palettes.append(p)
spal=[rgb(v) for v in ['000000','101023','292336','54465f','8a819d','bab8d1','f1edeb','efd0b5','a87b6f','401531','842344','d54f6d','a98549','ead59b','65d4e3','e5ffff']]
FONT={
'A':[14,17,17,31,17,17,17],'B':[30,17,17,30,17,17,30],'C':[14,17,16,16,16,17,14],'D':[30,17,17,17,17,17,30],
'E':[31,16,16,30,16,16,31],'F':[31,16,16,30,16,16,16],'G':[14,17,16,23,17,17,15],'H':[17,17,17,31,17,17,17],
'I':[14,4,4,4,4,4,14],'J':[7,2,2,2,2,18,12],'K':[17,18,20,24,20,18,17],'L':[16,16,16,16,16,16,31],
'M':[17,27,21,21,17,17,17],'N':[17,25,21,19,17,17,17],'O':[14,17,17,17,17,17,14],'P':[30,17,17,30,16,16,16],
'Q':[14,17,17,17,21,18,13],'R':[30,17,17,30,20,18,17],'S':[15,16,16,14,1,1,30],'T':[31,4,4,4,4,4,4],
'U':[17,17,17,17,17,17,14],'V':[17,17,17,17,17,10,4],'W':[17,17,17,21,21,21,10],'X':[17,17,10,4,10,17,17],
'Y':[17,17,10,4,4,4,4],'Z':[31,1,2,4,8,16,31],
'0':[14,17,19,21,25,17,14],'1':[4,12,4,4,4,4,14],'2':[14,17,1,2,4,8,31],'3':[30,1,1,14,1,1,30],
'4':[2,6,10,18,31,2,2],'5':[31,16,16,30,1,1,30],'6':[14,16,16,30,17,17,14],'7':[31,1,2,4,8,8,8],
'8':[14,17,17,14,17,17,14],'9':[14,17,17,15,1,1,14],
'!':[4,4,4,4,4,0,4],'?':[14,17,1,2,4,0,4],'.':[0,0,0,0,0,0,4],',':[0,0,0,0,0,4,8],':':[0,4,0,0,4,0,0],
';':[0,4,0,0,4,4,8],'-':[0,0,0,31,0,0,0],'+':[0,4,4,31,4,4,0],'/':[1,1,2,4,8,16,16],
'=':[0,0,31,0,31,0,0],'(':[2,4,8,8,8,4,2],')':[8,4,2,2,2,4,8],'[':[14,8,8,8,8,8,14],']':[14,2,2,2,2,2,14],
'<':[2,4,8,16,8,4,2],'>':[8,4,2,1,2,4,8],"'":[4,4,8,0,0,0,0],'"':[10,10,10,0,0,0,0],'*':[0,21,14,31,14,21,0],
'%':[17,2,4,8,16,17,0],'#':[10,31,10,10,31,10,0],'_':[0,0,0,0,0,0,31],'|':[4]*7,'@':[14,17,23,21,23,16,14],
'&':[12,18,20,8,21,18,13],'$':[4,15,20,14,5,30,4],'^':[4,10,17,0,0,0,0],'~':[0,0,9,22,0,0,0],'\\':[16,16,8,4,2,1,1],
}
def img(w,h):return Image.new('P',(w,h),0)
def palimg(im,p):
 im=im.copy(); im.putpalette(sum((list(c) for c in p),[])+[0]*720);return im.convert('RGB')
def tilefont(c):
 im=img(8,8)
 for y,bits in enumerate(FONT.get(c.upper(),[])):
  for x in range(5):
   if bits&(1<<(4-x)): im.putpixel((x+1,y),15)
 return im

def common_tiles():
 tiles=[tilefont(chr(i)) for i in range(32,128)]
 for i in range(32):
  im=img(8,8);d=ImageDraw.Draw(im)
  if i in [0,1,2,3]:
   d.rectangle((0,0,7,7),fill=2 if i==3 else 3)
   d.line((0,0,7,0),fill=5 if i==1 else 4)
   d.line((0,7,7,7),fill=1);d.line((7,1,7,6),fill=1)
   if i==1:d.line((0,1,7,1),fill=10)
   if i in [0,3]:d.line((3,1,3,6),fill=2)
  elif i in [4,5]:
   d.rectangle((1,0,6,7),fill=4);d.line((2,0,2,7),fill=5);d.line((5,0,5,7),fill=2)
  elif i in [6,7]:d.polygon([(0,7),(0,0),(7,0)],fill=4);d.line((1,7,7,1),fill=5)
  elif i==8:d.rectangle((2,0,5,7),fill=6);d.line((3,0,3,7),fill=14)
  elif i==9:
   d.rectangle((0,0,7,7),fill=1);d.line((1,0,1,7),fill=5);d.line((5,0,5,7),fill=5);d.line((0,4,7,4),fill=4)
  elif i==10:d.polygon([(0,7),(3,0),(6,7)],fill=5);d.line((3,1,3,6),fill=15)
  elif i in [11,12]:
   d.rectangle((1,0,6,7),fill=9 if i==11 else 6);d.line((1,0,6,0),fill=10);d.point((5,4),fill=10 if i==11 else 14)
  elif i==13:d.rectangle((3,3,4,6),fill=15);d.point((3,2),fill=10);d.point((3,1),fill=12);d.line((1,7,6,7),fill=10)
  elif i==14:d.polygon([(3,0),(6,3),(3,6),(0,3)],fill=7,outline=14);d.line((0,7,7,7),fill=5)
  elif i==15:d.ellipse((1,0,6,7),fill=10,outline=15);d.line((3,2,3,5),fill=9)
  elif i==16:d.rectangle((0,2,7,7),fill=9,outline=10);d.rectangle((3,3,4,5),fill=15)
  elif i==17:d.line((6,0,1,5),fill=15,width=2);d.line((0,4,3,7),fill=10);d.point((0,7),fill=9)
  elif i==18:d.polygon([(0,1),(2,0),(4,2),(6,0),(7,1),(7,3),(4,7),(0,3)],fill=12);d.line((1,1,2,1),fill=15)
  elif i==19:d.polygon([(2,0),(5,0),(5,2),(6,4),(6,7),(1,7),(1,4),(2,2)],fill=7,outline=14)
  elif i==20:d.ellipse((0,0,4,4),outline=10);d.line((3,3,7,7),fill=10);d.line((5,6,6,5),fill=15)
  elif i==21:d.rectangle((2,2,5,5),fill=14)
  elif i in [22,23]:d.rectangle((0,1,7,6),fill=12 if i==22 else 3);d.line((0,1,7,1),fill=15 if i==22 else 4)
  elif i==24:
   d.rectangle((0,3,7,7),fill=3);d.line((0,3,7,3),fill=7)
   for x in [1,3,6]:d.line((x,1,x,4),fill=14)
  elif i==25:d.rectangle((0,2,7,7),fill=6);d.line((0,2,7,2),fill=14);d.line((2,5,5,5),fill=7)
  elif i==26:d.ellipse((0,0,7,7),fill=10,outline=5);d.ellipse((2,2,5,5),fill=2);d.line((0,3,7,3),fill=4)
  elif i==27:d.polygon([(3,0),(6,3),(3,7),(0,3)],fill=13,outline=15)
  elif i==28:
   d.line((1,0,1,7),fill=10);d.line((6,0,6,7),fill=10)
   for y in [1,4,7]:d.line((1,y,6,y),fill=9)
  elif i==29:d.line((0,0,7,7),fill=12);d.line((7,0,0,7),fill=12)
  elif i==30:d.rectangle((0,0,7,7),fill=3);d.line((4,0,2,3,5,5,4,7),fill=1)
  else:d.rectangle((0,0,7,7),fill=6);d.line((3,0,3,7),fill=10);d.line((0,4,7,4),fill=10)
  tiles.append(im)
 return tiles

def gear(d,cx,cy,r,fill=10):
 pts=[]
 for a in range(48):
  rad=r if a%4 in (0,3) else r-3
  pts.append((round(cx+math.cos(a*math.pi/24)*rad),round(cy+math.sin(a*math.pi/24)*rad)))
 d.polygon(pts,fill=fill,outline=5);d.ellipse((cx-r+5,cy-r+5,cx+r-5,cy+r-5),fill=2,outline=4)
 for a in range(0,360,60):
  ex=round(cx+math.cos(math.radians(a))*(r-6));ey=round(cy+math.sin(math.radians(a))*(r-6));d.line((cx,cy,ex,ey),fill=4,width=2)
 d.ellipse((cx-3,cy-3,cx+3,cy+3),fill=10)

def background(region):
 im=img(256,224);d=ImageDraw.Draw(im);rng=random.Random(123+region)
 d.rectangle((0,0,255,223),fill=1)
 # Jointed medieval masonry with subtle texture.
 for y in range(16,224,16):
  d.line((0,y,255,y),fill=2)
  for x in range(-(16 if (y//16)%2 else 0),256,32):
   d.line((x,y,x,y+15),fill=2)
   if rng.random()<.36:d.line((x+9,y+11,x+15,y+11),fill=2)
 # Broad pointed windows, carved pilasters and distant night.
 for wx in [24,104,184]:
  pts=[(wx,176),(wx,77),(wx+24,43),(wx+48,77),(wx+48,176)]
  d.polygon(pts,fill=0,outline=4)
  d.line([(wx+3,175),(wx+3,78),(wx+24,49),(wx+45,78),(wx+45,175)],fill=3,width=2)
  d.polygon([(wx+6,174),(wx+6,83),(wx+24,57),(wx+42,83),(wx+42,174)],fill=6)
  for i in range(22):
   x=wx+rng.randrange(7,42);y=rng.randrange(86,167);d.point((x,y),fill=7)
  d.ellipse((wx+10,80,wx+33,103),fill=13);d.ellipse((wx+16,77,wx+36,98),fill=6)
  for bx in range(wx+7,wx+43,7):
   h=rng.randrange(6,23);d.rectangle((bx,173-h,bx+5,173),fill=1)
  d.line((wx+24,60,wx+24,176),fill=4,width=2)
  d.line((wx+6,113,wx+42,113),fill=3,width=2)
  d.line((wx+6,146,wx+42,146),fill=3,width=2)
 for x in [7,87,167,247]:
  d.rectangle((x-5,31,x+5,196),fill=3);d.line((x-3,32,x-3,196),fill=5);d.line((x+3,32,x+3,196),fill=2)
  for y in [32,35,185,190]:d.rectangle((x-7,y,x+7,y+2),fill=4)
 # Region signature.
 if region==1:
  for x in [23,102,181]:
   d.rectangle((x,72,x+49,185),fill=8,outline=10)
   for y in [93,115,137,159,181]:
    for bx in range(x+3,x+47,5):
     h=rng.randrange(10,19);c=rng.choice([3,5,9,10,12,13]);d.rectangle((bx,y-h,bx+3,y-1),fill=c);d.point((bx+1,y-h+3),fill=15 if c==10 else 10)
    d.line((x+1,y,x+48,y),fill=10)
 elif region==2:
  for x in [12,72,92,156,172,240]:
   pts=[(x,187),(x-5,163),(x+3,143),(x-2,119),(x+5,92),(x+2,60)];d.line(pts,fill=7,width=2)
   for y in range(71,183,16):
    d.polygon([(x,y),(x-8,y-6),(x-7,y+1)],fill=4);d.polygon([(x,y+7),(x+9,y+2),(x+6,y+10)],fill=7)
    if y%3==0:d.ellipse((x-2,y-3,x+2,y+1),fill=12)
  for _ in range(20):d.point((rng.randrange(256),rng.randrange(55,190)),fill=14)
 elif region==3:
  for x in [15,75,178,238]:
   d.rectangle((x,45,x+7,190),fill=3,outline=5);d.line((x+2,49,x+2,187),fill=7)
   for y in [69,119,168]:d.rectangle((x-2,y,x+9,y+4),fill=4)
  d.rectangle((0,188,255,223),fill=6)
  for y in range(190,224,5):
   for x in range((y*3)%19,256,31):d.line((x,y,x+16,y),fill=7 if y%2 else 14)
 elif region==4:
  for x in [30,109,188]:
   d.polygon([(x,170),(x,98),(x+17,81),(x+34,98),(x+34,170)],fill=2,outline=5)
   d.rectangle((x+4,111,x+30,168),fill=12)
   for i in range(12):
    fx=x+rng.randrange(5,29);h=rng.randrange(8,43);d.polygon([(fx-2,166),(fx,166-h),(fx+3,166)],fill=14 if i%2 else 10)
   for gx in range(x+4,x+31,6):d.line((gx,109,gx,170),fill=3,width=2)
  for x in [64,145,224]:
   d.rectangle((x,45,x+9,89),fill=4,outline=5);d.rectangle((x-5,82,x+14,92),fill=3,outline=5)
 elif region==5:
  gear(d,51,120,32);gear(d,203,111,30);gear(d,94,70,16);gear(d,161,167,19)
  d.ellipse((97,86,157,146),fill=8,outline=10);d.ellipse((102,91,152,141),fill=2,outline=5)
  for a in range(12):
   x=round(127+math.sin(a*math.pi/6)*22);y=round(116-math.cos(a*math.pi/6)*22);d.rectangle((x,y,x+1,y+1),fill=15)
  d.line((127,97,127,116,141,123),fill=15,width=2)
  for x in [78,179]:d.line((x,32,x,180),fill=5);d.ellipse((x-3,167,x+3,178),fill=10)
 elif region==6:
  d.rectangle((23,62,232,163),fill=0,outline=4)
  for i in range(72):
   x=rng.randrange(27,229);y=rng.randrange(66,161);d.point((x,y),fill=15 if i%5==0 else 7)
  d.ellipse((106,80,151,125),fill=6,outline=13);d.arc((93,87,165,114),0,340,fill=10,width=2)
  d.line((100,184,125,152,150,184),fill=5,width=3);d.line((125,152,159,119),fill=4,width=8);d.line((127,149,161,116),fill=13,width=2)
  d.line((82,56,82,164),fill=4);d.line((174,56,174,164),fill=4)
 elif region==7:
  for x in [24,48,72,184,208,232]:
   y=rng.randrange(80,145);d.line((x,39,x,y,x+8,y+8,x+8,187),fill=7);d.rectangle((x-1,y-1,x+1,y+1),fill=14)
  d.polygon([(99,185),(99,89),(112,72),(112,62),(143,62),(143,72),(156,89),(156,185)],fill=2,outline=5)
  d.polygon([(110,169),(110,97),(128,78),(145,97),(145,169)],fill=9,outline=12)
  d.polygon([(128,103),(138,123),(128,147),(118,123)],fill=12,outline=14)
  d.rectangle((105,170,151,178),fill=4);d.rectangle((93,179,162,184),fill=5)
 # Gothic cornice, lamps, and thin circuitry preserved in every environment.
 d.rectangle((0,25,255,28),fill=3);d.line((0,26,255,26),fill=5)
 for x in range(0,256,16):d.polygon([(x,28),(x+8,37),(x+16,28)],fill=3,outline=4)
 for x in [15,95,175,239]:
  d.line((x,148,x+8,148,x+8,140),fill=10);d.rectangle((x+7,135,x+9,139),fill=15);d.point((x+8,133),fill=12)
 d.rectangle((0,197,255,223),fill=2)
 for y in [199,215]:
  d.line((0,y,255,y),fill=3)
  for x in range(0,256,32):d.line((x+(16 if y==215 else 0),y,x+(16 if y==215 else 0),y+15),fill=1)
 # Clear HUD rows. Actual UI is drawn by game over the returned tilemap.
 d.rectangle((0,0,255,23),fill=0);d.line((0,23,255,23),fill=4)
 return im

def hero(frame):
 im=img(16,32);d=ImageDraw.Draw(im);step=[0,-2,0,2,0,0,1,0][frame]
 d.polygon([(5,9),(3,14),(0,26),(4,27),(8,20),(10,11)],fill=9)
 d.polygon([(4,13),(1,25),(4,24),(7,16)],fill=10);d.line((2,23,3,18),fill=11)
 d.rectangle((6-step,23,8-step,29),fill=1);d.rectangle((5-step,29,9-step,30),fill=4)
 d.rectangle((9+step,23,11+step,28),fill=2);d.rectangle((9+step,29,13+step,30),fill=5)
 d.polygon([(6,10),(11,10),(13,16),(11,21),(12,25),(5,24),(6,19)],fill=2)
 d.line((7,12,7,23),fill=5);d.line((9,12,9,22),fill=12);d.rectangle((5,20,12,21),fill=1);d.point((9,20),fill=13)
 d.rectangle((7,4,11,9),fill=7);d.point((11,6),fill=1);d.point((12,7),fill=8)
 d.polygon([(5,3),(8,1),(12,2),(13,4),(9,4),(7,8),(6,13),(3,16),(4,10),(4,5)],fill=4)
 d.line((5,5,6,3,10,2,12,3),fill=6);d.line((6,5,5,12,4,13),fill=5)
 if frame in [4,5]:
  d.rectangle((11,11,13,13),fill=5);d.rectangle((13,12,15,14),fill=7)
 else:
  d.rectangle((11,12,13,17),fill=4);d.rectangle((12,17,14,19),fill=7);d.line((13,20,15,25),fill=5);d.point((14,21),fill=15)
 if frame==7:
  im=im.rotate(90,expand=False)
 return im

def wolf(frame=0):
 im=img(32,16);d=ImageDraw.Draw(im)
 d.polygon([(4,6),(11,3),(20,4),(23,1),(27,4),(31,6),(29,9),(23,9),(19,12),(6,12)],fill=4,outline=5)
 d.polygon([(23,4),(23,0),(26,3)],fill=5);d.polygon([(5,7),(0,2),(1,8),(6,11)],fill=4)
 d.rectangle((27,4,28,5),fill=15);d.line((8,10,6+frame*2,15),fill=5,width=2);d.line((21,9,22-frame*2,15),fill=5,width=2)
 return im

def bat(frame=0):
 im=img(32,16);d=ImageDraw.Draw(im)
 wing=1 if frame==0 else 8
 d.polygon([(14,8),(8,wing),(1,wing-1 if wing else 0),(3,10),(8,8),(12,13)],fill=9,outline=13)
 d.polygon([(17,8),(23,wing),(30,wing-1),(28,10),(23,8),(19,13)],fill=9,outline=13)
 d.ellipse((13,5,18,13),fill=4);d.polygon([(13,7),(13,2),(16,6),(18,2),(18,8)],fill=4);d.point((14,7),fill=11);d.point((17,7),fill=11)
 return im

def mist(frame=0):
 im=img(32,32);d=ImageDraw.Draw(im)
 for i in range(17):
  a=i*.74+frame*.5;x=round(14+math.cos(a)*11);y=round(13+math.sin(a*1.4)*11)
  d.rectangle((x,y,x+4+i%3,y+1),fill=[3,5,14,4][i%4])
 return im

def enemy(kind):
 im=img(16,32);d=ImageDraw.Draw(im)
 if kind=='wisp':
  d.polygon([(8,5),(13,11),(11,18),(8,25),(4,18),(2,12)],fill=13,outline=14);d.ellipse((5,10,10,17),fill=15);return im
 if kind=='beast':
  w=wolf(0);im.paste(w.crop((8,0,24,16)),(0,16));return im
 d.rectangle((4,7,11,12),fill=4);d.polygon([(4,7),(5,3),(10,2),(12,7)],fill=5)
 d.line((4,9,11,9),fill=1);d.point((10,9),fill=11)
 d.polygon([(4,12),(11,12),(14,19),(11,25),(4,24),(2,18)],fill=3,outline=5)
 d.line((7,13,7,23),fill=12);d.rectangle((4,24,6,30),fill=3);d.rectangle((9,24,11,30),fill=4)
 d.line((3,30,6,30),fill=5);d.line((9,30,13,30),fill=5)
 if kind=='archer':d.arc((9,11,18,26),270,90,fill=12);d.line((14,12,14,25),fill=13)
 elif kind=='sentinel':d.rectangle((0,16,5,26),fill=2,outline=12);d.line((2,17,2,24),fill=14)
 else:d.line((14,8,14,26),fill=5);d.polygon([(14,4),(12,9),(15,9)],fill=15)
 return im

def boss(idx):
 im=img(32,32);d=ImageDraw.Draw(im)
 if idx in [0,4,8]:
  d.polygon([(8,9),(4,15),(3,27),(10,27),(13,22),(22,24),(29,28),(28,13),(22,8)],fill=9,outline=12)
  d.rectangle((11,7,21,16),fill=4);d.polygon([(10,7),(13,2),(21,2),(24,8)],fill=5,outline=12)
  d.line((11,10,21,10),fill=1);d.line((17,10,20,10),fill=11)
  d.polygon([(11,15),(22,15),(24,24),(19,26),(10,25)],fill=3,outline=5);d.line((16,16,16,25),fill=12)
  d.rectangle((10,25,14,30),fill=4);d.rectangle((20,25,24,30),fill=5)
  d.line((28,9,28,28),fill=12,width=2);d.polygon([(27,2),(24,8),(31,8)],fill=15)
 elif idx==3:
  for i in range(5):
   x=4+i*5;y=20-round(math.sin(i*.8)*8);d.ellipse((x-4,y-4,x+4,y+4),fill=3+i%3,outline=14)
  d.polygon([(23,7),(28,5),(31,9),(30,13),(24,15),(19,12)],fill=5,outline=14);d.point((28,8),fill=11);d.line((29,12,31,12),fill=15)
 elif idx==9:
  d.ellipse((2,2,29,29),outline=4);d.ellipse((5,5,26,26),outline=13)
  d.polygon([(16,0),(19,7),(17,21),(14,21),(13,7)],fill=5,outline=15)
  d.line((9,21,22,21),fill=12,width=2);d.line((15,22,15,30),fill=12,width=2);d.point((15,31),fill=13)
 else:
  # Distinct silhouettes: abbess veil, thorn queen, clock oracle, astronomer, regent.
  d.polygon([(12,9),(7,12),(3,27),(10,25),(16,30),(22,25),(29,27),(25,12),(21,9)],fill=9,outline=13)
  d.polygon([(13,10),(19,10),(22,21),(25,28),(7,28),(11,21)],fill=3,outline=5)
  d.rectangle((13,5,19,11),fill=7);d.line((14,8,18,8),fill=1);d.point((17,8),fill=11)
  d.polygon([(10,7),(12,2),(20,2),(23,7),(21,17),(19,10),(20,6),(12,6),(13,10),(10,17)],fill=5)
  if idx==2:
   for x in [8,13,20,25]:d.line((16,5,x,0),fill=14);d.point((x,0),fill=11)
  elif idx==5:
   gear(d,16,16,15,12);d.rectangle((13,6,19,11),fill=7);d.point((17,8),fill=11)
  elif idx==6:
   d.ellipse((4,0,28,24),outline=13);d.line((28,5,28,30),fill=12);d.polygon([(28,1),(31,5),(28,9),(25,5)],fill=14)
  elif idx==7:
   d.polygon([(9,3),(12,6),(15,0),(18,6),(23,3),(21,10),(11,10)],fill=12,outline=13);d.rectangle((13,12,19,22),fill=1);d.polygon([(16,13),(19,17),(16,21),(13,17)],fill=11)
 return im

def planar(im):
 data=bytearray();w,h=im.size
 assert w%8==h%8==0
 for ty in range(0,h,8):
  for tx in range(0,w,8):
   for plane in [0,2]:
    for y in range(8):
     b0=b1=0
     for x in range(8):
      v=im.getpixel((tx+x,ty+y));assert 0<=v<16
      b0|=((v>>plane)&1)<<(7-x);b1|=((v>>(plane+1))&1)<<(7-x)
     data.extend([b0,b1])
 return bytes(data)
def cgram(p):return b''.join(struct.pack('<H',(r>>3)|((g>>3)<<5)|((b>>3)<<10)) for r,g,b in p)

def main():
 import refined_art
 common=refined_art.shared_tiles(common_tiles());shared=b''.join(planar(t) for t in common)
 (OUT/'bg_common.chr').write_bytes(shared)
 previews=[];manifest={'format':'SNES4bpp/LE16map/BGR555','font':{'first':0,'asciiOffset':32,'last':95},'tile_ids':{k:96+i for i,k in enumerate(['stone','platform_top','platform_fill','dark_brick','column_l','column_r','arch_l','arch_r','neon_pipe','grate','spike','door_closed','door_open','candle','shrine','coin','chest','sword','heart','ether','key','mapdot','bar_full','bar_empty','grass','water','gear','crystal','ladder','hazard','secret','window'])},'regions':[],'sprites':{}}
 for r,(name,label,_) in enumerate(regions):
  bg=refined_art.indexed(refined_art.CASTLE_PIXELS,(256,224)) if r==0 else background(r); tiles=[];mapping={};tilemap=[]
  for y in range(0,256,8):
   for x in range(0,256,8):
    if y>=224: tilemap.append(0);continue
    t=bg.crop((x,y,x+8,y+8));enc=planar(t)
    if not any(enc):tilemap.append(0);continue
    if enc not in mapping:mapping[enc]=len(common)+len(tiles);tiles.append(enc)
    tilemap.append(mapping[enc])
  chrb=shared+b''.join(tiles);assert len(chrb)<=32768
  chrb=chrb.ljust(32768,b'\0');mapb=b''.join(struct.pack('<H',t) for t in tilemap)
  (OUT/f'bg_region{r}.chr').write_bytes(chrb);(OUT/f'bg_region{r}.map').write_bytes(mapb);(OUT/f'bg_region{r}.pal').write_bytes(cgram(palettes[r]))
  preview=palimg(bg,palettes[r]);previews.append(preview);preview.resize((768,672),Image.Resampling.NEAREST).save(OUT/f'bg_region{r}.png')
  manifest['regions'].append({'id':r,'name':name,'tiles':len(common)+len(tiles),'chrBytes':32768,'mapBytes':2048,'paletteBytes':32})
 (OUT/'bg_palettes.pal').write_bytes(b''.join(cgram(p) for p in palettes))
 # OBJ 128x256 = 512 tiles. SNES OBJ row stride is always sixteen 8x8 tiles.
 sheet=img(128,256)
 def add(name,im,x,y):
  sheet.paste(im,(x,y));manifest['sprites'][name]={'tile':(y//8)*16+x//8,'width':im.width,'height':im.height,'x':x,'y':y}
 for i in range(8):add(f'hero_{i}',hero(i),i*16,0)
 add('wolf_0',wolf(0),0,32);add('wolf_1',wolf(1),32,32);add('bat_0',bat(0),64,32);add('bat_1',bat(1),96,32)
 add('mist_0',mist(0),0,64);add('mist_1',mist(1),32,64)
 for i,kind in enumerate(['guard','archer','sentinel','beast','wisp']):add(kind,enemy(kind),i*16,96)
 for i in range(10):add(f'boss_{i}',boss(i),(i%4)*32,128+(i//4)*32)
 for i in range(4):
  im=img(32,16);d=ImageDraw.Draw(im)
  if i<2:
   d.arc((-8,-14,31,23),285,80,fill=15,width=2);d.arc((-5,-10,28,21),290,80,fill=14);d.line((1,9,29,8),fill=5)
  elif i==2:
   d.ellipse((8,3,23,12),fill=13,outline=14);d.line((0,8,26,8),fill=15)
  else:
   for a in range(8):d.line((16,8,round(16+math.cos(a*math.pi/4)*13),round(8+math.sin(a*math.pi/4)*7)),fill=15 if a%2 else 14)
  add(['slash_0','slash_1','projectile','spark'][i],im,i*32,224)
 (OUT/'sprites.chr').write_bytes(planar(sheet));(OUT/'sprites.pal').write_bytes(cgram(spal))
 # Eight OBJ banks retain common colors with accent variations for bosses/loot.
 objp=[]
 for i in range(8):
  p=spal.copy();p[9]=palettes[i][6];p[10]=palettes[i][7];p[11]=palettes[i][12];p[13]=palettes[i][10];p[14]=palettes[i][14]
  if i==0:p=spal.copy()
  objp.append(p)
 (OUT/'sprite_palettes.pal').write_bytes(b''.join(cgram(p) for p in objp))
 # Sprite preview with checkerboard making transparent bounds clear.
 spr=palimg(sheet,spal);bg=Image.new('RGB',spr.size)
 for y in range(spr.height):
  for x in range(spr.width):bg.putpixel((x,y),spr.getpixel((x,y)) if sheet.getpixel((x,y)) else ((27,28,42) if (x//8+y//8)%2 else (39,40,54)))
 bg.resize((512,1024),Image.Resampling.NEAREST).save(OUT/'sprites-preview.png')
 board=Image.new('RGB',(1024,896))
 for i,p in enumerate(previews):board.paste(p.resize((512,448),Image.Resampling.NEAREST),((i%2)*512,(i//2)*224))
 # Full region sheet, 2 columns by4 rows.
 board=Image.new('RGB',(1024,1792))
 for i,p in enumerate(previews):board.paste(p.resize((512,448),Image.Resampling.NEAREST),((i%2)*512,(i//2)*448))
 board.save(OUT/'regions-preview.png')
 refined_art.write_hero(OUT,planar,cgram)
 manifest['hero_dynamic']={'width':32,'height':48,'frames':16,'palette':7,'bytesPerFrame':768}
 manifest['portal_tiles']={'normal':128,'locked':148,'secret':168,'altar':188}
 (OUT/'graphics-layout.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print(json.dumps({'regionTiles':[r['tiles'] for r in manifest['regions']],'spriteBytes':len(planar(sheet)),'out':str(OUT)}))
if __name__=='__main__':main()
