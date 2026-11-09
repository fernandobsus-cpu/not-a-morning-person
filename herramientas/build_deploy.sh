#!/bin/zsh
# Genera deploy/index.html (página completa para Netlify u otro hosting) a partir de juego.html (fuente del artifact).
# El artifact de Claude envuelve la página con <!doctype>, <head> y un reset; aquí se agregan a mano.
cd "$(dirname "$0")/.."
{ printf '<!doctype html>\n<html lang="es">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
  sed -n '1,/<\/style>/p' juego.html | sed 's|^<style>$|<style>\n*,*::before,*::after{box-sizing:border-box}\nbody{margin:0}\nimg{max-width:100%}\n[hidden]{display:none!important}|'
  printf '</head>\n<body>\n'
  sed -n '/<\/style>/,$p' juego.html | tail -n +2
  printf '</body>\n</html>\n'
} > deploy/index.html
echo "deploy/index.html actualizado"
