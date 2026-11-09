// Netlify Function: recibe el resultado de una partida ganada, lo compara con el
// récord global de esa dificultad y, si lo supera, avisa a GitHub (repository_dispatch).
// GitHub Actions (.github/workflows/aviso-record.yml) abre un issue asignado al dueño del repo.
//
// Variables de entorno (Netlify > Site configuration > Environment variables):
//   GITHUB_TOKEN  token fine-grained con acceso SOLO a este repo, permiso "Contents: Read and write"
//   GITHUB_REPO   "usuario/repositorio", por ejemplo "fernando/not-a-morning-person"
import { getStore } from "@netlify/blobs";

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

export default async (req) => {
  if (req.method !== "POST") return json({ error: "Usa POST" }, 405);

  let data;
  try {
    data = await req.json();
  } catch {
    return json({ error: "JSON inválido" }, 400);
  }

  const dificultad = data?.dificultad;
  const segundos = data?.segundos;
  if (!DIFFS[dificultad] || !Number.isInteger(segundos) || segundos < 0 || segundos > MAX_SEG) {
    return json({ error: "Datos inválidos" }, 400);
  }
  const nombre = limpiarNombre(data?.nombre);

  const store = getStore("records");
  const actual = await store.get(dificultad, { type: "json" });

  if (actual && segundos <= actual.segundos) {
    return json({ record: false, actual });
  }

  const nuevo = { segundos, nombre, fecha: new Date().toISOString() };
  await store.setJSON(dificultad, nuevo);

  const avisado = await avisarGitHub({
    dificultad,
    dificultadNombre: DIFFS[dificultad],
    segundos,
    nombre,
    fecha: nuevo.fecha,
    anterior: actual ?? null,
  });

  return json({ record: true, actual: nuevo, anterior: actual ?? null, avisado });
};

export const config = { path: "/api/record" };
