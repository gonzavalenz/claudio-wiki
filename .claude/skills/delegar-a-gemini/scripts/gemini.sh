#!/usr/bin/env bash
# Delega una tarea chica a Gemini vía Antigravity CLI (agy), en modo solo lectura.
# Uso: gemini.sh [-m modelo] [-o archivo_salida] [-t timeout] "prompt"
# Imprime la respuesta por stdout; con -o además la guarda (ej. en .agents/inbox/).
set -euo pipefail

model="gemini-3.8-flash-medium"
out=""
timeout="5m"

while getopts "m:o:t:" opt; do
  case "$opt" in
    m) model="$OPTARG" ;;
    o) out="$OPTARG" ;;
    t) timeout="$OPTARG" ;;
    *) echo "Uso: $0 [-m modelo] [-o archivo] [-t timeout] \"prompt\"" >&2; exit 2 ;;
  esac
done
shift $((OPTIND - 1))

if [ $# -lt 1 ]; then
  echo "Falta el prompt." >&2
  exit 2
fi

if ! command -v agy >/dev/null 2>&1; then
  echo "No se encontró 'agy' (Antigravity CLI). Instalalo desde https://antigravity.google" >&2
  exit 1
fi

# En headless no se pueden aprobar comandos de shell: si Gemini intenta correr uno
# (ej. grep), se lo niegan y termina sin respuesta. Por eso se le pide solo leer archivos.
prompt="$1

Restricciones: no ejecutes comandos de terminal; usá solo herramientas de lectura de archivos. No armes un plan: respondé directamente en texto."

# --mode plan: Gemini puede leer el repo pero no editar archivos.
raw="$(agy -p "$prompt" --mode plan --model "$model" --print-timeout "$timeout" --output-format json 2>/dev/null)"
response="$(printf '%s' "$raw" | python3 -c 'import json,sys; print(json.loads(sys.stdin.read() or "{}").get("response",""))' 2>/dev/null || true)"

if [ -z "$response" ]; then
  echo "Gemini no devolvió respuesta. Salida cruda de agy:" >&2
  printf '%s\n' "$raw" >&2
  exit 1
fi

if [ -n "$out" ]; then
  mkdir -p "$(dirname "$out")"
  printf '%s\n' "$response" > "$out"
fi

printf '%s\n' "$response"
