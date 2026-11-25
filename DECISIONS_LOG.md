# DECISIONS_LOG — Assignment 3

Registro de lo que propuso el IS (Claude) y lo que decidió Fernando. Es insumo para la sección
"Decisiones de diseño vs. sugerencias del IS" del README; aquí no se redactan esas entradas.

| # | Fecha | Propuesta del IS | Decisión de Fernando | Estado / evidencia |
|---|---|---|---|---|
| 1 | 2026-11-25 | Avisó que el deploy estaba en Netlify y la entrega pide Vercel; preguntó si migrar o pedir permiso al profesor. | Migrar a Vercel. | Proyecto `not-a-morning-person` en Vercel (Hobby), commit `efe824f`, https://not-a-morning-person.vercel.app sirve byte por byte `deploy/index.html`. |
| 2 | 2026-11-25 | Publicar `deploy/` tal cual, sin build (`vercel.json` con `outputDirectory: deploy`). | Aceptado (implícito en "hazlo en Vercel"). | `vercel.json`, commit `efe824f`. |
| 3 | 2026-11-25 | Récord global: 4 opciones (función Vercel + tabla Supabase [recomendada] / RPC Supabase / Upstash Redis / dejarlo en Netlify). | **Función + Supabase.** | `api/record.js` + `supabase/records.sql` (tabla `records` con RLS sin políticas; función `registrar_record` atómica, solo `service_role`). Probada en local con servicios simulados: 11 casos (vacío, JSON roto, `toString`, 181 s, decimal, nombre de 500 caracteres con markdown, empate, récord con y sin GitHub, Supabase caído, sin llave). |
| 3b | 2026-11-25 | Hallazgo del IS al portar: la versión de Netlify validaba con `!DIFFS[dificultad]`, así que `"toString"` pasaba la validación. Propuso `Object.hasOwn`. | Aceptado (va dentro del cambio 3). | Caso "dificultad inválida" → 400. |
| 3c | 2026-11-25 | Riesgo que sigue abierto: cualquiera puede mandar `segundos: 180` a `/api/record` y quedarse con el récord (no hay prueba de que la partida ocurrió). | Sin decidir. | Pendiente. |
| 4 | 2026-11-25 | Dejar fuera del repo `correo_pascasio.md`, `entregas/…` sin commitear y `.claude/launch.json`. | Aceptado: fuera. | No se commitearon. |
| 5 | 2026-11-25 | Netlify: dejarlo vivo como respaldo o apagarlo. | Sin decidir. | Pendiente. |

## Verificación en vivo (2026-11-25, commit `53e8db6`)

`POST https://not-a-morning-person.vercel.app/api/record`:
vacío → 400 · `toString` → 400 · 181 s → 400 · GET → 405 · válido → 200 `record:true` · empate → 200 `record:false`.
Con la llave pública, `records` y `registrar_record` responden 401. La fila de prueba ("Prueba Claude", 1 s) se borró después.

| # | Fecha | Propuesta del IS | Decisión de Fernando | Estado / evidencia |
|---|---|---|---|---|
| 6 | 2026-11-25 | Al guardar la llave, quedó una variable extra en Vercel cuyo *nombre* es la llave secreta (visible en texto plano). El IS propone borrarla y rotar la llave en Supabase. | Pendiente. | — |
