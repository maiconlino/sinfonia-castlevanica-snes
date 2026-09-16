#!/usr/bin/env python3
"""Verify v1.1 tile topology, palette limits, composited portals and metasprites."""
import sys,struct,json
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import generate_graphics as g
import refine_graphics as h
from validate_graphics import decode_tile

def main():
    for region in range(8):
        data=(g.OUT/f'bg_region{region}.chr').read_bytes()
        words=struct.unpack('<1024H',(g.OUT/f'bg_region{region}.map').read_bytes())
        assert len(data)==32768
        back=Image.new('P',(256,224))
        for yy in range(28):
            for xx in range(32):
                word=words[yy*32+xx];tile=word&1023
                assert ((word>>10)&7)<8
                back.paste(decode_tile(data[tile*32:tile*32+32]),(xx*8,yy*8))
        assert back.tobytes()==h.enhanced_background(region).tobytes()
        palette=(g.OUT/f'bg_region{region}.pal').read_bytes();assert len(palette)==256
        assert all(x<32768 for x in struct.unpack('<128H',palette))
        for secret,base in ((False,128),(True,148)):
            door=Image.new('P',(32,40))
            for k in range(20):
                t=base+k;door.paste(decode_tile(data[t*32:t*32+32]),((k%4)*8,(k//4)*8))
            assert door.tobytes()==h.doorway(secret).tobytes()
    frames=(g.OUT/'hero-frames.chr').read_bytes();assert len(frames)==32768
    for f in range(16):
        data=frames[f*2048:(f+1)*2048];hero=Image.new('P',(32,48))
        for y in range(6):
            for x in range(4):
                tile=y*16+x if y<4 else (y-4)*16+x+4
                hero.paste(decode_tile(data[tile*32:tile*32+32]),(x*8,y*8))
        assert hero.tobytes()==h.protagonist(f).tobytes()
    assert len({h.protagonist(f).tobytes() for f in range(2,10)})==8
    print('PASS: 8 region tilemaps, 128-colour BG banks, coherent 20-tile portals, 16 streamed hero frames, all pixel roundtrips.')
if __name__=='__main__':main()
