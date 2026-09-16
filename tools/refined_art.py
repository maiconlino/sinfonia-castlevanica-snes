"""Revision 2: reproducible 32x48 poses and single-piece architectural portals.
The two compressed indexed drawings are source artwork, not external dependencies.
"""
import base64, zlib
from PIL import Image, ImageDraw
HERO_PALETTE=[(10, 12, 25), (16, 17, 34), (37, 38, 62), (53, 21, 46), (69, 66, 94), (124, 32, 68), (124, 122, 151), (128, 220, 230), (154, 116, 72), (180, 134, 130), (186, 190, 213), (203, 65, 106), (230, 199, 143), (242, 214, 189), (244, 241, 237), (0, 0, 0)]
HERO_PIXELS='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'
CASTLE_PIXELS='eNrtnemS4yoMRjFQ7ipXuef93/YmXkEbknAvdwb9mOnE8RcdCwmMsRPCsGHDhg0bNmzYsGHDhg0bNmzYsGHDhg0bNuxvs+UftzTsn7b1H7cR/1xajLF6PYHX7e213mreX96+rr3+Ab2c4fbyA3ECr9vbsaBtf7QdCfb5B/UOW4DAsr+awOv29lovm/dH22u93Osf0IvTlNLZWKZCYP/4BF4rtr8Ej9dpmhz7o+3TdL5OSM+jX+ntVfDIrVd2FQLx2j/W8uL2Wm8174+213prr39Aj8j/Y4dY7B9reWk7LajfH20nBf3+Mfl/pcBh91/l63y9T2+frrYFBZnP5/sPRo8R5D6fL091enGqeospSrZntWSv/WtBYBMhKGzf35MEY0MQar19LPUS5BfgctNe/EC+NqB/7sVtP45p5aF4+JEg+v7XRwDxVDQtOf4t9SP+laAYf1i3mfhLgrEhSMW/Jlbzbx9pHAAT/yX4FD8hqOAvumuJP1/qucFfCgr8hWCDXxCMDUGSvyJ+vbWmF1KU+c/iKx+Anb8Q5PkrwQY/LxgbgjR/SWzgv/qPp/gvwaf4keBT/If42jgAen4g2M9PCz7Ef7St9S0vZYCaHwn28jOCz/Dn6+CucgnQ8hOCffyc4HP8R9uSM8DCDwT7+SnBFv8EX1FWiN/y7Kd/vyAffzJeV2pNp/x9fkk0gcpdfphKCxLfL3k4geSHgtT3C/yJGq/n6uBOZQmIUyJOISt+4UyTEKS+X/DwOF9gBSn/sjX+QLxKMFf8JUFX/HlBY/yp70fipb8eflHQwy8I9vOD1AIJ5uCXBR38omAvP0itCBLMzt8QtPM3BB/gL8RjbLYvBb8g6OMXBPv4QWpt1ZiSn25Ukv/a3hS08us8LPyz8EPx+O5yGsdXjL9C0MaP8Zse6vkzaltpja0Ek/hVghZ+j4dqfiD+eahb5KcGPimo51cKSg4Ko2vUWCt1fpj96wV153/nntfBTYe6ULImabgKBdPhbiNj+fgDwXTwp8jWFNSeYDZEqbEe/Hz7eo+3K0Fh2C8JCuN1OZ0aHuLzCTb+pPipzmasEH+ToCb+Hg9xPZH4QWohdaJ9yfxqQS2/1UM1P5WrhXpxeOv5W5afytVCMAHBNj8qT7vOIZhoD7X8dNsq+Ln2xfGbBVv8Pg+V/JluW1gdHgCO3yEo8zs9NPBT4oU6nWASv1Gwze/wUMfP5erZ//MlgOFncvXq/0lBiZ8ULPp/sqZo+bnUem9aq4lp3L5Ifqcgz+/2UMPPptZrU8pIvToAJL9bkOP3e4j4idG1IP5qXYI8N1z/dYLi+R+fq5t6zPdrugRU7oq5WggyNYU8/6ME0xn+QzDx4xR5/l9qW3FZlthqsIC/T5Ca/+/1UI6/KP4KlyhPxb9LkIp/r4dNfl783Vzf8h+MPMPfFuT8Zfj9gjb+KveXo/9fzhKbUBfT5K9yfzn6/4WpKRr+KvcPwbQwNUXNjw9ujoW75fGtrjew/F5Blr/DQz0/bFvH+I+S1/GbBVv8Hg/V/BEdXEo96vkZwU9esMHv8lDLvw2+5n0E9/p/v1XufcPQsr2Tru1a/lsv5TnVgnO+9ZKW/9bb/Fm217vgfHg4pwQ9NPFf4oA/VSfoen6jYJPf4aGSH4hDdSCv4PcIivxOD+XxP1Y/ZE71j+OvlAl3PYLp42nBlofS+V+hXuTqJj/v6stcf22aL3Vq/dctCPdbDnfPm3DvGsA3qFJwhvsdgvNy6lw1gI1/EvjBQYTupoyO7rb+Hw/XOwTReL1TsDn/D9WLJFo29QWmXc3fTFeTYIx+wY/0+Se38r/FX83Ev4TX6o7xbOe3CSr4JcFPStDCn+ein3/JXzfMV7XBwJ/r/S/Bujbo+atxQyEIaoOTH69ugDdMZxs/K7jSgk1+q4dP86f8DD8j+AA/EtTzE4uH+vjNgi1+j6CaH+RqOvr/VNeErO//M9Z7C86opmj7/4z13v1/QjXFw08ucScemJC18XcIyvH3Cdr6/7a6sf83Ccb4vKB1/G9Qn/4fgobzv/kQnIF6lWP8cBWd/8HcPAXr9293U5IH1DPyZ6W+R9n+qeF6KodTjaOL1//H1BeulKkFRVrBT+qEwnz+b8j/ZvzN/ClZImTO/8HP88+q/r86/xf5KT2i/y/P/0V+Uo/o/+cR/8Gv518f5l8f5l+f4V8Z/nVd6/7/+P/D2f+/9Z7s/98PrXmg/38/SkfB3x//mr8//jW/O/4c//6Uoef4d7nn+A/3evn3h98Ro+vtqZBq9dgcrm96D47/d73u8f/+8Evi/K/gb/f/24Lbov+P+Pyv4Hf0/+j8LxX8Pf3/yY/m/5c/f/4I8U9y68Lz/5ve5BVECXXouQXP+f9Nhox/Jz+Kfxc/Ef9O/jP+TX6bKfhdghK/U9AUf5hLRf9/Lzk2xP/Q+VT2/834E/3/eSOA2P972/9dXev1Fe72vz7b/u/1373tv+FufJB/fYq/Wv9ezoAY+HX9f1Tzd/X/Yv9H4Zfr/8X49/X/0cP/xf0/uv/hPAKzhT/n5ujqM0U9f8zLk/Pf70uc5Pkfcf9H0QSI87+Fm/+v+UPt5Ypb/6/gjzR/bPETs+sVfwgBuxs5fnK6nuKPHfP/BH+MHH9k5/8Xbv6D5C/7/8jyk+u/Fjz/X7RM+/z/Auf/a94Vemdo/9vsUsm//UYCiH/k+cn1/0T8i5Zpn/+H8Y8N/kjP/7fiHy/+UPHH2BP/0mPn/FfNj2Axf9TXv5I/nvgVf+znr1pmHz/B2vRQzR9P/lD0/x38M2qwrvn/5Z7/j1/LHwJqAA/Ev26ZHfEnH4TXwX/+JsqpXvxMjIv/1Cv4P3G50vNfen3810+/oPjn8upqxR/g2ZUq/jnjy7XRzx9zBh764n8+/Va+/lPhh3n33dP+6+v/2F339f++9p9M/AGeXTr5KXe9179Y/vAEP/ylqDl28s8vo8M1Q+vjfzmr5udX10B+TesSl+vw/JHnlwQ9/FAP/BzQxMc/aOI/JfT7QiU/n64M/3VBihJk+O9oVTcVnoK1HHzWDpv/uupCP+/z5JfKFc2fkiAo8Yd7hFV7KP+KweP8VfzFcs3FnxdU8J99biEIf/+CW//o5BeWqzS6K4Y/Wuvf7XDxXCr7+s/H+Zvd9dP8mvUffP1z8pvL1fVniA/Uv3DxB2ZC7Xvrn55/+47u/C/4A83/Y/VPwx87+YOVX87/j49w/vvV+X8e5L78r/iDff3XD/OfB8DLH2r+8D386QH+Isu+lV8YXWv5tcv1Nfz713jH/wHyh+b6fyFcyvqnvv9b4gdfo7v/25P/6HySXV2v5G+tf1O1f/g9Bb8toZr88AYF6+pa43Kd9vpfWVB5/79pQdXgV/E/slwJPv/GKth8/o1V0BB/NP9XzH/X5xfa+HPTdQF+la/+bdfruuqfgj9d/I72/6X86Xv43xTC6FLOf2a6Dh4AD386+e8xSzf/B9JaE3FZWMsfmMu16Ejb+c/VKt/CH3z82y5fw59+gj94+NNX8Cc3v3B3LcvfGF2LFxSs/Krxf6r4xfpneP4PV//wm7rzv0AdgO36F88fFfEvxznm8//UxR8wP3+7bnkdsb7+y/OLz/8h1vm2+fXP/2H4g8zfin+Ay9VE/nb8U+qKfyd/cPGnev0LrjR6/vTd/HiwZuS/GkBVUH386Dzn/8C/H4CU+vnTL+APLv56Qa2TP/0Ef3f+4wWl3vrH8IvjHxs/Nf55gD8M/n+bP/wafvv4X+KfdAuK9Plvff5P7/g/dtY/6fzPxf+99V8z/yPxi/P/Pn7b8y/M81+u+MO0+Gvi/3P8zPhn8A/+38fvq/9Uvzz4n69/PeO/2Dn+G/yD/6f7/zH+/9L5f3H8Kz3/1cOP578frv/8/D9pKcmrC6Tn/3sEqd//7RJszf+vfYbj3ymI498p2Jj/SH2G+VO3PSs4+Ae/7vffyZXOZn6wv0NfFLT79wj/xCy/+y7+iVlPqvBvxF+8/6dXH3U3vfyyoJ2/cf9Prz4Q7OeXBe388v0/3fbrBcX7f8z5St0MA37/17g/2i552Ix3s56QP9d+3zcpd7fUdjj/b90fbRc8ZO43vm8Wo7ZL9a8//qZypdEXBR3xF+tfP7+pXGn0RUEHv8m/YcP+alv/cQvDhg0bNmzYsGHDhg0bNmzYsGHDhg0bNmzYsL/O/gNR0yGT'

