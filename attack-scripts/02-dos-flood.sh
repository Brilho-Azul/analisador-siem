#!/usr/bin/env bash

set -euo pipefail
TARGET="${1:-http://localhost}"
echo "⚠️  Ataque: HTTP Flood (DoS)"
echo "  Alvo: $TARGET/api/produtos"
echo "  Requisições: 60 em paralelo"
for i in $(seq 1 60); do
    curl -s -o /dev/null "$TARGET/api/produtos" &
done
wait
echo "  ✔ DoS concluído (verifique alerta no SIEM)"
