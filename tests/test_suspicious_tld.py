"""RF-08: TLD pertencente à lista fechada de TLDs suspeitos (SDD §4.2).

Os casos usam apenas TLDs presentes na lista normativa do SDD, para que a suíte independa da
decisão pendente sobre a ampliação de `config.SUSPICIOUS_TLDS`.
"""

import pytest

from analyzer.rules import suspicious_tld
from analyzer.url_normalizer import normalize


def check(url):
    return suspicious_tld.check(normalize(url))


# --- casos positivos ---

@pytest.mark.parametrize("tld", ["zip", "top", "xyz", "country", "click", "link"])
def test_tlds_da_lista_normativa_disparam(tld):
    resultado = check(f"https://exemplo.{tld}/home")
    assert resultado.triggered is True
    assert resultado.reason == "tld_suspeito"


def test_tld_suspeito_com_subdominios_dispara():
    assert check("https://login.conta.exemplo.top/home").triggered is True


# --- casos negativos ---

def test_tld_comum_nao_dispara():
    assert check("https://exemplo.com/home").triggered is False


def test_tld_composto_comum_nao_dispara():
    assert check("https://exemplo.com.br/home").triggered is False


# --- casos de borda ---

def test_tld_suspeito_em_label_intermediario_nao_dispara():
    # Só o último label conta; "top" aqui é subdomínio, não TLD.
    assert check("https://top.exemplo.com/home").triggered is False


def test_tld_suspeito_no_meio_do_host_nao_dispara():
    assert check("https://exemplo.top.com/home").triggered is False


def test_tld_como_substring_de_outro_tld_nao_dispara():
    # "linkedin" contém "link", mas o TLD é "com".
    assert check("https://linkedin.com/home").triggered is False


def test_host_ip_nao_dispara():
    # O último label de um IPv4 é numérico e nunca pertence à lista.
    assert check("http://192.168.0.1/home").triggered is False


def test_comparacao_e_case_insensitive():
    # N-05: o normalizador já entrega o host em minúsculas.
    assert check("https://EXEMPLO.TOP/home").triggered is True


def test_ponto_final_absoluto_nao_impede_deteccao():
    # N-05: o ponto final absoluto é removido pelo normalizador.
    assert check("https://exemplo.top./home").triggered is True