def indexed(payload,size):
    return Image.frombytes('P',size,zlib.decompress(base64.b64decode(payload)))

def shared_tiles(original):
    tiles=list(original)
    # Twenty distinct tiles compose each 32x40 doorway. No repeated miniature doors.
    for kind in range(3):
        im=Image.new('P',(32,40),0);d=ImageDraw.Draw(im)
        if kind==2:
            d.rectangle((0,0,31,39),fill=2)
            for y in range(0,40,8):
                d.line((0,y,31,y),fill=1)
                for x in range(-8 if y%16 else 0,32,16):
                    d.line((x,y+1,x,y+7),fill=3)
            d.line((18,4,14,12,19,19,14,28,16,36),fill=1)
            d.point((19,19),fill=5)
        else:
            outer=[(1,39),(1,15),(5,8),(10,3),(15,0),(20,3),(26,8),(30,15),(30,39)]
            d.polygon(outer,fill=4)
            d.line(outer+[outer[0]],fill=1,width=1)
            d.line((3,38,3,15,7,9,11,5,15,3,19,5,24,10,28,16,28,38),fill=5)
            d.polygon([(7,38),(7,16),(10,11),(15,7),(20,11),(24,16),(24,38)],fill=1)
            d.polygon([(9,38),(9,17),(12,13),(15,10),(18,13),(22,17),(22,38)],fill=6)
            for x in (11,15,19): d.line((x,18,x,36),fill=2)
            d.line((9,25,22,25),fill=9)
            d.line((9,26,22,26),fill=10)
            d.line((15,14,15,37),fill=10)
            d.point((18,28),fill=14 if kind==0 else 12)
            for y in (18,26,34):
                d.line((1,y,6,y),fill=1);d.line((25,y,30,y),fill=1)
                d.line((2,y+1,5,y+1),fill=5)
            d.rectangle((0,37,31,39),fill=3)
            d.line((0,37,31,37),fill=10)
            if kind==1:
                d.line((8,18,23,31),fill=4,width=2)
                d.line((23,18,8,31),fill=4,width=2)
                d.rectangle((13,22,18,28),fill=9,outline=10)
        for y in range(0,40,8):
            for x in range(0,32,8): tiles.append(im.crop((x,y,x+8,y+8)))
    # A 24x24 recovery altar, one coherent object instead of repeated diamonds.
    im=Image.new('P',(24,24),0);d=ImageDraw.Draw(im)
    d.polygon([(12,0),(17,7),(12,13),(7,7)],fill=7,outline=14)
    d.line((12,1,12,11),fill=15)
    d.rectangle((5,14,18,16),fill=5);d.line((5,14,18,14),fill=10)
    d.rectangle((7,17,16,21),fill=3);d.line((8,17,8,21),fill=5)
    d.rectangle((3,22,20,23),fill=4);d.line((3,22,20,22),fill=10)
    for y in range(0,24,8):
        for x in range(0,24,8): tiles.append(im.crop((x,y,x+8,y+8)))
    while len(tiles)<224: tiles.append(Image.new('P',(8,8),0))
    assert len(tiles)==224
    return tiles

def write_hero(out,planar,cgram):
    hero=indexed(HERO_PIXELS,(256,96));frames=[]
    for i in range(16):
        x=(i%8)*32;y=(i//8)*48
        frames.append(planar(hero.crop((x,y,x+32,y+48))))
    assert all(len(f)==768 for f in frames)
    (out/'hero-frames.chr').write_bytes(b''.join(frames))
    palette=(out/'sprite_palettes.pal').read_bytes()
    (out/'sprite_palettes.pal').write_bytes(palette[:224]+cgram(HERO_PALETTE))
    (out/'source').mkdir(exist_ok=True)
    hero.putpalette(sum((list(c) for c in HERO_PALETTE),[])+[0]*720)
    hero.save(out/'source/hero-poses.png')
    hero.convert('RGB').resize((1024,384),Image.Resampling.NEAREST).save(out/'hero-poses-preview.png')
