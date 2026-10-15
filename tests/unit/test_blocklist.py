"""RF-15 / RN-03 / RN-04 / N-07: listas locais de domínios."""

import json

import pytest

from analyzer.blocklist import (
    DEFAULT_DATA_DIR,
    DomainLists,
    InvalidDomainListError,
    canonical_for_lookup,
    is_allowed,
    is_blocked,
    load_domain_lists,
)

LISTAS = DomainLists(
    allowlist=frozenset({"exemplo.com"}),
    blocklist=frozenset({"malware.test"}),
)


# --- N-07: forma canônica usada na consulta ---

def test_prefixo_www_removido_na_consulta():
    assert canonical_for_lookup("www.exemplo.com") == "exemplo.com"


def test_host_normalizado_para_minusculas_e_sem_ponto_final():
    assert canonical_for_lookup("WWW.Exemplo.COM.") == "exemplo.com"


def test_www_removido_apenas_do_inicio():
    assert canonical_for_lookup("loja.www.exemplo.com") == "loja.www.exemplo.com"


def test_apenas_um_prefixo_www_removido():
    assert canonical_for_lookup("www.www.exemplo.com") == "www.exemplo.com"


# --- RF-15: correspondência exata ---

def test_host_exato_corresponde():
    assert is_allowed("exemplo.com", LISTAS) is True
    assert is_blocked("malware.test", LISTAS) is True


def test_host_fora_da_lista_nao_corresponde():
    assert is_allowed("outro.com", LISTAS) is False
    assert is_blocked("outro.com", LISTAS) is False


def test_subdominio_nao_corresponde_ao_item_da_lista():
    # RF-15 exige correspondência exata: um subdomínio não herda o status do domínio-base.
    assert is_allowed("login.exemplo.com", LISTAS) is False
    assert is_blocked("payload.malware.test", LISTAS) is False


def test_sufixo_parcial_nao_corresponde():
    assert is_allowed("naoexemplo.com", LISTAS) is False


def test_host_com_www_corresponde_a_item_sem_www():
    assert is_allowed("www.exemplo.com", LISTAS) is True


def test_host_sem_www_corresponde_a_item_com_www():
    listas = DomainLists(allowlist=frozenset({"exemplo.com"}), blocklist=frozenset())
    assert is_allowed("exemplo.com", listas) is True


# --- carregamento dos arquivos locais ---

def _escrever(tmp_path, allow, block):
    (tmp_path / "allowlist.json").write_text(json.dumps(allow), encoding="utf-8")
    (tmp_path / "blocklist.json").write_text(json.dumps(block), encoding="utf-8")
    load_domain_lists.cache_clear()
    return load_domain_lists(tmp_path)


def test_carrega_e_canonicaliza_os_itens(tmp_path):
    listas = _escrever(tmp_path, ["WWW.Exemplo.COM", "Outro.NET."], ["Malware.TEST"])
    assert listas.allowlist == frozenset({"exemplo.com", "outro.net"})
    assert listas.blocklist == frozenset({"malware.test"})


def test_arquivos_ausentes_geram_listas_vazias(tmp_path):
    load_domain_lists.cache_clear()
    listas = load_domain_lists(tmp_path)
    assert listas.allowlist == frozenset()
    assert listas.blocklist == frozenset()


def test_json_malformado_levanta_erro(tmp_path):
    (tmp_path / "allowlist.json").write_text("{isso nao e json", encoding="utf-8")
    load_domain_lists.cache_clear()
    with pytest.raises(InvalidDomainListError):
        load_domain_lists(tmp_path)


def test_json_que_nao_e_array_levanta_erro(tmp_path):
    (tmp_path / "allowlist.json").write_text('{"exemplo.com": true}', encoding="utf-8")
    load_domain_lists.cache_clear()
    with pytest.raises(InvalidDomainListError):
        load_domain_lists(tmp_path)


def test_item_nao_string_levanta_erro(tmp_path):
    (tmp_path / "allowlist.json").write_text('["exemplo.com", 42]', encoding="utf-8")
    load_domain_lists.cache_clear()
    with pytest.raises(InvalidDomainListError):
        load_domain_lists(tmp_path)


def test_listas_sao_lidas_uma_unica_vez_por_processo(tmp_path):
    # ADR-0003: as listas são configuração imutável durante a execução.
    listas_1 = _escrever(tmp_path, ["exemplo.com"], [])
    (tmp_path / "allowlist.json").write_text('["outro.com"]', encoding="utf-8")
    listas_2 = load_domain_lists(tmp_path)
    assert listas_1 is listas_2
    assert listas_2.allowlist == frozenset({"exemplo.com"})


# --- consistência da configuração versionada (nota do SDD §4) ---

def test_listas_versionadas_carregam_sem_erro():
    load_domain_lists.cache_clear()
    listas = load_domain_lists(DEFAULT_DATA_DIR)
    assert isinstance(listas.allowlist, frozenset)
    assert isinstance(listas.blocklist, frozenset)


def test_allowlist_e_blocklist_nao_se_interceptam():
    load_domain_lists.cache_clear()
    listas = load_domain_lists(DEFAULT_DATA_DIR)
    intersecao = listas.allowlist & listas.blocklist
    assert intersecao == frozenset(), f"domínios em ambas as listas: {sorted(intersecao)}"


def test_diretorio_de_dados_fica_dentro_do_repositorio():
    # O caminho padrão já apontou para fora do repositório; este teste trava a regressão.
    assert DEFAULT_DATA_DIR.name == "data"
    assert (DEFAULT_DATA_DIR.parent / "analyzer").is_dir()
