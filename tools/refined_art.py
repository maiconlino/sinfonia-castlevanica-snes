"""Native 4bpp revision art. Deterministic original pixels, no commercial assets.

The renderer chooses one 16-colour palette per 8x8 background tile. Character
frames are streamed as six 16x16 objects, retaining the SNES native tile stride.
"""
from PIL import Image, ImageDraw
import math, random, struct
import numpy as np
import generate_graphics as old

HEX=lambda xs:[tuple(bytes.fromhex(x)) for x in xs.split()]
STONE=HEX('05060f 0d101e 171c2e 232940 30384c 41495e 535d74 69758c 8a94aa b2b4c4 46394e 645167 856f84 a591a3 c8b7bc ede2d4')
NIGHT=HEX('05060f 091020 0b1c31 12334b 1b4b63 2d617b 427b92 68a0ae 9bced3 d7efee 202241 373557 56517b 8179a3 b4a7c8 f1e4d8')
GOLD=HEX('05060f 15121a 251c24 382831 4e343c 654546 805d50 9d7860 bb9978 d8bb92 2b303b 48505b 727986 a2a9b4 d2d8dd f5ebd3')
MAGIC=HEX('05060f 151027 281737 412447 643251 914469 bf667e e198a4 242741 44416a 72629a a991c4 16444e 347684 72c3c7 d5eff1')
DOOR=HEX('05060f 121320 242535 383749 535265 76758b a4a4b2 d7d6d4 35262e 5f403c 94634a c09361 e6c28b 23636e 6baab4 dbf1e4')
UI=HEX('05060f 101320 252334 443446 746172 a792a1 cbbab7 609eaf 264353 511e3d 962752 d64876 cf4269 928abb 75dce1 f0e5ce')
HERO=HEX('000000 10111d 25273b 414561 79748e bdb9ca f3e6df e9c4a2 976d71 37142d 722341 ba4060 997647 e1bc76 68b3c9 e9f6ed')

def mix(a,b,t):return tuple(round(x*(1-t)+y*t) for x,y in zip(a,b))
def palette_set(region):
    p=[STONE.copy(),NIGHT.copy(),GOLD.copy(),MAGIC.copy()]
    tint=[(96,82,116),(129,61,78),(56,112,79),(48,105,122),(156,74,40),(111,101,64),(93,65,139),(114,34,78)][region]
    # Stable dark outlines with individual material lighting in each region.
    for k in range(4):
        p[k]=[mix(c,tint,.09 if j<10 else .045) if j else (5,6,15) for j,c in enumerate(p[k])]
    return p+[STONE.copy(),NIGHT.copy(),DOOR,UI]

