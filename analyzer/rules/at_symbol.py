from urllib.parse import urlparse
from typing import Dict, Union, Optional

def evaluate_at_symbol(url: str) -> Optional[Dict[str, Union[int, str]]]:
    try:
        parsed = urlparse(url)
        # A regra de negócio dita que devemos verificar o '@' na autoridade (netloc).
        if '@' in parsed.netloc:
            return {"score": 2, "flag": "O uso de arroba na URL foi detectado"}
    except Exception:
        # Se a URL for malformada e falhar no parser básico, não pontua.
        pass
        
    return None

