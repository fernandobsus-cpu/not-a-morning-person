# Not a Morning Person — contexto del proyecto

Documento de traspaso para continuar el trabajo en una conversación nueva. Escrito el 5 de octubre de 2026.

## Quién es el usuario y cómo trabajar con él
- Habla español de México, informal ("wey", "jalar"). Responder en español, directo y sin halagos.
- Es admin (Owner) de la organización de Claude de Urban Capital. Ya activó el compartido externo de artifacts.
- Está tomando una clase donde usa este juego como su "app" para los assignments (entró tarde y no tiene el Assignment 1).
- Prefiere que se hagan los cambios directamente y luego se le explique qué cambió. Pide honestidad: si algo no se probó, decirlo.
- Quiere eventualmente lanzarlo en App Store con anuncios y marketing en redes para jóvenes (ver "Plan de negocio").

## Links y archivos
- **Juego publicado (artifact, público "Anyone with the link"):** https://claude.ai/artifact/4AwtdqttkPS3wkf4ot9MuZ
  - Se actualiza solo al republicar. Para actualizarlo desde otra conversación: publicar con `url` = ese link (primero `read`).
- **Documento del assignment (Claude Docs):** https://claude.ai/code/artifact/f8fa7aef-26db-44a4-aed1-85e8f707b4ac
  - Tiene: link del juego, descripción, cómo se juega, criterios de canción e ícono (con la imagen del ícono). Todos los criterios marcados como cumplidos.
- **También está subido a Netlify** por el usuario (arrastrando la carpeta `~/Desktop/not-a-morning-person/`). No conozco la URL de Netlify. Para actualizarlo, el usuario arrastra de nuevo la carpeta en Deploys. No hay deploy automático (no hay git/gh/node instalados en la Mac).
- **Esta carpeta (`~/Desktop/not-a-morning-person-proyecto/`):**
  - `juego.html` — FUENTE del artifact (sin doctype/head/body; el artifact los agrega). Editar aquí y publicar este archivo.
  - `herramientas/build_deploy.sh` — genera `deploy/index.html` (página completa). Después copiar a `~/Desktop/not-a-morning-person/index.html` para Netlify.
  - `icono/` — ícono de Baba en 1024, 512, 180 y 64 px (`herramientas/icono_baba.py` lo regenera con python3, sin librerías).
  - `musica/` — MP3 del tema (59 s) y versión emboscada (45 s), generados con `herramientas/render_musica.py` (necesita `lameenc`: `python3 -m venv env && env/bin/pip install lameenc`; uso: `python render_musica.py <tempo> <loops> <salida.mp3>`).

## Entorno de la Mac
- Sin node/npm, sin brew, sin gh, sin ffmpeg. Hay python3 3.9 y git (sin configurar).
- Revisar sintaxis JS: extraer el `<script>` a un .js y evaluarlo con `osascript -l JavaScript` (`new Function(src)`).
- Probar visualmente: python no puede servir desde el Escritorio (permisos), así que `.claude/launch.json` sirve una copia en el scratchpad de la sesión (`cp deploy/index.html <scratchpad>/site/`). El Browser pane limita `requestAnimationFrame` a ~1 fps cuando no está al frente: para probar se hace una copia `test.html` que reemplaza rAF por `setTimeout` (solo prueba, no se publica). Las teclas simuladas de la herramienta `computer` no llegan bien al juego; usar `dispatchEvent(new KeyboardEvent('keydown',{code:'Space'}))`.
- El Browser pane no puede abrir el link de claude.ai (pide login) ni archivos `file://`.

## Actualización 21 oct 2026: versión 12 («Amanecer en la torre»)
- Rediseño visual hecho con el skill `frontend-design` (instalado en `.claude/skills/frontend-design/`). Publicado como versión 12 del artifact; `juego.html` y `deploy/index.html` ya son v12.
- Respaldo de la v11: `respaldo/juego-v11.html` y `respaldo/netlify-index-v11.html`. Comparación con capturas: `comparacion-v11-v12/`.
- Cambios: solo Jacquard 24 + VT323 (se quitó Press Start 2P, ya hay acentos), fondo de cielo de madrugada en bandas, portada con el cuarto y despertador, instrucciones como ruta de 9 misiones con botón fijo «Jugar», HUD de un renglón pegado arriba, historial que cabe en celular. La mecánica no cambió.
- Netlify NO está actualizado: arrastrar de nuevo la carpeta con el `deploy/index.html` nuevo.

## El juego (estado de la versión 11 del artifact)
Juego web de un solo archivo HTML/JS, sin librerías. Estilo arcade medieval pixeleado.

**Objetivo:** 9 misiones en orden en 180 s; 2 vidas; perder = sin vidas o tiempo en 0.

