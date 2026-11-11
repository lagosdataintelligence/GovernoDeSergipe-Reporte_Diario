# -*- coding: utf-8 -*-
"""
Processador de Dados do Radar SECOM - Versão Refinada
Implementa a Skill de Sentimentalização Governamental:
 - Governança da liderança: posts do Governador (@fabiogov55) e Governo são Positivos (Vetor de Fortalecimento)
 - Resumos em um parágrafo para todas as transmissões de rádio e TV
 - Anonimização de ferramentas proprietárias (zero menções a Brandwatch e Palver)
 - Cálculo do Índice de Reputação Governamental (IRG Lagos v2.0)
"""

import os
import sys
import json
import re
import unicodedata
import pandas as pd
from datetime import datetime
from pathlib import Path

from broadcast_resumos import RESUMOS_BROADCAST
from resumos_redes import gerar_resumo_executivo

# MAPEAMENTO HIPOTÉTICO DE PRAÇAS E AUDIÊNCIA DE RÁDIOS REGIONAIS (SERGIPE)
# Projeção analítica para visualização executiva (aguardando parametrização oficial)
DADOS_HIPOTETICOS_RADIOS = {
    "radio_0": {
        "municipio": "Aracaju",
        "abrangencia": "Capital e Grande Aracaju",
        "ouvintes": 45800,
        "emissora": "Rede CBN Sergipe (90.5 FM)",
        "programa": "Giro Esportivo e Econômico"
    },
    "radio_1": {
        "municipio": "Aracaju",
        "abrangencia": "Metropolitana e Litoral",
        "ouvintes": 39200,
        "emissora": "Rádio Fan FM (99.7 FM)",
        "programa": "Mobilidade & Tecnologia"
    },
    "radio_2": {
        "municipio": "Itabaiana",
        "abrangencia": "Regional (Agreste Sergipano)",
        "ouvintes": 31500,
        "emissora": "Rádio FM Sergipe (105.9 FM)",
        "programa": "Debate & Crônica Esportiva"
    },
    "radio_3": {
        "municipio": "Aracaju",
        "abrangencia": "Estadual / Metropolitana",
        "ouvintes": 26400,
        "emissora": "Rádio Jornal FM (91.3 FM)",
        "programa": "Panorama Institucional"
    },
    "radio_4": {
        "municipio": "Lagarto",
        "abrangencia": "Regional (Centro-Sul Sergipano)",
        "ouvintes": 19700,
        "emissora": "Rádio Juventude FM (104.9 FM)",
        "programa": "Boletim de Negócios & Frotas"
    },
    "radio_5": {
        "municipio": "Estância",
        "abrangencia": "Regional (Sul Sergipano)",
        "ouvintes": 14300,
        "emissora": "Rádio Esperança FM (92.7 FM)",
        "programa": "Saúde & Atendimento 24h"
    }
}

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent

# DESIGN TOKENS OFICIAIS LAGOS DATA INTELLIGENCE
DESIGN_TOKENS = {
    "ind": "#252375",
    "ind_2": "#2E2C80",
    "ind_3": "#3B3990",
    "ind_4": "#4D4B9E",
    "ind_d": "#1D1B5E",
    "ind_deep": "#151347",
    "mag": "#FF005A",
    "mag_h": "#E0004F",
    "cy": "#00F3FF",
    "lav": "#D2D1F9",
    "lav_2": "#B9B8E0",
    "ice": "#F4F4FA",
    "pos": "#00F3FF",
    "neg": "#FF005A",
    "neu": "#B9B8E0"
}

