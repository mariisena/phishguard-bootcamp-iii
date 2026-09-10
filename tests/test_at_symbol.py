import pytest
from analyzer.rules.at_symbol import evaluate_at_symbol

def test_evaluate_at_symbol_detected():
    expected = {"score": 2, "flag": "O uso de arroba na URL foi detectado"}
    assert evaluate_at_symbol("http://google.com@site-falso.com") == expected

def test_evaluate_at_symbol_not_detected():
    assert evaluate_at_symbol("https://site-legitimo.com/login") is None

def test_evaluate_at_symbol_multiple_at():
    expected = {"score": 2, "flag": "O uso de arroba na URL foi detectado"}
    assert evaluate_at_symbol("http://teste@google.com@site-falso.com/login") == expected

def test_evaluate_at_symbol_in_query_parameters():
    assert evaluate_at_symbol("https://site-legitimo.com/login?email=user@email.com") is None

def test_evaluate_at_symbol_in_fragment():
    assert evaluate_at_symbol("https://site-legitimo.com/index.html#contact@email.com") is None

def test_evaluate_at_symbol_in_path():
    assert evaluate_at_symbol("https://site-legitimo.com/profile/@username") is None

