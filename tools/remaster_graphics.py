#!/usr/bin/env python3
"""Native SNES revision: coherent 32x48 doors, 32x48 streamed hero,
16 animation poses, shaded architecture, and per-tile 4bpp subpalettes.
All graphics are generated from original drawing instructions, not commercial assets.
"""
from pathlib import Path
import math, random, json, struct
import numpy as np
from PIL import Image, ImageDraw
import generate_graphics as old
OUT=old.OUT

def mix(a,b,t):return tuple(round(x*(1-t)+y*t) for x,y in zip(a,b))
def line(d,pts,c,w=1):d.line(pts,fill=c,width=w)
def scene(r):
    rng=random.Random(720+r); p=old.palettes[r]
    dark=(6,8,19);night=(12,18,36);stone=p[3];edge=p[5];gold=(156,116,66);ivory=(222,199,154)
    sky=[(7,12,30),(10,21,43),(16,34,60),(27,51,77),(40,70,96),(66,104,128)]
    im=Image.new('RGB',(256,224),dark);d=ImageDraw.Draw(im)
    # A single continuous night sky, not a moon repeated inside each window.
    for y in range(20,188):d.line((0,y,255,y),fill=mix(sky[0],sky[3],(y-20)/168))
    for i in range(84):
        x=rng.randrange(256);y=rng.randrange(24,148)
        d.point((x,y),fill=mix(sky[3],ivory,rng.random()*.7))
    d.ellipse((118,62,144,88),fill=(171,192,207));d.ellipse((126,59,148,81),fill=sky[1])
    for x in range(-8,264,17):
        h=rng.randrange(12,37);d.rectangle((x,184-h,x+12,184),fill=night)
        d.polygon([(x-2,184-h),(x+6,170-h),(x+14,184-h)],fill=night)
        for yy in range(189-h,175,8):d.rectangle((x+5,yy,x+6,yy+3),fill=sky[3])
    # Masonry surrounds individual windows. Natural joints and chiselled edges.
    walls=Image.new('RGB',(256,224),dark);wd=ImageDraw.Draw(walls)
    for row,y in enumerate(range(0,224,12)):
        for x in range(-16 if row%2 else 0,256,32):
            c=mix(p[2],p[3],rng.uniform(.15,.68));wd.rectangle((x+1,y+1,x+30,y+10),fill=c)
            wd.line((x+2,y+1,x+29,y+1),fill=mix(c,edge,.2));wd.line((x+30,y+2,x+30,y+10),fill=dark)
            for k in range(4):
                xx=x+rng.randrange(2,30);yy=y+rng.randrange(2,10)
                wd.point((xx,yy),fill=mix(c,edge,.10) if k%2 else mix(c,dark,.2))
    mask=Image.new('L',(256,224),255);md=ImageDraw.Draw(mask)
    for cx in (42,128,214):
        pts=[(cx-30,184),(cx-30,80),(cx-23,60),(cx,33),(cx+23,60),(cx+30,80),(cx+30,184)]
        md.polygon(pts,fill=0)
    im.paste(walls,(0,0),mask);d=ImageDraw.Draw(im)
    for cx in (42,128,214):
        for inset,c in [(0,dark),(2,p[4]),(4,mix(edge,ivory,.18)),(5,p[2]),(7,p[4])]:
            pts=[(cx-33+inset,184),(cx-33+inset,78),(cx-24+inset,58+inset),(cx,27+inset),(cx+24-inset,58+inset),(cx+33-inset,78),(cx+33-inset,184)]
            d.line(pts,fill=c,width=2 if inset in (0,2) else 1)
        # Fine tracery joins the arch, lit rim, mullions, and a recessed sill.
        d.line((cx,57,cx,182),fill=p[4],width=2);d.line((cx+1,58,cx+1,182),fill=mix(edge,p[7],.3))
        for yy in (96,140,180):
            d.rectangle((cx-25,yy,cx+25,yy+2),fill=p[2]);d.line((cx-25,yy,cx+25,yy),fill=p[4])
        d.arc((cx-23,56,cx,94),180,358,fill=p[4]);d.arc((cx,56,cx+23,94),182,360,fill=p[4])
        d.ellipse((cx-5,41,cx+5,52),outline=gold);d.line((cx,41,cx,52),fill=gold)
    # Region-specific objects in the middle distance.
    if r==1:
        for x in (13,96,181):
            d.rectangle((x,83,x+61,183),fill=(24,14,26),outline=gold)
            for yy in (105,129,153,178):
                bx=x+3
                while bx<x+57:
                    width=rng.randrange(3,6);h=rng.randrange(12,22);c=rng.choice([p[4],p[9],p[10],p[12],p[6]])
                    d.rectangle((bx,yy-h,bx+width-1,yy),fill=c);d.line((bx,yy-h,bx,yy),fill=mix(c,ivory,.2));
                    d.line((bx,yy-h+3,bx+width-2,yy-h+3),fill=gold);bx+=width+1
                d.rectangle((x+1,yy+1,x+60,yy+3),fill=p[3]);d.line((x,yy+1,x+61,yy+1),fill=gold)
    elif r==2:
        for x in (3,80,167,248):
            points=[(x+int(math.sin(y*.11)*4),y) for y in range(40,184,2)];d.line(points,fill=p[7],width=2)
            for yy in range(52,185,12):
                for side in (-1,1):
                    xx=x+int(math.sin(yy*.11)*4);d.polygon([(xx,yy),(xx+side*11,yy-6),(xx+side*7,yy+2)],fill=p[4]);d.line((xx,yy,xx+side*9,yy-4),fill=p[7])
                if yy%3==1:d.ellipse((x-3,yy-4,x+2,yy),fill=p[12])
    elif r==3:
        for x in (19,76,178,234):
            d.rectangle((x,35,x+7,183),fill=p[2],outline=p[5]);d.line((x+2,38,x+2,183),fill=p[7]);d.line((x+5,38,x+5,183),fill=dark)
            for yy in range(50,182,30):d.rectangle((x-2,yy,x+9,yy+4),fill=p[4],outline=p[5])
        for y in range(170,184,3):
            for x in range((y*3)%15,256,25):d.line((x,y,x+14,y),fill=p[7])
    elif r==4:
        for cx in (42,128,214):
            d.polygon([(cx-23,183),(cx-23,106),(cx,87),(cx+23,106),(cx+23,183)],fill=dark,outline=p[5])
            for i in range(18):
                x=cx+rng.randrange(-19,19);h=rng.randrange(8,54);d.polygon([(x-4,182),(x,182-h),(x+5,182)],fill=rng.choice([p[9],p[10],p[12],p[14]]))
            for x in range(cx-20,cx+21,6):d.line((x,106,x,184),fill=p[3],width=2);d.line((x+1,106,x+1,184),fill=p[5])
    elif r==5:
        # Teeth, concentric shaded rings, spokes, and pendulum behind the player.
        for cx,cy,rr in [(43,111,33),(210,92,30),(79,54,17),(173,161,21)]:
            pts=[]
            for k in range(96):
                a=k*math.tau/96;rad=rr if k%8 in (0,1,6,7) else rr-3;pts.append((round(cx+math.cos(a)*rad),round(cy+math.sin(a)*rad)))
            d.polygon(pts,fill=gold,outline=ivory);d.ellipse((cx-rr+5,cy-rr+5,cx+rr-5,cy+rr-5),fill=p[2],outline=p[5])
            for k in range(8):
                a=k*math.tau/8;d.line((cx,cy,cx+round(math.cos(a)*(rr-7)),cy+round(math.sin(a)*(rr-7))),fill=gold,width=2)
            d.ellipse((cx-5,cy-5,cx+5,cy+5),fill=p[4],outline=ivory)
        d.ellipse((96,62,161,127),fill=gold,outline=ivory);d.ellipse((100,66,157,123),fill=p[2],outline=p[5])
        for k in range(12):
            a=k*math.tau/12;x=128+round(math.sin(a)*24);y=94-round(math.cos(a)*24);d.rectangle((x,y,x+1,y+2),fill=ivory)
        d.line((128,75,128,94,145,101),fill=ivory,width=2)
        d.line((129,128,129,170),fill=p[5],width=2);d.ellipse((122,168,135,181),fill=gold,outline=ivory)
    elif r==6:
        for rr,c in [(40,p[4]),(34,gold),(28,p[7])]:d.ellipse((128-rr,112-rr,128+rr,112+rr),outline=c)
        d.line((93,166,162,64),fill=p[4],width=10);d.line((97,166,164,66),fill=p[5],width=3)
        d.line((103,184,125,143,151,184),fill=gold,width=3);d.ellipse((111,91,147,126),outline=ivory)
    elif r==7:
        for x in (13,51,80,177,210,245):
            yy=rng.randrange(74,140);d.line((x,35,x,yy,x+7,yy+7,x+7,183),fill=p[7]);d.rectangle((x-2,yy-2,x+2,yy+2),fill=p[14])
        d.polygon([(100,183),(94,143),(102,83),(128,62),(154,83),(162,143),(155,183)],fill=p[2],outline=p[5])
        for k in range(5):
            w=22-k*3;d.polygon([(128,83+k*5),(128+w,120),(128,157-k*5),(128-w,120)],outline=p[12] if k%2 else p[14])
        d.ellipse((122,113,134,125),fill=ivory)
    # Tall pillars, carved capitals, small sculptures and metallic circuitry.
    for x in (0,85,170,255):
        d.rectangle((x-6,23,x+6,185),fill=dark)
        for dx,c in [(-5,p[2]),(-4,p[3]),(-2,p[5]),(-1,p[4]),(1,p[3]),(3,p[2]),(5,p[4])]:d.line((x+dx,27,x+dx,184),fill=c,width=2)
        for yy in (26,30,178,181):d.rectangle((x-8,yy,x+8,yy+2),fill=p[4]);d.line((x-8,yy,x+8,yy),fill=gold)
        d.polygon([(x-6,31),(x,38),(x+6,31)],fill=p[3],outline=p[5])
    for x in (11,94,177,244):
        d.line((x,129,x+5,129,x+5,122),fill=gold);d.rectangle((x+3,121,x+7,122),fill=p[5])
        d.line((x+5,116,x+5,120),fill=ivory);d.point((x+4,116),fill=p[10]);d.point((x+5,114),fill=ivory)
    # Recessed stone floor and gilded edge instead of tall black HUD footer.
    for y in range(184,224):d.line((0,y,255,y),fill=mix(p[3],dark,(y-184)/40))
    for y in range(187,224,9):
        d.line((0,y,255,y),fill=p[4] if y==187 else p[2])
        for x in range((y%2)*15,256,30):d.line((x,y,x+3,y+8),fill=dark)
    d.line((0,184,255,184),fill=gold);d.line((0,185,255,185),fill=p[5])
    # HUD is composed later, only reserve the top two rows here.
    d.rectangle((0,0,255,15),fill=dark)
    return im

