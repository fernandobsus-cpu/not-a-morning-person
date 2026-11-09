#!/bin/zsh
# Revisa la sintaxis del JS de juego.html sin node: extrae el último <script> y lo compila con JavaScriptCore (osascript).
# Uso: revisar_sintaxis.sh <juego.html> <carpeta-temporal>
set -e
JUEGO="$1"; TMP="$2"; mkdir -p "$TMP"
python3 -c "
import re,sys;s=open(sys.argv[1],encoding='utf-8').read();m=re.findall(r'<script>(.*?)</script>',s,re.S)
if not m: sys.exit('No hay <script> en '+sys.argv[1])
open(sys.argv[2],'w',encoding='utf-8').write(m[-1])" "$JUEGO" "$TMP/check.js"
osascript -l JavaScript -e 'ObjC.import("Foundation");const s=$.NSString.stringWithContentsOfFileEncodingError("'"$TMP"'/check.js",4,null).js;try{new Function(s);"SINTAXIS OK"}catch(e){"ERROR DE SINTAXIS: "+e}'
