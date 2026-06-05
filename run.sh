#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -q -r requirements.txt

if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

case "${1:-}" in
  import)
    python import_xlsx.py
    ;;
  email|tiktok-email)
    shift
    python import_xlsx.py 2>/dev/null || true
    python batch_email_tiktok.py "$@"
    ;;
  *)
    python batch_outreach.py "$@"
    ;;
esac
