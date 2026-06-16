# Analisador SIEM

## O que é
Este repositório implementa um ambiente simples de detecção de ameaças em aplicações web.  
Ele combina uma API vulnerável (FastAPI), um proxy reverso (Nginx) e um analisador SIEM em Python que monitora logs e gera alertas (incluindo envio para Telegram).

## Infraestrutura
- **backend/**: API FastAPI com endpoints de produtos e login.
- **nginx/**: proxy reverso que recebe as requisições e grava logs em formato customizado.
- **siem/**: consumidor de logs do Nginx que aplica regras de detecção.
- **attack-scripts/**: scripts para simular ataques (brute force, DoS, fuzzing, LFI e SQLi).
- **docker-compose.yml**: orquestra os serviços:
  - `backend` (porta interna 8000),
  - `nginx` (porta exposta 80),
  - `siem` (leitura dos logs do Nginx por volume compartilhado).

## Fluxo de Operação
1. O cliente envia uma requisição para `http://localhost` (Nginx).
2. O Nginx encaminha para o backend FastAPI.
3. O Nginx registra cada requisição em `/var/log/nginx/siem_access.log`.
4. O serviço `siem` faz *tail* contínuo desse log.
5. Cada linha é parseada e avaliada por regras de segurança:
   - HTTP Flood (DoS),
   - Fuzzing por excesso de 404,
   - Brute force em `/api/auth/login`,
   - Path Traversal (LFI),
   - SQL Injection (URI/body).
6. Quando detectado um padrão suspeito, o SIEM gera alerta no console e, se configurado, envia para Telegram.

## Como testar em casa

### 1) Pré-requisitos
- Docker e Docker Compose instalados.
- (Opcional) Chat do Telegram + bot para receber alertas.

### 2) Configurar variáveis de ambiente
```bash
cp .env.example .env
```
Edite o arquivo `.env` com os dados do seu bot/chat.  
Se deixar vazio, os alertas serão exibidos apenas no console do SIEM.

### 3) Subir o ambiente
```bash
docker compose up --build
```

### 4) Validar API manualmente
```bash
curl http://localhost/api/produtos
```

### 5) Simular ataques
Em outro terminal:
```bash
cd attack-scripts
bash menu.sh http://localhost
```

### 6) Executar testes automatizados
Backend:
```bash
cd backend
python -m pytest -q
```

SIEM:
```bash
cd siem
python -m pytest -q
```