def door():
    im=old.img(32,48);d=ImageDraw.Draw(im)
    # Single continuous arched doorway, 24 distinct tiles, correctly assembled.
    d.polygon([(1,47),(1,17),(4,10),(15,0),(27,10),(30,17),(30,47)],fill=2,outline=5)
    d.line([(3,47),(3,18),(6,12),(15,4),(25,12),(28,18),(28,47)],fill=10,width=2)
    d.polygon([(6,47),(6,19),(9,14),(15,9),(22,15),(25,20),(25,47)],fill=1,outline=4)
    d.polygon([(8,45),(8,21),(11,17),(15,14),(21,18),(23,22),(23,45)],fill=6)
    for x in (9,13,17,21):d.line((x,22,x,44),fill=7 if x%3 else 2)
    d.line((15,17,15,44),fill=2);d.rectangle((13,31,14,32),fill=10);d.point((18,31),fill=14)
    for x in (3,27):
        for y in (24,39):d.rectangle((x-1,y,x+1,y+2),fill=5)
    d.rectangle((0,45,31,47),fill=3);d.line((0,45,31,45),fill=10)
    d.ellipse((13,5,17,9),fill=14,outline=7)
    return im

def hero(frame):
    im=old.img(32,48);d=ImageDraw.Draw(im)
    walking=2<=frame<10;phase=(frame-2)*math.tau/8 if walking else 0
    bob=round(math.sin(phase*2)*.7) if walking else (frame&1)
    attacking=frame in (10,11);jumping=frame in (12,13);dashing=frame==14
    hx=16+(2 if attacking else 0)+(2 if dashing else 0);hy=3+bob+(3 if dashing else 0)
    # Articulated back leg and foreground leg, hips, knees and ankles.
    lift=[0,2,4,5,0,0,0,0][(frame-2)%8] if walking else 0
    legs=[]
    for j in (0,1):
        a=phase+j*math.pi;hip=(16+j*2,29+bob)
        knee=(round(16+math.sin(a)*5),round(37+bob-math.cos(a)*1.5))
        ankle=(round(17+math.sin(a)*9),45-max(0,round(math.cos(a)*5)) if walking else 45)
        if jumping:knee=(12+j*9,33+j*3);ankle=(9+j*13,40+j*4)
        if dashing:knee=(10+j*13,35+j*3);ankle=(4+j*24,43)
        d.line([hip,knee,ankle],fill=1,width=6);d.line([hip,knee,ankle],fill=2 if j==0 else 3,width=4)
        d.line([hip,knee,ankle],fill=3 if j==0 else 4,width=2)
        ax,ay=ankle;d.rectangle((ax-2,ay-2,ax+4,ay),fill=2);d.line((ax-2,ay,ax+5,ay),fill=5 if j else 4)
    # Flowing double-layer cloak with folds; deliberately clear of the leg silhouette.
    sway=round(math.sin(phase)*3) if walking else frame%2
    cloak=[(hx-3,13+hy),(10,17+hy),(5-sway,27),(2,37),(8-sway,41),(13,35),(16,23)]
    d.polygon(cloak,fill=9,outline=1)
    d.polygon([(hx-4,15+hy),(10,20),(5-sway,35),(7-sway,38),(11,31)],fill=10)
    d.line([(11,20),(8-sway,31),(5-sway,37)],fill=11)
    d.line([(13,19),(11,32),(9,37)],fill=10)
    # Dark embroidered coat, fitted waist and separate coat tails.
    d.polygon([(hx-5,hy+11),(hx+4,hy+11),(hx+7,hy+17),(hx+4,28+bob),(hx+7,34),(16,32),(11,35),(11,22)],fill=1)
    d.polygon([(hx-4,hy+12),(hx+3,hy+12),(hx+4,hy+18),(hx+2,28),(13,29),(12,22)],fill=3)
    d.polygon([(hx-2,hy+12),(hx+2,hy+12),(hx+1,25),(14,25)],fill=5)
    d.line((hx-3,hy+14,hx-3,27),fill=12);d.line((hx+3,hy+14,hx+2,27),fill=12)
    for yy in (20,23,26):d.point((hx+1,yy+bob),fill=13)
    d.rectangle((12,28,21,30),fill=1);d.line((12,28,21,28),fill=12);d.rectangle((17,28,19,30),fill=13)
    # Face in profile with a distinct eye, jaw, ear and hair layers.
    d.polygon([(hx-3,hy+2),(hx+3,hy+2),(hx+4,hy+5),(hx+6,hy+7),(hx+4,hy+8),(hx+3,hy+11),(hx-1,hy+11),(hx-3,hy+8)],fill=8)
    d.polygon([(hx-2,hy+3),(hx+2,hy+3),(hx+3,hy+8),(hx+1,hy+10),(hx-1,hy+8)],fill=7)
    d.point((hx+3,hy+5),fill=1);d.point((hx+2,hy+5),fill=6);d.line((hx+3,hy+9,hx+4,hy+9),fill=8)
    d.polygon([(hx-5,hy+3),(hx-3,hy),(hx+2,hy-1),(hx+5,hy+1),(hx+4,hy+3),(hx,hy+3),(hx-2,hy+7),(hx-3,hy+13),(hx-7,hy+18),(hx-8,hy+16),(hx-6,hy+9)],fill=4,outline=3)
    d.line([(hx-5,hy+5),(hx-4,hy+2),(hx,hy),(hx+3,hy+1)],fill=6)
    d.line([(hx-3,hy+4),(hx-4,hy+11),(hx-7,hy+15)],fill=5)
    d.line([(hx-5,hy+8),(hx-6,hy+13),(hx-8,hy+17)],fill=5)
    # Separate articulated sword arm, not a static rectangle while walking.
    shoulder=(hx+3,hy+14)
    elbow=(hx+6,hy+20);hand=(hx+5,hy+24)
    if walking:elbow=(hx+5-round(math.sin(phase)*2),hy+19);hand=(hx+5-round(math.sin(phase)*3),hy+24)
    if attacking:elbow=(24,18 if frame==10 else 23);hand=(29,13 if frame==10 else 25)
    d.line([shoulder,elbow,hand],fill=1,width=5);d.line([shoulder,elbow],fill=4,width=3);d.line([elbow,hand],fill=3,width=3)
    d.rectangle((hand[0]-1,hand[1]-1,hand[0]+1,hand[1]+1),fill=7)
    if not attacking:
        d.line((hand[0]+1,hand[1]+2,hand[0]+6,hand[1]+10),fill=5);d.line((hand[0]-1,hand[1]+3,hand[0]+3,hand[1]+1),fill=13)
    return im

