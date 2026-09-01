# Especificação Técnica (SDD) — API Detector de URLs Suspeitas/Phishing

## 1. Visão Geral do Problema

A aplicação consiste em uma API backend que recebe uma URL e realiza uma análise estática (baseada em padrões de texto e regras pré-definidas).

O objetivo é determinar se a URL é segura, suspeita ou se apresenta características clássicas de phishing.

A solução foca em validações algorítmicas para garantir alta testabilidade.

## 2. Requisitos Funcionais (RF)

**RF-01:** O sistema deve receber a URL a ser analisada por meio do corpo de uma requisição de entrada.

**RF-02:** O sistema deve decompor a string da URL recebida em suas partes principais (protocolo, domínio, caminho/rota) para análise estrutural.

**RF-02.1:** Caso a URL contenha o símbolo `@`, o domínio real a ser considerado para todas as regras de análise (RN01, RN04, RN05) é a substring **após** o último `@` e antes da primeira `/`, `?` ou `#`. Tudo o que precede o `@` é tratado como informação de "userinfo" e **não** deve ser usado como domínio de referência.
> Exemplo: em `http://google.com@site-falso.com`, o domínio considerado é `site-falso.com`, não `google.com`.

**RF-03:** O sistema deve calcular o score de risco ("Pontuação de Risco") avaliando a URL decomposta contra as regras de negócio pré-definidas.

**RF-04:** O sistema deve classificar a URL analisada em níveis de risco (ex: Segura, Suspeita ou Phishing) com base no score total calculado.

**RF-05:** O sistema deve retornar o resultado da classificação final juntamente com uma lista detalhada contendo todos os motivos (flags/infrações) que justificam a pontuação gerada.

**RF-06:** O sistema deve validar o formato da URL recebida antes de submetê-la à análise. Uma URL é considerada válida quando:
- o campo `url` está presente e não é uma string vazia;
- possui um esquema reconhecido (`http://` ou `https://`);
- possui pelo menos um caractere de domínio após o esquema.

Caso qualquer uma dessas condições não seja atendida, a API deve retornar o erro descrito em 5.3, sem executar a análise de regras.

## 3. Requisitos Não-Funcionais (RNF)

**RNF01:** A aplicação deve ser desenvolvida utilizando Python com FastAPI para facilitar o empacotamento em contêineres Docker e a reprodutibilidade do ambiente.

**RNF02:** O tempo de processamento da análise deve ser inferior a 300ms, por se tratar de processamento em memória e análise de strings.

**RNF03:** Os contratos de comunicação (entrada e saída) devem ser estritamente no formato JSON.

**RNF04:** O código deve ser altamente modular para permitir a implementação fluida do Test Harness, permitindo testes isolados de cada regra de validação.

**RNF05:** O algoritmo deve ser determinístico, a mesma URL terá sempre o mesmo resultado. Para isso, todas as comparações de texto (RN04, RN05) devem ser **case-insensitive** (ex: `LOGIN`, `Login` e `login` devem ser tratados como equivalentes).

## 4. Regras de Negócio (RN)

A classificação da URL será baseada em um sistema de pontuação. Cada anomalia encontrada soma pontos de risco.

**RN01 - Uso de IP no Domínio (+3 pontos):** Se o domínio da URL (conforme RF-02/RF-02.1) for um endereço IPv4 (ex: `http://192.168.0.1/login`), é considerado de altíssimo risco, pois sites legítimos utilizam DNS.

**RN02 - Símbolo '@' na URL (+2 pontos):** O uso de arroba na URL (frequentemente usado para ofuscar o destino real, ex: `http://google.com@site-falso.com`) soma 2 pontos.

**RN03 - Comprimento excessivo (+1 ponto):** Se a URL completa possuir mais de 75 caracteres, recebe pontuação de suspeita (tática comum para esconder subdomínios falsos).

**RN04 - Excesso de Hifens (+1 ponto):** Se o domínio possuir 3 ou mais hifens (ex: `atualizacao-segura-conta-banco.com`).

**RN05 - Palavras-chave Suspeitas (+1 ponto por ocorrência):** A presença de termos comumente usados em engenharia social no domínio ou caminho soma pontos, um para cada ocorrência encontrada. A busca é **case-insensitive** e considera a seguinte lista fechada de termos:

```
login, update, secure, banking, free, admin
```

> Esta lista é a única fonte de verdade para RN05. Novos termos só devem ser adicionados via atualização desta especificação (ver seção 7).

**RN06 — Sistema de Classificação Final:**
- 0 pontos: **Seguro**
- 1 a 2 pontos: **Suspeito**
- 3 pontos ou mais: **Phishing**

## 5. Contratos de Entrada e Saída (API Contracts)

Endpoint Principal: `POST /api/v1/analyze`

### 5.1. Contrato de Entrada (Request)

```json
{
  "url": "http://192.168.1.1/secure-update/login"
}
```

### 5.2. Contrato de Saída - Sucesso (Response 200 OK)

Exemplo para `http://192.168.1.1/secure-update/login`:

- IP no domínio (RN01): +3
- Palavra-chave "secure" (RN05): +1
- Palavra-chave "update" (RN05): +1
- Palavra-chave "login" (RN05): +1
- **Total: 6 pontos → Phishing**

```json
{
  "url": "http://192.168.1.1/secure-update/login",
  "risk_score": 6,
  "risk_level": "Phishing",
  "flags": [
    "O domínio fornecido é um endereço IP",
    "Palavra-chave suspeita encontrada: secure",
    "Palavra-chave suspeita encontrada: update",
    "Palavra-chave suspeita encontrada: login"
  ]
}
```

### 5.3. Contrato de Saída - Erro de Validação (Response 400 Bad Request)

Quando o campo `url` estiver ausente, vazio, ou não atender aos critérios de validade definidos em RF-06, a API deve retornar:

```json
{
  "error": "O campo 'url' é obrigatório e deve conter uma URL válida."
}
```

## 6. Decomposição em Unidades (Arquitetura)

Para suportar o desenvolvimento iterativo e a testabilidade requerida para a entrega, o código não será monolítico. Ele deverá ser dividido em:

- **Controller / Roteador HTTP**: Lida exclusivamente com receber o JSON, validar a existência e o formato do campo `url` (RF-06), e enviar a resposta HTTP.
- **Serviço de Análise (Analyzer)**: Recebe a string da URL, orquestra a chamada de todas as regras e soma a pontuação final.
- **Módulo de Regras (Rules Engine)**: Funções puras e isoladas (ex: `is_ip_domain(url)`, `has_at_symbol(url)`). Isso é essencial para que o membro responsável pela Qualidade e Testes consiga escrever casos de teste cobrindo caminhos felizes e edge cases em frações de segundos.

## 7. Histórico de Revisões

| Versão | Data | Alteração | Motivo |
|--------|------|-----------|--------|
| v1.0 | — | Versão inicial da especificação | Primeira definição do problema, RF/RNF/RN e contratos |
| v1.1 | — |  | |
| v1.1 | — |  | |
| v1.1 | — |  | |
| v1.1 | — |  | |