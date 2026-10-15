"""RF-13: URL anormalmente longa (mais de 75 caracteres).

O comprimento é medido sobre a entrada após o trim de espaços externos (N-01).
"""

from analyzer.rules import url_length
from analyzer.url_normalizer import normalize

_BASE = "https://exemplo.com/"


def _url_com(tamanho):
    return _BASE + "a" * (tamanho - len(_BASE))


def check(url):
    return url_length.check(normalize(url))


# --- caso positivo ---

def test_url_com_76_caracteres_dispara():
    url = _url_com(76)
    assert len(url) == 76
    resultado = check(url)
    assert resultado.triggered is True
    assert resultado.reason == "url_muito_longa"


# --- caso negativo ---

def test_url_curta_nao_dispara():
    assert check("https://exemplo.com/").triggered is False


# --- casos de borda ---

def test_url_com_exatamente_75_caracteres_nao_dispara():
    url = _url_com(75)
    assert len(url) == 75
    assert check(url).triggered is False


def test_espacos_externos_nao_contam_no_comprimento():
    # N-01: o trim acontece antes; 75 caracteres úteis cercados de espaços não disparam.
    assert check("   " + _url_com(75) + "   ").triggered is False


def test_query_e_fragmento_contam_no_comprimento():
    # A regra mede a URL inteira, não só o host.
    url = "https://exemplo.com/?q=" + "x" * 40 + "#" + "y" * 20
    assert len(url) > 75
    assert check(url).triggered is True