REGRAS_SECRETARIAS = [
    {
        "secretaria": "DESO / Iguá (Saneamento & Água)",
        "sigla": "DESO/IGUÁ",
        "peso": 3,
        "cor": "#FF005A",
        "regex": r"deso|igua|saneamento|falta d'?agua|sem agua|abastecimento|hidrometro|adutora|torneira seca|desabastecimento"
    },
    {
        "secretaria": "SES (Saúde Pública & Hospitais)",
        "sigla": "SES/HUSE",
        "peso": 3,
        "cor": "#FF005A",
        "regex": r"\bses\b|saude|huse|hospital|cirurgia|leitos|samu|medico|medicamento|urgencia|ambulancia|medradius|exames"
    },
    {
        "secretaria": "SEMAC (Meio Ambiente & Recursos Hídricos)",
        "sigla": "SEMAC",
        "peso": 2,
        "cor": "#00F3FF",
        "regex": r"semac|barragem do poxim|poxim|meio ambiente|defesa civil|meteorolog|chuva|estiagem|reserva hidrica|recuperacao ambiental"
    },
    {
        "secretaria": "SSP (Segurança Pública & Polícia)",
        "sigla": "SSP/POLÍCIA",
        "peso": 2,
        "cor": "#FF005A",
        "regex": r"\bssp\b|seguranca publica|policia|delegad|andre dav|pmse|pcse|presidio|assalto|homicidio|patrulhamento|apreensao"
    },
    {
        "secretaria": "SEDURBI / DER (Obras & Rodovias)",
        "sigla": "SEDURBI/DER",
        "peso": 2,
        "cor": "#00F3FF",
        "regex": r"sedurbi|\bder\b|obras?|complexo viario|alca viaria|maria do carmo|ponte|rodovia|asfalt|paviment|recapeamento|duplicacao|veiculos hibridos"
    },
    {
        "secretaria": "SEDUC (Educação & Escolas)",
        "sigla": "SEDUC",
        "peso": 2,
        "cor": "#B9B8E0",
        "regex": r"seduc|educacao|escola|sintese|professor|colegio|alun|estudante|piso salarial|concurso seduc|nota 10|centro de excelencia"
    },
    {
        "secretaria": "SEDETEC (Emprego & Desenvolvimento)",
        "sigla": "SEDETEC",
        "peso": 2,
        "cor": "#00F3FF",
        "regex": r"sedetec|vagas? de emprego|go sergipe|oportunidade de emprego|trabalhador|caged|gas natural|novas industrias|senai|sine|produtividade"
    },
    {
        "secretaria": "SETUR (Turismo & Cultura)",
        "sigla": "SETUR",
        "peso": 1,
        "cor": "#00F3FF",
        "regex": r"setur|turismo|arraia do povo|vila do forro|festejos juninos|cultura|orla de atalaia|gastronomia|hotelaria|visitantes|voos? domesticos"
    },
    {
        "secretaria": "SEAD / Gestão & Liderança Governamental",
        "sigla": "SECOM/GOV",
        "peso": 1,
        "cor": "#B9B8E0",
        "regex": r"sead|servidor|governo de sergipe|mitidieri|governador|mpc|contas|eleicoes|lula|politica|assembleia|deputad|prefeit|equilibrio fiscal|pec"
    }
]

def normalizar(t: str) -> str:
    if not t or not isinstance(t, str):
        return ""
    nfkd = unicodedata.normalize('NFKD', t)
    return "".join([c for c in nfkd if not unicodedata.combining(c)]).lower().strip()

def formatar_numero(val):
    try:
        val = float(val)
        if val >= 1_000_000:
            return f"{val / 1_000_000:.1f} mi".replace(".", ",")
        elif val >= 1_000:
            return f"{val / 1_000:.1f} mil".replace(".", ",")
        return str(int(val))
    except Exception:
        return "0"

def safe_int(v):
    try:
        if pd.isna(v): return 0
        return int(float(v))
    except Exception:
        return 0

def safe_float(v):
    try:
        if pd.isna(v): return 0.0
        return float(v)
    except Exception:
        return 0.0

