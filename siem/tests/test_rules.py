import time
from unittest.mock import patch
import pytest

import core.rules as rules


@pytest.fixture(autouse=True)
def reset_historico():
    rules.historico_login_falho.clear()
    rules.historico_requisicoes.clear()
    rules.historico_404.clear()


@patch("core.rules.enviar_alerta")
def test_brute_force_nao_dispara_abaixo_do_limite(mock_enviar_alerta):
    ip = "192.168.1.1"
    uri = "/api/auth/login"
    agora = time.time()

    for i in range(5):
        rules.checar_brute_force_login(ip, uri, 401, agora + i)

    mock_enviar_alerta.assert_not_called()


@patch("core.rules.enviar_alerta")
def test_brute_force_dispara_no_limite(mock_enviar_alerta):
    ip = "10.0.0.1"
    uri = "/api/auth/login"
    agora = time.time()

    for i in range(6):
        rules.checar_brute_force_login(ip, uri, 401, agora + i)

    mock_enviar_alerta.assert_called_once()
    msg = mock_enviar_alerta.call_args[0][0]
    assert "Brute Force de Login detectado!" in msg
    assert ip in msg


@patch("core.rules.enviar_alerta")
def test_brute_force_ignora_outras_uris(mock_enviar_alerta):
    agora = time.time()
    for _ in range(6):
        rules.checar_brute_force_login("10.0.0.2", "/api/produtos", 401, agora)
    mock_enviar_alerta.assert_not_called()


@patch("core.rules.enviar_alerta")
def test_brute_force_ignora_outros_status(mock_enviar_alerta):
    agora = time.time()
    for _ in range(6):
        rules.checar_brute_force_login("10.0.0.3", "/api/auth/login", 200, agora)
    mock_enviar_alerta.assert_not_called()


@patch("core.rules.enviar_alerta")
def test_brute_force_limpeza_registros_antigos(mock_enviar_alerta):
    ip = "10.0.0.4"
    uri = "/api/auth/login"
    agora = 1_000_000.0

    for i in range(6):
        rules.checar_brute_force_login(ip, uri, 401, agora + i)

    mock_enviar_alerta.assert_called_once()
    mock_enviar_alerta.reset_mock()

    rules.checar_brute_force_login(ip, uri, 401, agora + rules.LOGIN_FAIL_JANELA + 1)

    mock_enviar_alerta.assert_not_called()


@patch("core.rules.enviar_alerta")
def test_brute_force_ips_diferentes_independentes(mock_enviar_alerta):
    agora = time.time()

    for i in range(6):
        rules.checar_brute_force_login("10.0.0.5", "/api/auth/login", 401, agora + i)
        rules.checar_brute_force_login("10.0.0.6", "/api/auth/login", 401, agora + i)

    assert mock_enviar_alerta.call_count == 2
