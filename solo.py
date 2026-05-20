import streamlit as st
import pandas as pd
import traceback
import sys
import math

# ============================================================================
# BLOCO: FUNÇÃO DE CÁLCULO DO pH
# PALAVRA-CHAVE: ACIDEZ_SOLO
# Descrição: Calcula o pH do solo com base nos teores de alumínio, H+Al,
# cátions básicos (Ca, Mg, K) e matéria orgânica. Retorna 7.0 se tudo zero.
# ============================================================================

def calcular_ph(dados):
    try:
        if (dados.get('calcium', 0) == 0 and 
            dados.get('magnesium', 0) == 0 and 
            dados.get('potassium', 0) == 0 and
            dados.get('aluminum', 0) == 0 and
            dados.get('h_al', 0) == 0):
            return 7.0
        
        fator_acidez = dados.get('aluminum', 0.5) * 0.3 + dados.get('h_al', 3.5) * 0.1
        fator_basicidade = dados.get('calcium', 3.0) * 0.2 + dados.get('magnesium', 1.5) * 0.15 + dados.get('potassium', 0.25) * 0.5
        om = dados.get('organic_matter', 25) / 100
        ph_base = 5.5 + (fator_basicidade - fator_acidez) - (om * 0.5)
        ph = max(4.0, min(8.0, ph_base))
        return round(ph, 1)
    except Exception:
        return 7.0

# ============================================================================
# BLOCO: FUNÇÃO DE CÁLCULO DA NECESSIDADE DE CALAGEM
# PALAVRA-CHAVE: CALAGEM
# Descrição: Calcula a necessidade de calcário em t/ha baseado no método
# da saturação por bases (V%) e no teor de alumínio trocável.
# ============================================================================

def calcular_calagem(v_atual, v_desejado, ctc, prnt=80):
    """Calcula necessidade de calcário em t/ha"""
    if v_atual >= v_desejado:
        return 0
    nc = ((v_desejado - v_atual) * ctc) / 100
    nc_corrigida = nc * (100 / prnt)
    return round(nc_corrigida, 2)

# ============================================================================
# BLOCO: FUNÇÃO DE CÁLCULO DA GESSAGEM
# PALAVRA-CHAVE: GESSAGEM
# Descrição: Recomenda gessagem para solos com argila > 350 g/kg ou
# com necessidade de correção de alumínio em profundidade.
# ============================================================================

def calcular_gessagem(calagem_t_ha, clay_gkg):
    """Calcula necessidade de gesso em t/ha"""
    if calagem_t_ha > 0 and clay_gkg >= 350:
        return round(calagem_t_ha * 0.5, 2)
    elif clay_gkg > 200:
        return round(calagem_t_ha * 0.3, 2)
    return 0

# ============================================================================
# BLOCO: FUNÇÃO DE RECOMENDAÇÃO DE N, P, K
# PALAVRA-CHAVE: NPK
# Descrição: Recomenda adubação nitrogenada, fosfatada e potássica
# baseada na cultura e nos teores de P e K do solo.
# ============================================================================

def recomendar_npk(cultura, p_atual, k_atual, p_min, k_min, p_recomendacao, k_recomendacao, n_base):
    """Recomenda adubação NPK baseada na análise do solo"""
    
    # Nitrogênio
    if "Soja" in cultura:
        n_recomendacao = 20  # Soja fixa N, necessidade mínima
    else:
        n_recomendacao = n_base
    
    # Fósforo
    if p_atual < p_min:
        if p_atual < p_min * 0.5:
            p_recomendacao = p_recomendacao * 1.5
        p_obs = f"🔴 Baixo - Aplicar {p_recomendacao:.0f} kg/ha P₂O₅"
    else:
        p_obs = f"✅ Adequado - Aplicar {p_recomendacao * 0.5:.0f} kg/ha P₂O₅ (manutenção)"
    
    # Potássio
    if k_atual < k_min:
        if k_atual < k_min * 0.5:
            k_recomendacao = k_recomendacao * 1.5
        k_obs = f"🔴 Baixo - Aplicar {k_recomendacao:.0f} kg/ha K₂O"
    else:
        k_obs = f"✅ Adequado - Aplicar {k_recomendacao * 0.5:.0f} kg/ha K₂O (manutenção)"
    
    return n_recomendacao, p_recomendacao, k_recomendacao, p_obs, k_obs

# ============================================================================
# BLOCO: FUNÇÃO DE ADUBAÇÃO PARA VASO
# PALAVRA-CHAVE: CONVERSAO_VASO
# Descrição: Converte recomendação de kg/ha para gramas por vaso,
# considerando a área do vaso em metros quadrados.
# ============================================================================

def calcular_adubacao_vaso(area_vaso_m2, recomendacao_kg_ha):
    kg_por_m2 = recomendacao_kg_ha / 10000
    kg_vaso = kg_por_m2 * area_vaso_m2
    gramas_vaso = kg_vaso * 1000
    return round(gramas_vaso, 2)

