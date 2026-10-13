# Ética, segurança e uso de IA no PhishGuard

> Análise crítica do uso de IA generativa (Claude Code, conforme [ADR-0005](../adr/0005-agente-ia-claude-code.md)) no desenvolvimento do PhishGuard.
> Issue de origem: #105 · Parte de #95 · Depende de #99 (lista de erros com origem IA) e #93 (regras em `.claude/rules/`).

## Introdução

O projeto adota Spec-Driven Development (SDD) com um agente de IA que escreve código, testes e documentação sob supervisão do time. Isso aumenta a produtividade, mas desloca o risco: o código passa a ser produzido mais rápido do que é lido. Esta análise examina quatro pilares (alucinação, vazamento de dados, propriedade intelectual e revisão humana) e, para cada um, segue a mesma estrutura: **risco geral → exemplo real no projeto → mitigação adotada → o que ainda falta**.

---

## 1. Alucinação e código inseguro ou destrutivo

### Risco geral

Modelos generativos produzem texto plausível, não texto verificado. Em código, isso se manifesta como dependências inexistentes, sintaxe de outra linguagem, identificadores inventados e tratamento de erros que esconde falhas. Quando o agente também executa comandos no terminal, a alucinação deixa de ser apenas um erro de texto e passa a ter efeito colateral real na máquina.

### Exemplo real no projeto

**Código que parecia correto e não era:**

- Import do pacote inexistente `phishguard` em `url_shortener.py`, em `userinfo_symbol.py` e no `docker-compose.yml`. O nome do próprio projeto foi tratado como se fosse um pacote instalável. O erro só apareceu quando o código foi executado em contexto limpo.
- Sintaxe de JavaScript dentro de um `return` em Python.
- Códigos de motivo inventados (`ip_literal_no_host`, `arroba_na_url`) que não constam no SDD, o que quebra o contrato com a especificação, que é a fonte da verdade.
- `except Exception: pass`, que silencia erros. Num detector de phishing isso é especialmente grave, pois uma falha interna pode virar um resultado aparentemente normal.

**Ações destrutivas:**

- Um comando git mal digitado criou um arquivo literalmente chamado `h --force-with-lease`, resíduo de um argumento que deveria ter sido interpretado como opção.
- Na revisão de 11/10, o agente executou um `taskkill` que encerrou **todos** os processos Python da máquina para derrubar um servidor de teste. O objetivo era legítimo (parar um servidor); o escopo, não. O agente escolheu a ferramenta mais ampla disponível em vez da mais precisa (encerrar apenas o PID do servidor iniciado por ele).

O segundo grupo é o mais instrutivo: um erro de texto é visto na revisão do diff, mas um comando destrutivo já aconteceu quando o humano toma conhecimento.

### Mitigação adotada

- **Testes antes da correção**: o comportamento esperado é fixado antes de alterar o código, o que torna visíveis imports quebrados e códigos de motivo fora do contrato.
- **CI** (pipeline da feature 16) executando a suíte a cada alteração.
- **Revisão em Pull Request** antes do merge.
- **Regras no `CLAUDE.md`**: ordem de precedência (SDD, ADRs, código), proibição de classificar URL inválida como `segura` por padrão, e lista de mudanças que exigem confirmação humana.
- **Regras de segurança em `.claude/rules/seguranca.md`**, previstas na issue #93.

### O que ainda falta

