# ============================================================================
# IMPORTAÇÕES
# ============================================================================

import stre
amlit as st
import pandas as pd
import requests
import json
import time
import re
# ============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================================

import streamlit as st
import base64

# Icone SVG convertido para Base64
svg_icon = """
<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M5 8C8 6 16 6 19 8" stroke="#8D6E63" stroke-width="2" stroke-linecap="round"/>
  <path d="M5 13C8 11 16 11 19 13" stroke="#6D4C41" stroke-width="2" stroke-linecap="round"/>
  <path d="M5 18C8 16 16 16 19 18" stroke="#4E342E" stroke-width="2" stroke-linecap="round"/>
  <circle cx="12" cy="4" r="2" fill="#4CAF50"/>
</svg>
"""

svg_base64 = base64.b64encode(svg_icon.encode()).decode()

st.set_page_config(
    page_title="Classificador Inteligente de Fertilidade do Solo",
    page_icon=f"data:image/svg+xml;base64,{svg_base64}",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# BASES DE FERTILIDADE DO SOLO - EMBRAPA, CFSEMG, BOLETIM 100 E REGIONAIS
# ============================================================================

# ============================================================================
# 1. EMBRAPA - Tabelas de interpretação de fertilidade
# ============================================================================

INTERPRETACAO_EMBRAPA = {
    "ph": {
        "muito_baixo": "< 4.5",
        "baixo": "4.5 - 5.0",
        "medio": "5.1 - 5.5",
        "adequado": "5.6 - 6.5",
        "alto": "6.6 - 7.0",
        "muito_alto": "> 7.0"
    },
    "p_mehlich": {
        "muito_baixo": "< 3",
        "baixo": "3 - 5",
        "medio": "6 - 10",
        "adequado": "11 - 20",
        "alto": "21 - 40",
        "muito_alto": "> 40"
    },
    "k": {
        "muito_baixo": "< 0.05",
        "baixo": "0.05 - 0.10",
        "medio": "0.11 - 0.20",
        "adequado": "0.21 - 0.30",
        "alto": "0.31 - 0.50",
        "muito_alto": "> 0.50"
    },
    "v_percent": {
        "baixo": "< 50",
        "medio": "50 - 70",
        "adequado": "70 - 85",
        "alto": "> 85"
    },
    "m_percent": {
        "baixo": "< 10",
        "medio": "10 - 20",
        "alto": "20 - 40",
        "muito_alto": "> 40"
    },
    "materia_organica": {
        "muito_baixo": "< 10",
        "baixo": "10 - 20",
        "medio": "21 - 30",
        "adequado": "31 - 40",
        "alto": "> 40"
    }
}

# ============================================================================
# 2. CFSEMG - COMISSÃO DE FERTILIDADE DO SOLO DO ESTADO DE MINAS GERAIS
# ============================================================================

INTERPRETACAO_CFSEMG = {
    "ph": {
        "muito_baixo": "< 4.9",
        "baixo": "5.0 - 5.4",
        "medio": "5.5 - 5.9",
        "adequado": "6.0 - 6.5",
        "alto": "> 6.5"
    },
    "p_resina": {
        "muito_baixo": "< 4",
        "baixo": "4 - 8",
        "medio": "9 - 15",
        "adequado": "16 - 30",
        "alto": "> 30"
    },
    "k": {
        "muito_baixo": "< 0.05",
        "baixo": "0.05 - 0.10",
        "medio": "0.11 - 0.20",
        "adequado": "0.21 - 0.35",
        "alto": "> 0.35"
    },
    "v_percent": {
        "baixo": "< 50",
        "medio": "50 - 70",
        "adequado": "70 - 80",
        "alto": "> 80"
    }
}

# ============================================================================
# 3. BOLETIM 100 - IAC (Instituto Agronômico de Campinas)
# ============================================================================

INTERPRETACAO_BOLETIM_100 = {
    "ph_cacl2": {
        "muito_baixo": "< 4.3",
        "baixo": "4.4 - 4.8",
        "medio": "4.9 - 5.2",
        "adequado": "5.3 - 6.0",
        "alto": "> 6.0"
    },
    "p_resina": {
        "muito_baixo": "< 5",
        "baixo": "5 - 14",
        "medio": "15 - 29",
        "adequado": "30 - 59",
        "alto": "> 60"
    },
    "v_percent": {
        "baixo": "< 50",
        "medio": "50 - 70",
        "adequado": "> 70"
    }
}

# ============================================================================
# 4. RECOMENDAÇÕES REGIONAIS POR UF
# ============================================================================

RECOMENDACOES_REGIONAIS = {
    "SP": {
        "nome": "São Paulo",
        "referencia": "Boletim 100 - IAC",
        "ph_ideal": (5.3, 6.0),
        "v_ideal": 70,
        "observacao": "Utilizar extrator Resina para P e K"
    },
    "MG": {
        "nome": "Minas Gerais",
        "referencia": "CFSEMG - 5ª Aproximação",
        "ph_ideal": (6.0, 6.5),
        "v_ideal": 70,
        "observacao": "Recomendado para cerrado e mata atlântica"
    },
    "RS": {
        "nome": "Rio Grande do Sul",
        "referencia": "CQFS RS/SC - 2016",
        "ph_ideal": (5.5, 6.0),
        "v_ideal": 65,
        "observacao": "Solos de várzea e planalto"
    },
    "SC": {
        "nome": "Santa Catarina",
        "referencia": "CQFS RS/SC - 2016",
        "ph_ideal": (5.5, 6.0),
        "v_ideal": 65,
        "observacao": "Solos de várzea e planalto"
    },
    "PR": {
        "nome": "Paraná",
        "referencia": "Manual de Adubação - IAPAR",
        "ph_ideal": (5.5, 6.2),
        "v_ideal": 65,
        "observacao": "Região Sul - Manejo conservacionista"
    },
    "MT": {
        "nome": "Mato Grosso",
        "referencia": "Embrapa Cerrados",
        "ph_ideal": (5.5, 6.5),
        "v_ideal": 60,
        "observacao": "Solos de cerrado - Necessidade de gessagem"
    },
    "GO": {
        "nome": "Goiás",
        "referencia": "Embrapa Cerrados",
        "ph_ideal": (5.5, 6.5),
        "v_ideal": 60,
        "observacao": "Solos de cerrado - Necessidade de gessagem"
    },
    "BA": {
        "nome": "Bahia",
        "referencia": "Embrapa Semiárido",
        "ph_ideal": (5.8, 6.5),
        "v_ideal": 65,
        "observacao": "Região semiárida - Manejo conservacionista"
    },
    "NORDESTE": {
        "nome": "Região Nordeste",
        "referencia": "Embrapa Semiárido",
        "ph_ideal": (5.8, 6.5),
        "v_ideal": 65,
        "observacao": "Solos com altos teores de sais"
    },
    "NORTE": {
        "nome": "Região Norte",
        "referencia": "Embrapa Amazônia",
        "ph_ideal": (5.0, 5.8),
        "v_ideal": 50,
        "observacao": "Solos ácidos - Floresta Amazônica"
    }
}

# ============================================================================
# FUNÇÃO PARA INTERPRETAR SEGUNDO MÚLTIPLAS METODOLOGIAS
# ============================================================================

def interpretar_pelo_embrapa(parametro, valor):
    """Interpreta o valor segundo a tabela da Embrapa"""
    interpretacao = INTERPRETACAO_EMBRAPA.get(parametro, {})
    if not interpretacao:
        return "Sem referência"
    
    for classe, faixa in interpretacao.items():
        if '-' in str(faixa):
            partes = faixa.split(' - ')
            if len(partes) == 2:
                try:
                    min_val = float(partes[0])
                    max_val = float(partes[1])
                    if min_val <= valor <= max_val:
                        return classe.replace('_', ' ').title()
                except:
                    pass
        elif '>' in str(faixa):
            try:
                limite = float(faixa.replace('>', ''))
                if valor > limite:
                    return classe.replace('_', ' ').title()
            except:
                pass
        elif '<' in str(faixa):
            try:
                limite = float(faixa.replace('<', ''))
                if valor < limite:
                    return classe.replace('_', ' ').title()
            except:
                pass
    
    return "Não classificado"

def interpretar_pelo_cfsemg(parametro, valor):
    """Interpreta o valor segundo a CFSEMG"""
    interpretacao = INTERPRETACAO_CFSEMG.get(parametro, {})
    if not interpretacao:
        return "Sem referência"
    
    for classe, faixa in interpretacao.items():
        if '-' in str(faixa):
            partes = faixa.split(' - ')
            if len(partes) == 2:
                try:
                    min_val = float(partes[0])
                    max_val = float(partes[1])
                    if min_val <= valor <= max_val:
                        return classe.replace('_', ' ').title()
                except:
                    pass
        elif '>' in str(faixa):
            try:
                limite = float(faixa.replace('>', ''))
                if valor > limite:
                    return classe.replace('_', ' ').title()
            except:
                pass
        elif '<' in str(faixa):
            try:
                limite = float(faixa.replace('<', ''))
                if valor < limite:
                    return classe.replace('_', ' ').title()
            except:
                pass
    
    return "Não classificado"

def interpretar_fertilidade_multiplas_bases(dados):
    """Gera interpretação combinada de múltiplas bases de fertilidade"""
    resultados = {
        "embrapa": {},
        "cfsemg": {},
        "boletim_100": {}
    }
    
    # pH
    ph = dados.get('ph', 0)
    resultados["embrapa"]["pH"] = interpretar_pelo_embrapa("ph", ph)
    resultados["cfsemg"]["pH"] = interpretar_pelo_cfsemg("ph", ph)
    
    # Fósforo
    p = dados.get('phosphorus', 0)
    resultados["embrapa"]["Fósforo"] = interpretar_pelo_embrapa("p_mehlich", p)
    resultados["cfsemg"]["Fósforo"] = interpretar_pelo_cfsemg("p_resina", p)
    
    # Potássio
    k = dados.get('potassium', 0)
    resultados["embrapa"]["Potássio"] = interpretar_pelo_embrapa("k", k)
    resultados["cfsemg"]["Potássio"] = interpretar_pelo_cfsemg("k", k)
    
    # Saturação por bases
    v = dados.get('v_porcentagem', 0)
    resultados["embrapa"]["V%"] = interpretar_pelo_embrapa("v_percent", v)
    resultados["cfsemg"]["V%"] = interpretar_pelo_cfsemg("v_percent", v)
    
    # Matéria orgânica
    om = dados.get('organic_matter', 0) if 'organic_matter' in dados else dados.get('materia_organica', 0)
    if om > 0:
        resultados["embrapa"]["Matéria Orgânica"] = interpretar_pelo_embrapa("materia_organica", om)
    
    return resultados

def recomendar_por_regiao(uf, dados):
    """Recomendações específicas baseadas na região"""
    regiao = RECOMENDACOES_REGIONAIS.get(uf.upper(), RECOMENDACOES_REGIONAIS.get("SP"))
    
    recomendacoes = []
    recomendacoes.append(f"**📍 Base técnica para {regiao['nome']}:** {regiao['referencia']}")
    recomendacoes.append(f"**🔬 Observação:** {regiao['observacao']}")
    
    ph_atual = dados.get('ph', 0)
    ph_min, ph_max = regiao['ph_ideal']
    
    if ph_atual < ph_min:
        recomendacoes.append(f"🔴 **pH regional:** {ph_atual:.1f} - Abaixo do ideal regional ({ph_min}-{ph_max}). Calagem recomendada.")
    elif ph_atual > ph_max:
        recomendacoes.append(f"🟡 **pH regional:** {ph_atual:.1f} - Acima do ideal regional ({ph_min}-{ph_max}). Monitorar disponibilidade de micronutrientes.")
    else:
        recomendacoes.append(f"🟢 **pH regional:** {ph_atual:.1f} - Dentro da faixa ideal para a região ({ph_min}-{ph_max}).")
    
    v_atual = dados.get('v_porcentagem', 0)
    v_ideal = regiao['v_ideal']
    
    if v_atual < v_ideal:
        recomendacoes.append(f"🔴 **V% regional:** {v_atual:.1f}% - Abaixo do ideal regional (≥{v_ideal}%). Necessidade de calagem.")
    else:
        recomendacoes.append(f"🟢 **V% regional:** {v_atual:.1f}% - Atende ao ideal regional (≥{v_ideal}%).")
    
    return recomendacoes

# ============================================================================
# CONFIGURAÇÃO GEMINI API
# ============================================================================

GEMINI_API_KEY = "AIzaSyAkj0m6HFJxX9hGNopoUiUxWDgPJrMkQww"  # ← INSIRA SUA CHAVE AQUI!

# ============================================================================
# FUNÇÃO PARA LISTAR MODELOS DISPONÍVEIS
# ============================================================================

def listar_modelos_disponiveis():
    """Lista todos os modelos Gemini disponíveis para sua chave"""
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={GEMINI_API_KEY}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            modelos = response.json()
            nomes_modelos = []
            
            for model in modelos.get('models', []):
                nome = model.get('name', '').replace('models/', '')
                if 'gemini' in nome and 'generateContent' in str(model.get('supportedGenerationMethods', [])):
                    nomes_modelos.append(nome)
            
            return nomes_modelos
        else:
            return []
    except Exception as e:
        return []

# ============================================================================
# FUNÇÃO IA GEMINI (ATUALIZADA COM BASES DE FERTILIDADE)
# ============================================================================

def gerar_resposta_ia(pergunta, dados_solo=None):
    """Função com detecção automática do modelo e bases de fertilidade"""
    
    if not GEMINI_API_KEY or GEMINI_API_KEY == "SUA_API_KEY_AQUI":
        return "⚠️ **API Key não configurada!** Configure sua chave no código."
    
    try:
        modelos = listar_modelos_disponiveis()
        
        if not modelos:
            return "❌ **Nenhum modelo Gemini disponível!** Verifique sua API Key."
        
        modelo = modelos[0]
        
        contexto = ""
        if dados_solo and len(dados_solo) > 0:
            contexto = f"""
            Dados do solo analisado:
            - pH: {dados_solo.get('ph', 'N/A')}
            - Saturação por bases (V%): {dados_solo.get('v_porcentagem', 0):.1f}%
            - Saturação por alumínio (m%): {dados_solo.get('m_porcentagem', 0):.1f}%
            - Nitrogênio (N): {dados_solo.get('nitrogen', 'N/A')} mg/dm³
            - Fósforo (P): {dados_solo.get('phosphorus', 'N/A')} mg/dm³
            - Potássio (K): {dados_solo.get('potassium', 'N/A')} cmolc/dm³
            - Cálcio (Ca): {dados_solo.get('calcium', 'N/A')} cmolc/dm³
            - Magnésio (Mg): {dados_solo.get('magnesium', 'N/A')} cmolc/dm³
            - Alumínio (Al): {dados_solo.get('aluminum', 'N/A')} cmolc/dm³
            - H+Al: {dados_solo.get('h_al', 'N/A')} cmolc/dm³
            - Soma de Bases (SB): {dados_solo.get('sb', 0):.2f} cmolc/dm³
            - CTC Potencial: {dados_solo.get('ctc', 0):.2f} cmolc/dm³
            - Textura: Areia {dados_solo.get('sand', 0)}% | Silte {dados_solo.get('silt', 0)}% | Argila {dados_solo.get('clay', 0)}%
            """
        
        prompt = f"""Você é um engenheiro agrônomo especialista em fertilidade do solo e de culturas brasileiras, SiBCS e manejo agrícola. 
        Suas respostas devem ser baseadas nas seguintes referências técnicas brasileiras:
        - Embrapa (Empresa Brasileira de Pesquisa Agropecuária)
        - CFSEMG (Comissão de Fertilidade do Solo do Estado de Minas Gerais)
        - Boletim 100 - IAC (Instituto Agronômico de Campinas)
        - Recomendações regionais por estado (SP, MG, RS, SC, PR, MT, GO, BA)

{contexto}

PERGUNTA DO USUÁRIO: {pergunta}

INSTRUÇÕES:
- Responda em português do Brasil
- Seja técnico, claro, objetivo e principalmente didático
- Dê recomendações práticas quando possível
- Se não souber algo, diga honestamente
- Use linguagem acessível para produtores rurais
- Sempre que possível, mencione qual base técnica (Embrapa, CFSEMG, Boletim 100) está sendo utilizada

RESPOSTA:"""
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent?key={GEMINI_API_KEY}"
        
        headers = {"Content-Type": "application/json"}
        
        data = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ]
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            resultado = response.json()
            
            if "candidates" in resultado and len(resultado["candidates"]) > 0:
                candidate = resultado["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    if len(candidate["content"]["parts"]) > 0:
                        resposta = candidate["content"]["parts"][0].get("text", "")
                        return resposta
            
            return "❌ Não foi possível extrair a resposta da IA."
        
        elif response.status_code == 401:
            return "❌ **Erro de autenticação (401):** API Key inválida."
        elif response.status_code == 403:
            return "❌ **Acesso negado (403):** Ative a API Gemini."
        elif response.status_code == 429:
            return "❌ **Limite excedido (429):** Muitas requisições. Aguarde."
        else:
            return f"❌ **Erro {response.status_code}**"
    
    except Exception as erro:
        return f"❌ **Erro:** {str(erro)}"

# ============================================================================
# CSS PERSONALIZADO - CORRIGIDO (INPUTS COM TEXTO VISÍVEL)
# ============================================================================

st.markdown("""
<style>
    /* ========== RESET E FONTES ========== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,300;14..32,400;14..32,500;14..32,600;14..32,700&display=swap');
    
    * {
        font-family: 'Inter', 'Segoe UI', sans-serif !important;
    }
    
    /* ========== FUNDO PRINCIPAL ========== */
    .stApp {
        background: radial-gradient(circle at 20% 30%, #0a0f1e, #05070f);
        color: #ffffff;
    }
    
    /* ========== SIDEBAR MAIS COMPACTA ========== */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(10,15,30,0.98) 0%, rgba(5,7,15,0.98) 100%);
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(46,204,113,0.2);
        box-shadow: 4px 0 30px rgba(0,0,0,0.3);
        min-width: 280px;
    }
    
    /* ========== TÍTULOS ========== */
    h1, h2, h3, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        background: linear-gradient(135deg, #2ecc71, #27ae60);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
    }
    
    h1 {
        font-size: 2.2rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    h2 {
        font-size: 1.5rem !important;
        margin-top: 0.5rem !important;
    }
    
    /* ========== TEXTO GERAL ========== */
    p, span, div, label, .stMarkdown, .stText, .stCaption {
        color: #e2e8f0 !important;
        line-height: 1.5;
    }
    
    /* ========== INPUTS CORRIGIDOS - TEXTO PRETO VISÍVEL ========== */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stDateInput > div > div > input {
        background: rgba(255,255,255,0.9) !important;
        border: 1px solid rgba(46,204,113,0.4) !important;
        border-radius: 12px !important;
        padding: 10px 14px !important;
        color: #1a1a2e !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #2ecc71 !important;
        box-shadow: 0 0 0 2px rgba(46,204,113,0.3) !important;
        outline: none !important;
    }
    
    /* Placeholder mais claro */
    .stTextInput > div > div > input::placeholder {
        color: #666 !important;
    }
    
        /* Selectbox corrigido - FUNDO ESCURO COM TEXTO BRANCO */
    .stSelectbox > div > div {
        background: rgba(20, 20, 40, 0.95) !important;
        border: 1px solid rgba(46,204,113,0.4) !important;
        border-radius: 12px !important;
        color: white !important;
    }
    
    .stSelectbox > div > div > div {
        color: white !important;
    }
    
    .stSelectbox > div > div > div[role="combobox"] {
        color: white !important;
    }
    
    /* Opções do dropdown (lista suspensa) */
    div[data-baseweb="select"] > div {
        background: rgba(20, 20, 40, 0.98) !important;
        backdrop-filter: blur(10px);
    }
    
    div[data-baseweb="select"] ul {
        background: rgba(15, 15, 30, 0.98) !important;
    }
    
    div[data-baseweb="select"] li {
        color: white !important;
        background: transparent !important;
    }
    
    div[data-baseweb="select"] li:hover {
        background: rgba(46,204,113,0.2) !important;
    }
    
    div[data-baseweb="select"] li[aria-selected="true"] {
        background: rgba(46,204,113,0.3) !important;
        color: #2ecc71 !important;
    }
    
    .stSelectbox label {
        color: #e2e8f0 !important;
    }
    
    /* ========== BOTÕES COM ANIMAÇÃO E TEXTO CLARO ========== */
    .stButton button {
        background: linear-gradient(135deg, #1e8f4a, #2ecc71);
        border: none;
        border-radius: 40px;
        padding: 12px 24px;
        font-weight: 600;
        font-size: 15px;
        color: white !important;
        transition: all 0.3s cubic-bezier(0.2, 0.9, 0.4, 1.1);
        cursor: pointer;
        box-shadow: 0 4px 15px rgba(46,204,113,0.3);
        width: 100%;
    }
    
    .stButton button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(46,204,113,0.4);
        background: linear-gradient(135deg, #2ecc71, #27ae60);
    }
    
    .stButton button:active {
        transform: translateY(2px);
    }
    
    /* ========== CARDS MAIS COMPACTOS ========== */
    .stContainer, .element-container:has(.stExpander), div[data-testid="stExpander"] {
        background: rgba(255,255,255,0.05);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        border: 1px solid rgba(255,255,255,0.08);
        margin-bottom: 0.8rem;
        transition: all 0.3s ease;
    }
    
    /* Expander header */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, rgba(46,204,113,0.15), rgba(46,204,113,0.05));
        border-radius: 20px;
        font-weight: 600;
        color: #2ecc71 !important;
        padding: 12px 16px;
    }
    
    /* ========== MÉTRICAS BONITAS ========== */
    .metric-card {
        background: linear-gradient(145deg, rgba(255,255,255,0.08), rgba(255,255,255,0.03));
        border-radius: 16px;
        padding: 0.8rem;
        text-align: center;
        border: 1px solid rgba(46,204,113,0.3);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-3px);
        border-color: rgba(46,204,113,0.6);
    }
    
    /* ========== TABS MODERNAS ========== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255,255,255,0.03);
        padding: 4px;
        border-radius: 50px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 40px;
        padding: 8px 16px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #1e8f4a, #2ecc71);
        color: white !important;
    }
    
    /* ========== RESULT CARD ========== */
    .result-card {
        background: linear-gradient(145deg, rgba(46,204,113,0.12), rgba(255,255,255,0.04));
        border: 1px solid rgba(46,204,113,0.4);
        border-radius: 20px;
        padding: 1.5rem;
        margin-top: 1rem;
    }
    
    /* ========== DIAGNÓSTICO CARD ========== */
    .diagnostico-card {
        background: linear-gradient(135deg, rgba(46,204,113,0.1), rgba(46,204,113,0.05));
        border-left: 4px solid #2ecc71;
        border-radius: 16px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    /* ========== ANIMAÇÕES ========== */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeInUp 0.4s ease;
    }
    
    /* ========== SCROLLBAR ========== */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255,255,255,0.05);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #2ecc71, #1e8f4a);
        border-radius: 10px;
    }
    
    /* ========== DATA FRAME ========== */
    .stDataFrame, .stTable {
        background: rgba(255,255,255,0.03);
        border-radius: 16px;
        overflow: hidden;
    }
    
    /* ========== ALERTAS ========== */
    .stAlert {
        border-radius: 16px;
        border-left: 4px solid #2ecc71;
        background: rgba(46,204,113,0.1);
    }
    
    /* ========== HERO BANNER MAIS COMPACTO ========== */
    .hero-banner {
        background: linear-gradient(135deg, rgba(46,204,113,0.12), rgba(46,204,113,0.04));
        border: 1px solid rgba(46,204,113,0.3);
        border-radius: 24px;
        padding: 1rem;
        text-align: center;
        margin-bottom: 1rem;
        backdrop-filter: blur(10px);
    }
    
    .hero-banner h1 {
        font-size: 1.8rem;
        margin-bottom: 0.25rem;
    }
    
    .hero-banner p {
        font-size: 0.9rem;
        opacity: 0.8;
    }
    
    /* ========== BADGE DE REFERÊNCIA ========== */
    .reference-badge {
        display: inline-block;
        background: rgba(46,204,113,0.2);
        border: 1px solid rgba(46,204,113,0.5);
        border-radius: 20px;
        padding: 2px 10px;
        font-size: 0.7rem;
        color: #2ecc71;
        margin-right: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# CABEÇALHO HERO - MAIS COMPACTO
# ============================================================================

st.markdown("""
<div class="hero-banner">
    <div style="display: flex; align-items: center; justify-content: center; gap: 20px; margin-bottom: 10px;">
        <svg width="60" height="60" viewBox="0 0 60 60" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="30" cy="30" r="28" stroke="#2ecc71" stroke-width="1.5" fill="none"/>
            <circle cx="30" cy="30" r="22" stroke="#27ae60" stroke-width="1" fill="none" stroke-dasharray="4 3"/>
            <path d="M30 8 L30 15" stroke="#2ecc71" stroke-width="2" stroke-linecap="round"/>
            <path d="M30 45 L30 52" stroke="#2ecc71" stroke-width="2" stroke-linecap="round"/>
            <path d="M8 30 L15 30" stroke="#2ecc71" stroke-width="2" stroke-linecap="round"/>
            <path d="M45 30 L52 30" stroke="#2ecc71" stroke-width="2" stroke-linecap="round"/>
            <path d="M14 14 L19 19" stroke="#2ecc71" stroke-width="1.5" stroke-linecap="round"/>
            <path d="M41 41 L46 46" stroke="#2ecc71" stroke-width="1.5" stroke-linecap="round"/>
            <path d="M46 14 L41 19" stroke="#2ecc71" stroke-width="1.5" stroke-linecap="round"/>
            <path d="M19 41 L14 46" stroke="#2ecc71" stroke-width="1.5" stroke-linecap="round"/>
            <circle cx="30" cy="30" r="3" fill="#2ecc71"/>
            <path d="M30 27 L30 33" stroke="#1e8f4a" stroke-width="1.5" stroke-linecap="round"/>
            <path d="M27 30 L33 30" stroke="#1e8f4a" stroke-width="1.5" stroke-linecap="round"/>
        </svg>
        <h1 style="margin: 0; font-size: 3rem; letter-spacing: 2px; background: linear-gradient(135deg, #2ecc71, #1e8f4a); -webkit-background-clip: text; background-clip: text; color: transparent;">
            TELLURIUM
        </h1>
    </div>
    <p style="margin: 0; font-size: 0.9rem; opacity: 0.9;">Classificador Inteligente de Fertilidade do Solo</p>
    <p style="margin-top: 8px; font-size: 0.75rem; opacity: 0.7;">SiBCS • Embrapa • CFSEMG • Boletim 100 • Recomendações Regionais</p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# SIDEBAR - MENU MAIS LIMPO
# ============================================================================

with st.sidebar:
    st.image(
        "https://cdn-icons-png.flaticon.com/512/2909/2909763.png",
        width=70
    )
    
    st.markdown("### 🌱 Sistema Inteligente")
    st.markdown("""
    • Avaliação da fertilidade  
    • Cálculo de V% e m%  
    • Classificação SiBCS  
    • Relatório técnico  
    • IA Gemini integrada  
    """)
    
    st.markdown("---")
    st.markdown("### 📚 Bases Técnicas")
    st.markdown("""
    <span class="reference-badge">Embrapa</span>
    <span class="reference-badge">CFSEMG</span>
    <span class="reference-badge">Boletim 100</span>
    <span class="reference-badge">Regionais</span>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Seletor de região para recomendações regionais
    uf_selecionada = st.selectbox(
        "📍 Selecione seu estado/região",
        ["SP", "MG", "RS", "SC", "PR", "MT", "GO", "BA", "NORDESTE", "NORTE"],
        index=0
    )
    st.session_state.uf_selecionada = uf_selecionada
    
    st.markdown("---")
    
    if st.button("🔧 Testar Conexão API", use_container_width=True):
        with st.spinner("Testando..."):
            modelos = listar_modelos_disponiveis()
            if modelos:
                st.success("✅ API conectada!")
            else:
                st.error("❌ Falha na conexão. Verifique sua API Key.")

# ============================================================================
# SESSION STATE
# ============================================================================

if "dados_basicos" not in st.session_state:
    st.session_state.dados_basicos = {}

if "dados_calculados" not in st.session_state:
    st.session_state.dados_calculados = {}

if "uf_selecionada" not in st.session_state:
    st.session_state.uf_selecionada = "SP"

# ============================================================================
# MENU HORIZONTAL MAIS COMPACTO
# ============================================================================

menu = st.radio(
    "Navegação",
    [
        "📊 1. Dados do Solo",
        "🌱 2. Classificação",
        "🤖 3. Assistente IA",
        "📈 4. Relatório",
        "ℹ️ 5. Métodos",
        "📋 6. Pesquisa"
    ],
    horizontal=True,
    label_visibility="collapsed"
)

# ============================================================================
# CULTURAS (EXPANDIDO)
# ============================================================================

necessidades_culturas = {
    "Alface": {"v_desejado": 80, "n_min": 45, "p_min": 30, "k_min": 0.45, "ph_min": 6.0, "ph_max": 7.0},
    "Algodão": {"v_desejado": 70, "n_min": 40, "p_min": 25, "k_min": 0.4, "ph_min": 5.8, "ph_max": 6.8},
    "Arroz": {"v_desejado": 65, "n_min": 35, "p_min": 20, "k_min": 0.35, "ph_min": 5.5, "ph_max": 6.5},
    "Batata": {"v_desejado": 80, "n_min": 45, "p_min": 30, "k_min": 0.45, "ph_min": 5.5, "ph_max": 6.5},
    "Café": {"v_desejado": 70, "n_min": 40, "p_min": 25, "k_min": 0.4, "ph_min": 5.8, "ph_max": 6.3},
    "Cana-de-açúcar": {"v_desejado": 65, "n_min": 35, "p_min": 20, "k_min": 0.35, "ph_min": 5.5, "ph_max": 6.5},
    "Cebola": {"v_desejado": 75, "n_min": 40, "p_min": 25, "k_min": 0.4, "ph_min": 6.0, "ph_max": 7.0},
    "Cenoura": {"v_desejado": 75, "n_min": 40, "p_min": 25, "k_min": 0.4, "ph_min": 5.8, "ph_max": 6.8},
    "Couve-flor": {"v_desejado": 75, "n_min": 40, "p_min": 25, "k_min": 0.4, "ph_min": 6.0, "ph_max": 7.0},
    "Feijão": {"v_desejado": 65, "n_min": 35, "p_min": 20, "k_min": 0.35, "ph_min": 5.5, "ph_max": 6.5},
    "Mandioca": {"v_desejado": 60, "n_min": 30, "p_min": 15, "k_min": 0.3, "ph_min": 5.0, "ph_max": 6.5},
    "Milheto": {"v_desejado": 60, "n_min": 30, "p_min": 18, "k_min": 0.3, "ph_min": 5.2, "ph_max": 6.2},
    "Milho Grão": {"v_desejado": 70, "n_min": 45, "p_min": 30, "k_min": 0.45, "ph_min": 5.6, "ph_max": 6.8},
    "Milho Semente": {"v_desejado": 75, "n_min": 50, "p_min": 35, "k_min": 0.5, "ph_min": 5.8, "ph_max": 6.8},
    "Pimentão": {"v_desejado": 80, "n_min": 45, "p_min": 30, "k_min": 0.45, "ph_min": 5.8, "ph_max": 6.8},
    "Soja": {"v_desejado": 75, "n_min": 40, "p_min": 25, "k_min": 0.4, "ph_min": 5.8, "ph_max": 6.5},
    "Sorgo": {"v_desejado": 65, "n_min": 35, "p_min": 20, "k_min": 0.35, "ph_min": 5.5, "ph_max": 6.5},
    "Tomate": {"v_desejado": 85, "n_min": 50, "p_min": 35, "k_min": 0.5, "ph_min": 5.8, "ph_max": 6.8},
    "Trigo": {"v_desejado": 65, "n_min": 35, "p_min": 25, "k_min": 0.4, "ph_min": 5.5, "ph_max": 6.5}
}

# ============================================================================
# FUNÇÕES DE CÁLCULO
# ============================================================================

def calcular_sb(ca, mg, k):
    return ca + mg + k

def calcular_tct_potencial(sb, h_al):
    return sb + h_al

def calcular_v_porcentagem(sb, tct_potencial):
    if tct_potencial == 0:
        return 0
    return (sb / tct_potencial) * 100

def calcular_m_porcentagem(al, sb):
    if (al + sb) == 0:
        return 0
    return (al / (al + sb)) * 100

def classificar_fertilidade(v_porcentagem):
    if v_porcentagem < 50:
        return "Baixa fertilidade (V% < 50)"
    elif v_porcentagem < 70:
        return "Fertilidade média (V% entre 50 e 70)"
    elif v_porcentagem < 85:
        return "Fertilidade boa (V% entre 70 e 85)"
    else:
        return "Fertilidade muito boa (V% > 85)"

# ============================================================================
# FUNÇÃO PARA GERAR DIAGNÓSTICO AMIGÁVEL
# ============================================================================

def gerar_diagnostico(dados, cultura_req):
    """Gera um diagnóstico amigável para o usuário"""
    diagnostico = []
    
    ph_atual = dados.get('ph', 0)
    if ph_atual < cultura_req['ph_min']:
        diagnostico.append(f"🔴 **pH ácido:** {ph_atual:.1f} (ideal: {cultura_req['ph_min']}-{cultura_req['ph_max']}). A calagem ajudará a corrigir.")
    elif ph_atual > cultura_req['ph_max']:
        diagnostico.append(f"🟡 **pH alcalino:** {ph_atual:.1f} (ideal: {cultura_req['ph_min']}-{cultura_req['ph_max']}). Pode afetar disponibilidade de nutrientes.")
    else:
        diagnostico.append(f"🟢 **pH adequado:** {ph_atual:.1f} dentro da faixa ideal.")
    
    v_atual = dados.get('v_porcentagem', 0)
    if v_atual < cultura_req['v_desejado']:
        diagnostico.append(f"🔴 **Saturação por bases baixa:** {v_atual:.1f}% (ideal: ≥{cultura_req['v_desejado']}%). Solo precisa de calagem.")
    else:
        diagnostico.append(f"🟢 **Saturação por bases adequada:** {v_atual:.1f}% (ideal: ≥{cultura_req['v_desejado']}%).")
    
    n_atual = dados.get('nitrogen', 0)
    if n_atual < cultura_req['n_min']:
        diagnostico.append(f"🔴 **Nitrogênio baixo:** {n_atual} mg/dm³ (mínimo: {cultura_req['n_min']}). Adubação nitrogenada necessária.")
    else:
        diagnostico.append(f"🟢 **Nitrogênio adequado:** {n_atual} mg/dm³.")
    
    p_atual = dados.get('phosphorus', 0)
    if p_atual < cultura_req['p_min']:
        diagnostico.append(f"🔴 **Fósforo baixo:** {p_atual} mg/dm³ (mínimo: {cultura_req['p_min']}). Adubação fosfatada necessária.")
    else:
        diagnostico.append(f"🟢 **Fósforo adequado:** {p_atual} mg/dm³.")
    
    k_atual = dados.get('potassium', 0)
    if k_atual < cultura_req['k_min']:
        diagnostico.append(f"🔴 **Potássio baixo:** {k_atual:.2f} cmolc/dm³ (mínimo: {cultura_req['k_min']}). Adubação potássica necessária.")
    else:
        diagnostico.append(f"🟢 **Potássio adequado:** {k_atual:.2f} cmolc/dm³.")
    
    return diagnostico

# ============================================================================
# FUNÇÕES DE RECOMENDAÇÃO DE ADUBAÇÃO E CALAGEM
# ============================================================================

def calcular_necessidade_calagem(v_atual, v_desejado, ctc, prnt=85):
    """Calcula a necessidade de calagem em t/ha com PRNT personalizável"""
    if v_atual >= v_desejado:
        return 0, "✅ Solo já atingiu V% desejado. Não necessita calagem.", 0
    
    f = 100 / prnt
    nc = (ctc * (v_desejado - v_atual) / 100) * f
    nc = round(nc * 2) / 2
    
    if nc <= 1.0:
        tempo_espera = 30
    elif nc <= 2.0:
        tempo_espera = 45
    elif nc <= 4.0:
        tempo_espera = 60
    else:
        tempo_espera = 90
    
    if nc > 0:
        recomendacao = f"🔹 **Calagem necessária:** {nc:.1f} t/ha de calcário (PRNT {prnt}%)"
        if nc > 5:
            recomendacao += " - Aplicar parcelado em 2 anos"
        return nc, recomendacao, tempo_espera
    else:
        return 0, "Calagem não necessária", 0

def recomendar_adubacao_nitrogenio(cultura, n_atual, n_min):
    if n_atual >= n_min:
        return "✅ N adequado. Adubação de manutenção: 30-50 kg/ha de N"
    
    deficiencia = n_min - n_atual
    
    if cultura in ["Tomate", "Alface", "Batata", "Milho Semente"]:
        kg_ha = deficiencia + 60
        recomendacao = f"Alta demanda. Aplicar {kg_ha:.0f} kg/ha de N"
    elif cultura in ["Café", "Cana-de-açúcar", "Milho Grão"]:
        kg_ha = deficiencia + 40
        recomendacao = f"Média demanda. Aplicar {kg_ha:.0f} kg/ha de N"
    else:
        kg_ha = deficiencia + 20
        recomendacao = f"Baixa demanda. Aplicar {kg_ha:.0f} kg/ha de N"
    
    return f"❌ N baixo ({n_atual} < {n_min}). {recomendacao}"

def recomendar_adubacao_fosforo(cultura, p_atual, p_min):
    if p_atual >= p_min:
        return "✅ P adequado. Adubação de manutenção: 40-80 kg/ha de P2O5"
    
    deficiencia = p_min - p_atual
    
    if cultura in ["Tomate", "Batata", "Soja"]:
        kg_ha = deficiencia + 80
        recomendacao = f"Alta demanda. Aplicar {kg_ha:.0f} kg/ha de P2O5"
    elif cultura in ["Café", "Cana-de-açúcar"]:
        kg_ha = deficiencia + 60
        recomendacao = f"Média demanda. Aplicar {kg_ha:.0f} kg/ha de P2O5"
    else:
        kg_ha = deficiencia + 40
        recomendacao = f"Baixa demanda. Aplicar {kg_ha:.0f} kg/ha de P2O5"
    
    return f"❌ P baixo ({p_atual} < {p_min}). {recomendacao}"

def recomendar_adubacao_potassio(cultura, k_atual, k_min):
    if k_atual >= k_min:
        return "✅ K adequado. Adubação de manutenção: 40-60 kg/ha de K2O"
    
    deficiencia = k_min - k_atual
    
    if cultura in ["Tomate", "Batata", "Café", "Cana-de-açúcar"]:
        kg_ha = deficiencia + 60
        recomendacao = f"Alta demanda. Aplicar {kg_ha:.0f} kg/ha de K2O"
    elif cultura in ["Soja", "Milho Grão", "Algodão"]:
        kg_ha = deficiencia + 40
        recomendacao = f"Média demanda. Aplicar {kg_ha:.0f} kg/ha de K2O"
    else:
        kg_ha = deficiencia + 30
        recomendacao = f"Baixa demanda. Aplicar {kg_ha:.0f} kg/ha de K2O"
    
    return f"❌ K baixo ({k_atual:.2f} < {k_min:.2f}). {recomendacao}"

# ============================================================================
# ABA 1 - DADOS DO SOLO (CAMPOS MAIS COMPACTOS)
# ============================================================================

if menu == "📊 1. Dados do Solo":
    st.markdown("### 📋 Dados Básicos do Solo")
    st.caption("Preencha os campos abaixo com os resultados da análise de solo")

    col1, col2 = st.columns(2)

    with col1:
        with st.container(border=True):
            st.markdown("**📊 Parâmetros Químicos**")
            nitrogen = st.text_input("🌱 Nitrogênio (mg/dm³)", value="30")
            phosphorus = st.text_input("🔴 Fósforo (mg/dm³)", value="20")
            potassium = st.text_input("🟡 Potássio (cmolc/dm³)", value="0.25")
            ph = st.text_input("🧪 pH (água)", value="6.0")

    with col2:
        with st.container(border=True):
            st.markdown("**⚗️ Cátions e Acidez**")
            aluminum = st.text_input("⚠️ Alumínio (cmolc/dm³)", value="0.5")
            calcium = st.text_input("🥛 Cálcio (cmolc/dm³)", value="3.0")
            magnesium = st.text_input("🧂 Magnésio (cmolc/dm³)", value="1.5")
            h_al = st.text_input("📊 H + Al (cmolc/dm³)", value="3.5")
            
            st.markdown("**🌾 Matéria Orgânica**")
            organic_matter = st.text_input("🌱 Matéria Orgânica (g/kg)", value="25.0")

    with st.container(border=True):
        st.markdown("**🏞️ Textura do Solo**")
        st.caption("⚠️ A soma de Areia + Silte + Argila deve ser igual a 100%")
        col3, col4, col5 = st.columns(3)
        with col3:
            sand = st.number_input("🏖️ Areia (%)", min_value=0, max_value=100, value=35, step=5)
        with col4:
            silt = st.number_input("🏞️ Silte (%)", min_value=0, max_value=100, value=30, step=5)
        with col5:
            clay = st.number_input("🧱 Argila (%)", min_value=0, max_value=100, value=35, step=5)
        
        # Validação da soma da textura
        soma_textura = sand + silt + clay
        if soma_textura != 100:
            st.warning(f"⚠️ **Atenção:** A soma das frações é {soma_textura}%. O ideal é 100%. Ajuste os valores.")
        else:
            st.success(f"✅ Textura válida! Areia: {sand}%, Silte: {silt}%, Argila: {clay}%")
    
    st.caption("💡 Após salvar os dados, vá para a aba 'Classificação' para ver as recomendações.")

    if st.button("✅ SALVAR DADOS", use_container_width=True):
        # Verificar textura antes de salvar
        soma_textura = sand + silt + clay
        if soma_textura != 100:
            st.error(f"❌ **Erro na textura do solo:** A soma das frações é {soma_textura}%, mas deve ser exatamente 100%. Corrija os valores antes de salvar.")
        else:
            with st.spinner("💾 Salvando e processando dados..."):
                time.sleep(0.5)
                try:
                    dados = {
                        "nitrogen": float(nitrogen),
                        "phosphorus": float(phosphorus),
                        "potassium": float(potassium),
                        "ph": float(ph),
                        "aluminum": float(aluminum),
                        "calcium": float(calcium),
                        "magnesium": float(magnesium),
                        "h_al": float(h_al),
                        "organic_matter": float(organic_matter) if organic_matter else 25.0,
                        "sand": sand,
                        "silt": silt,
                        "clay": clay,
                        "materia_organica": float(organic_matter) if organic_matter else 25.0
                    }
                    
                    sb = calcular_sb(dados["calcium"], dados["magnesium"], dados["potassium"])
                    ctc = calcular_tct_potencial(sb, dados["h_al"])
                    v = calcular_v_porcentagem(sb, ctc)
                    m = calcular_m_porcentagem(dados["aluminum"], sb)
                    
                    dados["sb"] = sb
                    dados["ctc"] = ctc
                    dados["v_porcentagem"] = v
                    dados["m_porcentagem"] = m
                    
                    st.session_state.dados_basicos = dados
                    
                    st.success("✅ Dados salvos com sucesso! Vá para a aba **Classificação**.")
                    
                    st.markdown("### 📊 Resumo dos Cálculos")
                    col_a, col_b, col_c, col_d = st.columns(4)
                    with col_a:
                        st.metric("SB (Soma de Bases)", f"{sb:.2f} cmolc/dm³")
                    with col_b:
                        st.metric("CTC (Potencial)", f"{ctc:.2f} cmolc/dm³")
                    with col_c:
                        st.metric("V% (Saturação)", f"{v:.1f}%")
                    with col_d:
                        st.metric("m% (Alumínio)", f"{m:.1f}%")
                        
                except ValueError:
                    st.error("❌ Erro: Verifique se todos os valores são números válidos!")

# ============================================================================
# ABA 2 - CLASSIFICAÇÃO (COM MÚLTIPLAS BASES DE FERTILIDADE)
# ============================================================================

elif menu == "🌱 2. Classificação":
    st.markdown("### 🌱 Classificação e Recomendações")
    
    if not st.session_state.dados_basicos:
        st.warning("⚠️ Por favor, vá até a aba 'Dados do Solo' e insira as informações primeiro!")
    else:
        dados = st.session_state.dados_basicos
        
        # Métricas principais
        col_metric1, col_metric2, col_metric3, col_metric4, col_metric5 = st.columns(5)
        with col_metric1:
            st.metric("pH", f"{dados.get('ph', 'N/A')}")
        with col_metric2:
            st.metric("V%", f"{dados.get('v_porcentagem', 0):.1f}%")
        with col_metric3:
            st.metric("m%", f"{dados.get('m_porcentagem', 0):.1f}%")
        with col_metric4:
            st.metric("N", f"{dados.get('nitrogen', 'N/A')} mg/dm³")
        with col_metric5:
            st.metric("P", f"{dados.get('phosphorus', 'N/A')} mg/dm³")
        
        # Exibir textura do solo
        st.info(f"🏞️ **Textura do solo:** Areia: {dados.get('sand', 0)}% | Silte: {dados.get('silt', 0)}% | Argila: {dados.get('clay', 0)}%")
        
        # ========== INTERPRETAÇÃO POR MÚLTIPLAS BASES ==========
        st.markdown("### 📊 Interpretação por Múltiplas Bases Técnicas")
        
        # Tabs para as diferentes metodologias
        tab_embrapa, tab_cfsemg, tab_regional = st.tabs([
            "🌿 Embrapa", 
            "📘 CFSEMG", 
            f"📍 {st.session_state.uf_selecionada} - Recomendações Regionais"
        ])
        
        with tab_embrapa:
            st.markdown("**Interpretação segundo a Embrapa (Empresa Brasileira de Pesquisa Agropecuária)**")
            
            interpretacoes = interpretar_fertilidade_multiplas_bases(dados)
            
            col_e1, col_e2 = st.columns(2)
            with col_e1:
                st.markdown(f"""
                | Parâmetro | Classificação Embrapa |
                |-----------|----------------------|
                | **pH** | {interpretacoes['embrapa'].get('pH', 'N/A')} |
                | **Fósforo (P)** | {interpretacoes['embrapa'].get('Fósforo', 'N/A')} |
                | **Potássio (K)** | {interpretacoes['embrapa'].get('Potássio', 'N/A')} |
                | **V%** | {interpretacoes['embrapa'].get('V%', 'N/A')} |
                """)
            with col_e2:
                if interpretacoes['embrapa'].get('Matéria Orgânica', 'N/A') != 'N/A':
                    st.markdown(f"""
                    | Parâmetro | Classificação Embrapa |
                    |-----------|----------------------|
                    | **Matéria Orgânica** | {interpretacoes['embrapa'].get('Matéria Orgânica', 'N/A')} |
                    """)
            
            st.caption("📚 Fonte: Embrapa - Manual de Métodos de Análise de Solo")
        
        with tab_cfsemg:
            st.markdown("**Interpretação segundo a CFSEMG (Comissão de Fertilidade do Solo do Estado de Minas Gerais)**")
            
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                st.markdown(f"""
                | Parâmetro | Classificação CFSEMG |
                |-----------|----------------------|
                | **pH** | {interpretacoes['cfsemg'].get('pH', 'N/A')} |
                | **Fósforo (P)** | {interpretacoes['cfsemg'].get('Fósforo', 'N/A')} |
                | **Potássio (K)** | {interpretacoes['cfsemg'].get('Potássio', 'N/A')} |
                | **V%** | {interpretacoes['cfsemg'].get('V%', 'N/A')} |
                """)
            
            st.caption("📚 Fonte: CFSEMG - 5ª Aproximação - Recomendações para uso de corretivos e fertilizantes em Minas Gerais")
        
        with tab_regional:
            st.markdown(f"**Recomendações específicas para {st.session_state.uf_selecionada}**")
            
            recomendacoes_reg = recomendar_por_regiao(st.session_state.uf_selecionada, dados)
            for rec in recomendacoes_reg:
                st.markdown(rec)
        
        st.markdown("---")
        
        v = dados.get('v_porcentagem', 0)
        classificacao = classificar_fertilidade(v)
        st.info(f"📌 **Classificação geral do solo (SiBCS):** {classificacao}")
        
        st.markdown("---")
        
        st.markdown("### 🌾 Selecione a Cultura")
        cultura = st.selectbox("Cultura planejada", list(necessidades_culturas.keys()))
        
        if cultura:
            req = necessidades_culturas[cultura]
            
            # ========== DIAGNÓSTICO AMIGÁVEL ==========
            st.markdown("### 📋 Diagnóstico do Solo para a Cultura Selecionada")
            diagnostico = gerar_diagnostico(dados, req)
            
            with st.container(border=True):
                for diag in diagnostico:
                    st.markdown(diag)
            
            st.markdown("---")
            
            # TABS CORRIGIDAS (CALAGEM, ADUBAÇÃO, MANEJO FUNCIONANDO)
            aba1, aba2, aba3 = st.tabs(["🧪 Calagem", "🌱 Adubação", "📝 Manejo Geral"])
            
            with aba1:
                st.markdown("#### 🧪 Recomendação de Calagem")
                
                ctc = dados.get('ctc', 0)
                v_atual = dados.get('v_porcentagem', 0)
                
                col_prnt1, col_prnt2 = st.columns([2, 1])
                with col_prnt1:
                    prnt_calcario = st.slider(
                        "PRNT do Calcário (%)", 
                        min_value=50, 
                        max_value=100, 
                        value=85, 
                        step=5,
                        help="Poder Relativo de Neutralização Total. Quanto menor o PRNT, maior a quantidade necessária."
                    )
                with col_prnt2:
                    st.metric("Fator de correção", f"{100/prnt_calcario:.2f}")
                
                nc, rec_calagem, tempo_espera = calcular_necessidade_calagem(v_atual, req['v_desejado'], ctc, prnt_calcario)
                
                st.info(f"**V% atual:** {v_atual:.1f}% | **V% desejado:** {req['v_desejado']}% | **CTC:** {ctc:.2f} cmolc/dm³")
                
                if nc > 0:
                    st.success(f"### {rec_calagem}")
                    
                    st.markdown("**📋 Detalhamento da Calagem:**")
                    col_det1, col_det2, col_det3 = st.columns(3)
                    with col_det1:
                        st.metric("Necessidade", f"{nc:.1f} t/ha de calcário")
                    with col_det2:
                        st.metric("PRNT considerado", f"{prnt_calcario}%")
                    with col_det3:
                        st.metric("Tempo de espera mínimo", f"{tempo_espera} dias")
                    
                    st.markdown("---")
                    with st.expander("⏰ Ver tabela de tempo de espera por dose"):
                        st.markdown("""
                        | Dose de calcário (t/ha) | Tempo de espera mínimo |
                        |------------------------|----------------------|
                        | Até 1.0 t/ha | 30 dias |
                        | 1.1 - 2.0 t/ha | 45 dias |
                        | 2.1 - 4.0 t/ha | 60 dias |
                        | Acima de 4.0 t/ha | 90 dias (parcelar) |
                        """)
                else:
                    st.success(rec_calagem)
            
            with aba2:
                st.markdown("#### 🌱 Recomendação de Adubação")
                
                with st.container(border=True):
                    st.markdown("**Nitrogênio (N)**")
                    n_atual = dados.get('nitrogen', 0)
                    n_recomendacao = recomendar_adubacao_nitrogenio(cultura, n_atual, req['n_min'])
                    
                    if "✅" in n_recomendacao:
                        st.success(n_recomendacao)
                    else:
                        st.warning(n_recomendacao)
                        # Extrair o valor de kg/ha da recomendação
                        import re
                        match = re.search(r'Aplicar (\d+) kg/ha', n_recomendacao)
                        if match:
                            kg_n = int(match.group(1))
                            st.info(f"**📌 Forma de aplicação do Nitrogênio (parcelamento):**")
                            st.markdown(f"""
                            - **Parcelamento recomendado:** Aplicar em **3 vezes**
                            - 1ª parcela (plantio): {max(20, kg_n // 3)} kg/ha
                            - 2ª parcela (30-40 dias após emergência): {max(20, kg_n // 3)} kg/ha  
                            - 3ª parcela (60-70 dias após emergência): {kg_n - 2 * max(20, kg_n // 3)} kg/ha
                            - **Evitar aplicação em superfície sem incorporação** para reduzir perdas por volatilização
                            """)
                
                with st.container(border=True):
                    st.markdown("**Fósforo (P)**")
                    p_atual = dados.get('phosphorus', 0)
                    p_recomendacao = recomendar_adubacao_fosforo(cultura, p_atual, req['p_min'])
                    
                    if "✅" in p_recomendacao:
                        st.success(p_recomendacao)
                    else:
                        st.warning(p_recomendacao)
                        match = re.search(r'Aplicar (\d+) kg/ha', p_recomendacao)
                        if match:
                            kg_p = int(match.group(1))
                            st.info(f"**📌 Forma de aplicação do Fósforo:**")
                            st.markdown(f"""
                            - **Aplicação:** Total na **semeadura/plantio** (100% da dose)
                            - **Profundidade:** Aplicar a **5-10 cm de profundidade** na linha de semeadura
                            - **Observação:** O fósforo tem baixa mobilidade no solo, por isso deve ser aplicado próximo às raízes
                            """)
                
                with st.container(border=True):
                    st.markdown("**Potássio (K)**")
                    k_atual = dados.get('potassium', 0)
                    k_recomendacao = recomendar_adubacao_potassio(cultura, k_atual, req['k_min'])
                    
                    if "✅" in k_recomendacao:
                        st.success(k_recomendacao)
                    else:
                        st.warning(k_recomendacao)
                        match = re.search(r'Aplicar (\d+) kg/ha', k_recomendacao)
                        if match:
                            kg_k = int(match.group(1))
                            st.info(f"**📌 Forma de aplicação do Potássio:**")
                            st.markdown(f"""
                            - **Parcelamento recomendado:** Aplicar em **2 vezes**
                            - 1ª parcela (plantio): {kg_k // 2} kg/ha
                            - 2ª parcela (cobertura): {kg_k - kg_k // 2} kg/ha (30-40 dias após emergência)
                            - **Evitar excesso** que pode causar salinidade e prejudicar a germinação
                            """)

# ============================================================================
# ABA 3 - IA
# ============================================================================

elif menu == "🤖 3. Assistente IA":
    st.markdown("### 🤖 Assistente IA Gemini")
    st.markdown("""
    <span class="reference-badge">Embrapa</span>
    <span class="reference-badge">CFSEMG</span>
    <span class="reference-badge">Boletim 100</span>
    <span class="reference-badge">Regionais</span>
    """, unsafe_allow_html=True)
    st.caption("Faça perguntas sobre fertilidade do solo, manejo, culturas e práticas agrícolas - Baseado nas principais referências brasileiras")

    if not st.session_state.dados_basicos:
        st.info("ℹ️ Amigo Agricultor, para melhores respostas, preencha os dados do solo na aba 'Dados do Solo' primeiro!")

    pergunta = st.text_area(
        "💬 Faça sua pergunta sobre fertilidade do solo, manejo ou culturas:",
        height=100,
        placeholder="Exemplo: Qual a recomendação de calagem para um solo com pH 5.0? Como interpretar o V% segundo a Embrapa?"
    )

    if st.button("🚀 GERAR RESPOSTA", use_container_width=True):
        if not pergunta:
            st.warning("⚠️ Por favor, digite uma pergunta!")
        else:
            with st.spinner("🤖 Consultando IA Gemini. Analisando seus dados..."):
                resposta = gerar_resposta_ia(
                    pergunta,
                    st.session_state.dados_basicos if st.session_state.dados_basicos else None
                )
                
                st.markdown(f"""
                <div class="result-card">
                    <h3 style="text-align: center; margin-bottom: 1rem;">🤖 Resposta da IA</h3>
                    <div style="margin-top: 10px;">
                        {resposta}
                    </div>
                </div>
                """, unsafe_allow_html=True)

# ============================================================================
# ABA 4 - RELATÓRIO
# ============================================================================

elif menu == "📈 4. Relatório":
    st.markdown("### 📈 Relatório Técnico")

    if st.session_state.dados_basicos:
        dados = st.session_state.dados_basicos
        
        relatorio_data = {
            "Parâmetro": [
                "Nitrogênio (N)", "Fósforo (P)", "Potássio (K)",
                "pH", "Alumínio (Al)", "Cálcio (Ca)", "Magnésio (Mg)",
                "H + Al", "Matéria Orgânica", "Areia (%)", "Silte (%)", "Argila (%)",
                "Soma de Bases (SB)", "CTC Potencial", "V (%)", "m (%)"
            ],
            "Valor": [
                f"{dados.get('nitrogen', 'N/A')} mg/dm³",
                f"{dados.get('phosphorus', 'N/A')} mg/dm³",
                f"{dados.get('potassium', 'N/A')} cmolc/dm³",
                f"{dados.get('ph', 'N/A')}",
                f"{dados.get('aluminum', 'N/A')} cmolc/dm³",
                f"{dados.get('calcium', 'N/A')} cmolc/dm³",
                f"{dados.get('magnesium', 'N/A')} cmolc/dm³",
                f"{dados.get('h_al', 'N/A')} cmolc/dm³",
                f"{dados.get('organic_matter', 'N/A')} g/kg",
                f"{dados.get('sand', 'N/A')}%",
                f"{dados.get('silt', 'N/A')}%",
                f"{dados.get('clay', 'N/A')}%",
                f"{dados.get('sb', 0):.2f} cmolc/dm³",
                f"{dados.get('ctc', 0):.2f} cmolc/dm³",
                f"{dados.get('v_porcentagem', 0):.1f}%",
                f"{dados.get('m_porcentagem', 0):.1f}%"
            ]
        }
        
        relatorio = pd.DataFrame(relatorio_data)
        
        st.dataframe(relatorio, use_container_width=True, hide_index=True)
        
        csv = relatorio.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Baixar Relatório (CSV)",
            data=csv,
            file_name="relatorio_solo.csv",
            mime="text/csv"
        )
        
        st.markdown("---")
        st.markdown("### 📚 Referências Técnicas Utilizadas")
        st.markdown("""
        | Código | Referência |
        |--------|------------|
        | **Embrapa** | Empresa Brasileira de Pesquisa Agropecuária - Manual de Métodos de Análise de Solo |
        | **CFSEMG** | Comissão de Fertilidade do Solo do Estado de Minas Gerais - 5ª Aproximação |
        | **Boletim 100** | IAC - Instituto Agronômico de Campinas - Boletim Técnico 100 |
        | **Regionais** | Recomendações específicas por estado (CQFS RS/SC, IAPAR PR, Embrapa Cerrados, etc.) |
        | **SiBCS** | Sistema Brasileiro de Classificação de Solos |
        """)
    else:
        st.info("ℹ️ Nenhum dado cadastrado. Vá até a aba 'Dados do Solo' para inserir as informações.")

# ============================================================================
# ABA 5 - MÉTODOS
# ============================================================================

elif menu == "ℹ️ 5. Métodos":
    st.markdown("### ℹ️ Métodos Utilizados")
    
    with st.container(border=True):
        st.markdown("""
        ### 📐 Fórmulas e Interpretações
        
        | Parâmetro | Fórmula | Interpretação |
        |-----------|---------|---------------|
        | **Soma de Bases (SB)** | SB = Ca²⁺ + Mg²⁺ + K⁺ (cmolc/dm³) | Indica a quantidade de cátions básicos |
        | **CTC Potencial (T)** | T = SB + (H+Al) (cmolc/dm³) | Capacidade máxima de troca catiônica |
        | **Saturação por Bases (V%)** | V% = (SB/T) × 100 | Fertilidade do solo |
        | **Saturação por Alumínio (m%)** | m% = (Al³⁺ / (Al³⁺ + SB)) × 100 | Toxicidade por alumínio |
        """)
    
    with st.container(border=True):
        st.markdown("""
        ### 🌡️ Classificação do V% (SiBCS)
        
        - **V% < 50%** → Baixa fertilidade (solos ácidos)
        - **50% ≤ V% < 70%** → Fertilidade média
        - **70% ≤ V% < 85%** → Fertilidade boa
        - **V% ≥ 85%** → Fertilidade muito boa
        """)
    
    with st.container(border=True):
        st.markdown("""
        ### 📚 Bases de Fertilidade do Solo Incorporadas
        
        | Base Técnica | Abrangência | Principais Parâmetros |
        |--------------|-------------|----------------------|
        | **Embrapa** | Nacional | pH, P, K, V%, MO |
        | **CFSEMG** | Minas Gerais | pH, P-resina, K, V% |
        | **Boletim 100** | São Paulo | pH CaCl2, P-resina, V% |
        | **CQFS RS/SC** | Sul do Brasil | pH, P, K, V% |
        | **IAPAR** | Paraná | pH, P, K, V% |
        | **Embrapa Cerrados** | Centro-Oeste | pH, P, K, V%, gessagem |
        | **Embrapa Semiárido** | Nordeste | pH, P, K, V%, sais |
        | **Embrapa Amazônia** | Norte | pH, P, K, V%, acidez |
        """)
    
    with st.container(border=True):
        st.markdown("""
        ### 🧪 pH e Disponibilidade de Nutrientes
        
        - **pH < 5.5** → Alumínio tóxico, baixa disponibilidade de P, Ca, Mg
        - **pH 5.5 - 6.5** → Faixa ideal para maioria das culturas
        - **pH > 6.5** → Pode reduzir disponibilidade de micronutrientes
        """)
    
    with st.container(border=True):
        st.markdown("""
        ### 📚 Referências Bibliográficas
        
        1. **EMBRAPA** - Empresa Brasileira de Pesquisa Agropecuária. Sistema Brasileiro de Classificação de Solos (SiBCS). Brasília, 2018.
        
        2. **CFSEMG** - Comissão de Fertilidade do Solo do Estado de Minas Gerais. Recomendações para o uso de corretivos e fertilizantes em Minas Gerais. 5ª Aproximação. Viçosa, 2020.
        
        3. **IAC** - Instituto Agronômico de Campinas. Boletim Técnico 100: Recomendações de adubação e calagem para o Estado de São Paulo. Campinas, 2020.
        
        4. **CQFS RS/SC** - Comissão de Química e Fertilidade do Solo. Manual de calagem e adubação para os Estados do Rio Grande do Sul e Santa Catarina. Porto Alegre, 2016.
        
        5. **CONAB** - Companhia Nacional de Abastecimento. Manual de Adubação e Calagem para as principais culturas. Brasília, 2021.
        """)
    
    st.markdown("---")
    st.markdown("### 🤖 IA Gemini")
    st.markdown("""
    O assistente utiliza o modelo **Gemini** do Google para:
    - Interpretar laudos de análise de solo
    - Recomendar práticas de manejo
    - Sugerir correções de fertilidade
    - Esclarecer dúvidas sobre nutrição de plantas
    
    **Bases de conhecimento da IA:** Embrapa, CFSEMG, Boletim 100, recomendações regionais
    """)


# ============================================================================
# ABA 6 - PESQUISA DE SATISFAÇÃO
# ============================================================================

elif menu == "📋 6. Pesquisa":
    import os
    from datetime import datetime
    
    st.markdown("### 📋 Pesquisa de Satisfação - Classificador de Fertilidade do Solo")
    st.markdown("Sua opinião é fundamental para melhorarmos a ferramenta!")
    st.markdown("---")
    
    # ========== FORMULÁRIO PARA TODOS OS USUÁRIOS ==========
    
    if "pesquisa_respondida" not in st.session_state:
        st.session_state.pesquisa_respondida = False
    
    if not st.session_state.pesquisa_respondida:
        
        with st.form("pesquisa_form"):
            st.markdown("#### 1. Avaliação da Plataforma")
            nota_plataforma = st.slider(
                "De 0 a 10, qual a nota pela funcionalidade da plataforma?",
                min_value=0, max_value=10, value=5, step=1
            )
            
            st.markdown("---")
            st.markdown("#### 2. Didática da Interpretação")
            nota_didatica = st.slider(
                "De 0 a 10, o quão didático foi a interpretação dos dados?",
                min_value=0, max_value=10, value=5, step=1
            )
            
            st.markdown("---")
            st.markdown("#### 3. Uso Acadêmico")
            
            col_estudante, col_nota = st.columns([1, 2])
            with col_estudante:
                eh_estudante = st.checkbox("Sou estudante/pesquisador")
            
            with col_nota:
                if eh_estudante:
                    nota_academico = st.slider(
                        "De 0 a 10, qual a probabilidade de utilizar a ferramenta para fins acadêmicos?",
                        min_value=0, max_value=10, value=5, step=1
                    )
                else:
                    nota_academico = "Não se aplica (não sou estudante)"
                    st.info("✅ Você marcou que não é estudante. Esta pergunta não se aplica.")
            
            st.markdown("---")
            st.markdown("#### 4. Uso em Propriedade Rural")
            
            col_produtor, col_nota2 = st.columns([1, 2])
            with col_produtor:
                eh_produtor = st.checkbox("Sou produtor rural")
            
            with col_nota2:
                if eh_produtor:
                    nota_produtor = st.slider(
                        "De 0 a 10, qual a probabilidade de usar esta ferramenta em sua propriedade rural?",
                        min_value=0, max_value=10, value=5, step=1
                    )
                else:
                    nota_produtor = "Não se aplica (não sou produtor)"
                    st.info("✅ Você marcou que não é produtor. Esta pergunta não se aplica.")
            
            st.markdown("---")
            st.markdown("#### 5. Classificação do Uso")
            
            classificacao_uso = st.radio(
                "Como você classificaria o uso da ferramenta?",
                ["Fácil", "Médio", "Difícil"],
                horizontal=True
            )
            
            st.markdown("---")
            st.markdown("#### 6. Sugestoes de Aprimoramento")
            
            sugestoes = st.text_area(
                "Sugestoes de aprimoramentos. O que falta ou pode melhorar?",
                placeholder="Ex: Adicionar gráficos, incluir mais culturas, melhorar a explicação do V%...",
                height=100
            )
            
            st.markdown("---")
            
            # Campo para identificacao opcional
            with st.expander("🔒 Identificacao (opcional)"):
                nome = st.text_input("Nome (opcional)")
                email = st.text_input("E-mail (opcional - para contato)")
            
            # Botão de envio
            submitted = st.form_submit_button("📤 ENVIAR PESQUISA", use_container_width=True)
            
            if submitted:
                resposta = {
                    "data_hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "nota_plataforma": nota_plataforma,
                    "nota_didatica": nota_didatica,
                    "eh_estudante": "Sim" if eh_estudante else "Não",
                    "nota_academico": nota_academico,
                    "eh_produtor": "Sim" if eh_produtor else "Não",
                    "nota_produtor": nota_produtor,
                    "classificacao_uso": classificacao_uso,
                    "sugestoes": sugestoes,
                    "nome": nome if nome else "Anônimo",
                    "email": email if email else "Não informado"
                }
                
                arquivo_txt = "pesquisas_satisfacao.txt"
                
                # Formatar resposta para TXT
                texto_resposta = f"""
{'='*60}
NOVA PESQUISA - {resposta['data_hora']}
{'='*60}

1. NOTA DA PLATAFORMA: {resposta['nota_plataforma']}/10

2. DIDÁTICA DA INTERPRETAÇÃO: {resposta['nota_didatica']}/10

3. USO ACADÊMICO:
   - É estudante? {resposta['eh_estudante']}
   - Probabilidade de uso acadêmico: {resposta['nota_academico']}

4. USO EM PROPRIEDADE:
   - É produtor? {resposta['eh_produtor']}
   - Probabilidade de uso na propriedade: {resposta['nota_produtor']}

5. CLASSIFICAÇÃO DO USO: {resposta['classificacao_uso']}

6. SUGESTOES DE APRIMORAMENTO:
   {resposta['sugestoes']}

7. IDENTIFICAÇAO:
   - Nome: {resposta['nome']}
   - E-mail: {resposta['email']}

{'='*60}
"""
                
                # Salvar no arquivo TXT (anexar)
                with open(arquivo_txt, "a", encoding='utf-8') as f:
                    f.write(texto_resposta)
                
                st.session_state.pesquisa_respondida = True
                st.session_state.ultima_pesquisa = resposta
                
                st.success("✅ Pesquisa enviada com sucesso! Muito obrigado pela sua contribuição!")
                
                st.markdown("### 📊 Resumo da sua resposta")
                st.markdown(f"""
                | Pergunta | Resposta |
                |----------|----------|
                | Nota da plataforma | {nota_plataforma}/10 |
                | Didática da interpretação | {nota_didatica}/10 |
                | É estudante? | {"Sim" if eh_estudante else "Não"} |
                | Probabilidade de uso acadêmico | {nota_academico} |
                | É produtor? | {"Sim" if eh_produtor else "Não"} |
                | Probabilidade de uso na propriedade | {nota_produtor} |
                | Classificação do uso | {classificacao_uso} |
                """)
                
                st.info("💾 Sua resposta foi registrada. Obrigado!")
    
    else:
        st.success("✅ Você já respondeu à pesquisa! Muito obrigado pela sua contribuição!")
        st.info("💡 Caso queira dar novas sugestoes, entre em contato pelo e-mail.")
    
    # ========== RELATÓRIO PROTEGIDO POR SENHA (SÓ VOCÊ VÊ) ==========
    st.markdown("---")
    st.markdown("### 🔒 Relatório de Pesquisas (Área Restrita)")
    
    senha_correta = "91959441"  # ← MUDE PARA SUA SENHA
    
    if "relatorio_liberado" not in st.session_state:
        st.session_state.relatorio_liberado = False
    
    if not st.session_state.relatorio_liberado:
        senha = st.text_input("Digite a senha do administrador para acessar o relatório:", type="password")
        if st.button("🔓 Acessar Relatório"):
            if senha == senha_correta:
                st.session_state.relatorio_liberado = True
                st.rerun()
            else:
                st.error("❌ Senha incorreta!")
    else:
        st.success("✅ Modo administrador - Relatório liberado!")
        
        arquivo_txt = "pesquisas_satisfacao.txt"
        
        if os.path.exists(arquivo_txt):
            with open(arquivo_txt, "r", encoding='utf-8') as f:
                conteudo = f.read()
            
            st.text_area("📋 RELATÓRIO COMPLETO", conteudo, height=400)
            
            # Download em TXT
            with open(arquivo_txt, "rb") as f:
                st.download_button(
                    label="📥 Baixar Relatório (TXT)",
                    data=f,
                    file_name="relatorio_pesquisas.txt",
                    mime="text/plain"
                )
        else:
            st.info("ℹ️ Ainda não há nenhuma pesquisa registrada.")
        
        if st.button("🔒 Sair do modo administrador"):
            st.session_state.relatorio_liberado = False
            st.rerun()
# ============================================================================
# RODAPÉ
# ============================================================================

st.markdown("---")

col_rodape1, col_rodape2, col_rodape3 = st.columns([1, 2, 1])
with col_rodape2:
    st.caption("© 2026 - Sistema Inteligente de Fertilidade do Solo | Fins Acadêmicos")
    st.caption("🤖 IA Gemini do Google • 🌱 Metodologias: Embrapa | CFSEMG | Boletim 100 | Regionais")
    st.caption("📧 Contato: [laenor@outlook.com](mailto:laenor@outlook.com)")
