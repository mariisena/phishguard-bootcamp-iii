import pytest
from analyzer.scorer import calculate_risk

def test_scorer_segura_zero_points():
    result = calculate_risk("https://site-legitimo.com/home", "site-legitimo.com", "/home")
    assert result["score"] == 0
    assert result["classification"] == "segura"
    assert result["reasons"] == []

def test_scorer_segura_single_heuristic():
    result = calculate_risk("http://user@site-legitimo.com/home", "site-legitimo.com", "/home")
    assert result["score"] == 25
    assert result["classification"] == "segura"
    assert result["reasons"] == ["uso_arroba_userinfo"]

def test_scorer_suspeita_ip_and_keyword():
    result = calculate_risk("http://192.168.0.1/login", "192.168.0.1", "/login")
    assert result["score"] == 45
    assert result["classification"] == "suspeita"
    assert result["reasons"] == ["host_ip", "palavra_chave_sensivel_no_path_query"]

def test_scorer_perigosa_all_heuristics():
    result = calculate_risk("http://user@192.168.0.1/login", "192.168.0.1", "/login")
    assert result["score"] == 70
    assert result["classification"] == "perigosa"
    assert result["reasons"] == ["host_ip", "uso_arroba_userinfo", "palavra_chave_sensivel_no_path_query"]

def test_scorer_rn06_keyword_ignored_without_other_signals():
    result = calculate_risk("https://site-legitimo.com/login", "site-legitimo.com", "/login")
    assert result["score"] == 0
    assert result["classification"] == "segura"
    assert result["reasons"] == []

def test_scorer_contract_format():
    result = calculate_risk("http://192.168.0.1/login", "192.168.0.1", "/login")
    assert set(result.keys()) == {"score", "classification", "reasons"}
    assert isinstance(result["score"], int)
    assert isinstance(result["classification"], str)
    assert isinstance(result["reasons"], list)