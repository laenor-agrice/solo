# ============================================================================
# IMPORTAÇÕES - VERSÃO SIMPLIFICADA
# ============================================================================
# Importa sys primeiro para resolver o erro
import sys
# Cria módulos fake ANTES de qualquer outra importação
if 'sklearn._loss' not in sys.modules:
    import types
    sys.modules['sklearn._loss'] = types.ModuleType('sklearn._loss')

if 'sklearn.metrics._loss' not in sys.modules:
    import types
    sys.modules['sklearn.metrics._loss'] = types.ModuleType('sklearn.metrics._loss')

# Agora importa o resto
import streamlit as st
import pandas as pd
import requests
import json
import time
import re
import base64
import os
import math
import joblib
import pickle
from datetime import datetime
import importlib
import warnings
import numpy as np

warnings.filterwarnings('ignore')
# ============================================================================
# CONFIGURAÇÃO DA PÁGINA - DESIGN PREMIUM
# ============================================================================

# Icone SVG para fertilidade do solo
svg_icon = """
<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M5 8C8 6 16 6 19 8" stroke="#6D4C41" stroke-width="2" stroke-linecap="round"/>
  <path d="M5 13C8 11 16 11 19 13" stroke="#8D6E63" stroke-width="2" stroke-linecap="round"/>
  <path d="M5 18C8 16 16 16 19 18" stroke="#4E342E" stroke-width="2" stroke-linecap="round"/>
  <circle cx="12" cy="4" r="2" fill="#4CAF50"/>
</svg>
"""

svg_base64 = base64.b64encode(svg_icon.encode()).decode()

st.set_page_config(
    page_title="🌱 Tellurium - Classificador Inteligente de Fertilidade do Solo",
    page_icon=f"data:image/svg+xml;base64,{svg_base64}",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/laenor-agricre/Excel',
        'Report a bug': 'mailto:laenor@outlook.com',
        'About': '### 🌱 Tellurium\nSistema Inteligente de Classificação de Fertilidade do Solo\n\nDesenvolvido com base nas metodologias:\n- Embrapa\n- CFSEMG\n- Boletim 100 IAC\n- Recomendações Regionais'
    }
)

# ============================================================================
# CSS DESIGN PREMIUM - CORES TERRA E VERDE AGRÍCOLA
# ============================================================================

