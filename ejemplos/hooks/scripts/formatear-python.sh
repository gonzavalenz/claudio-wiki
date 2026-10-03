#!/bin/bash
# PostToolUse (matcher: Edit|Write) — formatea con ruff el .py que Claude acaba de editar.
# Si quedan errores de lint que ruff no arregla solo, sale con 2: en PostToolUse eso
# le muestra el stderr a Claude (el archivo ya se escribió) para que lo corrija.
# Requiere jq y ruff.

input=$(cat)
file=$(jq -r '.tool_input.file_path // empty' <<<"$input")

[[ "$file" == *.py ]] || exit 0
command -v ruff >/dev/null 2>&1 || exit 0

ruff format --quiet "$file"
if ! out=$(ruff check --fix --quiet "$file" 2>&1); then
  echo "ruff check encontró problemas en $file que no pudo arreglar solo:" >&2
  echo "$out" >&2
  exit 2
fi
exit 0
