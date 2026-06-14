import os
import requests

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def enviar_alerta(mensagem):
    if not TOKEN or not CHAT_ID:
        print(f"[ALERTA LOCAL] {mensagem.replace('*', '').replace('`', '')}")
        return

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": mensagem,
        "parse_mode": "Markdown"
    }

    try:
        response = requests.post(url, json=payload, timeout=5)
        response.raise_for_status()
        print(f"Alerta enviado para o Telegram: {mensagem[:30]}...")
    except requests.exceptions.RequestException as e:
        print(f"Erro ao enviar para o Telegram: {e}")