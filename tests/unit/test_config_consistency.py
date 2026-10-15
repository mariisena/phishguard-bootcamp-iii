import re
from pathlib import Path
from analyzer import config

def test_sdd_consistency_tlds():
    """Garante que os TLDs no SDD correspondam exatamente ao config.py."""
    content = Path("docs/SDD.md").read_text(encoding="utf-8")
    
    match = re.search(r'\*\*TLDs suspeitos\*\*: (.*)', content)
    assert match is not None, "Lista de TLDs não encontrada no SDD."
    
    sdd_tlds = {t.strip().strip('`.') for t in match.group(1).split(',')}
    assert sdd_tlds == config.SUSPICIOUS_TLDS, "Divergência entre TLDs do SDD e do config.py"

def test_sdd_consistency_shorteners():
    """Garante que os Encurtadores no SDD correspondam exatamente ao config.py."""
    content = Path("docs/SDD.md").read_text(encoding="utf-8")
    
    match = re.search(r'\*\*Encurtadores conhecidos\*\*: (.*)', content)
    assert match is not None, "Lista de encurtadores não encontrada no SDD."
    
    sdd_shorteners = {t.strip().strip('`') for t in match.group(1).split(',')}
    assert sdd_shorteners == config.URL_SHORTENERS, "Divergência entre Encurtadores do SDD e do config.py"

def test_sdd_consistency_brands():
    """Garante que a tabela de marcas monitoradas no SDD corresponda ao config.py."""
    content = Path("docs/SDD.md").read_text(encoding="utf-8")
    
    table_start = content.find('| Marca monitorada | Domínio oficial |')
    assert table_start != -1, "Tabela de marcas não encontrada no SDD."
    
    table_end = content.find('\n\n', table_start)
    if table_end == -1:
        table_end = len(content)
    
    table_lines = content[table_start:table_end].strip().split('\n')
    
    sdd_brands = {}
    for line in table_lines[2:]:  # Pula o header e o separador Markdown
        parts = [p.strip() for p in line.split('|') if p.strip()]
        if len(parts) >= 2:
            brand = parts[0]
            domains = {d.strip() for d in parts[1].split(',')}
            sdd_brands[brand] = domains
            
    assert sdd_brands == config.MONITORED_BRANDS, "Divergência entre Marcas do SDD e do config.py"

