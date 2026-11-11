# -*- coding: utf-8 -*-
import sys
import pandas as pd

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

df = pd.read_csv('classificacao_comentarios_amostra.csv', encoding='utf-8-sig')
conteudo = df[df['Estrutura'] == 'Comentário com Conteúdo']

print('=== CONTEÚDO NEGATIVO ===')
for idx, r in conteudo[conteudo['Sentimento_Contextual'] == 'Negativo'].head(12).iterrows():
    print(f"#{r['ID']} [{r['Subtema']}]: {r['Comentario']}")

print('\n=== CONTEÚDO POSITIVO ===')
for idx, r in conteudo[conteudo['Sentimento_Contextual'] == 'Positivo'].head(12).iterrows():
    print(f"#{r['ID']} [{r['Subtema']}]: {r['Comentario']}")

print('\n=== CONTEÚDO NEUTRO ===')
for idx, r in conteudo[conteudo['Sentimento_Contextual'] == 'Neutro'].head(12).iterrows():
    print(f"#{r['ID']} [{r['Subtema']}]: {r['Comentario']}")