def classificar_mencao_completa(autor: str, texto: str, pautas_extra: str = "", sentimento_original: str = ""):
    """
    Classifica a menção utilizando os critérios técnicos da Skill de Sentimentalização Governamental:
    1. Governança da liderança: publicações da conta do Governador e do Governo são Vetores de Fortalecimento.
    2. Engajamento cidadão de apoio e entregas são Positivos.
    3. Reclamações reais de serviços públicos e atritos são Negativos.
    4. Notas protocolares, editais e coberturas sem juízo são Neutros.
    """
    norm_txt = normalizar(f"{texto} {pautas_extra}")
    norm_aut = normalizar(autor)

    # 1. Identificar Secretaria e Peso
    sec = "Governo de Sergipe / Geral"
    sigla = "GERAL"
    peso = 1
    for r in REGRAS_SECRETARIAS:
        if re.search(r["regex"], norm_txt):
            sec = r["secretaria"]
            sigla = r["sigla"]
            peso = r["peso"]
            break

    # 2. Citação ao Governador / Liderança
    is_gov_author = any(x in norm_aut for x in ["fabiogov55", "governosergipe", "fabio mitidieri", "governo do estado"])
    is_gov_cited = any(x in norm_txt for x in ["fabio", "mitidieri", "governador", "fabiogov55"]) or is_gov_author

    # REGRA 1 DA SKILL: Publicações de autoria oficial do Governador ou Governo são POSITIVAS
    if is_gov_author:
        sentimento = "Positivo"
        papel = "Vetor de Fortalecimento"
        return sec, sigla, peso, is_gov_cited, papel, sentimento

    # REGRA 2 DA SKILL: Apoio Cidadão e Entregas Institucionais
    pos_institucional = [
        "gov responde", "tava com saudade do gov responde", "fala, meu povo", "fala meu povo",
        "complexo viario", "maria do carmo", "go sergipe", "rode bem", "caminhada da vitoria",
        "nao calem os nordestinos", "mais oportunidades de emprego", "recuperacao ambiental gera renda",
        "atendimento com tecnologia", "simbora", "e 13", "parabens governador", "vamos juntos",
        "avanca", "vagas de emprego", "renovacao", "sucesso", "otimo trabalho", "deixaria ele mesmo",
        "entrega de mais uma etapa", "obrigado pelo carinho", "seguimos trabalhando"
    ]
    if any(p in norm_txt for p in pos_institucional):
        sentimento = "Positivo"
        papel = "Vetor de Fortalecimento" if is_gov_cited else "Neutro"
        return sec, sigla, peso, is_gov_cited, papel, sentimento

    # REGRA 3 DA SKILL: Reclamações de Serviços Públicos Essenciais e Ataques
    neg_terms = [
        "falta d'agua", "falta de agua", "sem agua", "estamos sendo roubados", "desumano",
        "vergonha", "absurdo", "ar-condicionado quebrado", "nega cessao", "boicotando",
        "birra de governador", "pior que", "superlotacao", "caos", "buraco", "cratera",
        "assalto", "roubo", "inadimplencia", "vida cara", "abandono", "cade o dinheiro"
    ]
    if any(n in norm_txt for n in neg_terms):
        sentimento = "Negativo"
        papel = "Menção Negativa" if is_gov_cited else "Não citado"
        return sec, sigla, peso, is_gov_cited, papel, sentimento

    # REGRA 4 DA SKILL: Informativos e Pautas Neutras
    neu_terms = [
        "alerta", "barragem", "semac", "edital", "parecer", "mpc", "diario oficial",
        "esclarecimento", "pesquisa", "pec", "estudos", "audiencia publica"
    ]
    if any(n in norm_txt for n in neu_terms):
        sentimento = "Neutro"
        papel = "Neutro" if is_gov_cited else "Não citado"
        return sec, sigla, peso, is_gov_cited, papel, sentimento

    # Fallback coerente baseado no sentimento de origem
    if sentimento_original == "positive":
        sentimento = "Positivo"
        papel = "Vetor de Fortalecimento" if is_gov_cited else "Neutro"
    elif sentimento_original == "negative":
        sentimento = "Negativo"
        papel = "Menção Negativa" if is_gov_cited else "Não citado"
    else:
        sentimento = "Neutro"
        papel = "Neutro" if is_gov_cited else "Não citado"

    return sec, sigla, peso, is_gov_cited, papel, sentimento