**Misiones (en orden):**
1. Pararse de la cama — machacar Espacio/botón; la barra se vacía sola.
2. Lavarse los dientes — alternar ← →, 24 veces.
3. Bañarse — tocar 14 manchas de mugre.
4. Vestirse — elegir prenda correcta (Camisa, Pantalón, Calcetines, Zapatos, Cinturón) entre señuelos; error = −2 s.
5. Servir el café — mantener presionado y soltar en la franja dorada.
6. Pedirle el licuado a Naye por WhatsApp — tocar palabras en orden ("Naye, ¿me haces mi licuado de proteína porfa?"). (El usuario pidió que fuera "antes de salir del cuarto".)
7. Agarrar el café — mantener la taza derecha con ← → mientras camina.
8. Picarle al elevador — el usuario vive en el **piso 21**; llamar y entrar cuando abren las puertas (1.4 s).
9. Bajar al E2 — tablero con PH, 25…1 y E1–E5; presionar ¡Alto! cuando se ilumina **E2**; en estacionamientos baja más lento. Final: puertas abren en E2 y el coche arranca.

**Enemigos (emboscadas):** antes se llamaban Trump, Salo, Mario y Mamá; el usuario los renombró. Las claves internas siguen siendo `trump/salo/mario/mama`.
| Nombre | Quién es | Qué hace | Cómo se vence |
|---|---|---|---|
| Shrum | Perro: golden doodle bebé (rizos dorados) | Se hace popó | Tocar todas las popós (se mueven) |
| Ishmun | Hermano: flaco, alto, chinos negros, piel clara ligeramente morena | Esconde las llaves del coche | Encontrar el objeto que tiembla |
| Shmane | Hermano chico (al usuario le gusta su diseño) | Pide tiernamente que lo lleve a la escuela | Decir "No" varias veces; el botón se mueve |
| Baba | Mamá (al usuario le encanta su diseño, con corona y chinos) | "¡Ven un momento!" | Marcar secuencia de flechas |

**Snooze:** 1 solo por partida, tecla Z o botón; +1 vida, −45 s.

**Dificultad (se elige en la portada; objeto `DIFF` en el código):**
- Normal (default): emboscadas de 7–8 s, cada 8–13 s, 12% de doble emboscada; 5 popós, 2 intentos con Ishmun, 3 "No", 5 flechas; tirar café o fallar E2 = −5 s.
- Difícil: emboscadas de 5.5–6.5 s, cada 5–9 s, 30% doble; 6 popós, 1 intento, 4 "No", 6 flechas; tirar café o fallar E2 = −1 vida.
- Las emboscadas se acortan conforme avanzan las misiones (15% normal, 25% difícil).
- Historia: el usuario pidió primero que se perdiera en promedio ≥1.5 vidas por partida, luego dijo que quedó "imposible", y por eso se creó el modo Normal. Falta calibrar con partidas reales.

**Música:** chiptune generado en vivo con Web Audio (melodía en Re dórico 6/8, bajo, tambor, ruido, bordón). Loop de 9.6 s. Tempo +6% por misión (función `musicTempo`: misión 1 = 100%, misión 9 = 148%), ×1.2 en emboscadas, ×1.1 en los últimos 30 s. En iPhone se fuerza `navigator.audioSession.type='playback'` y un audio silencioso para que suene con el switch de silencio (no probado en iPhone real).

**Gráficos:** personajes dibujados como SVG animado con CSS (ojos que se mueven, cola, lágrimas, etc.).
- Pixeleado: filtro CSS `filter:url(#px)` (bloques de 4 px; antes 6, el usuario dijo que se dejaba de entender) y `#px3` (ahora 2 px con feOffset+feMerge; antes 3 px, para retratos pequeños), solo cuando `html.pxok` (Chrome/Edge/Firefox). En Safari/iOS se ven como dibujo normal porque ahí el filtro hacía desaparecer los personajes.
- Un intento de filtro dentro de cada SVG falló (retratos vacíos en algunos tamaños); no volver a usarlo.
- Retratos pequeños: Shrum e Ishmun usan versión "cara" recortada (`SPR.dog('',true)`, `SPR.salo('')` con viewBox recortado + clase `crop`).
- v11 (5 oct 2026, mejora visual): ya no hay emojis en la interfaz salvo los del chat de WhatsApp. Todo es pixel art propio: objeto `ICONS` (mapas de letras → colores de `PAL`, se dibujan con `pix()`/`ico()`): corazones, reloj de arena, bocina, pausa, Zzz, flecha, despertador, iconos de las 9 misiones, ropa, escondites de Ishmun, llave, puerta.
- Flechas: UN solo dibujo (`ico('arrow')`) girado con clases `rot-d/rot-l/rot-r`. La fuente Press Start 2P no trae flechas (salían chicas o como cuadros): no usar ←→↑↓ en texto con esa fuente; para teclas usar `KL`/`KR`.
- Escenarios: `BG.bedroom/bathroom/kitchen/hallway/lobby/elevator()` dibujan un fondo pixel (viewBox 120×72, `xMidYMax slice`) detrás de cada misión (`scene` en cada TASK). En pantallas anchas se recorta ~12 unidades de arriba: no poner adornos arriba de y≈14.
- Efectos: `celebrate()` (destello + sello "¡Hecho!" + confeti), `fx('good'|'bad'|'ambush')`, `quake()`; emboscadas con franjas animadas; viñeta roja en los últimos 30 s; animación de entrada en la pantalla entre misiones.
- Respaldo de la v10 en `respaldo/juego-v10.html`.
- Fuentes: Jacquard 24 (títulos), Press Start 2P (botones/HUD), VT323 (texto). Press Start 2P no trae acentos: un MutationObserver (`deaccent`) quita acentos solo en texto con esa fuente.

