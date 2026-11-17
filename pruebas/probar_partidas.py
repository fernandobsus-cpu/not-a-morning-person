#!/usr/bin/env python3
"""Prueba automática de «Partidas en la nube» (Assignment 2) en Chrome headless, sin servidor ni librerías.

Hace una copia de prueba de deploy/index.html (nunca toca el original) donde:
  - el cliente de Supabase se cambia por uno FALSO en memoria que registra cada insert/select
    (así no se usan contraseñas ni se escribe en la base real);
  - requestAnimationFrame se cambia por setTimeout (headless lo congela).
Un bot juega/fuerza 4 partidas y revisa:
  1. con sesión: perder por vidas → 1 fila con causa "vidas" y un culpable por vida;
  2. con sesión: ganar → 1 fila con gano=true, 9 misiones, causa null;
  3. con sesión: perder por tiempo → 1 fila con causa "tiempo" y 0 segundos;
  4. llamar endGame otra vez no duplica la fila;
  5. cada fila cumple las mismas reglas que los CHECK de supabase/partidas.sql;
  6. la portada muestra récord, partidas y culpable calculados con las filas guardadas;
  7. sin sesión: no se manda nada a Supabase y el historial local sí crece.
Además completa la misión 1 de verdad (machacando Espacio) para probar el contador de misiones.

Uso: python3 pruebas/probar_partidas.py --salida <carpeta-temporal>
Deja <salida>/resultado.json y capturas de la portada (celular y escritorio).
"""
import argparse, json, os, re, subprocess, sys, tempfile

CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FAKE_SB = r"""<script>
// Supabase FALSO (solo prueba). Modo con sesión si el hash trae "sesion=1".
window.requestAnimationFrame=f=>setTimeout(()=>f(performance.now()),16);
window.__ERR=[];addEventListener('error',e=>window.__ERR.push(String(e.message)+' @'+(e.lineno||'?')));
addEventListener('unhandledrejection',e=>window.__ERR.push('promesa: '+String(e.reason)));
window.__SB={inserts:[],selects:0,rows:[]};
(()=>{
  const conSesion=/sesion=1/.test(location.hash);
  const user=conSesion?{id:'00000000-0000-4000-8000-00000000000a',email:'bot@prueba.local',user_metadata:{nombre:'Bot'}}:null;
  if(location.hash.includes('semilla=1')) window.__SB.rows=[
    {fecha:'2026-11-10T10:00:00Z',dificultad:'normal',gano:true,causa:null,misiones_completadas:9,vidas_perdidas:1,segundos_restantes:61,vida_perdida_por:['baba']},
    {fecha:'2026-11-09T10:00:00Z',dificultad:'normal',gano:true,causa:null,misiones_completadas:9,vidas_perdidas:0,segundos_restantes:75,vida_perdida_por:[]},
    {fecha:'2026-11-08T10:00:00Z',dificultad:'normal',gano:false,causa:'vidas',misiones_completadas:5,vidas_perdidas:2,segundos_restantes:80,vida_perdida_por:['baba','shrum']},
    {fecha:'2026-11-07T10:00:00Z',dificultad:'hard',gano:false,causa:'tiempo',misiones_completadas:7,vidas_perdidas:1,segundos_restantes:0,vida_perdida_por:['ishmun']}];
  const ok=v=>Promise.resolve(v);
  function query(tabla){
    const q={_t:tabla,_op:'select',
      select(){return q},eq(){return q},order(){return q},limit(){return q},
      maybeSingle(){return ok({data:tabla==='perfiles'&&user?{nombre:'Bot'}:null,error:null})},
      insert(row){q._op='insert';q._row=row;return q},
      then(res,rej){
        if(q._op==='insert'){
          if(!user) return ok({data:null,error:{message:'sin sesión (RLS)'}}).then(res,rej);
          window.__SB.inserts.push({tabla,row:JSON.parse(JSON.stringify(q._row))});
          return ok({data:null,error:null}).then(res,rej);
        }
        window.__SB.selects++;
        return ok({data:tabla==='partidas'?(user?window.__SB.rows.slice():[]):null,error:null}).then(res,rej);
      }};
    return q;
  }
  window.supabase={createClient:()=>({
    auth:{getSession:()=>ok({data:{session:user?{user}:null}}),onAuthStateChange:()=>({data:{subscription:{unsubscribe(){}}}}),
          signOut:()=>ok({}),signUp:()=>ok({}),signInWithPassword:()=>ok({})},
    from:query})};
})();
</script>
"""

