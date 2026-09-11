"""RF-05: host é um endereço IP (IPv4 ou IPv6).

Os testes exercitam o contrato `check(parsed) -> HeuristicResult` sobre a URL já normalizada,
que é como o `scorer` invoca a heurística.
"""

from analyzer.rules import ip_domain
from analyzer.url_normalizer import normalize


def check(url):
    return ip_domain.check(normalize(url))


# --- casos positivos ---

def test_host_ipv4_dispara():
    resultado = check("http://192.168.0.1/home")
    assert resultado.triggered is True
    assert resultado.reason == "host_ip"


def test_host_ipv6_dispara():
    # RF-05 cobre IPv4 *e* IPv6; o normalizador remove os colchetes da autoridade.
    resultado = check("http://[2001:db8::1]/home")
    assert resultado.triggered is True
    assert resultado.reason == "host_ip"


# --- casos negativos ---

def test_dominio_comum_nao_dispara():
    assert check("https://google.com/home").triggered is False


def test_dominio_iniciado_por_numeros_nao_dispara():
    assert check("https://123site.com/home").triggered is False


# --- casos de borda ---

def test_octeto_fora_do_intervalo_nao_e_ip():
    # 256 é inválido em IPv4, logo o host é tratado como nome de domínio.
    assert check("http://256.100.50.25/home").triggered is False


def test_ip_com_porta_dispara():
    # N-05: a porta não faz parte do host canônico, então o host continua sendo um IP.
    assert check("http://192.168.0.1:8080/home").triggered is True


def test_ip_com_hifens_nao_dispara():
    assert check("https://192-168-0-1.com/home").triggered is False


def test_ipv4_como_subdominio_nao_dispara():
    assert check("https://192.168.0.1.exemplo.com/home").triggered is False
