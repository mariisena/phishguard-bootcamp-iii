"""Normalização e validação de URLs — regras N-01 a N-09 do SDD §5.4."""

import pytest

from analyzer import config
from analyzer.url_normalizer import InvalidURLError, is_ip_host, normalize


# --- N-01: tipo da entrada e trim ---

@pytest.mark.parametrize("entrada", [None, 42, b"http://exemplo.com", ["http://exemplo.com"]])
def test_n01_entrada_nao_string_e_invalida(entrada):
    with pytest.raises(InvalidURLError):
        normalize(entrada)


def test_n01_espacos_externos_sao_removidos():
    parsed = normalize("   https://exemplo.com/home   ")
    assert parsed.raw == "https://exemplo.com/home"


# --- N-02: comprimento ---

@pytest.mark.parametrize("entrada", ["", "   ", "\t\n"])
def test_n02_entrada_vazia_e_invalida(entrada):
    with pytest.raises(InvalidURLError):
        normalize(entrada)


def test_n02_entrada_acima_do_limite_e_invalida():
    url = "https://exemplo.com/" + "a" * config.MAX_INPUT_LENGTH
    with pytest.raises(InvalidURLError):
        normalize(url)


def test_n02_entrada_no_limite_e_valida():
    sufixo = "a" * (config.MAX_INPUT_LENGTH - len("https://exemplo.com/"))
    parsed = normalize("https://exemplo.com/" + sufixo)
    assert len(parsed.raw) == config.MAX_INPUT_LENGTH


# --- N-03: esquema obrigatório, http ou https ---

def test_n03_url_sem_esquema_e_invalida():
    # SDD §7 lista "www.exemplo.com" como caso de borda; N-03 e RF-04 exigem URL absoluta.
    with pytest.raises(InvalidURLError):
        normalize("www.exemplo.com")


def test_n03_host_nu_sem_esquema_e_invalido():
    with pytest.raises(InvalidURLError):
        normalize("exemplo.com/login")


@pytest.mark.parametrize("url", ["ftp://exemplo.com", "javascript:alert(1)", "mailto:a@b.com", "data:text/html,x"])
def test_n03_esquemas_nao_suportados_sao_invalidos(url):
    with pytest.raises(InvalidURLError):
        normalize(url)


@pytest.mark.parametrize("url", ["HTTP://exemplo.com/", "HtTpS://exemplo.com/"])
def test_n03_esquema_e_case_insensitive(url):
    assert normalize(url).scheme in ("http", "https")


# --- N-04: host obrigatório ---

@pytest.mark.parametrize("url", ["http://", "https:///caminho"])
def test_n04_host_ausente_e_invalido(url):
    with pytest.raises(InvalidURLError):
        normalize(url)


# --- N-05: host canônico ---

def test_n05_host_em_minusculas():
    assert normalize("https://EXEMPLO.COM/home").host == "exemplo.com"


def test_n05_ponto_final_absoluto_removido():
    assert normalize("https://exemplo.com./home").host == "exemplo.com"


def test_n05_porta_nao_faz_parte_do_host():
    assert normalize("https://exemplo.com:8443/home").host == "exemplo.com"


def test_n05_pontos_finais_repetidos_sao_invalidos():
    # Remover apenas um ponto deixa um label vazio, que é host malformado.
    with pytest.raises(InvalidURLError):
        normalize("https://exemplo.com../home")


def test_n05_label_vazio_no_meio_e_invalido():
    with pytest.raises(InvalidURLError):
        normalize("https://exemplo..com/home")


def test_porta_invalida_e_rejeitada():
    with pytest.raises(InvalidURLError):
        normalize("https://exemplo.com:99999/home")


def test_host_com_espaco_e_invalido():
    with pytest.raises(InvalidURLError):
        normalize("https://exe mplo.com/home")


# --- N-06: IDNA ---

def test_n06_host_unicode_convertido_para_idna():
    # "аpple.com" com "а" cirílico (U+0430).
    parsed = normalize("https://аpple.com/home")
    assert parsed.host == "xn--pple-43d.com"


def test_n06_host_original_preservado_para_rf11():
    parsed = normalize("https://аpple.com/home")
    assert parsed.host_original == "аpple.com"
    assert not parsed.host_original.isascii()


def test_n06_host_ascii_permanece_inalterado():
    parsed = normalize("https://exemplo.com/home")
    assert parsed.host == parsed.host_original == "exemplo.com"


def test_n06_host_ja_em_punycode_e_preservado():
    parsed = normalize("https://xn--pple-43d.com/home")
    assert parsed.host == "xn--pple-43d.com"


def test_n06_label_ascii_longo_nao_e_rejeitado_pelo_codec():
    # O codec `idna` recusa labels ASCII com mais de 63 caracteres; a especificação não manda
    # invalidar esse caso, então hosts ASCII não passam pelo codec.
    host = "a" * 70
    assert normalize(f"https://{host}.com/home").host == f"{host}.com"


# --- N-08: path, query e fragmento ---

def test_n08_path_e_query_preservados():
    parsed = normalize("https://exemplo.com/Conta/Login?Acao=Verify")
    assert parsed.path == "/Conta/Login"
    assert parsed.query == "Acao=Verify"


def test_n08_visao_em_minusculas_disponivel():
    parsed = normalize("https://exemplo.com/Conta/Login?Acao=Verify")
    assert parsed.path_lower == "/conta/login"
    assert parsed.query_lower == "acao=verify"


def test_n08_fragmento_nao_entra_em_path_nem_query():
    parsed = normalize("https://exemplo.com/home#login")
    assert parsed.path == "/home"
    assert parsed.query == ""


# --- N-09: userinfo ---

def test_n09_userinfo_nao_invalida_a_url():
    parsed = normalize("http://usuario:senha@exemplo.com/home")
    assert parsed.host == "exemplo.com"
    assert parsed.has_userinfo is True


def test_n09_arroba_no_path_nao_marca_userinfo():
    assert normalize("https://exemplo.com/perfil/@usuario").has_userinfo is False


# --- is_ip_host (RF-05) ---

@pytest.mark.parametrize("host", ["192.168.0.1", "8.8.8.8", "::1", "2001:db8::1"])
def test_is_ip_host_reconhece_ipv4_e_ipv6(host):
    assert is_ip_host(host) is True


@pytest.mark.parametrize("host", ["exemplo.com", "256.100.50.25", "192-168-0-1.com", ""])
def test_is_ip_host_rejeita_nao_ips(host):
    assert is_ip_host(host) is False


def test_host_ipv6_perde_os_colchetes():
    assert normalize("http://[2001:db8::1]/home").host == "2001:db8::1"