st.markdown("""
<style>
    /* ========== IMPORTAÇÃO DE FONTES ========== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    /* ========== FUNDO PRINCIPAL ========== */
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 25%, #0f3460 50%, #16213e 75%, #1a1a2e 100%);
        background-attachment: fixed;
    }
    
    /* ========== SIDEBAR PREMIUM ========== */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(26,26,46,0.98) 0%, rgba(15,20,40,0.98) 100%);
        backdrop-filter: blur(12px);
        border-right: 1px solid rgba(76,175,80,0.25);
        box-shadow: 4px 0 40px rgba(0,0,0,0.3);
    }
    
    /* ========== TÍTULOS ========== */
    h1, h2, h3, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        background: linear-gradient(135deg, #8D6E63, #6D4C41, #4CAF50);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
    }
    
    h1 {
        font-size: 2.5rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    h2 {
        font-size: 1.6rem !important;
        margin-top: 0.5rem !important;
        border-left: 4px solid #4CAF50;
        padding-left: 15px;
    }
    
    /* ========== TEXTO GERAL ========== */
    p, span, div, label, .stMarkdown, .stText, .stCaption {
        color: #e2e8f0 !important;
        line-height: 1.6;
    }
    
    /* ========== INPUTS ========== */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stDateInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: rgba(255,255,255,0.95) !important;
        border: 1px solid rgba(139,69,19,0.3) !important;
        border-radius: 14px !important;
        padding: 12px 16px !important;
        color: #1a1a2e !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #4CAF50 !important;
        box-shadow: 0 0 0 3px rgba(76,175,80,0.25) !important;
        outline: none !important;
    }
    
    /* ========== SELECTBOX ========== */
    .stSelectbox > div > div {
        background: rgba(20, 20, 40, 0.95) !important;
        border: 1px solid rgba(139,69,19,0.35) !important;
        border-radius: 14px !important;
        color: white !important;
    }
    
    .stSelectbox > div > div > div {
        color: white !important;
    }
    
    div[data-baseweb="select"] > div {
        background: rgba(20, 20, 40, 0.98) !important;
        backdrop-filter: blur(10px);
    }
    
    div[data-baseweb="select"] ul {
        background: rgba(15, 15, 30, 0.98) !important;
        border: 1px solid rgba(76,175,80,0.3);
        border-radius: 12px;
    }
    
    div[data-baseweb="select"] li {
        color: white !important;
        background: transparent !important;
    }
    
    div[data-baseweb="select"] li:hover {
        background: rgba(76,175,80,0.2) !important;
    }
    
    div[data-baseweb="select"] li[aria-selected="true"] {
        background: rgba(76,175,80,0.3) !important;
        color: #4CAF50 !important;
    }
    
    /* ========== BOTÕES ========== */
    .stButton button {
        background: linear-gradient(135deg, #6D4C41, #8D6E63);
        border: none;
        border-radius: 40px;
        padding: 12px 28px;
        font-weight: 600;
        font-size: 15px;
        color: white !important;
        transition: all 0.3s cubic-bezier(0.2, 0.9, 0.4, 1.1);
        cursor: pointer;
        box-shadow: 0 4px 15px rgba(109,76,65,0.3);
        width: 100%;
    }
    
    .stButton button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(76,175,80,0.4);
        background: linear-gradient(135deg, #8D6E63, #4CAF50);
    }
    
    .stButton button:active {
        transform: translateY(2px);
    }
    
    /* ========== CARDS ========== */
    .stContainer, .element-container:has(.stExpander), div[data-testid="stExpander"] {
        background: rgba(255,255,255,0.03);
        backdrop-filter: blur(12px);
        border-radius: 20px;
        border: 1px solid rgba(255,255,255,0.08);
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    
    .stContainer:hover, div[data-testid="stExpander"]:hover {
        border-color: rgba(76,175,80,0.4);
        transform: translateY(-2px);
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    /* Expander header */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, rgba(109,76,65,0.15), rgba(76,175,80,0.05));
        border-radius: 16px;
        font-weight: 600;
        color: #4CAF50 !important;
        padding: 12px 20px;
    }
    
    /* ========== MÉTRICAS ========== */
    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 800 !important;
        background: linear-gradient(135deg, #8D6E63, #4CAF50);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #a0aec0 !important;
        font-size: 0.85rem !important;
        font-weight: 500;
    }
    
    /* ========== TABS ========== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255,255,255,0.05);
        padding: 6px;
        border-radius: 60px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 40px;
        padding: 10px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #6D4C41, #4CAF50);
        color: white !important;
        box-shadow: 0 2px 15px rgba(76,175,80,0.3);
    }
    
    /* ========== RESULT CARD ========== */
    .result-card {
        background: linear-gradient(145deg, rgba(76,175,80,0.1), rgba(109,76,65,0.05));
        border: 1px solid rgba(76,175,80,0.35);
        border-radius: 24px;
        padding: 1.5rem;
        margin-top: 1rem;
        backdrop-filter: blur(8px);
        animation: fadeInUp 0.5s ease;
    }
    
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* ========== DIAGNÓSTICO CARD ========== */
    .diagnostico-card {
        background: linear-gradient(135deg, rgba(76,175,80,0.1), rgba(109,76,65,0.05));
        border-left: 4px solid #4CAF50;
        border-radius: 16px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    /* ========== SCROLLBAR ========== */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255,255,255,0.05);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #8D6E63, #4CAF50);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #6D4C41, #4CAF50);
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
        border-left: 4px solid #4CAF50;
        background: rgba(76,175,80,0.08);
        backdrop-filter: blur(4px);
    }
    
    /* ========== HERO BANNER ========== */
    .hero-banner {
        background: linear-gradient(135deg, rgba(109,76,65,0.15), rgba(76,175,80,0.08));
        border: 1px solid rgba(76,175,80,0.3);
        border-radius: 32px;
        padding: 2rem;
        text-align: center;
        margin-bottom: 2rem;
        backdrop-filter: blur(12px);
        animation: fadeInDown 0.8s ease;
    }
    
    @keyframes fadeInDown {
        from { opacity: 0; transform: translateY(-30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* ========== BADGES ========== */
    .reference-badge {
        display: inline-block;
        background: linear-gradient(135deg, rgba(109,76,65,0.2), rgba(76,175,80,0.1));
        border: 1px solid rgba(76,175,80,0.4);
        border-radius: 30px;
        padding: 4px 14px;
        font-size: 0.7rem;
        font-weight: 500;
        color: #4CAF50;
        margin-right: 8px;
        margin-bottom: 6px;
        transition: all 0.2s ease;
    }
    
    .reference-badge:hover {
        background: rgba(76,175,80,0.2);
        transform: translateY(-1px);
    }
    
    /* ========== FILE UPLOADER ========== */
    .stFileUploader > div > div {
        background: rgba(255,255,255,0.04);
        border: 1px dashed rgba(76,175,80,0.4);
        border-radius: 20px;
        transition: all 0.3s ease;
    }
    
    .stFileUploader > div > div:hover {
        border-color: #4CAF50;
        background: rgba(76,175,80,0.06);
    }
    
    /* ========== STATUS ========== */
    [data-testid="stStatus"] {
        background: rgba(0,0,0,0.85);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        border: 1px solid rgba(76,175,80,0.3);
    }
    
    /* ========== MENU HORIZONTAL ========== */
    .stRadio > div {
        gap: 8px;
        background: rgba(255,255,255,0.04);
        padding: 8px;
        border-radius: 60px;
        backdrop-filter: blur(8px);
    }
    
    .stRadio > div > label {
        background: transparent;
        border-radius: 40px;
        padding: 8px 24px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stRadio > div > label > div > p {
        color: #e2e8f0 !important;
    }
    
    .stRadio > div > label[data-baseweb="radio"]:has(input:checked) {
        background: linear-gradient(135deg, #6D4C41, #4CAF50);
        box-shadow: 0 2px 10px rgba(76,175,80,0.3);
    }
    
    /* ========== EXPANDER ========== */
    .streamlit-expanderHeader {
        font-size: 1rem !important;
    }
    
    /* ========== DIVISORES ========== */
    hr {
        margin: 1.5rem 0;
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(76,175,80,0.5), transparent);
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# CABEÇALHO HERO
# ============================================================================

st.markdown("""
<div class="hero-banner">
    <div style="display: flex; align-items: center; justify-content: center; gap: 20px; margin-bottom: 15px;">
        <svg width="65" height="65" viewBox="0 0 60 60" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="30" cy="30" r="28" stroke="#4CAF50" stroke-width="1.5" fill="none"/>
            <circle cx="30" cy="30" r="22" stroke="#8D6E63" stroke-width="1" fill="none" stroke-dasharray="4 3"/>
            <path d="M30 8 L30 15" stroke="#4CAF50" stroke-width="2" stroke-linecap="round"/>
            <path d="M30 45 L30 52" stroke="#4CAF50" stroke-width="2" stroke-linecap="round"/>
            <path d="M8 30 L15 30" stroke="#4CAF50" stroke-width="2" stroke-linecap="round"/>
            <path d="M45 30 L52 30" stroke="#4CAF50" stroke-width="2" stroke-linecap="round"/>
            <path d="M14 14 L19 19" stroke="#4CAF50" stroke-width="1.5" stroke-linecap="round"/>
            <path d="M41 41 L46 46" stroke="#4CAF50" stroke-width="1.5" stroke-linecap="round"/>
            <path d="M46 14 L41 19" stroke="#4CAF50" stroke-width="1.5" stroke-linecap="round"/>
            <path d="M19 41 L14 46" stroke="#4CAF50" stroke-width="1.5" stroke-linecap="round"/>
            <circle cx="30" cy="30" r="4" fill="#4CAF50"/>
            <path d="M30 26 L30 34" stroke="#6D4C41" stroke-width="1.5" stroke-linecap="round"/>
            <path d="M26 30 L34 30" stroke="#6D4C41" stroke-width="1.5" stroke-linecap="round"/>
        </svg>
        <h1 style="margin: 0; font-size: 3.2rem; letter-spacing: 2px; background: linear-gradient(135deg, #8D6E63, #4CAF50); -webkit-background-clip: text; background-clip: text; color: transparent;">
            TELLURIUM
        </h1>
    </div>
    <p style="margin: 0; font-size: 1rem; opacity: 0.95;">🌱 Classificador Inteligente de Fertilidade do Solo</p>
    <p style="margin-top: 10px; font-size: 0.8rem; opacity: 0.75;">SiBCS • Embrapa • CFSEMG • Boletim 100 • Recomendações Regionais • Adubação para Vasos</p>
</div>
""", unsafe_allow_html=True)

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
# MENU HORIZONTAL
# ============================================================================

menu = st.radio(
    "Navegação",
    ["📊 Dados do Solo", "🌱 Classificação", "🪴 Adubação para Vasos", "🤖 Assistente IA", "📈 Relatório", "ℹ️ Métodos", "📋 Pesquisa"],
    horizontal=True,
    label_visibility="collapsed"
)

# ============================================================================
# FUNÇÃO PARA LISTAR MODELOS DISPONÍVEIS
# ============================================================================

def listar_modelos_disponiveis():
    """Lista todos os modelos Gemini disponíveis para sua chave"""
    try:
        if not GEMINI_API_KEY or GEMINI_API_KEY == "":
            return []
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={GEMINI_API_KEY}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            modelos = response.json()
            nomes_modelos = []
            
            for model in modelos.get('models', []):
                nome = model.get('name', '').replace('models/', '')
                if 'gemini' in nome.lower() and 'generateContent' in str(model.get('supportedGenerationMethods', [])):
                    if 'embedding' not in nome.lower() and 'imagen' not in nome.lower():
                        nomes_modelos.append(nome)
            
            return nomes_modelos
        else:
            return []
    except Exception as e:
        return []
    
# ============================================================================
# CONFIGURAÇÃO GEMINI API
# ============================================================================

GEMINI_API_KEY = "AQ.Ab8RN6J5uzUogvavjQyfFr3wGWEaJbdrW3oByqhWo2bm_mMxmQ"

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
# CULTURAS (EXPANDIDO)
# ============================================================================

necessidades_culturas = {
    "Alface": {"v_desejado": 80, "n_min": 50, "p_min": 30, "k_min": 0.50, "ph_min": 6.0, "ph_max": 7.0, "n_recomendado": 100, "p_recomendado": 80, "k_recomendado": 100},
    "Algodão": {"v_desejado": 70, "n_min": 40, "p_min": 25, "k_min": 0.45, "ph_min": 5.8, "ph_max": 6.8, "n_recomendado": 120, "p_recomendado": 100, "k_recomendado": 120},
    "Arroz": {"v_desejado": 60, "n_min": 35, "p_min": 20, "k_min": 0.30, "ph_min": 5.2, "ph_max": 6.2, "n_recomendado": 80, "p_recomendado": 60, "k_recomendado": 80},
    "Batata": {"v_desejado": 75, "n_min": 50, "p_min": 35, "k_min": 0.50, "ph_min": 5.5, "ph_max": 6.5, "n_recomendado": 150, "p_recomendado": 120, "k_recomendado": 180},
    "Café": {"v_desejado": 65, "n_min": 40, "p_min": 20, "k_min": 0.50, "ph_min": 5.5, "ph_max": 6.5, "n_recomendado": 200, "p_recomendado": 100, "k_recomendado": 150},
    "Cana-de-açúcar": {"v_desejado": 60, "n_min": 35, "p_min": 20, "k_min": 0.40, "ph_min": 5.2, "ph_max": 6.5, "n_recomendado": 120, "p_recomendado": 80, "k_recomendado": 120},
    "Cebola": {"v_desejado": 75, "n_min": 45, "p_min": 30, "k_min": 0.45, "ph_min": 6.0, "ph_max": 7.0, "n_recomendado": 100, "p_recomendado": 80, "k_recomendado": 100},
    "Cenoura": {"v_desejado": 70, "n_min": 40, "p_min": 25, "k_min": 0.40, "ph_min": 5.8, "ph_max": 6.8, "n_recomendado": 80, "p_recomendado": 70, "k_recomendado": 100},
    "Couve-flor": {"v_desejado": 75, "n_min": 50, "p_min": 30, "k_min": 0.50, "ph_min": 6.0, "ph_max": 7.0, "n_recomendado": 120, "p_recomendado": 90, "k_recomendado": 120},
    "Feijão": {"v_desejado": 65, "n_min": 35, "p_min": 20, "k_min": 0.35, "ph_min": 5.5, "ph_max": 6.5, "n_recomendado": 40, "p_recomendado": 80, "k_recomendado": 60},
    "Mandioca": {"v_desejado": 55, "n_min": 25, "p_min": 15, "k_min": 0.30, "ph_min": 5.0, "ph_max": 6.2, "n_recomendado": 80, "p_recomendado": 60, "k_recomendado": 100},
    "Milheto": {"v_desejado": 55, "n_min": 30, "p_min": 18, "k_min": 0.30, "ph_min": 5.0, "ph_max": 6.2, "n_recomendado": 60, "p_recomendado": 50, "k_recomendado": 60},
    "Milho Grão": {"v_desejado": 70, "n_min": 45, "p_min": 30, "k_min": 0.45, "ph_min": 5.5, "ph_max": 6.8, "n_recomendado": 120, "p_recomendado": 100, "k_recomendado": 100},
    "Milho Semente": {"v_desejado": 75, "n_min": 50, "p_min": 35, "k_min": 0.50, "ph_min": 5.8, "ph_max": 6.8, "n_recomendado": 140, "p_recomendado": 120, "k_recomendado": 120},
    "Pimentão": {"v_desejado": 75, "n_min": 50, "p_min": 30, "k_min": 0.50, "ph_min": 5.8, "ph_max": 6.8, "n_recomendado": 120, "p_recomendado": 100, "k_recomendado": 150},
    "Soja": {"v_desejado": 70, "n_min": 20, "p_min": 25, "k_min": 0.40, "ph_min": 5.5, "ph_max": 6.5, "n_recomendado": 20, "p_recomendado": 80, "k_recomendado": 80},
    "Sorgo": {"v_desejado": 60, "n_min": 35, "p_min": 20, "k_min": 0.35, "ph_min": 5.2, "ph_max": 6.5, "n_recomendado": 80, "p_recomendado": 60, "k_recomendado": 80},
    "Tomate": {"v_desejado": 80, "n_min": 50, "p_min": 35, "k_min": 0.55, "ph_min": 5.8, "ph_max": 6.8, "n_recomendado": 150, "p_recomendado": 120, "k_recomendado": 200},
    "Trigo": {"v_desejado": 65, "n_min": 35, "p_min": 25, "k_min": 0.40, "ph_min": 5.5, "ph_max": 6.5, "n_recomendado": 80, "p_recomendado": 60, "k_recomendado": 60}
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
    
    ph = dados.get('ph', 0)
    resultados["embrapa"]["pH"] = interpretar_pelo_embrapa("ph", ph)
    resultados["cfsemg"]["pH"] = interpretar_pelo_cfsemg("ph", ph)
    
    p = dados.get('phosphorus', 0)
    resultados["embrapa"]["Fósforo"] = interpretar_pelo_embrapa("p_mehlich", p)
    resultados["cfsemg"]["Fósforo"] = interpretar_pelo_cfsemg("p_resina", p)
    
    k = dados.get('potassium', 0)
    resultados["embrapa"]["Potássio"] = interpretar_pelo_embrapa("k", k)
    resultados["cfsemg"]["Potássio"] = interpretar_pelo_cfsemg("k", k)
    
    v = dados.get('v_porcentagem', 0)
    resultados["embrapa"]["V%"] = interpretar_pelo_embrapa("v_percent", v)
    resultados["cfsemg"]["V%"] = interpretar_pelo_cfsemg("v_percent", v)
    
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
# FUNÇÃO IA GEMINI
# ============================================================================

def gerar_resposta_ia(pergunta, dados_solo=None):
    """Função com detecção automática do modelo e bases de fertilidade"""
    
    if not GEMINI_API_KEY or GEMINI_API_KEY == "":
        return "⚠️ **API Key não configurada!** \n\nConfigure sua chave no código (linha GEMINI_API_KEY)"
    
    try:
        modelos = listar_modelos_disponiveis()
        
        if not modelos:
            return "❌ **Nenhum modelo Gemini disponível!** \n\nVerifique se sua chave API está correta e se a API Gemini está ativada."
        
        modelo_valido = None
        for m in modelos:
            if 'gemini-2.0-flash' in m or 'gemini-2.5-flash' in m or 'gemini-2.0-flash-001' in m:
                modelo_valido = m
                break
        
        if not modelo_valido:
            modelo_valido = modelos[0]
        
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
            """
        
        prompt = f"""Você é um engenheiro agrônomo especialista em fertilidade do solo e de culturas brasileiras, SiBCS e manejo agrícola. 
        Suas respostas devem ser baseadas nas seguintes referências técnicas brasileiras:
        - Embrapa
        - CFSEMG
        - Boletim 100 - IAC
        - Recomendações regionais por estado

{contexto}

PERGUNTA DO USUÁRIO: {pergunta}

INSTRUÇÕES:
- Responda em português do Brasil
- Seja técnico, claro, objetivo e didático
- Dê recomendações práticas quando possível
- Use linguagem acessível para produtores rurais

RESPOSTA:"""
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo_valido}:generateContent?key={GEMINI_API_KEY}"
        
        headers = {"Content-Type": "application/json"}
        
        data = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 1024,
            }
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=60)
        
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
            return "❌ **Erro de autenticação (401):** API Key inválida. Verifique sua chave."
        elif response.status_code == 403:
            return "❌ **Acesso negado (403):** Ative a API Gemini no Google Cloud Console."
        elif response.status_code == 429:
            return "❌ **Limite excedido (429):** Muitas requisições. Aguarde alguns instantes."
        else:
            return f"❌ **Erro {response.status_code}**"
    
    except Exception as erro:
        return f"❌ **Erro:** {str(erro)}"

