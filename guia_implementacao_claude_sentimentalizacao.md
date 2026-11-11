# Guia de Implementação: Análise Automatizada de Sentimento e Reputação com Claude (Anthropic API)

Este documento estabelece o guia técnico e operacional para implantar em produção o motor de inteligência artificial generativa baseado na família **Claude (Anthropic)** para leitura, análise contextual e sentimentalização das menções coletadas (Redes Sociais, Notícias e Transmissões de Rádio/TV) no âmbito do **Governo do Estado de Sergipe** e da liderança do **Governador Fábio Mitidieri**.

---

## 1. Visão Geral da Arquitetura

O sistema opera em um modelo de **esteira em lotes (batch processing)** com validação de esquema estrito e mecanismo de contingência local (*fallback* heurístico).

```mermaid
flowchart TD
    A["Menções Coletadas<br/>(Redes Sociais, Notícias, Rádio/TV)"] --> B["Normalizador de Dados<br/>(Texto, Canal, Post-Mãe)"]
    B --> C["Divisor em Lotes<br/>(Chunks de 40 a 50 menções)"]
    
    subgraph Anthropic_Engine ["Motor Claude (Anthropic API)"]
        D["System Prompt Especializado<br/>(Prompt Caching Ativado)"]
        E["Claude 3.7 / 3.5 Sonnet<br/>(temperature: 0.1)"]
        D --> E
    end
    
    C --> E
    E --> F{"Resposta da API<br/>Válida?"}
    
    F -->|Sim| G["Parser & Validador JSON<br/>(Schema Estrito)"]
    F -->|Erro / Timeout| H["Motor Heurístico Local<br/>(Fallback de Regras / IRG)"]
    
    G --> I["Consolidação da Base<br/>(Positivo, Negativo, Neutro)"]
    H --> I
    
    I --> J["Cálculo do IRG Sergipe<br/>e Balanço de Percepção"]
    J --> K["Relatório Executivo SECOM<br/>(relatorio_secom_apresentacao.html)"]
```

### Princípios Fundamentais do Projeto:
1. **Escopo Dual e Integrado:** Todo registro avalia o reflexo institucional no **Governo de Sergipe** e a dimensão política no **Governador Fábio Mitidieri**.
2. **Sentimentalização Tríplice:** Apenas `"Positivo"`, `"Negativo"` e `"Neutro"`. Jamais utilizar a categoria "Crítica".
3. **Métrica Padronizada:** O termo para visibilidade agregada é sempre **"Alcance Estimado"**.
4. **Isolamento de Marcas:** Não expor nomenclaturas de fornecedores ou ferramentas de monitoramento em prompts, relatórios ou saídas da API.

---

## 2. Requisitos e Configuração do Ambiente

### 2.1. Instalação das Dependências

No terminal ou ambiente virtual da aplicação, instale a biblioteca oficial da Anthropic e utilitários de suporte:

```bash
pip install anthropic pydantic python-dotenv
```

### 2.2. Variáveis de Ambiente (`.env`)

Crie ou edite o arquivo `.env` na raiz do projeto (`c:\Users\Lagos\Documents\Limpeza-BW\.env`):

```ini
# Chave de Autenticação da Anthropic (Console: console.anthropic.com)
ANTHROPIC_API_KEY=sk-ant-api03-sua-chave-aqui-exemplo

# Modelo Recomendado: Claude 3.7 Sonnet (ou Claude 3.5 Sonnet)
CLAUDE_MODEL=claude-3-7-sonnet-20250219

# Parâmetros de Execução
CLAUDE_TEMPERATURE=0.1
CLAUDE_MAX_TOKENS=4000

# Identificadores Institucionais
CLIENT_NAME=Governo do Estado de Sergipe
LEADERSHIP_NAME=Fábio Mitidieri
```

---

## 3. Seleção do Modelo e Estratégia de Tokens

### 3.1. Por que o Claude 3.7 / 3.5 Sonnet?

* **Compreensão de Nuance e Ironia Política:** O Sonnet decodifica sarcasmo, gírias regionais sergipanas e contextos contraditórios (ex: lealdade local vs. divergência nacional).
* **Semiótica de Emojis e Siglas Eleitorais:** Aplica com rigor a regra de que emojis de aplausos ou coração em post do Governo/Governador indicam apoio, enquanto códigos numéricos da oposição (`22`) em perfis oficiais indicam ataque.
* **Aderência a JSON Schema:** Quase 100% de precisão na geração estrita de JSON, sem alucinar campos ou incluir comentários desnecessários.
* **Prompt Caching:** Permite manter em cache o System Prompt institucional (cerca de 4.000 tokens), reduzindo o custo dos tokens de entrada em até 90% e acelerando o tempo de resposta para menos de 4 segundos por lote.

