# Not a Morning Person

App en vivo: https://not-a-morning-person.vercel.app

## Decisiones de diseño vs. sugerencias del IS

### 1. Migrar el deploy de Netlify a Vercel (escalabilidad)

- **Propuesta del IS:** el IS notó que la app estaba en Netlify y que la entrega pide Vercel, y me preguntó si migrar o pedir permiso para quedarme en Netlify.
- **Mi decisión:** aceptar la migración.
- **Motivo técnico:** además de cumplir con la entrega, mi diagnóstico de la Sesión 22 mostró que en Netlify Free mi cuello de botella eran los deploys, no los usuarios. Cada push a `main` gastaba 15 de mis 300 créditos al mes, así que con 20 pushes el sitio se pausaba aunque nadie entrara, y con ~10,000 usuarios al mes también. En Vercel Hobby los deploys no gastan créditos (límite de 100 al día) y lo primero que se agota es el millón de requests al CDN, alrededor de 100,000 usuarios al mes con mis supuestos (5 visitas por usuario, ~2 requests por visita). Fuentes: vercel.com/pricing y vercel.com/docs/plans/hobby, consultadas el 25 nov 2026.
- **Cómo lo verifiqué:** el deploy `efe824f` en Vercel sirve exactamente el mismo archivo que `deploy/index.html` del repo (comparación byte por byte con `cmp`). Netlify sigue conectado a `main`, así que cada push todavía le cuesta créditos: falta desconectarlo.

### 2. Dónde guardar el récord global (seguridad)

- **Propuesta del IS:** Vercel no tiene Netlify Blobs, así que el IS dio 4 opciones: función de Vercel + tabla en Supabase (recomendada), función RPC de Supabase llamada desde el navegador, Upstash Redis, o dejar la función en Netlify.
- **Mi decisión:** aceptar la función de Vercel + Supabase.
- **Motivo técnico:** uso una sola base de datos que ya conocía, en vez de agregar otro servicio que vigilar. La llave secreta de Supabase solo vive en el servidor (variable de entorno de Vercel) y nunca llega al navegador. La tabla `records` tiene RLS sin políticas, así que con la llave pública nadie la puede leer ni escribir. La función `registrar_record` compara y guarda en un solo paso, para que dos partidas al mismo tiempo no se pisen.
- **Cómo lo verifiqué:** en vivo, con la llave pública, la tabla y la función responden 401. Probé `/api/record` con input vacío, `"toString"` como dificultad y 181 segundos (todos dan 400), GET (405), un récord válido (200) y un empate (200 sin cambiar el récord). Después borré las filas de prueba.

### 3. Rotar la llave secreta que quedó expuesta (seguridad)

- **Propuesta del IS:** al guardar la llave en Vercel quedó una variable extra cuyo *nombre* era la llave secreta, visible en texto plano. El IS propuso borrar esa variable y además rotar la llave.
- **Mi decisión:** aceptar ambas cosas, aunque solo yo tengo acceso al panel de Vercel.
- **Motivo técnico:** borrar la variable no invalida la llave; mientras la llave vieja existiera en Supabase, seguiría sirviendo para saltarse RLS. Rotarla me da certeza de que la llave expuesta ya no sirve, y deja el proceso ordenado.
- **Cómo lo verifiqué:** creé la llave nueva `vercel_record` y redesplegué (`4ff57cf`). Probé `/api/record` en vivo (200) antes de borrar la llave vieja, la borré y volví a probar (200) con solo la nueva.

### 4. El récord global se puede falsificar (seguridad, riesgo aceptado)

- **Propuesta del IS:** el IS señaló que cualquiera puede mandar `{"dificultad":"normal","segundos":180}` a `/api/record` y quedarse con el récord, porque el servidor no puede comprobar que la partida ocurrió.
- **Mi decisión:** revisar y aceptar el riesgo para esta entrega, sin arreglarlo.
- **Motivo técnico:** la URL sí es pública (se ve en la pestaña Network del navegador), pero el juego solo lo usa mi clase, y lo peor que puede pasar es un récord falso: no hay datos personales ni dinero de por medio. El servidor ya limita el daño: rechaza valores fuera de 0–180, dificultades que no existen y nombres con markdown o menciones. Si el juego fuera público, haría falta validar la partida en el servidor o pedir sesión iniciada para el récord.
- **Cómo lo verifiqué:** mandar 181 segundos o `"toString"` da 400; mandar 180 sí lo aceptaría, que es justo el riesgo que estoy aceptando.

