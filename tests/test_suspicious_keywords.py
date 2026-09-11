"""RF-14: palavra-chave sensível no path ou na query.

A heurística apenas detecta; a condição da RN-06 (só pontua junto de outro sinal) é aplicada pelo
`scorer` e está coberta em `test_scorer.py`.
"""

from analyzer.rules import suspicious_keywords
from analyzer.url_normalizer import normalize


def check(url):
    return suspicious_keywords.check(normalize(url))


# --- casos positivos ---

def test_palavra_chave_no_path_dispara():
    resultado = check("https://exemplo.com/secure/login.php")
    assert resultado.triggered is True
    assert resultado.reason == "palavra_chave_sensivel_no_path_query"


def test_palavra_chave_na_query_dispara():
    assert check("https://exemplo.com/index.php?action=verify").triggered is True


# --- casos negativos ---

def test_path_e_query_limpos_nao_disparam():
    assert check("https://exemplo.com/sobre-nos").triggered is False


def test_palavra_chave_apenas_no_host_nao_dispara():
    # RF-14 restringe a busca a path/query; o host não participa desta heurística.
    assert check("https://meu-banco-seguro.com/home").triggered is False


# --- casos de borda ---

def test_busca_e_case_insensitive():
    assert check("https://exemplo.com/UpDaTe/LoGiN").triggered is True


def test_multiplas_ocorrencias_disparam_uma_unica_vez():
    # RN-07: várias palavras não acumulam; o retorno é um único HeuristicResult.
    resultado = check("https://exemplo.com/update?action=login")
    assert resultado.triggered is True
    assert resultado.reason == "palavra_chave_sensivel_no_path_query"


def test_palavra_chave_como_substring_dispara():
    assert check("https://exemplo.com/portal-login-novo/").triggered is True


def test_palavra_chave_apenas_no_fragmento_nao_dispara():
    # N-08: o fragmento não participa da pontuação.
    assert check("https://exemplo.com/home#login").triggered is False
