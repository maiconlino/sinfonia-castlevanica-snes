#!/usr/bin/env python3
"""Roundtrip the produced SNES 4bpp data and maps into their source pixels."""
from pathlib import Path
import struct
from PIL import Image
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from generate_graphics import OUT, background, hero, wolf, bat, mist, enemy, boss, common_tiles, planar

def decode_tile(data):
 assert len(data)==32
 out=Image.new('P',(8,8))
 for y in range(8):
  for x in range(8):
   val=0
   for p in range(4):
    b=data[(p//2)*16+y*2+(p%2)]
    val|=((b>>(7-x))&1)<<p
   out.putpixel((x,y),val)
 return out

def main():
 for r in range(8):
  data=(OUT/f'bg_region{r}.chr').read_bytes();assert len(data)==32768
  tilemap=struct.unpack('<1024H',(OUT/f'bg_region{r}.map').read_bytes())
  reconstructed=Image.new('P',(256,224))
  for y in range(28):
   for x in range(32):
    tile=tilemap[y*32+x];assert tile<1024
    reconstructed.paste(decode_tile(data[tile*32:tile*32+32]),(x*8,y*8))
  assert reconstructed.tobytes()==background(r).tobytes(),f'region{r} mismatch'
  assert all(v<32768 for v in struct.unpack('<16H',(OUT/f'bg_region{r}.pal').read_bytes()))
 for i,tile in enumerate(common_tiles()):assert decode_tile(planar(tile)).tobytes()==tile.tobytes(),f'common{i}'
 data=(OUT/'sprites.chr').read_bytes();assert len(data)==16384
 assert len((OUT/'sprite_palettes.pal').read_bytes())==256
 assert all(v<32768 for v in struct.unpack('<128H',(OUT/'sprite_palettes.pal').read_bytes()))
 # Reassemble sprites directly from raw ROM-format tile bytes.
 def crop(x,y,w,h):
  im=Image.new('P',(w,h))
  for yy in range(h//8):
   for xx in range(w//8):
    t=(y//8+yy)*16+x//8+xx;im.paste(decode_tile(data[t*32:t*32+32]),(xx*8,yy*8))
  return im
 for i in range(8):assert crop(i*16,0,16,32).tobytes()==hero(i).tobytes()
 for i in range(10):assert crop((i%4)*32,128+i//4*32,32,32).tobytes()==boss(i).tobytes()
 print('PASS: 8 background maps, 128 common tiles,8 hero frames,10bosses,16-bit CGRAM palettes round-trip exactly.')
if __name__=='__main__':main()
