# Renders the game's procedural chiptune (same notes/voices as the Web Audio engine) to MP3.
import math, random, array, sys, lameenc
SR=44100
SEM={'C':0,'D':2,'E':4,'F':5,'G':7,'A':9,'B':11}
def hz(n):
    sharp=n[1]=='#'; octv=int(n[2:] if sharp else n[1:])
    return 440*2**((12*(octv+1)+SEM[n[0]]+(1 if sharp else 0)-69)/12)
MEL=('D5 A4 D5 E5 F5 E5  D5 C5 A4 G4 A4 C5  D5 A4 D5 F5 G5 A5  G5 F5 E5 D5 - -  '
     'F5 G5 A5 A5 G5 F5  E5 D5 C5 D5 E5 C5  A4 C5 D5 E5 F5 E5  D5 C5 A4 D5 - -').split()
BASS='D3 A2 C3 G2 D3 A2 G2 A2 F2 C3 C3 G2 A2 A2 D3 D3'.split()

tempo=float(sys.argv[1]); loops=int(sys.argv[2]); out=sys.argv[3]
e=0.2/tempo
total=len(MEL)*e*loops
N=int((total+1.5)*SR)
buf=[0.0]*N

def env(i,n,att,vol):
    t=i/SR
    if t<att: return 0.0001*(vol/0.0001)**(t/att)
    return vol*(0.0001/vol)**((t-att)/(max(1e-3,n/SR-att)))

def tone(f,t0,dur,vol,kind='triangle',cut=None,glide=None):
    s=int(t0*SR); n=int(dur*SR); ph=0.0; y=0.0
    a=1-math.exp(-2*math.pi*cut/SR) if cut else None
    for i in range(n):
        if s+i>=N: break
        fr=f*(glide/f)**(i/n) if glide else f
        ph=(ph+fr/SR)%1.0
        if kind=='square': x=1.0 if ph<.5 else -1.0
        elif kind=='sine': x=math.sin(2*math.pi*ph)
        elif kind=='saw': x=2*ph-1
        else: x=4*abs(ph-.5)-1
        if a: y+=a*(x-y); x=y
        buf[s+i]+=x*env(i,n,.005,vol)

def noise(t0,dur,vol,hp):
    s=int(t0*SR); n=int(dur*SR); lp=0.0; a=1-math.exp(-2*math.pi*hp/SR)
    for i in range(n):
        if s+i>=N: break
        x=random.uniform(-1,1); lp+=a*(x-lp)
        buf[s+i]+=(x-lp)*vol*(0.0001/vol)**(i/n)

def pluck(f,t,dur,vol):
    tone(f,t,dur*.8,vol*.45,'square',cut=4200)
    tone(f,t,dur,vol*.5,'triangle')

t=0.1
for step in range(len(MEL)*loops):
    i=step%len(MEL); n=MEL[i]
    if n!='-':
        ln=1
        while MEL[(i+ln)%len(MEL)]=='-' and ln<3: ln+=1
        pluck(hz(n),t,e*ln*1.7,.18)
    if i%3==0:
        pluck(hz(BASS[i//3]),t,e*3.3,.22); noise(t,.05,.07,7000)
    if i%6==0: tone(120,t,.2,.35,'sine',glide=45)
    if i%6==4: noise(t,.04,.035,8500)
    t+=e

# drone: D3 + A3 sawtooth, lowpassed
for f in (hz('D3'),hz('A3')):
    ph=0.0; y1=y2=0.0; a=1-math.exp(-2*math.pi*420/SR)
    for i in range(N):
        ph=(ph+f/SR)%1.0; x=2*ph-1; y1+=a*(x-y1); y2+=a*(y1-y2)
        buf[i]+=y2*.028

# fade out last 2.5 s, normalize
fade=int(2.5*SR); end=int((total+0.4)*SR)
for i in range(N):
    if i>end: buf[i]=0.0
    elif i>end-fade: buf[i]*=(end-i)/fade
peak=max(abs(v) for v in buf) or 1
pcm=array.array('h',(int(max(-1,min(1,v/peak*.89))*32767) for v in buf))
enc=lameenc.Encoder(); enc.set_bit_rate(192); enc.set_in_sample_rate(SR); enc.set_channels(1); enc.set_quality(2)
open(out,'wb').write(enc.encode(pcm.tobytes())+enc.flush())
print(out, round(total,1),'s')
