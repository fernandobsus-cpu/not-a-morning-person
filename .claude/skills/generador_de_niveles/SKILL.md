---
name: generador_de_niveles
description: Crea un nivel (misión/minijuego) nuevo para Not a Morning Person a partir de un formulario que llena el usuario. Entrega el formulario, lo revisa, programa la misión en juego.html, la prueba con un bot en Chrome headless, revisa gráficos y claridad del pixel, la pasa por el subagente revisor-diseno y entrega el nivel funcionando. Úsalo cuando el usuario diga /generador_de_niveles o pida un nivel, misión o minijuego nuevo para el juego.
---

# /generador_de_niveles

Crea una misión nueva para el juego a partir de lo que el usuario llena en un formulario. Trabaja en `~/Desktop/not-a-morning-person-proyecto/`. Habla en español de México, directo, sin halagos. Si algo no se probó, dilo.

Antes de empezar lee `CONTEXTO.md` (estado del juego y reglas visuales) y `referencia-juego.md` de esta skill (cómo se programa una misión y la lista de cosas que hay que tocar).

Rutas usadas abajo:
- `SK` = `.claude/skills/generador_de_niveles`
- `<slug>` = nombre corto de la misión, sin acentos, con guiones (ej. `buscar-calcetines`)
- `<tmp>` = el scratchpad de la sesión (nunca el Escritorio para archivos de prueba)

Sigue los pasos en orden. No te saltes ninguno; si uno no se puede hacer, dilo y explica por qué.

## 1. Entregar formulario
1. Copia `SK/formulario.md` a `niveles/<fecha>-nuevo/formulario.md` (crea la carpeta; `<fecha>` = AAAA-MM-DD). Si el usuario ya dio el nombre de la misión, usa `niveles/<slug>/formulario.md`.
2. Ábrelo para que lo llene: `open -e <ruta>` (TextEdit).
3. Dile en 2 líneas dónde está y que te avise con "listo". **Detente aquí y espera.** No inventes las respuestas.
   - Si el usuario prefiere contestar en el chat, acepta sus respuestas ahí y pásalas al archivo tú mismo.

## 2. Revisarlo
1. Lee el formulario completo. Si hay imágenes de referencia, ábrelas con Read.
2. Revisa y anota:
   - **Huecos**: campos vacíos que sí hacen falta (meta para ganar, controles en celular, castigo al fallar).
   - **Contradicciones** (ej. "dura 5 s" pero "tocar 40 cosas").
   - **Qué tan factible es** con las reglas del juego: un solo HTML sin librerías, pixel art con `PAL`, sin emojis, Press Start 2P sin flechas ni acentos, celular de 390 px, la última misión sigue siendo «Bajar al E2».
   - **Impacto en el juego**: segundos que agrega frente a `TOTAL=180`, si se cruza con alguna emboscada, si repite una mecánica que ya existe.
3. Escribe `niveles/<slug>/ficha.md` con la ficha final: título, posición, mecánica paso a paso, controles (teclado y toque), meta, castigo, parámetros Normal/Difícil (con números), escenario, íconos/sprites nuevos, textos, sonidos, criterios de aceptación medibles (ej. "el bot la completa en 6–10 s en Normal") y supuestos que tomaste.
4. Pregunta solo lo que de verdad bloquea (AskUserQuestion, máximo 4 preguntas) y propone un valor por defecto para lo demás. Si algo del formulario es mala idea (no se entiende, rompe el ritmo, no funciona en celular), dilo con el porqué y propone otra cosa; no le des la razón por darla.
5. Enséñale un resumen corto de la ficha y **espera su visto bueno** antes de programar.

## 3. Crear código
1. Respaldo: copia `juego.html` a `respaldo/juego-v<versión actual>.html` (la versión está en `CONTEXTO.md`) si ese respaldo no existe ya.
2. Programa la misión en `juego.html` siguiendo `referencia-juego.md`, incluida la **lista de cosas que hay que tocar** (arreglo `art` por posición, `DIFF` en las dos dificultades, textos con el número de misiones, lista de instrucciones, ícono, escenario, CSS). Imita el estilo del código existente: compacto, nombres cortos, comentarios en español solo donde hacen falta.
3. Escribe `niveles/<slug>/bot.js`: un bot que juega la misión como lo haría alguien que juega bien (ver la API en la cabecera de `SK/scripts/probar_nivel.py`). Si la misión tiene azar, que el bot lea el DOM en lugar de suponer posiciones.
4. Revisa la sintaxis: `zsh SK/scripts/revisar_sintaxis.sh juego.html <tmp>/sintaxis`. Si no dice `SINTAXIS OK`, arréglalo antes de seguir.

