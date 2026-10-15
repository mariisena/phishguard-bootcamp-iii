---
paths:
  - "tests/**/*.py"
  - "pytest.ini"
  - "scripts/run_harness.sh"
---

# Regras de testes (`tests/`)

Complementa as seções "Escrever os testes antes ou junto da implementação" e "Testes" do
`CLAUDE.md`, e o §7 do `docs/SDD.md`.

## O que todo teste de regra precisa ter

- Pelo menos um caso **positivo** (dispara), um **negativo** (não dispara) e um **de borda**, com
  comentários `# --- casos positivos ---`, `# --- casos negativos ---`, `# --- casos de borda ---`
  como nos arquivos existentes.
- A docstring do módulo cita o requisito/regra (`RF-08`, `RN-06`...) e a seção do SDD.
- Monte a entrada pelo caminho real: `check(normalize(url))`. Não construa `ParsedURL` à mão,
  para que o teste também pegue regressões do normalizador.

## Valores esperados vêm do SDD, não do código

- Escreva o teste a partir do texto do SDD. Se o código atual der outro resultado, isso é uma
  **divergência a reportar**, não um valor a copiar para o `assert`.
- Scores esperados são **literais** derivados da Tabela 4.1, com a conta no comentário:
  `assert r.score == 70  # 15 tld + 25 marca + 10 http + 20 palavra`.
  Não use `config.POINTS[...]` no lado esperado: se um peso mudar por engano, a suíte precisa quebrar.
- Códigos de motivo também são literais (`"tld_suspeito"`), e a ordem de `reasons` é verificada
  com igualdade de lista, não com `in` ou `set`.

## Determinismo

- Sem rede, DNS, relógio (`datetime.now`, `time.time` como valor esperado), aleatoriedade ou
  dependência da ordem de execução entre testes.
- Listas de domínios no scorer: injete `DomainLists` no teste em vez de ler `data/*.json`, salvo
  no teste que valida justamente o carregamento dos arquivos.
- O único teste que mede tempo é o de desempenho (RNF-01); ele verifica um limite, não um valor exato.

## Dados de teste

- URLs sintéticas. Prefira domínios reservados (`example.com`, `.test`, `.invalid`) ou nomes
  claramente fictícios. Nunca use URL real de campanha de phishing com identificadores de pessoas.

## O que não fazer

- Não apague, pule (`skip`/`xfail`) ou afrouxe um teste existente para a suíte passar. Se o teste
  parecer errado, aponte a divergência com o SDD e espere a decisão humana.
- Não dê a tarefa por concluída sem rodar a suíte completa (`./scripts/run_harness.sh` ou
  `docker compose run --rm test`) e mostrar o resultado.
