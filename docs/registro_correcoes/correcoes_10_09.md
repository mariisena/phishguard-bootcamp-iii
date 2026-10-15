> **Registro bruto** (saída do agente na revisão de 10–11/09, mantida sem edição como fonte original).
> A versão organizada, com detecção, impacto, evidência e origem de cada erro, está em [`erros_logicos.md`](erros_logicos.md).

analyzer/scorer.py — reescrito. Correções sobre os achados da revisão:

| Achado	| Correção |
| -----	| ---- |
| 1.1 sintaxe JS no return	| return _result(...) construindo AnalysisResult |
| 1.2 score/reasons antes de existirem	| blocos manuais removidos; inicialização antes do loop |
| 1.5 lists=None → AttributeError	| lists if lists is not None else load_domain_lists() |
| 2.2 reasons de lista	| dominio_allowlist / dominio_blocklist (RN-03/RN-04) |
| 2.5 ordem + dupla contagem	| tupla na ordem normativa do §4.1; suspicious_keywords sai da tupla e é avaliada uma única vez ao final |
| 2.6 RN-06 triplicada e furada	| uma implementação: if keyword_result.triggered and reasons — a palavra-chave não pode mais liberar a si mesma |
| 2.7 clamp antes do bônus	| clamp movido para depois de toda a agregação |
| 2.8 faixas hardcoded	| bloco morto removido; só classify(), derivada de config.THRESHOLDS |
| 3.7 domain redundante	| assinatura agora calculate_risk(url, lists=None) |
| 4. imports mortos/duplicados	| limpos |

Além disso: url agora usa parsed.raw (entrada após trim, conforme §5.2) em vez do argumento cru, e _points_for levanta KeyError com mensagem apontando a Tabela 4.1 quando um motivo não existe em config.POINTS — é o que vai sinalizar o desalinhamento do item 2.1 assim que os códigos forem renomeados.

Também alterei dois pontos fora do arquivo, ambos mecânicos:

config.py:21-23 — adicionei SCORE_MIN/SCORE_MAX. Sem isso o clamp da RN-01 ficaria hardcoded no scorer, exatamente o que o CLAUDE.md proíbe. Nenhum peso ou lista foi tocado.
url_shortener.py:3-5 — phishguard → analyzer (item 1.3). Era typo de pacote; sem isso o scorer nem importa.
Verificação
import analyzer.scorer funciona, e classify() bate nos limites da RN-02 (0/29 segura, 30/59 suspeita, 60/100 perigosa). Validei RN-01, RN-03, RN-04, RN-06, RN-07 e o determinismo (50 execuções idênticas) com stubs para os três módulos que ainda não têm check().

Ressalva importante: os scores desses testes usam os pesos atuais de config.py, que divergem da Tabela 4.1 (item 2.1, pendente do grupo). Validei a mecânica do scorer, não os valores finais

Migração das três heurísticas
Todas agora seguem check(parsed: ParsedURL) -> HeuristicResult, sem parsing próprio e sem except Exception: pass:

Arquivo	Antes	Depois
ip_domain.py	evaluate_ip_domain(str) -> dict|None, só IPv4	check(parsed), IPv4 e IPv6 via is_ip_host (item 3.3)
at_symbol.py	urlparse próprio sobre a URL crua	usa parsed.has_userinfo (itens 3.2, 3.5)
suspicious_keywords.py	urlparse próprio + SENSITIVE_KEYWORDS duplicada	Fusa parsed.path/parsed.query e config.SENSITIVE_KEYWORDS (itens 3.2, 3.4, 3.5)
O score embutido nos dicts ({"score": 3}, {"score": 2}) sumiu — pontuação é do scorer, via config.POINTS.

Códigos de motivo e pesos
Alinhei config.POINTS à Tabela 4.1 — chaves e valores, conforme sua decisão. Seis valores mudaram: host_ip 30→25, encurtador 10→15, impersonação 35→25, punycode 30→25, url_muito_longa 5→10, palavra_chave 10→20. Também renomeei REASON em punycode_homograph.py:6 para punycode_ou_unicode_suspeito, que era o único módulo conforme com código divergente. Isso fecha o item 2.1.

Testes
Reescrevi os quatro arquivos. Cada heurística tem caso positivo, negativo e de borda, como o CLAUDE.md exige.

test_scorer.py passou a cobrir RN-01 a RN-07, RF-17 e RNF-02, com as listas injetadas via DomainLists — sem tocar em disco. Os scores esperados estão escritos como literais derivados da Tabela 4.1 (com a conta no comentário), não lidos de config.POINTS, para que uma alteração indevida de peso quebre a suíte.

Três mudanças de expectativa que valem registro, todas porque os testes antigos exercitavam funções que recebiam string crua:

192.168.0.1:8080 agora dispara RF-05 (antes: None). N-05 diz que a porta não faz parte do host canônico.
@ em path/query/fragmento continua não disparando, agora por via do normalizador em vez de urlparse local.
Os scores subiram, porque sem_https passou a entrar nas contas — os testes antigos só consideravam as três heurísticas então implementadas.
Verificações
Clamp da RN-01: soma bruta 130 → 100.
Determinismo: 50 execuções idênticas.
RN-03 vence RN-04 quando há interseção entre as listas (a nota do §4 do SDD).
Uma lacuna confirmada: o exemplo normativo do §5.2 (http://paypa1-secure.verify-account.top/login) devolve 55, não os 70 documentados. A diferença são exatamente os 15 pontos de tld_suspeito — RF-08 continua sem módulo. Não escrevi um teste para esse exemplo porque ele falharia; ele deve entrar junto com o passo 4.

Não commitei — a branch ainda é main. Restam também .claude/ e docs/registro_correcoes/ não rastreados, que apareceram durante a sessão e não são meus.