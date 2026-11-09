#!/usr/bin/env python3
"""Prueba una misión de Not a Morning Person en Chrome headless (sin servidor, sin librerías).

Genera una copia de prueba de juego.html (nunca toca el original), salta directo a la misión,
apaga las emboscadas, corre un bot opcional y deja:
  - <salida>/resultado-<diff>.json  -> {completada, segundos, errores, notas, ...}
  - <salida>/<diff>-<vista>.png     -> capturas en celular (390x844) y escritorio (1280x800)

Uso:
  python3 probar_nivel.py --juego juego.html --mision 10 --salida <scratchpad>/prueba \
      [--bot bot.js] [--diff normal|hard|ambas] [--espera 3] [--limite 40] [--emboscadas]

El bot es un archivo JS que define:
  window.__BOT = async (t) => { ... }
  t.arena          -> el elemento #arena de la misión
  t.$(sel)         -> querySelector dentro de la arena
  t.key(code)      -> keydown (+ keyup a los 60 ms); t.down(code) / t.up(code) por separado
  t.tap(selOrEl)   -> pointerdown + pointerup + click
  t.wait(seg)      -> espera en tiempo de juego
  t.S              -> estado del juego (S); t.DF -> dificultad activa
  t.note(texto)    -> agrega una nota al resultado
El bot termina solo; la prueba se da por completada si la misión llamó a api.done().
"""
import argparse, json, os, re, shutil, subprocess, sys, tempfile

CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
VISTAS = {'celular': (390, 844), 'escritorio': (1280, 800)}

PRE = r"""<script>
// headless congela requestAnimationFrame: solo en la copia de prueba se cambia por setTimeout
window.requestAnimationFrame=f=>setTimeout(()=>f(performance.now()),16);
window.__ERR=[];
addEventListener('error',e=>window.__ERR.push(String(e.message)+' @'+(e.lineno||'?')));
addEventListener('unhandledrejection',e=>window.__ERR.push('promesa: '+String(e.reason)));
const __ce=console.error;console.error=function(...a){window.__ERR.push('console.error: '+a.join(' '));__ce.apply(console,a)};
</script>
"""

# Se inserta DENTRO de la IIFE del juego, justo antes del último showTitle(), para tener acceso a S, TASKS, etc.
HOOK = r"""
window.__T={get S(){return S},TASKS,DIFF,get DF(){return DF()},setDiff(d){chosenDiff=d},startGame,nextTask,done:0};
{const __c=celebrate;celebrate=function(t){if(t==='¡Hecho!')window.__T.done++;return __c.apply(this,arguments)};}
"""

RUNNER = r"""<script>
(async()=>{
  const P=Object.fromEntries(new URLSearchParams(location.hash.slice(1)));
  const out=document.createElement('pre');out.id='__result';out.hidden=true;document.body.append(out);
  const R={mision:+P.m,diff:P.d,completada:false,segundos:null,errores:window.__ERR,notas:[]};
  const save=()=>{out.textContent=JSON.stringify(R)};save();
  const T=window.__T; if(!T){R.errores.push('No se inyectó el hook (¿cambió el final de juego.html?)');return save()}
  const sleep=s=>new Promise(r=>setTimeout(r,s*1000));
  try{
    T.setDiff(P.d); T.startGame();
    const S=T.S; S.timers=[]; S.nextEvent=P.e==='1'?S.nextEvent:1e9;
    S.taskIdx=+P.m-2; T.nextTask();
    await sleep(1.3);
    const t0=S.time;
    const arena=document.getElementById('arena');
    const ev=(type,code)=>dispatchEvent(new KeyboardEvent(type,{code,key:code.replace(/^(Digit|Key)/,''),bubbles:true}));
    const el=x=>typeof x==='string'?arena.querySelector(x)||document.querySelector(x):x;
    const t={arena,$:s=>arena.querySelector(s),get S(){return T.S},get DF(){return T.DF},wait:sleep,
      down:c=>ev('keydown',c),up:c=>ev('keyup',c),
      key:async c=>{ev('keydown',c);await sleep(.06);ev('keyup',c)},
      tap:x=>{const e=el(x);if(!e){R.notas.push('tap: no existe '+x);return}
        const o={bubbles:true,pointerId:1,isPrimary:true};e.dispatchEvent(new PointerEvent('pointerdown',o));e.dispatchEvent(new PointerEvent('pointerup',o));e.click()},
      note:m=>R.notas.push(String(m))};
    if(window.__BOT){
      const lim=+P.l||40;
      await Promise.race([window.__BOT(t),sleep(lim).then(()=>R.notas.push('el bot llegó al límite de '+lim+' s'))]);
      await sleep(.3);
      R.completada=T.done>0; R.segundos=+(t0-T.S.time).toFixed(1);
      R.vidas=T.S.lives; R.tiempoRestante=+T.S.time.toFixed(1);
    }
  }catch(e){R.errores.push('runner: '+e.message)}
  save();
})();
</script>
"""


