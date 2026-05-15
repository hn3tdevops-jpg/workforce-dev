#!/usr/bin/env bash
# pa_inventory.sh — Phase 1 inventory for PythonAnywhere Workforce reorg.
#
# Companion to docs/planning/deployment/PYTHONANYWHERE_SERVER_REORG.md.
#
# Safe and idempotent: read-only. Writes one Markdown report per run into
# ${REPORT_DIR:-$HOME/dev_hub/reports/server_reorg} and never deletes or
# moves anything. Intended to be copied to the PythonAnywhere bash console
# (where $HOME is /home/hn3t) and run there.
#
# Usage:
#   bash pa_inventory.sh                 # default report dir
#   REPORT_DIR=/tmp/wf-report bash pa_inventory.sh
#
# After running, hand the report to the human + AI collaborator pair for
# Phase 2 (Classify) per the reorg spec. Do NOT make destructive changes
# before that classification has been reviewed.

set -u
umask 077

REPORT_DIR="${REPORT_DIR:-$HOME/dev_hub/reports/server_reorg}"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
REPORT="$REPORT_DIR/inventory_${TS}.md"
mkdir -p "$REPORT_DIR"

section() { printf "\n## %s\n\n" "$1" >> "$REPORT"; }
codeblock() { printf '\n```\n' >> "$REPORT"; "$@" >> "$REPORT" 2>&1 || true; printf '```\n' >> "$REPORT"; }
note() { printf "%s\n" "$1" >> "$REPORT"; }

{
  printf "# Workforce PythonAnywhere Inventory\n\n"
  printf -- "- Generated: %s UTC\n" "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  printf -- "- Host: %s\n" "$(hostname 2>/dev/null || echo unknown)"
  printf -- "- User: %s (HOME=%s)\n" "$(id -un)" "$HOME"
  printf -- "- Spec: docs/planning/deployment/PYTHONANYWHERE_SERVER_REORG.md (Phase 1)\n"
  printf -- "- Read-only. No files moved or deleted.\n"
} > "$REPORT"

section "Git roots under \$HOME"
codeblock find "$HOME" -maxdepth 4 -type d -name .git -not -path '*/node_modules/*' \
  -not -path '*/.venv/*' -not -path '*/venv/*' -printf '%h\n'

section "Branches and remotes per git root"
while IFS= read -r dir; do
  [ -n "$dir" ] || continue
  note "### \`$dir\`"
  codeblock bash -c "cd '$dir' && git rev-parse --abbrev-ref HEAD 2>/dev/null; git remote -v 2>/dev/null; git log -1 --oneline 2>/dev/null"
done < <(find "$HOME" -maxdepth 4 -type d -name .git -not -path '*/node_modules/*' \
  -not -path '*/.venv/*' -not -path '*/venv/*' -printf '%h\n')

section "Likely frontend build directories"
codeblock find "$HOME" -maxdepth 5 -type d \( -name dist -o -name build -o -name .next -o -name out \) \
  -not -path '*/node_modules/*' -printf '%p\n'

section "WSGI files under /var/www"
codeblock bash -c 'ls -la /var/www 2>/dev/null; find /var/www -maxdepth 2 -name "*_wsgi.py" 2>/dev/null'

section "Recent PythonAnywhere logs (heads only)"
codeblock bash -c 'ls -la /var/log 2>/dev/null | head -40; for f in /var/log/*hn3t*.log /var/log/*hn3t*.access.log /var/log/*hn3t*.error.log /var/log/*hn3t*.server.log; do [ -f "$f" ] && { printf "\n--- %s ---\n" "$f"; tail -n 20 "$f"; }; done'

section "Virtual environments"
codeblock find "$HOME" -maxdepth 5 -type d \( -name .venv -o -name venv -o -name env \) \
  -not -path '*/node_modules/*' -printf '%p\n'

section "Environment files (paths only — values not printed)"
codeblock find "$HOME" -maxdepth 5 -type f \( -name '.env' -o -name '.env.*' -o -name 'env.local' \) \
  -not -path '*/node_modules/*' -printf '%p\n'

section "Top-level project roots under \$HOME"
codeblock find "$HOME" -maxdepth 2 -type d -not -name '.*' -printf '%p\n'

section "Candidate duplicate/legacy backend roots"
note "(Anything outside the canonical paths warrants Phase 2 classification.)"
note ""
note "- Canonical backend: \`$HOME/projects_active\` (and/or \`$HOME/workforce_api\` per master plan)"
note "- Canonical frontend: \`$HOME/workforce_frontend_app\` (clone of hn3tdevops-jpg/Workforce-Showcase)"
note "- Canonical dev hub: \`$HOME/dev_hub\`"
codeblock find "$HOME" -maxdepth 3 -type d \( -iname '*workforce*' -o -iname '*hospitable*' -o -iname '*frontend*' -o -iname '*backend*' -o -iname 'projects*' \) -printf '%p\n'

section "OpenAI / Copilot footprint (text search, no secrets printed)"
codeblock bash -c "grep -rIl --exclude-dir=node_modules --exclude-dir=.venv --exclude-dir=.git -e 'openai' -e 'OPENAI_API_KEY' -e 'copilot' '$HOME' 2>/dev/null | head -100"

section "Done"
note "Report written to: \`$REPORT\`"
note ""
note "Next: open this file with the operator + AI collaborator and produce the boundary decision report (Phase 2)."

printf "Inventory complete: %s\n" "$REPORT"
