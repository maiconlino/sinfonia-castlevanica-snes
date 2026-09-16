#!/usr/bin/env python3
"""Build original SinfonIA music for real SNES SPC700/S-DSP. Python stdlib only.
The tiny assembler is an explicit opcode emitter; labels and branch ranges are
resolved and checked. All notes are arrangements of this project's MIDI suite.
No Nintendo or third-party samples or drivers are included.
"""
from pathlib import Path
import argparse, json, math, struct, hashlib
ROOT=Path(__file__).resolve().parent
ORIGIN=0x0200
DIR=0x0800
SAMPLES=0x0900
TABLES=0x0A00
MUSIC=0x0D00
THEMES=['castle','hauntedlibrary','mythicgarden','crypt','reservoir','giantclocktower','observatory','agicore','boss','finalboss','victory']
ROLES=[('organ','harpsi','bass','strings'),('harpsi','pluck','bass','choir'),('flute','pluck','bass','strings'),('organ','bell','bass','choir'),('bell','pluck','bass','strings'),('harpsi','square','bass','organ'),('flute','bell','bass','choir'),('square','harpsi','bass','organ'),('strings','harpsi','bass','organ'),('organ','square','bass','choir'),('organ','harpsi','bass','strings')]
# Direct-page work bytes. These never overlap hardware ports or the stack.
SEQ=0x10; PTR=0x12; START=0x14; TEMPO=0x16; COUNT=0x17; KON=0x18; KOFF=0x19; SFXTIME=0x1A; THEME=0x1B; ELAPSED=0x1C; FX=0x1D

class Asm:
    def __init__(self): self.code=bytearray();self.labels={};self.fixups=[];self.listing=[]
    @property
    def pc(self):return ORIGIN+len(self.code)
    def label(self,s):assert s not in self.labels;s0=self.pc;self.labels[s]=s0;self.listing.append(f'{s}:')
    def emit(self,*b,comment=''):
        at=self.pc;self.code.extend(b);self.listing.append(f'{at:04X}  '+ ' '.join(f'{v:02X}' for v in b).ljust(12)+' '+comment)
    def im(self,d,v):self.emit(0x8F,v&255,d,comment=f'mov ${d:02x}, #${v&255:02x}')
    def a(self,v):self.emit(0xE8,v&255,comment=f'mov a, #${v&255:02x}')
    def x(self,v):self.emit(0xCD,v&255,comment=f'mov x, #${v&255:02x}')
    def y(self,v):self.emit(0x8D,v&255,comment=f'mov y, #${v&255:02x}')
    def load(self,d):self.emit(0xE4,d,comment=f'mov a, ${d:02x}')
    def store(self,d):self.emit(0xC4,d,comment=f'mov ${d:02x}, a')
    def absx(self,addr):self.emit(0xF5,addr&255,addr>>8,comment=f'mov a, !${addr:04x}+x')
    def indy(self,dp):self.emit(0xF7,dp,comment=f'mov a, [${dp:02x}]+y')
    def branch(self,op,label):self.emit(op,0,comment=f'branch ${op:02x} {label}');self.fixups.append(('rel',len(self.code)-1,label))
    def jump(self,label):self.emit(0x5F,0,0,comment=f'jmp {label}');self.fixups.append(('abs',len(self.code)-2,label))
    def call(self,label):self.emit(0x3F,0,0,comment=f'call {label}');self.fixups.append(('abs',len(self.code)-2,label))
    def dsp(self,r,v):self.im(0xF2,r);self.im(0xF3,v)
    def dsp_a(self,r):self.im(0xF2,r);self.store(0xF3)
    def ref16(self,dp,label):
        self.im(dp,0);self.fixups.append(('lo',len(self.code)-2,label));self.im(dp+1,0);self.fixups.append(('hi',len(self.code)-2,label))
    def finish(self):
        for kind,off,label in self.fixups:
            addr=self.labels[label]
            if kind=='rel':
                v=addr-(ORIGIN+off+1)
                assert -128<=v<=127,(label,v)
                self.code[off]=v&255
            elif kind=='abs': self.code[off:off+2]=struct.pack('<H',addr)
            else:self.code[off]=(addr>>(8 if kind=='hi' else 0))&255
        return bytes(self.code)