**Historial de partidas:** `localStorage` clave `nmp-historial`, máximo 20 (while borra la más antigua). Registro actual: `{fecha, dificultad, gano, vidasPerdidas, segundos, snooze}`. La pantalla final muestra promedio de vidas perdidas por modo y mensaje: <1 "muy fácil", 1–1.5 "justa", >1.5 "muy difícil", más tabla de últimas 5.

## Trabajo de la clase (assignments ya hechos en esta conversación)
1. **Lógica con for/if:** se describió la funcionalidad del historial (pasos, condición, repetición, prompt). Ya implementada.
2. **Schema JSON acordado (Planificador/Validador/Documentador):**
```jsonc
{
  "fecha": "string",               // ISO 8601 UTC
  "dificultad": "string",          // "normal" | "hard"; si falta (registros viejos) = "hard"
  "gano": "boolean",
  "causa": "string | null",        // "vidas" | "tiempo"; null si ganó
  "misionesCompletadas": "integer",// 0–9; 9 si ganó
  "vidasPerdidas": "integer",      // 0–3 (2 + 1 del snooze)
  "vidasRestantes": "integer",     // 0–3; 0 si causa = "vidas"
  "segundosRestantes": "integer",  // 0–180; puede ser 0 aunque gane
  "usoSnooze": "boolean",
  "emboscadas": "integer",
  "emboscadasGanadas": "integer",  // ≤ emboscadas
  "vidaPerdidaPor": ["string"]     // "shrum"|"ishmun"|"shmane"|"baba"|"torpeza"; largo = vidasPerdidas
}
```
   PENDIENTE: el juego todavía guarda el formato simple; actualizarlo a este schema cuando el usuario lo pida.
3. **Prompt para generar un dato con el schema:** se probó en vivo con un agente de Claude; regresó JSON válido. Hallazgo: "perdió en la misión 7" es ambiguo; mejor "perdió mientras jugaba la misión 7 (completó 6)".
4. **Criterios de canción e ícono** (corregidos):
   - Canción: instrumental; loop de 8–10 s; tempo +6% por misión (100% → 148%); éxito = melodía se distingue sobre efectos, loop sin cortes, misión 9 ≥40% más rápida. CUMPLE.
   - Ícono: sin texto, arcade pixeleado, 1024 × 1024 px; éxito = Baba reconocible a 64 × 64 px. HECHO: `icono/icono-1024.png` (Baba en pixel art 32 × 32, generado con `herramientas/icono_baba.py`; también 512, 180 y 64 px). Agregado al documento del assignment.

## Plan de negocio (opinión ya dada al usuario)
- Así como está no es producto de mercado: el chiste es interno, dura 3 min, poca rejugabilidad, mecánica tipo WarioWare.
- Cambio clave recomendado: que cada jugador meta a su propia familia/mascota (nombres y apariencia).
- Después: semana lunes–viernes con dificultad creciente, orden aleatorio, tarjeta de resultado para compartir, diseño mobile-first.
- Anuncios: NO saturar ("anuncios en anuncios en anuncios" espanta a jóvenes). Usar anuncio con recompensa para el snooze/revivir, uno entre días, y compra para quitar anuncios.
- App Store: Apple Developer 99 USD/año (confirmar), Google Play 25 USD una vez; empaquetar con Capacitor; riesgo de rechazo de Apple por poco contenido (guideline 4.2); evitar público <13 años; revisar marca "Not a Morning Person".
- Validar barato primero: itch.io/CrazyGames + 10–15 videos de TikTok; medir cuántos juegan 3+ veces.

## Pendientes / ideas abiertas
- Actualizar el historial al schema completo.
- Calibrar la dificultad Normal con partidas reales del usuario.
- Probar en iPhone/Safari (personajes visibles y música).
- Detalle visual: en retratos pequeños, Shrum dorado contrasta poco con el pergamino.
- Pendiente visual: el emulador de celular del Browser pane no aplica el filtro pixel (igual que Safari/iPhone, a propósito). No se ha visto en un iPhone real.
- Si se quiere deploy automático: GitHub + Netlify (el usuario tendría que crear cuenta e instalar GitHub Desktop o gh).
