#!/usr/bin/env python3
"""Validate the actual native 4bpp layout used by revision 1.1."""
from pathlib import Path
import struct,sys
from PIL import Image
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import refined_art as art
import generate_graphics as old

def decode_tile(raw):
    assert len(raw)==32
    out=Image.new('P',(8,8))
    for y in range(8):
        for x in range(8):
            value=sum(((raw[(p//2)*16+y*2+p%2]>>(7-x))&1)<<p for p in range(4))
            out.putpixel((x,y),value)
    return out

def crop_sheet(raw,x,y,w,h):
    out=Image.new('P',(w,h))
    for yy in range(h//8):
        for xx in range(w//8):
            ti=(y//8+yy)*16+x//8+xx
            out.paste(decode_tile(raw[ti*32:ti*32+32]),(xx*8,yy*8))
    return out

def main():
    for r in range(8):
        expected=art.tiled_scene(r)
        for ext,reference in zip(('chr','map','pal'),expected[:3]):
            actual=(ROOT/f'assets/bg_region{r}.{ext}').read_bytes()
            assert actual==reference,(r,ext)
        tiles=struct.unpack('<1024H',expected[1])
        assert all((v&1023)<1024 and ((v>>10)&7)<8 for v in tiles)
        assert len(expected[2])==256 and all(v<32768 for v in struct.unpack('<128H',expected[2]))
    shared=(ROOT/'assets/bg_common.chr').read_bytes()
    assert len(shared)==8192
    for variant in range(3):
        door=Image.new('P',(32,48))
        for y in range(6):
            for x in range(4):
                t=128+variant*24+y*4+x
                door.paste(decode_tile(shared[t*32:t*32+32]),(x*8,y*8))
        assert door.tobytes()==art.doorway(variant).tobytes(),('door',variant)
    raw=(ROOT/'assets/hero_frames.chr').read_bytes();frames=art.hero_bank()[2]
    assert len(raw)==len(frames)*1024
    for i,reference in enumerate(frames):
        frame=raw[i*1024:(i+1)*1024];out=Image.new('P',(32,48))
        for y in range(3):
            for x in range(2):out.paste(crop_sheet(frame,(y*2+x)*16,0,16,16),(x*16,y*16))
        assert out.tobytes()==reference.tobytes(),('hero',i)
    raw=(ROOT/'assets/boss_frames0.chr').read_bytes()+(ROOT/'assets/boss_frames1.chr').read_bytes()
    assert len(raw)==40960
    for i in range(20):
        frame=raw[i*2048:(i+1)*2048];out=Image.new('P',(64,64))
        for y in range(2):
            for x in range(2):out.paste(crop_sheet(frame,(y*2+x)*32,0,32,32),(x*32,y*32))
        assert out.tobytes()==art.boss_frame(i//2,i%2).tobytes(),('boss',i)
    print('PASS: 8 native region maps and 8x128 colours; coherent 24-tile doorways; 16 six-OBJ hero poses; 20 four-OBJ boss poses.')
if __name__=='__main__':main()
