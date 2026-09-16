#!/usr/bin/env python3
"""Revision 2 native pixel art. 4bpp tiles, two real Mode 1 backgrounds.
The 32x48 protagonist uses six 16x16 objects and streamed poses, not a
scaled image. Every visible door is a single 24x40, 15-tile metatile.
"""
from pathlib import Path
from PIL import Image, ImageDraw
import math, random, struct, json
import generate_graphics as g
OUT = g.OUT
HERO_POSES = 16
COMMON_COUNT = 224
DOOR_OPEN, DOOR_CLOSED, DOOR_SECRET, ALTAR = 128, 143, 158, 173
PLATFORM_LEFT, PLATFORM_MIDDLE, PLATFORM_RIGHT = 185, 186, 187

# More deliberate material ramps. Palette 0 = masonry, 1 = distant sky,
# 2 = architectural fixtures, 3 = HUD. Each remains a genuine 16-color bank.
for i,p in enumerate(g.palettes):
    p[0] = (4,5,13)
    if i == 0:
        for k,c in {1:'0c0d20',2:'181a32',3:'2b2948',4:'494365',5:'817491',6:'183e58',7:'418a9a',8:'251b30',9:'6c3042',10:'bd9866',11:'d8baa6',12:'be416c',13:'9a9dcc',14:'88eeee',15:'f3e4c6'}.items():p[k]=g.rgb(c)
SPAL = [g.rgb(c) for c in ['000000','101122','25263e','45425e','7c7a97','babed5','f4f1ed','f2d6bd','b48682','35152e','7c2044','cb416a','9a7448','e6c78f','80dce6','e8ffff']]

def sky_palette(region):
    p = [g.rgb(c) for c in ['04050d','070918','111a31','172843','24425a','326079','417c94','7096bb','95b4d5','c1d0e0','e2e3df','3c516f','122237','1a334b','496581','7ee0df']]
    if region == 7:
        p[2:7]=[g.rgb(c) for c in ['211329','35203b','482644','663954','885571']]
    if region == 4:p[2:7]=[g.rgb(c) for c in ['28131b','3e1f25','593132','784139','99503b']]
    return p

def distant(region):
    im=g.img(256,256);d=ImageDraw.Draw(im);rng=random.Random(2026+region)
    d.rectangle((0,0,255,255),fill=1)
    for y in range(24,200):
        d.line((0,y,255,y),fill=2 if y<80 else 3 if y<130 else 4)
        if y%4==0:
            c=3 if y<80 else 4
            for x in range(y%8,256,8):d.point((x,y),fill=c)
    for _ in range(83):
        x,y=rng.randrange(256),rng.randrange(26,134);d.point((x,y),fill=rng.choice([6,7,8]))
    for x,y in [(42,58),(128,40),(222,86)]:
        d.line((x-1,y,x+1,y),fill=8);d.line((x,y-1,x,y+1),fill=8);d.point((x,y),fill=10)
    # One moon in real depth, rather than a repeated crescent in every window.
    moon=g.img(48,48);md=ImageDraw.Draw(moon)
    md.ellipse((1,1,44,44),fill=7);md.ellipse((2,1,43,41),fill=9)
    md.ellipse((5,2,41,37),fill=10);md.ellipse((26,0,47,36),fill=0)
    for x,y,rad,c in [(11,16,3,8),(18,31,4,8),(8,28,2,7),(21,9,2,9)]:md.ellipse((x-rad,y-rad,x+rad,y+rad),fill=c)
    im.paste(moon,(120,79),moon.point([0]+[255]*255,'L'))
    d.polygon([(0,145),(21,117),(39,135),(63,107),(99,148),(119,119),(156,150),(183,128),(213,110),(255,143),(255,199),(0,199)],fill=12)
    d.polygon([(0,159),(33,142),(55,153),(89,125),(119,162),(159,144),(188,162),(225,132),(255,153),(255,199),(0,199)],fill=3)
    for x,h in [(8,35),(27,58),(50,28),(78,43),(103,24),(133,39),(164,22),(207,47),(234,29)]:
        y=190-h;d.rectangle((x,y,x+13,199),fill=1);d.polygon([(x-2,y),(x+6,y-14),(x+15,y)],fill=1)
        for yy in range(y+8,190,12):
            for xx in (x+3,x+9):d.rectangle((xx,yy,xx+1,yy+3),fill=6)
    return im