# Dentro de la IIFE del juego, antes del último showTitle(): acceso a S y funciones internas.
HOOK = r"""
window.__T={get S(){return S},TASKS,EVENTS,DIFF,CLOUD,AUTH,startGame,startEvent,endGame,win,showTitle,cloudStats,
  setDiff(d){chosenDiff=d},HIST_KEY};
"""

RUNNER = r"""<script>
(async()=>{
  const out=document.createElement('pre');out.id='__result';out.hidden=true;document.body.append(out);
  const R={casos:[],errores:window.__ERR,notas:[]};const save=()=>{out.textContent=JSON.stringify(R)};save();
  const wait=s=>new Promise(r=>setTimeout(r,s*1000));
  const until=async(f,lim=10)=>{const t0=performance.now();while(!f()){if(performance.now()-t0>lim*1000)return false;await wait(.05)}return true};
  const caso=(nombre,ok,detalle)=>{R.casos.push({nombre,ok:!!ok,detalle});save()};
  const T=window.__T;
  const conSesion=/sesion=1/.test(location.hash);
  // Mismas reglas que los CHECK de supabase/partidas.sql
  const CUL=['shrum','ishmun','shmane','baba','torpeza'];
  function valida(r){
    const e=[];const ent=(v,a,b)=>Number.isInteger(v)&&v>=a&&v<=b;
    if(!['normal','hard'].includes(r.dificultad))e.push('dificultad');
    if(typeof r.gano!=='boolean')e.push('gano');
    if(!(r.causa===null||['vidas','tiempo'].includes(r.causa)))e.push('causa');
    if(!ent(r.misiones_completadas,0,9))e.push('misiones');
    if(!ent(r.vidas_perdidas,0,3))e.push('vidas_perdidas');
    if(!ent(r.vidas_restantes,0,3))e.push('vidas_restantes');
    if(!ent(r.segundos_restantes,0,180))e.push('segundos');
    if(typeof r.uso_snooze!=='boolean')e.push('snooze');
    if(!ent(r.emboscadas,0,1e6)||!ent(r.emboscadas_ganadas,0,r.emboscadas))e.push('emboscadas');
    if(r.gano&&!(r.causa===null&&r.misiones_completadas===9))e.push('resultado(gano)');
    if(!r.gano&&r.causa===null)e.push('resultado(perdio sin causa)');
    if(r.causa==='vidas'&&r.vidas_restantes!==0)e.push('vidas_coherentes');
    if(!Array.isArray(r.vida_perdida_por)||r.vida_perdida_por.length!==r.vidas_perdidas||r.vida_perdida_por.some(k=>!CUL.includes(k)))e.push('culpables');
    if(isNaN(Date.parse(r.fecha)))e.push('fecha');
    if('user_id' in r)e.push('no debe mandar user_id');
    return e;
  }
  await until(()=>document.querySelector('#goBtn'));
  if(conSesion) await until(()=>T.AUTH.user&&T.AUTH.ready);

  if(location.hash.includes('modo=portada')){
    // Solo esperar a que se pinte la portada para la captura / revisar el texto.
    await until(()=>{const b=document.querySelector('#cloudBox');return b&&!b.hidden&&/Récord/.test(b.textContent)},5);
    const b=document.querySelector('#cloudBox');
    R.portada=b?{hidden:b.hidden,texto:b.textContent.replace(/\s+/g,' ').trim()}:null;
    const st=T.cloudStats(window.__SB.rows,'normal');
    R.statsNormal=st;
    caso('cloudStats: récord 75 s, última victoria a 14 s, 3 partidas, 2 victorias, Baba x2',
      st.best===75&&st.ultima===61&&st.falta===14&&st.jugadas===3&&st.victorias===2&&JSON.stringify(st.nemeses)==='["baba"]'&&st.nemesisVidas===2&&Math.abs(st.promVidas-1)<1e-9,JSON.stringify(st));
    caso('Portada muestra récord y culpable de la nube',b&&!b.hidden&&/1:15/.test(b.textContent)&&/0:14/.test(b.textContent)&&/Baba/.test(b.textContent),R.portada&&R.portada.texto);
    caso('Récord local oculto con sesión',document.querySelector('#localRec').hidden,'');
    // Empate (caso real de la partida en producción: ishmun 1, shrum 1)
    const emp=T.cloudStats([{dificultad:'hard',gano:false,vidas_perdidas:2,segundos_restantes:144,vida_perdida_por:['ishmun','shrum']}],'hard');
    caso('Empate: devuelve a todos los empatados (Ishmun y Shrum)',JSON.stringify(emp.nemeses)==='["ishmun","shrum"]'&&emp.nemesisVidas===1,JSON.stringify(emp));
    document.querySelector('[data-d=hard]').click(); await wait(.3);
    const tb=document.querySelector('#cloudBox').textContent.replace(/\s+/g,' ');
    caso('Portada en Difícil (1 vida de Ishmun, sin empate) usa singular',/Quien más vidas te quita: Ishmun \(1\)/.test(tb),tb);
    R.listo=true;save();return;
  }

  const ins=()=>window.__SB.inserts.filter(i=>i.tabla==='partidas');
  const hist=()=>{try{return JSON.parse(localStorage.getItem(T.HIST_KEY)||'[]').length}catch(e){return -1}};

  // --- Partida 1: completar la misión 1 de verdad y luego perder por vidas en 2 emboscadas ---
  T.setDiff('normal');
  const h0=hist();
  T.startGame();
  await until(()=>T.S.task,6);
  const t0=performance.now();
  while(T.S.stats.missions<1&&performance.now()-t0<15000){
    if(T.S.event){T.S.event.api.win('bot');}
    dispatchEvent(new KeyboardEvent('keydown',{code:'Space',key:' '}));await wait(.03);
    dispatchEvent(new KeyboardEvent('keyup',{code:'Space',key:' '}));await wait(.03);
  }
  caso('Misión 1 completada jugando (contador de misiones = 1)',T.S.stats.missions===1,'misiones='+T.S.stats.missions);
  const ev0=T.S.stats.events, won0=T.S.stats.won;
  const culpables=[];
  for(let i=0;i<2&&T.S.running;i++){
    if(T.S.event) T.S.event.api.win('bot');
    T.startEvent(); const k=T.S.event.D.key; culpables.push(k);
    T.S.event.api.fail('bot');
  }
  await until(()=>!T.S.running,3);
  const map={trump:'shrum',salo:'ishmun',mario:'shmane',mama:'baba'};
  if(conSesion){
    await until(()=>ins().length>=1,3);
    const r=ins()[0]&&ins()[0].row;
    caso('Perder por vidas → 1 fila en partidas',ins().length===1,JSON.stringify(r));
    caso('Fila 1 cumple las reglas del schema',r&&valida(r).length===0,r?valida(r).join(','):'sin fila');
    caso('Fila 1 cuadra con la partida (vidas, 1 misión, culpables, emboscadas)',
      r&&r.causa==='vidas'&&r.gano===false&&r.vidas_perdidas===2&&r.vidas_restantes===0&&r.misiones_completadas===1
       &&JSON.stringify(r.vida_perdida_por)===JSON.stringify(culpables.map(k=>map[k]))&&r.emboscadas===ev0+2&&r.emboscadas_ganadas===won0,
      'culpables esperados '+culpables.map(k=>map[k]).join(','));
    // repetir endGame no duplica
    T.S.running=true; T.endGame('lives'); await wait(.5);
    caso('Llamar endGame otra vez no duplica la fila',ins().length===1,'filas='+ins().length);
    const msg=document.querySelector('#cloudMsg');
    caso('Pantalla final dice que se guardó',msg&&!msg.hidden&&/guardada/.test(msg.textContent),msg&&msg.textContent);
  }else{
    await wait(.6);
    caso('Sin sesión: no se manda nada a Supabase',window.__SB.inserts.length===0,'inserts='+window.__SB.inserts.length);
    caso('Sin sesión: el historial local sí crece',hist()===h0+1,`antes ${h0}, después ${hist()}`);
    const msg=document.querySelector('#cloudMsg');
    caso('Sin sesión: no aparece mensaje de la nube',msg&&msg.hidden,'');
    R.listo=true;save();return;
  }

  // --- Partida 2: ganar (forzado; con 1 emboscada ganada) ---
  T.setDiff('hard');
  T.startGame(); await until(()=>T.S.task,6);
  if(T.S.event) T.S.event.api.win('bot');
  T.startEvent(); T.S.event.api.win('bot');
  const ev=T.S.stats.events, wn=T.S.stats.won;
  T.win(); await until(()=>ins().length>=2,4);
  let r=ins()[1]&&ins()[1].row;
  caso('Ganar → 1 fila más',ins().length===2,JSON.stringify(r));
  caso('Fila 2 cumple las reglas del schema',r&&valida(r).length===0,r?valida(r).join(','):'sin fila');
  caso('Fila 2: gano=true, 9 misiones, causa null, dificultad hard',r&&r.gano===true&&r.misiones_completadas===9&&r.causa===null&&r.dificultad==='hard'
    &&r.emboscadas===ev&&r.emboscadas_ganadas===wn&&r.segundos_restantes>0,'');

  // --- Partida 3: perder por tiempo ---
  await wait(2.4); // deja terminar la animación de victoria
  T.setDiff('normal');
  T.startGame(); await until(()=>T.S.task,6);
  T.S.time=0.05;
  await until(()=>!T.S.running,3); await until(()=>ins().length>=3,3);
  r=ins()[2]&&ins()[2].row;
  caso('Perder por tiempo → 1 fila más',ins().length===3,JSON.stringify(r));
  caso('Fila 3 cumple las reglas del schema',r&&valida(r).length===0,r?valida(r).join(','):'sin fila');
  caso('Fila 3: causa tiempo, 0 segundos',r&&r.causa==='tiempo'&&r.segundos_restantes===0&&r.gano===false,'');
  R.filas=ins().map(i=>i.row);
  R.listo=true;save();
})();
</script>
"""


