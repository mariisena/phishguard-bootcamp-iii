import time
from analyzer.scorer import calculate_risk

def test_performance_rnf01_analysis_under_300ms():
    
    # Conjunto representativo de URLs:
    urls_teste = [
        # URL perfeitamente segura e na allowlist (Early return na checagem de listas)
        "https://google.com/",
        
        # URL comum, neutra
        "https://exemplo-comum.com.br/contato",
        
        # URL intermediária (algumas heurísticas: http, keyword)
        "http://exemplo-intermediario.com/login",
        
        # Pior caso estrutural projetado: 
        # HTTP, @ no userinfo, subdomínios excessivos, impersonação (paypa1 -> paypal, leet),
        # TLD suspeito (.top), muito longa (>75 chars) e múltiplas keywords suspeitas no path.
        "http://usuario@a.b.c.d.e.paypa1-suporte-urgente.top/login/update/secure/account/banco/verify?q=senha",
    ]
    
    # Aquecimento (Warm-up): carrega listas (LRU cache) e módulos para não penalizar o timer.
    for url in urls_teste:
        calculate_risk(url)
        
    iteracoes = 500
    total_analises = iteracoes * len(urls_teste)
    
    start_time = time.perf_counter()
    
    for _ in range(iteracoes):
        for url in urls_teste:
            calculate_risk(url)
            
    end_time = time.perf_counter()
    
    tempo_total_segundos = end_time - start_time
    media_por_url_ms = (tempo_total_segundos / total_analises) * 1000.0
    
    # O requisito RNF-01 exige < 300 ms.
    assert media_por_url_ms < 300.0, (
        f"Violação do RNF-01: A análise demorou em média {media_por_url_ms:.2f} ms "
        f"por URL, o que excede o limite de 300 ms."
    )