def tile_encode_scene(im,p0):
    arr=np.asarray(im,dtype=np.int16); dark=(6,8,19)
    # Per-tile local subpalettes selected from image colour clusters. The HUD
    # always uses palette zero, so scenery can have colour without tinting text.
    q=im.quantize(colors=96,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE)
    colors=q.getpalette()[:288];cs=[tuple(colors[i:i+3]) for i in range(0,len(colors),3)]
    groups=[cs[i:i+15] for i in range(0,90,15)]
    pals=[p0]+[[dark]+g+[dark]*(15-len(g)) for g in groups]
    # A global reduced palette gives each subpalette dark, midtone and highlight.
    base16=im.quantize(colors=15,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE).getpalette()[:45]
    pals.append([dark]+[tuple(base16[i:i+3]) for i in range(0,45,3)])
    pa=np.asarray(pals,dtype=np.int32);cache={};tiles=[];mapping={};entries=[]
    common=old.common_tiles();common.extend([door().crop((x,y,x+8,y+8)) for y in range(0,48,8) for x in range(0,32,8)])
    while len(common)<160:common.append(old.img(8,8))
    shared=b''.join(old.planar(t) for t in common)
    for y in range(0,256,8):
        for x in range(0,256,8):
            if y>=224:entries.append(0);continue
            t=arr[y:y+8,x:x+8,:].reshape(-1,3).astype(np.int32);key=t.tobytes()
            if key not in cache:
                dist=((t[None,:,None,:]-pa[:,None,:,:])**2).sum(axis=3)
                indices=dist.argmin(axis=2);err=dist.min(axis=2).sum(axis=1);pi=int(err.argmin())
                indexed=Image.fromarray(indices[pi].reshape(8,8).astype('uint8'),mode='P');enc=old.planar(indexed)
                if enc not in mapping:mapping[enc]=160+len(tiles);tiles.append(enc)
                cache[key]=mapping[enc]|(pi<<10)
            entries.append(cache[key])
    assert 160+len(tiles)<=1024,(160+len(tiles))
    return (shared+b''.join(tiles)).ljust(32768,b'\0'),struct.pack('<1024H',*entries),b''.join(old.cgram(p) for p in pals),pals,entries

