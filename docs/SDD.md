# Especificação Técnica (SDD) — API Detector de URLs Suspeitas/Phishing

## 1. Visão Geral do Problema

A aplicação consiste em uma API backend que recebe uma URL e realiza uma análise estática (baseada em padrões de texto e regras pré-definidas).

O objetivo é determinar se a URL é segura, suspeita ou se apresenta características clássicas de phishing.

A solução é intencionalmente livre de integrações complexas ou bancos de dados, focando estritamente em validações algorítmicas para garantir alta testabilidade.

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