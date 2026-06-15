#!/usr/bin/env bash

set -euo pipefail

BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET="${1:-http://localhost}"

ATAQUES=(
    "Brute Force de Login"
    "HTTP Flood (DoS)"
    "Fuzzing de Diretórios"
    "Path Traversal (LFI)"
    "SQL Injection"
)

SCRIPTS=(
    "$BASE_DIR/01-brute-force.sh"
    "$BASE_DIR/02-dos-flood.sh"
    "$BASE_DIR/03-fuzzing.sh"
    "$BASE_DIR/04-lfi.sh"
    "$BASE_DIR/05-sqli.sh"
)

verde() { echo -e "\033[32m$1\033[0m"; }
amarelo() { echo -e "\033[33m$1\033[0m"; }
ciano() { echo -e "\033[36m$1\033[0m"; }
bold() { echo -e "\033[1m$1\033[0m"; }

mostrar_menu() {
    clear
    echo "$(bold "╔══════════════════════════════════════════╗")"
    echo "$(bold "║      🛡️  SIEM ATTACK TEST SUITE 🛡️       ║")"
    echo "$(bold "╚══════════════════════════════════════════╝")"
    echo ""
    echo "$(amarelo "Alvo: $TARGET")"
    echo ""
    echo "$(ciano "Escolha um ataque para executar:")"
    echo ""
    for i in "${!ATAQUES[@]}"; do
        echo "  $(bold "$((i+1)))") ${ATAQUES[$i]}"
    done
    echo ""
    echo "  $(bold "T)") 🔄 Todos os ataques (aleatório)"
    echo "  $(bold "0)") ❌ Sair"
    echo ""
    echo -n "$(verde "▶ Opção: ")"
}

executar_ataque() {
    local idx=$1
    local nome="${ATAQUES[$idx]}"
    local script="${SCRIPTS[$idx]}"
    echo ""
    echo "$(bold "──────────────────────────────────────────────")"
    echo "$(bold "▶ Executando: $nome")"
    echo "$(bold "──────────────────────────────────────────────")"
    echo ""
    bash "$script" "$TARGET"
    echo ""
    echo "$(verde "✔ Ataque finalizado.")"
}

executar_aleatorio() {
    local total=${#ATAQUES[@]}
    echo ""
    echo "$(bold "🔥 MODO: TODOS OS ATAQUES (ORDEM ALEATÓRIA)")"
    echo "$(bold "──────────────────────────────────────────────")"
    echo ""

    local indices=($(seq 0 $((total - 1))))
    for ((i = total - 1; i > 0; i--)); do
        local j=$((RANDOM % (i + 1)))
        local tmp=${indices[i]}
        indices[i]=${indices[j]}
        indices[j]=$tmp
    done

    for i in "${indices[@]}"; do
        executar_ataque "$i"
        if [[ $i -lt $((total - 1)) ]]; then
            local pausa=$((RANDOM % 3 + 1))
            echo "$(amarelo "⏳ Aguardando ${pausa}s antes do próximo ataque...")"
            sleep "$pausa"
        fi
    done

    echo "$(bold "──────────────────────────────────────────────")"
    echo "$(verde "✔ Todos os ataques foram executados!")"
    echo "$(amarelo "  Verifique os alertas recebidos no SIEM/Telegram.")"
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    while true; do
        mostrar_menu
        read -r opcao
        case "$opcao" in
            [Tt])
                executar_aleatorio
                echo ""
                echo -n "$(amarelo "Prima ENTER para voltar ao menu...")"
                read -r
                ;;
            0|q|Q)
                echo ""
                echo "$(verde "🚪 A sair...")"
                exit 0
                ;;
            [1-5])
                executar_ataque $((opcao - 1))
                echo ""
                echo -n "$(amarelo "Prima ENTER para voltar ao menu...")"
                read -r
                ;;
            *)
                echo ""
                echo "$(bold "Opção inválida!")"
                sleep 1
                ;;
        esac
    done
fi
