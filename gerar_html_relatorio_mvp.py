# -*- coding: utf-8 -*-
"""
Gerador Definitivo do Radar Diário de Reputação - SECOM / Governo de Sergipe
Versão Executiva Refinada - Lagos Data Intelligence:
- Arquitetura CSS Híbrida 100% Autossuficiente e Responsiva (Desktop e Mobile)
- Design de Fundo do Header: Mesh Gradient CSS puro em alta definição (substitui imagem rasterizada)
- Padronização Tipográfica Global (todos os botões herdam 'Space Grotesk' e filtros unificados)
- Título Oficial: 'Radar Diário de Reputação' (SECOM / Governo de Sergipe)
- Remoção Estrita de Nomes de Ferramentas Terceirizadas (Zero menções a Brandwatch e Palver)
- Janela Diária de 24h: 20/10 às 17h até 21/10 às 17h
- Volume Total Monitorado: 1.008 manifestações agregadas (inclui 317 comentários auditados)
- Nomenclaturas Oficiais: 'Redes Sociais' e 'Notícias'; 'Negativo' em todo o relatório
- Balanço da Percepção: Gráfico de barras empilhadas duplo (Redes Sociais e Comentários do Público)
- Rádios Regionais: Ordenadas por quantidade de ouvintes com praça (Aracaju vs. Regional) e abrangência
- Feed de Destaques: Focado em alta repercussão, fácil leitura com resumos em 1 parágrafo e links originais
"""

import os
import sys
import json
import html
from datetime import datetime
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from processar_mvp_dados import carregar_dados, calcular_kpis, DESIGN_TOKENS, formatar_numero
from secao_comentarios_html import gerar_secao_comentarios_html

BASE_DIR = Path(__file__).resolve().parent

def escapar(txt):
    if not txt: return ""
    return html.escape(str(txt))

def construir_cards_feed_html(mencoes_curadas):
    """Gera os cards de alta repercussão com síntese executiva de 1 parágrafo e links originais proeminentes."""
    cards_html = []

    for m in mencoes_curadas:
        mid = m["id"]
        canal_filtro = m["canal_filtro"]
        sent_filtro = m["sentimento"].lower()
        sigla = m["sigla"]
        autor = escapar(m["autor"])
        hora = m["hora"]
        data = m["data"]
        url = m["url"]
        alcance = formatar_numero(m["alcance"])
        eng = formatar_numero(m["engajamento"])
        canal = m["canal"]
        canal_icon = m["canal_icon"]
        sentimento = m["sentimento"]
        programa = escapar(m.get("programa") or "")
        val = m.get("valuation", 0.0)

        # Classes e cores de sentimento (Strictly Negativo, Positivo, Neutro)
        if sentimento == "Positivo":
            badge_sent_cls = "badge-pos"
            icon_sent = "🟢"
        elif sentimento == "Negativo":
            badge_sent_cls = "badge-neg"
            icon_sent = "🔴"
        else:
            badge_sent_cls = "badge-neu"
            icon_sent = "🟡"

        # Badge de Liderança (Governador)
        badge_gov = ""
        if m["cita_governador"]:
            if m["papel_governador"] == "Vetor de Fortalecimento":
                badge_gov = '<span class="badge badge-gov-pos">⭐ Vetor Governamental</span>'
            elif m["papel_governador"] in ["Alvo de Crítica", "Menção Negativa"]:
                badge_gov = '<span class="badge badge-gov-neg">⚠️ Cobrança ao Governo</span>'
            else:
                badge_gov = '<span class="badge badge-gov-neu">🏛️ Pauta Institucional</span>'

        # Limpar autor caso seja genérico e tentar inferir domínio da fonte
        if not autor or autor.lower() in ["nan", "news"]:
            if url and url.startswith("http"):
                try:
                    import urllib.parse
                    domain = urllib.parse.urlparse(url).netloc.replace("www.", "")
                    autor = domain
                except Exception:
                    autor = "Portal de Notícias"
            else:
                autor = "Portal de Notícias"

        # Link de acesso ao registro original
        link_html = ""
        if url and url != "nan" and url.startswith("http"):
            link_html = f'<a href="{url}" target="_blank" rel="noopener noreferrer" class="link-original-btn">🔗 Acessar link original ↗</a>'

        # Valuation
        val_badge = ""
        if val > 0:
            val_fmt = f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            val_badge = f'<span class="badge-val">Valuation: {val_fmt}</span>'

        # Resumo executivo (rótulo conciso 'Resumo')
        resumo_exec = escapar(m.get("resumo_executivo") or m.get("resumo_paragrafo") or m["texto"])

        body_content_html = f"""
        <div class="content-summary-box">
          <span class="summary-badge">Resumo</span>
          <p class="content-summary-text">{resumo_exec}</p>
        </div>
        """

        card = f"""
        <div class="mencao-card" data-tipo="{canal_filtro}" data-sentimento="{sent_filtro}" data-id="{mid}">
          <div class="card-main">
            <div class="card-top">
              <div class="card-meta">
                <div class="meta-tags">
                  <span class="badge badge-channel">{canal_icon} {canal}</span>
                  <span class="badge badge-sec">{sigla}</span>
                  {badge_gov}
                </div>
                <h3 class="author-title">
                  {autor} {f'<span class="program-sub">· {programa}</span>' if programa else ''}
                </h3>
                <span class="post-time">{data} às {hora}</span>
              </div>
              <span class="badge-sentiment {badge_sent_cls}">{icon_sent} {sentimento}</span>
            </div>

            {body_content_html}
          </div>

          <div class="card-footer">
            <div class="footer-metrics">
              <span>Alcance Estimado: <strong>{alcance}</strong></span>
              {f'<span>Engajamento: <strong>{eng}</strong></span>' if eng != "0" else ''}
              {val_badge}
            </div>
            {link_html}
          </div>
        </div>
        """
        cards_html.append(card)

    return "\n".join(cards_html)

