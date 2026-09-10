import pytest
from analyzer.rules.suspicious_keywords import evaluate_suspicious_keywords

def test_evaluate_suspicious_keywords_found_in_path():
    expected = {"score": 20, "flag": "palavra_chave_sensivel_no_path_query"}
    assert evaluate_suspicious_keywords("https://exemplo.com/secure/login.php") == expected

def test_evaluate_suspicious_keywords_found_in_query():
    expected = {"score": 20, "flag": "palavra_chave_sensivel_no_path_query"}
    assert evaluate_suspicious_keywords("https://exemplo.com/index.php?action=verify") == expected

def test_evaluate_suspicious_keywords_not_found():
    assert evaluate_suspicious_keywords("https://exemplo.com/sobre-nos") is None

def test_evaluate_suspicious_keywords_multiple_occurrences():
    expected = {"score": 20, "flag": "palavra_chave_sensivel_no_path_query"}
    assert evaluate_suspicious_keywords("https://exemplo.com/update?action=login") == expected

def test_evaluate_suspicious_keywords_case_insensitive():
    expected = {"score": 20, "flag": "palavra_chave_sensivel_no_path_query"}
    assert evaluate_suspicious_keywords("https://exemplo.com/UpDaTe/LoGiN") == expected

def test_evaluate_suspicious_keywords_domain_ignored():
    # A palavra 'banco' está no domínio, mas o path e a query estão limpos
    assert evaluate_suspicious_keywords("https://meu-banco-seguro.com/home") is None

def test_evaluate_suspicious_keywords_substring():
    expected = {"score": 20, "flag": "palavra_chave_sensivel_no_path_query"}
    assert evaluate_suspicious_keywords("https://exemplo.com/portal-login-novo/") == expected