---

## 4. Estruturação do System Prompt com Prompt Caching

O System Prompt deve ser injetado separadamente através do parâmetro `system` da API da Anthropic, utilizando o cabeçalho de cache efêmero. O arquivo de referência completo é o [`prompt_instrucao_ia_classificacao_automatizada.md`](file:///c:/Users/Lagos/Documents/Limpeza-BW/prompt_instrucao_ia_classificacao_automatizada.md).

### Trecho Estrutural do System Prompt (`system`):

```text
Você é o Analista Chefe de Dados e Social Listening especializado em Reputação Governamental para o Governo do Estado de Sergipe e a liderança do Governador Fábio Mitidieri.
Seu escopo de análise é dual e integrado: avalie tanto a dimensão institucional do Governo de Sergipe quanto a liderança política do Governador.

DIRETRIZES FUNDAMENTAIS:
1. Sentimentos permitidos: ESTRITAMENTE "Positivo", "Negativo" ou "Neutro".
2. Regra do Contexto da Postagem-Mãe (Parent Context): O tom deve ser inferido em relação ao tema publicado.
3. Semiótica de Emojis e Siglas:
   - "22", "Flávio 22", "Bora 22" em canais governistas = Negativo (Oposição política).
   - "Lula 13", "1313❤️❤️", "Boraaa gente!!", "👏👏👏👏🙌❤️" em canais governistas = Positivo.
   - Sarcasmo ("Iludidos 🤭", "desta pra pior") = Negativo.
4. Métrica de Visibilidade: "Alcance Estimado".
5. Alvo Principal: Definir entre "Governador", "Governo de Sergipe", "Ambos", "Secretaria / Órgão Específico" ou "Geral".
6. Resposta: Apenas e estritamente o JSON estruturado conforme o schema.
```

---

## 5. Implementação Completa em Python

Abaixo está a implementação recomendada para o módulo [`core/claude_analyzer.py`](file:///c:/Users/Lagos/Documents/Limpeza-BW/core/claude_analyzer.py), incorporando tratamento de lotes, validação de JSON e tolerância a falhas.

```python
import os
import re
import json
import logging
from typing import List, Dict, Any, Optional
from anthropic import Anthropic, APIConnectionError, RateLimitError, APIStatusError
import config
from core.irg_engine import classificar_mencao_regras, calcular_irg

logger = logging.getLogger(__name__)

class ClaudeGovernmentAnalyzer:
    """Motor de Classificação e Reputação Governamental com Claude API."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY", config.ANTHROPIC_API_KEY)
        self.model = model or os.getenv("CLAUDE_MODEL", "claude-3-7-sonnet-20250219")
        self.client = Anthropic(api_key=self.api_key) if self.api_key else None
        self.system_prompt = self._carregar_system_prompt()

    def _carregar_system_prompt(self) -> str:
        """Carrega as diretrizes do arquivo oficial de prompt se existir, ou usa prompt interno."""
        caminho_prompt = os.path.join(
            os.path.dirname(__file__), "..", "prompt_instrucao_ia_classificacao_automatizada.md"
        )
        if os.path.exists(caminho_prompt):
            try:
                with open(caminho_prompt, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception as e:
                logger.warning(f"Não foi possível carregar prompt externo: {e}. Usando interno.")

        return f"""Você é o Analista Chefe de Social Listening para o {config.CLIENT_NAME} e o Governador {config.LEADERSHIP_NAME}.
Seu escopo é dual: avalie a dimensão do Governo do Estado de Sergipe e do Governador.
Categorias de sentimento: estritamente 'Positivo', 'Negativo' ou 'Neutro'.
Responda ESTRITAMENTE em formato JSON."""

    def processar_lote_mencoes(self, mencoes: List[Dict[str, Any]], tamanho_lote: int = 40) -> Dict[str, Any]:
        """Divide a base em lotes gerenciáveis e processa com Claude ou fallback."""
        if not self.client:
            print("[AVISO] Chave ANTHROPIC_API_KEY ausente. Ativando motor de regras local.")
            return self._analisar_localmente(mencoes)

        todas_classificadas = []
        resumo_executivo_acumulado = []
        acoes_recomendadas_acumuladas = []
        alertas_criticos_acumulados = []

        # Divide as menções em lotes de até tamanho_lote
        for i in range(0, len(mencoes), tamanho_lote):
            lote = mencoes[i : i + tamanho_lote]
            print(f"[Claude Engine] Processando lote {i // tamanho_lote + 1} ({len(lote)} menções)...")

            try:
                resultado_lote = self._chamar_api_claude(lote)
                
                todas_classificadas.extend(resultado_lote.get("mencoes_classificadas", []))
                resumo_executivo_acumulado.extend(resultado_lote.get("resumo_executivo", []))
                acoes_recomendadas_acumuladas.extend(resultado_lote.get("acoes_recomendadas", []))
                alertas_criticos_acumulados.extend(resultado_lote.get("alertas_criticos", []))
            except (RateLimitError, APIConnectionError, APIStatusError, json.JSONDecodeError) as err:
                print(f"[ERRO API CLAUDE] Falha no lote: {err}. Aplicando fallback local.")
                fallback_lote = [classificar_mencao_regras(m) for m in lote]
                todas_classificadas.extend(fallback_lote)

        return {
            "resumo_executivo": resumo_executivo_acumulado[:4],
            "acoes_recomendadas": acoes_recomendadas_acumuladas[:3],
            "alertas_criticos": alertas_criticos_acumulados[:3],
            "mencoes_classificadas": todas_classificadas,
            "total_processado": len(todas_classificadas)
        }

    def _chamar_api_claude(self, lote: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Executa a requisição de chat completions com Prompt Caching ativo."""
        amostra_minimizada = [
            {
                "id": str(m.get("id", idx)),
                "canal": m.get("canal", "Redes Sociais"),
                "texto": m.get("texto", ""),
                "post_origem": m.get("post_origem", ""),
                "autor": m.get("autor", "Não identificado"),
                "alcance_estimado": m.get("alcance_estimado", m.get("impacto", 0))
            }
            for idx, m in enumerate(lote)
        ]

        payload_user = f"""Analise as seguintes {len(amostra_minimizada)} menções de acordo com as regras estabelecidas no System Prompt.
Devolva ESTRITAMENTE o JSON estruturado contendo 'resumo_executivo', 'acoes_recomendadas', 'alertas_criticos' e a lista 'mencoes_classificadas'.

DADOS BRUTOS:
{json.dumps(amostra_minimizada, ensure_ascii=False, indent=2)}"""

        # Chamada com caching habilitado no System Prompt
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4000,
            temperature=0.1,
            system=[
                {
                    "type": "text",
                    "text": self.system_prompt,
                    "cache_control": {"type": "ephemeral"}  # Habilita Anthropic Prompt Caching
                }
            ],
            messages=[
                {"role": "user", "content": payload_user}
            ]
        )

        texto_resposta = response.content[0].text.strip()

        # Extração higienizada de JSON caso venha encapsulado em ```json ... ```
        if "```" in texto_resposta:
            match = re.search(r"\{.*\}", texto_resposta, re.DOTALL)
            if match:
                texto_resposta = match.group(0)

        return json.loads(texto_resposta)

    def _analisar_localmente(self, mencoes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Motor heurístico local para execução offline ou fallback."""
        classificadas = [classificar_mencao_regras(m) for m in mencoes]
        return {
            "resumo_executivo": [
                "Monitoramento processado pelo motor de contingência local.",
                "Taxa de polaridade governamental favorável identificada.",
                "Foco operacional nas áreas de infraestrutura e serviços públicos."
            ],
            "acoes_recomendadas": [
                "Auditar demandas prioritárias nas secretarias de atendimento direto.",
                "Acompanhar repercussões em emissoras de rádio no interior.",
                "Sustentar divulgação de entregas e agendas executivas."
            ],
            "alertas_criticos": [],
            "mencoes_classificadas": classificadas,
            "total_processado": len(classificadas)
        }
```

---

## 6. Formato do JSON de Resposta

O Claude devolverá um JSON estruturado para cada item do lote. Veja a estrutura completa:

```json
{
  "resumo_executivo": [
    "Apoio consolidado nas redes à agenda de investimentos no interior de Sergipe.",
    "Cobranças pontuais em emissoras de rádio sobre abastecimento na zona rural.",
    "Adesão do público jovem a programas de fomento ao turismo e eventos."
  ],
  "acoes_recomendadas": [
    "Articular com a assessoria da DESO esclarecimento imediato para rádio comunitária.",
    "Impulsionar matérias institucionais destacando os números da geração de emprego.",
    "Responder aos pedidos de infraestrutura com links dos cronogramas oficiais."
  ],
  "alertas_criticos": [
    "Ouvinte na Rádio X cobrando pavimentação no município Y em horário nobre."
  ],
  "mencoes_classificadas": [
    {
      "id": "1001",
      "sentimento": "Positivo",
      "alvo_principal": "Governador",
      "secretaria": "Turismo / Cultura",
      "peso_impacto": 2,
      "cita_governador": true,
      "papel_governador": "Vetor de Fortalecimento",
      "cita_governo": true,
      "papel_governo": "Vetor de Fortalecimento",
      "destaque_resumo": "Elogio enfático às atrações culturais anunciadas pelo Governador."
    },
    {
      "id": "1002",
      "sentimento": "Negativo",
      "alvo_principal": "Governo de Sergipe",
      "secretaria": "DESO / Saneamento",
      "peso_impacto": 3,
      "cita_governador": false,
      "papel_governador": "Não citado",
      "cita_governo": true,
      "papel_governo": "Alvo de Crítica",
      "destaque_resumo": "Reclamação severa sobre interrupção no fornecimento de água potável."
    }
  ]
}
```

---

## 7. Integração com o Cálculo do IRG e o Relatório Executivo

Após a classificação pelo Claude, os dados alimentam diretamente a função de cálculo do **Índice de Reputação Governamental (IRG)** e a montagem dos 4 cards executivos no gerador de relatórios:

### 7.1. Cálculo do IRG Sergipe

$$\text{IRG} = \left( \frac{\sum \text{Positivos Ponderados} - \sum \text{Negativos Ponderados}}{\text{Total de Menções}} \right) \times 100$$

* Escala do IRG: de **-100** (Crítico) a **+100** (Excelente).
* **Positivo Ponderado:** `1 + (peso_impacto - 1) * 0.5`
* **Negativo Ponderado:** `1 + (peso_impacto - 1) * 0.7` (penalização mais acentuada para pastas de serviços essenciais como DESO e HUSE).

### 7.2. Conexão com o Script do Relatório (`gerar_html_relatorio_mvp.py`)

No pipeline principal de geração do relatório:

```python
from core.claude_analyzer import ClaudeGovernmentAnalyzer
from core.irg_engine import calcular_irg

def executar_pipeline_relatorio():
    # 1. Carrega dados brutos coletados
    mencoes_brutas = carregar_mencoes_do_dia()
    
    # 2. Executa a análise inteligente com Claude
    analyzer = ClaudeGovernmentAnalyzer()
    resultado = analyzer.processar_lote_mencoes(mencoes_brutas, tamanho_lote=40)
    
    # 3. Calcula métricas consolidadas
    mencoes_classificadas = resultado["mencoes_classificadas"]
    metricas_irg = calcular_irg(mencoes_classificadas)
    
    # 4. Alimenta os Cards Executivos:
    # - Card 1: metricas_irg["irg_score"] (ex: +34.0 / 100)
    # - Card 2: metricas_irg["total_mencoes"] (ex: 1.008)
    # - Card 3: metricas_irg["alcance_estimado_total"] (ex: 2,0 mi)
    # - Card 4: metricas_irg["balanco_percepcao"] (ex: 57.6% Positivo, 18.5% Negativo, 23.9% Neutro)
    
    # 5. Renderiza o relatório final
    gerar_html_apresentacao(resultado, metricas_irg)
```

---

## 8. Monitoramento de Custos e Boas Práticas

| Operação | Sem Caching | Com Prompt Caching (Anthropic) | Economia |
| :--- | :---: | :---: | :---: |
| **System Prompt (~4.000 tokens)** | \$0.012 por lote | \$0.0012 por lote | **-90%** |
| **Lote de 40 menções (~2.000 tokens entrada)** | \$0.006 por lote | \$0.006 por lote | — |
| **Saída JSON (~2.500 tokens saída)** | \$0.0375 por lote | \$0.0375 por lote | — |
| **Custo por Edição Diária (1.000 menções / 25 lotes)** | ~\$1.39 / dia | **~\$1.12 / dia** | **Alta Eficiência** |

### Checklist de Operação em Produção:
- [x] Chave `ANTHROPIC_API_KEY` isolada em variável de ambiente.
- [x] Lotes configurados entre 40 e 50 menções para evitar estouro de `max_tokens` na resposta.
- [x] `temperature: 0.1` fixada para garantir estabilidade e repetibilidade analítica.
- [x] Tratamento de fallback local implementado para contingências de rede.
- [x] Nomenclaturas de terceiros estritamente eliminadas de logs e saídas públicas.
