# -*- coding: utf-8 -*-
import sys
import pandas as pd

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

df = pd.read_csv('classificacao_comentarios_amostra.csv', encoding='utf-8-sig')

def get_samples(df, estrutura, sent, n=5):
    sub = df[(df['Estrutura'] == estrutura) & (df['Sentimento_Contextual'] == sent)]
    return sub.head(n)[['ID', 'Autor', 'Contexto_Post', 'Comentario', 'Subtema', 'Justificativa']].to_dict(orient='records')

print("=== CONTEÚDO POSITIVO (5) ===")
for r in get_samples(df, 'Comentário com Conteúdo', 'Positivo'):
    print(f"#{r['ID']} [{r['Subtema']}] {r['Comentario']}")

print("\n=== CONTEÚDO NEGATIVO (5) ===")
for r in get_samples(df, 'Comentário com Conteúdo', 'Negativo'):
    print(f"#{r['ID']} [{r['Subtema']}] {r['Comentario']}")

print("\n=== CONTEÚDO NEUTRO (5) ===")
for r in get_samples(df, 'Comentário com Conteúdo', 'Neutro'):
    print(f"#{r['ID']} [{r['Subtema']}] {r['Comentario']}")

print("\n=== EMOJIS POSITIVO (5) ===")
for r in get_samples(df, 'Comentário com Apenas Emojis / Siglas', 'Positivo'):
    print(f"#{r['ID']} [{r['Subtema']}] {r['Comentario']}")

print("\n=== EMOJIS NEGATIVO (5) ===")
for r in get_samples(df, 'Comentário com Apenas Emojis / Siglas', 'Negativo'):
    print(f"#{r['ID']} [{r['Subtema']}] {r['Comentario']}")

print("\n=== EMOJIS NEUTRO (5) ===")
for r in get_samples(df, 'Comentário com Apenas Emojis / Siglas', 'Neutro'):
    print(f"#{r['ID']} [{r['Subtema']}] {r['Comentario']}")
