#!/usr/bin/env python3
"""Minimal libretro SNES test frontend. No firmware or commercial ROM required."""
import argparse, ctypes as C, hashlib, json, struct, wave, os
from pathlib import Path

BUTTONS = dict(B=0,Y=1,SELECT=2,START=3,UP=4,DOWN=5,LEFT=6,RIGHT=7,A=8,X=9,L=10,R=11)
ROOT = Path(__file__).resolve().parent
class GameInfo(C.Structure):
    _fields_=[('path',C.c_char_p),('data',C.c_void_p),('size',C.c_size_t),('meta',C.c_char_p)]
class SystemInfo(C.Structure):
    _fields_=[('library_name',C.c_char_p),('library_version',C.c_char_p),('valid_extensions',C.c_char_p),('need_fullpath',C.c_bool),('block_extract',C.c_bool)]
class Geometry(C.Structure):
    _fields_=[('base_width',C.c_uint),('base_height',C.c_uint),('max_width',C.c_uint),('max_height',C.c_uint),('aspect_ratio',C.c_float)]
class Timing(C.Structure):
    _fields_=[('fps',C.c_double),('sample_rate',C.c_double)]
class AVInfo(C.Structure):
    _fields_=[('geometry',Geometry),('timing',Timing)]
class Variable(C.Structure):
    _fields_=[('key',C.c_char_p),('value',C.c_char_p)]

