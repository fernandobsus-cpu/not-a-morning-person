// Vercel Function: POST /api/record
// Recibe el resultado de una partida ganada y lo manda a Supabase (función registrar_record,
// supabase/records.sql), que compara y guarda el récord global de esa dificultad en un solo paso.
// Si hay récord nuevo, avisa a GitHub (repository_dispatch) y Actions abre un issue
// (.github/workflows/aviso-record.yml).
//
// Variables de entorno (Vercel > Settings > Environment Variables):
//   SUPABASE_URL         https://<ref>.supabase.co
//   SUPABASE_SECRET_KEY  llave secreta (sb_secret_...). NUNCA va en el navegador.
//   GITHUB_TOKEN         opcional; fine-grained, solo este repo, "Contents: Read and write"
//   GITHUB_REPO          opcional; "usuario/repositorio"

const DIFFS = { normal: "Normal", hard: "Difícil" };
const MAX_SEG = 180;

const json = (body, status = 200) =>
  new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json", "cache-control": "no-store" },
  });

const limpiarNombre = (n) =>
  String(n ?? "")
    .replace(/[\u0000-\u001f<>@`*_#\[\]()|\\]/g, "") // sin menciones ni markdown
    .trim()
    .slice(0, 30) || "Caballero";

async function avisarGitHub(payload) {
  const { GITHUB_TOKEN, GITHUB_REPO } = process.env;
  if (!GITHUB_TOKEN || !GITHUB_REPO) {
    console.error("Faltan GITHUB_TOKEN o GITHUB_REPO; no se mandó aviso.");
    return false;
  }
  const r = await fetch(`https://api.github.com/repos/${GITHUB_REPO}/dispatches`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${GITHUB_TOKEN}`,
      Accept: "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28",
      "User-Agent": "not-a-morning-person-records",
    },
    body: JSON.stringify({ event_type: "nuevo-record", client_payload: payload }),
  });
  if (!r.ok) console.error("GitHub respondió", r.status, await r.text());
  return r.ok; // GitHub responde 204 si salió bien
}

export async function POST(req) {
  const { SUPABASE_URL, SUPABASE_SECRET_KEY } = process.env;
  if (!SUPABASE_URL || !SUPABASE_SECRET_KEY) {
    console.error("Faltan SUPABASE_URL o SUPABASE_SECRET_KEY.");
    return json({ error: "Servidor sin configurar" }, 500);
  }

  let data;
  try {
    data = await req.json();
  } catch {
    return json({ error: "JSON inválido" }, 400);
  }

  const dificultad = data?.dificultad;
  const segundos = data?.segundos;
  if (!Object.hasOwn(DIFFS, dificultad) || !Number.isInteger(segundos) || segundos < 0 || segundos > MAX_SEG) {
    return json({ error: "Datos inválidos" }, 400);
  }
  const nombre = limpiarNombre(data?.nombre);

  const r = await fetch(`${SUPABASE_URL}/rest/v1/rpc/registrar_record`, {
    method: "POST",
    headers: {
      apikey: SUPABASE_SECRET_KEY,
      Authorization: `Bearer ${SUPABASE_SECRET_KEY}`,
      "content-type": "application/json",
    },
    body: JSON.stringify({ p_dificultad: dificultad, p_segundos: segundos, p_nombre: nombre }),
  });
  if (!r.ok) {
    console.error("Supabase respondió", r.status, await r.text());
    return json({ error: "No se pudo guardar" }, 502);
  }
  const res = await r.json();

  if (!res.record) return json({ record: false, actual: res.actual });

  const avisado = await avisarGitHub({
    dificultad,
    dificultadNombre: DIFFS[dificultad],
    segundos,
    nombre,
    fecha: res.actual.fecha,
    anterior: res.anterior ?? null,
  });

  return json({ record: true, actual: res.actual, anterior: res.anterior ?? null, avisado });
}