# ============================================================================
# CARREGAR MODELO TREINADO (RANDOM FOREST) - CORRIGIDO PARA GITHUB
# ============================================================================

@st.cache_resource
def carregar_modelo():
    """
    Carrega o modelo Random Forest treinado no Colab
    Corrigido para evitar erro 'No module named _loss' no GitHub/Streamlit Cloud
    """
    try:
        # ============================================================
        # SOLUÇÃO PARA O ERRO '_loss' - Usar pickle com compatibilidade
        # ============================================================
        
        # Primeiro, tenta carregar com joblib
        try:
            modelo = joblib.load('modelo_rf.pkl')
            return modelo, None, None, None
        except Exception as e:
            # Se joblib falhar, usa pickle com tratamento especial
            
            # Cria um módulo fake _loss se não existir
            if '_loss' not in sys.modules:
                import types
                fake_loss = types.ModuleType('_loss')
                sys.modules['_loss'] = fake_loss
            
            try:
                with open('modelo_rf.pkl', 'rb') as f:
                    modelo = pickle.load(f)
                    return modelo, None, None, None
            except Exception as e2:
                # Se ainda falhar, tenta com o unpickler seguro
                class SafeUnpickler(pickle.Unpickler):
                    def find_class(self, module, name):
                        if module == 'sklearn.loss' or module == 'sklearn._loss':
                            import sklearn.metrics
                            return getattr(sklearn.metrics, name, None)
                        return super().find_class(module, name)
                
                with open('modelo_rf.pkl', 'rb') as f:
                    modelo = SafeUnpickler(f).load()
                    return modelo, None, None, None
                    
    except FileNotFoundError as e:
        return None, None, None, f"Arquivo não encontrado: {e.filename}"
    except Exception as e:
        return None, None, None, f"Erro ao carregar modelo: {str(e)}"

