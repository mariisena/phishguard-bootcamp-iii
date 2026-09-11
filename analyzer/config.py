"""Constantes de negócio do PhishGuard.

Mantidas centralizadas (RNF-04 / regra "sem valores mágicos espalhados") para que qualquer
ajuste de regra de negócio seja feito em um único lugar e refletido nos testes.
"""

# Pontuação de cada heurística (chave = código do motivo retornado pela heurística).
# Chaves, valores e ordem seguem a Tabela 4.1 do SDD, que é a fonte normativa.
POINTS = {
    "host_ip": 25,
    "uso_arroba_userinfo": 25,
    "subdominios_excessivos": 15,
    "tld_suspeito": 15,
    "encurtador_conhecido_destino_nao_verificado": 15,
    "possivel_impersonacao_marca": 25,
    "punycode_ou_unicode_suspeito": 25,
    "sem_https": 10,
    "url_muito_longa": 10,
    "palavra_chave_sensivel_no_path_query": 20,
}

# RN-01: intervalo válido do score final (clamp aplicado ao fim da agregação).
SCORE_MIN = 0
SCORE_MAX = 100

# RN-02: limiares de classificação — score < LOW = segura, < HIGH = suspeita, >= HIGH = perigosa.
THRESHOLDS = (30, 60)

SUSPICIOUS_TLDS = {
    "zip", "top", "xyz", "country", "click", "link", "work", "gq", "tk", "ml", "cf", "mom", "fit",
}

URL_SHORTENERS = {
    "bit.ly", "tinyurl.com", "t.co", "is.gd", "goo.gl", "ow.ly", "buff.ly", "cutt.ly", "rebrand.ly",
}

# Marcas monitoradas para detecção de possível typosquatting/impersonação (RF-10 / RN-05).
# Cada marca aponta para o conjunto de domínios considerados oficiais.
MONITORED_BRANDS = {
    "paypal": {"paypal.com"},
    "google": {"google.com"},
    "microsoft": {"microsoft.com", "live.com", "office.com"},
    "apple": {"apple.com"},
    "itau": {"itau.com.br"},
    "caixa": {"caixa.gov.br"},
    "bradesco": {"bradesco.com.br"},
    "nubank": {"nubank.com.br"},
    "amazon": {"amazon.com", "amazon.com.br"},
}

SENSITIVE_KEYWORDS = {
    "login", "verify", "secure", "update", "confirm", "account", "senha", "banco", "wp-login",
}

MAX_URL_LENGTH = 75          # RF-13
MAX_SUBDOMAIN_LEVELS = 3     # RF-07
MAX_INPUT_LENGTH = 2048      # RF-04 / limite de validação de entrada