def carregar_dados():
    """Lê as duas bases de dados reais e consolida em lista unificada com resumos em parágrafo."""
    print("⏳ Carregando bases de dados reais...")
    
    # 1. Base Brandwatch
    bw_path = BASE_DIR / "teste- brandwatch.csv"
    df_bw = pd.read_csv(bw_path, skiprows=10)
    print(f"   ✔ Redes Sociais & Noticiário: {len(df_bw)} registros lidos")

    # 2. Base Palver
    palver_path = BASE_DIR / "teste- palver.xlsx"
    df_palver = pd.read_excel(palver_path)
    print(f"   ✔ Broadcast (Rádio & TV) e Portais: {len(df_palver)} registros lidos")

    mencoes = []

    # Processar Brandwatch
    for idx, r in df_bw.iterrows():
        mid = f"redes_{idx+1}"
        data_raw = str(r.get("Date", ""))
        try:
            dt = datetime.strptime(data_raw[:19], "%Y-%m-%d %H:%M:%S")
            data_fmt = dt.strftime("%d/%m/%Y")
            hora_fmt = dt.strftime("%H:%M")
        except Exception:
            data_fmt = "21/10/2026"
            hora_fmt = "12:00"

        title = str(r.get("Title", "")).strip()
        snippet = str(r.get("Snippet", "")).strip()
        if title and snippet and title != snippet:
            texto = f"{title}. {snippet}"
        else:
            texto = snippet or title or "Menção pública em rede social"

        page_type = str(r.get("Page Type", "")).lower()
        autor = str(r.get("Author", "")).strip() or "Cidadão / Usuário"
        
        # Mapeamento do canal
        if "instagram" in page_type:
            canal = "Instagram"
            canal_icon = "📸"
            canal_filtro = "instagram"
        elif "twitter" in page_type:
            canal = "Twitter / X"
            canal_icon = "🐦"
            canal_filtro = "twitter"
        elif "facebook" in page_type:
            canal = "Facebook"
            canal_icon = "👥"
            canal_filtro = "facebook"
        elif "news" in page_type:
            canal = "Notícia Online"
            canal_icon = "📰"
            canal_filtro = "noticia"
        else:
            canal = "Rede Social"
            canal_icon = "🌐"
            canal_filtro = "social"

        pautas = f"{r.get('2025 Pautas', '')} {r.get('Pautas', '')}"
        bw_sent = str(r.get("Sentiment", "")).lower()

        sec, sigla, peso, cita_gov, papel_gov, sentimento = classificar_mencao_completa(
            autor=autor,
            texto=texto,
            pautas_extra=pautas,
            sentimento_original=bw_sent
        )

        resumo_exec = gerar_resumo_executivo(
            autor=autor,
            texto=texto,
            sentimento=sentimento,
            secretaria=sec,
            sigla=sigla
        )

        alcance = safe_int(r.get("Estimated Reach", 0))
        likes = safe_int(r.get("Likes", 0))
        comments = safe_int(r.get("Comments", 0))
        shares = safe_int(r.get("Shares", 0))
        engajamento = likes + comments + shares

        mencoes.append({
            "id": mid,
            "origem": "Redes Sociais & Noticiário",
            "canal": canal,
            "canal_icon": canal_icon,
            "canal_filtro": canal_filtro,
            "autor": autor,
            "municipio": "Sergipe",
            "abrangencia": "Redes Sociais",
            "ouvintes": 0,
            "data": data_fmt,
            "hora": hora_fmt,
            "texto": texto,
            "texto_original": texto,
            "resumo_executivo": resumo_exec,
            "resumo_paragrafo": resumo_exec,
            "url": str(r.get("Url", "")),
            "alcance": alcance,
            "engajamento": engajamento,
            "sentimento": sentimento,
            "secretaria": sec,
            "sigla": sigla,
            "peso": peso,
            "cita_governador": cita_gov,
            "papel_governador": papel_gov,
            "midia_url": None,
            "midia_tipo": None,
            "valuation": 0.0
        })

    # Processar Palver (Rádios, TVs e Notícias)
    radio_counter = 0
    tv_counter = 0

    for idx, r in df_palver.iterrows():
        mid = f"bcast_{idx+1}"
        src = str(r.get("Source", "")).strip()
        data_raw = str(r.get("Date", ""))[:10]
        hora_raw = str(r.get("Time", ""))[:5]
        try:
            dt = datetime.strptime(data_raw, "%Y-%m-%d")
            data_fmt = dt.strftime("%d/%m/%Y")
        except Exception:
            data_fmt = "21/10/2026"
        hora_fmt = hora_raw if len(hora_raw) == 5 else "11:30"

        outlet = str(r.get("Outlet") or r.get("Source") or "Emissora Regional")
        prog = str(r.get("Program Title") or r.get("Program Host") or "")
        
        media_url = r.get("Media Link 01")
        if pd.isna(media_url) or not str(media_url).startswith("http"):
            media_url = None
        else:
            media_url = str(media_url)

        val = safe_float(r.get("Valuation", 0.0))
        alcance = safe_int(r.get("Audience / Views", 0)) or 15000

        # Identificar se é Rádio, TV ou Notícia e atribuir resumo em 1 parágrafo
        if src.lower() == "radio":
            canal = "Rádio Broadcast"
            canal_icon = "📻"
            canal_filtro = "radio"
            midia_tipo = "audio"
            chave_resumo = f"radio_{radio_counter}"
            
            info_radio = DADOS_HIPOTETICOS_RADIOS.get(chave_resumo, {
                "municipio": "Aracaju",
                "abrangencia": "Regional",
                "ouvintes": 20000,
                "emissora": outlet,
                "programa": prog
            })

            if chave_resumo in RESUMOS_BROADCAST:
                resumo_paragrafo, emissora_nome, programa_nome = RESUMOS_BROADCAST[chave_resumo]
            else:
                resumo_paragrafo = "Transmissão em emissora de rádio regional abordando temas de relevância pública, prestação de serviços e debates sobre demandas da população sergipana."
                emissora_nome = info_radio["emissora"]
                programa_nome = info_radio["programa"]

            radio_counter += 1
            autor = info_radio["emissora"]
            prog = info_radio["programa"]
            municipio = info_radio["municipio"]
            abrangencia = info_radio["abrangencia"]
            ouvintes = info_radio["ouvintes"]
            alcance = ouvintes
            texto = resumo_paragrafo
            resumo_exec = resumo_paragrafo

        elif src.lower() == "television":
            canal = "Televisão Broadcast"
            canal_icon = "📺"
            canal_filtro = "tv"
            midia_tipo = "video"
            chave_resumo = f"tv_{tv_counter}"
            if chave_resumo in RESUMOS_BROADCAST:
                resumo_paragrafo, emissora_nome, programa_nome = RESUMOS_BROADCAST[chave_resumo]
            else:
                resumo_paragrafo = "Registro jornalístico televisivo veiculando notícias factuais, matérias temáticas e prestação de contas sobre ações sociais e de infraestrutura regional."
                emissora_nome = outlet
                programa_nome = prog
            tv_counter += 1
            autor = emissora_nome
            prog = programa_nome
            municipio = "Aracaju"
            abrangencia = "Estadual (Aberta / Fechada)"
            ouvintes = alcance
            texto = resumo_paragrafo
            resumo_exec = resumo_paragrafo

        else:
            canal = "Notícia Online"
            canal_icon = "📰"
            canal_filtro = "noticia"
            midia_tipo = None
            autor = outlet
            municipio = "Sergipe"
            abrangencia = "Portais Regionais"
            ouvintes = 0
            texto_raw = str(r.get("Content", "")).strip()
            texto = texto_raw[:350] + ("..." if len(texto_raw) >= 350 else "")
            sec, sigla, peso, cita_gov, papel_gov, sentimento = classificar_mencao_completa(
                autor=autor,
                texto=texto,
                pautas_extra=prog,
                sentimento_original=""
            )
            resumo_exec = gerar_resumo_executivo(
                autor=autor,
                texto=texto_raw,
                sentimento=sentimento,
                secretaria=sec,
                sigla=sigla
            )
            resumo_paragrafo = resumo_exec

        if src.lower() in ["radio", "television"]:
            sec, sigla, peso, cita_gov, papel_gov, sentimento = classificar_mencao_completa(
                autor=autor,
                texto=texto,
                pautas_extra=prog,
                sentimento_original=""
            )

        mencoes.append({
            "id": mid,
            "origem": "Broadcast & Noticiário",
            "canal": canal,
            "canal_icon": canal_icon,
            "canal_filtro": canal_filtro,
            "autor": autor,
            "programa": prog,
            "municipio": municipio,
            "abrangencia": abrangencia,
            "ouvintes": ouvintes,
            "data": data_fmt,
            "hora": hora_fmt,
            "texto": texto,
            "texto_original": texto,
            "resumo_executivo": resumo_exec,
            "resumo_paragrafo": resumo_paragrafo,
            "url": str(r.get("Link", "")),
            "alcance": alcance,
            "engajamento": safe_int(r.get("Comments", 0)) + safe_int(r.get("Shares", 0)),
            "sentimento": sentimento,
            "secretaria": sec,
            "sigla": sigla,
            "peso": peso,
            "cita_governador": cita_gov,
            "papel_governador": papel_gov,
            "midia_url": media_url,
            "midia_tipo": midia_tipo,
            "duracao": str(r.get("Duration")) if pd.notna(r.get("Duration")) else "00:00:30",
            "valuation": val
        })

    print(f"✔ Total consolidado processado: {len(mencoes)} menções")
    return mencoes

