# Ícono de "Not a Morning Person": Baba en pixel art 32x32, exportado a PNG (1024 y tamaños de prueba).
import zlib, struct, math, os
N=32
INK=(18,12,8)
C={'bg':(40,28,58),'halo':(70,44,86),'halo2':(96,58,104),'hair':(74,42,24),'hair2':(102,62,34),
   'skin':(240,198,155),'skin2':(214,166,124),'blush':(232,128,112),'gold':(222,172,66),'gold2':(250,214,110),
   'gem':(178,34,40),'white':(255,255,255),'mouth':(122,26,26),'tongue':(232,96,122),'robe':(139,36,32),
   'robe2':(104,24,22),'yell':(250,214,110)}
img=[[C['bg'] for _ in range(N)] for _ in range(N)]
def cells():
    for y in range(N):
        for x in range(N): yield x,y,x+.5,y+.5
def paint(inside,color,outline=True):
    mask=[[inside(x+.5,y+.5) for x in range(N)] for y in range(N)]
    if outline:
        for y in range(N):
            for x in range(N):
                if not mask[y][x] and any(0<=x+dx<N and 0<=y+dy<N and mask[y+dy][x+dx] for dx,dy in((1,0),(-1,0),(0,1),(0,-1))):
                    img[y][x]=INK
    for y in range(N):
        for x in range(N):
            if mask[y][x]: img[y][x]=color(x,y) if callable(color) else color
circ=lambda cx,cy,r:(lambda x,y:(x-cx)**2+(y-cy)**2<=r*r)
ell=lambda cx,cy,rx,ry:(lambda x,y:((x-cx)/rx)**2+((y-cy)/ry)**2<=1)
def poly(pts):
    def f(x,y):
        ins=False; j=len(pts)-1
        for i in range(len(pts)):
            xi,yi=pts[i]; xj,yj=pts[j]
            if (yi>y)!=(yj>y) and x<(xj-xi)*(y-yi)/(yj-yi)+xi: ins=not ins
            j=i
        return ins
    return f
def px(x,y,c):
    if 0<=x<N and 0<=y<N: img[y][x]=c

# fondo: halo detrás de la cabeza
paint(circ(16,15,15.5),C['halo'],outline=False)
paint(circ(16,15,11),C['halo2'],outline=False)
# líneas de grito (fuera del pelo)
for (x,y) in [(1,12),(2,12),(1,18),(2,18),(29,12),(30,12),(29,18),(30,18),(2,15),(29,15)]: px(x,y,C['yell'])
# túnica / hombros
paint(poly([(6,32),(9,27),(23,27),(26,32)]),lambda x,y:C['robe'] if (x+y)%4 else C['robe2'])
paint(poly([(12,27),(16,30),(20,27)]),C['gold'])
# cuello
paint(lambda x,y:14<=x<=18 and 24<=y<=27.5,C['skin2'])
# pelo chino (círculos alrededor de la cara)
for cx,cy,r in [(9,16,3.4),(8.6,21,3.1),(10,11,3.3),(13.3,8.6,3.2),(18.7,8.6,3.2),(22,11,3.3),(23,16,3.4),(23.4,21,3.1),(10,25,2.6),(22,25,2.6)]:
    paint(circ(cx,cy,r),lambda x,y,cx=cx,cy=cy:C['hair2'] if (x+.5-cx)+(y+.5-cy)<-1.2 else C['hair'])
# cara
paint(circ(16,18,7.4),C['skin'])
# corona
paint(poly([(10.5,8.2),(11,3),(13.6,6.2),(16,1.6),(18.4,6.2),(21,3),(21.5,8.2)]),lambda x,y:C['gold2'] if y<5 else C['gold'])
px(16,5,C['gem']); px(12,6,C['gem']); px(19,6,C['gem'])
# mejillas
for (x,y) in [(10,20),(11,20),(20,20),(21,20)]: px(x,y,C['blush'])
# cejas enojadas
for (x,y) in [(10,14),(11,14),(12,15),(13,15),(14,16),(21,14),(20,14),(19,15),(18,15),(17,16)]: px(x,y,INK)
# ojos
for ex in (12,19):
    for (x,y) in [(ex,17),(ex+1,17),(ex,18),(ex+1,18)]: px(x,y,C['white'])
px(13,18,INK); px(19,18,INK)
# boca gritando
paint(ell(16,22.6,2.9,2.3),C['mouth'])
for (x,y) in [(15,23),(16,23),(15,24),(16,24),(14,24),(17,24)]:
    if img[y][x]==C['mouth']: img[y][x]=C['tongue']
px(15,21,C['white']); px(16,21,C['white'])

def png(path,w,h,pix):
    raw=b''.join(b'\x00'+bytes(c for p in row for c in p) for row in pix)
    ch=lambda t,d:struct.pack('>I',len(d))+t+d+struct.pack('>I',zlib.crc32(t+d)&0xffffffff)
    open(path,'wb').write(b'\x89PNG\r\n\x1a\n'+ch(b'IHDR',struct.pack('>IIBBBBB',w,h,8,2,0,0,0))+ch(b'IDAT',zlib.compress(raw,9))+ch(b'IEND',b''))
def scaled(s):  # nearest-neighbour: cada pixel de la cuadrícula = s x s
    return [[img[y//s][x//s] for x in range(N*s)] for y in range(N*s)]
out=os.path.join(os.path.dirname(__file__),'..','icono')
png(os.path.join(out,'icono-1024.png'),1024,1024,scaled(32))
png(os.path.join(out,'icono-512.png'),512,512,scaled(16))
png(os.path.join(out,'icono-180.png'),180,180,[[img[y*N//180][x*N//180] for x in range(180)] for y in range(180)])
png(os.path.join(out,'icono-64.png'),64,64,scaled(2))
# prueba de legibilidad: el de 64 px mostrado ampliado para revisarlo
png(os.path.join(out,'prueba-64-ampliado.png'),512,512,[[img[(y//8)//2][(x//8)//2] for x in range(512)] for y in range(512)])
print('ok')