def driver():
    a=Asm();a.label('start');a.emit(0x20,comment='clrp');a.x(0xEF);a.emit(0xBD,comment='mov sp,x')
    a.im(0xF1,0x30) # Disable IPL/timers, clear all CPU input latches once.
    a.dsp(0x6C,0xE0);a.dsp(0x5C,0xFF);a.dsp(0x4C,0)
    a.dsp(0x2D,0);a.dsp(0x3D,0);a.dsp(0x4D,0);a.dsp(0x5D,DIR>>8)
    a.dsp(0x0C,90);a.dsp(0x1C,90);a.dsp(0x2C,0);a.dsp(0x3C,0)
    a.dsp(0x6D,0xF0);a.dsp(0x7D,0);a.dsp(0x0D,0)
    # 4 music voices, one independently triggered FX voice. Gentle stereo spread.
    for v,(l,r,src,adsr1,adsr2) in enumerate([(70,62,0,0x8F,0xC0),(38,50,1,0x8F,0x95),(62,62,2,0x8F,0xD0),(28,35,3,0x89,0xC0),(90,90,4,0x8F,0x91)]):
        base=v*16
        for reg,value in [(0,l),(1,r),(4,src),(5,adsr1),(6,adsr2),(7,0x7F)]:a.dsp(base+reg,value)
    for dp in [SEQ,KON,SFXTIME,THEME,FX]:a.im(dp,0)
    a.im(KOFF,0);a.dsp(0x5C,0);a.dsp(0x6C,0x20) # Echo writes disabled; mute/reset released.
    a.im(0xFA,16);a.im(0xF1,1) # Timer 0: 8000/16 = 500 Hz.
    a.a(0);a.call('set_theme');a.im(0xF6,0);a.im(0xF7,0x53)
    a.label('main')
    a.load(0xF6);a.emit(0x64,SEQ,comment='cmp a, seq');a.branch(0xF0,'timer')
    a.store(ELAPSED);a.load(0xF6);a.emit(0x64,ELAPSED);a.branch(0xD0,'timer') # Stable sequence double read.
    a.store(SEQ);a.load(0xF4);a.emit(0x68,1);a.branch(0xD0,'check_sfx')
    a.load(0xF5);a.emit(0x68,len(THEMES));a.branch(0xB0,'ack');a.call('set_theme');a.jump('ack')
    a.label('check_sfx');a.emit(0x68,2);a.branch(0xD0,'check_mute');a.load(0xF5);a.call('sfx');a.jump('ack')
    a.label('check_mute');a.emit(0x68,3);a.branch(0xD0,'ack');a.load(0xF5);a.branch(0xF0,'unmute');a.dsp(0x6C,0x60);a.jump('ack')
    a.label('unmute');a.dsp(0x6C,0x20)
    a.label('ack');a.load(SEQ);a.store(0xF6)
    a.label('timer');a.load(0xFD);a.branch(0xF0,'flush');a.store(ELAPSED)
    a.load(SFXTIME);a.branch(0xF0,'music_timer');a.emit(0x80,comment='setc');a.emit(0xA4,ELAPSED,comment='sbc a, elapsed');a.branch(0x90,'sfx_stop');a.branch(0xF0,'sfx_stop');a.store(SFXTIME);a.jump('music_timer')
    a.label('sfx_stop');a.im(SFXTIME,0);a.load(KOFF);a.emit(0x08,0x10);a.store(KOFF)
    a.label('music_timer');a.load(COUNT);a.emit(0x80);a.emit(0xA4,ELAPSED);a.branch(0x90,'music_tick');a.branch(0xF0,'music_tick');a.store(COUNT);a.jump('flush')
    a.label('music_tick');a.load(TEMPO);a.store(COUNT);a.call('row')
    a.label('flush');a.load(KOFF);a.dsp_a(0x5C);a.load(KON);a.branch(0xF0,'main_again');a.dsp_a(0x4C);a.im(KON,0)
    a.label('main_again');a.jump('main')
    # A = theme 0..10. Offset into 4-byte metadata: ptr lo,hi,ticks,lead sample.
    a.label('set_theme');a.store(THEME);a.emit(0x1C,0x1C,0x5D,comment='asl a / asl a / mov x,a')
    for addr,dp in [(TABLES+0x200,PTR),(TABLES+0x201,PTR+1),(TABLES+0x202,TEMPO)]:a.absx(addr);a.store(dp)
    a.load(PTR);a.store(START);a.load(PTR+1);a.store(START+1)
    a.absx(TABLES+0x203);a.dsp_a(0x04);a.im(COUNT,1)
    a.load(KOFF);a.emit(0x08,15);a.store(KOFF);a.emit(0x6F,comment='ret')
    # Each row: one command per voice. 0 hold, 1 key-off, 2..127 MIDI key-on.
    a.label('row');a.y(0);a.indy(PTR);a.emit(0x68,0xFF);a.branch(0xD0,'row_start');a.load(START);a.store(PTR);a.load(START+1);a.store(PTR+1)
    a.label('row_start')
    for v in range(4):
        bit=1<<v;base=v*16
        a.y(v);a.indy(PTR);a.branch(0xF0,f'v{v}_done');a.emit(0x68,1);a.branch(0xD0,f'v{v}_on')
        a.load(KOFF);a.emit(0x08,bit);a.store(KOFF);a.jump(f'v{v}_done')
        a.label(f'v{v}_on');a.emit(0x5D,comment='mov x,a');a.absx(TABLES);a.dsp_a(base+2);a.absx(TABLES+0x100);a.dsp_a(base+3)
        a.load(KOFF);a.emit(0x28,255-bit);a.store(KOFF);a.load(KON);a.emit(0x08,bit);a.store(KON)
        a.label(f'v{v}_done')
    a.load(PTR);a.emit(0x60,0x88,4,comment='clrc / adc a,#4');a.store(PTR);a.branch(0x90,'row_done');a.emit(0xAB,PTR+1,comment='inc pointer high')
    a.label('row_done');a.emit(0x6F)
    # Each effect: base note, timbre, lifetime in 2ms ticks; a new effect steals voice 4 only.
    a.label('sfx');a.emit(0x68,7);a.branch(0xB0,'sfx_return');a.store(FX);a.emit(0x1C,0x1C,0x5D)
    a.absx(TABLES+0x240);a.store(SFXTIME);a.absx(TABLES+0x241);a.dsp_a(0x44);a.absx(TABLES+0x242);a.store(ELAPSED)
    a.absx(TABLES+0x243);a.dsp_a(0x46);a.load(ELAPSED);a.emit(0x5D);a.absx(TABLES);a.dsp_a(0x42);a.absx(TABLES+0x100);a.dsp_a(0x43)
    a.load(KOFF);a.emit(0x28,0xEF);a.store(KOFF);a.load(KON);a.emit(0x08,0x10);a.store(KON)
    a.label('sfx_return');a.emit(0x6F)
    return a.finish(),a

