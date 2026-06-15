# ============================================================================
# IMPORTAÇÕES
# ============================================================================

import streamlit as st
import pandas as pd
import requests
import json
import time
import re
import base64
import os
import math
from datetime import datetime

# ============================================================================
# CONFIGURAÇÃO DA PÁGINA - DESIGN PREMIUM (CORES TERRA/VERDE)
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
    page_title="🌱 Telluriun - Classificador Inteligente de Fertilidade do Solo",
    page_icon=f"data:image/svg+xml;base64,{svg_base64}",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/laenor-agricre/Excel',
        'Report a bug': 'mailto:laenor@outlook.com',
        'About': '### 🌱 SoilSense\nSistema Inteligente de Classificação de Fertilidade do Solo\n\nDesenvolvido com base nas metodologias:\n- Embrapa\n- CFSEMG\n- Boletim 100 IAC\n- Recomendações Regionais'
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
    }
    
    /* ========== FUNDO PRINCIPAL - TONS DE TERRA ========== */
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
    
    /* ========== TÍTULOS COM GRADIENTE TERRA/VERDE ========== */
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
    
    /* ========== CARDS GLASSMORPHISM ========== */
    .stContainer, .element-container:has(.stExpander), div[data-testid="stExpander"] {
        background: rgba(255,255,255,0.03);
        backdrop-filter: blur(12px);
        border-radius: 20px;
        border: 1px solid rgba(139,69,19,0.2);
        margin-bottom: 1rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .stContainer:hover, div[data-testid="stExpander"]:hover {
        border-color: rgba(76,175,80,0.4);
        transform: translateY(-2px);
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    /* ========== INPUTS ESTILIZADOS ========== */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
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
    .stNumberInput > div > div > input:focus {
        border-color: #4CAF50 !important;
        box-shadow: 0 0 0 3px rgba(76,175,80,0.25) !important;
    }
    
    /* ========== SELECTBOX ESTILIZADO ========== */
    .stSelectbox > div > div {
        background: rgba(20, 20, 40, 0.95) !important;
        border: 1px solid rgba(139,69,19,0.35) !important;
        border-radius: 14px !important;
    }
    
    div[data-baseweb="select"] ul {
        background: rgba(15, 15, 30, 0.98) !important;
        border: 1px solid rgba(76,175,80,0.3);
    }
    
    div[data-baseweb="select"] li[aria-selected="true"] {
        background: rgba(76,175,80,0.3) !important;
        color: #4CAF50 !important;
    }
    
    /* ========== BOTÕES COM EFEITO ========== */
    .stButton button {
        background: linear-gradient(135deg, #6D4C41, #8D6E63);
        border: none;
        border-radius: 40px;
        padding: 12px 28px;
        font-weight: 600;
        font-size: 15px;
        color: white !important;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(109,76,65,0.3);
        width: 100%;
    }
    
    .stButton button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(76,175,80,0.4);
        background: linear-gradient(135deg, #8D6E63, #4CAF50);
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
        color: #4CAF50;
        margin-right: 8px;
        transition: all 0.2s ease;
    }
    
    .reference-badge:hover {
        background: rgba(76,175,80,0.2);
        transform: translateY(-1px);
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
    
    /* ========== MENU HORIZONTAL ========== */
    .stRadio > div {
        gap: 8px;
        background: rgba(255,255,255,0.04);
        padding: 8px;
        border-radius: 60px;
    }
    
    .stRadio > div > label {
        background: transparent;
        border-radius: 40px;
        padding: 8px 24px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stRadio > div > label[data-baseweb="radio"]:has(input:checked) {
        background: linear-gradient(135deg, #6D4C41, #4CAF50);
        box-shadow: 0 2px 10px rgba(76,175,80,0.3);
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
            <circle cx="30" cy="30" r="4" fill="#4CAF50"/>
            <path d="M30 26 L30 34" stroke="#6D4C41" stroke-width="1.5" stroke-linecap="round"/>
            <path d="M26 30 L34 30" stroke="#6D4C41" stroke-width="1.5" stroke-linecap="round"/>
        </svg>
        <h1 style="margin: 0; font-size: 3.2rem; letter-spacing: 2px;">SOILSENSE</h1>
    </div>
    <p style="margin: 0; font-size: 1rem; opacity: 0.95;">🌱 Classificador Inteligente de Fertilidade do Solo</p>
    <p style="margin-top: 10px; font-size: 0.8rem; opacity: 0.75;">SiBCS • Embrapa • CFSEMG • Boletim 100 • Recomendações Regionais • Adubação para Vasos</p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/18629/18629540.png", width=80)
    st.markdown("### 🌱 SoilSense")
    st.markdown("""
    <span class="reference-badge">SiBCS</span>
    <span class="reference-badge">Embrapa</span>
    <span class="reference-badge">CFSEMG</span>
    <span class="reference-badge">Boletim 100</span>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 📊 Sistema Inteligente")
    st.markdown("""
    • Avaliação da fertilidade  
    • Cálculo de V% e m%  
    • Classificação SiBCS  
    • Relatório técnico  
    • IA Gemini integrada  
    • Adubação para vasos  
    """)
    
    st.markdown("---")
    st.markdown("### 🗺️ Base Regional")
    uf_selecionada = st.selectbox(
        "Selecione o estado/região:",
        ["SP", "MG", "RS", "SC", "PR", "MT", "GO", "BA", "NORDESTE", "NORTE"],
        index=0
    )
    st.session_state.uf_selecionada = uf_selecionada
    
    st.markdown("---")
    st.caption("🔬 Metodologias: Embrapa | CFSEMG | IAC | Regionais")
    st.caption("🤖 IA Gemini | 📊 Classificação Inteligente")

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
# MENU HORIZONTAL (COM NOVA ABA DE VASOS)
# ============================================================================

menu = st.radio(
    "Navegação",
    ["📊 Dados do Solo", "🌱 Classificação", "🪴 Adubação para Vasos", "🤖 Assistente IA", "📈 Relatório", "ℹ️ Métodos", "📋 Pesquisa"],
    horizontal=True,
    label_visibility="collapsed"
)

# ============================================================================
# BASES DE FERTILIDADE DO SOLO (COMPLETAS)
# ============================================================================

GEMINI_API_KEY = "AQ.Ab8RN6KDhETV-bQ9RBKAPsKHjFLyj28H-hsUh8Yg-uhEyU5t1A"

INTERPRETACAO_EMBRAPA = {
    "ph": {"muito_baixo": "< 4.5", "baixo": "4.5 - 5.0", "medio": "5.1 - 5.5", "adequado": "5.6 - 6.5", "alto": "6.6 - 7.0", "muito_alto": "> 7.0"},
    "p_mehlich": {"muito_baixo": "< 3", "baixo": "3 - 5", "medio": "6 - 10", "adequado": "11 - 20", "alto": "21 - 40", "muito_alto": "> 40"},
    "k": {"muito_baixo": "< 0.05", "baixo": "0.05 - 0.10", "medio": "0.11 - 0.20", "adequado": "0.21 - 0.30", "alto": "0.31 - 0.50", "muito_alto": "> 0.50"},
    "v_percent": {"baixo": "< 50", "medio": "50 - 70", "adequado": "70 - 85", "alto": "> 85"},
    "m_percent": {"baixo": "< 10", "medio": "10 - 20", "alto": "20 - 40", "muito_alto": "> 40"},
    "materia_organica": {"muito_baixo": "< 10", "baixo": "10 - 20", "medio": "21 - 30", "adequado": "31 - 40", "alto": "> 40"}
}

INTERPRETACAO_CFSEMG = {
    "ph": {"muito_baixo": "< 4.9", "baixo": "5.0 - 5.4", "medio": "5.5 - 5.9", "adequado": "6.0 - 6.5", "alto": "> 6.5"},
    "p_resina": {"muito_baixo": "< 4", "baixo": "4 - 8", "medio": "9 - 15", "adequado": "16 - 30", "alto": "> 30"},
    "k": {"muito_baixo": "< 0.05", "baixo": "0.05 - 0.10", "medio": "0.11 - 0.20", "adequado": "0.21 - 0.35", "alto": "> 0.35"},
    "v_percent": {"baixo": "< 50", "medio": "50 - 70", "adequado": "70 - 80", "alto": "> 80"}
}

RECOMENDACOES_REGIONAIS = {
    "SP": {"nome": "São Paulo", "referencia": "Boletim 100 - IAC", "ph_ideal": (5.3, 6.0), "v_ideal": 70, "observacao": "Utilizar extrator Resina para P e K"},
    "MG": {"nome": "Minas Gerais", "referencia": "CFSEMG - 5ª Aproximação", "ph_ideal": (6.0, 6.5), "v_ideal": 70, "observacao": "Recomendado para cerrado e mata atlântica"},
    "RS": {"nome": "Rio Grande do Sul", "referencia": "CQFS RS/SC - 2016", "ph_ideal": (5.5, 6.0), "v_ideal": 65, "observacao": "Solos de várzea e planalto"},
    "SC": {"nome": "Santa Catarina", "referencia": "CQFS RS/SC - 2016", "ph_ideal": (5.5, 6.0), "v_ideal": 65, "observacao": "Solos de várzea e planalto"},
    "PR": {"nome": "Paraná", "referencia": "Manual de Adubação - IAPAR", "ph_ideal": (5.5, 6.2), "v_ideal": 65, "observacao": "Região Sul - Manejo conservacionista"},
    "MT": {"nome": "Mato Grosso", "referencia": "Embrapa Cerrados", "ph_ideal": (5.5, 6.5), "v_ideal": 60, "observacao": "Solos de cerrado - Necessidade de gessagem"},
    "GO": {"nome": "Goiás", "referencia": "Embrapa Cerrados", "ph_ideal": (5.5, 6.5), "v_ideal": 60, "observacao": "Solos de cerrado - Necessidade de gessagem"},
    "BA": {"nome": "Bahia", "referencia": "Embrapa Semiárido", "ph_ideal": (5.8, 6.5), "v_ideal": 65, "observacao": "Região semiárida - Manejo conservacionista"},
    "NORDESTE": {"nome": "Região Nordeste", "referencia": "Embrapa Semiárido", "ph_ideal": (5.8, 6.5), "v_ideal": 65, "observacao": "Solos com altos teores de sais"},
    "NORTE": {"nome": "Região Norte", "referencia": "Embrapa Amazônia", "ph_ideal": (5.0, 5.8), "v_ideal": 50, "observacao": "Solos ácidos - Floresta Amazônica"}
}

# ============================================================================
# CULTURAS (EXPANDIDO PARA VASOS)
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
# FUNÇÃO PARA CÁLCULO DE VASOS
# ============================================================================

def calcular_volume_vaso(raio_superior, raio_inferior, altura, formato="tronco_cone"):
    """Calcula o volume do vaso em litros"""
    if formato == "cilindro":
        volume_cm3 = math.pi * (raio_superior ** 2) * altura
    else:  # tronco de cone
        volume_cm3 = (math.pi * altura / 3) * (raio_superior**2 + raio_superior*raio_inferior + raio_inferior**2)
    
    volume_litros = volume_cm3 / 1000
    return round(volume_litros, 2)

def calcular_adubo_para_vaso(cultura, volume_litros, area_plantio_cm2=None):
    """Calcula a quantidade de adubo para vaso baseado nas recomendações de campo"""
    
    req = necessidades_culturas[cultura]
    
    # Fator de conversão: 1 hectare = 10.000 m²
    # Para vaso, usamos proporção baseada na área de plantio típica
    if area_plantio_cm2:
        area_m2 = area_plantio_cm2 / 10000
        fator_escala = area_m2  # 1 m² no campo
    else:
        # Assumindo área de plantio padrão de 1 m² para vaso
        fator_escala = 1
    
    # Cálculo das quantidades (em gramas)
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
# FUNÇÕES GERAIS (PRESERVADAS)
# ============================================================================

def interpretar_pelo_embrapa(parametro, valor):
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
    resultados = {"embrapa": {}, "cfsemg": {}}
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
    return resultados

def recomendar_por_regiao(uf, dados):
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

def listar_modelos_disponiveis():
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

def gerar_resposta_ia(pergunta, dados_solo=None):
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
            """
        prompt = f"""Você é um engenheiro agrônomo especialista em fertilidade do solo. Responda em português do Brasil de forma clara e técnica.

{contexto}

PERGUNTA: {pergunta}

RESPOSTA:"""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent?key={GEMINI_API_KEY}"
        headers = {"Content-Type": "application/json"}
        data = {"contents": [{"parts": [{"text": prompt}]}]}
        response = requests.post(url, headers=headers, json=data, timeout=30)
        if response.status_code == 200:
            resultado = response.json()
            if "candidates" in resultado and resultado["candidates"]:
                return resultado["candidates"][0]["content"]["parts"][0]["text"]
            return "❌ Não foi possível extrair a resposta da IA."
        else:
            return f"❌ **Erro {response.status_code}**"
    except Exception as erro:
        return f"❌ **Erro:** {str(erro)}"

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

def gerar_diagnostico(dados, cultura_req):
    diagnostico = []
    ph_atual = dados.get('ph', 0)
    if ph_atual < cultura_req['ph_min']:
        diagnostico.append(f"🔴 **pH ácido:** {ph_atual:.1f} (ideal: {cultura_req['ph_min']}-{cultura_req['ph_max']}). Calagem necessária.")
    elif ph_atual > cultura_req['ph_max']:
        diagnostico.append(f"🟡 **pH alcalino:** {ph_atual:.1f} (ideal: {cultura_req['ph_min']}-{cultura_req['ph_max']}). Monitorar nutrientes.")
    else:
        diagnostico.append(f"🟢 **pH adequado:** {ph_atual:.1f} dentro da faixa ideal.")
    v_atual = dados.get('v_porcentagem', 0)
    if v_atual < cultura_req['v_desejado']:
        diagnostico.append(f"🔴 **V% baixo:** {v_atual:.1f}% (ideal: ≥{cultura_req['v_desejado']}%). Calagem necessária.")
    else:
        diagnostico.append(f"🟢 **V% adequado:** {v_atual:.1f}%.")
    return diagnostico

def calcular_necessidade_calagem(v_atual, v_desejado, ctc, prnt=85):
    if v_atual >= v_desejado:
        return 0, "✅ Solo já atingiu V% desejado.", 0
    f = 100 / prnt
    nc = (ctc * (v_desejado - v_atual) / 100) * f
    nc = round(nc * 2) / 2
    if nc <= 1.0:
        tempo = 30
    elif nc <= 2.0:
        tempo = 45
    elif nc <= 4.0:
        tempo = 60
    else:
        tempo = 90
    return nc, f"🔹 **Calagem necessária:** {nc:.1f} t/ha", tempo

def recomendar_adubacao_nitrogenio(cultura, n_atual, n_min):
    if n_atual >= n_min:
        return "✅ N adequado."
    return f"❌ N baixo ({n_atual} < {n_min}). Aplicar {n_min - n_atual + 40:.0f} kg/ha de N"

def recomendar_adubacao_fosforo(cultura, p_atual, p_min):
    if p_atual >= p_min:
        return "✅ P adequado."
    return f"❌ P baixo ({p_atual} < {p_min}). Aplicar {p_min - p_atual + 50:.0f} kg/ha de P2O5"

def recomendar_adubacao_potassio(cultura, k_atual, k_min):
    if k_atual >= k_min:
        return "✅ K adequado."
    return f"❌ K baixo ({k_atual:.2f} < {k_min:.2f}). Aplicar {(k_min - k_atual) * 100 + 40:.0f} kg/ha de K2O"

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
        col3, col4, col5 = st.columns(3)
        with col3:
            sand = st.number_input("🏖️ Areia (%)", min_value=0, max_value=100, value=35, step=5)
        with col4:
            silt = st.number_input("🏞️ Silte (%)", min_value=0, max_value=100, value=30, step=5)
        with col5:
            clay = st.number_input("🧱 Argila (%)", min_value=0, max_value=100, value=35, step=5)
        
        soma_textura = sand + silt + clay
        if soma_textura != 100:
            st.warning(f"⚠️ Soma das frações: {soma_textura}%. Ajuste para 100%.")
        else:
            st.success(f"✅ Textura válida! Areia: {sand}%, Silte: {silt}%, Argila: {clay}%")
    
    if st.button("✅ SALVAR DADOS", use_container_width=True):
        soma_textura = sand + silt + clay
        if soma_textura != 100:
            st.error(f"❌ Erro: Soma das frações é {soma_textura}%. Deve ser 100%.")
        else:
            with st.spinner("💾 Salvando..."):
                time.sleep(0.5)
                try:
                    dados = {
                        "nitrogen": float(nitrogen), "phosphorus": float(phosphorus), "potassium": float(potassium),
                        "ph": float(ph), "aluminum": float(aluminum), "calcium": float(calcium),
                        "magnesium": float(magnesium), "h_al": float(h_al), "organic_matter": float(organic_matter),
                        "sand": sand, "silt": silt, "clay": clay
                    }
                    sb = calcular_sb(dados["calcium"], dados["magnesium"], dados["potassium"])
                    ctc = calcular_tct_potencial(sb, dados["h_al"])
                    v = calcular_v_porcentagem(sb, ctc)
                    m = calcular_m_porcentagem(dados["aluminum"], sb)
                    dados["sb"] = sb; dados["ctc"] = ctc; dados["v_porcentagem"] = v; dados["m_porcentagem"] = m
                    st.session_state.dados_basicos = dados
                    st.success("✅ Dados salvos! Vá para a aba **Classificação**.")
                    col_a, col_b, col_c, col_d = st.columns(4)
                    with col_a: st.metric("SB", f"{sb:.2f} cmolc/dm³")
                    with col_b: st.metric("CTC", f"{ctc:.2f} cmolc/dm³")
                    with col_c: st.metric("V%", f"{v:.1f}%")
                    with col_d: st.metric("m%", f"{m:.1f}%")
                except ValueError:
                    st.error("❌ Verifique se todos os valores são números válidos!")

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
    
    aba1, aba2 = st.tabs(["📊 Classificação", "🌱 Adubação"])
    
    with aba1:
        st.markdown("## 📊 Classificação da Fertilidade")
        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric("pH", f"{dados.get('ph', 0):.1f}")
        with col2: st.metric("V%", f"{dados.get('v_porcentagem', 0):.1f}%")
        with col3: st.metric("m%", f"{dados.get('m_porcentagem', 0):.1f}%")
        with col4: st.metric("CTC", f"{dados.get('ctc', 0):.2f}")
        
        st.markdown("---")
        st.markdown(f"### 🔍 Diagnóstico para {cultura}")
        for diag in gerar_diagnostico(dados, req):
            st.markdown(f"- {diag}")
        
        st.markdown("---")
        v = dados.get('v_porcentagem', 0)
        classe = classificar_fertilidade(v)
        if v < 50: st.error(f"**{classe}**")
        elif v < 70: st.warning(f"**{classe}**")
        else: st.success(f"**{classe}**")
        
        st.markdown("---")
        st.markdown("### 📚 Interpretação por Múltiplas Bases")
        interps = interpretar_fertilidade_multiplas_bases(dados)
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("**🌱 Embrapa**")
            for k, v in interps["embrapa"].items(): st.caption(f"• {k}: {v}")
        with col_b:
            st.markdown("**📍 CFSEMG (MG)**")
            for k, v in interps["cfsemg"].items(): st.caption(f"• {k}: {v}")
        
        st.markdown("---")
        st.markdown("### 📍 Recomendação Regional")
        for rec in recomendar_por_regiao(st.session_state.uf_selecionada, dados):
            st.markdown(f"- {rec}")
    
    with aba2:
        st.markdown(f"#### 🌱 Recomendação de Adubação para {cultura}")
        with st.container(border=True):
            st.markdown("**Nitrogênio (N)**")
            n_recomendacao = recomendar_adubacao_nitrogenio(cultura, dados.get('nitrogen', 0), req['n_min'])
            if "✅" in n_recomendacao: st.success(n_recomendacao)
            else: st.warning(n_recomendacao)
        with st.container(border=True):
            st.markdown("**Fósforo (P)**")
            p_recomendacao = recomendar_adubacao_fosforo(cultura, dados.get('phosphorus', 0), req['p_min'])
            if "✅" in p_recomendacao: st.success(p_recomendacao)
            else: st.warning(p_recomendacao)
        with st.container(border=True):
            st.markdown("**Potássio (K)**")
            k_recomendacao = recomendar_adubacao_potassio(cultura, dados.get('potassium', 0), req['k_min'])
            if "✅" in k_recomendacao: st.success(k_recomendacao)
            else: st.warning(k_recomendacao)
        with st.container(border=True):
            st.markdown("**🧪 Calagem**")
            nc, rec, tempo = calcular_necessidade_calagem(dados.get('v_porcentagem', 0), req['v_desejado'], dados.get('ctc', 0))
            if nc > 0: st.warning(rec)
            else: st.success(rec)

# ============================================================================
# ABA 3 - ADUBAÇÃO PARA VASOS (NOVA FUNCIONALIDADE)
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
            st.info(f"📐 **Área de superfície:** {area_superficie:.1f} cm² ({area_superficie/10000:.2f} m²)")
    
    with col2:
        with st.container(border=True):
            st.markdown("**🌾 Seleção da Cultura**")
            cultura_vaso = st.selectbox("Escolha a cultura:", list(necessidades_culturas.keys()), key="cultura_vaso")
            req_vaso = necessidades_culturas[cultura_vaso]
            
            st.markdown("---")
            st.markdown("**📊 Parâmetros da Cultura**")
            col_a, col_b, col_c = st.columns(3)
            with col_a: st.metric("N recomendado (kg/ha)", f"{req_vaso.get('n_recomendado', 80)}")
            with col_b: st.metric("P recomendado (kg/ha)", f"{req_vaso.get('p_recomendado', 60)}")
            with col_c: st.metric("K recomendado (kg/ha)", f"{req_vaso.get('k_recomendado', 80)}")
    
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
                st.caption("Equivalente a: Sulfato de Amônio")
            with col_r2:
                st.metric("💀 Fósforo (P₂O₅)", f"{adubo['P2O5']:.2f} g")
                st.caption("Equivalente a: Superfosfato Simples")
            with col_r3:
                st.metric("🍌 Potássio (K₂O)", f"{adubo['K2O']:.2f} g")
                st.caption("Equivalente a: Cloreto de Potássio")
            
            st.markdown("---")
            st.markdown("### 📋 Recomendações de Aplicação")
            st.markdown(f"""
            - **Cultura:** {adubo['cultura']}
            - **Volume do vaso:** {adubo['volume_litros']:.2f} litros
            - **Área de plantio:** {adubo['area_m2']:.2f} m²
            
            **Como aplicar:**
            1. Misture os fertilizantes uniformemente ao substrato antes do plantio
            2. Para culturas perenes, divida a aplicação em 2-3 parcelas
            3. Regue após a aplicação para melhor absorção
            4. Monitore o desenvolvimento da planta
            """)
            
            st.markdown("</div>", unsafe_allow_html=True)

# ============================================================================
# ABA 4 - ASSISTENTE IA
# ============================================================================

elif menu == "🤖 Assistente IA":
    st.markdown("### 🤖 Assistente IA Gemini")
    st.markdown('<span class="reference-badge">Embrapa</span><span class="reference-badge">CFSEMG</span><span class="reference-badge">Boletim 100</span>', unsafe_allow_html=True)
    
    if not st.session_state.dados_basicos:
        st.info("ℹ️ Para melhores respostas, preencha os dados do solo primeiro!")
    
    pergunta = st.text_area("💬 Faça sua pergunta sobre fertilidade do solo:", height=100)
    
    if st.button("🚀 GERAR RESPOSTA", use_container_width=True):
        if not pergunta:
            st.warning("⚠️ Digite uma pergunta!")
        else:
            with st.spinner("🤖 Consultando IA Gemini..."):
                resposta = gerar_resposta_ia(pergunta, st.session_state.dados_basicos if st.session_state.dados_basicos else None)
                st.markdown(f"""
                <div class="result-card">
                    <h3 style="text-align: center;">🤖 Resposta da IA</h3>
                    <div style="margin-top: 10px;">{resposta}</div>
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
            "Parâmetro": ["N", "P", "K", "pH", "Al", "Ca", "Mg", "H+Al", "MO", "Areia", "Silte", "Argila", "SB", "CTC", "V%", "m%"],
            "Valor": [
                f"{dados.get('nitrogen', 'N/A')} mg/dm³", f"{dados.get('phosphorus', 'N/A')} mg/dm³",
                f"{dados.get('potassium', 'N/A')} cmolc/dm³", f"{dados.get('ph', 'N/A')}",
                f"{dados.get('aluminum', 'N/A')} cmolc/dm³", f"{dados.get('calcium', 'N/A')} cmolc/dm³",
                f"{dados.get('magnesium', 'N/A')} cmolc/dm³", f"{dados.get('h_al', 'N/A')} cmolc/dm³",
                f"{dados.get('organic_matter', 'N/A')} g/kg", f"{dados.get('sand', 'N/A')}%",
                f"{dados.get('silt', 'N/A')}%", f"{dados.get('clay', 'N/A')}%",
                f"{dados.get('sb', 0):.2f} cmolc/dm³", f"{dados.get('ctc', 0):.2f} cmolc/dm³",
                f"{dados.get('v_porcentagem', 0):.1f}%", f"{dados.get('m_porcentagem', 0):.1f}%"
            ]
        }
        st.dataframe(pd.DataFrame(relatorio_data), use_container_width=True, hide_index=True)
        csv = pd.DataFrame(relatorio_data).to_csv(index=False).encode('utf-8')
        st.download_button("📥 Baixar Relatório CSV", csv, "relatorio_solo.csv", "text/csv")
    else:
        st.info("ℹ️ Nenhum dado cadastrado.")

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
        | **Soma de Bases (SB)** | SB = Ca²⁺ + Mg²⁺ + K⁺ | Cátions básicos |
        | **CTC Potencial (T)** | T = SB + (H+Al) | Capacidade de troca |
        | **Saturação por Bases (V%)** | V% = (SB/T) × 100 | Fertilidade do solo |
        | **Saturação por Alumínio (m%)** | m% = (Al³⁺ / (Al³⁺ + SB)) × 100 | Toxicidade por Al |
        """)
    with st.container(border=True):
        st.markdown("""
        ### 🌡️ Classificação do V% (SiBCS)
        - **V% < 50%** → Baixa fertilidade
        - **50% ≤ V% < 70%** → Fertilidade média
        - **70% ≤ V% < 85%** → Fertilidade boa
        - **V% ≥ 85%** → Fertilidade muito boa
        """)

# ============================================================================
# ABA 7 - PESQUISA
# ============================================================================

elif menu == "📋 Pesquisa":
    st.markdown("### 📋 Pesquisa de Satisfação")
    if "pesquisa_respondida" not in st.session_state:
        st.session_state.pesquisa_respondida = False
    
    if not st.session_state.pesquisa_respondida:
        with st.form("pesquisa_form"):
            nota = st.slider("Nota para a plataforma (0-10):", 0, 10, 5)
            sugestoes = st.text_area("Sugestões de melhoria:")
            submitted = st.form_submit_button("📤 ENVIAR")
            if submitted:
                st.session_state.pesquisa_respondida = True
                st.success("✅ Pesquisa enviada! Muito obrigado!")
    else:
        st.success("✅ Você já respondeu à pesquisa! Muito obrigado!")

# ============================================================================
# RODAPÉ
# ============================================================================

st.markdown("---")
col_rodape1, col_rodape2, col_rodape3 = st.columns([1, 2, 1])
with col_rodape2:
    st.caption("© 2026 - Telluriun | Sistema Inteligente de Fertilidade do Solo")
    st.caption("🤖 IA Gemini • 🌱 Embrapa | CFSEMG | Boletim 100 | Regionais")
    st.caption("📧 Contato: laenor@outlook.com")
