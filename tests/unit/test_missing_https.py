"""RF-12: ausência de HTTPS quando o esquema da URL é http."""

from analyzer.rules import missing_https
from analyzer.url_normalizer import normalize


def check(url):
    return missing_https.check(normalize(url))


# --- caso positivo ---

def test_http_dispara():
    resultado = check("http://exemplo.com/")
    assert resultado.triggered is True
    assert resultado.reason == "sem_https"


# --- caso negativo ---

def test_https_nao_dispara():
    assert check("https://exemplo.com/").triggered is False


# --- casos de borda ---

def test_esquema_em_maiusculas_e_case_insensitive():
    # N-03: o esquema é comparado sem distinção de maiúsculas/minúsculas.
    assert check("HTTP://exemplo.com/").triggered is True
    assert check("HTTPS://exemplo.com/").triggered is False


def test_porta_443_com_http_continua_disparando():
    # A regra olha o esquema, não a porta.
    assert check("http://exemplo.com:443/").triggered is True


def test_https_no_path_nao_evita_disparo():
    assert check("http://exemplo.com/https/login").triggered is True
