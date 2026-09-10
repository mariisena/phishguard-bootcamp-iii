import ipaddress
from typing import Dict, Union, Optional

def evaluate_ip_domain(domain: str) -> Optional[Dict[str, Union[int, str]]]:
    try:
        # A validação estrita do IPv4Address já descarta strings com portas, 
        # letras, hifens ou octetos fora do intervalo 0-255.
        ipaddress.IPv4Address(domain)
        return {"score": 3, "flag": "O domínio fornecido é um endereço IP"}
    except ValueError:
        return None

