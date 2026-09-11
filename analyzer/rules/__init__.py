"""Cada módulo deste pacote implementa exatamente uma heurística (uma regra de negócio).

Contrato comum: `check(parsed: ParsedURL) -> HeuristicResult`, sem efeitos colaterais nem I/O
(RNF-03). Ver docs/SSD.md §6.
"""