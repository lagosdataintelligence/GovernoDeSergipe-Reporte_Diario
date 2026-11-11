# -*- coding: utf-8 -*-
import re

with open('relatorio_secom_apresentacao.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Check brandwatch
bw_matches = list(re.finditer(r'brandwatch', text, re.I))
print(f"Total 'brandwatch' occurrences: {len(bw_matches)}")

# Check palver outside src/href URLs
no_urls = re.sub(r'(?:href|src)=["\'][^"\']*["\']', '', text)
palver_visible = list(re.finditer(r'palver', no_urls, re.I))
print(f"Visible 'palver' occurrences outside URLs: {len(palver_visible)}")
for m in palver_visible:
    start = max(0, m.start() - 50)
    end = min(len(no_urls), m.end() + 50)
    print(f"  Snippet: {no_urls[start:end]}")

# Check "crítica" / "críticas"
critica_matches = list(re.finditer(r'cr[íi]tica[s]?', text, re.I))
print(f"Total 'crítica(s)' occurrences: {len(critica_matches)}")
for m in critica_matches[:10]:
    start = max(0, m.start() - 50)
    end = min(len(text), m.end() + 50)
    print(f"  Snippet: {text[start:end].strip()}")

print("\n--- Key Requirement Checks ---")
reqs = {
    "Radar Diário de Reputação": "Radar Diário de Reputação" in text,
    "1.008 manifestações": "1.008" in text,
    "Redes Sociais": "Redes Sociais" in text,
    "Notícias": "Notícias" in text,
    "Positivo, Negativo e Neutro no balanço": "Positivo" in text and "Negativo" in text and "Neutro" in text,
    "Amostra representativa": "amostra representativa" in text.lower(),
    "Janela Diária 17h": "17h" in text,
    "Aracaju": "Aracaju" in text,
    "Itabaiana": "Itabaiana" in text,
    "Lagarto": "Lagarto" in text,
    "Estância": "Estância" in text,
    "Ausência de Metodologia: IRG": "Metodologia: IRG" not in text,
    "Ausência de Atualização Operacional": "Atualização Operacional" not in text,
    "Ausência de '100% dos dados coletados'": "100% dos dados coletados" not in text,
    "Ausência de 'secao-secretarias'": "secao-secretarias" not in text,
    "Ausência de 'skill lagos 2.0 calibrada'": "skill lagos 2.0 calibrada" not in text.lower(),
    "Ausência de 'Casos de Calibração Especial'": "Casos de Calibração Especial" not in text,
    "Ausência de 'Críticas' como rótulo de KPI": "KPI Críticas" not in text and "Críticas (" not in text,
}

for req, ok in reqs.items():
    print(f"[{'OK' if ok else 'FAIL'}] {req}")
