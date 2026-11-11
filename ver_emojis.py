# -*- coding: utf-8 -*-
import sys
import pandas as pd

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

df = pd.read_csv('classificacao_comentarios_amostra.csv', encoding='utf-8-sig')
emojis = df[df['Estrutura'] == 'Comentário com Apenas Emojis / Siglas']

print('=== EMOJIS NEGATIVOS ===')
for idx, r in emojis[emojis['Sentimento_Contextual'] == 'Negativo'].iterrows():
    print(f"#{r['ID']}: '{r['Comentario']}' ({r['Subtema']})")

print('\n=== EMOJIS NEUTROS (sem nan) ===')
neutros = emojis[(emojis['Sentimento_Contextual'] == 'Neutro') & (emojis['Comentario'].notna()) & (emojis['Comentario'] != 'nan')]
for idx, r in neutros.iterrows():
    print(f"#{r['ID']}: '{r['Comentario']}' ({r['Subtema']})")

print('\n=== EMOJIS POSITIVOS ===')
positivos = emojis[(emojis['Sentimento_Contextual'] == 'Positivo') & (emojis['Comentario'].notna())]
for idx, r in positivos.head(10).iterrows():
    print(f"#{r['ID']}: '{r['Comentario']}' ({r['Subtema']})")