# ============================================================================
# BLOCO: IMPORTAÇÃO DO MODELO DE IA
# PALAVRA-CHAVE: MODELO_JOBLIB
# Descrição: Tenta carregar o modelo treinado (modelo.pkl) e as features
# necessárias para a classificação por Inteligência Artificial.
# ============================================================================

try:
    import joblib
    JOBLIB_AVAILABLE = True
except ImportError:
    JOBLIB_AVAILABLE = False
    joblib = None

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None

@st.cache_resource
def carregar_modelo():
    if not JOBLIB_AVAILABLE:
        st.sidebar.warning("⚠️ Biblioteca 'joblib' não encontrada.")
        return None, None
    try:
        import os
        if not os.path.exists('modelo.pkl') or not os.path.exists('features.pkl'):
            return None, None
        modelo = joblib.load('modelo.pkl')
        features = joblib.load('features.pkl')
        st.sidebar.success(f"✅ Modelo carregado com {len(features)} features")
        return modelo, features
    except Exception as e:
        st.sidebar.error(f"❌ Erro: {str(e)}")
        return None, None

modelo, features = carregar_modelo()

# ============================================================================
# BLOCO: CONFIGURAÇÃO DA PÁGINA E CSS
# PALAVRA-CHAVE: ESTILIZACAO
# Descrição: Define o layout da página, título, ícone e aplica CSS customizado
# para tabs com texto sempre visível e métricas com alto contraste.
# ============================================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

* {
    font-family: 'Outfit', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #f5f7fa 0%, #eef2f7 100%) !important;
}

.main .block-container {
    background: rgba(255, 255, 255, 0.92) !important;
    backdrop-filter: blur(10px) !important;
    border-radius: 32px !important;
    padding: 2rem !important;
    margin-top: 1rem !important;
    margin-bottom: 2rem !important;
    box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.08) !important;
    border: 1px solid rgba(255, 255, 255, 0.3) !important;
}

