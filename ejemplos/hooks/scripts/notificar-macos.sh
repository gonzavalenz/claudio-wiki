#!/bin/bash
# Stop / Notification — notificación nativa de macOS cuando Claude termina o te necesita.
# Si no aparece nada: Configuración del Sistema > Notificaciones > Script Editor > permitir.

input=$(cat)
evento=$(jq -r '.hook_event_name // empty' <<<"$input")
proyecto=$(basename "$(jq -r '.cwd // "."' <<<"$input")")

case "$evento" in
  Stop)         msg="Terminó de responder" ;;
  Notification) msg=$(jq -r '.message // "Necesita tu atención"' <<<"$input") ;;
  *)            msg="$evento" ;;
esac

# Pasar los textos como argumentos evita romper el AppleScript con comillas.
osascript -e 'on run argv' \
          -e 'display notification (item 1 of argv) with title (item 2 of argv)' \
          -e 'end run' "$msg" "Claude Code · $proyecto" >/dev/null 2>&1
exit 0
