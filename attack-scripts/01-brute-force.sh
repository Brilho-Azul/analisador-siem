#!/usr/bin/env bash

set -euo pipefail
TARGET="${1:-http://localhost}"
echo "🔐 Ataque: Brute Force de Login"
echo "  Alvo: $TARGET/api/auth/login"
echo "  Tentativas: 6 falhas em sequência"
for i in $(seq 1 6); do
    curl -s -o /dev/null -w "  Tentativa $i -> HTTP %{http_code}\n" \
        -X POST "$TARGET/api/auth/login" \
        -H "Content-Type: application/json" \
        -d '{"username":"admin","password":"errada'"$i"'"}' &
done
wait
echo "  ✔ Brute Force concluído (verifique alerta no SIEM)"
