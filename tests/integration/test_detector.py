from analyzer.scorer import calculate_risk

def test_e2e_url_claramente_segura_via_allowlist():
    url = "https://google.com/search?q=teste"
    resultado = calculate_risk(url)
    
    assert resultado.score == 0
    assert resultado.classification == "segura"
    assert resultado.reasons == ["dominio_allowlist"]


def test_e2e_url_intermediaria_classificada_como_suspeita():
    url = "http://meu-dominio-qualquer.com/login"
    resultado = calculate_risk(url)
    
    assert resultado.score == 30
    assert resultado.classification == "suspeita"
    assert "sem_https" in resultado.reasons
    assert "palavra_chave_sensivel_no_path_query" in resultado.reasons


def test_e2e_url_claramente_perigosa_via_blocklist():
    url = "https://phishing-banco-teste.com/home"
    resultado = calculate_risk(url)
    
    assert resultado.score == 100
    assert resultado.classification == "perigosa"
    assert resultado.reasons == ["dominio_blocklist"]