h1, h2, h3 {
    background: linear-gradient(120deg, #2d5a3b 0%, #4a8c5c 100%) !important;
    -webkit-background-clip: text !important;
    background-clip: text !important;
    color: transparent !important;
    font-weight: 700 !important;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a3022 0%, #0e1e14 100%) !important;
    border-right: none !important;
    box-shadow: 4px 0 20px rgba(0, 0, 0, 0.05) !important;
}

section[data-testid="stSidebar"] * {
    color: #e8f0e5 !important;
}

.stTextInput input, 
.stNumberInput input, 
textarea, 
input,
div[data-baseweb="select"] > div {
    background-color: #ffffff !important;
    border: 2px solid #e2e8f0 !important;
    border-radius: 14px !important;
    padding: 12px 16px !important;
    color: #1a2a1f !important;
    font-weight: 500 !important;
    transition: all 0.3s ease !important;
}

.stTextInput input:not([value="0"]):not([value="0.0"]),
.stNumberInput input:not([value="0"]):not([value="0.0"]) {
    background: linear-gradient(95deg, #f0fdf4 0%, #ecfdf5 100%) !important;
    border-color: #86efac !important;
}

.stTextInput input:focus, 
.stNumberInput input:focus {
    border-color: #4a8c5c !important;
    box-shadow: 0 0 0 4px rgba(74, 140, 92, 0.15) !important;
    outline: none !important;
}

.stButton > button {
    background: linear-gradient(95deg, #2d5a3b 0%, #4a8c5c 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 40px !important;
    padding: 0.7rem 2rem !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 12px rgba(45, 90, 59, 0.2) !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 20px rgba(45, 90, 59, 0.3) !important;
}

/* ========== MÉTRICAS CORRIGIDAS ========== */
div[data-testid="stMetric"] {
    background: #ffffff !important;
    border-radius: 24px !important;
    padding: 1.2rem !important;
    border: 2px solid #d4e8d4 !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05) !important;
}
div[data-testid="stMetricLabel"] {
    color: #2d5a3b !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
}
div[data-testid="stMetricValue"] {
    color: #1a5a3a !important;
    font-weight: 900 !important;
    font-size: 2rem !important;
}

/* ========== TABS CORRIGIDAS ========== */
button[data-baseweb="tab"] {
    background: #e8ece8 !important;
    color: #1a3a2a !important;
    font-weight: 700 !important;
    border-radius: 30px !important;
    padding: 0.6rem 1.5rem !important;
    margin: 0 4px !important;
    border: 1px solid #c8dcc8 !important;
}
button[data-baseweb="tab"]:hover {
    background: #d4e4d4 !important;
    border-color: #4a8c5c !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    background: linear-gradient(95deg, #2d5a3b 0%, #4a8c5c 100%) !important;
    color: white !important;
    border-color: transparent !important;
}

/* ========== DATAFRAME CORRIGIDO (TABELA DE RECOMENDAÇÕES) ========== */
.dataframe {
    background: #ffffff !important;
    border-radius: 20px !important;
    overflow: hidden !important;
    border: 2px solid #4a8c5c !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
}
.dataframe th {
    background: linear-gradient(95deg, #2d5a3b 0%, #3a6b48 100%) !important;
    color: white !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    padding: 15px 12px !important;
    text-align: center !important;
}
.dataframe td {
    color: #1a2a1f !important;
    font-weight: 500 !important;
    padding: 12px !important;
    background: #ffffff !important;
    border-bottom: 1px solid #e0e8e0 !important;
    text-align: center !important;
}
.dataframe tr:hover td {
    background: #f0f8f0 !important;
}

/* ========== CARDS DE RECOMENDAÇÃO ========== */
.recomendacao-card {
    background: linear-gradient(135deg, #ffffff 0%, #f8faf8 100%) !important;
    border-radius: 20px !important;
    padding: 1.5rem !important;
    margin: 1rem 0 !important;
    border: 2px solid #4a8c5c !important;
    box-shadow: 0 4px 15px rgba(74, 140, 92, 0.15) !important;
}
.recomendacao-card h4 {
    color: #2d5a3b !important;
    font-weight: 800 !important;
    margin-bottom: 1rem !important;
}

/* ========== ALERTAS E INFOS ========== */
.stAlert {
    border-radius: 16px !important;
    border: none !important;
    background: #fefdf7 !important;
    border-left: 4px solid #4a8c5c !important;
}
.stInfo {
    background: #e8f5e9 !important;
    color: #2d5a3b !important;
    border-radius: 16px !important;
    border-left: 4px solid #4a8c5c !important;
}
.stSuccess {
    background: #e8f5e9 !important;
    color: #2d5a3b !important;
}
.stWarning {
    background: #fff8e1 !important;
    color: #856404 !important;
}
.stError {
    background: #ffebee !important;
    color: #c62828 !important;
}

.streamlit-expanderHeader {
    background: #ffffff !important;
    border-radius: 16px !important;
    color: #2d5a3b !important;
    font-weight: 600 !important;
    border: 1px solid #e2e8f0 !important;
}
.streamlit-expanderContent {
    background: #ffffff !important;
    border-radius: 0 0 16px 16px !important;
    border: 1px solid #e2e8f0 !important;
    border-top: none !important;
}

hr {
    margin: 2rem 0 !important;
    border: none !important;
    height: 2px !important;
    background: linear-gradient(90deg, transparent, #4a8c5c, #86efac, #4a8c5c, transparent) !important;
}

.custom-header {
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.95), rgba(248, 250, 245, 0.95));
    backdrop-filter: blur(10px);
    border-radius: 28px;
    padding: 1.5rem 2rem;
    margin-bottom: 2rem;
    border: 1px solid rgba(74, 140, 92, 0.2);
}

.version-badge {
    background: linear-gradient(95deg, #e8f5e9, #d4edda);
    color: #2d5a3b;
    border-radius: 40px;
    padding: 0.25rem 1rem;
    font-size: 0.7rem;
    font-weight: 600;
    display: inline-block;
}

label {
    color: #4a5b44 !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
}

/* Cores para texto dentro da tabela */
.css-1y0tads tr td {
    color: #1a2a1f !important;
}

/* Ajuste para métricas dentro da aba 5 */
.stMarkdown p {
    color: #1a2a1f !important;
}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# BLOCO: CABECALHO E SIDEBAR
# ============================================================================

st.markdown("""
<div class="custom-header">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
        <div>
            <h1 style="margin-bottom: 0.3rem;">🌿 Classificador Inteligente de Fertilidade do Solo</h1>
            <p style="color: #5a6e5a;">Sistema Brasileiro de Classificação de Solos (SiBCS) · Embrapa</p>
        </div>
        <div class="version-badge">📊 Análise em Tempo Real</div>
    </div>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2934/2934128.png", width=80)
    st.markdown("### 📊 Sobre o Sistema")
    st.markdown("""
    - ✅ Avaliação da fertilidade do solo
    - ✅ Classificação agrícola profissional
    - ✅ Recomendação de calagem e gessagem
    - ✅ Recomendação de N, P, K
    - ✅ Relatórios técnicos detalhados
    - ✅ Cálculo de adubação para vasos
    """)
    st.markdown("---")
    st.markdown("### 🤖 Status da IA")
    if not JOBLIB_AVAILABLE:
        st.error("⚠️ joblib não instalado")
    elif modelo is not None and features is not None:
        st.success("✅ IA carregada com sucesso!")
        st.caption(f"🎯 Features: {len(features)}")
    else:
        st.warning("⚠️ IA não disponível")
    st.markdown("---")
    st.caption("✨ Versão 9.0 — Recomendações Completas")
    st.caption("Desenvolvido com Streamlit")

# ============================================================================
# BLOCO: SESSION STATE
# ============================================================================

if "dados_basicos" not in st.session_state:
    st.session_state.dados_basicos = {}
if "dados_calculados" not in st.session_state:
    st.session_state.dados_calculados = {}
if "dados_salvos" not in st.session_state:
    st.session_state.dados_salvos = False
if "classificacao_realizada" not in st.session_state:
    st.session_state.classificacao_realizada = False

# ============================================================================
# BLOCO: MENU DE NAVEGAÇÃO (5 ABAS)
# ============================================================================

menu = st.radio(
    "Navegação",
    ["📊 1. Dados do Solo", "🌱 2. Classificação", "🧪 3. Adubação (Vaso)", "📈 4. Relatório", "🎯 5. Recomendações"],
    horizontal=True,
    label_visibility="collapsed"
)

# ============================================================================
# BLOCO: DICIONÁRIOS DE CULTURAS
# ============================================================================

necessidades_culturas = {
    "Soja": {"v_desejado": 60, "ph_min": 5.5, "ph_max": 6.5, "p_min": 15, "k_min": 0.35, "p_rec": 80, "k_rec": 60, "n_base": 20},
    "Milho Grão": {"v_desejado": 65, "ph_min": 5.5, "ph_max": 6.5, "p_min": 20, "k_min": 0.40, "p_rec": 100, "k_rec": 80, "n_base": 120},
    "Milho Semente": {"v_desejado": 65, "ph_min": 5.5, "ph_max": 6.5, "p_min": 20, "k_min": 0.40, "p_rec": 100, "k_rec": 80, "n_base": 120},
    "Sorgo": {"v_desejado": 55, "ph_min": 5.2, "ph_max": 6.2, "p_min": 12, "k_min": 0.30, "p_rec": 60, "k_rec": 50, "n_base": 90},
    "Milheto": {"v_desejado": 50, "ph_min": 5.0, "ph_max": 6.0, "p_min": 10, "k_min": 0.25, "p_rec": 50, "k_rec": 40, "n_base": 70},
    "Feijão": {"v_desejado": 65, "ph_min": 5.5, "ph_max": 6.5, "p_min": 20, "k_min": 0.35, "p_rec": 80, "k_rec": 60, "n_base": 40},
    "Café": {"v_desejado": 70, "ph_min": 5.5, "ph_max": 6.5, "p_min": 25, "k_min": 0.40, "p_rec": 120, "k_rec": 100, "n_base": 180},
    "Pastagem": {"v_desejado": 50, "ph_min": 5.0, "ph_max": 6.0, "p_min": 10, "k_min": 0.25, "p_rec": 60, "k_rec": 50, "n_base": 80},
    "Algodão": {"v_desejado": 70, "ph_min": 5.5, "ph_max": 6.5, "p_min": 25, "k_min": 0.45, "p_rec": 120, "k_rec": 100, "n_base": 140},
    "Cana-de-açúcar": {"v_desejado": 60, "ph_min": 5.5, "ph_max": 6.5, "p_min": 15, "k_min": 0.30, "p_rec": 100, "k_rec": 120, "n_base": 100},
    "Trigo": {"v_desejado": 65, "ph_min": 5.5, "ph_max": 6.5, "p_min": 18, "k_min": 0.35, "p_rec": 80, "k_rec": 60, "n_base": 110},
    "Tomate": {"v_desejado": 80, "ph_min": 6.0, "ph_max": 6.8, "p_min": 30, "k_min": 0.50, "p_rec": 150, "k_rec": 120, "n_base": 150},
    "Citrus": {"v_desejado": 70, "ph_min": 5.5, "ph_max": 6.5, "p_min": 20, "k_min": 0.35, "p_rec": 100, "k_rec": 80, "n_base": 130},
    "Arroz": {"v_desejado": 50, "ph_min": 5.0, "ph_max": 6.0, "p_min": 10, "k_min": 0.25, "p_rec": 60, "k_rec": 50, "n_base": 85}
}

# ============================================================================
# BLOCO: FUNÇÃO DE PREDIÇÃO IA
# ============================================================================

def fazer_predicao_ia(dados):
    if not JOBLIB_AVAILABLE or modelo is None or features is None:
        return None, "IA não disponível"
    try:
        features_disponiveis = {
            "nitrogen": dados.get("nitrogen", 0), "phosphorus": dados.get("phosphorus", 0),
            "potassium": dados.get("potassium", 0), "ph": dados.get("ph", 7.0),
            "organic_matter": dados.get("organic_matter", 0), "bulk_density": dados.get("bulk_density", 0),
            "sand": dados.get("sand", 0), "silt": dados.get("silt", 0), "clay": dados.get("clay", 0),
            "calcium": dados.get("calcium", 0), "magnesium": dados.get("magnesium", 0),
            "aluminum": dados.get("aluminum", 0), "h_al": dados.get("h_al", 0),
            "particle_density": dados.get("particle_density", 2.65)
        }
        valores = [features_disponiveis.get(feature, 0) for feature in features]
        entrada_ia = pd.DataFrame([valores], columns=features)
        predicao = modelo.predict(entrada_ia)
        
        ph = dados.get("ph", 7.0)
        v_percent = dados.get("v_percent", 0)
        if ph < 5.5 or v_percent < 50:
            return "🔴 BAIXA FERTILIDADE (Solo Ácido/Distrófico)", "Sucesso"
        elif ph > 7.0:
            return "🟡 ALCALINIDADE (Fertilidade Reduzida)", "Sucesso"
        else:
            mapeamento = {0: "🔴 BAIXA FERTILIDADE", 1: "🟢 ALTA FERTILIDADE"}
            return mapeamento.get(predicao[0], "🔴 BAIXA FERTILIDADE"), "Sucesso"
    except Exception as e:
        return None, f"Erro: {str(e)}"

# ============================================================================
# ABA 1 - DADOS DO SOLO
# ============================================================================

if menu == "📊 1. Dados do Solo":
    st.markdown("## 📋 Dados Básicos do Solo")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🌱 Macronutrientes")
        nitrogen = st.text_input("Nitrogênio (N) - mg/dm³", value="0.0", key="n_input")
        phosphorus = st.text_input("Fósforo (P) - mg/dm³", value="0.0", key="p_input")
        potassium = st.text_input("Potássio (K+) - cmolc/dm³", value="0.0", key="k_input")
        st.markdown("### 🍂 Matéria Orgânica")
        organic_matter = st.text_input("Matéria Orgânica (g/kg)", value="0.0", key="om_input")
    with col2:
        st.markdown("### 📦 Densidade do Solo")
        bulk_density = st.text_input("Densidade do Solo (g/cm³)", value="0.0", key="bd_input")
        particle_density = st.text_input("Densidade de Partícula (g/cm³)", value="2.65", key="pd_input")
        st.markdown("### 🧱 Composição Textural")
        sand = st.text_input("Areia (g/kg)", value="0.0", key="sand_input")
        silt = st.text_input("Silte (g/kg)", value="0.0", key="silt_input")
        clay = st.text_input("Argila (g/kg)", value="0.0", key="clay_input")
    st.markdown("---")
    if st.button("💾 SALVAR DADOS BÁSICOS", key="salvar_basicos"):
        try:
            st.session_state.dados_basicos = {
                "nitrogen": float(nitrogen.replace(",", ".")), "phosphorus": float(phosphorus.replace(",", ".")),
                "potassium": float(potassium.replace(",", ".")), "organic_matter": float(organic_matter.replace(",", ".")),
                "bulk_density": float(bulk_density.replace(",", ".")), "particle_density": float(particle_density.replace(",", ".")),
                "sand": float(sand.replace(",", ".")), "silt": float(silt.replace(",", ".")), "clay": float(clay.replace(",", "."))
            }
            st.session_state.dados_salvos = True
            st.success("✅ Dados salvos! Vá para aba 'Classificação'.")
        except Exception as e:
            st.error(f"❌ Erro: {str(e)}")

# ============================================================================
# ABA 2 - CLASSIFICAÇÃO
# ============================================================================

elif menu == "🌱 2. Classificação":
    if not st.session_state.dados_salvos:
        st.warning("⚠️ Preencha e salve os dados na ABA 1 primeiro!")
        st.stop()
    st.markdown("## 🌱 Classificação da Fertilidade")
    col1, col2 = st.columns(2)
    with col1:
        aluminum = st.text_input("Alumínio (Al³⁺) - cmolc/dm³", value="0.0", key="al_input")
        h_al = st.text_input("H + Al - cmolc/dm³", value="0.0", key="hal_input")
    with col2:
        calcium = st.text_input("Cálcio (Ca²⁺) - cmolc/dm³", value="0.0", key="ca_input")
        magnesium = st.text_input("Magnésio (Mg²⁺) - cmolc/dm³", value="0.0", key="mg_input")
        cultura = st.selectbox("🌾 Cultura", list(necessidades_culturas.keys()), key="cultura_select")
    st.markdown("---")
    if st.button("🔬 REALIZAR CLASSIFICAÇÃO", key="classificar"):
        try:
            dados = st.session_state.dados_basicos.copy()
            dados["aluminum"] = float(aluminum.replace(",", "."))
            dados["h_al"] = float(h_al.replace(",", "."))
            dados["calcium"] = float(calcium.replace(",", "."))
            dados["magnesium"] = float(magnesium.replace(",", "."))
            dados["cultura"] = cultura
            dados["ph"] = calcular_ph(dados)
            sb = dados["calcium"] + dados["magnesium"] + dados["potassium"]
            ctc_efetiva = sb + dados["aluminum"]
            ctc_potencial = sb + dados["h_al"]
            v_percent = (sb / ctc_potencial) * 100 if ctc_potencial > 0 else 0
            m_percent = (dados["aluminum"] / ctc_efetiva) * 100 if ctc_efetiva > 0 else 0
            dados["v_percent"] = v_percent
            
            st.session_state.dados_calculados = dados
            st.session_state.sb = sb
            st.session_state.ctc_potencial = ctc_potencial
            st.session_state.v_percent = v_percent
            st.session_state.m_percent = m_percent
            st.session_state.cultura_selecionada = cultura
            st.session_state.classificacao_realizada = True
            
            st.success("✅ Classificação realizada!")
            col_r1, col_r2, col_r3 = st.columns(3)
            col_r1.metric("pH do Solo", f"{dados['ph']:.1f}")
            col_r2.metric("CTC Potencial", f"{ctc_potencial:.2f} cmolc/dm³")
            col_r3.metric("Saturação por Bases (V%)", f"{v_percent:.1f}%")
            
            st.markdown("---")
            st.markdown("### 🤖 Classificação por IA")
            if modelo is not None:
                with st.spinner("🔄 IA processando..."):
                    predicao, status = fazer_predicao_ia(dados)
                    if predicao:
                        st.success(f"🌾 **Classe prevista:** {predicao}")
                    else:
                        st.warning(f"⚠️ {status}")
            else:
                st.info("ℹ️ Modelo de IA não disponível")
        except Exception as e:
            st.error(f"❌ Erro: {str(e)}")

# ============================================================================
# ABA 3 - ADUBAÇÃO PARA VASO
# ============================================================================

elif menu == "🧪 3. Adubação (Vaso)":
    st.markdown("## 🧪 Cálculo de Adubação para Vaso")
    st.markdown("### 🧑‍🔬 Bem-vindo, Pesquisador! Faça aqui os cálculos para seu experimento!")
    
    if not st.session_state.classificacao_realizada:
        st.warning("⚠️ Execute a classificação na ABA 2 primeiro!")
        if st.button("📊 Usar demonstração"):
            st.session_state.classificacao_realizada = True
            st.session_state.dados_calculados = {"phosphorus": 5.0, "potassium": 0.15, "clay": 200}
            st.session_state.cultura_selecionada = "Soja"
            st.rerun()
        st.stop()
    
    st.info("🌱 **Recomendação baseada na análise do solo!**")
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        altura_cm = st.number_input("Altura (cm)", min_value=5.0, value=20.0, step=1.0)
    with col_v2:
        diametro_cm = st.number_input("Diâmetro (cm)", min_value=5.0, value=10.0, step=1.0)
    
    area_m2 = math.pi * ((diametro_cm/2) ** 2) / 10000
    st.caption(f"📐 Área do vaso: **{area_m2:.4f} m²**")
    
    cultura = st.session_state.cultura_selecionada
    dados_cultura = necessidades_culturas[cultura]
    st.success(f"Cultura: **{cultura}**")
    
    dados = st.session_state.dados_calculados
    p_atual = dados.get("phosphorus", 0)
    k_atual = dados.get("potassium", 0)
    
    # Calcular recomendações para vaso
    n_vaso = calcular_adubacao_vaso(area_m2, dados_cultura["n_base"])
    p_vaso = calcular_adubacao_vaso(area_m2, dados_cultura["p_rec"])
    k_vaso = calcular_adubacao_vaso(area_m2, dados_cultura["k_rec"])
    
    # Ajustes baseados na análise
    if p_atual < dados_cultura["p_min"]:
        p_vaso = p_vaso * 1.5
    if k_atual < dados_cultura["k_min"]:
        k_vaso = k_vaso * 1.5
    
    st.markdown("---")
    st.markdown("### 📊 Resultado para o Vaso")
    
    col_r1, col_r2, col_r3 = st.columns(3)
    col_r1.metric("Nitrogênio (N)", f"{n_vaso:.2f} g")
    col_r2.metric("Fósforo (P₂O₅)", f"{p_vaso:.2f} g")
    col_r3.metric("Potássio (K₂O)", f"{k_vaso:.2f} g")
    
    st.markdown(f"""
    **🧴 Modo de aplicação sugerido:**
    - Misturar **{n_vaso:.2f}g de N** + **{p_vaso:.2f}g de P₂O₅** + **{k_vaso:.2f}g de K₂O** no solo do vaso
    - Para ureia (45% N): use **{(n_vaso/0.45):.2f}g**
    - Para superfosfato simples (18% P₂O₅): use **{(p_vaso/0.18):.2f}g**
    - Para cloreto de potássio (60% K₂O): use **{(k_vaso/0.60):.2f}g**
    """)

# ============================================================================
# ABA 4 - RELATÓRIO
# ============================================================================

elif menu == "📈 4. Relatório":
    if not st.session_state.classificacao_realizada:
        st.warning("⚠️ Execute a classificação na ABA 2 primeiro!")
        st.stop()
    st.markdown("## 📈 Relatório Técnico")
    
    dados = st.session_state.dados_calculados
    sb = st.session_state.sb
    ctc = st.session_state.ctc_potencial
    v_percent = st.session_state.v_percent
    
    relatorio = pd.DataFrame({
        "Parâmetro": ["pH", "N (mg/dm³)", "P (mg/dm³)", "K (cmolc/dm³)", "Ca (cmolc/dm³)",
                      "Mg (cmolc/dm³)", "Al (cmolc/dm³)", "H+Al (cmolc/dm³)", "SB (cmolc/dm³)",
                      "CTC (cmolc/dm³)", "V%", "Mat. Orgânica (g/kg)", "Areia (g/kg)", "Silte (g/kg)", "Argila (g/kg)"],
        "Valor": [f"{dados['ph']:.1f}", f"{dados['nitrogen']:.1f}", f"{dados['phosphorus']:.1f}",
                  f"{dados['potassium']:.2f}", f"{dados['calcium']:.2f}", f"{dados['magnesium']:.2f}",
                  f"{dados['aluminum']:.2f}", f"{dados['h_al']:.2f}", f"{sb:.2f}",
                  f"{ctc:.2f}", f"{v_percent:.1f}%", f"{dados['organic_matter']:.1f}",
                  f"{dados['sand']:.0f}", f"{dados['silt']:.0f}", f"{dados['clay']:.0f}"]
    })
    st.dataframe(relatorio, hide_index=True, use_container_width=True)
    
    csv = relatorio.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Baixar CSV", data=csv, file_name="relatorio_solo.csv", mime="text/csv")

# ============================================================================
# ABA 5 - RECOMENDAÇÕES (COMPLETA COM CALAGEM, GESSAGEM, N, P, K)
# ============================================================================

elif menu == "🎯 5. Recomendações":
    st.markdown("## 🎯 Recomendações Técnicas Completas")
    
    if not st.session_state.classificacao_realizada:
        st.warning("⚠️ Execute a classificação na ABA 2 primeiro para gerar as recomendações!")
        if st.button("📊 Usar demonstração"):
            st.session_state.classificacao_realizada = True
            st.session_state.dados_calculados = {
                "ph": 5.2, "phosphorus": 5.0, "potassium": 0.15, "clay": 400,
                "calcium": 1.5, "magnesium": 0.8, "aluminum": 0.8, "h_al": 4.0,
                "v_percent": 35, "organic_matter": 20
            }
            st.session_state.ctc_potencial = 8.0
            st.session_state.sb = 2.5
            st.session_state.v_percent = 35
            st.session_state.cultura_selecionada = "Soja"
            st.session_state.classificacao_realizada = True
            st.rerun()
        st.stop()
    
    cultura = st.session_state.cultura_selecionada
    dados_cultura = necessidades_culturas[cultura]
    dados = st.session_state.dados_calculados
    
    # Dados do solo
    ph_atual = dados.get("ph", 7.0)
    p_atual = dados.get("phosphorus", 0)
    k_atual = dados.get("potassium", 0)
    ca_atual = dados.get("calcium", 0)
    mg_atual = dados.get("magnesium", 0)
    al_atual = dados.get("aluminum", 0)
    h_al_atual = dados.get("h_al", 0)
    v_atual = st.session_state.v_percent
    ctc = st.session_state.ctc_potencial
    clay = dados.get("clay", 0)
    mo = dados.get("organic_matter", 0)
    
    # Calcular calagem
    v_desejado = dados_cultura["v_desejado"]
    calagem_t = calcular_calagem(v_atual, v_desejado, ctc, prnt=80)
    
    # Calcular gessagem
    gessagem_t = calcular_gessagem(calagem_t, clay)
    
    # Calcular recomendações NPK
    n_rec = dados_cultura["n_base"]
    p_rec_base = dados_cultura["p_rec"]
    k_rec_base = dados_cultura["k_rec"]
    
    # Ajustes por análise de solo
    if p_atual < dados_cultura["p_min"]:
        if p_atual < dados_cultura["p_min"] * 0.5:
            p_rec = p_rec_base * 1.5
            p_status = "🔴 Muito Baixo"
        else:
            p_rec = p_rec_base * 1.2
            p_status = "🟠 Baixo"
        p_obs = f"Aplicar {p_rec:.0f} kg/ha de P₂O₅"
    else:
        p_rec = p_rec_base * 0.5
        p_status = "🟢 Adequado"
        p_obs = f"Aplicar {p_rec:.0f} kg/ha de P₂O₅ (manutenção)"
    
    if k_atual < dados_cultura["k_min"]:
        if k_atual < dados_cultura["k_min"] * 0.5:
            k_rec = k_rec_base * 1.5
            k_status = "🔴 Muito Baixo"
        else:
            k_rec = k_rec_base * 1.2
            k_status = "🟠 Baixo"
        k_obs = f"Aplicar {k_rec:.0f} kg/ha de K₂O"
    else:
        k_rec = k_rec_base * 0.5
        k_status = "🟢 Adequado"
        k_obs = f"Aplicar {k_rec:.0f} kg/ha de K₂O (manutenção)"
    
    # Ajuste N para Soja
    if "Soja" in cultura:
        n_obs = f"Aplicar {n_rec:.0f} kg/ha de N (inoculação + cobertura)"
    else:
        n_obs = f"Aplicar {n_rec:.0f} kg/ha de N (parcelado em 2-3 vezes)"
    
    # Exibir resultados
    st.markdown(f"### 🌾 Cultura Selecionada: **{cultura}**")
    
    # Cards de resumo
    col_res1, col_res2, col_res3 = st.columns(3)
    with col_res1:
        st.metric("pH do Solo", f"{ph_atual:.1f}", delta="Ideal: 5.5-6.5")
    with col_res2:
        st.metric("CTC Potencial", f"{ctc:.2f} cmolc/dm³")
    with col_res3:
        st.metric("V% Atual", f"{v_atual:.1f}%", delta=f"Alvo: {v_desejado}%")
    
    st.markdown("---")
    
    # Seção de Calagem e Gessagem
    st.markdown("## 🪨 Correção do Solo")
    
    col_cal1, col_cal2 = st.columns(2)
    with col_cal1:
        st.markdown('<div class="recomendacao-card">', unsafe_allow_html=True)
        st.markdown("#### 🧱 Calagem")
        if calagem_t > 0:
            st.warning(f"**Necessidade de Calcário:** {calagem_t} t/ha")
            st.caption(f"Calcular com PRNT 80% | V% desejado: {v_desejado}%")
            st.info("💡 Aplicar 30-60 dias antes do plantio, incorporado na camada de 0-20cm")
        else:
            st.success("✅ Solo com V% adequado. Calagem não necessária!")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_cal2:
        st.markdown('<div class="recomendacao-card">', unsafe_allow_html=True)
        st.markdown("#### 💎 Gessagem")
        if gessagem_t > 0:
            st.info(f"**Recomendação de Gesso:** {gessagem_t} t/ha")
            st.caption("Necessário para solos com alto teor de argila e alumínio")
        else:
            st.success("✅ Gessagem não necessária para esta cultura/solo")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Seção de Adubação NPK
    st.markdown("## 🌱 Adubação NPK")
    
    col_n1, col_n2, col_n3 = st.columns(3)
    with col_n1:
        st.markdown('<div class="recomendacao-card">', unsafe_allow_html=True)
        st.markdown("#### ⚛️ Nitrogênio (N)")
        st.markdown(f"**{n_rec} kg/ha**")
        st.caption(n_obs)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_n2:
        st.markdown('<div class="recomendacao-card">', unsafe_allow_html=True)
        st.markdown("#### 🪨 Fósforo (P₂O₅)")
        st.markdown(f"**Status:** {p_status}")
        st.markdown(f"**Recomendação:** {p_rec} kg/ha")
        st.caption(p_obs)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_n3:
        st.markdown('<div class="recomendacao-card">', unsafe_allow_html=True)
        st.markdown("#### 🍌 Potássio (K₂O)")
        st.markdown(f"**Status:** {k_status}")
        st.markdown(f"**Recomendação:** {k_rec} kg/ha")
        st.caption(k_obs)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Resumo completo
    st.markdown("## 📋 Resumo das Recomendações")
    
    resumo = pd.DataFrame({
        "Recomendação": ["Calagem", "Gessagem", "Nitrogênio (N)", "Fósforo (P₂O₅)", "Potássio (K₂O)"],
        "Dose (kg/ha)": [f"{calagem_t:.2f} t/ha" if calagem_t > 0 else "Não necessária",
                         f"{gessagem_t:.2f} t/ha" if gessagem_t > 0 else "Não necessária",
                         f"{n_rec} kg/ha", f"{p_rec} kg/ha", f"{k_rec} kg/ha"],
        "Observação": [f"Elevar V% de {v_atual:.0f}% para {v_desejado}%",
                      "Aplica-se em solos argilosos" if gessagem_t > 0 else "Não se aplica",
                      n_obs, p_obs, k_obs]
    })
    
    st.dataframe(resumo, hide_index=True, use_container_width=True)
    
    # Botão para baixar recomendações
    csv_resumo = resumo.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Baixar Recomendações (CSV)", data=csv_resumo, file_name="recomendacoes.csv", mime="text/csv")
    
    st.caption("💡 *Recomendações baseadas no Manual de Adubação e Calagem para o Estado de São Paulo (IAC) e SiBCS-Embrapa*")

# ============================================================================
# BLOCO: RODAPÉ
# ============================================================================

st.markdown("---")
st.caption("© 2026 - Classificador de Fertilidade do Solo | SiBCS - Embrapa | Versão 9.0 - Recomendações Completas")
