from urllib.parse import urlparse
from typing import Dict, Union, Optional

# Lista normativa de palavras-chave sensíveis (SDD.md, Seção 4.2)
SENSITIVE_KEYWORDS = {
    "login", "verify", "secure", "update", 
    "confirm", "account", "senha", "banco", "wp-login"
}

def evaluate_suspicious_keywords(url: str) -> Optional[Dict[str, Union[int, str]]]:
    try:
        parsed = urlparse(url)
        # RF-14 determina busca restrita ao path e query
        target_text = f"{parsed.path} {parsed.query}".lower()
        
        for keyword in SENSITIVE_KEYWORDS:
            if keyword in target_text:
                return {
                    "score": 20,
                    "flag": "palavra_chave_sensivel_no_path_query"
                }
    except Exception:
        pass
        
    return None