class SNES:
    def __init__(self,rom,core=None):
        self.core=C.CDLL(str(core or os.environ.get('SNES_CORE') or ROOT/'snes9x/libretro/snes9x_libretro.so'))
        self.frame=0; self.mask=0; self.pixel_format=0; self.image=None; self.audio=bytearray(); self.variables={}; self.env_calls={}
        self.directory=str(Path(rom).resolve().parent).encode()
        self.rom_path=str(Path(rom).resolve()).encode(); self.rom_bytes=Path(rom).read_bytes(); self.rom_buffer=C.create_string_buffer(self.rom_bytes)
        env_type=C.CFUNCTYPE(C.c_bool,C.c_uint,C.c_void_p)
        vid_type=C.CFUNCTYPE(None,C.c_void_p,C.c_uint,C.c_uint,C.c_size_t)
        sample_type=C.CFUNCTYPE(None,C.c_int16,C.c_int16)
        audio_type=C.CFUNCTYPE(C.c_size_t,C.POINTER(C.c_int16),C.c_size_t)
        poll_type=C.CFUNCTYPE(None)
        input_type=C.CFUNCTYPE(C.c_int16,C.c_uint,C.c_uint,C.c_uint,C.c_uint)
        self.callbacks=[env_type(self.environment),vid_type(self.video),sample_type(self.sample),audio_type(self.audio_batch),poll_type(lambda:None),input_type(self.input)]
        for name,cb in zip(['environment','video_refresh','audio_sample','audio_sample_batch','input_poll','input_state'],self.callbacks):
            f=getattr(self.core,'retro_set_'+name); f.argtypes=[type(cb)]; f(cb)
        self.core.retro_init()
        self.core.retro_get_memory_data.argtypes=[C.c_uint]; self.core.retro_get_memory_data.restype=C.c_void_p
        self.core.retro_get_memory_size.argtypes=[C.c_uint]; self.core.retro_get_memory_size.restype=C.c_size_t
        self.core.retro_load_game.argtypes=[C.POINTER(GameInfo)]; self.core.retro_load_game.restype=C.c_bool
        info=GameInfo(self.rom_path,C.cast(self.rom_buffer,C.c_void_p),len(self.rom_bytes),None)
        if not self.core.retro_load_game(C.byref(info)): raise RuntimeError('Snes9x rejected ROM')
        self.core.retro_set_controller_port_device(0,1)
        self.av=AVInfo(); self.core.retro_get_system_av_info(C.byref(self.av))
        self.info=SystemInfo(); self.core.retro_get_system_info(C.byref(self.info))
    def environment(self,cmd,data):
        self.env_calls[cmd]=self.env_calls.get(cmd,0)+1
        if cmd==10:
            self.pixel_format=C.cast(data,C.POINTER(C.c_int))[0]; return self.pixel_format in (0,1,2)
        if cmd in (9,30,31): C.cast(data,C.POINTER(C.c_char_p))[0]=self.directory; return True
        if cmd in (3,): C.cast(data,C.POINTER(C.c_bool))[0]=True; return True
        if cmd in (17,65585): C.cast(data,C.POINTER(C.c_bool))[0]=False; return True
        if cmd in (39,52,57,59): C.cast(data,C.POINTER(C.c_uint))[0]=0; return True
        if cmd==61: C.cast(data,C.POINTER(C.c_uint))[0]=1; return True
        if cmd==65583: C.cast(data,C.POINTER(C.c_uint))[0]=3; return True
        if cmd==16:
            arr=C.cast(data,C.POINTER(Variable)); i=0
            while arr[i].key:
                vals=arr[i].value.split(b'; ',1)
                self.variables[arr[i].key]=vals[-1].split(b'|')[0]; i+=1
            return True
        if cmd==15:
            var=C.cast(data,C.POINTER(Variable))[0]
            if var.key in self.variables: var.value=self.variables[var.key]; return True
            return False
        if cmd in (6,8,11,18,34,35,37,65572,65578,63): return True
        return False
    def video(self,data,w,h,pitch):
        if not data: return
        bpp=4 if self.pixel_format==1 else 2
        self.image=(w,h,b''.join(C.string_at(data+y*pitch,w*bpp) for y in range(h)))
    def sample(self,l,r): self.audio.extend(struct.pack('<hh',l,r))
    def audio_batch(self,data,frames): self.audio.extend(C.string_at(data,frames*4)); return frames
    def input(self,port,device,index,button):
        if port or device!=1: return 0
        if button==256: return self.mask
        return 1 if self.mask&(1<<button) else 0
    def run(self,frames=1,buttons=()):
        self.mask=buttons if isinstance(buttons,int) else sum(1<<BUTTONS[b.upper()] for b in buttons)
        for _ in range(frames): self.core.retro_run(); self.frame+=1
    def memory(self,kind=2):
        ptr=self.core.retro_get_memory_data(kind); n=self.core.retro_get_memory_size(kind)
        return C.string_at(ptr,n) if ptr and n else b''
    def set_memory(self,addr,content,kind=2):
        ptr=self.core.retro_get_memory_data(kind); n=self.core.retro_get_memory_size(kind)
        if addr<0 or addr+len(content)>n: raise ValueError('Memory bounds')
        C.memmove(ptr+addr,content,len(content))
    def save_image(self,path,scale=1):
        from PIL import Image
        import numpy as np
        if not self.image: raise RuntimeError('No rendered frame')
        w,h,raw=self.image
        if self.pixel_format==1:
            a=np.frombuffer(raw,dtype='<u4').reshape(h,w); r=(a>>16)&255; g=(a>>8)&255; b=a&255
        else:
            a=np.frombuffer(raw,dtype='<u2').reshape(h,w)
            if self.pixel_format==2: r=((a>>11)&31)*255//31; g=((a>>5)&63)*255//63; b=(a&31)*255//31
            else: r=((a>>10)&31)*255//31; g=((a>>5)&31)*255//31; b=(a&31)*255//31
        im=Image.fromarray(np.stack([r,g,b],axis=2).astype('uint8'))
        if scale!=1: im=im.resize((w*scale,h*scale),Image.Resampling.NEAREST)
        im.save(path)
    def save_audio(self,path):
        with wave.open(str(path),'wb') as out:
            out.setnchannels(2); out.setsampwidth(2); out.setframerate(round(self.av.timing.sample_rate)); out.writeframes(self.audio)
    def summary(self):
        return dict(core=self.info.library_name.decode(),version=self.info.library_version.decode(),frames=self.frame,fps=self.av.timing.fps,sample_rate=self.av.timing.sample_rate,pixel_format=self.pixel_format,video=[self.image[0],self.image[1]] if self.image else None,video_sha256=hashlib.sha256(self.image[2]).hexdigest() if self.image else None,audio_frames=len(self.audio)//4,audio_nonzero=any(self.audio),ram_bytes=len(self.memory()),sram_bytes=len(self.memory(0)))
    def close(self): self.core.retro_unload_game(); self.core.retro_deinit()

def main():
    p=argparse.ArgumentParser(); p.add_argument('rom'); p.add_argument('--frames',type=int,default=180); p.add_argument('--buttons',default=''); p.add_argument('--out',default='capture'); p.add_argument('--script'); p.add_argument('--core')
    args=p.parse_args(); em=SNES(args.rom,args.core)
    if args.script:
        for entry in json.loads(Path(args.script).read_text()):
            em.run(entry.get('frames',1),entry.get('buttons',[]))
            if entry.get('screenshot'): em.save_image(entry['screenshot'])
    else: em.run(args.frames,args.buttons.split(',') if args.buttons else [])
    out=Path(args.out); out.parent.mkdir(parents=True,exist_ok=True)
    em.save_image(str(out)+'.png'); em.save_audio(str(out)+'.wav'); Path(str(out)+'.wram').write_bytes(em.memory()); Path(str(out)+'.srm').write_bytes(em.memory(0)); Path(str(out)+'.json').write_text(json.dumps(em.summary(),indent=2)+'\n'); print(json.dumps(em.summary(),indent=2)); em.close()
if __name__=='__main__': main()