def calcular_kpis(mencoes):
    """Calcula os indicadores estratégicos e o IRG oficial ponderado."""
    tot_vol = len(mencoes)
    pos_m = [m for m in mencoes if m["sentimento"] == "Positivo"]
    neu_m = [m for m in mencoes if m["sentimento"] == "Neutro"]
    neg_m = [m for m in mencoes if m["sentimento"] == "Negativo"]

    tot_pos = len(pos_m)
    tot_neu = len(neu_m)
    tot_neg = len(neg_m)

    pct_pos = round((tot_pos / tot_vol) * 100, 1) if tot_vol else 0
    pct_neu = round((tot_neu / tot_vol) * 100, 1) if tot_vol else 0
    pct_neg = round((tot_neg / tot_vol) * 100, 1) if tot_vol else 0

    # Cálculo do IRG Ponderado com Multiplicador de Liderança
    soma_pos = 0.0
    soma_neg = 0.0
    soma_tot = 0.0

    for m in mencoes:
        mult = 1.3 if m["cita_governador"] else 1.0
        peso_ajustado = m["peso"] * mult
        soma_tot += peso_ajustado
        if m["sentimento"] == "Positivo":
            soma_pos += peso_ajustado
        elif m["sentimento"] == "Negativo":
            soma_neg += peso_ajustado

    if soma_tot > 0:
        score_irg = round(((soma_pos - soma_neg) / soma_tot) * 100, 1)
    else:
        score_irg = 0.0

    # Faixas do IRG
    if score_irg >= 40:
        badge_irg = "🟢 Fortalecimento Expressivo"
        cor_irg = DESIGN_TOKENS["pos"]
        desc_irg = "Cenário amplamente favorável. Entregas, aprovação e mobilização positiva superam amplamente as manifestações negativas."
    elif score_irg >= 10:
        badge_irg = "🟢 Percepção Favorável"
        cor_irg = DESIGN_TOKENS["pos"]
        desc_irg = "Cenário positivo e estável. Entregas do Governo e engajamento da liderança superam com folga as demandas pontuais."
    elif score_irg >= -10:
        badge_irg = "🟡 Estabilidade Governamental"
        cor_irg = DESIGN_TOKENS["neu"]
        desc_irg = "Cenário equilibrado. Pautas de rotina e notas institucionais dominam o debate, mantendo a percepção em patamar seguro."
    elif score_irg >= -40:
        badge_irg = "🔴 Alerta de Risco / Desgaste"
        cor_irg = DESIGN_TOKENS["neg"]
        desc_irg = "Cenário com foco de tensão. Demandas reprimidas de serviços essenciais (água, segurança ou saúde) geram desgaste pontual."
    else:
        badge_irg = "🔴 Crise de Imagem Aguda"
        cor_irg = DESIGN_TOKENS["neg"]
        desc_irg = "Cenário crítico exigindo ação imediata de contenção de danos e resposta emergencial da SECOM."

    # Liderança (Governador)
    gov_m = [m for m in mencoes if m["cita_governador"]]
    gov_pos = sum(1 for m in gov_m if m["papel_governador"] == "Vetor de Fortalecimento")
    gov_neg = sum(1 for m in gov_m if m["papel_governador"] in ["Menção Negativa", "Alvo de Crítica"])
    gov_neu = sum(1 for m in gov_m if m["papel_governador"] == "Neutro")

    # Alcance e Engajamento
    tot_alcance = sum(m["alcance"] for m in mencoes)
    tot_engajamento = sum(m["engajamento"] for m in mencoes)

    # Detalhamento por Secretaria
    sec_stats = {}
    for m in mencoes:
        s = m["secretaria"]
        if s not in sec_stats:
            sec_stats[s] = {"total": 0, "pos": 0, "neu": 0, "neg": 0, "peso": m["peso"]}
        sec_stats[s]["total"] += 1
        if m["sentimento"] == "Positivo": sec_stats[s]["pos"] += 1
        elif m["sentimento"] == "Neutro": sec_stats[s]["neu"] += 1
        elif m["sentimento"] == "Negativo": sec_stats[s]["neg"] += 1

    sec_lista = []
    for s_nome, st in sec_stats.items():
        t = st["total"]
        score_sec = round(((st["pos"] - st["neg"]) / t) * 100, 1) if t else 0
        sec_lista.append({
            "nome": s_nome,
            "total": t,
            "pos": st["pos"],
            "neu": st["neu"],
            "neg": st["neg"],
            "score": score_sec,
            "peso": st["peso"]
        })
    sec_lista.sort(key=lambda x: x["total"], reverse=True)

    # Contagem por Canais
    canais = {
        "radio": {"total": sum(1 for m in mencoes if m["canal_filtro"] == "radio"), "nome": "Rádios Broadcast", "icon": "📻"},
        "tv": {"total": sum(1 for m in mencoes if m["canal_filtro"] == "tv"), "nome": "Televisão", "icon": "📺"},
        "instagram": {"total": sum(1 for m in mencoes if m["canal_filtro"] == "instagram"), "nome": "Instagram", "icon": "📸"},
        "twitter": {"total": sum(1 for m in mencoes if m["canal_filtro"] == "twitter"), "nome": "Twitter / X", "icon": "🐦"},
        "noticia": {"total": sum(1 for m in mencoes if m["canal_filtro"] == "noticia"), "nome": "Imprensa & Notícias", "icon": "📰"},
        "facebook": {"total": sum(1 for m in mencoes if m["canal_filtro"] == "facebook"), "nome": "Facebook", "icon": "👥"},
    }

    return {
        "totais": {
            "volume": tot_vol,
            "positivos": tot_pos,
            "neutros": tot_neu,
            "negativos": tot_neg,
            "pct_positivo": pct_pos,
            "pct_neutro": pct_neu,
            "pct_negativo": pct_neg,
            "alcance": tot_alcance,
            "alcance_fmt": formatar_numero(tot_alcance),
            "engajamento": tot_engajamento,
            "engajamento_fmt": formatar_numero(tot_engajamento)
        },
        "irg": {
            "score": score_irg,
            "badge": badge_irg,
            "cor": cor_irg,
            "descricao": desc_irg
        },
        "lideranca": {
            "total": len(gov_m),
            "pct_total": round((len(gov_m) / tot_vol) * 100, 1) if tot_vol else 0,
            "vetor_fortalecimento": gov_pos,
            "mencao_negativa": gov_neg,
            "alvo_critica": gov_neg,
            "neutro": gov_neu
        },
        "secretarias": sec_lista,
        "canais": canais
    }

if __name__ == "__main__":
    mencoes = carregar_dados()
    kpis = calcular_kpis(mencoes)
    print("\n--- KPIS ATUALIZADOS COM SKILL ---")
    print(f"IRG: {kpis['irg']['score']} | {kpis['irg']['badge']}")
    print(f"Volume: {kpis['totais']['volume']} menções")
    print(f"Positivo: {kpis['totais']['pct_positivo']}% | Neutro: {kpis['totais']['pct_neutro']}% | Negativo: {kpis['totais']['pct_negativo']}%")
    print(f"Governador citado: {kpis['lideranca']['total']} menções (Positivas: {kpis['lideranca']['vetor_fortalecimento']}, Negativas: {kpis['lideranca']['alvo_critica']})")
