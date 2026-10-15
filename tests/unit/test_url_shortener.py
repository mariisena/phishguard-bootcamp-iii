"""RF-09 / RN-08: domínio de encurtador conhecido (lista fechada do SDD §4.2).

Encurtadores são sinalizados, não bloqueados; o serviço não segue o redirecionamento.
"""

import pytest

from analyzer.rules import url_shortener
from analyzer.url_normalizer import normalize


def check(url):
    return url_shortener.check(normalize(url))


# --- casos positivos ---

@pytest.mark.parametrize(
    "host",
    ["bit.ly", "tinyurl.com", "t.co", "is.gd", "goo.gl", "ow.ly", "buff.ly", "cutt.ly", "rebrand.ly"],
)
def test_encurtadores_da_lista_normativa_disparam(host):
    resultado = check(f"https://{host}/abc123")
    assert resultado.triggered is True
    assert resultado.reason == "encurtador_conhecido_destino_nao_verificado"


# --- casos negativos ---

def test_dominio_comum_nao_dispara():
    assert check("https://exemplo.com/abc123").triggered is False


def test_encurtador_apenas_no_path_nao_dispara():
    assert check("https://exemplo.com/bit.ly/abc123").triggered is False


# --- casos de borda ---

def test_comparacao_e_case_insensitive():
    assert check("https://BIT.LY/abc123").triggered is True


def test_dominio_que_contem_encurtador_como_prefixo_nao_dispara():
    # "t.co" é encurtador, "t.com" não é.
    assert check("https://t.com/abc").triggered is False


def test_encurtador_seguido_de_outro_dominio_nao_dispara():
    assert check("https://bit.ly.evil.com/abc").triggered is False


def test_dominio_que_termina_com_nome_de_encurtador_nao_dispara():
    assert check("https://notbit.ly/abc").triggered is False


# --- Issue #90 (RF-09 Opção B): correspondência por sufixo com fronteira de ponto ---

def test_www_bit_ly_dispara():
    # www.bit.ly termina em ".bit.ly" → deve disparar (RF-09 Opção B).
    # Peso e reason derivados da Tabela 4.1 do SDD.
    resultado = check("https://www.bit.ly/abc123")
    assert resultado.triggered is True
    assert resultado.reason == "encurtador_conhecido_destino_nao_verificado"


def test_notbit_ly_nao_dispara():
    # "notbit.ly" não possui ponto de fronteira antes do encurtador → NÃO deve disparar.
    assert check("https://notbit.ly/abc").triggered is False


def test_encurtador_no_meio_do_host_nao_dispara():
    # "bit.ly" aparece no início do host, mas bit.ly.evil.com termina em ".evil.com",
    # não em ".bit.ly" — portanto NÃO deve disparar.
    assert check("https://bit.ly.evil.com/abc").triggered is False
