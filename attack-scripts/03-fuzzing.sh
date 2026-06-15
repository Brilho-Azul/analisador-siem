#!/usr/bin/env bash

set -euo pipefail
TARGET="${1:-http://localhost}"
echo "🔍 Ataque: Fuzzing de Diretórios"
echo "  Alvo: $TARGET"
echo "  Paths: 20 inexistentes"
for path in admin config backup login wp-admin test api/v2 private \
            .env .git/config.php phpinfo.php server-status \
            console debug trace shell cmd uploads files; do
    curl -s -o /dev/null -w "  GET /$path -> HTTP %{http_code}\n" \
        "$TARGET/$path" &
done
wait
echo "  ✔ Fuzzing concluído (verifique alerta no SIEM)"
