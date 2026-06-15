import time
import re
from telegram.telegram import enviar_alerta


PADRAO_LFI = re.compile(r'(?i)(\.\./|\.\.\\|%2e%2e%2f|/etc/passwd)')


PADRAO_SQLI = re.compile(r'(?i)(UNION\s+SELECT|OR\s+1=1|--|\'|%27|;|%3B)')


historico_requisicoes = {}
historico_404 = {}

DOS_LIMITE = 50
DOS_JANELA = 5

FUZZ_LIMITE = 15
FUZZ_JANELA = 10

historico_login_falho = {}

LOGIN_FAIL_LIMITE = 5
LOGIN_FAIL_JANELA = 60


def limpar_registros_antigos(dicionario, tempo_atual, janela):
    for ip in list(dicionario.keys()):
        dicionario[ip] = [t for t in dicionario[ip] if tempo_atual - t <= janela]
        if not dicionario[ip]:
            del dicionario[ip]


def checar_dos(ip, tempo_atual):
    if ip not in historico_requisicoes:
        historico_requisicoes[ip] = []

    historico_requisicoes[ip].append(tempo_atual)
    limpar_registros_antigos(historico_requisicoes, tempo_atual, DOS_JANELA)

    if len(historico_requisicoes[ip]) > DOS_LIMITE:
        alerta = f"⚠️ *HTTP Flood (DoS)* detectado!\nIP: `{ip}`\nMais de {DOS_LIMITE} reqs em {DOS_JANELA}s."
        enviar_alerta(alerta)
        historico_requisicoes[ip] = []  # Zera para evitar spam


def checar_fuzzing(ip, status, tempo_atual):
    if status != 404:
        return

    if ip not in historico_404:
        historico_404[ip] = []

    historico_404[ip].append(tempo_atual)
    limpar_registros_antigos(historico_404, tempo_atual, FUZZ_JANELA)

    if len(historico_404[ip]) > FUZZ_LIMITE:
        alerta = f"🔍 *Fuzzing de Diretórios* detectado!\nIP: `{ip}`\nMais de {FUZZ_LIMITE} erros 404 em {FUZZ_JANELA}s."
        enviar_alerta(alerta)
        historico_404[ip] = []


def checar_brute_force_login(ip, uri, status, tempo_atual):
    if "/api/auth/login" not in uri or status != 401:
        return

    if ip not in historico_login_falho:
        historico_login_falho[ip] = []

    historico_login_falho[ip].append(tempo_atual)
    limpar_registros_antigos(historico_login_falho, tempo_atual, LOGIN_FAIL_JANELA)

    if len(historico_login_falho[ip]) > LOGIN_FAIL_LIMITE:
        alerta = f"🚨 Brute Force de Login detectado! IP: {ip}. Múltiplas tentativas de autenticação falharam."
        enviar_alerta(alerta)
        historico_login_falho[ip] = []


def checar_lfi(ip, uri):
    if PADRAO_LFI.search(uri):
        alerta = f"🚨 *Path Traversal (LFI)*\nIP: `{ip}`\nAlvo: `{uri}`"
        enviar_alerta(alerta)


def checar_sqli(ip, uri, body=''):
    texto = uri
    if body:
        texto += ' ' + body
    if PADRAO_SQLI.search(texto):
        alerta = f"🚨 *SQL Injection*\nIP: `{ip}`\nAlvo: `{uri}`"
        if body:
            alerta += f"\nPayload: `{body}`"
        enviar_alerta(alerta)



def avaliar_evento(evento):
    tempo_atual = time.time()
    ip = evento['ip']
    status = evento['status']
    uri = evento['uri']
    body = evento.get('body', '')

    checar_dos(ip, tempo_atual)
    checar_fuzzing(ip, status, tempo_atual)

    checar_lfi(ip, uri)
    checar_sqli(ip, uri, body)
    checar_brute_force_login(ip, uri, status, tempo_atual)