def arch(d,box,colors,width=2):
    x0,y0,x1,y1=box;cx=(x0+x1)//2;w=x1-x0
    for k,c in enumerate(colors):
        pts=[(x0+k*width,y1),(x0+k*width,y0+w//3),(cx,y0+k*width),(x1-k*width,y0+w//3),(x1-k*width,y1)]
        d.line(pts,fill=c,width=width)

def scene(region):
    rng=random.Random(94021+region);p=palette_set(region);s,n,g,m=p[:4]
    im=Image.new('RGB',(256,224),s[0]);d=ImageDraw.Draw(im)
    # Recessed individual masonry and bevelled joints, not flat rectangles.
    for y in range(24,201,12):
        for x in range(-24 if (y//12)%2 else 0,256,32):
            c=s[2+rng.randrange(2)]
            d.rectangle((x+1,y+1,x+30,y+10),fill=c)
            d.line((x+2,y+1,x+29,y+1),fill=s[4]);d.line((x+1,y+2,x+1,y+9),fill=s[3])
            d.line((x+1,y+11,x+31,y+11),fill=s[1]);d.line((x+31,y,x+31,y+11),fill=s[1])
            for _ in range(5):d.point((x+rng.randrange(2,30),y+rng.randrange(3,10)),fill=s[2])
    # Stone arch bays form the hall's depth. Only one moon in the night sky.
    for wi,wx in enumerate((20,104,188)):
        pts=[(wx,181),(wx,76),(wx+24,41),(wx+48,76),(wx+48,181)]
        d.polygon(pts,fill=n[1])
        mask=Image.new('L',(256,224));md=ImageDraw.Draw(mask);md.polygon(pts,fill=255)
        glass=Image.new('RGB',(256,224));gd=ImageDraw.Draw(glass)
        for y in range(41,182):
            c=mix(n[2],n[5],max(0,1-abs(y-112)/83)*.7)
            gd.line((wx,y,wx+48,y),fill=c)
        for _ in range(24):
            x=wx+rng.randrange(5,44);y=rng.randrange(50,141);gd.point((x,y),fill=n[6 if rng.random()<.8 else 8])
        if wi==1:
            gd.ellipse((wx+9,71,wx+37,99),fill=n[8]);gd.ellipse((wx+15,68,wx+39,91),fill=n[3])
            gd.point((wx+12,86),fill=n[7]);gd.line((wx+14,91,wx+18,93),fill=n[7])
        for x in range(wx+1,wx+48,6):
            top=163-rng.randrange(3,20);gd.rectangle((x,top,x+5,181),fill=n[1]);gd.polygon([(x-1,top),(x+3,top-5),(x+7,top)],fill=n[1])
            gd.point((x+2,top+7),fill=g[7])
        im.paste(glass,(0,0),mask)
        d=ImageDraw.Draw(im)
        arch(d,(wx-4,36,wx+52,187),[s[1],s[6],s[3],s[5]],1)
        arch(d,(wx+1,44,wx+47,181),[s[1],s[4]],1)
        d.line((wx+24,48,wx+24,181),fill=s[1],width=3);d.line((wx+24,48,wx+24,181),fill=s[5])
        for yy in (102,143):
            d.line((wx+3,yy,wx+45,yy),fill=s[1],width=3);d.line((wx+3,yy,wx+45,yy),fill=s[4])
        d.rectangle((wx-3,181,wx+51,184),fill=s[3]);d.line((wx-3,181,wx+51,181),fill=s[6])
    # Four fluted, shaded columns, capitals and deep bases.
    for cx in (8,88,168,248):
        for dx,c in enumerate([s[1],s[2],s[4],s[6],s[5],s[3],s[2],s[3],s[5],s[4],s[2],s[1]]):
            d.line((cx-6+dx,35,cx-6+dx,190),fill=c)
        for yy in (34,38,174,187,191):
            d.rectangle((cx-9,yy,cx+8,yy+3),fill=s[3]);d.line((cx-9,yy,cx+8,yy),fill=s[6]);d.line((cx-8,yy+2,cx+7,yy+2),fill=s[2])
        for dx in (-6,4):d.arc((cx+dx-2,39,cx+dx+4,46),0,330,fill=s[6])
    # Material-specific elements make each destination visually identifiable.
    if region==1:
        for xx in (19,103,187):
            d.rectangle((xx,78,xx+48,181),fill=g[1],outline=g[6])
            for yy in (96,117,138,159,180):
                for bx in range(xx+3,xx+45,4):
                    h=rng.randrange(10,18);c=rng.choice([g[4],g[6],g[7],m[4],m[5],s[5]])
                    d.rectangle((bx,yy-h,bx+2,yy-2),fill=c);d.line((bx,yy-h+2,bx+2,yy-h+2),fill=g[9]);d.point((bx+1,yy-5),fill=g[8])
                d.rectangle((xx+1,yy,xx+47,yy+2),fill=g[5]);d.line((xx+1,yy,xx+47,yy),fill=g[8])
            for bx in (xx,xx+46):d.line((bx,77,bx,181),fill=g[8])
        # Scattered parchment and a narrow upper gallery.
        d.rectangle((92,125,162,129),fill=g[4]);d.line((92,125,162,125),fill=g[8]);d.line((120,130,127,137),fill=g[7])
    elif region==2:
        for xx in (12,74,91,177,242):
            x=xx
            for yy in range(177,45,-3):
                x=xx+round(math.sin(yy*.105)*4);d.line((x,yy,x+1,yy+3),fill=m[12])
                if yy%9==0:
                    d.polygon([(x,yy),(x-7,yy-4),(x-5,yy+2)],fill=n[5]);d.line((x-5,yy-2,x,yy),fill=n[7])
                    d.polygon([(x+1,yy+5),(x+8,yy),(x+7,yy+6)],fill=n[6])
                if yy%15==0:d.ellipse((x-3,yy-2,x,yy+1),fill=m[6]);d.point((x-2,yy-1),fill=m[7])
        for xx in range(0,256,5):
            h=rng.randrange(3,13);d.line((xx,183,xx+2,183-h),fill=n[5])
    elif region==3:
        for xx in (17,74,178,237):
            d.rectangle((xx,37,xx+7,184),fill=s[3]);d.line((xx+2,38,xx+2,183),fill=n[7]);d.line((xx+6,38,xx+6,183),fill=n[2])
            for yy in (73,123,172):d.rectangle((xx-2,yy,xx+9,yy+4),fill=s[4]);d.line((xx-1,yy,xx+8,yy),fill=s[7])
        for yy in range(165,185):
            for xx in range(0,256,2):
                if (xx//11+yy)%7==0:d.line((xx,yy,xx+8,yy),fill=n[5 if yy%3 else 7])
    elif region==4:
        for xx in (25,109,193):
            d.polygon([(xx,177),(xx,112),(xx+17,92),(xx+34,112),(xx+34,177)],fill=g[1],outline=g[7])
            for fy in range(116,177):d.line((xx+5,fy,xx+29,fy),fill=mix(g[4],g[9],(fy-116)/61))
            for i in range(16):
                fx=xx+rng.randrange(6,28);h=rng.randrange(8,39);d.polygon([(fx-2,175),(fx,175-h),(fx+2,175)],fill=g[8+i%2])
            for gx in range(xx+5,xx+30,5):d.line((gx,114,gx,177),fill=g[2],width=2)
            d.line((xx+1,133,xx+33,133),fill=g[2],width=3)
        for x in (69,154):
            d.line((x,32,x,81),fill=g[6]);d.rectangle((x-3,68,x+3,83),fill=s[3],outline=s[6]);d.rectangle((x-9,81,x+9,85),fill=s[5],outline=s[8])
    elif region==5:
        def cog(cx,cy,r):
            pts=[]
            for a in range(64):
                rr=r if a%4 in (0,3) else r-3;pts.append((round(cx+math.cos(a*math.pi/32)*rr),round(cy+math.sin(a*math.pi/32)*rr)))
            d.polygon(pts,fill=g[5],outline=g[8]);d.ellipse((cx-r+5,cy-r+5,cx+r-5,cy+r-5),fill=g[2],outline=g[7])
            for a in range(0,360,60):
                d.line((cx,cy,round(cx+math.cos(math.radians(a))*(r-7)),round(cy+math.sin(math.radians(a))*(r-7))),fill=g[6],width=3)
            d.ellipse((cx-4,cy-4,cx+4,cy+4),fill=g[7],outline=g[9])
        cog(43,113,32);cog(210,119,34);cog(76,58,17);cog(175,59,19)
        d.ellipse((96,78,161,143),fill=g[3],outline=g[9]);d.ellipse((101,83,156,138),fill=s[1],outline=g[6])
        for a in range(12):
            x=round(128+math.sin(a*math.pi/6)*24);y=round(110-math.cos(a*math.pi/6)*24);d.line((x,y,x+1,y+2),fill=g[9])
        d.line((128,91,128,110,141,121),fill=g[9],width=2);d.ellipse((126,108,130,112),fill=g[15])
        d.line((128,144,139,169),fill=g[7],width=2);d.ellipse((133,165,147,179),fill=g[6],outline=g[9])
    elif region==6:
        d.rectangle((23,63,232,160),fill=n[1],outline=s[6])
        for i in range(130):
            x=rng.randrange(25,231);y=rng.randrange(65,159);d.point((x,y),fill=n[9] if i%9==0 else n[6])
        d.ellipse((106,74,152,120),fill=n[4],outline=n[7]);d.arc((93,85,165,112),0,350,fill=g[8],width=2)
        for a in range(0,360,45):
            x=round(128+math.cos(math.radians(a))*67);y=round(112+math.sin(math.radians(a))*40);d.line((128,112,x,y),fill=n[2])
        d.line((107,182,130,150,154,182),fill=g[5],width=3);d.line((130,150,169,117),fill=s[3],width=10);d.line((131,147,169,116),fill=g[8],width=2)
    elif region==7:
        for xx in (24,48,72,184,208,232):
            yy=rng.randrange(69,127);d.line((xx,36,xx,yy,xx+6,yy+6,xx+6,181),fill=m[9]);d.line((xx+1,37,xx+1,yy-1),fill=m[12])
            d.rectangle((xx-1,yy-1,xx+2,yy+2),fill=m[13]);d.point((xx,yy),fill=m[15])
        d.polygon([(100,182),(100,90),(127,53),(155,90),(155,182)],fill=s[1],outline=m[8])
        d.polygon([(109,166),(109,96),(128,72),(146,96),(146,166)],fill=m[2],outline=m[5])
        for rr in range(22,5,-4):d.ellipse((128-rr,123-rr,128+rr,123+rr),outline=m[3+(22-rr)//4])
        d.polygon([(128,97),(138,123),(128,150),(118,123)],fill=m[5],outline=m[7]);d.line((128,100,128,148),fill=m[15])
        d.rectangle((96,177,158,181),fill=s[5]);d.line((97,177,157,177),fill=g[8])
    # Warm candelabra and hanging chains, contrast against cold recesses.
    for xx in (16,82,174,239):
        d.line((xx,131,xx,146,xx-4,146),fill=g[7]);d.line((xx+1,133,xx+1,145),fill=g[4])
        d.rectangle((xx-2,127,xx+2,131),fill=g[6]);d.rectangle((xx-1,122,xx+1,127),fill=g[9])
        d.polygon([(xx,116),(xx-2,121),(xx,124),(xx+2,121)],fill=g[8]);d.point((xx,121),fill=g[15])
        d.point((xx-3,121),fill=g[5]);d.point((xx+3,121),fill=g[5])
    for y,c in ((32,s[6]),(33,s[3]),(34,s[1]),(184,s[7]),(185,s[3]),(191,s[1]),(193,s[5]),(196,s[1])):
        d.line((0,y,255,y),fill=c)
    for x in range(0,256,16):
        d.rectangle((x+1,186,x+14,190),fill=s[3]);d.line((x+2,186,x+13,186),fill=s[5]);d.line((x+14,186,x+14,190),fill=s[1])
        d.point((x+8,194),fill=g[7])
    d.rectangle((0,0,255,31),fill=s[0]);d.rectangle((0,200,255,223),fill=s[0])
    return im,p

def tiled_scene(region):
    im,pals=scene(region);pixels=np.asarray(im,dtype=np.int32);pt=np.array(pals[:4],dtype=np.int32)
    shared=shared_tiles();data=bytearray(b''.join(old.planar(x) for x in shared));cache={};maps=[];preview=Image.new('RGB',(256,224),pals[0][0])
    for y in range(0,256,8):
        for x in range(0,256,8):
            if y<32 or y>=200:maps.append(0);continue
            block=pixels[y:y+8,x:x+8].reshape(-1,3)
            dist=((block[None,:,None,:]-pt[:,None,:,:])**2*np.array([2,3,2])).sum(axis=3)
            nearest=dist.argmin(axis=2);error=dist.min(axis=2).sum(axis=1);pal=int(error.argmin());indices=nearest[pal].astype(np.uint8).reshape(8,8)
            tile=Image.fromarray(indices,mode='P');enc=old.planar(tile)
            if enc not in cache:cache[enc]=len(data)//32;data.extend(enc)
            maps.append(cache[enc]|(pal<<10))
            rgb=np.array(pals[pal],dtype=np.uint8)[indices];preview.paste(Image.fromarray(rgb),(x,y))
    assert len(data)<=32768,(region,len(data)//32)
    return bytes(data).ljust(32768,b'\0'),struct.pack('<1024H',*maps),b''.join(old.cgram(p) for p in pals),preview,len(data)//32

def doorway(variant=0):
    im=old.img(32,48);d=ImageDraw.Draw(im)
    # One coherent 32x48 arch: jambs, separate voussoirs, threshold and recess.
    d.polygon([(0,47),(0,18),(4,10),(15,0),(20,2),(29,12),(31,18),(31,47)],fill=1)
    d.polygon([(2,46),(2,18),(6,10),(15,2),(19,4),(27,12),(29,18),(29,46)],fill=4,outline=6)
    d.polygon([(7,44),(7,20),(9,13),(16,7),(23,14),(25,20),(25,44)],fill=1,outline=2)
    for xx in (3,26):
        d.rectangle((xx,20,xx+2,43),fill=4);d.line((xx,20,xx,43),fill=6);d.line((xx+2,20,xx+2,43),fill=2)
        for yy in (23,30,37):d.line((xx-1,yy,xx+3,yy),fill=2)
    for p in [((3,14),(8,17)),((7,8),(11,12)),((11,4),(14,9)),((19,5),(18,10)),((25,10),(21,14)),((28,16),(24,18))]:d.line(p,fill=2)
    if variant==0:
        # Open doorway with receding stair treads and a cool interior light.
        d.polygon([(10,42),(10,21),(12,16),(16,12),(21,18),(22,23),(22,42)],fill=13)
        d.polygon([(12,40),(12,23),(16,17),(20,23),(20,40)],fill=1)
        for yy in (36,39,42):d.line((11,yy,22,yy),fill=3);d.line((12,yy,21,yy),fill=5)
        d.line((10,24,10,37),fill=14);d.line((23,22,23,40),fill=2)
    elif variant==1:
        d.polygon([(9,43),(9,21),(12,14),(16,11),(22,18),(23,43)],fill=8)
        for xx in (11,15,19,22):d.line((xx,22,xx,42),fill=9)
        for yy in (27,38):d.line((9,yy,23,yy),fill=11)
        d.rectangle((17,30,19,33),fill=11);d.point((18,31),fill=15)
    else:
        for yy in range(19,44):d.line((10,yy,22,yy),fill=13 if yy%5 else 14)
        d.polygon([(16,22),(20,29),(16,36),(12,29)],outline=15)
    d.rectangle((0,44,31,47),fill=3);d.line((0,44,31,44),fill=6);d.line((3,46,28,46),fill=5)
    d.polygon([(15,2),(18,6),(15,10),(12,6)],fill=11,outline=12);d.point((15,5),fill=15)
    return im

def shared_tiles():
    tiles=old.common_tiles()
    # Refined platform/floor bevels, retaining original collision indices.
    for i in (96,97,98):
        t=old.img(8,8);d=ImageDraw.Draw(t);d.rectangle((0,0,7,7),fill=3);d.line((0,0,7,0),fill=7);d.line((0,1,7,1),fill=5);d.line((0,2,7,2),fill=2)
        d.line((0,7,7,7),fill=1);d.line((7,3,7,7),fill=1)
        if i==97:d.line((1,1,6,1),fill=12);d.point((3,5),fill=4)
        tiles[i]=t
    for variant in range(3):
        door=doorway(variant)
        for y in range(0,48,8):
            for x in range(0,32,8):tiles.append(door.crop((x,y,x+8,y+8)))
    while len(tiles)<256:tiles.append(old.img(8,8))
    return tiles

def hero_frame(kind,phase=0):
    im=old.img(32,48);d=ImageDraw.Draw(im)
    run=kind=='run';air=kind in ('rise','fall');strike=kind=='attack'
    angle=phase*math.pi/4;bob=(0 if phase%4<2 else 1) if run else (1 if kind=='idle' and phase==1 else 0)
    if kind=='land':bob=3
    # Back cape, independently trailing the gait and the sword extension.
    trail=round(math.sin(angle+.6)*2) if run else (phase%2)
    cape=[(16,18+bob),(12,18+bob),(9,23),(5+trail,30),(1+trail,39),(7+trail,41),(13,37),(18,28)]
    if air:cape=[(15,18),(11,19),(7,22),(1,26),(5,32),(12,31),(17,26)]
    d.polygon(cape,fill=9);d.line(cape[:5],fill=1)
    d.polygon([(12,22+bob),(9,29),(4+trail,38),(8+trail,38),(13,34),(16,24)],fill=10)
    d.line((11,25,8+trail,34,6+trail,37),fill=11);d.line((13,26,11,34,8+trail,39),fill=9)
    d.point((4+trail,38),fill=11)
    # Articulated legs. Draw the far leg first, then the near one.
    def leg(near):
        a=angle+(0 if near else math.pi);hip=(19 if near else 16,32+bob)
        if run:
            knee=(round(hip[0]+math.sin(a)*4),38+round(math.cos(a)*1))
            foot=(round(hip[0]+math.sin(a)*7),45-max(0,round(-math.cos(a)*4)))
        elif kind=='rise':knee=(23 if near else 12,35 if near else 39);foot=(26 if near else 9,39 if near else 43)
        elif kind=='fall':knee=(22 if near else 14,39);foot=(23 if near else 11,44 if near else 43)
        elif kind=='land':knee=(23 if near else 12,40);foot=(25 if near else 11,46)
        else:knee=(19 if near else 15,39);foot=(21 if near else 14,46)
        d.line([hip,knee,foot],fill=1,width=4);d.line([hip,knee,foot],fill=3 if near else 2,width=2)
        d.line((hip[0],hip[1]+1,knee[0],knee[1]-1),fill=4 if near else 3)
        d.line((knee[0],knee[1]+1,foot[0],foot[1]-2),fill=2 if near else 1,width=2)
        d.line((foot[0]-1,foot[1],foot[0]+3,foot[1]),fill=1,width=2);d.line((foot[0],foot[1]-1,foot[0]+3,foot[1]-1),fill=4 if near else 3)
    leg(False)
    # Long open coat and embroidery use multiple shades rather than flat blocks.
    d.polygon([(14,18+bob),(21,18+bob),(24,24+bob),(22,29+bob),(25,37+bob),(20,35+bob),(17,30+bob),(13,36+bob),(10,36+bob),(13,27+bob)],fill=1)
    d.polygon([(14,19+bob),(18,20+bob),(17,29+bob),(12,34+bob),(13,27+bob)],fill=3)
    d.polygon([(18,20+bob),(22,20+bob),(23,26+bob),(21,30+bob),(23,35+bob),(19,31+bob)],fill=2)
    d.line((14,20+bob,14,27+bob,12,32+bob),fill=4)
    d.line((18,20+bob,18,28+bob),fill=12);d.point((19,21+bob),fill=13);d.point((19,24+bob),fill=13)
    d.line((13,29+bob,22,29+bob),fill=12);d.rectangle((17,28+bob,19,30+bob),fill=13);d.point((18,29+bob),fill=1)
    leg(True)
    # Neck, profile and pale flowing hair, with face kept separate from outline.
    d.rectangle((18,15+bob,21,19+bob),fill=8);d.line((19,17+bob,21,17+bob),fill=7)
    d.polygon([(16,9+bob),(20,7+bob),(23,10+bob),(23,12+bob),(25,13+bob),(23,14+bob),(22,17+bob),(18,16+bob),(16,13+bob)],fill=7,outline=8)
    d.line((19,9+bob,22,10+bob),fill=6);d.point((22,12+bob),fill=1);d.point((23,15+bob),fill=8)
    hair=[(12,12+bob),(14,8+bob),(19,6+bob),(22,7+bob),(24,9+bob),(19,9+bob),(16,12+bob),(16,17+bob),(12,21+bob),(10,27+bob),(6,29+bob),(10,22+bob),(10,15+bob)]
    d.polygon(hair,fill=4,outline=3);d.line((12,13+bob,14,10+bob,19,7+bob,22,8+bob),fill=6)
    d.line((14,13+bob,13,19+bob,10,24+bob,8,26+bob),fill=5);d.line((15,12+bob,14,17+bob,12,20+bob),fill=6)
    d.line((11,16+bob,11,21+bob,9,24+bob),fill=3);d.point((20,8+bob),fill=6)
    # Front arm movement follows the gait; attacks have three separate poses.
    shoulder=(21,20+bob)
    if strike:
        elbow=[(24,20),(25,23),(23,25)][phase];hand=[(23,15),(29,23),(28,29)][phase]
    else:
        elbow=(22+round(math.sin(angle+math.pi)*2),26+bob) if run else (23,25+bob)
        hand=(23+round(math.sin(angle+math.pi)*3),30+bob) if run else (23,29+bob)
    d.line([shoulder,elbow,hand],fill=1,width=5);d.line([shoulder,elbow,hand],fill=3,width=3);d.line((shoulder[0],shoulder[1],elbow[0],elbow[1]),fill=5)
    d.rectangle((hand[0]-1,hand[1]-1,hand[0]+1,hand[1]+1),fill=7);d.point((hand[0]+1,hand[1]),fill=6)
    if not strike:
        d.line((hand[0]+1,hand[1]+2,min(31,hand[0]+6),hand[1]+9),fill=4);d.line((hand[0]+2,hand[1]+3,min(31,hand[0]+6),hand[1]+8),fill=14)
        d.line((hand[0]-1,hand[1]+3,hand[0]+3,hand[1]),fill=13)
    else:
        d.line((hand[0]-2,hand[1]+2,hand[0]+2,hand[1]-2),fill=13)
    return im

def hero_bank():
    frames=[hero_frame('idle',0),hero_frame('idle',1)]+[hero_frame('run',i) for i in range(8)]+[hero_frame('rise'),hero_frame('fall')]+[hero_frame('attack',i) for i in range(3)]+[hero_frame('land')]
    buf=bytearray();board=Image.new('RGB',(32*8,48*2),(16,16,26))
    for i,im in enumerate(frames):
        strip=old.img(128,16)
        for y in range(3):
            for x in range(2):strip.paste(im.crop((x*16,y*16,x*16+16,y*16+16)),((y*2+x)*16,0))
        enc=old.planar(strip);assert len(enc)==1024;buf.extend(enc)
        view=old.palimg(im,HERO);board.paste(view,(i%8*32,i//8*48))
    return bytes(buf),board,frames

def generate():
    manifest={'revision':'1.1','format':'SNES 4bpp, per-tile CGRAM palette, streamed six-OBJ hero','regions':[],'door':{'first_tile':128,'tiles_per_variant':24,'width':32,'height':48,'palette':6},'hero':{'frames':16,'frame_bytes':1024,'canvas':[32,48],'objects':6,'rom_bank':13}}
    out=old.OUT;previews=[]
    for r in range(8):
        chr_,map_,pal_,preview,count=tiled_scene(r)
        (out/f'bg_region{r}.chr').write_bytes(chr_);(out/f'bg_region{r}.map').write_bytes(map_);(out/f'bg_region{r}.pal').write_bytes(pal_)
        preview.resize((768,672),Image.Resampling.NEAREST).save(out/f'bg_region{r}.png');previews.append(preview)
        manifest['regions'].append({'id':r,'tiles':count,'chrBytes':len(chr_),'mapBytes':len(map_),'paletteBytes':len(pal_)})
    (out/'bg_common.chr').write_bytes(b''.join(old.planar(x) for x in shared_tiles()))
    (out/'bg_palettes.pal').write_bytes(b''.join((out/f'bg_region{r}.pal').read_bytes() for r in range(8)))
    frames,board,_=hero_bank();(out/'hero_frames.chr').write_bytes(frames);board.resize((1024,384),Image.Resampling.NEAREST).save(out/'hero-animation-sheet.png')
    op=bytearray((out/'sprite_palettes.pal').read_bytes());op[:32]=old.cgram(HERO);(out/'sprite_palettes.pal').write_bytes(op)
    board=Image.new('RGB',(1024,1792))
    for i,p in enumerate(previews):board.paste(p.resize((512,448),Image.Resampling.NEAREST),(i%2*512,i//2*448))
    board.save(out/'regions-preview.png')
    doors=Image.new('RGB',(96,48))
    for i in range(3):doors.paste(old.palimg(doorway(i),DOOR),(i*32,0))
    doors.resize((576,288),Image.Resampling.NEAREST).save(out/'doors-preview.png')
    (out/'graphics-revision.json').write_text(old.json.dumps(manifest,indent=2)+'\n');print(old.json.dumps(manifest,indent=2))

if __name__=='__main__':generate()

# Additional native object art. This runs after the base revision generation.
def enemy_frame(kind,phase):
    im=old.img(16,32);d=ImageDraw.Draw(im)
    if kind=='wisp':
        yy=phase*2;d.polygon([(7,1+yy),(11,6+yy),(14,13+yy),(10,21+yy),(8,28),(5,22+yy),(2,16+yy),(3,9+yy)],fill=3,outline=4)
        d.polygon([(8,6+yy),(11,12+yy),(10,19+yy),(7,23+yy),(4,16+yy)],fill=14);d.ellipse((5,11+yy,10,16+yy),fill=5);d.point((7,12+yy),fill=15);return im
    # Steel armour and an eight-pixel tabard, with separate contact poses.
    delta=2 if phase else -1
    d.polygon([(3,13),(1,23),(2,28),(8,24),(10,13)],fill=9)
    d.line((5,23,4-delta,29),fill=2,width=3);d.line((10,23,11+delta,29),fill=4,width=3)
    d.line((2-delta,30,5-delta,30),fill=5);d.line((9+delta,30,13+delta,30),fill=6)
    d.polygon([(4,11),(10,11),(13,17),(11,23),(4,24),(2,18)],fill=3,outline=1)
    d.line((5,13,5,21),fill=5);d.line((8,12,10,20),fill=4);d.line((4,20,11,20),fill=12);d.point((8,21),fill=13)
    d.polygon([(3,7),(5,3),(9,2),(12,7),(11,12),(4,11)],fill=4,outline=2);d.line((5,4,8,3,10,5),fill=6)
    d.rectangle((4,7,11,8),fill=1);d.point((9,8),fill=11);d.line((6,10,11,10),fill=5)
    d.line((6,3,5,0,2,0),fill=10);d.point((3,0),fill=11)
    if kind=='sentinel':
        d.polygon([(0,14),(5,13),(7,18),(6,25),(3,28),(0,25)],fill=2,outline=12);d.line((3,16,3,25),fill=14);d.line((1,19,5,19),fill=13)
    else:
        d.line((13,11,13,27),fill=12);d.line((13,5,13,15),fill=5);d.polygon([(13,2),(11,7),(14,7)],fill=6);d.rectangle((11,18,14,20),fill=7)
    return im

def boss_frame(idx,phase):
    im=old.img(64,64);d=ImageDraw.Draw(im);b=phase
    if idx==3: # Bone-and-bronze serpent, segmented at native resolution.
        pts=[]
        for t in range(13):
            x=5+t*4;y=47-round(math.sin(t*.36+phase*.2)*13);pts.append((x,y))
        for j,(x,y) in enumerate(pts):
            rr=6 if j<10 else 7;d.ellipse((x-rr,y-rr,x+rr,y+rr),fill=3,outline=12);d.arc((x-rr+1,y-rr+1,x+rr-1,y+rr-1),180,340,fill=5);d.point((x,y-2),fill=14)
        hx,hy=pts[-1];d.polygon([(hx-3,hy-4),(hx+5,hy-12),(hx+11,hy-9),(hx+9,hy+2),(hx+1,hy+6),(hx-5,hy+3)],fill=4,outline=12)
        d.line((hx+5,hy-7,hx+8,hy-7),fill=11);d.line((hx+3,hy+1,hx+9,hy-1),fill=1);d.point((hx+7,hy),fill=6)
        d.polygon([(hx+1,hy-9),(hx-3,hy-17),(hx+4,hy-11)],fill=13);return im
    if idx==9: # Secret living blade inside a broken machine halo.
        for rr,c in [(27,3),(24,12),(20,4)]:d.arc((32-rr,31-rr,32+rr,31+rr),10+phase*8,338+phase*8,fill=c)
        for a in range(0,360,45):
            x=round(32+math.cos(math.radians(a))*26);y=round(31+math.sin(math.radians(a))*26);d.rectangle((x-2,y-2,x+2,y+2),fill=12);d.point((x,y),fill=15)
        d.polygon([(32,1),(39,13),(36,43),(32,48),(28,43),(26,13)],fill=4,outline=6)
        d.polygon([(32,4),(34,13),(33,42),(31,42),(30,13)],fill=15);d.line((20,45,43,45),fill=12,width=3)
        d.line((31,48,31,59),fill=9,width=3);d.line((32,48,32,59),fill=13);d.ellipse((29,59,35,63),fill=12,outline=13);return im
    armored=idx in (0,4,8)
    if armored:
        # Large knight: shoulders, articulated greaves, flowing lined mantle.
        d.polygon([(17,19),(10,23),(4,52+b),(12,50),(19,55),(29,48),(44,48),(60,56-b),(55,23),(44,17)],fill=9,outline=1)
        for x in (12,18,47,53):d.line((x,29,x-3 if x<32 else x+3,49),fill=10)
        d.line((10,40,6,50,12,47,17,51),fill=11)
        for xx,shift in ((24,-1),(40,1)):
            d.polygon([(xx-4,41),(xx+4,41),(xx+3+shift,53),(xx+6+shift,60),(xx-4+shift,61),(xx-5+shift,54)],fill=3,outline=1)
            d.line((xx-2,44,xx-2+shift,55),fill=5);d.line((xx-4+shift,60,xx+6+shift,60),fill=6)
            d.ellipse((xx-4,39,xx+4,46),fill=4,outline=5)
        d.polygon([(23,22),(40,22),(46,33),(40,43),(23,43),(18,33)],fill=3,outline=1)
        d.line((24,25,29,27,34,26,39,24),fill=6);d.polygon([(24,29),(38,29),(40,36),(33,40),(24,36)],fill=4,outline=5)
        d.line((32,26,32,39),fill=12);d.point((32,32),fill=13);d.line((23,42,41,42),fill=12,width=2)
        for xx in (16,45):
            d.ellipse((xx-7,20+b,xx+7,31+b),fill=4,outline=1);d.line((xx-5,23+b,xx+3,22+b),fill=6)
            d.line((xx,31,xx+(-3 if xx<32 else 4),43+b),fill=3,width=6);d.line((xx-1,32,xx+(-4 if xx<32 else 3),42+b),fill=5)
        d.polygon([(23,10),(27,5),(37,5),(42,11),(40,23),(26,23)],fill=4,outline=1)
        d.line((26,10,29,7,36,7,39,10),fill=6);d.line((24,13,41,13),fill=1,width=3);d.line((33,14,39,14),fill=11)
        d.polygon([(30,14),(35,14),(34,22),(31,22)],fill=5);d.line((27,20,29,21),fill=3)
        if idx==0:
            d.polygon([(27,7),(20,1),(20,12),(26,14)],fill=12,outline=13);d.polygon([(38,7),(45,0),(44,12),(39,14)],fill=12,outline=13)
        elif idx==4:
            d.polygon([(25,5),(27,0),(31,4),(35,0),(40,5)],fill=12);d.line((28,9,37,9),fill=13)
        else:
            d.ellipse((20,1,43,23),outline=14);d.line((22,6,41,18),fill=12)
        # Blade or forge hammer, not a scaled copy of the older tiny sprite.
        if idx==4:
            d.line((53,17,53,56),fill=12,width=2);d.rectangle((43,6+b,62,20+b),fill=3,outline=5);d.line((45,8+b,60,8+b),fill=6);d.rectangle((47,12+b,57,15+b),fill=11)
        else:
            d.line((54,23,54,57),fill=12,width=2);d.polygon([(54,3+b),(57,10+b),(55,31),(52,31),(51,10+b)],fill=5,outline=6);d.line((48,32,60,32),fill=13,width=2)
        return im
    # Spectral sovereigns: veil, thorn crown, clock halo, astronomer and AGI regent.
    d.polygon([(24,17+b),(16,23),(7,53),(15,51),(20,58),(31,54),(43,58),(49,51),(59,54),(49,23),(40,17+b)],fill=9,outline=1)
    d.polygon([(26,21),(38,21),(43,37),(49,56),(38,59),(31,55),(21,60),(15,57),(23,37)],fill=3,outline=4)
    for xx in (23,29,37,42):d.line((31 if xx<32 else 35,30,xx,55),fill=5 if xx%2 else 2)
    d.line((27,23,26,36,21,51),fill=12);d.line((37,24,38,38,44,51),fill=12)
    d.ellipse((26,10+b,38,24+b),fill=4);d.rectangle((29,14+b,36,21+b),fill=1);d.point((30,17+b),fill=14);d.point((35,17+b),fill=14)
    d.polygon([(24,19+b),(24,10+b),(30,5+b),(37,6+b),(42,12+b),(43,25),(38,20+b),(36,10+b),(30,9+b),(28,20+b)],fill=5,outline=3)
    d.line((26,10+b,30,7+b,36,8+b),fill=6)
    d.line((24,25,17,35,11,31+b),fill=4,width=4);d.line((41,25,48,35,55,30-b),fill=4,width=4)
    d.ellipse((8,27+b,13,32+b),fill=5);d.ellipse((53,27-b,58,32-b),fill=5)
    if idx==1:
        d.arc((8,0,55,41),180,358,fill=13);d.line((9,33,9,56),fill=12);d.rectangle((3,34,14,42),fill=9,outline=13);d.line((8,34,8,41),fill=6)
    elif idx==2:
        for a in range(200,346,23):
            x=round(32+math.cos(math.radians(a))*20);y=round(24+math.sin(math.radians(a))*22);d.line((32,14,x,y),fill=12,width=2);d.point((x,y),fill=11)
        d.ellipse((28,29,36,37),fill=10,outline=13);d.point((32,32),fill=14)
    elif idx==5:
        for a in range(0,360,30):
            x=round(32+math.cos(math.radians(a))*27);y=round(31+math.sin(math.radians(a))*27);d.rectangle((x-2,y-2,x+2,y+2),fill=12)
        d.ellipse((7,6,57,56),outline=13);d.ellipse((26,28,40,42),fill=1,outline=12);d.line((33,30,33,35,38,37),fill=6)
    elif idx==6:
        d.arc((4,4,59,55),0,320,fill=5);d.arc((6,12,61,48),20,310,fill=14);d.ellipse((7,18+b,15,26+b),fill=4,outline=14)
        d.line((56,20,56,58),fill=12);d.polygon([(56,10),(60,17),(56,25),(52,17)],fill=4,outline=14)
    else:
        d.polygon([(22,10),(20,1),(28,7),(32,0),(36,7),(45,1),(42,11)],fill=12,outline=13)
        d.polygon([(32,28),(38,35),(32,44),(26,35)],fill=10,outline=14);d.line((32,30,32,42),fill=15)
        for yy in (26,39,49):d.line((3,yy,12,yy,15,yy+3),fill=14);d.line((49,yy+3,53,yy,62,yy),fill=14)
    return im

def extra_objects():
    out=old.OUT
    # Decode the existing 512-tile sheet, retaining wolf, bat and mist graphics.
    raw=(out/'sprites.chr').read_bytes();sheet=old.img(128,256)
    for ti in range(512):
        block=raw[ti*32:ti*32+32]
        for yy in range(8):
            for xx in range(8):
                v=sum(((block[(p//2)*16+yy*2+p%2]>>(7-xx))&1)<<p for p in range(4));sheet.putpixel((ti%16*8+xx,ti//16*8+yy),v)
    for k,kind in enumerate(('guard','sentinel','wisp')):
        for phase in range(2):sheet.paste(enemy_frame(kind,phase),(k*32+phase*16,96))
    for phase in range(2):
        dust=old.img(16,16);d=ImageDraw.Draw(dust)
        for i in range(8):
            x=(i*5+phase*3)%15;y=12-(i*3+phase*4)%9;d.point((x,y),fill=4 if i%3 else 5)
            if i%2:d.point((x+1 if x<15 else x,y),fill=3)
        sheet.paste(dust,(64+phase*16,64))
    (out/'sprites.chr').write_bytes(old.planar(sheet))
    (out/'sprites.pal').write_bytes(old.cgram(HERO))
    board=Image.new('RGB',(320,128),(5,6,15));frames=[]
    for i in range(10):
        for phase in range(2):
            im=boss_frame(i,phase);strip=old.img(128,32)
            # Four 32x32 objects packed as four columns across VRAM tile rows.
            for yy in range(2):
                for xx in range(2):strip.paste(im.crop((xx*32,yy*32,xx*32+32,yy*32+32)),((yy*2+xx)*32,0))
            frames.append(old.planar(strip))
        board.paste(old.palimg(boss_frame(i,0),HERO),(i%5*64,i//5*64))
    assert all(len(x)==2048 for x in frames)
    (out/'boss_frames0.chr').write_bytes(b''.join(frames[:16]));(out/'boss_frames1.chr').write_bytes(b''.join(frames[16:]))
    board.resize((960,384),Image.Resampling.NEAREST).save(out/'boss-revision-sheet.png')

if __name__=='__main__':extra_objects()