def door(kind=0):
    im=g.img(24,40);d=ImageDraw.Draw(im)
    if kind==2:
        d.rectangle((0,0,23,39),fill=2)
        for y in range(0,40,8):
            d.line((0,y,23,y),fill=1)
            for x in range(-8 if y%16 else 0,24,16):
                d.line((x,y,x,y+8),fill=1);d.line((x+1,y+1,min(23,x+14),y+1),fill=3)
        d.line((13,9,11,15,14,20,12,26,13,29),fill=1);d.point((12,20),fill=4)
        return im
    d.polygon([(0,39),(0,11),(4,6),(11,0),(12,0),(20,6),(23,11),(23,39)],fill=1)
    d.line([(1,38),(1,12),(6,6),(11,2),(12,2),(18,6),(22,12),(22,38)],fill=5,width=2)
    d.line([(4,36),(4,13),(8,8),(11,6),(12,6),(16,8),(19,13),(19,36)],fill=10)
    d.polygon([(6,35),(6,14),(9,10),(12,8),(17,14),(17,35)],fill=1 if kind==0 else 8)
    if kind==0:
        d.line((7,16,7,34),fill=6);d.line((16,16,16,34),fill=6)
        d.point((8,20),fill=7);d.point((14,30),fill=7)
        d.line((7,35,16,35),fill=7);d.line((8,36,15,36),fill=14)
    else:
        for x in [7,10,13,16]:d.line((x,14,x,35),fill=9)
        for y in [19,29]:d.line((6,y,17,y),fill=4);d.point((8,y),fill=10);d.point((15,y),fill=10)
        d.ellipse((14,23,16,25),outline=13)
    for y in [18,26,34]:
        d.line((0,y,3,y),fill=2);d.line((20,y,23,y),fill=2)
    d.rectangle((0,37,23,39),fill=3);d.line((0,37,23,37),fill=10);d.line((1,38,22,38),fill=5)
    # One central keystone, one arch, no repeated complete door images.
    d.polygon([(10,3),(13,3),(14,7),(11,9),(9,7)],fill=10);d.point((11,5),fill=15)
    return im

def altar():
    im=g.img(24,32);d=ImageDraw.Draw(im)
    d.line((2,11,2,25,21,25,21,11),fill=5)
    for x in [1,20]:d.rectangle((x,9,x+2,12),fill=10);d.point((x+1,8),fill=15)
    d.polygon([(11,1),(16,9),(14,18),(11,22),(7,17),(6,9)],fill=6,outline=14)
    d.polygon([(11,2),(11,21),(7,16),(7,9)],fill=7);d.line((11,3,14,9,12,15),fill=15)
    d.ellipse((8,22,15,25),fill=4,outline=10)
    d.rectangle((4,26,19,28),fill=4);d.line((4,26,19,26),fill=10)
    d.rectangle((1,29,22,31),fill=3);d.line((1,29,22,29),fill=5)
    return im

