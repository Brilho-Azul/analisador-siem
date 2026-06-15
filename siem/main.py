from core.reader import tail_log
from core.parser import parse_line
from core.rules import avaliar_evento

ARQUIVO_DE_LOG = "/var/log/nginx/siem_access.log"


def main():
    print("SIEM Analyzer Iniciado com sucesso.")
    print(f"Monitorando eventos no arquivo: {ARQUIVO_DE_LOG}")

    for linha_bruta in tail_log(ARQUIVO_DE_LOG):
        evento_normalizado = parse_line(linha_bruta)

        if evento_normalizado:
            body = evento_normalizado.get('body', '')
            info_extra = f" | Body: {body}" if body else ""
            print(
                f"[DEBUG] {evento_normalizado['ip']} | {evento_normalizado['method']} {evento_normalizado['uri']} -> HTTP {evento_normalizado['status']}{info_extra}",
                flush=True)
            avaliar_evento(evento_normalizado)


if __name__ == "__main__":
    main()