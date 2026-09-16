#!/usr/bin/env python3
"""Revision 1.1: larger animated hero, coherent portals and native multi-palette art.
The original pixel generator is retained so the initial art remains reproducible.
No scaling of small sprites: the protagonist is newly drawn at 32 x 48 pixels.
"""
from pathlib import Path
import json, math, struct, random
from PIL import Image, ImageDraw
import generate_graphics as g

OUT=g.OUT

def protagonist(frame):
    im=g.img(32,48);d=ImageDraw.Draw(im)
    run=2<=frame<=9
    phase=(frame-2)*math.pi/4 if run else 0
    stride=round(math.sin(phase)*7) if run else 0
    bob=1 if run and frame%4 in (0,1) else 0
    if frame==1:bob=1
    jump=frame in (10,11)
    attacking=frame in (12,13,14)
    lean=1 if run or attacking else 0
    # Back leg, layered before the coat; articulated knee and ankle.
    hx,hy=17+lean,29+bob
    knee=(16-stride//2,37-abs(stride)//3)
    ankle=(16-stride,45-abs(stride)//3)
    if jump:knee=(12,35);ankle=(9,40)
    d.line([(hx,hy),knee,ankle],fill=1,width=5)
    d.line([(hx-1,hy),knee,ankle],fill=3,width=2)
    d.line((ankle[0]-1,ankle[1],ankle[0]+4,ankle[1]),fill=4,width=2)
    d.point((ankle[0]+4,ankle[1]-1),fill=5)
    # Cape trails with an eight-frame travelling wave, not a translated rectangle.
    wave=round(math.sin(phase+.7)*3) if run else frame%2
    cape=[(15+lean,13+bob),(11,15),(8,23),(5,30),(2+wave,37),(7+wave,39),(13,35),(17,24),(20,16)]
    d.polygon(cape,fill=9,outline=1)
    d.polygon([(13,17),(10,25),(7,33),(4+wave,36),(8+wave,37),(13,29),(16,18)],fill=10)
    d.line([(12,19),(10,28),(8+wave,36)],fill=11)
    d.line([(15,18),(14,27),(11,33)],fill=3)
    # Front boot uses an independently bent knee and grounded sole.
    knee=(20+stride//2,37-abs(stride)//4)
    ankle=(20+stride,45)
    if run and stride<0:ankle=(20+stride,41)
    if jump:knee=(24,34);ankle=(22,40)
    d.line([(20+lean,28+bob),knee,ankle],fill=1,width=5)
    d.line([(20+lean,29+bob),knee,ankle],fill=3,width=3)
    d.line((knee[0]+1,knee[1],ankle[0]+1,ankle[1]-1),fill=4)
    d.line((ankle[0]-1,ankle[1],ankle[0]+4,ankle[1]),fill=5,width=2)
    d.line((ankle[0]-2,ankle[1]+1,ankle[0]+4,ankle[1]+1),fill=1)
    # Fitted dark coat, split tails and silver shoulder protection.
    d.polygon([(15+lean,14+bob),(21+lean,14+bob),(24,20+bob),(21,26+bob),(24,34),(19,33),(17,28),(15,34),(11,33),(14,23)],fill=2,outline=1)
    d.line((16+lean,17+bob,15,29),fill=4)
    d.line((18+lean,17+bob,18,29),fill=12)
    d.line((19+lean,17+bob,19,26),fill=13)
    for y in (19,23,26):d.point((19+lean,y+bob),fill=6)
    d.polygon([(14+lean,14+bob),(18,14+bob),(16,18+bob),(13,18+bob)],fill=4,outline=5)
    d.line((13,16+bob,16,15+bob),fill=6)
    d.rectangle((14,27+bob,22,28+bob),fill=1)
    d.rectangle((18,27+bob,19,28+bob),fill=13)
    # Face and long silver hair, three highlight levels and a one-pixel eye.
    d.polygon([(17+lean,6+bob),(22+lean,6+bob),(23+lean,10+bob),(21+lean,13+bob),(18+lean,12+bob)],fill=8)
    d.polygon([(18+lean,6+bob),(22+lean,6+bob),(22+lean,11+bob),(20+lean,12+bob),(18+lean,10+bob)],fill=7)
    d.point((22+lean,8+bob),fill=1)
    d.point((23+lean,10+bob),fill=7)
    d.line((19+lean,13+bob,21+lean,13+bob),fill=7)
    d.polygon([(14+lean,6+bob),(17+lean,3+bob),(22+lean,3+bob),(24+lean,6+bob),(20+lean,6+bob),(17+lean,9+bob),(16,14+bob),(12,19),(10,20),(12,15),(12,9)],fill=3,outline=1)
    d.line([(14+lean,7+bob),(16+lean,5+bob),(20+lean,4+bob),(23+lean,5+bob)],fill=6)
    d.line([(15+lean,7+bob),(14,12+bob),(13,17)],fill=5,width=2)
    d.line([(17+lean,6+bob),(16,12+bob),(14,15)],fill=4)
    # Front arm has separate anticipation, extension and follow-through poses.
    shoulder=(22+lean,17+bob)
    elbow=(23,22+bob);hand=(24,27+bob)
    if run:elbow=(23-stride//3,23+bob);hand=(22-stride//2,27+bob)
    if jump:elbow=(25,20);hand=(27,22)
    if frame==12:elbow=(21,14);hand=(19,11)
    if frame==13:elbow=(26,18);hand=(30,19)
    if frame==14:elbow=(25,23);hand=(29,27)
    d.line([shoulder,elbow,hand],fill=1,width=5)
    d.line([shoulder,elbow,hand],fill=3,width=3)
    d.line([shoulder,elbow],fill=5,width=2)
    d.rectangle((hand[0]-1,hand[1]-1,hand[0]+1,hand[1]+1),fill=7)
    if not attacking:
        d.line((hand[0]+1,hand[1]+2,min(31,hand[0]+5),hand[1]+9),fill=5)
        d.line((hand[0]-1,hand[1]+3,hand[0]+3,hand[1]+1),fill=12)
    else:
        d.line((hand[0]-2,hand[1]+2,hand[0]+2,hand[1]-2),fill=13)
    return im

def doorway(secret=False):
    im=g.img(32,40);d=ImageDraw.Draw(im)
    if secret:
        d.rectangle((0,0,31,39),fill=2)
        for y in range(0,40,8):
            d.line((0,y,31,y),fill=1)
            for x in range((-8 if y%16 else 0),32,16):
                d.line((x,y,x,y+7),fill=1)
                d.line((x+1,y+1,x+14,y+1),fill=3)
        d.line([(16,7),(14,12),(18,17),(15,23),(17,28),(14,33)],fill=1)
        d.point((19,19),fill=4)
        return im
    # Single pointed portal, each tile is a different piece of the same arch.
    d.polygon([(1,39),(1,16),(4,9),(15,0),(26,9),(30,16),(30,39)],fill=1)
    d.polygon([(3,39),(3,15),(7,9),(15,3),(24,9),(28,15),(28,39)],fill=4,outline=5)
    d.polygon([(7,39),(7,17),(10,12),(15,8),(21,12),(24,17),(24,39)],fill=0,outline=10)
    d.polygon([(9,38),(9,18),(12,14),(15,11),(19,14),(22,18),(22,38)],fill=6)
    d.polygon([(11,37),(11,20),(16,15),(20,20),(20,37)],fill=1)
    d.line((15,18,15,36),fill=7)
    d.line((16,18,16,36),fill=14)
    for y in (18,25,32):
        d.line((3,y,6,y),fill=1);d.line((25,y,28,y),fill=1)
        d.line((3,y+1,6,y+1),fill=5);d.line((25,y+1,28,y+1),fill=5)
    d.line([(4,15),(8,10),(15,5),(23,10),(27,15)],fill=11)
    d.polygon([(14,4),(16,4),(17,8),(15,10),(13,8)],fill=10)
    d.point((15,6),fill=13)
    d.rectangle((1,37,30,39),fill=3);d.line((1,37,30,37),fill=10)
    d.line((4,38,27,38),fill=5)
    return im

def enhanced_background(region):
    im=g.background(region).copy();d=ImageDraw.Draw(im);rng=random.Random(619+region)
    # A subtle deterministic masonry grain only on wall pixels, not characters.
    for y in range(33,184):
        for x in range(256):
            c=im.getpixel((x,y))
            if c in (1,2) and rng.random()<.027:
                im.putpixel((x,y),2 if c==1 else 3)
    # Contoured stone columns with narrow reflected moonlight.
    for x in (7,87,167,247):
        d.rectangle((x-4,39,x+4,182),fill=3)
        d.line((x-4,39,x-4,182),fill=2)
        d.line((x-2,39,x-2,182),fill=5)
        d.line((x-1,39,x-1,182),fill=4)
        d.line((x+2,39,x+2,182),fill=2)
        for y in range(49,182,14):
            d.line((x-3,y,x+3,y),fill=2)
            d.point((x-2,y+1),fill=5)
        d.rectangle((x-7,38,x+7,40),fill=5)
        d.rectangle((x-6,41,x+6,43),fill=4)
    if region==0:
        # Side windows become stained glass instead of three identical moons.
        for wx in (24,184):
            d.rectangle((wx+7,80,wx+41,112),fill=6)
            for yy in range(80,112,8):
                for xx in range(wx+7,wx+42,8):
                    d.polygon([(xx+4,yy),(xx+7,yy+4),(xx+4,yy+7),(xx,yy+4)],fill=7 if (xx+yy)%3 else 13)
            d.line((wx+24,60,wx+24,176),fill=4,width=2)
        for x in (48,128,208):
            d.line([(x-22,75),(x-22,70),(x,40),(x+22,70),(x+22,75)],fill=5)
            d.line([(x-20,75),(x-20,70),(x,43),(x+20,70),(x+20,75)],fill=3)
    # A lower stone frieze with inset panels and thin circuit inlays.
    for x in range(0,256,32):
        d.rectangle((x,193,x+31,206),fill=3,outline=2)
        d.rectangle((x+3,196,x+27,202),fill=1,outline=4)
        d.line((x+5,197,x+25,197),fill=2)
        d.line((x,191,x+31,191),fill=5)
        d.point((x+15,204),fill=10)
    d.rectangle((0,0,255,31),fill=0)
    d.rectangle((0,200,255,223),fill=0)
    return im

def background_banks(region):
    p=g.palettes[region]
    front=[g.rgb(v) for v in ['080917','101328','212537','34374b','55566d','8c87a2','164756','357b91','261d2f','55394a','bb9360','ada1b0','a33869','f2d4a1','89e4ed','fff0d1']]
    # Eight BG banks, first four used for walls, architecture and light shading.
    dark=[tuple(round(v*.70) for v in c) for c in p]
    light=[tuple(min(255,round(v*1.16+3)) for v in c) for c in p]
    dark[0]=p[0];light[0]=p[0]
    return [p,front,dark,light,p,p,p,front]

def main():
    # Generate original non-hero enemies, bosses, music-compatible metadata first.
    g.main()
    from refine_enemies import apply
    apply()
    shared=g.common_tiles()
    for secret in (False,True):
        portal=doorway(secret)
        for y in range(0,40,8):
            for x in range(0,32,8):shared.append(portal.crop((x,y,x+8,y+8)))
    while len(shared)<256:shared.append(g.img(8,8))
    raw_shared=b''.join(g.planar(t) for t in shared)
    (OUT/'bg_common.chr').write_bytes(raw_shared)
    manifests=[];previews=[];allpal=[]
    for region in range(8):
        bg=enhanced_background(region);banks=background_banks(region)
        data=[g.planar(t) for t in shared];mapping={v:i for i,v in enumerate(data)}
        tilemap=[];preview=Image.new('RGB',(256,224))
        for y in range(0,256,8):
            for x in range(0,256,8):
                if y>=224:tilemap.append(0);continue
                t=bg.crop((x,y,x+8,y+8));raw=g.planar(t)
                if raw not in mapping:mapping[raw]=len(data);data.append(raw)
                n=mapping[raw]
                # Tile-aligned native palette variation keeps identical ink indices.
                bank=0
                if y>=32 and y<184:
                    if x%80 in (0,8,72):bank=3
                    elif y>=168:bank=2
                tilemap.append(n|(bank<<10))
                preview.paste(g.palimg(t,banks[bank]),(x,y))
        assert len(data)<=1024,(region,len(data))
        (OUT/f'bg_region{region}.chr').write_bytes(b''.join(data).ljust(32768,b'\0'))
        (OUT/f'bg_region{region}.map').write_bytes(struct.pack('<1024H',*tilemap))
        pals=b''.join(g.cgram(p) for p in banks);allpal.append(pals)
        (OUT/f'bg_region{region}.pal').write_bytes(pals)
        preview.resize((768,672),Image.Resampling.NEAREST).save(OUT/f'bg_region{region}.png')
        previews.append(preview)
        manifests.append({'region':region,'tiles':len(data),'palette_banks':8})
    (OUT/'bg_palettes.pal').write_bytes(b''.join(allpal))
    frames=[];sheet=Image.new('RGB',(32*8,48*2),(9,12,23))
    for f in range(16):
        hero=protagonist(f);native=g.img(128,32)
        native.paste(hero.crop((0,0,32,32)),(0,0))
        native.paste(hero.crop((0,32,32,48)),(32,0))
        block=g.planar(native);assert len(block)==2048
        frames.append(block)
        rgb=g.palimg(hero,g.spal);mask=hero.point(lambda x:255 if x else 0).convert('L')
        sheet.paste(rgb,((f%8)*32,(f//8)*48),mask)
    (OUT/'hero-frames.chr').write_bytes(b''.join(frames))
    flash=[g.spal[0]]+[tuple(min(255,round(v*.4+145)) for v in c) for c in g.spal[1:]]
    pal=(OUT/'sprite_palettes.pal').read_bytes()
    (OUT/'sprite_palettes.pal').write_bytes(pal[:224]+g.cgram(flash))
    sheet.resize((1024,384),Image.Resampling.NEAREST).save(OUT/'hero-animation-preview.png')
    board=Image.new('RGB',(768,672*4))
    for i,im in enumerate(previews):board.paste(im.resize((384,336),Image.Resampling.NEAREST),((i%2)*384,(i//2)*336))
    board.crop((0,0,768,1344)).save(OUT/'regions-preview.png')
    (OUT/'graphics-revision.json').write_text(json.dumps({'version':'1.1','hero_frames':16,'hero_canvas':[32,48],'hero_dma_bytes':2048,'regions':manifests,'portal_tile_range':[128,147],'secret_tile_range':[148,167]},indent=2)+'\n')
    print(json.dumps({'revision':'1.1','regions':manifests,'hero_frames':16}))
if __name__=='__main__':main()