def main():
    # Preserve original enemy/boss and soundtrack inputs; rebuild before upgrade.
    old.main();manifest=json.loads((OUT/'graphics-layout.json').read_text())
    framebytes=[]
    for f in range(16):
        im=hero(f);framebytes.append(old.planar(im))
        rgba=old.palimg(im,old.spal).convert('RGBA');rgba.putalpha(im.point(lambda x:255 if x else 0).convert('L'))
        rgba.save(OUT/f'hero-v2-{f:02d}.png')
    (OUT/'hero-frames.chr').write_bytes(b''.join(framebytes))
    # Rebuild OBJ table with non-overlapping reserved hero streaming tiles.
    sheet=old.img(128,256)
    sheet.paste(hero(0),(0,0))
    for name,im,x,y in [('wolf_0',old.wolf(0),0,48),('wolf_1',old.wolf(1),32,48),('bat_0',old.bat(0),64,48),('bat_1',old.bat(1),96,48),('mist_0',old.mist(0),0,64),('mist_1',old.mist(1),32,64)]:sheet.paste(im,(x,y))
    for i,kind in enumerate(['guard','archer','sentinel','beast','wisp']):
        im=old.enemy(kind);sheet.paste(im,(i*16,96))
    for i,kind in enumerate(['guard','sentinel','wisp']):
        im=old.enemy(kind);d=ImageDraw.Draw(im)
        if kind!='wisp':
            d.rectangle((0,24,15,31),fill=0);d.line((6,23,4,27,2,30),fill=4,width=3);d.line((10,23,12,27,13,29),fill=5,width=3);d.line((1,31,6,31),fill=5)
        sheet.paste(im,(64+i*16,64))
    for i in range(10):sheet.paste(old.boss(i),((i%4)*32,128+(i//4)*32))
    original=(OUT/'sprites.chr').read_bytes();new=bytearray(old.planar(sheet));new[448*32:]=original[448*32:]
    (OUT/'sprites.chr').write_bytes(new)
    previews=[]
    for r in range(8):
        im=scene(r);ch,mapb,pal,pals,entries=tile_encode_scene(im,old.palettes[r]);
        (OUT/f'bg_region{r}.chr').write_bytes(ch);(OUT/f'bg_region{r}.map').write_bytes(mapb);(OUT/f'bg_region{r}.pal').write_bytes(pal)
        im.save(OUT/f'bg_region{r}.png');previews.append(im)
        manifest['regions'][r]['paletteBytes']=256;manifest['regions'][r]['tiles']=max(t&1023 for t in entries)+1
    manifest['revision']='2.0';manifest['hero']={'width':32,'height':48,'frames':16,'frameBytes':768,'method':'VRAM row DMA streaming'}
    manifest['door']={'tile':128,'columns':4,'rows':6,'distinctTiles':24}
    (OUT/'graphics-layout-v2.json').write_text(json.dumps(manifest,indent=2))
    print('V2 assets:',len(b''.join(framebytes)),'hero bytes; 8 scenes with 8 subpalettes each')
if __name__=='__main__':main()
