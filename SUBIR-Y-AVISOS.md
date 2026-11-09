# Subir a GitHub + Netlify y avisos de récord

Cómo funciona:

```
Juego (Netlify) ──POST /api/record──▶ Netlify Function (netlify/functions/record.mjs)
   guarda el récord global por dificultad (Netlify Blobs)
   si se rompe ──repository_dispatch──▶ GitHub Actions (.github/workflows/aviso-record.yml)
   ──▶ abre un issue asignado a ti ──▶ te llega correo / notificación de la app de GitHub
```

Solo funciona en la versión de Netlify. En el artifact de claude.ai no hay servidor: ahí el juego sigue igual.

## 1. Subir el repo a GitHub (privado)

Sin `gh` en la Mac, lo más fácil es GitHub Desktop (https://desktop.github.com):

1. Instálalo e inicia sesión con tu cuenta.
2. File → Add Local Repository → elige `~/Desktop/not-a-morning-person-proyecto`.
3. "Publish repository" → deja marcado **Keep this code private** → Publish.

## 2. Conectar Netlify con el repo

1. En Netlify: Add new site → Import an existing project → GitHub → elige el repo.
   (O en tu sitio actual: Site configuration → Build & deploy → Link repository, para conservar la URL.)
2. Netlify lee `netlify.toml` solo: publica la carpeta `deploy/` y las funciones de `netlify/functions/`.
3. Desde ahí, cada push a `main` se publica solo. Ya no hay que arrastrar la carpeta.

## 3. Token de GitHub para que Netlify pueda avisar

1. GitHub → Settings → Developer settings → Personal access tokens → **Fine-grained tokens** → Generate new token.
2. Repository access: **Only select repositories** → este repo.
3. Permissions → Repository permissions → **Contents: Read and write** (nada más).
4. Copia el token. En Netlify → Site configuration → Environment variables agrega:
   - `GITHUB_TOKEN` = el token
   - `GITHUB_REPO` = `tu-usuario/nombre-del-repo`
5. Deploys → Trigger deploy → Deploy site (para que tome las variables).

## 4. Recibir el aviso

- GitHub te asigna el issue y te menciona. Revisa en GitHub → Settings → Notifications que "Participating, @mentions and custom" tenga Email y/o GitHub Mobile activado.

## 5. Probar sin jugar

En Terminal (cambia la URL por la de tu sitio):

```bash
curl -X POST https://TU-SITIO.netlify.app/api/record -H 'content-type: application/json' -d '{"dificultad":"normal","segundos":1,"nombre":"Prueba"}'
```

Debe responder `"record":true,..."avisado":true` (si ya hay récord mayor, responde `"record":false`) y aparecer un issue nuevo en el repo.

## Flujo de trabajo de aquí en adelante

1. Editar `juego.html`.
2. `zsh herramientas/build_deploy.sh` (regenera `deploy/index.html`).
3. Commit + push (GitHub Desktop) → Netlify publica solo.

## Límites conocidos

- El puntaje lo manda el navegador: alguien que sepa puede mandar un récord falso con `curl`. Para un juego entre amigos está bien; si crece, hay que validar del lado del servidor.
- Para borrar los récords: Netlify → Blobs → store `records`.
