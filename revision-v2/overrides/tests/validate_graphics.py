#!/usr/bin/env python3
"""Validate v2 native 4bpp pixels, tile flips, OBJ slots and door metatiles."""
from pathlib import Path
import json, struct, sys
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import generate_graphics as g
import graphics_v2 as v2

def decode_tile(data):
    if len(data)!=32: raise ValueError('A 4bpp tile requires 32 bytes')
    out=Image.new('P',(8,8))
    for y in range(8):
        for x in range(8):
            value=sum(((data[(p//2)*16+y*2+p%2]>>(7-x))&1)<<p for p in range(4))
            out.putpixel((x,y),value)
    return out

def decode_map(chrdata,mapdata):
    out=Image.new('P',(256,256));entries=struct.unpack('<1024H',mapdata)
    for i,word in enumerate(entries):
        tile=word&1023
        assert (tile+1)*32<=len(chrdata)
        im=decode_tile(chrdata[tile*32:(tile+1)*32])
        if word&0x4000:im=im.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        if word&0x8000:im=im.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        out.paste(im,((i%32)*8,(i//32)*8))
    return out

def main():
    assets=ROOT/'assets';layout=json.loads((assets/'graphics-layout.json').read_text())
    assert layout['version']==2 and layout['hero_poses']==16 and layout['hero_size']==[32,48]
    for r in range(8):
        fg=(assets/f'bg_region{r}.chr').read_bytes();far=(assets/f'far_region{r}.chr').read_bytes()
        assert len(fg)==32768 and len(far)==8192
        expected=Image.new('P',(256,256));expected.paste(v2.architecture(r),(0,0))
        assert decode_map(fg,(assets/f'bg_region{r}.map').read_bytes()).tobytes()==expected.tobytes(),f'foreground {r}'
        assert decode_map(far,(assets/f'far_region{r}.map').read_bytes()).tobytes()==v2.distant(r).tobytes(),f'sky {r}'
        palette=(assets/f'bg_region{r}.pal').read_bytes()
        assert len(palette)==128 and all(n<32768 for n in struct.unpack('<64H',palette))
    common=v2.common_tiles();encoded=(assets/'bg_common.chr').read_bytes()
    assert len(common)==224 and len(encoded)==224*32
    for i,im in enumerate(common):assert decode_tile(encoded[i*32:(i+1)*32]).tobytes()==im.tobytes()
    for name,kind in [('open',0),('closed',1),('secret',2)]:
        start=layout['doors'][name];im=Image.new('P',(24,40))
        for i in range(15):im.paste(decode_tile(encoded[(start+i)*32:(start+i+1)*32]),((i%3)*8,(i//3)*8))
        assert im.tobytes()==v2.door(kind).tobytes(),name
        assert len({encoded[(start+i)*32:(start+i+1)*32] for i in range(15)}) >= (3 if name=='secret' else 6), 'Repeated whole-door tiles'
    hero=(assets/'hero-frames.chr').read_bytes();assert len(hero)==16*768
    for frame in range(16):
        im=Image.new('P',(32,48))
        for i in range(24):im.paste(decode_tile(hero[frame*768+i*32:frame*768+(i+1)*32]),((i%4)*8,(i//4)*8))
        assert im.tobytes()==v2.hero_pose(frame).tobytes(),f'hero pose {frame}'
    assert len({hero[i*768:(i+1)*768] for i in range(16)})==16
    assert len((assets/'sprites.chr').read_bytes())==16384
    assert len((assets/'sprite_palettes.pal').read_bytes())==256
    # The six live 16x16 hero pieces must not overwrite neighboring form tiles.
    occupied=set()
    for item in layout['sprites'].values():
        coords={(item['x']//8+x,item['y']//8+y) for y in range(item['height']//8) for x in range(item['width']//8)}
        assert not occupied.intersection(coords),'Overlapping OBJ allocations'
        occupied.update(coords)
    report={'passed':True,'backgrounds':8,'layers_per_region':2,'hero_poses':16,'hero_pixels':[32,48],
            'door_metatiles':[3,5],'common_tiles':224,'obj_overlaps':0,'pixel_roundtrip':'exact, including H/V flip flags'}
    (ROOT/'build/graphics-validation-v2.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