def common_tiles():
    tiles=g.common_tiles()
    def append_image(im):
        for y in range(0,im.height,8):
            for x in range(0,im.width,8):tiles.append(im.crop((x,y,x+8,y+8)))
    for kind in (0,1,2):append_image(door(kind))
    append_image(altar())
    for kind in range(3):
        im=g.img(8,8);d=ImageDraw.Draw(im)
        d.rectangle((0,0,7,5),fill=3);d.line((0,0,7,0),fill=10);d.line((0,1,7,1),fill=5);d.line((0,5,7,5),fill=1)
        d.line((1,3,6,3),fill=4)
        if kind==0:d.line((0,2,0,4),fill=10);d.line((2,6,5,7),fill=4)
        elif kind==2:d.line((7,2,7,4),fill=2);d.line((2,7,5,6),fill=4)
        else:d.point((3,3),fill=10)
        tiles.append(im)
    while len(tiles)<COMMON_COUNT:tiles.append(g.img(8,8))
    # Top edge and alternating slabs of the walkable floor.
    for idx in [96,188,189]:
        im=g.img(8,8);d=ImageDraw.Draw(im);d.rectangle((0,0,7,7),fill=3)
        d.line((0,0,7,0),fill=5);d.line((0,1,7,1),fill=4);d.line((0,7,7,7),fill=1)
        if idx!=188:d.line((7,2,7,7),fill=2)
        d.point((2,4),fill=4);tiles[idx]=im
    for idx,color in [(118,12),(200,14),(119,2),(201,2)]:
        im=g.img(8,8);d=ImageDraw.Draw(im);d.rectangle((0,1,7,6),fill=color)
        d.line((0,1,7,1),fill=15 if idx in [118,200] else 4)
        d.line((0,6,7,6),fill=9 if idx==118 else 6 if idx==200 else 1);tiles[idx]=im
    return tiles