### 5. Los gráficos del juego eran emojis (diseño; error que detecté yo)

- **Propuesta del IS:** en las primeras versiones, la IA dibujó a los personajes, los objetos y las misiones con emojis del sistema, y lo presentó como terminado sin marcarlo como provisional.
- **Mi decisión:** rechazarlo y rediseñar con la IA, nivel por nivel, cada gráfico como pixel art propio, dentro del estilo medieval-arcade del juego.
- **Motivo técnico:** los emojis se ven distintos en cada sistema operativo (iPhone, Android, Windows), así que no controlaba cómo se ve el juego en el celular de cada compañero, y rompían el estilo pixeleado. Además, mis personajes son mi familia (Shrum, Ishmun, Shmane y Baba) y un emoji genérico no los representa.
- **Cómo lo verifiqué:** las versiones viejas están en el repo. `respaldo/juego-v10.html` tiene 49 emojis, `respaldo/juego-v11.html` tiene 11 y `juego.html` (v12) tiene 5, que son los del chat de WhatsApp de la misión 6, donde sí tienen sentido. Lo revisé jugando cada nivel en el celular.

## Autoevaluación

**LO en el que más crecí: #ComputationalTools.**  
Al empezar, el 5 de octubre de 2026, mi juego era un solo archivo HTML publicado como artifact y subido a Netlify arrastrando una carpeta.  
No tenía git configurado ni node instalado, y nada se publicaba solo (`CONTEXTO.md`, sección "Entorno de la Mac").  
Hoy el mismo juego vive en un repo de GitHub y cada push a `main` lo publica en Vercel.  
Las cuentas y las partidas se guardan en Supabase, con RLS para que cada usuario solo vea las suyas (`supabase/partidas.sql`).  
El récord global pasa por una función de servidor (`api/record.js`) con la llave secreta en una variable de entorno, nunca en el navegador.  
El momento que lo respalda es el 25 de noviembre.  
Al guardar la llave secreta en Vercel quedó visible en texto plano.  
No me conformé con borrar la variable: roté la llave en Supabase, redesplegué y probé el endpoint en vivo antes y después de borrar la llave vieja (entrada 3 y `DECISIONS_LOG.md`, entrada 6).  
También aprendí a medir una herramienta antes de elegirla.  
En la Sesión 22 calculé que en Netlify Free mis deploys (15 de 300 créditos cada uno) se acababan antes que mis usuarios.  
Ese número pesó en la migración a Vercel, donde el límite sube a unos 100,000 usuarios al mes (entrada 1).  
Lo que todavía me falta: desconectar Netlify, que sigue gastando créditos con cada push, y validar que el récord global venga de una partida real (entrada 4).

## Uso de IA

- **Claude (Claude Code y artifacts de claude.ai):** programó el juego, los minijuegos, el pixel art, la música y el ícono a partir de mis indicaciones. También programó el login y las partidas con Supabase, la función del récord y los deploys en Netlify y Vercel.
- **Skill `frontend-design`:** con él se hizo el rediseño visual v12 ("Amanecer en la torre").
- **En este Assignment 3:** Claude hizo la auditoría, la migración a Vercel y la función del récord, y operó los paneles de Vercel, Supabase y GitHub en Chrome con mi permiso. Las llaves secretas las pegué yo.
- **Redacción:** las entradas de "Decisiones de diseño vs. sugerencias del IS" y esta autoevaluación las redactó Claude a partir de mis respuestas: por qué migré, por qué rotar la llave, por qué acepto el riesgo del récord y el ejemplo de los emojis. Las decisiones son mías, y las revisé antes de entregar.
- **Trazabilidad:** cada propuesta de la IA y lo que decidí está en `DECISIONS_LOG.md`.