def brr_period(kind):
    waves=[]
    for n in range(32):
        x=2*math.pi*n/32
        val={'organ':math.sin(x)+.28*math.sin(3*x),'harpsi':math.sin(x)+.45*math.sin(2*x)+.21*math.sin(5*x),'bass':(2/math.pi)*math.asin(math.sin(x)),'pad':math.sin(x)+.12*math.sin(2*x),'noise':math.sin(x*11)+.6*math.sin(x*7),'flute':math.sin(x)+.08*math.sin(x*3),'bell':math.sin(x)+.5*math.sin(3*x)+.2*math.sin(7*x),'square':1 if n<16 else -1}[kind]
        waves.append(val)
    norm=max(abs(v) for v in waves);nibbles=[max(-8,min(7,round(v/norm*7)))&15 for v in waves]
    out=bytearray()
    for block in range(2):
        out.append(0xB0|(3 if block==1 else 0)) # range 11, filter 0, last block loop+end
        out.extend((nibbles[i]<<4)|nibbles[i+1] for i in range(block*16,block*16+16,2))
    return bytes(out)

def arrange(score,roles):
    count=int(score['beats']*4);out=[[0]*4 for _ in range(count)];details=[]
    for voice,inst in enumerate(roles):
        notes=[n for n in score['notes'] if n['i']==inst]
        # Preserve one line per allocated DSP voice. Pad polyphony becomes chord roots.
        groups={}
        for n in notes:
            st=max(0,min(count-1,round(n['t']*4)));groups.setdefault(st,[]).append(n)
        prev=None;end=0
        for step in range(count):
            candidates=groups.get(step,[])
            if candidates:
                note=(min(candidates,key=lambda n:n['n']) if voice==3 else max(candidates,key=lambda n:(n['v'],n['n'])))
                key=max(2,min(95,note['n']));out[step][voice]=key;prev=key;end=step+max(1,round(note['d']*4))
            elif prev is not None and step>=end:out[step][voice]=1;prev=None
        details.append({'voice':voice,'instrument':inst,'input_notes':len(notes)})
    return bytes(v for row in out for v in row)+b'\xff\x00\x00\x00',details