# ============================================================================
# FUNÇÃO ALTERNATIVA PARA PREVISÃO SEM MODELO (FALLBACK)
# ============================================================================

def prever_sem_modelo(dados_usuario):
    """
    Função de fallback para prever fertilidade usando regras manuais
    Caso o modelo não possa ser carregado
    """
    ph = dados_usuario.get('ph', 6.0)
    v = dados_usuario.get('v_porcentagem', 50)
    n = dados_usuario.get('nitrogen', 30)
    p = dados_usuario.get('phosphorus', 20)
    k = dados_usuario.get('potassium', 0.25)
    
    # Pontuação baseada em regras agronômicas
    pontuacao = 0
    
    # pH (0-10)
    if 5.5 <= ph <= 6.5:
        pontuacao += 3
    elif 5.0 <= ph < 5.5 or 6.5 < ph <= 7.0:
        pontuacao += 2
    elif 4.5 <= ph < 5.0 or 7.0 < ph <= 7.5:
        pontuacao += 1
    else:
        pontuacao += 0
    
    # V% (0-5)
    if v >= 80:
        pontuacao += 5
    elif v >= 70:
        pontuacao += 4
    elif v >= 60:
        pontuacao += 3
    elif v >= 50:
        pontuacao += 2
    else:
        pontuacao += 0
    
    # N (0-3)
    if n >= 50:
        pontuacao += 3
    elif n >= 30:
        pontuacao += 2
    elif n >= 20:
        pontuacao += 1
    
    # P (0-3)
    if p >= 30:
        pontuacao += 3
    elif p >= 20:
        pontuacao += 2
    elif p >= 10:
        pontuacao += 1
    
    # K (0-3)
    if k >= 0.40:
        pontuacao += 3
    elif k >= 0.25:
        pontuacao += 2
    elif k >= 0.15:
        pontuacao += 1
    
    # Classificação
    pontuacao_maxima = 17
    
    if pontuacao >= 12:
        classe = 'Alta'
        confianca = (pontuacao / pontuacao_maxima) * 100
    elif pontuacao >= 8:
        classe = 'Media'
        confianca = (pontuacao / pontuacao_maxima) * 100
    else:
        classe = 'Baixa'
        confianca = (pontuacao / pontuacao_maxima) * 100
    
    # Probabilidades simuladas
    if classe == 'Alta':
        probs = [0.70, 0.15, 0.15]
    elif classe == 'Media':
        probs = [0.15, 0.10, 0.75]
    else:
        probs = [0.10, 0.70, 0.20]
    
    return classe, confianca, probs

# ============================================================================
# PREPARAR DADOS PARA PREVISÃO
# ============================================================================

def preparar_dados_para_previsao(dados_usuario, features_do_modelo):
    """
    Prepara os dados do usuário para o modelo Random Forest
    """
    mapeamento = {
        'ph': 'pH',
        'nitrogen': 'N',
        'phosphorus': 'P',
        'potassium': 'K',
        'sand': 'Areia',
        'silt': 'Silte',
        'clay': 'Argila'
    }
    
    dados_modelo = {}
    tabela_diagnostico = []
    
    for feature in features_do_modelo:
        if feature == 'Score_Agronomico':
            ph = dados_usuario.get('ph', 6.0)
            n = dados_usuario.get('nitrogen', 30)
            p = dados_usuario.get('phosphorus', 20)
            k = dados_usuario.get('potassium', 0.25)
            score = (ph * 10) + (n * 0.5) + (p * 0.5) + (k * 100)
            dados_modelo[feature] = score
            coluna_encontrada = "calculado"
        else:
            coluna_encontrada = "(não encontrada)"
            for chave_app, nome_feature in mapeamento.items():
                if feature == nome_feature and chave_app in dados_usuario:
                    dados_modelo[feature] = dados_usuario[chave_app]
                    coluna_encontrada = chave_app
                    break
            
            if coluna_encontrada == "(não encontrada)":
                dados_modelo[feature] = 0
        
        tabela_diagnostico.append({
            'Feature esperada': feature,
            'Coluna encontrada': coluna_encontrada,
            'Valor utilizado': dados_modelo[feature]
        })
    
    df_previsao = pd.DataFrame([dados_modelo])
    df_previsao = df_previsao[features_do_modelo]
    
    return df_previsao, tabela_diagnostico

# ============================================================================
# INTERPRETAÇÃO DO NÍVEL DE FERTILIDADE
# ============================================================================

