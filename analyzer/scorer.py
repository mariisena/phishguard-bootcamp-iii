from analyzer.rules.ip_domain import evaluate_ip_domain
from analyzer.rules.at_symbol import evaluate_at_symbol
from analyzer.rules.suspicious_keywords import evaluate_suspicious_keywords

def calculate_risk(url: str, domain: str, path: str = "") -> dict:
    score = 0
    reasons = []
    
    # 1. IP como host (Tabela 4.1: 25 pontos, reason: 'host_ip')
    # heurísticas isoladas apenas como triggers booleanos (is not None)
    if evaluate_ip_domain(domain) is not None:
        score += 25
        reasons.append("host_ip")
        
    # 2. Uso de arroba (Tabela 4.1: 25 pontos, reason: 'uso_arroba_userinfo')
    if evaluate_at_symbol(url) is not None:
        score += 25
        reasons.append("uso_arroba_userinfo")
        
    # 3. Palavras-chave sensíveis (Tabela 4.1: 20 pontos, reason: 'palavra_chave_sensivel_no_path_query')
    # Aplicação estrita da RN-06: A heurística só soma pontos se outra heurística tiver disparado (score > 0).
    if evaluate_suspicious_keywords(url) is not None and score > 0:
        score += 20
        reasons.append("palavra_chave_sensivel_no_path_query")
        
    # RN-01: Pontuação limitada ao intervalo [0, 100]
    score = min(score, 100)
    
    # RN-02: Classificação por faixa
    if score <= 29:
        classification = "segura"
    elif score <= 59:
        classification = "suspeita"
    else:
        classification = "perigosa"
        
    return {
        "score": score,
        "classification": classification,
        "reasons": reasons
    }