def make_spc(blob,theme=0):
    out=bytearray(0x10200);sig=b'SNES-SPC700 Sound File Data v0.30';out[:len(sig)]=sig
    out[0x21:0x25]=bytes([0x1A,0x1A,0x1A,30]);struct.pack_into('<H',out,0x25,ORIGIN);out[0x2B]=0xEF
    def field(off,s,size):out[off:off+size]=s.encode('ascii','replace')[:size].ljust(size,b'\0')
    field(0x2E,'SinfonIA - '+THEMES[theme],32);field(0x4E,'SinfonIA Castlevanica Futuristica',32);field(0x6E,'Original engine',16);field(0x7E,'Native SPC700 original music',32);field(0xA9,'180',3);field(0xAC,'05000',5);field(0xB1,'Maicon Lino / OpenAI',32)
    out[0x100+ORIGIN:0x100+ORIGIN+len(blob)]=blob;out[0x100+0xF0]=0x0A
    # The driver's one immediate initial theme number is patched in snapshots only.
    if theme:
        _,asm=driver();needle=bytes([0xE8,0,0x3F,asm.labels['set_theme']&255,asm.labels['set_theme']>>8]);i=out.find(needle,0x100+ORIGIN);assert i>=0;out[i+1]=theme
    return bytes(out)

def build(output):
    scores=json.loads((ROOT/'original_scores.json').read_text());ram=bytearray(65536);code,assembler=driver();assert ORIGIN+len(code)<=DIR,(len(code),hex(ORIGIN+len(code)))
    ram[ORIGIN:ORIGIN+len(code)]=code
    timbres=['organ','harpsi','bass','pad','noise','flute','bell','square']
    for i,kind in enumerate(timbres):
        addr=SAMPLES+i*18;struct.pack_into('<HH',ram,DIR+i*4,addr,addr);ram[addr:addr+18]=brr_period(kind)
    for note in range(128):
        pitch=min(0x3FFF,round(440*2**((note-69)/12)*32/32000*4096));ram[TABLES+note]=pitch&255;ram[TABLES+0x100+note]=pitch>>8
    ptr=MUSIC;metadata=[]
    for idx,key in enumerate(THEMES):
        score=scores[key];arr,roles=arrange(score,ROLES[idx]);ticks=round(7500/score['bpm']);lead={'organ':0,'harpsi':1,'flute':5,'bell':6,'square':7,'strings':3}.get(ROLES[idx][0],0)
        struct.pack_into('<HBB',ram,TABLES+0x200+idx*4,ptr,ticks,lead);ram[ptr:ptr+len(arr)]=arr
        metadata.append({'id':idx,'key':key,'title':score['title'],'bpm_original':score['bpm'],'bpm_snes':round(7500/ticks,3),'rows':int(score['beats']*4),'duration_seconds':round(int(score['beats']*4)*ticks/500,3),'address':hex(ptr),'bytes':len(arr),'roles':roles});ptr+=len(arr)
    fx=[(1,4,32,0x91),(45,4,64,0x92),(65,5,84,0xD2),(95,7,34,0x92),(120,6,88,0x96),(180,0,40,0xD0),(125,6,76,0xC8)]
    for i,f in enumerate(fx):ram[TABLES+0x240+i*4:TABLES+0x244+i*4]=bytes(f)
    blob=bytes(ram[ORIGIN:ptr]);assert len(blob)<32768
    output.mkdir(parents=True,exist_ok=True);(output/'audio-driver.bin').write_bytes(blob);(output/'audio-driver.lst').write_text('\n'.join(assembler.listing));(output/'audio-metadata.json').write_text(json.dumps({'origin':ORIGIN,'entry':ORIGIN,'bytes':len(blob),'driver_bytes':len(code),'sha256':hashlib.sha256(blob).hexdigest(),'themes':metadata},ensure_ascii=False,indent=2))
    for i,key in enumerate(THEMES):(output/f'{key}.spc').write_bytes(make_spc(blob,i))
    print(json.dumps({'driver_bytes':len(code),'blob_bytes':len(blob),'themes':len(metadata),'out':str(output)}))
    return blob

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,default=ROOT.parent/'assets');args=parser.parse_args();build(args.out)