def armar_copia(destino):
    src = open(os.path.join(RAIZ, 'deploy', 'index.html'), encoding='utf-8').read()
    src, n = re.subn(r'<script src="https://cdn\.jsdelivr\.net/npm/@supabase/[^"]+"></script>', FAKE_SB, src)
    assert n == 1, 'no encontré el <script> de supabase-js'
    i = src.rfind('showTitle();')
    assert i > 0
    src = src[:i] + HOOK + src[i:]
    src = src.replace('</body>', RUNNER + '</body>')
    open(destino, 'w', encoding='utf-8').write(src)


def chrome(args, size, profile, budget=60000):
    cmd = [CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--mute-audio', '--no-first-run',
           f'--user-data-dir={profile}', f'--window-size={size[0]},{size[1]}',
           f'--virtual-time-budget={budget}'] + args
    return subprocess.run(cmd, capture_output=True, text=True, timeout=240)


def leer(dom):
    m = re.search(r'<pre id="__result" hidden="">(.*?)</pre>', dom, re.S)
    if not m:
        return {'error': 'sin resultado', 'dom': dom[-500:]}
    import html
    return json.loads(html.unescape(m.group(1)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--salida', required=True)
    a = ap.parse_args()
    os.makedirs(a.salida, exist_ok=True)
    copia = os.path.join(a.salida, 'prueba.html')
    armar_copia(copia)
    url = 'file://' + copia
    res = {}
    for nombre, frag in [('con_sesion', 'sesion=1'), ('sin_sesion', 'sesion=0'), ('portada', 'sesion=1&semilla=1&modo=portada')]:
        prof = tempfile.mkdtemp(prefix='chrome-', dir=a.salida)
        r = chrome(['--dump-dom', f'{url}#{frag}'], (390, 844), prof)
        res[nombre] = leer(r.stdout)
    for vista, size in [('celular', (390, 844)), ('escritorio', (1280, 800))]:
        prof = tempfile.mkdtemp(prefix='chrome-', dir=a.salida)
        chrome([f'--screenshot={os.path.join(a.salida, "portada-" + vista + ".png")}', f'{url}#sesion=1&semilla=1&modo=portada'],
               size, prof, budget=4000)
    json.dump(res, open(os.path.join(a.salida, 'resultado.json'), 'w'), ensure_ascii=False, indent=1)
    total = fallas = 0
    for nombre, r in res.items():
        print(f'== {nombre} ==')
        if 'casos' not in r:
            print('  ERROR', r); fallas += 1; continue
        for c in r['casos']:
            total += 1; fallas += not c['ok']
            print(('  OK   ' if c['ok'] else '  FALLA') + ' ' + c['nombre'] + ('' if c['ok'] else '  → ' + str(c['detalle'])))
        if not r.get('listo'): print('  (el bot no terminó)'); fallas += 1
        if r.get('errores'): print('  errores JS:', r['errores']); fallas += 1
    print(f'\n{total - fallas}/{total} casos OK' if not fallas else f'\n{fallas} falla(s) de {total} casos')
    sys.exit(1 if fallas else 0)


if __name__ == '__main__':
    main()