def architecture(region):
    im=g.img(256,224);d=ImageDraw.Draw(im);rng=random.Random(761+region)
    d.rectangle((0,24,255,199),fill=2)
    # Broken joins, bevels and small inclusions, not flat wide outlines.
    for y in range(24,201,12):
        for x in range(-16 if (y//12)%2 else 0,256,32):
            c=rng.choice([2,2,2,3]);d.rectangle((x,y,x+31,y+11),fill=c)
            d.line((x,y+11,x+31,y+11),fill=1);d.line((x+31,y,x+31,y+11),fill=1)
            d.line((x+1,y+1,x+29,y+1),fill=3 if c==2 else 4)
            if rng.random()<.5:d.line((x+7,y+7,x+10,y+7),fill=1)
    # Windows expose a separate scrolling background instead of baked moons.
    for wx in [18,99,180]:
        d.polygon([(wx,182),(wx,74),(wx+29,36),(wx+58,74),(wx+58,182)],fill=1)
        d.line([(wx,181),(wx,74),(wx+29,36),(wx+58,74),(wx+58,181)],fill=4,width=3)
        d.line([(wx+4,181),(wx+4,77),(wx+29,43),(wx+54,77),(wx+54,181)],fill=5)
        d.polygon([(wx+8,180),(wx+8,82),(wx+29,53),(wx+50,82),(wx+50,180)],fill=0)
        d.line((wx+29,55,wx+29,181),fill=3,width=2);d.line((wx+30,57,wx+30,180),fill=5)
        for yy in [109,146]:
            d.line((wx+8,yy,wx+50,yy),fill=3,width=2);d.line((wx+8,yy+2,wx+50,yy+2),fill=1)
        d.line([(wx+9,93),(wx+29,69),(wx+49,93)],fill=4)
        d.ellipse((wx+24,73,wx+34,88),outline=10)
        d.rectangle((wx-2,182,wx+60,185),fill=3);d.line((wx-2,182,wx+60,182),fill=5)
    for x in [7,88,169,249]:
        d.rectangle((x-6,29,x+6,199),fill=1)
        d.rectangle((x-4,31,x+4,195),fill=3);d.line((x-2,32,x-2,195),fill=5);d.line((x,32,x,195),fill=4)
        d.line((x+3,32,x+3,195),fill=2)
        for yy in [29,33,132,137,189,194]:
            d.rectangle((x-7,yy,x+7,yy+2),fill=4);d.line((x-7,yy,x+7,yy),fill=5)
        d.polygon([(x-6,35),(x+6,35),(x+3,40),(x-3,40)],fill=4)
    if region==1:
        for x in [19,100,181]:
            d.rectangle((x,65,x+57,181),fill=8,outline=10)
            for yy in [86,109,132,155,178]:
                d.rectangle((x+3,yy-19,x+54,yy),fill=1)
                for xx in range(x+5,x+52,4):
                    h=rng.randrange(12,19);c=rng.choice([3,4,6,9,12,13]);d.rectangle((xx,yy-h,xx+2,yy-1),fill=c)
                    d.point((xx+1,yy-h+2),fill=10);d.point((xx+1,yy-3),fill=10)
                d.line((x+1,yy,x+56,yy),fill=10);d.line((x+2,yy+1,x+55,yy+1),fill=4)
            for xx in [x+1,x+55]:d.line((xx,66,xx,181),fill=5)
    elif region==2:
        for x in [9,77,91,161,172,244]:
            d.line([(x,187),(x-4,153),(x+3,125),(x-2,90),(x+4,53)],fill=7,width=2)
            for yy in range(49,181,11):
                s=1 if yy%2 else -1
                d.polygon([(x,yy),(x+s*8,yy-7),(x+s*11,yy-6),(x+s*8,yy-1)],fill=4,outline=7)
                if yy%3==1:
                    d.ellipse((x-3,yy-4,x+3,yy+2),fill=12);d.point((x,yy-1),fill=15)
        for _ in range(36):d.point((rng.randrange(256),rng.randrange(40,181)),fill=14)
    elif region==3:
        for x in [14,76,174,236]:
            d.rectangle((x,32,x+7,183),fill=3,outline=5);d.line((x+2,34,x+2,183),fill=7)
            for yy in [62,112,166]:d.rectangle((x-2,yy,x+9,yy+4),fill=4);d.line((x-2,yy,x+9,yy),fill=5)
        d.rectangle((0,190,255,199),fill=6)
        for xx in range(0,256,12):d.line((xx,194+(xx//12)%2,xx+8,194+(xx//12)%2),fill=14)
    elif region==4:
        for x in [25,106,187]:
            d.polygon([(x,181),(x,111),(x+19,88),(x+38,111),(x+38,181)],fill=1,outline=10)
            d.rectangle((x+4,121,x+34,177),fill=9)
            for j in range(15):
                fx=x+rng.randrange(5,32);h=rng.randrange(12,42)
                d.polygon([(fx-3,176),(fx,176-h),(fx+4,176)],fill=12 if j%2 else 10)
                d.line((fx,174,fx+1,177-h//2),fill=15)
            for gx in range(x+4,x+35,6):d.line((gx,120,gx,179),fill=2,width=2)
    elif region==5:
        g.gear(d,41,114,35);g.gear(d,213,108,33);g.gear(d,78,64,18);g.gear(d,171,161,23)
        d.ellipse((87,71,169,153),fill=1,outline=10);d.ellipse((91,75,165,149),fill=3,outline=5)
        d.ellipse((96,80,160,144),fill=2,outline=10)
        for a in range(60):
            r=29 if a%5 else 27;an=a*math.pi/30
            x,y=round(128+math.sin(an)*r),round(112-math.cos(an)*r)
            d.point((x,y),fill=15 if a%5==0 else 5)
        d.line((128,89,128,112,143,123),fill=15,width=2);d.ellipse((125,109,131,115),fill=10)
        for x in [69,184]:
            d.line((x,31,x,174),fill=5)
            for y in range(35,163,6):d.ellipse((x-1,y,x+1,y+3),outline=10)
            d.ellipse((x-4,166,x+4,182),fill=10,outline=5)
    elif region==6:
        d.rectangle((26,42,231,153),fill=0,outline=4)
        for x in [75,182]:d.line((x,43,x,151),fill=4)
        d.arc((57,45,207,179),180,360,fill=10);d.arc((67,49,197,169),180,360,fill=5)
        d.line((94,181,127,146,160,181),fill=5,width=3)
        d.line((127,146,171,105),fill=3,width=10);d.line((130,145,175,104),fill=13,width=3)
        d.line((167,100,178,112),fill=10,width=2)
    elif region==7:
        for x in [22,40,58,79,175,196,215,234]:
            yy=rng.randrange(70,141);d.line((x,31,x,yy,x+7,yy+7,x+7,180),fill=7)
            d.rectangle((x-1,yy-1,x+1,yy+1),fill=14)
        d.polygon([(96,180),(96,87),(112,62),(143,62),(159,87),(159,180)],fill=1,outline=10)
        d.polygon([(105,167),(105,96),(128,73),(150,96),(150,167)],fill=9,outline=12)
        d.polygon([(128,91),(144,120),(128,157),(111,120)],fill=12,outline=14)
        d.polygon([(128,97),(132,119),(128,151),(123,120)],fill=15)
        d.rectangle((92,180,163,184),fill=5)
    # Brass sconces and hanging crystal lanterns; no repeated mock doors.
    for x in [12,92,172,243]:
        d.line((x,126,x+7,126,x+7,117),fill=10);d.line((x+1,127,x+7,127),fill=4)
        d.rectangle((x+5,107,x+9,116),fill=10);d.rectangle((x+6,109,x+8,114),fill=15)
        d.polygon([(x+5,106),(x+7,103),(x+9,106)],fill=5)
    d.rectangle((0,24,255,28),fill=3);d.line((0,24,255,24),fill=10);d.line((0,27,255,27),fill=5)
    for x in range(0,256,16):
        d.polygon([(x+2,29),(x+8,35),(x+14,29)],fill=4);d.point((x+8,31),fill=10)
    d.rectangle((0,196,255,199),fill=2);d.line((0,199,255,199),fill=5)
    # The horizon in BG2 is dark under the HUD and the footer.
    d.rectangle((0,0,255,23),fill=0);d.rectangle((0,200,255,223),fill=0)
    return im

def hero_pose(pose):
    im=g.img(32,48);d=ImageDraw.Draw(im)
    walking=2<=pose<=9;phase=(pose-2)*math.pi/4 if walking else 0
    stride=math.sin(phase);bob=-1 if walking and pose in [3,4,7,8] else (1 if pose==1 else 0)
    swing=round(stride*5) if walking else 0
    # One-pixel contour and separate far limb prevent the rigid puppet shape.
    farfoot=18-swing;nearfoot=22+swing
    fy=45 if not walking or stride<0 else 42
    if pose in [13,14]:farfoot=12;nearfoot=25;fy=40 if pose==13 else 44
    d.polygon([(16,29+bob),(20,29+bob),(20-swing//2,37),(farfoot+2,fy),(farfoot-3,fy),(15-swing//2,37)],fill=1)
    d.line((18,31+bob,17-swing//2,37,farfoot-1,fy-1),fill=3,width=2)
    d.rectangle((farfoot-3,fy,farfoot+3,fy+1),fill=3);d.point((farfoot+2,fy),fill=5)
    # Animated cloak, independently deformed along its length.
    flutter=round(math.cos(phase)*2) if walking else pose%2
    tail=3+flutter
    cape=[(14,13+bob),(10,17+bob),(7,24),(4,32),(tail,41),(2,43),(8,44),(14,39),(17,29),(18,15+bob)]
    d.polygon(cape,fill=9,outline=1)
    d.polygon([(12,18+bob),(10,25),(7,34),(5+flutter,41),(8,41),(12,35),(15,20)],fill=10)
    d.line([(11,22),(9,29),(8+flutter,36),(6+flutter,41)],fill=11)
    d.line([(14,23),(12,32),(11,37)],fill=11)
    # Front leg, articulated knee and layered leather boot.
    ny=45 if not walking or stride>=0 else 43
    if pose==13:ny=41
    d.polygon([(20,29+bob),(24,30+bob),(24+swing//2,37),(nearfoot+1,ny),(nearfoot-4,ny),(19+swing//2,38)],fill=1)
    d.line((22,32+bob,22+swing//2,37,nearfoot-2,ny-1),fill=2,width=2)
    d.line((nearfoot-3,ny-7,nearfoot-2,ny-1),fill=4)
    d.line((nearfoot-4,ny-8,nearfoot,ny-8),fill=12)
    d.rectangle((nearfoot-4,ny,nearfoot+3,ny+1),fill=3);d.line((nearfoot-3,ny,nearfoot+2,ny),fill=5)
    # Brocade coat, silver shoulder pieces and gold clasps.
    d.polygon([(15,13+bob),(21,13+bob),(25,17+bob),(23,27+bob),(24,34+bob),(19,31+bob),(13,34+bob),(14,24+bob),(12,18+bob)],fill=1)
    d.polygon([(16,16+bob),(21,15+bob),(23,20+bob),(21,28+bob),(22,32+bob),(18,29+bob),(15,32+bob)],fill=2)
    d.line((16,17+bob,16,27+bob),fill=5);d.line((19,17+bob,19,28+bob),fill=12)
    d.line((14,29+bob,23,29+bob),fill=10);d.rectangle((18,28+bob,20,30+bob),fill=13);d.point((19,29+bob),fill=1)
    for y in [19,23,26]:d.point((20,y+bob),fill=13)
    d.polygon([(13,14+bob),(16,13+bob),(18,16+bob),(15,19+bob),(12,17+bob)],fill=4,outline=1)
    d.line((13,15+bob,16,14+bob,17,16+bob),fill=6)
    # Silver hair has several contour levels, not a flat rectangle.
    d.polygon([(14,5+bob),(18,2+bob),(23,3+bob),(26,6+bob),(23,9+bob),(22,13+bob),(19,17+bob),(14,24+bob),(9,27+bob),(11,20+bob),(11,13+bob)],fill=1)
    d.polygon([(15,5+bob),(19,3+bob),(23,4+bob),(25,6+bob),(21,8+bob),(18,15+bob),(15,22+bob),(11,24+bob),(13,16+bob),(12,11+bob)],fill=4)
    d.line([(15,6+bob),(17,4+bob),(21,4+bob),(24,6+bob)],fill=6)
    d.line([(15,7+bob),(14,12+bob),(15,16+bob),(12,22+bob)],fill=5)
    d.line([(18,6+bob),(16,12+bob),(16,16+bob)],fill=6)
    d.polygon([(20,7+bob),(24,7+bob),(24,10+bob),(26,11+bob),(24,12+bob),(23,15+bob),(20,14+bob),(19,10+bob)],fill=7)
    d.line((20,13+bob,22,14+bob),fill=8);d.point((23,9+bob),fill=1);d.point((24,10+bob),fill=14)
    d.line((20,6+bob,24,6+bob),fill=6)
    # Forearm follows walking, jumping and a three-pose sword sequence.
    if pose in [10,11,12]:
        handx=28 if pose!=10 else 25;handy=21+bob if pose==11 else 18+bob if pose==10 else 25+bob
        d.line((23,18+bob,26,21+bob,handx,handy),fill=1,width=5)
        d.line((23,18+bob,26,21+bob,handx,handy),fill=4,width=3)
        d.rectangle((handx-1,handy-1,handx+1,handy+1),fill=7)
        d.line((handx+1,handy-4,handx+1,handy+4),fill=13)
        if pose==10:d.line((handx+1,handy-3,30,7),fill=6,width=2)
    else:
        handx=24-round(stride*2) if walking else 24
        handy=29+bob if pose not in [13,14] else 24
        d.line((24,19+bob,25,24+bob,handx,handy),fill=1,width=5)
        d.line((24,19+bob,25,24+bob,handx,handy),fill=4,width=3)
        d.line((24,19+bob,25,22+bob),fill=6)
        d.rectangle((handx-1,handy,handx+1,handy+2),fill=7);d.point((handx+1,handy+2),fill=8)
        d.line((handx-2,handy+4,handx+3,handy+3),fill=13)
        d.line((handx,handy+4,min(31,handx+4),42),fill=5);d.line((handx+1,handy+4,min(31,handx+5),42),fill=6)
    if pose==15:
        # A crouched dash is a pose, not a forced global screen jump.
        out=g.img(32,48);out.paste(im.crop((0,0,32,40)),(1,7));im=out
    return im

def enemy_pose(kind,phase=0):
    im=g.enemy(kind);d=ImageDraw.Draw(im)
    if kind in ['guard','archer','sentinel']:
        d.line((5,4,10,3),fill=6);d.line((4,13,10,12,13,17),fill=5)
        d.point((10,9),fill=14);d.line((5,17,10,17),fill=12)
        d.line((5,20,10,20),fill=4);d.line((6,22,9,22),fill=5)
        if phase:
            d.rectangle((2,24,13,31),fill=0)
            d.polygon([(5,23),(8,23),(7,27),(3,30),(1,30),(4,26)],fill=3,outline=5)
            d.polygon([(9,23),(11,23),(12,28),(15,30),(11,30),(9,27)],fill=4,outline=5)
    return im

def encode_map(im,shared_count=0):
    tiles=[];mapping={};m=[]
    for yy in range(0,256,8):
        for xx in range(0,256,8):
            enc=g.planar(im.crop((xx,yy,xx+8,yy+8)))
            if not any(enc):m.append(0);continue
            if enc not in mapping:
                number=shared_count+len(tiles);tiles.append(enc);mapping[enc]=number
                tile=im.crop((xx,yy,xx+8,yy+8))
                for trans,flag in [(Image.Transpose.FLIP_LEFT_RIGHT,0x4000),(Image.Transpose.FLIP_TOP_BOTTOM,0x8000),(Image.Transpose.ROTATE_180,0xc000)]:
                    mapping.setdefault(g.planar(tile.transpose(trans)),number|flag)
            m.append(mapping[enc])
    return tiles,m

def main():
    tiles=common_tiles();shared=b''.join(g.planar(t) for t in tiles)
    (OUT/'bg_common.chr').write_bytes(shared)
    manifest={'version':2,'format':'SNES 4bpp / Mode 1 / BGR555','common_count':len(tiles),'hero_poses':HERO_POSES,'hero_size':[32,48],'regions':[],'sprites':{},'doors':{'open':DOOR_OPEN,'closed':DOOR_CLOSED,'secret':DOOR_SECRET,'width':3,'height':5,'altar':ALTAR}}
    allpal=[]
    for r,(name,_,_) in enumerate(g.regions):
        foreground=g.img(256,256);foreground.paste(architecture(r),(0,0))
        ts,m=encode_map(foreground,len(tiles));assert len(ts)+len(tiles)<=1024
        (OUT/f'bg_region{r}.chr').write_bytes((shared+b''.join(ts)).ljust(32768,b'\0'))
        (OUT/f'bg_region{r}.map').write_bytes(struct.pack('<1024H',*m))
        sky=distant(r);st,sm=encode_map(sky,1)
        assert len(st)<256, (r,len(st))
        (OUT/f'far_region{r}.chr').write_bytes((bytes(32)+b''.join(st)).ljust(8192,b'\0'))
        (OUT/f'far_region{r}.map').write_bytes(struct.pack('<1024H',*[v|0x400 for v in sm]))
        fixture=g.palettes[r].copy();fixture[1]=(8,9,19);fixture[6]=(13,49,58);fixture[7]=(37,114,126);fixture[14]=(112,235,231)
        ui=g.palettes[r].copy();ui[12]=(193,46,82);ui[14]=(89,191,231);ui[15]=(233,227,206)
        pal=g.cgram(g.palettes[r])+g.cgram(sky_palette(r))+g.cgram(fixture)+g.cgram(ui)
        (OUT/f'bg_region{r}.pal').write_bytes(pal);allpal.append(pal)
        bg=g.palimg(sky.crop((0,0,256,224)),sky_palette(r));fg=g.palimg(foreground.crop((0,0,256,224)),g.palettes[r])
        mask=foreground.crop((0,0,256,224)).point([0]+[255]*255,'L');bg.paste(fg,(0,0),mask)
        bg.resize((768,672),Image.Resampling.NEAREST).save(OUT/f'bg_region{r}.png')
        manifest['regions'].append({'id':r,'name':name,'foreground_tiles':len(ts)+len(tiles),'far_tiles':len(st)+1,'palette_bytes':128})
    (OUT/'bg_palettes.pal').write_bytes(b''.join(allpal))
    sheet=g.img(128,256)
    def add(name,im,x,y):
        sheet.paste(im,(x,y));manifest['sprites'][name]={'tile':(y//8)*16+x//8,'x':x,'y':y,'width':im.width,'height':im.height}
    add('hero_stream',hero_pose(0),0,0)
    add('wolf_0',g.wolf(0),32,0);add('wolf_1',g.wolf(1),64,0)
    add('bat_0',g.bat(0),96,0);add('bat_1',g.bat(1),32,32)
    add('mist_0',g.mist(0),64,32);add('mist_1',g.mist(1),96,32)
    for i,kind in enumerate(['guard','archer','sentinel','beast','wisp']):
        add(kind+'_walk',enemy_pose(kind,1),i*16,64);add(kind,enemy_pose(kind,0),i*16,96)
    for i in range(10):
        b=g.boss(i);d=ImageDraw.Draw(b)
        d.line((12,16,20,16),fill=12);d.point((18,10),fill=14)
        add(f'boss_{i}',b,(i%4)*32,128+(i//4)*32)
    for i in range(4):
        im=g.img(32,32);d=ImageDraw.Draw(im)
        if i<2:
            d.arc((-7,-4,30,33),275,80,fill=5,width=4);d.arc((-6,-3,31,32),275,80,fill=14,width=2)
            d.arc((-4,-1,28,30),285,80,fill=15,width=2)
            for x,y in [(26,8),(29,15),(22,26)]:d.point((x,y),fill=6)
        elif i==2:
            d.polygon([(4,7),(8,3),(12,7),(8,12)],fill=14,outline=5);d.point((8,7),fill=15)
        else:
            for a in range(8):d.line((8,8,round(8+math.cos(a*math.pi/4)*7),round(8+math.sin(a*math.pi/4)*7)),fill=15 if a%2 else 14)
        add(['slash_0','slash_1','projectile','spark'][i],im,i*32,224)
    (OUT/'sprites.chr').write_bytes(g.planar(sheet));(OUT/'sprites.pal').write_bytes(g.cgram(SPAL))
    objpal=[]
    for i in range(8):
        p=SPAL.copy()
        if i:p[9],p[10],p[11],p[13],p[14]=g.palettes[i][6],g.palettes[i][7],g.palettes[i][12],g.palettes[i][10],g.palettes[i][14]
        objpal.append(g.cgram(p))
    (OUT/'sprite_palettes.pal').write_bytes(b''.join(objpal))
    (OUT/'hero-frames.chr').write_bytes(b''.join(g.planar(hero_pose(i)) for i in range(HERO_POSES)))
    preview=Image.new('RGB',(32*8,48*2),(10,12,25))
    for i in range(HERO_POSES):
        sprite=hero_pose(i);color=g.palimg(sprite,SPAL);mask=sprite.point([0]+[255]*255,'L')
        preview.paste(color,((i%8)*32,(i//8)*48),mask)
    preview.resize((1024,384),Image.Resampling.NEAREST).save(OUT/'hero-poses-preview.png')
    g.palimg(sheet,SPAL).resize((512,1024),Image.Resampling.NEAREST).save(OUT/'sprites-preview.png')
    (OUT/'graphics-layout.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'hero_poses':HERO_POSES,'hero_chr_bytes':HERO_POSES*768,'regions':manifest['regions']}))
if __name__=='__main__':main()
