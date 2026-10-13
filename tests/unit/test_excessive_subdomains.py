"""RF-07: excesso de subdomínios (critério operacional do SDD §4.2).

Os dois últimos labels são tratados como domínio-base; a heurística dispara quando houver mais de
três labels anteriores a eles.
"""

from analyzer.rules import excessive_subdomains
from analyzer.url_normalizer import normalize


def check(url):
    return excessive_subdomains.check(normalize(url))


# --- casos positivos ---

def test_quatro_subdominios_dispara():
    # Exemplo literal do SDD §4.2.
    resultado = check("https://a.b.c.d.example.com/")
    assert resultado.triggered is True
    assert resultado.reason == "subdominios_excessivos"


def test_muitos_subdominios_dispara():
    # Caso de borda listado no SDD §7.
    assert check("https://a.b.c.d.e.exemplo.com/").triggered is True


# --- casos negativos ---

def test_tres_subdominios_nao_dispara():
    # Exemplo literal do SDD §4.2: limite exato.
    assert check("https://a.b.c.example.com/").triggered is False


def test_dominio_simples_nao_dispara():
    assert check("https://example.com/").triggered is False


def test_host_de_um_label_nao_dispara():
    assert check("http://localhost/").triggered is False


# --- casos de borda ---

def test_www_conta_como_label():
    # O critério conta labels; "www" não recebe tratamento especial (N-07 vale só para listas).
    assert check("https://www.a.b.c.example.com/").triggered is True


def test_sufixo_composto_e_aproximado_pelos_dois_ultimos_labels():
    # Aproximação conhecida, sem Public Suffix List: em ".com.br" o domínio-base vira "com.br",
    # então "exemplo" passa a contar como subdomínio.
    assert check("https://a.b.c.exemplo.com.br/").triggered is True
    assert check("https://a.b.exemplo.com.br/").triggered is False


def test_ipv4_nao_dispara():
    assert check("http://192.168.0.1/").triggered is False


def test_ponto_final_absoluto_nao_conta_como_label():
    # N-05: o ponto final é removido antes da contagem.
    assert check("https://a.b.c.example.com./").triggered is False
