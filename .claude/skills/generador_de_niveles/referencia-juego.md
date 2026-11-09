# Cómo se programa una misión en `juego.html`

Busca por texto, no por número de línea: los números cambian con cada versión.

## Forma de una misión (arreglo `const TASKS=[`)
```js
{icon:'clave_en_ICONS', scene:()=>BG.bedroom(), title:'Título visible',
 how:'Instrucción (HTML)' /* o ()=>'…'+DF().param para que cambie con la dificultad */,
 art:()=>SPR.algo(),            // opcional: dibujo grande del banner "MISIÓN N DE M"
 mount(a,api){                  // a = #arena (vacío). Pinta con a.innerHTML y conecta eventos.
   a.innerHTML=`…`;
   return {
     tick(dt){…},               // cada cuadro (dt en segundos); no corre durante emboscadas ni pausa
     key(e){…},                 // keydown (usar e.code; ignorar e.repeat si importa)
     keyup(e){…},
     interrupt(){…}             // OBLIGATORIO si hay "mantener presionado": soltar todo cuando entra una emboscada
   };
 }}
```
`api`: `done()` (gana; solo cuenta la primera vez), `lock()` (deja de recibir tick/teclas antes del done, p. ej. para una animación final), `float(texto,'good'|'bad')`, `penalty(seg)` (resta tiempo y lo muestra), `hurt(msg)` (−1 vida). También se puede tocar `S.time` directo.

Ayudas disponibles dentro de la IIFE: `$(sel,raíz)`, `rand(a,b)`, `randi(a,b)`, `shuffle(arr)`, `esc(txt)`, `holdable(btn,down,up)`, `mashable(btn,fn)`, `DF()` (parámetros de la dificultad activa), `val(v)`, `ico(nombre,cls)`, `pix(filas,cls,pal)`, `KL`/`KR` (teclas flecha dibujadas), `SND.tap/good/bad/hurt/alarm/ding/tick/laugh/whine/bark/mom`, `celebrate`, `fx`, `quake`.

## Lista de cosas que hay que tocar al agregar una misión
1. **`TASKS`**: insertar el objeto en su posición. La última misión debe seguir siendo «Bajar al E2»: su `done()` llama a `win()` (escena del coche).
2. **Arreglo de `art` justo después de `TASKS`** (`{const A=[()=>SPR.bed(), …]; TASKS.forEach((t,i)=>{if(A[i])t.art=A[i]})}`): es POR POSICIÓN. Si insertas en medio, agrega un elemento en ese mismo índice (`null` si el `art` va dentro del objeto). Si no, todas las misiones siguientes quedan con el dibujo equivocado.
3. **`DIFF.normal` y `DIFF.hard`**: agregar los parámetros nuevos en las DOS, con prefijo de la misión (ej. `sockCount`, `sockSpeed`). Leerlos con `DF().param` dentro de `mount`/`tick`, no al cargar.
4. **Textos con el número de misiones**: «Una gesta matutina en nueve misiones» (portada) y «Completa las <b>9 misiones en orden</b>» (instrucciones). Mejor escribirlos con `TASKS.length` y una palabra calculada, para no volver a romperlos.
5. **Lista `<ol class="quests">` en `showHowTo()`**: agregar el `<li>` en su posición, con el mismo formato.
6. **Ícono nuevo en `ICONS`** (sección «misiones») si no reutilizas uno.
7. **Escenario**: reutilizar `BG.*` o agregar un método nuevo dentro del `return {…}` de `BG`.
8. **Tiempo total** (`const TOTAL=180`): cada misión suma segundos. Si la nueva dura más de ~6 s, proponer al usuario subir `TOTAL` (no hacerlo sin preguntar).
9. **Sin emboscadas** (si el formulario lo pide): agregar `noAmbush:true` al objeto y en `step()` cambiar `if(S.task){S.nextEvent-=dt;…}` para que no descuente cuando `TASKS[S.taskIdx].noAmbush`.
10. **CSS**: agregar al `<style>` con clases propias de la misión (prefijo corto) y sin tocar estilos compartidos.
11. **Comentario de `musicTempo`** («misión 9 = 148%»): actualizar el número.
12. **`CONTEXTO.md`**: agregar la misión a la lista y subir la versión.

## Reglas de gráficos (de `CONTEXTO.md`; no romperlas)
- **Pixel art propio, sin emojis** (excepción: dentro del chat de WhatsApp). Íconos = mapas de letras de `PAL` dibujados con `pix()`; `.` = transparente; todas las filas del mismo largo; tamaño típico de 9 a 13 px; contorno `k`.
- Colores: solo letras de `PAL`. Si falta un color, agregarlo a `PAL` con una letra libre en lugar de usar hex sueltos en los íconos.
- **Escenarios** (`BG`): viewBox 120×72, `xMidYMax slice`, piso en y≈52. En pantallas anchas se recortan ~12 unidades de arriba: nada importante arriba de y≈14.
- **Personajes SVG (`SPR`)**: se pixelean con `filter:url(#px)` (bloques de 4 px) solo cuando `html.pxok` (Chrome/Edge/Firefox). Si el sprite se ve chico en pantalla, agregar su clase a la regla de `#px3` (2 px). No volver a poner filtros dentro del SVG (ya falló).
- **Fuentes**: Jacquard 24 = títulos, Press Start 2P = botones/HUD, VT323 = texto. Press Start 2P no trae acentos (el `deaccent` los quita solo) ni flechas: nunca escribir ←→↑↓ con esa fuente; usar `ico('arrow','pi rot-l|rot-r|rot-d')`, `KL`, `KR`.
- **Celular primero**: tiene que caber en 390 px de ancho sin scroll horizontal; botones táctiles de al menos 44 px; todo lo que se hace con teclado debe poder hacerse tocando.

## Probar
- Sintaxis: `zsh .claude/skills/generador_de_niveles/scripts/revisar_sintaxis.sh juego.html <scratchpad>/sintaxis`
- Juego real con bot y capturas: `python3 .claude/skills/generador_de_niveles/scripts/probar_nivel.py --juego juego.html --mision <N> --salida <scratchpad>/prueba-<slug> --bot niveles/<slug>/bot.js`
  - Corre en Chrome headless sobre una COPIA (cambia `requestAnimationFrame` por `setTimeout`, apaga emboscadas salvo `--emboscadas`). Nunca modifica `juego.html`.
  - Deja `resultado-normal.json`, `resultado-hard.json` y capturas `normal|hard-celular|escritorio.png`. `--espera <seg>` cambia en qué momento se toma la captura.
  - El bot es JS (`window.__BOT=async t=>{…}`; ver la cabecera del script para la API). Las teclas se simulan con `dispatchEvent`, igual que se descubrió en sesiones anteriores.
  - Ojo en los bots: `deaccent` le quita los acentos al texto del DOM que usa Press Start 2P («Pantalón» → «Pantalon»). Compara textos normalizados: `s.normalize('NFD').replace(/[̀-ͯ]/g,'')`.
- Lo que el headless NO prueba: Safari/iPhone (ahí no hay filtro pixel y el audio se comporta distinto) ni que se sienta bien jugarlo. Decirlo así al entregar.