def gerar_relatorio_completo():
    print("🚀 Gerando Radar Diário de Reputação (SECOM / Governo de Sergipe) - Versão Refinada...")
    mencoes = carregar_dados()
    kpis = calcular_kpis(mencoes)

    totais = kpis["totais"]
    irg = kpis["irg"]
    lideranca = kpis["lideranca"]
    canais = kpis["canais"]

    # 1. TRANSMISSÕES DE BROADCAST: RÁDIOS E TELEVISÃO
    mencoes_broadcast = [m for m in mencoes if m["canal_filtro"] in ["radio", "tv"]]
    radios_bcast = [m for m in mencoes_broadcast if m["canal_filtro"] == "radio"]
    tvs_bcast = [m for m in mencoes_broadcast if m["canal_filtro"] == "tv"]

    # Ordenação das rádios pela quantidade de ouvintes estimada (decrescente)
    radios_bcast.sort(key=lambda x: x.get("ouvintes", 0), reverse=True)

    # Cards das Rádios ordenadas por ouvintes (Top 5 emissoras)
    cards_radios_list = []
    for r in radios_bcast[:5]:
        midia_url = r["midia_url"]
        duracao = r.get("duracao", "00:00:30")
        emissora = escapar(r["autor"])
        prog = escapar(r.get("programa") or "")
        resumo = escapar(r.get("resumo_executivo") or r.get("resumo_paragrafo") or r["texto"])
        data = r["data"]
        hora = r["hora"]
        municipio = escapar(r.get("municipio", "Aracaju"))
        abrangencia = escapar(r.get("abrangencia", "Regional"))
        ouvintes = r.get("ouvintes", 0)
        ouvintes_fmt = f"{ouvintes:,}".replace(",", ".")

        player_html = ""
        if midia_url:
            player_html = f"""
            <div class="player-box">
              <audio controls class="audio-native" preload="none" src="{midia_url}">
                <source src="{midia_url}" type="audio/mpeg">
                Seu navegador não suporta reprodução direta.
              </audio>
              <div style="margin-top: 8px; text-align: right;">
                <a href="{midia_url}" target="_blank" rel="noopener noreferrer" class="btn-play-external">▶ Reproduzir Áudio em Nova Guia ↗</a>
              </div>
            </div>
            """

        card_radio = f"""
        <div class="bcast-card">
          <div>
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; margin-bottom: 10px;">
              <div style="display: flex; gap: 6px; align-items: center; flex-wrap: wrap;">
                <span class="badge badge-channel">📻 Rádio Broadcast</span>
                <span class="badge" style="background-color: rgba(0, 243, 255, 0.12); color: var(--cy); border: 1px solid rgba(0, 243, 255, 0.35);">👥 {ouvintes_fmt} ouvintes est.</span>
                <span class="badge badge-sec">📍 {municipio} · {abrangencia}</span>
              </div>
              <span style="font-size: 11px; color: var(--lav-2);">{data} às {hora}</span>
            </div>

            <h3 style="font-size: 13px; font-weight: 800; color: #FFF; margin-bottom: 4px;">
              {emissora} <span style="font-size: 11px; font-weight: 500; color: var(--lav-2);">· {prog}</span>
            </h3>

            <div class="content-summary-box bcast-summary">
              <span class="summary-badge">Síntese</span>
              <p class="content-summary-text">{resumo}</p>
            </div>

            {player_html}
          </div>

          <div style="margin-top: 12px; display: flex; justify-content: space-between; align-items: center; font-size: 11px; color: var(--lav-2);">
            <span>Duração da veiculação: <strong>{duracao}</strong></span>
            {f'<a href="{midia_url}" target="_blank" rel="noopener noreferrer" class="link-original-btn">▶ Áudio Original ↗</a>' if midia_url else ''}
          </div>
        </div>
        """
        cards_radios_list.append(card_radio)

    radios_html = "\n".join(cards_radios_list)

    # Cards de Destaque de Televisão (Top 5 reportagens)
    cards_tvs_list = []
    for tv in tvs_bcast[:5]:
        midia_url = tv["midia_url"]
        duracao = tv.get("duracao", "00:00:30")
        emissora = escapar(tv["autor"])
        prog = escapar(tv.get("programa") or "")
        resumo = escapar(tv.get("resumo_executivo") or tv.get("resumo_paragrafo") or tv["texto"])
        data = tv["data"]
        hora = tv["hora"]

        player_html = ""
        if midia_url:
            player_html = f"""
            <div class="player-box">
              <video controls class="video-native" preload="metadata" playsinline src="{midia_url}">
                <source src="{midia_url}" type="video/mp4">
                Seu navegador não suporta reprodução direta.
              </video>
              <div style="margin-top: 8px; text-align: right;">
                <a href="{midia_url}" target="_blank" rel="noopener noreferrer" class="btn-play-external">▶ Reproduzir Vídeo em Nova Guia ↗</a>
              </div>
            </div>
            """

        card_tv = f"""
        <div class="bcast-card">
          <div>
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; margin-bottom: 10px;">
              <div style="display: flex; gap: 6px; align-items: center; flex-wrap: wrap;">
                <span class="badge" style="background-color: var(--ind-deep); color: var(--mag); border: 1px solid rgba(255,0,90,0.4);">📺 Televisão</span>
                <span class="badge badge-sec">📍 Aracaju · Cobertura Estadual</span>
              </div>
              <span style="font-size: 11px; color: var(--lav-2);">{data} às {hora}</span>
            </div>

            <h3 style="font-size: 13px; font-weight: 800; color: #FFF; margin-bottom: 4px;">
              {emissora} <span style="font-size: 11px; font-weight: 500; color: var(--lav-2);">· {prog}</span>
            </h3>

            <div class="content-summary-box bcast-summary">
              <span class="summary-badge">Síntese</span>
              <p class="content-summary-text">{resumo}</p>
            </div>

            {player_html}
          </div>

          <div style="margin-top: 12px; display: flex; justify-content: space-between; align-items: center; font-size: 11px; color: var(--lav-2);">
            <span>Duração da reportagem: <strong>{duracao}</strong></span>
            {f'<a href="{midia_url}" target="_blank" rel="noopener noreferrer" class="link-original-btn">▶ Vídeo Original ↗</a>' if midia_url else ''}
          </div>
        </div>
        """
        cards_tvs_list.append(card_tv)

    tvs_html = "\n".join(cards_tvs_list)

    # 2. CURADORIA DO FEED DE ALTA REPERCUSSÃO (CONCISO, DIRECIONADO PARA LINKS)
    mencoes_noticias = [m for m in mencoes if m["canal_filtro"] == "noticia"]
    mencoes_sociais = [m for m in mencoes if m["canal_filtro"] in ["instagram", "twitter", "facebook", "social"]]

    textos_vistos = set()
    sociais_filtradas = []
    for m in mencoes_sociais:
        txt_res = m["texto"][:70].lower()
        if txt_res not in textos_vistos:
            textos_vistos.add(txt_res)
            sociais_filtradas.append(m)

    sociais_filtradas.sort(key=lambda x: (x["engajamento"], x["alcance"]), reverse=True)

    noticias_vistas = set()
    noticias_filtradas = []
    for m in mencoes_noticias:
        txt_res = m["texto"][:70].lower()
        if txt_res not in noticias_vistas:
            noticias_vistas.add(txt_res)
            noticias_filtradas.append(m)

    # Priorizar matérias jornalísticas com links diretos válidos para os portais
    noticias_com_link = [m for m in noticias_filtradas if m.get("url") and str(m["url"]).startswith("http")]
    if len(noticias_com_link) >= 5:
        top_noticias = noticias_com_link[:5]
    else:
        top_noticias = (noticias_com_link + [m for m in noticias_filtradas if m not in noticias_com_link])[:5]

    # Seleção dos destaques de maior repercussão (5 para cada segmento):
    # 5 principais manifestações em redes sociais + 5 principais matérias jornalísticas de notícias
    curadas_feed = sociais_filtradas[:5] + top_noticias
    curadas_feed.sort(key=lambda x: (x["engajamento"], x["alcance"]), reverse=True)

    print(f"   ✔ Cards selecionados para o feed de alta repercussão: {len(curadas_feed)} ocorrências")
    cards_feed_html = construir_cards_feed_html(curadas_feed)

    cnt_feed_todos = len(curadas_feed)
    cnt_feed_sociais = sum(1 for m in curadas_feed if m["canal_filtro"] in ["instagram", "twitter", "facebook", "social"])
    cnt_feed_noticias = sum(1 for m in curadas_feed if m["canal_filtro"] == "noticia")
    cnt_feed_pos = sum(1 for m in curadas_feed if m["sentimento"] == "Positivo")
    cnt_feed_neg = sum(1 for m in curadas_feed if m["sentimento"] == "Negativo")

    # 3. SEÇÃO ESPECIAL DE COMENTÁRIOS E EMOJIS
    print("   ✔ Integrando Seção de Comentários e Emojis...")
    secao_comentarios_html = gerar_secao_comentarios_html()

    # MONTAGEM DO HTML COMPLETO
    html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0">
  <title>Radar Diário de Reputação · Governo de Sergipe | SECOM</title>
  
  <!-- Fontes Oficiais -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700;800&display=swap" rel="stylesheet">

  <style>
    /* ==========================================================================
       DESIGN TOKENS & ESTILOS GLOBAIS AUTOSSUFICIENTES (LAGOS DATA INTELLIGENCE)
       Visual moderno, responsivo, nítido em Desktop e Mobile.
       ========================================================================== */
    :root {{
      --ind: #252375;
      --ind-2: #2E2C80;
      --ind-3: #3B3990;
      --ind-4: #4D4B9E;
      --ind-d: #1D1B5E;
      --ind-deep: #151347;
      --mag: #FF005A;
      --mag-h: #E0004F;
      --cy: #00F3FF;
      --lav: #D2D1F9;
      --lav-2: #B9B8E0;
      --ice: #F4F4FA;
      --pos: #00F3FF;
      --neg: #FF005A;
      --neu: #B9B8E0;
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      font-family: 'Space Grotesk', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      background-color: var(--ind-deep);
      color: var(--ice);
      line-height: 1.45;
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
      overflow-x: hidden;
      padding: 20px 0 40px 0;
    }}

    /* PADRONIZAÇÃO TIPOGRÁFICA GLOBAL: Todos os botões herdam Space Grotesk */
    button, input, select, textarea {{
      font-family: inherit;
    }}

    /* CONTAINER CENTRAL E MARGENS DEFINITIVAS - FORMATO A4 EXECUTIVO */
    .container {{
      width: 100%;
      max-width: 800px;
      margin: 0 auto;
      padding: 0 16px;
    }}

    /* CABEÇALHO INSTITUCIONAL ENQUADRADO */
    .header-wrapper {{
      background-color: var(--ind-d);
      background-image:
        radial-gradient(circle at 88% 12%, rgba(0, 243, 255, 0.14) 0%, transparent 42%),
        radial-gradient(circle at 12% 88%, rgba(255, 0, 90, 0.12) 0%, transparent 38%),
        radial-gradient(circle at 50% 50%, rgba(59, 57, 144, 0.28) 0%, transparent 60%);
      border: 1px solid var(--ind-3);
      border-radius: 16px;
      padding: 16px 20px;
      margin-bottom: 18px;
      box-shadow: 0 6px 24px rgba(0, 0, 0, 0.22);
      position: relative;
    }}

    .header-top {{
      display: flex;
      flex-direction: row;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
      flex-wrap: wrap;
    }}

    .brand-area {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .brand-logo {{
      height: 32px;
      width: auto;
      object-fit: contain;
    }}

    .kicker {{
      display: inline-block;
      font-size: 10px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      color: var(--mag);
      background-color: var(--ind-deep);
      padding: 2px 10px;
      border-radius: 9999px;
      border: 1px solid rgba(255, 0, 90, 0.35);
      margin-bottom: 3px;
    }}

    .header-title {{
      font-size: 18px;
      font-weight: 800;
      color: #FFFFFF;
      letter-spacing: -0.02em;
      line-height: 1.2;
    }}

    .header-subtitle {{
      font-size: 11.5px;
      color: var(--lav-2);
      margin-top: 3px;
    }}

    .header-actions {{
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
    }}

    .btn-action {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 8px 14px;
      border-radius: 10px;
      font-size: 11px;
      font-weight: 700;
      cursor: pointer;
      text-decoration: none;
      transition: all 0.2s ease;
      background-color: var(--ind-2);
      color: #FFFFFF;
      border: 1px solid var(--ind-4);
    }}

    .btn-action:hover {{
      background-color: var(--ind-3);
      border-color: var(--lav-2);
    }}

    .badge-live {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 7px 12px;
      border-radius: 10px;
      font-size: 11px;
      font-weight: 700;
      background-color: var(--ind-deep);
      color: var(--cy);
      border: 1px solid rgba(0, 243, 255, 0.4);
    }}

    .pulse-dot {{
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background-color: var(--cy);
      box-shadow: 0 0 8px var(--cy);
    }}

    /* BARRA DE METADADOS */
    .meta-bar {{
      margin-top: 12px;
      padding-top: 10px;
      border-top: 1px solid var(--ind-3);
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 10px;
      font-size: 10.5px;
      color: var(--lav-2);
    }}

    .meta-items {{
      display: flex;
      flex-wrap: wrap;
      gap: 16px;
    }}

    /* SEÇÕES E GRIDS */
    main.main-content {{
      display: flex;
      flex-direction: column;
      gap: 18px;
    }}

    .kpi-grid {{
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 14px;
    }}

    .card {{
      background-color: var(--ind-2);
      border: 1px solid var(--ind-3);
      border-radius: 16px;
      padding: 14px 16px;
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.16);
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      position: relative;
    }}

    .card-label {{
      font-size: 9.5px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--lav-2);
      display: block;
    }}

    .kpi-big {{
      font-size: 24px;
      font-weight: 900;
      color: #FFFFFF;
      line-height: 1.1;
      margin-top: 4px;
    }}

    .kpi-unit {{
      font-size: 11px;
      font-weight: 500;
      color: var(--lav-2);
    }}

    .card-desc {{
      font-size: 10.5px;
      color: var(--lav-2);
      margin-top: 4px;
    }}

    /* CARD DO IRG ESPECÍFICO */
    .card-irg {{
      border-width: 2px;
    }}

    .irg-header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
    }}

    .badge-irg {{
      font-size: 10px;
      font-weight: 800;
      padding: 3px 9px;
      border-radius: 9999px;
      border: 1px solid transparent;
    }}

    .gauge-wrap {{
      margin-top: 12px;
    }}

    .gauge-legend {{
      display: flex;
      justify-content: space-between;
      font-size: 9px;
      color: var(--lav-2);
      margin-bottom: 3px;
    }}

    .gauge-track {{
      width: 100%;
      height: 8px;
      background-color: var(--ind-d);
      border-radius: 9999px;
      overflow: hidden;
      border: 1px solid var(--ind-4);
    }}

    .gauge-fill {{
      height: 100%;
      border-radius: 9999px;
      transition: width 0.8s ease;
    }}

    .irg-diag {{
      font-size: 10px;
      color: var(--ice);
      margin-top: 8px;
      line-height: 1.35;
    }}

    /* SÍNTESE EXECUTIVA & DIRECIONAMENTOS */
    .two-cols-grid {{
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 14px;
    }}

    .section-title-wrap {{
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 12px;
    }}

    .section-icon {{
      font-size: 14px;
      background-color: var(--ind-d);
      padding: 6px;
      border-radius: 10px;
      border: 1px solid var(--ind-3);
    }}

    .section-h2 {{
      font-size: 14px;
      font-weight: 800;
      color: #FFFFFF;
    }}

    .section-sub {{
      font-size: 11px;
      color: var(--lav-2);
    }}

    .bullet-list {{
      display: flex;
      flex-direction: column;
      gap: 8px;
    }}

    .bullet-item {{
      display: flex;
      align-items: flex-start;
      gap: 8px;
      background-color: rgba(29, 27, 94, 0.7);
      padding: 10px 12px;
      border-radius: 12px;
      border: 1px solid var(--ind-3);
      font-size: 11px;
      line-height: 1.45;
    }}

    .bullet-icon-pos {{ color: var(--pos); font-weight: bold; font-size: 13px; }}
    .bullet-icon-neg {{ color: var(--neg); font-weight: bold; font-size: 13px; }}
    .bullet-icon-mag {{ color: var(--mag); font-weight: bold; font-size: 13px; }}

    /* SEÇÃO DESTAQUES DE BROADCAST (RÁDIO E TELEVISÃO) */
    .bcast-grid {{
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 12px;
      margin-top: 12px;
    }}

    .bcast-card {{
      background-color: var(--ind-d);
      border: 1px solid var(--ind-3);
      border-radius: 14px;
      padding: 14px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }}

    /* BARRA DE FILTROS & BUSCA PADRONIZADA */
    .filter-card {{
      background-color: var(--ind-2);
      border: 1px solid var(--ind-3);
      border-radius: 16px;
      padding: 14px 16px;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }}

    .filter-row-top {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 12px;
    }}

    .search-wrapper {{
      position: relative;
      width: 100%;
      max-width: 260px;
    }}

    .search-input {{
      width: 100%;
      background-color: var(--ind-d);
      border: 1px solid var(--ind-4);
      border-radius: 10px;
      padding: 7px 12px 7px 30px;
      color: #FFFFFF;
      font-size: 11px;
      outline: none;
      transition: border-color 0.2s;
    }}

    .search-input:focus {{
      border-color: var(--cy);
    }}

    .search-icon {{
      position: absolute;
      left: 10px;
      top: 8px;
      font-size: 11px;
      color: var(--lav-2);
    }}

    .filter-groups {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 12px;
      padding-top: 10px;
      border-top: 1px solid var(--ind-3);
    }}

    .btn-filter {{
      background-color: transparent;
      border: 1px solid var(--ind-4);
      color: var(--lav-2);
      padding: 4px 10px;
      border-radius: 9999px;
      font-size: 10.5px;
      font-weight: 700;
      cursor: pointer;
      transition: all 0.2s;
    }}

    .btn-filter:hover {{
      color: #FFFFFF;
      border-color: var(--lav-2);
    }}

    .btn-filter.active-canal {{
      background-color: var(--mag);
      border-color: var(--mag);
      color: #FFFFFF;
    }}

    .btn-filter.active-sent {{
      background-color: var(--ind-4);
      border-color: var(--ind-4);
      color: #FFFFFF;
    }}

    /* GRID DO FEED DE MENÇÕES */
    .mencoes-grid {{
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 12px;
    }}

    .mencao-card {{
      background-color: var(--ind-2);
      border: 1px solid var(--ind-3);
      border-radius: 16px;
      padding: 14px 16px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      transition: transform 0.15s ease, border-color 0.15s ease;
    }}

    .mencao-card:hover {{
      border-color: var(--ind-4);
    }}

    .card-top {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 10px;
      margin-bottom: 8px;
    }}

    .meta-tags {{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 5px;
      margin-bottom: 4px;
    }}

    .badge {{
      display: inline-flex;
      align-items: center;
      padding: 2px 6px;
      border-radius: 5px;
      font-size: 9px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }}

    .badge-channel {{
      background-color: var(--ind-d);
      color: var(--cy);
      border: 1px solid rgba(0, 243, 255, 0.3);
    }}

    .badge-sec {{
      background-color: var(--ind-d);
      color: var(--lav-2);
      border: 1px solid var(--ind-4);
    }}

    .badge-gov-pos {{
      background-color: rgba(0, 243, 255, 0.15);
      color: var(--pos);
      border: 1px solid rgba(0, 243, 255, 0.4);
    }}

    .badge-gov-neg {{
      background-color: rgba(255, 0, 90, 0.15);
      color: var(--neg);
      border: 1px solid rgba(255, 0, 90, 0.4);
    }}

    .badge-gov-neu {{
      background-color: var(--ind-d);
      color: var(--ice);
      border: 1px solid var(--ind-4);
    }}

    .author-title {{
      font-size: 12.5px;
      font-weight: 800;
      color: #FFFFFF;
      margin-top: 2px;
    }}

    .program-sub {{
      font-size: 11px;
      font-weight: 400;
      color: var(--lav-2);
    }}

    .post-time {{
      font-size: 10px;
      color: var(--lav-2);
      display: block;
      margin-top: 1px;
    }}

    .badge-sentiment {{
      padding: 3px 8px;
      border-radius: 9999px;
      font-size: 10px;
      font-weight: 800;
      flex-shrink: 0;
    }}

    .badge-pos {{
      background-color: rgba(0, 243, 255, 0.15);
      color: var(--pos);
      border: 1px solid rgba(0, 243, 255, 0.4);
    }}

    .badge-neg {{
      background-color: rgba(255, 0, 90, 0.15);
      color: var(--neg);
      border: 1px solid rgba(255, 0, 90, 0.4);
    }}

    .badge-neu {{
      background-color: var(--ind-d);
      color: var(--lav-2);
      border: 1px solid var(--ind-4);
    }}

    /* SÍNTESE EXECUTIVA DE CONTEÚDO */
    .content-summary-box {{
      background-color: rgba(255, 255, 255, 0.03);
      border: 1px solid var(--ind-4);
      border-left: 3px solid var(--cy);
      border-radius: 10px;
      padding: 10px 12px;
      margin: 8px 0;
    }}

    .content-summary-box.bcast-summary {{
      border-left-color: var(--mag);
      background-color: rgba(255, 0, 90, 0.04);
    }}

    .summary-badge {{
      display: inline-block;
      font-size: 9px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--cy);
      margin-bottom: 3px;
    }}

    .bcast-summary .summary-badge {{
      color: var(--mag);
    }}

    .content-summary-text {{
      font-size: 11px;
      font-weight: 500;
      line-height: 1.45;
      color: #FFFFFF;
      margin: 0;
    }}

    /* EXPANSÃO DO TEXTO ORIGINAL */
    .raw-toggle {{
      margin-top: 6px;
    }}

    .raw-toggle-btn {{
      font-size: 10px;
      font-weight: 600;
      color: var(--lav-2);
      cursor: pointer;
      user-select: none;
      transition: color 0.2s;
    }}

    .raw-toggle-btn:hover {{
      color: var(--cy);
    }}

    .raw-text-content {{
      font-size: 10px;
      line-height: 1.4;
      color: var(--lav-2);
      background-color: rgba(0, 0, 0, 0.25);
      border-radius: 6px;
      padding: 8px 10px;
      margin-top: 4px;
      border-left: 2px solid var(--ind-4);
      font-style: italic;
      word-break: break-word;
    }}

    /* PLAYERS MULTIMÍDIA */
    .player-box {{
      margin-top: 8px;
      padding: 8px 10px;
      background-color: var(--ind-d);
      border-radius: 12px;
      border: 1px solid var(--ind-3);
    }}

    .btn-play-external {{
      display: inline-flex;
      align-items: center;
      gap: 4px;
      background-color: rgba(255, 255, 255, 0.07);
      border: 1px solid var(--ind-4);
      color: var(--cy);
      font-size: 9.5px;
      font-weight: 700;
      text-decoration: none;
      padding: 3px 8px;
      border-radius: 6px;
      transition: all 0.2s ease;
    }}

    .btn-play-external:hover {{
      background-color: var(--mag);
      border-color: var(--mag);
      color: #FFFFFF;
    }}

    .audio-native {{
      width: 100%;
      height: 28px;
      border-radius: 6px;
    }}

    .video-native {{
      width: 100%;
      max-height: 160px;
      border-radius: 10px;
      background-color: #000;
    }}

    /* RODAPÉ DO CARD */
    .card-footer {{
      margin-top: 10px;
      padding-top: 10px;
      border-top: 1px solid var(--ind-3);
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 6px;
      font-size: 10.5px;
      color: var(--lav-2);
    }}

    .footer-metrics {{
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
    }}

    .footer-metrics strong {{
      color: #FFFFFF;
    }}

    .badge-val {{
      font-size: 9px;
      font-weight: 700;
      color: var(--cy);
      background-color: var(--ind-d);
      padding: 2px 6px;
      border-radius: 5px;
      border: 1px solid rgba(0, 243, 255, 0.3);
    }}

    .link-original-btn {{
      display: inline-flex;
      align-items: center;
      gap: 5px;
      background-color: rgba(0, 243, 255, 0.12);
      border: 1px solid rgba(0, 243, 255, 0.4);
      color: var(--cy);
      font-size: 10px;
      font-weight: 700;
      text-decoration: none;
      padding: 4px 10px;
      border-radius: 8px;
      transition: all 0.2s ease;
    }}

    .link-original-btn:hover {{
      background-color: var(--cy);
      color: var(--ind-deep);
      transform: translateY(-1px);
    }}

    /* NAVEGAÇÃO RÁPIDA (ÍNDICE EXECUTIVO) */
    .quick-nav {{
      margin-top: 10px;
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      align-items: center;
    }}

    .btn-nav {{
      font-size: 10px;
      font-weight: 700;
      color: var(--ice);
      background-color: var(--ind-d);
      border: 1px solid var(--ind-4);
      padding: 4px 10px;
      border-radius: 9999px;
      text-decoration: none;
      transition: all 0.2s ease;
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }}

    .btn-nav:hover {{
      background-color: var(--ind-3);
      border-color: var(--cy);
      color: #FFFFFF;
      transform: translateY(-1px);
    }}

    .btn-nav.active-nav {{
      border-color: rgba(0, 243, 255, 0.5);
      color: var(--cy);
      background-color: rgba(0, 243, 255, 0.08);
    }}

    /* RODAPÉ INSTITUCIONAL ENQUADRADO */
    footer.page-footer {{
      margin-top: 24px;
      background-color: var(--ind-d);
      border: 1px solid var(--ind-3);
      border-radius: 14px;
      padding: 14px 18px;
      font-size: 10.5px;
      color: var(--lav-2);
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.16);
    }}

    .footer-flex {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 14px;
    }}

    /* REGRAS DE RESPONSIVIDADE (MOBILE & TABLET) */
    @media (max-width: 820px) {{
      .container {{
        padding: 0 12px;
      }}
      .kpi-grid {{
        grid-template-columns: repeat(2, 1fr);
      }}
      .two-cols-grid {{
        grid-template-columns: 1fr;
      }}
      .bcast-grid {{
        grid-template-columns: 1fr;
      }}
      .mencoes-grid {{
        grid-template-columns: 1fr;
      }}
    }}

    @media (max-width: 560px) {{
      body {{
        padding: 12px 0 30px 0;
      }}
      .header-wrapper {{
        padding: 14px;
        border-radius: 14px;
        margin-bottom: 14px;
      }}
      .header-title {{
        font-size: 16px;
      }}
      .kpi-grid {{
        grid-template-columns: 1fr;
        gap: 10px;
      }}
      .kpi-big {{
        font-size: 22px;
      }}
      .card {{
        padding: 12px;
        border-radius: 14px;
      }}
      footer.page-footer {{
        padding: 12px;
        border-radius: 12px;
      }}
    }}

    @media print {{
      @page {{
        size: A4 portrait;
        margin: 10mm 12mm;
      }}
      .no-print {{ display: none !important; }}
      body {{
        background-color: #FFFFFF !important;
        color: #000000 !important;
        padding: 0 !important;
        font-size: 9pt !important;
      }}
      .container {{
        max-width: 100% !important;
        padding: 0 !important;
        margin: 0 !important;
      }}
      .header-wrapper, footer.page-footer, .card, .bcast-card, .mencao-card, .coment-card {{
        background-color: #FFFFFF !important;
        border: 1px solid #D0D0D0 !important;
        color: #000000 !important;
        box-shadow: none !important;
        border-radius: 8px !important;
        background-image: none !important;
        padding: 10px 12px !important;
        break-inside: avoid !important;
        page-break-inside: avoid !important;
      }}
      .header-title {{ font-size: 14pt !important; color: #000000 !important; }}
      .kpi-big {{ font-size: 16pt !important; color: #000000 !important; }}
      .section-h2 {{ font-size: 10.5pt !important; color: #000000 !important; }}
      .author-title {{ font-size: 9.5pt !important; color: #000000 !important; }}
      .content-summary-text, .bullet-item {{ font-size: 8pt !important; color: #222222 !important; }}
      .card-desc, .section-sub, .post-time, .footer-metrics {{ font-size: 7.5pt !important; color: #555555 !important; }}
      .link-original-btn, .btn-action, .btn-nav, .btn-filter {{ display: none !important; }}
    }}
  </style>
</head>
<body>

  <div class="container report-container">

    <!-- CABEÇALHO INSTITUCIONAL -->
    <header class="header-wrapper">
      <div class="header-top">
        <div class="brand-area">
          <img src="assets/logo-lagos.png" alt="Lagos Data Intelligence" class="brand-logo">
          <div>
            <span class="kicker">Inteligência Governamental · SECOM</span>
            <h1 class="header-title">Radar Diário de Reputação</h1>
            <p class="header-subtitle">
              Governo do Estado de Sergipe · Monitoramento Integrado Multimodal: Redes Sociais, Noticiário, Rádios e Televisão
            </p>
          </div>
        </div>

        <div class="header-actions no-print">
          <button onclick="window.print()" class="btn-action">
            🖨️ Exportar PDF / Imprimir
          </button>
          <div class="badge-live">
            <span class="pulse-dot"></span>
            Base Integrada: 1.008 manifestações
          </div>
        </div>
      </div>

      <!-- Barra de Metadados -->
      <div class="meta-bar">
        <div class="meta-items">
          <span>📅 <strong>Período de Referência:</strong> 20/10 às 17h até 21/10 às 17h (Janela Diária de 24h)</span>
          <span>🏛️ <strong>Liderança:</strong> Gov. Fábio Mitidieri ({lideranca['pct_total']}% de centralidade)</span>
          <span>⏱️ <strong>Ciclo Operacional:</strong> Diário (17h às 17h)</span>
        </div>
      </div>

      <!-- Menu de Navegação Rápida (Índice Executivo) -->
      <nav class="quick-nav no-print">
        <span style="font-size: 11px; font-weight: 800; text-transform: uppercase; color: var(--lav-2); margin-right: 4px;">Índice Executivo:</span>
        <a href="#secao-visao-geral" class="btn-nav">📊 Visão Geral & IRG</a>
        <a href="#secao-sintese" class="btn-nav">📌 Síntese Executiva</a>
        <a href="#secao-broadcast" class="btn-nav">🎙️ Rádios & TV</a>
        <a href="#secao-comentarios-sociais" class="btn-nav">💬 Comentários do Público</a>
        <a href="#secao-feed-mencoes" class="btn-nav active-nav">🔎 Destaques de Repercussão</a>
      </nav>
    </header>

    <!-- CONTEÚDO PRINCIPAL -->
    <main class="main-content">

    <!-- SEÇÃO 1: CARDS DE KPIS & ÍNDICE IRG -->
    <section id="secao-visao-geral">
      <div class="kpi-grid">
        
        <!-- CARD IRG -->
        <div class="card card-irg" style="border-color: {irg['cor']};">
          <div>
            <div class="irg-header">
              <span class="card-label">Índice IRG Sergipe</span>
              <span class="badge-irg" style="background-color: {irg['cor']}25; color: {irg['cor']}; border-color: {irg['cor']}60; white-space: nowrap;">
                {irg['badge']}
              </span>
            </div>
            <div class="kpi-big" style="color: {irg['cor']};">
              +{irg['score']} <span class="kpi-unit">/ 100</span>
            </div>
          </div>

          <div class="gauge-wrap">
            <div class="gauge-legend" style="display: flex; justify-content: space-between; font-size: 9.5px; color: var(--lav-2); margin-bottom: 4px; white-space: nowrap;">
              <span>-100 (Crítico)</span>
              <span>0 (Neutro)</span>
              <span>+100 (Excelente)</span>
            </div>
            <div class="gauge-track">
              <div class="gauge-fill" style="width: {(irg['score'] + 100) / 2}%; background-color: {irg['cor']};"></div>
            </div>
            <p class="irg-diag" style="font-size: 11px; color: var(--ice); margin-top: 8px; line-height: 1.45;">{irg['descricao']}</p>
          </div>
        </div>

        <!-- CARD VOLUME & MULTIMODAL (COM COMENTÁRIOS E NOMENCLATURAS OFICIAIS) -->
        <div class="card">
          <div>
            <span class="card-label">Volume Total Monitorado</span>
            <div class="kpi-big">1.008 <span class="kpi-unit">manifestações</span></div>
            <p class="card-desc">Redes sociais, notícias, rádio, TV e comentários populares</p>
          </div>

          <div style="margin-top: 14px; display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px;">
            <div style="background-color: var(--ind-d); padding: 8px 12px; border-radius: 12px; border: 1px solid var(--ind-4); display: flex; justify-content: space-between; align-items: center; gap: 8px;">
              <span style="font-size: 10.5px; color: var(--lav-2); white-space: nowrap;">🎙️ Rádios</span>
              <strong style="font-size: 11.5px; color: #FFF; white-space: nowrap;">{canais['radio']['total']} áudios</strong>
            </div>
            <div style="background-color: var(--ind-d); padding: 8px 12px; border-radius: 12px; border: 1px solid var(--ind-4); display: flex; justify-content: space-between; align-items: center; gap: 8px;">
              <span style="font-size: 10.5px; color: var(--lav-2); white-space: nowrap;">📺 Televisão</span>
              <strong style="font-size: 11.5px; color: #FFF; white-space: nowrap;">{canais['tv']['total']} vídeos</strong>
            </div>
            <div style="background-color: var(--ind-d); padding: 8px 12px; border-radius: 12px; border: 1px solid var(--ind-4); display: flex; justify-content: space-between; align-items: center; gap: 8px;">
              <span style="font-size: 10.5px; color: var(--lav-2); white-space: nowrap;">📱 Redes Sociais</span>
              <strong style="font-size: 11.5px; color: #FFF; white-space: nowrap;">622 posts</strong>
            </div>
            <div style="background-color: var(--ind-d); padding: 8px 12px; border-radius: 12px; border: 1px solid var(--ind-4); display: flex; justify-content: space-between; align-items: center; gap: 8px;">
              <span style="font-size: 10.5px; color: var(--lav-2); white-space: nowrap;">📰 Notícias</span>
              <strong style="font-size: 11.5px; color: #FFF; white-space: nowrap;">50 matérias</strong>
            </div>
            <div style="grid-column: span 2; background-color: var(--ind-d); padding: 8px 12px; border-radius: 12px; border: 1px solid var(--ind-4); display: flex; justify-content: space-between; align-items: center; gap: 8px;">
              <span style="font-size: 11px; color: var(--cy); display: flex; align-items: center; gap: 6px; white-space: nowrap;">
                💬 <strong>Comentários Auditados</strong>
              </span>
              <strong style="font-size: 11.5px; color: var(--cy); white-space: nowrap;">317 interações</strong>
            </div>
          </div>
        </div>

        <!-- CARD AUDIÊNCIA & ALCANCE ESTIMADO -->
        <div class="card">
          <div>
            <span class="card-label">Alcance Estimado Total</span>
            <div class="kpi-big" style="color: var(--cy);">{totais['alcance_fmt']}</div>
            <p class="card-desc">Audiência agregada de ouvintes, telespectadores e leitores</p>
          </div>

          <div style="margin-top: 14px; padding-top: 12px; border-top: 1px solid var(--ind-3); font-size: 11.5px; display: flex; flex-direction: column; gap: 8px;">
            <div style="display: flex; justify-content: space-between; align-items: center; gap: 12px;">
              <span style="color: var(--lav-2); white-space: nowrap;">Engajamento Direto:</span>
              <strong style="color: #FFF; white-space: nowrap;">{totais['engajamento_fmt']} interações</strong>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; gap: 12px;">
              <span style="color: var(--lav-2); white-space: nowrap;">Média por Publicação:</span>
              <strong style="color: #FFF; white-space: nowrap;">{round(totais['engajamento'] / (totais['volume'] or 1), 1)} interações/post</strong>
            </div>
          </div>
        </div>

        <!-- CARD BALANÇO DE PERCEPÇÃO: GRÁFICO DE BARRAS EMPILHADAS (REDES E COMENTÁRIOS) -->
        <div class="card">
          <div>
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
              <span class="card-label">Balanço da Percepção</span>
              <div style="display: flex; gap: 8px; font-size: 10px; font-weight: 700; white-space: nowrap;">
                <span style="color: var(--pos);">🟢 Positivo</span>
                <span style="color: var(--neg);">🔴 Negativo</span>
                <span style="color: var(--neu);">🟡 Neutro</span>
              </div>
            </div>
            <p class="card-desc" style="margin-top: 4px;">Comparativo de polaridade por fonte de manifestação</p>
          </div>

          <div style="margin-top: 14px; display: flex; flex-direction: column; gap: 12px;">
            
            <!-- Barra Empilhada 1: Redes Sociais & Noticiário -->
            <div>
              <div style="display: flex; justify-content: space-between; align-items: center; font-size: 10.5px; margin-bottom: 4px;">
                <span style="color: var(--ice); font-weight: 700; white-space: nowrap;">📱 Redes Sociais & Notícias</span>
                <span style="color: var(--lav-2); font-weight: 600; white-space: nowrap;">
                  <strong style="color: var(--pos);">{totais['pct_positivo']}%</strong> / 
                  <strong style="color: var(--neg);">{totais['pct_negativo']}%</strong> / 
                  <strong style="color: var(--neu);">{totais['pct_neutro']}%</strong>
                </span>
              </div>
              <div style="width: 100%; height: 8px; background-color: var(--ind-d); border-radius: 9999px; overflow: hidden; display: flex; border: 1px solid var(--ind-4);">
                <div style="width: {totais['pct_positivo']}%; background-color: var(--pos);" title="Positivo: {totais['pct_positivo']}%"></div>
                <div style="width: {totais['pct_negativo']}%; background-color: var(--neg);" title="Negativo: {totais['pct_negativo']}%"></div>
                <div style="width: {totais['pct_neutro']}%; background-color: var(--neu);" title="Neutro: {totais['pct_neutro']}%"></div>
              </div>
            </div>

            <!-- Barra Empilhada 2: Comentários do Público -->
            <div>
              <div style="display: flex; justify-content: space-between; align-items: center; font-size: 10.5px; margin-bottom: 4px;">
                <span style="color: var(--ice); font-weight: 700; white-space: nowrap;">💬 Comentários do Público</span>
                <span style="color: var(--lav-2); font-weight: 600; white-space: nowrap;">
                  <strong style="color: var(--pos);">52.4%</strong> / 
                  <strong style="color: var(--neg);">23.3%</strong> / 
                  <strong style="color: var(--neu);">24.3%</strong>
                </span>
              </div>
              <div style="width: 100%; height: 8px; background-color: var(--ind-d); border-radius: 9999px; overflow: hidden; display: flex; border: 1px solid var(--ind-4);">
                <div style="width: 52.4%; background-color: var(--pos);" title="Positivo: 52.4%"></div>
                <div style="width: 23.3%; background-color: var(--neg);" title="Negativo: 23.3%"></div>
                <div style="width: 24.3%; background-color: var(--neu);" title="Neutro: 24.3%"></div>
              </div>
            </div>

          </div>
        </div>

      </div>
    </section>

    <!-- SEÇÃO 2: SÍNTESE EXECUTIVA & RECOMENDAÇÕES DA SECOM -->
    <section class="two-cols-grid" id="secao-sintese">
      
      <!-- SÍNTESE EXECUTIVA -->
      <div class="card">
        <div>
          <div class="section-title-wrap">
            <span class="section-icon">📌</span>
            <div>
              <h2 class="section-h2">Síntese Executiva Diária</h2>
              <p class="section-sub">Diagnóstico estratégico das últimas 24 horas</p>
            </div>
          </div>

          <div class="bullet-list">
            <div class="bullet-item">
              <span class="bullet-icon-pos">✓</span>
              <span><strong>Liderança do Governador como Vetor Positivo:</strong> As publicações oficiais do Governador Fábio Mitidieri (quadro "Gov Responde", mobilização comunitária e agendas de governo) geraram forte engajamento favorável, somando 343 manifestações de apoio direto.</span>
            </div>
            <div class="bullet-item">
              <span class="bullet-icon-pos">✓</span>
              <span><strong>Entregas em Infraestrutura e Emprego:</strong> A liberação da 2ª alça do Complexo Viário Senadora Maria do Carmo Alves e o anúncio de 521 vagas de trabalho na Plataforma GO Sergipe ancoraram a percepção de resolutividade da gestão.</span>
            </div>
            <div class="bullet-item">
              <span class="bullet-icon-neg">!</span>
              <span><strong>Foco Negativo em Saneamento (DESO / Iguá):</strong> Queixas pontuais sobre desabastecimento em bairros de Aracaju e no interior pautaram ligações de ouvintes no rádio matinal e comentários em publicações públicas.</span>
            </div>
            <div class="bullet-item">
              <span class="bullet-icon-mag">⚡</span>
              <span><strong>Segurança Pública em Foco:</strong> A decisão administrativa da SSP quanto à lotação do delegado André David concentrou debates na imprensa regional e comentários no meio político.</span>
            </div>
          </div>
        </div>
      </div>

      <!-- DIRECIONAMENTOS SECOM -->
      <div class="card">
        <div>
          <div class="section-title-wrap">
            <span class="section-icon">🎯</span>
            <div>
              <h2 class="section-h2">Direcionamentos & Ações Táticas (SECOM)</h2>
              <p class="section-sub">Recomendações prioritárias de comunicação institucional</p>
            </div>
          </div>

          <div class="bullet-list">
            <div class="bullet-item">
              <span class="bullet-icon-mag">1.</span>
              <span><strong>Comunicação Preventiva de Saneamento:</strong> Intensificar a divulgação do cronograma de manutenções e reparos da rede hídrica nas rádios locais e redes sociais para antecipar respostas a ouvintes.</span>
            </div>
            <div class="bullet-item">
              <span class="bullet-icon-mag">2.</span>
              <span><strong>Potencialização do Complexo Viário:</strong> Veicular vídeos com tomadas aéreas e depoimentos de motoristas evidenciando a fluidez no trânsito após a inauguração da 2ª alça do viaduto.</span>
            </div>
            <div class="bullet-item">
              <span class="bullet-icon-mag">3.</span>
              <span><strong>Passo a Passo de Vagas GO Sergipe:</strong> Lançar carrossel informativo e reels orientando a população sobre o cadastro digital para as 521 vagas de emprego da SEDETEC.</span>
            </div>
          </div>
        </div>

        <div style="margin-top: 16px; padding-top: 14px; border-top: 1px solid var(--ind-3);">
          <span style="font-size: 11px; font-weight: 800; text-transform: uppercase; color: var(--neg); display: block; margin-bottom: 6px;">
            🚨 Ponto de Atenção em Monitoramento Contínuo:
          </span>
          <p style="font-size: 12px; background-color: rgba(255, 0, 90, 0.15); padding: 10px 14px; border-radius: 12px; border: 1px solid rgba(255, 0, 90, 0.35); color: #FFF;">
            Acompanhar comentários no interior sobre o fornecimento de água para preservar a avaliação positiva da gestão e garantir respostas operacionais rápidas aos cidadãos.
          </p>
        </div>
      </div>

    </section>

    <!-- SEÇÃO 3: DESTAQUES DE BROADCAST (RÁDIOS ORDENADAS POR OUVINTES E TELEVISÃO) -->
    <section class="card" id="secao-broadcast">
      <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 14px; margin-bottom: 20px; padding-bottom: 14px; border-bottom: 1px solid var(--ind-3);">
        <div class="section-title-wrap" style="margin-bottom: 0;">
          <span class="section-icon">🎙️</span>
          <div>
            <h2 class="section-h2">Destaques da Radiodifusão & Televisão</h2>
            <p class="section-sub">
              Emissoras de rádio ordenadas por audiência estimada e praça de cobertura, acompanhadas dos registros televisivos com reprodutor de mídia e síntese executiva.
            </p>
          </div>
        </div>
        <span class="badge badge-channel">Top 10 Veiculações Multimídia (5 Rádios + 5 TVs)</span>
      </div>

      <!-- SUBSEÇÃO RÁDIOS -->
      <div style="margin-bottom: 24px;">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
          <h3 style="font-size: 13px; font-weight: 800; color: #FFF; display: flex; align-items: center; gap: 8px;">
            📻 Emissoras de Rádio Regionais <span style="font-size: 11px; font-weight: 500; color: var(--lav-2);">(Ordenadas por Audiência Estimada)</span>
          </h3>
          <span style="font-size: 11px; color: var(--cy); font-weight: 700;">Top 5 emissoras por audiência</span>
        </div>

        <div class="bcast-grid">
          {radios_html}
        </div>
      </div>

      <!-- SUBSEÇÃO TELEVISÃO -->
      <div style="padding-top: 16px; border-top: 1px solid var(--ind-3);">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
          <h3 style="font-size: 13px; font-weight: 800; color: #FFF; display: flex; align-items: center; gap: 8px;">
            📺 Cobertura em Telejornais <span style="font-size: 11px; font-weight: 500; color: var(--lav-2);">(Principais Veiculações Estaduais)</span>
          </h3>
          <span style="font-size: 11px; color: var(--mag); font-weight: 700;">Top 5 matérias televisivas</span>
        </div>

        <div class="bcast-grid">
          {tvs_html}
        </div>
      </div>
    </section>

    <!-- SEÇÃO 4: RADAR DE ENGAJAMENTO POPULAR & ANÁLISE QUALITATIVA DE COMENTÁRIOS -->
    {secao_comentarios_html}

    <!-- SEÇÃO 5: FEED DE DESTAQUES DE ALTA REPERCUSSÃO -->
    <section id="secao-feed-mencoes" style="display: flex; flex-direction: column; gap: 20px;">
      
      <!-- FILTROS & PESQUISA DE ALTA REPERCUSSÃO -->
      <div class="filter-card no-print">
        <div class="filter-row-top">
          <div>
            <h2 class="section-h2" style="font-size: 14px;">Feed de Destaques de Repercussão & Fatos Relevantes</h2>
            <p class="section-sub">Seleção executiva dos fatos de maior repercussão, audiência e engajamento nas últimas 24 horas</p>
          </div>

          <div class="search-wrapper">
            <input type="text" id="campo-busca" oninput="buscar()" placeholder="Buscar por termo, autor ou tema..." class="search-input">
            <span class="search-icon">🔎</span>
          </div>
        </div>

        <div class="filter-groups">
          <!-- Filtro por Canal -->
          <div style="display: flex; flex-wrap: wrap; align-items: center; gap: 8px;">
            <span style="font-size: 11px; font-weight: 800; text-transform: uppercase; color: var(--lav-2); margin-right: 4px;">Canal:</span>
            <button onclick="filtrarCanal('todos')" id="btn-c-todos" class="btn-filter active-canal">
              Todos ({cnt_feed_todos})
            </button>
            <button onclick="filtrarCanal('social')" id="btn-c-social" class="btn-filter">
              📱 Redes Sociais ({cnt_feed_sociais})
            </button>
            <button onclick="filtrarCanal('noticia')" id="btn-c-noticia" class="btn-filter">
              📰 Notícias ({cnt_feed_noticias})
            </button>
          </div>

          <!-- Filtro por Sentimento -->
          <div style="display: flex; flex-wrap: wrap; align-items: center; gap: 8px;">
            <span style="font-size: 11px; font-weight: 800; text-transform: uppercase; color: var(--lav-2); margin-right: 4px;">Sentimento:</span>
            <button onclick="filtrarSentimento('todos')" id="btn-s-todos" class="btn-filter active-sent">
              Todos
            </button>
            <button onclick="filtrarSentimento('positivo')" id="btn-s-positivo" class="btn-filter" style="color: var(--pos);">
              🟢 Positivo ({cnt_feed_pos})
            </button>
            <button onclick="filtrarSentimento('negativo')" id="btn-s-negativo" class="btn-filter" style="color: var(--neg);">
              🔴 Negativo ({cnt_feed_neg})
            </button>
          </div>
        </div>

        <div style="display: flex; justify-content: space-between; font-size: 11px; color: var(--lav-2); padding-top: 8px; border-top: 1px solid rgba(77, 75, 158, 0.4);">
          <span>Exibindo <strong id="contador-visivel" style="color: #FFF;">{len(curadas_feed)}</strong> fatos de maior repercussão (5 em Redes Sociais + 5 em Notícias)</span>
          <span style="font-style: italic;">Acesso direto à publicação original</span>
        </div>
      </div>

      <!-- GRID DOS CARDS DE MENÇÃO -->
      <div id="grid-mencoes" class="mencoes-grid">
        {cards_feed_html}
      </div>

    </section>

  </main>

  <!-- RODAPÉ INSTITUCIONAL -->
  <footer class="page-footer">
    <div class="footer-flex">
      <div>
        <p style="font-size: 12px; font-weight: 800; color: #FFFFFF;">
          Radar Diário de Reputação · Governo do Estado de Sergipe
        </p>
        <p style="margin-top: 4px; color: var(--lav-2);">
          Sistema Integrado de Inteligência de Comunicação & Monitoramento Multimodal
        </p>
        <p style="font-size: 10px; margin-top: 2px; color: rgba(185, 184, 224, 0.6);">
          Metodologia IRG · Desenvolvido para a Secretaria de Estado da Comunicação Social (SECOM)
        </p>
      </div>
      <div>
        <img src="assets/logo-lagos.png" alt="Lagos Data Intelligence" style="height: 24px; width: auto; object-fit: contain;">
      </div>
    </div>
  </footer>

  </div>

  <!-- SCRIPT DE FILTROS & BUSCA -->
  <script>
    let canalAtivo = 'todos';
    let sentimentoAtivo = 'todos';

    function atualizarFeed() {{
      const termo = (document.getElementById('campo-busca').value || '').toLowerCase().trim();
      const cards = document.querySelectorAll('.mencao-card');
      let visiveis = 0;

      cards.forEach(card => {{
        const tipo = card.getAttribute('data-tipo');
        const sent = card.getAttribute('data-sentimento');
        const textoCard = card.innerText.toLowerCase();

        const matchCanal = (canalAtivo === 'todos') || (tipo === canalAtivo) || (canalAtivo === 'social' && (tipo === 'instagram' || tipo === 'twitter' || tipo === 'facebook' || tipo === 'social'));
        const matchSent = (sentimentoAtivo === 'todos') || (sent === sentimentoAtivo);
        const matchTermo = !termo || textoCard.includes(termo);

        if (matchCanal && matchSent && matchTermo) {{
          card.style.display = 'flex';
          visiveis++;
        }} else {{
          card.style.display = 'none';
        }}
      }});

      document.getElementById('contador-visivel').innerText = visiveis;
    }}

    function filtrarCanal(canal) {{
      canalAtivo = canal;
      document.querySelectorAll('.btn-filter').forEach(btn => {{
        if (btn.id.startsWith('btn-c-')) {{
          btn.classList.remove('active-canal');
        }}
      }});
      const bAtivo = document.getElementById('btn-c-' + canal);
      if (bAtivo) {{
        bAtivo.classList.add('active-canal');
      }}
      atualizarFeed();
    }}

    function filtrarSentimento(sent) {{
      sentimentoAtivo = sent;
      document.querySelectorAll('.btn-filter').forEach(btn => {{
        if (btn.id.startsWith('btn-s-')) {{
          btn.classList.remove('active-sent');
        }}
      }});
      const bAtivo = document.getElementById('btn-s-' + sent);
      if (bAtivo) {{
        bAtivo.classList.add('active-sent');
      }}
      atualizarFeed();
    }}

    function buscar() {{
      atualizarFeed();
    }}
  </script>

</body>
</html>
"""

    # 1. Salvar na raiz
    caminho_raiz = BASE_DIR / "relatorio_secom_apresentacao.html"
    with open(caminho_raiz, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"✔ Salvo com sucesso em: {caminho_raiz}")

    # 2. Salvar na pasta output
    caminho_output = BASE_DIR / "output" / "relatorio_secom_apresentacao.html"
    os.makedirs(BASE_DIR / "output", exist_ok=True)
    with open(caminho_output, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"✔ Salvo cópia em: {caminho_output}")

    print("🎉 Relatório concluído e gerado com 100% de sucesso!")

if __name__ == "__main__":
    gerar_relatorio_completo()
