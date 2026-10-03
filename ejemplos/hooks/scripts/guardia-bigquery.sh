#!/bin/bash
# PreToolUse (matcher: Bash) — guardia para comandos de BigQuery.
#   - deny: `bq rm` y SQL destructivo (DROP / TRUNCATE / DELETE FROM) dentro de un comando bq
#   - ask:  `bq query` sin --dry_run (cuesta plata: que lo confirme una persona)
#   - resto: no decide nada, sigue el flujo normal de permisos
# Requiere jq.

input=$(cat)
cmd=$(jq -r '.tool_input.command // empty' <<<"$input")
lower=$(tr '[:upper:]' '[:lower:]' <<<"$cmd")

# Si no hay ningún `bq` en el comando, no nos metemos.
grep -qE '(^|[^a-z0-9_.-])bq[[:space:]]' <<<"$lower" || exit 0

decidir() {  # $1 = deny | ask, $2 = motivo
  jq -nc --arg d "$1" --arg r "$2" \
    '{hookSpecificOutput: {hookEventName: "PreToolUse", permissionDecision: $d, permissionDecisionReason: $r}}'
  exit 0
}

# bq [flags globales] rm ...
if grep -qE 'bq([[:space:]]+-[^[:space:]]+)*[[:space:]]+rm([[:space:]]|$)' <<<"$lower"; then
  decidir deny "Borrar tablas/datasets con 'bq rm' está bloqueado por la guardia del proyecto. Pedile a una persona que lo haga."
fi

# SQL destructivo dentro de un bq query
if grep -qE '(^|[^a-z_])(drop|truncate)[[:space:]]+(table|schema|view|materialized)|(^|[^a-z_])delete[[:space:]]+from([[:space:]]|$)' <<<"$lower"; then
  decidir deny "SQL destructivo (DROP/TRUNCATE/DELETE) bloqueado por la guardia del proyecto."
fi

# bq query sin --dry_run -> confirmar
if grep -qE 'bq([[:space:]]+-[^[:space:]]+)*[[:space:]]+query([[:space:]]|$)' <<<"$lower" && ! grep -q -- '--dry_run' <<<"$lower"; then
  decidir ask "Query real contra BigQuery (procesa bytes y cuesta). ¿Corrió antes el --dry_run?"
fi

exit 0
