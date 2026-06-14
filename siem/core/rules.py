import time
import re
from integrations.telegram import enviar_alerta


PADRAO_LFI = re.compile(r'(?i)(\.\./|\.\.\\|%2e%2e%2f|/etc/passwd)')


PADRAO_SQLI = re.compile(r'(?i)(UNION\s+SELECT|OR\s+1=1|--|\'|%27|;|%3B)')


historico_requisicoes = {}
historico_404 = {}
historico_405 = {}

DOS_LIMITE = 50
DOS_JANELA = 5

FUZZ_LIMITE = 15
FUZZ_JANELA = 10

MNA_LIMITE = 5
MNA_JANELA = 10


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


def checar_metodo_nao_permitido(ip, status, tempo_atual):
    if status != 405:
        return

    if ip not in historico_405:
        historico_405[ip] = []

    historico_405[ip].append(tempo_atual)
    limpar_registros_antigos(historico_405, tempo_atual, MNA_JANELA)

    if len(historico_405[ip]) > MNA_LIMITE:
        alerta = f"🛠️ *Mapeamento de API (405)* detectado!\nIP: `{ip}`\nTentativas de métodos inválidos."
        enviar_alerta(alerta)
        historico_405[ip] = []



def checar_lfi(ip, uri):
    if PADRAO_LFI.search(uri):
        alerta = f"🚨 *Path Traversal (LFI)*\nIP: `{ip}`\nAlvo: `{uri}`"
        enviar_alerta(alerta)


def checar_sqli(ip, uri):
    if PADRAO_SQLI.search(uri):
        alerta = f"🚨 *SQL Injection*\nIP: `{ip}`\nAlvo: `{uri}`"
        enviar_alerta(alerta)



def avaliar_evento(evento):
    tempo_atual = time.time()
    ip = evento['ip']
    status = evento['status']
    uri = evento['uri']

    checar_dos(ip, tempo_atual)
    checar_fuzzing(ip, status, tempo_atual)
    checar_metodo_nao_permitido(ip, status, tempo_atual)

    checar_lfi(ip, uri)
    checar_sqli(ip, uri)