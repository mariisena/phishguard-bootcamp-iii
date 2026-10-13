"""RF-10 / RN-05: possível impersonação de marca monitorada (SDD §4.2).

A regra dispara quando o host contém o nome de uma marca monitorada — após a normalização leet
speak básica (0→o, 1→l, 3→e, 4→a, 5→s, 7→t) — e o host não é o domínio oficial da marca nem um
subdomínio dele.
"""

import pytest

from analyzer.rules import brand_impersonation
from analyzer.url_normalizer import normalize


def check(url):
    return brand_impersonation.check(normalize(url))


# --- casos positivos ---

def test_marca_fora_do_dominio_oficial_dispara():
    resultado = check("https://paypal-seguranca.com/home")
    assert resultado.triggered is True
    assert resultado.reason == "possivel_impersonacao_marca:paypal"


@pytest.mark.parametrize(
    "host, marca",
    [
        ("paypa1-secure.verify-account.top", "paypal"),  # exemplo normativo do §5.2
        ("g00gle-login.com", "google"),
        ("4mazon-ofertas.com", "amazon"),
        ("nub4nk.app", "nubank"),
    ],
)
def test_substituicao_leet_dispara(host, marca):
    resultado = check(f"https://{host}/")
    assert resultado.triggered is True
    assert resultado.reason == f"possivel_impersonacao_marca:{marca}"


# --- casos negativos ---

@pytest.mark.parametrize(
    "url",
    [
        "https://paypal.com/",
        "https://itau.com.br/",
        "https://caixa.gov.br/",
        "https://amazon.com.br/",
    ],
)
def test_dominio_oficial_nao_dispara(url):
    assert check(url).triggered is False


def test_subdominio_do_dominio_oficial_nao_dispara():
    assert check("https://www.paypal.com/").triggered is False
    assert check("https://contas.google.com/").triggered is False


def test_marca_com_varios_dominios_oficiais_nao_dispara_em_nenhum():
    for host in ("microsoft.com", "login.live.com", "office.com"):
        assert check(f"https://{host}/").triggered is False, host


def test_host_sem_marca_nao_dispara():
    assert check("https://exemplo.com/").triggered is False


# --- casos de borda ---

def test_dominio_oficial_como_prefixo_de_outro_dominio_dispara():
    # "paypal.com.evil.com" não é paypal.com nem subdomínio dele.
    assert check("https://paypal.com.evil.com/").triggered is True


def test_dominio_oficial_como_sufixo_sem_ponto_dispara():
    # "evilpaypal.com" termina em "paypal.com", mas não é subdomínio (falta o ponto separador).
    assert check("https://evilpaypal.com/").triggered is True


def test_comparacao_e_case_insensitive():
    assert check("https://PayPal-Login.com/").triggered is True
    assert check("https://WWW.PAYPAL.COM/").triggered is False


def test_varias_marcas_no_host_disparam_uma_unica_vez():
    # RN-07: um único motivo, mesmo com duas marcas presentes.
    resultado = check("https://paypal-google-login.com/")
    assert resultado.triggered is True
    assert resultado.reason.startswith("possivel_impersonacao_marca:")
    assert resultado.reason.count(":") == 1


def test_marca_apenas_no_path_nao_dispara():
    # A regra considera somente o host.
    assert check("https://exemplo.com/paypal/login").triggered is False


def test_host_ip_nao_dispara():
    assert check("http://192.168.0.1/paypal").triggered is False
