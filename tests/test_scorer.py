"""Orquestração do scorer: precedência de listas, agregação e RN-01 a RN-07.

Os scores esperados vêm da Tabela 4.1 do SDD, não da leitura de `config.POINTS`, para que uma
alteração indevida de peso quebre a suíte.
"""

import pytest

from analyzer.blocklist import DomainLists
from analyzer.scorer import calculate_risk, classify
from analyzer.url_normalizer import InvalidURLError

# Listas de teste injetadas — a suíte não depende de arquivos externos (RNF-02).
LISTAS = DomainLists(
    allowlist=frozenset({"site-legitimo.com"}),
    blocklist=frozenset({"malware.test"}),
)

VAZIAS = DomainLists(allowlist=frozenset(), blocklist=frozenset())


def analisar(url, listas=VAZIAS):
    return calculate_risk(url, listas)


# --- RN-02: faixas de classificação ---

@pytest.mark.parametrize(
    "score, esperado",
    [(0, "segura"), (29, "segura"), (30, "suspeita"), (59, "suspeita"), (60, "perigosa"), (100, "perigosa")],
)
def test_rn02_faixas_de_classificacao(score, esperado):
    assert classify(score) == esperado


# --- RN-03 / RN-04: precedência das listas locais ---

def test_rn03_allowlist_zera_o_score():
    # A URL tem sinais de risco (http + palavra-chave), mas a allowlist tem prioridade absoluta.
    resultado = calculate_risk("http://site-legitimo.com/login", LISTAS)
    assert resultado.score == 0
    assert resultado.classification == "segura"
    assert resultado.reasons == ["dominio_allowlist"]


def test_rn04_blocklist_forca_perigosa():
    resultado = calculate_risk("https://malware.test/home", LISTAS)
    assert resultado.score == 100
    assert resultado.classification == "perigosa"
    assert resultado.reasons == ["dominio_blocklist"]


def test_rn03_allowlist_avaliada_antes_da_blocklist():
    # Interseção por erro de configuração: RN-03 prevalece (nota do SDD §4).
    ambas = DomainLists(allowlist=frozenset({"exemplo.com"}), blocklist=frozenset({"exemplo.com"}))
    assert calculate_risk("https://exemplo.com/home", ambas).reasons == ["dominio_allowlist"]


# --- Agregação de heurísticas (SDD Tabela 4.1) ---

def test_url_sem_sinais_e_segura():
    resultado = analisar("https://site-neutro.com/home")
    assert resultado.score == 0
    assert resultado.classification == "segura"
    assert resultado.reasons == []


def test_http_isolado_soma_dez():
    resultado = analisar("https://site-neutro.com/home")
    assert resultado.score == 0
    resultado = analisar("http://site-neutro.com/home")
    assert resultado.score == 10
    assert resultado.reasons == ["sem_https"]


def test_host_ip_com_http_e_palavra_chave():
    # host_ip 25 + sem_https 10 + palavra-chave 20 = 55
    resultado = analisar("http://192.168.0.1/login")
    assert resultado.score == 55
    assert resultado.classification == "suspeita"


def test_multiplas_heuristicas_elevam_para_perigosa():
    # host_ip 25 + arroba 25 + sem_https 10 + palavra-chave 20 = 80
    resultado = analisar("http://user@192.168.0.1/login")
    assert resultado.score == 80
    assert resultado.classification == "perigosa"


# --- RN-06: palavra-chave sensível exige outro sinal ---

def test_rn06_palavra_chave_isolada_nao_pontua():
    resultado = analisar("https://site-neutro.com/login")
    assert resultado.score == 0
    assert resultado.classification == "segura"
    assert resultado.reasons == []


def test_rn06_palavra_chave_pontua_com_outro_sinal():
    resultado = analisar("http://site-neutro.com/login")
    assert resultado.reasons == ["sem_https", "palavra_chave_sensivel_no_path_query"]
    assert resultado.score == 30  # sem_https 10 + palavra-chave 20


def test_rn06_palavra_chave_nao_pontua_sob_allowlist():
    assert calculate_risk("https://site-legitimo.com/login", LISTAS).reasons == ["dominio_allowlist"]


# --- RN-07 / ordem normativa dos motivos (SDD §4.1) ---

def test_ordem_normativa_dos_motivos():
    resultado = analisar("http://user@192.168.0.1/login")
    assert resultado.reasons == [
        "host_ip",
        "uso_arroba_userinfo",
        "sem_https",
        "palavra_chave_sensivel_no_path_query",
    ]


def test_rn07_sem_motivos_duplicados():
    resultado = analisar("http://user@teste@192.168.0.1/login-verify-secure-account")
    assert len(resultado.reasons) == len(set(resultado.reasons))


# --- RN-01: clamp do score ---

def test_rn01_score_limitado_a_cem():
    # Soma bruta = 25+15+25+25+10+10+20 = 130.
    url = "http://user@a.b.c.d.xn--paypal-fake.top/login-verify-secure-account-confirm-senha-banco"
    resultado = analisar(url)
    assert resultado.score == 100
    assert resultado.classification == "perigosa"


# --- RF-17 / RN-09: entrada inválida não recebe classificação ---

@pytest.mark.parametrize("entrada", ["", "   ", "ftp://exemplo.com", "javascript:alert(1)", "http://", None, 42])
def test_rf17_entrada_invalida_levanta_erro(entrada):
    with pytest.raises(InvalidURLError):
        analisar(entrada)


# --- RNF-02: determinismo ---

def test_rnf02_resultado_deterministico():
    url = "http://user@a.b.c.d.paypal-fake.top/login"
    resultados = {repr(analisar(url)) for _ in range(50)}
    assert len(resultados) == 1


def test_url_da_resposta_e_a_entrada_apos_trim():
    # SDD §5.2: o campo `url` é a entrada original após remoção de espaços externos.
    assert analisar("  https://site-neutro.com/home  ").url == "https://site-neutro.com/home"