- O arquivo `.claude/rules/seguranca.md` ainda não existe na branch principal. Enquanto a #93 não for concluída, **nada no repositório impede formalmente** comandos como o `taskkill` amplo. A regra precisa ser escrita de forma explícita: proibir encerramento de processos por nome, exigir PID específico, e exigir confirmação para comandos git com `--force`, `reset --hard` e remoções recursivas.
- Falta um teste ou verificação automática que detecte `except Exception: pass` (por exemplo, regra de linter) e imports de módulos que não existem no `requirements.txt` ou no pacote `analyzer`.
- Falta um teste que valide os códigos de motivo emitidos contra a lista fechada do SDD.
- Falta usar a lista de erros com origem IA (#99) como insumo para novas regras, em vez de apenas registro histórico.

---

## 2. Vazamento de dados, privacidade e confidencialidade

### Risco geral

Tudo o que o agente lê pode ser enviado ao provedor do modelo: código-fonte, documentação, saída de terminal e metadados do git (nome e e-mail dos autores). O risco é duplo: o dado sensível pode sair da máquina por meio do contexto, e pode ser persistido no repositório público por meio de um commit.

### Exemplo real no projeto

Os principais vetores identificados no projeto são:

- **`.env`, tokens e credenciais**: arquivos de configuração local e variáveis de ambiente podem ser lidos pelo agente ou aparecer na saída do terminal.
- **Dados pessoais**: RA dos integrantes e e-mails, presentes em metadados do git e em documentos acadêmicos.
- **URLs reais de vítimas em testes**: um projeto de detecção de phishing tem forte tentação de usar URLs reais coletadas de ataques, que podem conter identificadores de pessoas reais no caminho ou na query string.

### Mitigação adotada

- `.env` e `.env.local` estão no `.gitignore` (seção "Variaveis de ambiente"), assim como os logs gerados localmente em `logs/`.
- As listas locais (allowlist e blocklist) e os testes **não contêm dados reais**: os testes usam URLs falsas, construídas para exercitar a heurística sem identificar ninguém.
- Revisão consciente do que é colado no chat com o agente.
- Configurações de privacidade de cada ferramenta (por exemplo, desativar o uso de conversas para treinamento, quando a conta permite).

### O que ainda falta

- O `.gitignore` protege apenas contra commit acidental. Ele **não impede** que o agente **leia** o `.env`. É necessário configurar permissões de leitura do agente (lista de arquivos negados) e registrar isso nas regras de segurança.
- Não há varredura automática de segredos (por exemplo, `gitleaks` ou o secret scanning do GitHub) no CI.
- Não há documentação verificável de quais configurações de privacidade cada integrante realmente ativou. Hoje é uma prática individual, não uma garantia do time.
- O e-mail nos metadados do git é público no histórico e já foi enviado como contexto; isso deveria ser uma decisão consciente de cada integrante (por exemplo, usar o e-mail `noreply` do GitHub).
- Falta uma regra explícita de que dados de teste devem ser sintéticos, com exemplos sob domínios reservados (`example.com`, `.test`, `.invalid`).

---

## 3. Propriedade intelectual e direitos autorais

### Risco geral

Quem é o autor de um código gerado por IA? A resposta depende da jurisdição, dos termos de uso da ferramenta e do grau de contribuição humana, e ainda não é pacífica. Há também o risco de o modelo reproduzir trechos de código sob licença incompatível com a do projeto, sem indicar a origem.

### Exemplo real no projeto

- **O repositório não possui arquivo `LICENSE`** (pendência registrada na issue #101). Sem licença, o padrão legal é "todos os direitos reservados": terceiros não têm permissão de usar, copiar ou modificar o código, mesmo que o repositório seja público. Para um trabalho acadêmico isso pode ser intencional, mas **não foi uma decisão registrada**; foi uma omissão.
- Os commits e PRs de #85 a #89 foram feitos com **`Co-Authored-By`** e marcados como gerados por IA, o que registra no histórico, de forma rastreável, que parte do trabalho veio do agente.

### Mitigação adotada

- Atribuição explícita via `Co-Authored-By` nos commits e marcação de PRs gerados por IA. Isso é transparência: quem lê o histórico sabe o que passou pelo agente.
- O agente trabalha sobre uma especificação escrita pelo time (SDD), então as decisões de projeto e as regras de negócio têm autoria humana.

### O que ainda falta

- **Decidir e adicionar a `LICENSE`.** É uma decisão humana (o `CLAUDE.md` já reserva decisões de peso ao time). Opções comuns: MIT ou Apache-2.0 (permissivas; a Apache-2.0 traz cláusula de patentes) ou GPL-3.0 (copyleft). Deve-se verificar também se a instituição de ensino impõe condições sobre trabalhos de curso.
- Ler e registrar os termos de uso de cada ferramenta de IA utilizada, em especial quem detém os direitos sobre a saída gerada e se há restrições de uso.
- Não há verificação de que trechos gerados não reproduzem código licenciado. Para um projeto deste tamanho o risco é baixo, mas deveria constar como risco aceito e não apenas ignorado.
- A prática de `Co-Authored-By` não está padronizada em regra: ela depende de o agente ou o integrante lembrar. Deve constar no `CLAUDE.md` como obrigatória.
- Registrar nas dependências (`requirements.txt`) as licenças de terceiros, já que `phishguard` mostrou que o agente pode sugerir dependências sem critério.

---

## 4. Homologação e revisão humana no SDD

### Risco geral

O fluxo do projeto é **spec → teste → implementação → revisão → merge**. A revisão humana é a única etapa que não é automatizada, e por isso é a primeira a ser pulada sob pressão de prazo. O risco é o chamado *automation bias*: confiar no que a IA entrega porque ela entrega com confiança, e fechar a tarefa sem verificar.

### Exemplo real no projeto

**Falha:** as issues #56 (remover `checked_at` de `models.py`), #57 (corrigir o `docker-compose.yml`) e #66 (reorganizar a suíte conforme §7.1) foram **fechadas como concluídas sem verificação**. Coincidência ou não, o `docker-compose.yml` é um dos arquivos que continham o import do pacote inexistente `phishguard` (pilar 1). Ou seja, uma issue que existia justamente para corrigir esse tipo de problema foi dada como resolvida sem que alguém conferisse. A revisão humana só funciona se realmente acontecer: um checkbox marcado não é revisão.

**Acerto:** o `CLAUDE.md` reserva a humanos as decisões de peso. Alterar pesos de heurísticas, limiares de classificação, palavras-chave, TLDs ou marcas monitoradas exige confirmação humana e atualização prévia do SDD, e, diante de divergência, o agente deve **apontá-la em vez de decidi-la**. Dois casos concretos:

- **#90**: decidir se encurtador com subdomínio (`www.bit.ly`) deve disparar o RF-09.
- **#91**: registrar no SDD a limitação de falso positivo por inclusão de marca (`capitaurbana.com` → `itau`).

Nos dois casos, o agente expôs o problema e a decisão ficou com o time. É o comportamento desejado.

### Mitigação adotada

- Regras no `CLAUDE.md` que definem o que o agente não pode alterar sem confirmação e que mandam sinalizar divergências entre código, teste e SDD.
- Hierarquia de fontes (SDD, ADRs, código) que dá uma referência objetiva para a revisão.
- Revisão em PR e CI como barreiras anteriores ao merge.

### O que ainda falta

- **Critério de fechamento verificável**: uma issue só fecha com evidência (link para o commit, saída do teste ou diff). Os fechamentos de #56, #57 e #66 deveriam ser reabertos e auditados.
- **Aprovação humana obrigatória em PR** (proteção de branch exigindo ao menos uma revisão de pessoa diferente de quem pediu a mudança ao agente).
- **Distinguir revisão de leitura**: quem revisa precisa executar os testes ou o código, e não apenas ler o diff.
- Registrar, por PR, quem revisou e o que foi conferido.

---

## Conclusão: posição crítica do grupo

Nossa avaliação é que a IA foi **útil e, em vários momentos, perigosa pelo mesmo motivo**: ela é rápida e confiante. Os erros que encontramos (pacote inexistente, códigos de motivo inventados, `taskkill` amplo) não vieram de situações exóticas, e sim de tarefas rotineiras. Três conclusões decorrem disso.

1. **Alucinação não é exceção, é custo operacional.** Qualquer fluxo com IA precisa assumir que parte da saída está errada e ter barreiras mecânicas (testes, CI, linters) que detectem isso sem depender de atenção humana.
2. **As mitigações atuais são majoritariamente reativas e baseadas em disciplina.** `.gitignore`, `CLAUDE.md` e revisão em PR funcionam quando alguém lembra de usá-los. O episódio das issues fechadas sem verificação mostra que disciplina individual falha. O que impediu um dano maior no `taskkill` foi sorte de contexto (máquina de desenvolvimento), não uma regra.
3. **A responsabilidade não é transferível.** Atribuir `Co-Authored-By` à IA é transparência, mas não divide a responsabilidade: o time responde pelo que entrega. Por isso as decisões de peso permanecem humanas, e a falta da `LICENSE` ou a revisão pulada são falhas nossas, não da ferramenta.

**Prioridades recomendadas**, em ordem: (1) concluir #93 com regras proibindo comandos destrutivos amplos e leitura de `.env`; (2) reabrir e auditar #56, #57 e #66, e exigir evidência para fechar issues; (3) decidir e adicionar a `LICENSE` (#101); (4) incluir varredura de segredos e verificação de imports no CI.

## Referências

> A preencher conforme exigência do professor.

- Termos de uso e política de privacidade da ferramenta de IA utilizada (Anthropic / Claude Code): a consultar e registrar a versão e a data de acesso.
- [ADR-0005: Claude Code como agente de IA no fluxo SDD](../adr/0005-agente-ia-claude-code.md)
- [`CLAUDE.md`](../../CLAUDE.md) e [`docs/SDD.md`](../SDD.md)
- Issues do repositório: #56, #57, #66, #90, #91, #93, #95, #99, #101, #105. PRs: #85 a #89.
