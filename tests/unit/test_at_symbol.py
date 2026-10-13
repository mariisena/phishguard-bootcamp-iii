"""RF-06: uso do caractere @ na seção de autoridade/userinfo.

Critério do SDD §4.2: o @ conta apenas entre "//" e o início de path/query/fragmento.
"""

from analyzer.rules import at_symbol
from analyzer.url_normalizer import normalize


def check(url):
    return at_symbol.check(normalize(url))


# --- casos positivos ---

def test_arroba_na_autoridade_dispara():
    resultado = check("http://google.com@site-falso.com/home")
    assert resultado.triggered is True
    assert resultado.reason == "uso_arroba_userinfo"


def test_userinfo_com_usuario_e_senha_dispara():
    assert check("http://usuario:senha@site-falso.com/home").triggered is True


# --- casos negativos ---

def test_url_sem_arroba_nao_dispara():
    assert check("https://site-legitimo.com/login").triggered is False


# --- casos de borda ---

def test_arroba_apenas_na_query_nao_dispara():
    assert check("https://site-legitimo.com/login?email=user@email.com").triggered is False


def test_arroba_apenas_no_path_nao_dispara():
    assert check("https://site-legitimo.com/profile/@username").triggered is False


def test_arroba_apenas_no_fragmento_nao_dispara():
    assert check("https://site-legitimo.com/index.html#contato@email.com").triggered is False


def test_multiplos_arrobas_disparam_uma_unica_vez():
    # RN-07: a heurística devolve um único resultado, independente do número de ocorrências.
    resultado = check("http://teste@google.com@site-falso.com/login")
    assert resultado.triggered is True
    assert resultado.reason == "uso_arroba_userinfo"