## 4. Probar nivel
1. Corre: `python3 SK/scripts/probar_nivel.py --juego juego.html --mision <N> --salida <tmp>/prueba-<slug> --bot niveles/<slug>/bot.js`
2. Lee `resultado-normal.json` y `resultado-hard.json`. Para pasar:
   - `completada: true` en las dos dificultades.
   - `errores` vacío.
   - `segundos` dentro del rango de la ficha (Difícil igual o más lento que Normal, o más castigo).
3. Prueba también el camino de **fallar**: un segundo bot (`<tmp>/bot-falla.js`) que se equivoque a propósito, y confirma que el castigo de la ficha se aplica (`vidas` o `tiempoRestante` bajan lo esperado) y que no hay errores.
4. Prueba con emboscadas (`--emboscadas --limite 30`) si la misión las permite: no debe haber errores y, si hay "mantener presionado", `interrupt()` debe soltarlo.
5. Corre de nuevo el bot de la misión 1 o de la misión siguiente (`--mision <N+1>`) sin bot para confirmar que el resto del juego sigue montando (captura sin errores).
6. Si algo falla: arregla, vuelve a revisar la sintaxis y repite este paso. Máximo 5 vueltas; si sigue fallando, para y explícale al usuario qué pasa.

## 5. Revisar gráficos y claridad de pixeles
1. Abre con Read TODAS las capturas: `normal-celular.png`, `normal-escritorio.png`, `hard-celular.png`, `hard-escritorio.png`. Si hace falta ver un momento específico, vuelve a capturar con `--espera <seg>`.
2. Revisa contra las reglas de gráficos de `referencia-juego.md`:
   - Cada ícono/objeto se reconoce a tamaño real; bordes nítidos; contorno `k`; solo colores de `PAL`.
   - El pixeleado de 4 px no deja ilegible ningún sprite (si sí, usa `#px3` o haz el sprite más grande).
   - El texto se lee; no hay flechas ←→ ni emojis fuera de lugar; nada cortado ni encimado; nada importante arriba de y≈14 en el escenario.
   - En celular cabe en 390 px y los botones miden ≥ 44 px.
3. Arregla lo que encuentres, vuelve a correr el paso 4 (para no romper nada) y vuelve a capturar.

## 6. Revisar diseño con el subagente de diseño
1. Lanza el subagente `revisor-diseno` (Agent con `subagent_type: "revisor-diseno"`). Pásale: las rutas absolutas de las 4 capturas, la ruta de `niveles/<slug>/ficha.md`, el nombre de la misión y de sus íconos/escenario/clases CSS, y los resultados del bot (segundos por dificultad).
2. Si regresa `CAMBIOS NECESARIOS`: aplica los bloqueantes e importantes (los menores, a tu criterio; si no aplicas alguno, di cuál y por qué), repite los pasos 4 y 5, y vuelve a mandarlo al subagente. Máximo 3 vueltas.
3. No discutas con el subagente solo para aprobar: si crees que un hallazgo está mal, explícale al usuario por qué no lo aplicaste.

## 7. Entregar nivel funcional
1. Regenera la página completa: `zsh herramientas/build_deploy.sh` y copia `deploy/index.html` a `~/Desktop/not-a-morning-person/index.html` (la carpeta que se sube a Netlify).
2. Actualiza `CONTEXTO.md`: misión nueva en la lista, versión nueva, parámetros de dificultad nuevos y pendientes.
3. Guarda las capturas finales en `niveles/<slug>/capturas/` para que el usuario las vea.
4. **Pregunta antes de publicar** el artifact público (https://claude.ai/artifact/4AwtdqttkPS3wkf4ot9MuZ): lo ve cualquiera que tenga el link. Si dice que sí: primero `Artifact` con `action: "read"` de esa URL y luego publica `juego.html` con ese `url`. Recuérdale que para Netlify tiene que arrastrar de nuevo la carpeta `~/Desktop/not-a-morning-person/`.
5. Cierra con un resumen corto:
   - Qué se agregó y en qué posición quedó.
   - Resultados de las pruebas (segundos en Normal y Difícil, camino de fallar, emboscadas) y veredicto del subagente.
   - Qué cambió fuera de la misión (tiempo total, textos, etc.).
   - Qué **no** se probó: Safari/iPhone (sin filtro pixel, audio distinto) y la sensación de jugarlo con las manos. Pídele que la juegue y te diga si se siente bien.
