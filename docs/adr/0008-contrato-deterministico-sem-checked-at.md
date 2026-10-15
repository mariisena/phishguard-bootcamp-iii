# ADR-0008: Contrato de resposta determinístico, sem o campo `checked_at`

**Status:** Aceita
**Data:** 2026-09-08 (removido do contrato no SDD v1.1); implementada em 2026-10-11 (PR #86);
registrada como ADR em 2026-10-12

## Contexto

O RNF-02 exige que a mesma URL, com a mesma versão de código, configuração e listas, produza
exatamente o mesmo `url`, `normalized_host`, `score`, `classification` e `reasons`, inclusive na
ordem dos motivos. Esse requisito é o que permite um Test Harness confiável: um teste pode comparar
o corpo inteiro da resposta.

A primeira versão do contrato previa um campo `checked_at` com o horário da análise. Útil para
auditoria, ele muda a cada requisição, então duas respostas para a mesma URL nunca seriam iguais.

O SDD retirou o campo do contrato em 2026-09-08, mas `analyzer/models.py` e `analyzer/api.py`
continuaram a devolvê-lo. A issue #56 foi fechada como concluída sem a correção, e a divergência só
foi encontrada na revisão de 11/10 (#84).

## Decisão

A resposta de `POST /api/v1/analyze` contém **somente** os campos do SDD §5.2:
`url`, `normalized_host`, `score`, `classification` e `reasons`. Nenhum campo gerado no momento da
requisição (timestamp, UUID, tempo de processamento) faz parte do resultado analítico.

Se for preciso observar quando uma análise ocorreu, isso deve ser tratado como metadado separado e
explicitamente excluído das comparações de igualdade, conforme a nota do SDD §5.2.

O teste `test_same_request_returns_identical_body` em `tests/test_api.py` garante a regra: duas
requisições iguais devolvem corpos idênticos.

## Alternativas Consideradas

### Manter `checked_at` e ignorá-lo nos testes

Os testes comparariam o corpo sem esse campo. Funciona, mas a resposta oficial deixaria de ser
determinística, e cada teste novo precisaria lembrar de excluir o campo. Um esquecimento geraria
testes instáveis.

### Enviar o horário em cabeçalho HTTP

O cabeçalho `Date` já é enviado pelo servidor e fica fora do corpo JSON. Não foi necessário criar
cabeçalho próprio, porque nenhum requisito pede o horário da análise.

### Registrar o horário em log do servidor

Adequado para auditoria futura, sem afetar o contrato. Não foi implementado porque o serviço não
tem requisito de log de análises (ADR-0003: nada é persistido).

## Consequências

### Positivas

* O RNF-02 vale para a resposta HTTP inteira, não só para o núcleo do scorer.
* Testes de contrato podem usar igualdade direta de dicionários.
* O contrato fica menor e igual ao documentado no SDD.

### Negativas / Trade-offs

* A resposta não informa quando a análise foi feita. Um cliente que precise disso deve registrar o
  horário do seu lado ou usar o cabeçalho `Date`.
* Sem identificador de requisição, correlacionar uma resposta com logs de servidor fica mais difícil.
* Remover um campo é mudança incompatível para quem já o consumia. Como o serviço ainda não tem
  clientes externos, o impacto foi nulo nesta versão.

## Lição de processo

A decisão estava correta no SDD desde 2026-09-08, mas o código levou mais de um mês para segui-la
porque a issue foi fechada sem verificação. Desde então, issue só fecha com evidência (commit, PR
ou saída de teste), e o teste de contrato exige o conjunto exato de campos.

## Evolução da decisão

Adicionar metadados não determinísticos no futuro exige: atualizar o SDD §5.2 primeiro, separar
esses campos do resultado analítico (por exemplo, num objeto `meta`) e ajustar os testes para
compará-los separadamente.
