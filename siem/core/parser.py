import re

LOG_PATTERN = re.compile(
    r'^(?P<ip>\S+)\s+-\s+\[(?P<time>.*?)\]\s+"(?P<method>\S+)\s+(?P<uri>\S+).*?"\s+(?P<status>\d+)'
)

def parse_line(linha):
    match = LOG_PATTERN.match(linha)
    if match:
        dados = match.groupdict()
        dados['status'] = int(dados['status'])
        return dados
    return None