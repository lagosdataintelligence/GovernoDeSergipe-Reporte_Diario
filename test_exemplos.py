# -*- coding: utf-8 -*-
import sys
import pandas as pd

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

df = pd.read_csv('classificacao_comentarios_amostra.csv', encoding='utf-8-sig')

# Specific IDs selected for maximum diversity and analytical clarity:
# 1. Conteudo Positivo (5)
ids_cont_pos = [11, 17, 21, 25, 36]
# 2. Conteudo Negativo (5)
ids_cont_neg = [4, 5, 24, 32, 10]
# 3. Conteudo Neutro (5)
ids_cont_neu = [6, 18, 34, 42, 62]
# 4. Emojis Positivo (5)
ids_emj_pos = [2, 3, 7, 12, 35]
# 5. Emojis Negativo (5)
ids_emj_neg = [13, 52, 131, 276, 288]
# 6. Emojis Neutro (5)
ids_emj_neu = [16, 121, 182, 229, 290]

all_ids = ids_cont_pos + ids_cont_neg + ids_cont_neu + ids_emj_pos + ids_emj_neg + ids_emj_neu
print("Total IDs:", len(all_ids))

sub_df = df[df['ID'].isin(all_ids)].copy()
print("Found in df:", len(sub_df))

for seg, ids in [
    ("Conteúdo Positivo", ids_cont_pos),
    ("Conteúdo Negativo", ids_cont_neg),
    ("Conteúdo Neutro", ids_cont_neu),
    ("Emojis Positivo", ids_emj_pos),
    ("Emojis Negativo", ids_emj_neg),
    ("Emojis Neutro", ids_emj_neu),
]:
    print(f"\n--- {seg} (5) ---")
    for i in ids:
        row = df[df['ID'] == i].iloc[0]
        print(f"#{row['ID']} [{row['Sentimento_Contextual']}] {row['Comentario'][:60]} | {row['Subtema']}")