def interpretar_fertilidade(classe_prevista, confianca):
    """
    Interpreta o resultado da previsão do modelo
    """
    if classe_prevista == "Alta":
        return {
            'nivel': 'Alta',
            'icone': '✅',
            'cor': 'success',
            'mensagem': 'O solo apresenta **ALTA fertilidade**. Condições favoráveis para a maioria das culturas. Recomenda-se apenas adubação de manutenção.',
            'recomendacao': 'Manutenção: 30-50 kg/ha de N, 40-80 kg/ha de P2O5, 40-60 kg/ha de K2O'
        }
    elif classe_prevista == "Media":
        return {
            'nivel': 'Média',
            'icone': '⚠️',
            'cor': 'warning',
            'mensagem': 'O solo apresenta **MÉDIA fertilidade**. Recomenda-se adubação para atingir níveis adequados.',
            'recomendacao': 'Adubação: 60-100 kg/ha de N, 80-120 kg/ha de P2O5, 60-100 kg/ha de K2O. Avaliar necessidade de calagem.'
        }
    else:
        return {
            'nivel': 'Baixa',
            'icone': '❌',
            'cor': 'error',
            'mensagem': 'O solo apresenta **BAIXA fertilidade**. Necessidade de correção do solo e adubação significativa.',
            'recomendacao': 'Correção: Calagem para elevar V% a 70-80%. Adubação: 100-150 kg/ha de N, 120-180 kg/ha de P2O5, 100-150 kg/ha de K2O.'
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
# FUNÇÃO PARA CÁLCULO DE VASOS
# ============================================================================

def calcular_volume_vaso(raio_superior, raio_inferior, altura, formato="tronco_cone"):
    """Calcula o volume do vaso em litros"""
    if formato == "cilindro":
        volume_cm3 = math.pi * (raio_superior ** 2) * altura
    else:
        volume_cm3 = (math.pi * altura / 3) * (raio_superior**2 + raio_superior*raio_inferior + raio_inferior**2)
    
    volume_litros = volume_cm3 / 1000
    return round(volume_litros, 2)

def calcular_adubo_para_vaso(cultura, volume_litros, area_plantio_cm2=None):
    """Calcula a quantidade de adubo para vaso"""
    req = necessidades_culturas[cultura]
    
    if area_plantio_cm2:
        area_m2 = area_plantio_cm2 / 10000
        fator_escala = area_m2
    else:
        fator_escala = 1
    
    n_gramas = req.get('n_recomendado', 80) * fator_escala
    p_gramas = req.get('p_recomendado', 60) * fator_escala
    k_gramas = req.get('k_recomendado', 80) * fator_escala
    
    return {
        'N': round(n_gramas, 2),
        'P2O5': round(p_gramas, 2),
        'K2O': round(k_gramas, 2),
        'cultura': cultura,
        'volume_litros': volume_litros,
        'area_m2': round(fator_escala, 2)
    }

# ============================================================================
# ABA 1 - DADOS DO SOLO
# ============================================================================

if menu == "📊 Dados do Solo":
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
        
        soma_textura = sand + silt + clay
        if soma_textura != 100:
            st.warning(f"⚠️ **Atenção:** A soma das frações é {soma_textura}%. O ideal é 100%. Ajuste os valores.")
        else:
            st.success(f"✅ Textura válida! Areia: {sand}%, Silte: {silt}%, Argila: {clay}%")
    
    st.caption("💡 Após salvar os dados, vá para a aba 'Classificação' para ver as recomendações.")

    if st.button("✅ SALVAR DADOS", use_container_width=True):
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

                    # ================================================================
                    # PREVISÃO COM O MODELO RANDOM FOREST (COM FALLBACK)
                    # ================================================================
                    
                    # Carrega o modelo
                    modelo, label_encoder, features, erro = carregar_modelo()

                    if modelo is not None:
                        st.markdown("---")
                        st.markdown("## 🤖 Resultados do Modelo de Machine Learning")
                        
                        # Extrai features do modelo se possível
                        try:
                            if hasattr(modelo, 'feature_names_in_'):
                                features = list(modelo.feature_names_in_)
                            else:
                                features = ['pH', 'N', 'P', 'K', 'Areia', 'Silte', 'Argila', 'Score_Agronomico']
                        except:
                            features = ['pH', 'N', 'P', 'K', 'Areia', 'Silte', 'Argila', 'Score_Agronomico']
                        
                        with st.expander("ℹ️ Informações do Modelo", expanded=False):
                            st.markdown(f"**Tipo:** Random Forest Classifier")
                            st.markdown(f"**Features:** {features}")
                        
                        with st.spinner("🧠 Realizando previsão com o modelo treinado..."):
                            try:
                                df_previsao, tabela_diagnostico = preparar_dados_para_previsao(dados, features)

                                with st.expander("🔍 Visualizar dados de entrada", expanded=False):
                                    st.dataframe(df_previsao, use_container_width=True)
                                    st.caption("📋 Diagnóstico do mapeamento das features")
                                    st.dataframe(pd.DataFrame(tabela_diagnostico), use_container_width=True, hide_index=True)

                                previsao = modelo.predict(df_previsao)[0]
                                probabilidades = modelo.predict_proba(df_previsao)[0]
                                
                                # Mapeamento de classes
                                classes_nomes = ['Alta', 'Baixa', 'Media']
                                if hasattr(modelo, 'classes_'):
                                    if len(modelo.classes_) == 3:
                                        classes_nomes = list(modelo.classes_)
                                
                                classe_prevista = classes_nomes[previsao] if previsao < len(classes_nomes) else 'Media'
                                confianca = max(probabilidades) * 100
                                
                                col_classe, col_conf = st.columns(2)
                                with col_classe:
                                    st.metric("🏷️ Classe Prevista", classe_prevista)
                                with col_conf:
                                    st.metric("📊 Confiança do Modelo", f"{confianca:.2f}%")
                                
                                st.markdown("**📈 Probabilidades por Classe:**")
                                prob_df = pd.DataFrame({
                                    'Classe': classes_nomes[:len(probabilidades)],
                                    'Probabilidade (%)': (probabilidades * 100).round(2)
                                }).sort_values('Probabilidade (%)', ascending=False)
                                
                                st.dataframe(prob_df, use_container_width=True, hide_index=True)
                                st.progress(confianca / 100)
                                
                                st.markdown("---")
                                st.markdown("### 🌱 Interpretação da Fertilidade")
                                
                                interpretacao = interpretar_fertilidade(classe_prevista, confianca)
                                
                                if interpretacao['cor'] == 'success':
                                    st.success(f"{interpretacao['icone']} **{interpretacao['mensagem']}**")
                                elif interpretacao['cor'] == 'warning':
                                    st.warning(f"{interpretacao['icone']} **{interpretacao['mensagem']}**")
                                else:
                                    st.error(f"{interpretacao['icone']} **{interpretacao['mensagem']}**")
                                
                                st.info(f"📌 **Recomendação:** {interpretacao['recomendacao']}")
                                
                            except Exception as e:
                                st.warning(f"⚠️ Erro ao usar o modelo: {e}")
                                st.info("💡 Usando classificação manual como fallback...")
                                
                                # FALLBACK
                                classe_prevista, confianca, probabilidades = prever_sem_modelo(dados)
                                
                                st.markdown("---")
                                st.markdown("## 🤖 Resultado da Classificação (Modo Fallback)")
                                st.info("ℹ️ A classificação é baseada em regras agronômicas.")
                                
                                col_classe, col_conf = st.columns(2)
                                with col_classe:
                                    st.metric("🏷️ Classe Prevista", classe_prevista)
                                with col_conf:
                                    st.metric("📊 Pontuação", f"{confianca:.1f}%")
                                
                                st.markdown("**📈 Pontuação por Classe:**")
                                classes_nomes = ['Alta', 'Baixa', 'Media']
                                prob_df = pd.DataFrame({
                                    'Classe': classes_nomes,
                                    'Pontuação (%)': (np.array(probabilidades) * 100).round(2)
                                }).sort_values('Pontuação (%)', ascending=False)
                                
                                st.dataframe(prob_df, use_container_width=True, hide_index=True)
                                st.progress(confianca / 100)
                                
                                interpretacao = interpretar_fertilidade(classe_prevista, confianca)
                                if interpretacao['cor'] == 'success':
                                    st.success(f"{interpretacao['icone']} **{interpretacao['mensagem']}**")
                                elif interpretacao['cor'] == 'warning':
                                    st.warning(f"{interpretacao['icone']} **{interpretacao['mensagem']}**")
                                else:
                                    st.error(f"{interpretacao['icone']} **{interpretacao['mensagem']}**")
                                st.info(f"📌 **Recomendação:** {interpretacao['recomendacao']}")

                    else:
                        st.warning(f"ℹ️ **Modelo não disponível:** {erro if erro else 'Erro desconhecido'}")
                        st.info("💡 Usando classificação manual baseada em regras agronômicas.")
                        
                        # FALLBACK
                        classe_prevista, confianca, probabilidades = prever_sem_modelo(dados)
                        
                        st.markdown("---")
                        st.markdown("## 🤖 Resultado da Classificação (Modo Manual)")
                        
                        col_classe, col_conf = st.columns(2)
                        with col_classe:
                            st.metric("🏷️ Classe Prevista", classe_prevista)
                        with col_conf:
                            st.metric("📊 Pontuação", f"{confianca:.1f}%")
                        
                        st.markdown("**📈 Pontuação por Classe:**")
                        classes_nomes = ['Alta', 'Baixa', 'Media']
                        prob_df = pd.DataFrame({
                            'Classe': classes_nomes,
                            'Pontuação (%)': (np.array(probabilidades) * 100).round(2)
                        }).sort_values('Pontuação (%)', ascending=False)
                        
                        st.dataframe(prob_df, use_container_width=True, hide_index=True)
                        st.progress(confianca / 100)
                        
                        interpretacao = interpretar_fertilidade(classe_prevista, confianca)
                        if interpretacao['cor'] == 'success':
                            st.success(f"{interpretacao['icone']} **{interpretacao['mensagem']}**")
                        elif interpretacao['cor'] == 'warning':
                            st.warning(f"{interpretacao['icone']} **{interpretacao['mensagem']}**")
                        else:
                            st.error(f"{interpretacao['icone']} **{interpretacao['mensagem']}**")
                        st.info(f"📌 **Recomendação:** {interpretacao['recomendacao']}")

                except ValueError as ve:
                    st.error(f"❌ Erro: Verifique se todos os valores são números válidos! Detalhes: {ve}")
                except Exception as e:
                    st.error(f"❌ Erro inesperado: {e}")

# ============================================================================
# ABA 2 - CLASSIFICAÇÃO
# ============================================================================

elif menu == "🌱 Classificação":

    if "dados_basicos" not in st.session_state or not st.session_state.dados_basicos:
        st.warning("⚠️ Preencha e salve os dados na aba 'Dados do Solo' primeiro!")
        st.stop()

    dados = st.session_state.dados_basicos

    cultura = st.selectbox("🌾 Selecione a cultura:", list(necessidades_culturas.keys()))
    req = necessidades_culturas[cultura]

    aba1, aba2 = st.tabs([
        "📊 Classificação",
        "🌱 Adubação"
    ])

    with aba1:
        st.markdown("## 📊 Classificação da Fertilidade")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("pH", f"{dados.get('ph', 0):.1f}")
        with col2:
            st.metric("V%", f"{dados.get('v_porcentagem', 0):.1f}%")
        with col3:
            st.metric("m%", f"{dados.get('m_porcentagem', 0):.1f}%")
        with col4:
            st.metric("CTC", f"{dados.get('ctc', 0):.2f} cmolc/dm³")
        
        st.markdown("---")
        
        st.markdown(f"### 🔍 Diagnóstico para {cultura}")
        diagnosticos = gerar_diagnostico(dados, req)
        for diag in diagnosticos:
            st.markdown(f"- {diag}")
        
        st.markdown("---")
        
        st.markdown("### 📊 Classificação da Fertilidade (SiBCS)")
        v = dados.get('v_porcentagem', 0)
        classe = classificar_fertilidade(v)
        if v < 50:
            st.error(f"**{classe}**")
        elif v < 70:
            st.warning(f"**{classe}**")
        else:
            st.success(f"**{classe}**")
        
        st.markdown("---")
        
        st.markdown("### 📚 Interpretação por Múltiplas Bases")
        interps = interpretar_fertilidade_multiplas_bases(dados)
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("**🌱 Embrapa**")
            for k, v in interps["embrapa"].items():
                st.caption(f"• {k}: {v}")
        with col_b:
            st.markdown("**📍 CFSEMG (MG)**")
            for k, v in interps["cfsemg"].items():
                st.caption(f"• {k}: {v}")
        
        st.markdown("---")
        
        if "uf_selecionada" in st.session_state:
            st.markdown("### 📍 Recomendação Regional")
            for rec in recomendar_por_regiao(st.session_state.uf_selecionada, dados):
                st.markdown(f"- {rec}")

    with aba2:
        st.markdown(f"#### 🌱 Recomendação de Adubação para {cultura}")

        with st.container(border=True):
            st.markdown("**Nitrogênio (N)**")
            n_atual = dados.get('nitrogen', 0)
            usa_biologico = False
            if cultura in ["Soja", "Feijão"]:
                usa_biologico = st.toggle(f"🦠 Utilizar inoculação biológica em {cultura}?", value=True)
            n_recomendacao = recomendar_adubacao_nitrogenio(cultura, n_atual, req['n_min'])
            if "✅" in n_recomendacao:
                st.success(n_recomendacao)
            else:
                match = re.search(r'Aplicar (\d+) kg/ha', n_recomendacao)
                if match:
                    kg_n = int(match.group(1))
                    if cultura == "Soja":
                        if usa_biologico:
                            kg_n = max(0, int(kg_n * 0.15))
                            st.success("🦠 Inoculação biológica ativada: redução da necessidade de N mineral.")
                        else:
                            st.warning("⚠️ Sem inoculação biológica: maior demanda de N mineral.")
                    elif cultura == "Feijão":
                        if usa_biologico:
                            kg_n = max(20, int(kg_n * 0.50))
                            st.success("🦠 Coinoculação/inoculação considerada: redução parcial do N mineral.")
                    st.warning(f"Aplicar {kg_n} kg/ha de Nitrogênio")
                    st.info("**📌 Forma de aplicação do Nitrogênio:**")
                    if cultura == "Soja":
                        if usa_biologico:
                            st.markdown(f"""
                            - **Aplicação recomendada:** Dose simbólica ou starter
                            - Aplicar até {kg_n} kg/ha no sulco de plantio
                            - **Preferir inoculação eficiente com Bradyrhizobium**
                            - Evitar excesso de N mineral para não reduzir a FBN
                            """)
                        else:
                            p1 = kg_n // 2
                            p2 = kg_n - p1
                            st.markdown(f"""
                            - **Parcelamento recomendado:** 2 aplicações
                            - Plantio: {p1} kg/ha
                            - V4-V6: {p2} kg/ha
                            - Recomenda-se inoculação biológica para maior eficiência
                            """)
                    elif cultura == "Feijão":
                        if kg_n <= 40:
                            st.markdown(f"""
                            - **Aplicação recomendada:** Dose única
                            - Aplicar {kg_n} kg/ha no plantio
                            """)
                        else:
                            p1 = kg_n // 2
                            p2 = kg_n - p1
                            st.markdown(f"""
                            - **Parcelamento recomendado:** 2 aplicações
                            - Plantio: {p1} kg/ha
                            - Cobertura (20-30 DAE): {p2} kg/ha
                            """)
                    elif cultura == "Café":
                        p1 = kg_n // 4
                        p2 = kg_n // 4
                        p3 = kg_n // 4
                        p4 = kg_n - p1 - p2 - p3
                        st.markdown(f"""
                        - **Parcelamento recomendado:** 4 aplicações anuais
                        - 1ª aplicação: {p1} kg/ha
                        - 2ª aplicação: {p2} kg/ha
                        - 3ª aplicação: {p3} kg/ha
                        - 4ª aplicação: {p4} kg/ha
                        """)
                    elif cultura in ["Milho Grão", "Milho Semente", "Tomate", "Alface", "Couve-flor", "Pimentão", "Batata"]:
                        if kg_n <= 40:
                            st.markdown(f"""
                            - **Aplicação recomendada:** Dose única
                            - Aplicar {kg_n} kg/ha no plantio
                            """)
                        elif kg_n <= 80:
                            p1 = kg_n // 2
                            p2 = kg_n - p1
                            st.markdown(f"""
                            - **Parcelamento recomendado:** 2 aplicações
                            - Plantio: {p1} kg/ha
                            - Cobertura: {p2} kg/ha
                            """)
                        else:
                            p1 = kg_n // 3
                            p2 = kg_n // 3
                            p3 = kg_n - p1 - p2
                            st.markdown(f"""
                            - **Parcelamento recomendado:** 3 aplicações
                            - Plantio: {p1} kg/ha
                            - V4-V6 / Desenvolvimento vegetativo: {p2} kg/ha
                            - Pré-florescimento: {p3} kg/ha
                            """)
                    else:
                        if kg_n <= 50:
                            st.markdown(f"""
                            - **Aplicação recomendada:** Dose única
                            - Aplicar {kg_n} kg/ha no plantio
                            """)
                        else:
                            p1 = kg_n // 2
                            p2 = kg_n - p1
                            st.markdown(f"""
                            - **Parcelamento recomendado:** 2 aplicações
                            - Plantio: {p1} kg/ha
                            - Cobertura: {p2} kg/ha
                            """)
                    st.markdown("""
                    - **Evitar aplicação superficial sem incorporação**
                    - Parcelamentos reduzem perdas por volatilização e lixiviação
                    """)

        with st.container(border=True):
            st.markdown("**Fósforo (P)**")
            p_atual = dados.get('phosphorus', 0)
            p_recomendacao = recomendar_adubacao_fosforo(cultura, p_atual, req['p_min'])
            if "✅" in p_recomendacao:
                st.success(p_recomendacao)
            else:
                match = re.search(r'Aplicar (\d+) kg/ha', p_recomendacao)
                if match:
                    kg_p = int(match.group(1))
                    st.warning(f"Aplicar {kg_p} kg/ha de Fósforo")
                    st.info("**📌 Forma de aplicação do Fósforo:**")
                    st.markdown("""
                    - Aplicar 100% no plantio/semeadura
                    - Aplicação localizada no sulco
                    - Profundidade ideal: 5–10 cm
                    - O fósforo possui baixa mobilidade no solo
                    - Preferir aplicação próxima ao sistema radicular
                    """)

        with st.container(border=True):
            st.markdown("**Potássio (K)**")
            k_atual = dados.get('potassium', 0)
            k_recomendacao = recomendar_adubacao_potassio(cultura, k_atual, req['k_min'])
            if "✅" in k_recomendacao:
                st.success(k_recomendacao)
            else:
                match = re.search(r'Aplicar (\d+) kg/ha', k_recomendacao)
                if match:
                    kg_k = int(match.group(1))
                    st.warning(f"Aplicar {kg_k} kg/ha de Potássio")
                    st.info("**📌 Forma de aplicação do Potássio:**")
                    if cultura in ["Tomate", "Batata", "Café", "Pimentão"]:
                        p1 = kg_k // 3
                        p2 = kg_k // 3
                        p3 = kg_k - p1 - p2
                        st.markdown(f"""
                        - **Parcelamento recomendado:** 3 aplicações
                        - Plantio: {p1} kg/ha
                        - Desenvolvimento vegetativo: {p2} kg/ha
                        - Florescimento/frutificação: {p3} kg/ha
                        """)
                    else:
                        p1 = kg_k // 2
                        p2 = kg_k - p1
                        st.markdown(f"""
                        - **Parcelamento recomendado:** 2 aplicações
                        - Plantio: {p1} kg/ha
                        - Cobertura: {p2} kg/ha
                        """)
                    st.markdown("""
                    - Evitar aplicação excessiva para reduzir salinização
                    - Parcelamento melhora eficiência de uso do K
                    """)

        with st.container(border=True):
            st.markdown("**🧪 Calagem**")
            v_atual = dados.get('v_porcentagem', 0)
            ctc = dados.get('ctc', 0)
            v_desejado = req['v_desejado']
            nc, rec_calagem, tempo = calcular_necessidade_calagem(v_atual, v_desejado, ctc)
            if nc > 0:
                st.warning(rec_calagem)
                st.info(f"⏱️ Tempo estimado para reação: {tempo} dias")
                st.caption("💡 O calcário deve ser incorporado na camada de 0-20cm")
            else:
                st.success(rec_calagem)

# ============================================================================
# ABA 3 - ADUBAÇÃO PARA VASOS
# ============================================================================

elif menu == "🪴 Adubação para Vasos":
    st.markdown("### 🪴 Calculadora de Adubação para Vasos")
    st.caption("Calcule a quantidade ideal de fertilizantes para cultivo em vasos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        with st.container(border=True):
            st.markdown("**📏 Dimensões do Vaso**")
            formato_vaso = st.radio("Formato do vaso:", ["Cilindro", "Tronco de Cone (mais comum)"], horizontal=True)
            if formato_vaso == "Cilindro":
                raio_sup = st.number_input("📐 Raio do vaso (cm)", min_value=5.0, max_value=100.0, value=15.0, step=1.0)
                raio_inf = raio_sup
            else:
                raio_sup = st.number_input("📐 Raio superior (cm)", min_value=5.0, max_value=100.0, value=20.0, step=1.0)
                raio_inf = st.number_input("📐 Raio inferior (cm)", min_value=5.0, max_value=100.0, value=12.0, step=1.0)
            altura_vaso = st.number_input("📏 Altura do vaso (cm)", min_value=10.0, max_value=150.0, value=25.0, step=5.0)
            volume = calcular_volume_vaso(raio_sup, raio_inf, altura_vaso, "cilindro" if formato_vaso == "Cilindro" else "tronco_cone")
            st.success(f"💧 **Volume estimado:** {volume:.2f} litros")
            area_superficie = math.pi * (raio_sup ** 2)
            st.info(f"📐 **Área de superfície:** {area_superficie:.1f} cm² ({area_superficie/10000:.4f} m²)")
    
    with col2:
        with st.container(border=True):
            st.markdown("**🌾 Seleção da Cultura**")
            cultura_vaso = st.selectbox("Escolha a cultura:", list(necessidades_culturas.keys()), key="cultura_vaso")
            req_vaso = necessidades_culturas[cultura_vaso]
            st.markdown("---")
            st.markdown("**📊 Parâmetros da Cultura**")
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("🌱 N recomendado", f"{req_vaso.get('n_recomendado', 80)} kg/ha")
            with col_b:
                st.metric("💀 P₂O₅ recomendado", f"{req_vaso.get('p_recomendado', 60)} kg/ha")
            with col_c:
                st.metric("🍌 K₂O recomendado", f"{req_vaso.get('k_recomendado', 80)} kg/ha")
    
    st.markdown("---")
    
    if st.button("🔬 CALCULAR ADUBAÇÃO PARA O VASO", use_container_width=True):
        with st.spinner("Calculando..."):
            area_m2 = area_superficie / 10000
            adubo = calcular_adubo_para_vaso(cultura_vaso, volume, area_superficie)
            st.markdown("""
            <div class="result-card">
                <h3 style="text-align: center; margin-bottom: 1rem;">📊 Resultado da Adubação</h3>
            """, unsafe_allow_html=True)
            col_r1, col_r2, col_r3 = st.columns(3)
            with col_r1:
                st.metric("🌱 Nitrogênio (N)", f"{adubo['N']:.2f} g")
                st.caption("Equivalente a: Sulfato de Amônio | Ureia")
            with col_r2:
                st.metric("💀 Fósforo (P₂O₅)", f"{adubo['P2O5']:.2f} g")
                st.caption("Equivalente a: Superfosfato Simples")
            with col_r3:
                st.metric("🍌 Potássio (K₂O)", f"{adubo['K2O']:.2f} g")
                st.caption("Equivalente a: Cloreto de Potássio")
            st.markdown("---")
            st.markdown("### 📋 Recomendações de Aplicação")
            st.markdown(f"""
            - **Cultura selecionada:** {adubo['cultura']}
            - **Volume do vaso:** {adubo['volume_litros']:.2f} litros
            - **Área de superfície:** {adubo['area_m2']:.2f} m²
            
            **Como aplicar:**
            1. Misture os fertilizantes uniformemente ao substrato antes do plantio
            2. Para culturas perenes, divida a aplicação em 2-3 parcelas
            3. Regue após a aplicação para melhor absorção dos nutrientes
            4. Monitore o desenvolvimento da planta e ajuste se necessário
            
            **Observações importantes:**
            - As quantidades são estimativas baseadas em recomendações para campo
            - Ajuste conforme o substrato utilizado e a fase da cultura
            - Considere a fertilidade natural do substrato antes da adubação
            """)
            st.markdown("</div>", unsafe_allow_html=True)

# ============================================================================
# ABA 4 - ASSISTENTE IA
# ============================================================================

elif menu == "🤖 Assistente IA":
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
# ABA 5 - RELATÓRIO
# ============================================================================

elif menu == "📈 Relatório":
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
# ABA 6 - MÉTODOS
# ============================================================================

elif menu == "ℹ️ Métodos":
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
# ABA 7 - PESQUISA DE SATISFAÇÃO
# ============================================================================

elif menu == "📋 Pesquisa":
    st.markdown("### 📋 Pesquisa de Satisfação - Classificador de Fertilidade do Solo")
    st.markdown("Sua opinião é fundamental para melhorarmos a ferramenta!")
    st.markdown("---")
    
    if "pesquisa_respondida" not in st.session_state:
        st.session_state.pesquisa_respondida = False
    
    if not st.session_state.pesquisa_respondida:
        with st.form("pesquisa_form"):
            st.markdown("#### 1. Avaliação da Plataforma")
            nota_plataforma = st.slider("De 0 a 10, qual a nota pela funcionalidade da plataforma?", min_value=0, max_value=10, value=5, step=1)
            st.markdown("---")
            st.markdown("#### 2. Didática da Interpretação")
            nota_didatica = st.slider("De 0 a 10, o quão didático foi a interpretação dos dados?", min_value=0, max_value=10, value=5, step=1)
            st.markdown("---")
            st.markdown("#### 3. Uso Acadêmico")
            col_estudante, col_nota = st.columns([1, 2])
            with col_estudante:
                eh_estudante = st.checkbox("Sou estudante/pesquisador")
            with col_nota:
                if eh_estudante:
                    nota_academico = st.slider("De 0 a 10, qual a probabilidade de utilizar a ferramenta para fins acadêmicos?", min_value=0, max_value=10, value=5, step=1)
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
                    nota_produtor = st.slider("De 0 a 10, qual a probabilidade de usar esta ferramenta em sua propriedade rural?", min_value=0, max_value=10, value=5, step=1)
                else:
                    nota_produtor = "Não se aplica (não sou produtor)"
                    st.info("✅ Você marcou que não é produtor. Esta pergunta não se aplica.")
            st.markdown("---")
            st.markdown("#### 5. Classificação do Uso")
            classificacao_uso = st.radio("Como você classificaria o uso da ferramenta?", ["Fácil", "Médio", "Difícil"], horizontal=True)
            st.markdown("---")
            st.markdown("#### 6. Sugestoes de Aprimoramento")
            sugestoes = st.text_area("Sugestoes de aprimoramentos. O que falta ou pode melhorar?", placeholder="Ex: Adicionar gráficos, incluir mais culturas, melhorar a explicação do V%...", height=100)
            st.markdown("---")
            with st.expander("🔒 Identificacao (opcional)"):
                nome = st.text_input("Nome (opcional)")
                email = st.text_input("E-mail (opcional - para contato)")
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
    
    st.markdown("---")
    st.markdown("### 🔒 Relatório de Pesquisas (Área Restrita)")
    senha_correta = "91959441"
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
    st.caption("© 2026 - Tellurium | Sistema Inteligente de Fertilidade do Solo | Fins Acadêmicos")
    st.caption("🤖 IA Gemini do Google • 🌱 Metodologias: Embrapa | CFSEMG | Boletim 100 | Regionais")
    st.caption("📧 Contato: laenor@outlook.com")
