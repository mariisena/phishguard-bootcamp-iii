"""RF-11: host em Punycode ou originalmente informado com caracteres não ASCII.

Critério do SDD §4.2: dispara se o host original tiver qualquer caractere não ASCII **ou** se a
forma canônica IDNA contiver label iniciado por `xn--`.
"""

from analyzer.rules import punycode_homograph
from analyzer.url_normalizer import normalize


def check(url):
    return punycode_homograph.check(normalize(url))


# --- casos positivos ---

def test_host_com_homoglifo_unicode_dispara():
    # "аpple.com" com "а" cirílico (U+0430) — o caso de borda citado no SDD §7.
    resultado = check("https://аpple.com/home")
    assert resultado.triggered is True
    assert resultado.reason == "punycode_ou_unicode_suspeito"


def test_host_ja_em_punycode_dispara():
    assert check("http://xn--pple-43d.com/home").triggered is True


def test_host_idn_legitimo_tambem_dispara():
    # RF-11 sinaliza a forma, não a intenção; um IDN legítimo também é marcado.
    assert check("https://münchen.de/home").triggered is True


def test_punycode_em_subdominio_dispara():
    assert check("https://xn--pple-43d.exemplo.com/home").triggered is True


# --- casos negativos ---

def test_host_ascii_comum_nao_dispara():
    assert check("https://exemplo.com/home").triggered is False


def test_host_com_hifens_nao_dispara():
    assert check("https://meu-site-seguro.com.br/home").triggered is False


# --- casos de borda ---

def test_xn_no_meio_do_label_nao_dispara():
    # O critério exige label *iniciado* por "xn--".
    assert check("https://meuxn--site.com/home").triggered is False


def test_label_iniciado_por_xn_sem_hifens_duplos_nao_dispara():
    assert check("https://xnsite.com/home").triggered is False


def test_caractere_unicode_apenas_no_path_nao_dispara():
    # RF-11 avalia o host; path e query não participam desta heurística.
    assert check("https://exemplo.com/café").triggered is False


def test_host_ip_nao_dispara():
    assert check("http://192.168.0.1/home").triggered is False
