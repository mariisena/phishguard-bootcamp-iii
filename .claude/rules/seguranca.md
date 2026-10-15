# Regras de segurança para o agente

Esta regra não tem `paths`, então é carregada em **toda** sessão. Complementa as seções
"Branches e Pull Requests", "Ausência de dependências externas" e "O que o agente NÃO deve fazer
sem confirmação humana" do `CLAUDE.md`. A motivação de cada item está em
`docs/relatorio_ia/etica_seguranca.md` (issue #105).

## Git

- Nunca faça commit, merge ou push na `main`. Antes de commitar, confira a branch atual com
  `git branch --show-current`. Trabalho novo sai de `develop` em `feature/*`, `fix/*` ou `docs/*`.
- Peça confirmação explícita antes de: `git push --force` (inclusive `--force-with-lease`),
  `git reset --hard`, `git clean`, `git checkout -- <arquivo>`/`git restore` sobre alterações não
  commitadas, `git branch -D`, rebase de branch já publicada e exclusão de tag.
- Não use `--no-verify` nem desative assinatura de commit.
- Ao montar comandos git, confira as aspas e a ordem dos argumentos. Um comando mal digitado já
  criou neste repositório um arquivo chamado `h --force-with-lease`.
- Commits e PRs feitos com ajuda do agente levam `Co-Authored-By` e o aviso de que exigem revisão
  humana antes do merge.

## Comandos destrutivos e processos

- Não apague arquivos ou pastas fora do que a tarefa pede. Remoção recursiva (`rm -rf`,
  `Remove-Item -Recurse`) exige confirmação.
- Para parar um processo, use o **PID** do processo que você iniciou. É proibido encerrar
  processos por nome ou em massa (`taskkill /IM python.exe`, `pkill python`, `killall`): na
  revisão de 11/10 isso derrubou todos os processos Python da máquina.
- Servidores de teste (`uvicorn`, `docker compose up`) iniciados pelo agente devem ser encerrados
  pelo próprio agente ao final, pelo PID ou por `docker compose down`.

## Segredos e dados pessoais

- Não leia, imprima nem copie para o contexto `.env`, `.env.*`, chaves, tokens ou arquivos de
  credenciais. Se a tarefa parecer exigir isso, pare e pergunte.
- Não exponha dados pessoais (RA, e-mail, telefone) em código, testes, logs ou descrições de PR.
- Não cole saída de terminal com tokens ou variáveis de ambiente em issues e PRs.

## Rede e dependências

- Nenhuma chamada de rede no código da aplicação ou nos testes (ADR-0002). Não adicione
  `requests`, `httpx`, consulta DNS ou API de reputação.
- Não instale pacotes nem altere `requirements.txt`, `Dockerfile` ou `.github/workflows/` sem
  pedido explícito.

## Decisões de produto

- Pesos, limiares, listas (TLDs, encurtadores, marcas, palavras-chave), precedência
  allowlist/blocklist, contrato HTTP e regras de normalização só mudam com decisão humana
  registrada e com o SDD atualizado antes.
- Issue só é dada como concluída com evidência verificável (commit, PR ou saída de teste).
  Não feche issue sem que a correção esteja de fato na branch.

## Limite destas regras

Estas regras são contexto, não bloqueio técnico: o agente pode deixar de segui-las. Para os itens
mais críticos (`.env`, push na `main`, comandos destrutivos), a proteção real está na proteção de
branch do GitHub (#94) e pode ser reforçada com regras `deny` em `.claude/settings.json` ou com um
hook `PreToolUse`.
