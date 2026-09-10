import pytest
from analyzer.rules.ip_domain import evaluate_ip_domain

def test_evaluate_ip_domain_valid_ipv4():
    """Cenário normal: deve retornar o payload para um IPv4 válido."""
    expected = {"score": 3, "flag": "O domínio fornecido é um endereço IP"}
    assert evaluate_ip_domain("192.168.0.1") == expected

def test_evaluate_ip_domain_common_domain():
    """Cenário normal: domínios comuns devem retornar None."""
    assert evaluate_ip_domain("google.com") is None

def test_evaluate_ip_domain_invalid_ip_large_octet():
    """Edge case: IPs com octetos > 255 devem retornar None."""
    assert evaluate_ip_domain("256.100.50.25") is None

def test_evaluate_ip_domain_numbers_not_ip():
    """Edge case: domínio contendo números que imita IP deve retornar None."""
    assert evaluate_ip_domain("123site.com") is None

def test_evaluate_ip_domain_with_port():
    """Edge case: domínio (ou IP) que inclui porta não deve ser reconhecido como IP estrito."""
    assert evaluate_ip_domain("192.168.0.1:80") is None
    assert evaluate_ip_domain("google.com:443") is None

def test_evaluate_ip_domain_with_hyphens():
    """Edge case: domínio com hifens (mesmo parecendo IP) deve retornar None."""
    assert evaluate_ip_domain("192-168-0-1.com") is None
    assert evaluate_ip_domain("meu-site-seguro.com") is None

