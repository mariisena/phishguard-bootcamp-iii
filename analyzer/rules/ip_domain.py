import ipaddress
from typing import Dict, Union, Optional

def evaluate_ip_domain(domain: str) -> Optional[Dict[str, Union[int, str]]]:
    """
    Verifica se o domínio informado é um endereço IPv4 legítimo.
    
    Atende à regra RN01 (e aos requisitos associados RF-02 / RF-02.1) descrita
    no docs/SDD.md, identificando o uso de endereço IP como host.
    
    Args:
        domain (str): O domínio/host a ser analisado.
        
    Returns:
        dict | None: Payload padronizado se for um IPv4, caso contrário None.
    """
    try:
        # A validação estrita do IPv4Address já descarta strings com portas, 
        # letras, hifens ou octetos fora do intervalo 0-255.
        ipaddress.IPv4Address(domain)
        return {"score": 3, "flag": "O domínio fornecido é um endereço IP"}
    except ValueError:
        return None

