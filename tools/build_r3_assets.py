#!/usr/bin/env python3
"""Build R3 side exits, distinct 64x64 bosses and animated ground enemies.
Source artwork and explicit room-port mappings are local, without network input.
Run after build_content.py and generate_graphics.py.
"""
from pathlib import Path
import json, struct
from PIL import Image, ImageDraw
R=Path(__file__).resolve().parents[1]

def planar(im):
    out=bytearray()
    for y in range(0,im.height,8):
        for x in range(0,im.width,8):
            pixels=list(im.crop((x,y,x+8,y+8)).getdata());t=bytearray(32)
            for yy in range(8):
                for xx in range(8):
                    v=pixels[yy*8+xx]
                    for b in range(4):t[(b//2)*16+yy*2+b%2]|=((v>>b)&1)<<(7-xx)
            out.extend(t)
    return bytes(out)

def cgram(colors):return b''.join(struct.pack('<H',(r>>3)|((g>>3)<<5)|((b>>3)<<10)) for r,g,b in colors)

rooms=json.loads((R/'assets/data.json').read_text())['rooms'];ids={r['id']:i for i,r in enumerate(rooms)}
ports=json.loads((R/'assets/source/room-ports-r3.json').read_text())
side=[];height=[];destside=[];destheight=[]
for i,(r,pp) in enumerate(zip(rooms,ports)):
    assert len(pp)==len(r['exits'])
    assert len({(p['side'],p['y']) for p in pp})==len(pp)
    for e,p in zip(r['exits'],pp):
        assert e['to']==p['to'] and p['side'] in (0,1) and p['y'] in (72,152)
        back=next(q for q in ports[ids[e['to']]] if q['to']==r['id'])
        assert back['side']!=p['side']
        side.append(p['side']);height.append(p['y']);destside.append(back['side']);destheight.append(back['y'])
    for _ in range(4-len(pp)):
        side.append(255);height.append(255);destside.append(255);destheight.append(255)
lines=['; R3 physical exits: same graph and gates, automatic edge crossing.']
for label,values in [('exit_side_r3',side),('exit_y_r3',height),('exit_dest_side_r3',destside),('exit_dest_y_r3',destheight)]:
    lines.append(label+':')
    lines.extend(' .byte '+','.join(map(str,values[i:i+16])) for i in range(0,len(values),16))
(R/'assets/edges-r3.inc').write_text('\n'.join(lines)+'\n')
# Recover each original drawing from the previous revision's authored source sheet.
sheet=Image.open(R/'assets/source/bosses-r3-source.png').convert('RGB')
if sheet.size==(320,128):
    sheet=sheet.resize((960,384),Image.Resampling.NEAREST)
assert sheet.size==(960,384)
chrdata=bytearray();pals=bytearray();preview=Image.new('RGB',(320,128))
for i in range(10):
    im=sheet.crop(((i%5)*192,(i//5)*192,(i%5+1)*192,(i//5+1)*192)).resize((64,64),Image.Resampling.NEAREST)
    bg=im.getpixel((0,0));colors=[c for n,c in sorted(im.getcolors(4096),reverse=True) if c!=bg]
    if len(colors)>15:
        q=im.quantize(colors=15,method=Image.Quantize.MEDIANCUT).convert('RGB');colors=[c for n,c in sorted(q.getcolors(4096),reverse=True) if c!=bg]
        # Keep a dedicated transparent mask even if quantization changed the backdrop.
    colors=colors[:15];pal=[bg]+colors+[(0,0,0)]*(15-len(colors))
    ix=Image.new('P',(64,64));vals=[]
    for c in im.getdata():
        vals.append(0 if c==bg else min(range(1,len(colors)+1),key=lambda k:sum((c[j]-pal[k][j])**2 for j in range(3))))
    ix.putdata(vals);chrdata.extend(planar(ix));pals.extend(cgram(pal));preview.paste(im,((i%5)*64,(i//5)*64))
(R/'assets/bosses-r3.chr').write_bytes(chrdata);(R/'assets/bosses-r3.pal').write_bytes(pals)
preview.resize((960,384),Image.Resampling.NEAREST).save(R/'assets/bosses-r3-preview.png')
# Decode original enemy drawings, then author four walking poses per ground class.
raw=bytearray((R/'assets/sprites.chr').read_bytes())
def decode_tile(n):
    t=raw[n*32:n*32+32];im=Image.new('P',(8,8))
    im.putdata([sum(((t[(b//2)*16+y*2+b%2]>>(7-x))&1)<<b for b in range(4)) for y in range(8) for x in range(8)])
    return im
for src,dst in [(192,192),(196,200),(200,384)]:
    base=Image.new('P',(16,32))
    for y in range(4):
        for x in range(2):base.paste(decode_tile(src+y*16+x),(x*8,y*8))
    # Save base now because frame upload may overlap another original sprite.
    if src==192:bases=[]
    bases.append((base,dst))
for base,dst in bases:
    for f in range(4):
        im=base.copy();d=ImageDraw.Draw(im)
        d.rectangle((2,23,13,31),fill=0)
        a,b=[(-2,2),(0,0),(2,-2),(0,0)][f]
        d.line((6,23,5+a,28,4+a,30),fill=4,width=2)
        d.line((10,23,10+b,27,11+b,30),fill=5,width=2)
        d.line((3+a,31,7+a,31),fill=6);d.line((9+b,31,13+b,31),fill=4)
        for y in range(4):
            for x in range(2):
                n=dst+f*2+y*16+x;raw[n*32:n*32+32]=planar(im.crop((x*8,y*8,x*8+8,y*8+8)))
(R/'assets/sprites.chr').write_bytes(raw)
print(json.dumps({'version':'R3','automatic_side_exits':len(side)-side.count(255),'rooms':len(rooms),'unique_bosses':10,'boss_size':[64,64],'boss_chr_bytes':len(chrdata),'ground_enemy_poses':12}))
