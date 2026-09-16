#!/usr/bin/env python3
"""Validate the actual 4bpp tile layouts of revision 2, not the old atlas."""
from pathlib import Path
import struct, sys
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import generate_graphics as old
import remaster_graphics as new

def decode(data):
    assert len(data)==32
    im=Image.new('P',(8,8))
    for y in range(8):
        for x in range(8):
            value=sum(((data[(p//2)*16+y*2+p%2]>>(7-x))&1)<<p for p in range(4))
            im.putpixel((x,y),value)
    return im

def main():
    frames=(ROOT/'assets/hero-frames.chr').read_bytes()
    assert len(frames)==16*768
    for f in range(16):
        im=Image.new('P',(32,48))
        for y in range(6):
            for x in range(4):
                off=f*768+(y*4+x)*32
                im.paste(decode(frames[off:off+32]),(x*8,y*8))
        assert im.tobytes()==new.hero(f).tobytes(),f'hero frame {f}'
    for r in range(8):
        data=(ROOT/f'assets/bg_region{r}.chr').read_bytes()
        entries=struct.unpack('<1024H',(ROOT/f'assets/bg_region{r}.map').read_bytes())
        pal=(ROOT/f'assets/bg_region{r}.pal').read_bytes()
        assert len(data)==32768 and len(pal)==256
        assert all(v<32768 for v in struct.unpack('<128H',pal))
        assert all((t&1023)<1024 and ((t>>10)&7)<8 for t in entries)
        assert not any(t&0xC000 for t in entries), 'Unexpected unhandled tile flips'
        door=Image.new('P',(32,48))
        for y in range(6):
            for x in range(4):
                off=(128+y*4+x)*32
                door.paste(decode(data[off:off+32]),(x*8,y*8))
        assert door.tobytes()==new.door().tobytes(),f'door in region {r}'
        assert len(set(data[t*32:t*32+32] for t in range(128,152)))>8
    assert len((ROOT/'assets/sprites.chr').read_bytes())==16384
    print('PASS: 16 hero frames roundtrip, 8 native tilemaps/palettes, whole 32x48 tiled doorway in every region.')
if __name__=='__main__': main()