def build(juego, bot):
    src = open(juego, encoding='utf-8').read()
    i = src.rfind('\nshowTitle();')
    if i < 0:
        sys.exit('No encontré "showTitle();" al final de juego.html; no puedo inyectar el hook.')
    src = src[:i] + '\n' + HOOK + src[i:]
    head, sep, body = src.partition('</style>')
    if not sep:
        sys.exit('juego.html no tiene </style>.')
    bot_js = open(bot, encoding='utf-8').read() if bot else ''
    return ('<!doctype html>\n<html lang="es">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n' + PRE +
            head.replace('<style>', '<style>\n*,*::before,*::after{box-sizing:border-box}\nbody{margin:0}\n[hidden]{display:none!important}', 1) +
            sep + '\n</head>\n<body>\n' + body +
            ('<script>\n' + bot_js + '\n</script>\n' if bot_js else '') + RUNNER + '</body>\n</html>\n')


def chrome(args, budget_ms, size, profile):
    cmd = [CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--mute-audio',
           '--autoplay-policy=no-user-gesture-required', f'--user-data-dir={profile}',
           f'--window-size={size[0]},{size[1]}', f'--virtual-time-budget={budget_ms}'] + args
    return subprocess.run(cmd, capture_output=True, text=True, timeout=180)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--juego', required=True)
    ap.add_argument('--mision', type=int, required=True, help='número de misión, empezando en 1')
    ap.add_argument('--salida', required=True)
    ap.add_argument('--bot')
    ap.add_argument('--diff', default='ambas', choices=['normal', 'hard', 'ambas'])
    ap.add_argument('--espera', type=float, default=3, help='segundos de juego antes de la captura')
    ap.add_argument('--limite', type=float, default=40, help='segundos máximos para el bot')
    ap.add_argument('--emboscadas', action='store_true', help='deja activas las emboscadas')
    a = ap.parse_args()
    if not os.path.exists(CHROME):
        sys.exit('No encontré Google Chrome en /Applications.')
    os.makedirs(a.salida, exist_ok=True)
    page = os.path.join(a.salida, 'prueba.html')
    open(page, 'w', encoding='utf-8').write(build(a.juego, a.bot))
    profile = tempfile.mkdtemp(prefix='chrome-', dir=a.salida)
    diffs = ['normal', 'hard'] if a.diff == 'ambas' else [a.diff]
    resumen = []
    try:
        for d in diffs:
            frag = f"m={a.mision}&d={d}&l={a.limite}&e={'1' if a.emboscadas else '0'}"
            url = 'file://' + os.path.abspath(page)
            if a.bot:
                r = chrome(['--dump-dom', f'{url}#{frag}'], int((a.limite + 4) * 1000), VISTAS['celular'], profile)
                m = re.search(r'<pre id="__result"[^>]*>(.*?)</pre>', r.stdout, re.S)
                res = json.loads(m.group(1).replace('&quot;', '"').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')) if m else {'errores': ['Chrome no devolvió resultado', r.stderr[-800:]]}
                json.dump(res, open(os.path.join(a.salida, f'resultado-{d}.json'), 'w'), ensure_ascii=False, indent=1)
                resumen.append(res)
            # sin bot: la captura muestra la misión recién montada
            shot = page.replace('.html', '-captura.html')
            if not os.path.exists(shot):
                open(shot, 'w', encoding='utf-8').write(build(a.juego, None))
            for vista, size in VISTAS.items():
                png = os.path.join(a.salida, f'{d}-{vista}.png')
                target = 'file://' + os.path.abspath(shot) + f'#{frag}'
                win = size
                if size[0] < 500:
                    # Chrome headless no baja de 500 px de ancho: el juego va en un iframe del ancho del teléfono
                    frame = os.path.join(a.salida, f'marco-{vista}.html')
                    open(frame, 'w', encoding='utf-8').write(
                        f'<!doctype html><body style="margin:0;background:#000"><iframe src="{target}" '
                        f'style="border:0;display:block" width="{size[0]}" height="{size[1]}"></iframe></body>')
                    target, win = 'file://' + os.path.abspath(frame), (500, size[1])
                chrome([f'--screenshot={png}', target], int((1.3 + a.espera) * 1000), win, profile)
                print(('OK ' if os.path.exists(png) else 'FALLÓ ') + png)
    finally:
        shutil.rmtree(profile, ignore_errors=True)
    for res in resumen:
        print(json.dumps(res, ensure_ascii=False))


if __name__ == '__main__':
    main()
