import streamlit as st
import pandas as pd
import traceback
import sys
import math

# ============================================================================
# FUNÇÃO PARA CALCULAR pH BASEADO NOS NUTRIENTES (CORRIGIDA)
# ============================================================================

def calcular_ph(dados):
    """
    Calcula o pH do solo com base nos nutrientes e matéria orgânica
    Fórmula adaptada para solos tropicais
    """
    try:
        # Verificar se todos os valores são zero
        if (dados.get('calcium', 0) == 0 and 
            dados.get('magnesium', 0) == 0 and 
            dados.get('potassium', 0) == 0 and
            dados.get('aluminum', 0) == 0 and
            dados.get('h_al', 0) == 0):
            return 7.0  # Solo neutro quando tudo está zerado
        
        # Fatores de acidez (contribuem para pH baixo)
        fator_acidez = (
            dados.get('aluminum', 0.5) * 0.3 +
            dados.get('h_al', 3.5) * 0.1
        )
        
        # Fatores de basicidade (contribuem para pH alto)
        fator_basicidade = (
            dados.get('calcium', 3.0) * 0.2 +
            dados.get('magnesium', 1.5) * 0.15 +
            dados.get('potassium', 0.25) * 0.5
        )
        
        # Matéria orgânica (pode acidificar ou tamponar)
        om = dados.get('organic_matter', 25) / 100
        
        # Cálculo do pH base
        ph_base = 5.5 + (fator_basicidade - fator_acidez) - (om * 0.5)
        
        # Limitar o pH entre 4.0 e 8.0
        ph = max(4.0, min(8.0, ph_base))
        
        return round(ph, 1)
    
    except Exception:
        return 7.0  # Valor padrão neutro

# ============================================================================
# FUNÇÃO PARA CALCULAR ADUBAÇÃO PARA VASO
# ============================================================================

def calcular_adubacao_vaso(area_vaso_m2, recomendacao_kg_ha, fator_cultura=1.0):
    """
    Calcula a quantidade de adubo para um vaso baseado na recomendação por hectare
    """
    kg_por_m2 = recomendacao_kg_ha / 10000
    kg_vaso = kg_por_m2 * area_vaso_m2
    gramas_vaso = kg_vaso * 1000 * fator_cultura
    return round(gramas_vaso, 2)

# ============================================================================
# TRATAMENTO DE ERROS DE IMPORTAÇÃO
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

# ============================================================================
# FUNÇÃO PARA CARREGAR MODELO
# ============================================================================

@st.cache_resource
def carregar_modelo():
    """Carrega o modelo e features com tratamento de erro"""
    
    if not JOBLIB_AVAILABLE:
        st.sidebar.warning("⚠️ Biblioteca 'joblib' não encontrada. Instale com: pip install joblib")
        return None, None
    
    try:
        import os
        
        if not os.path.exists('modelo.pkl'):
            st.sidebar.warning("⚠️ Arquivo 'modelo.pkl' não encontrado! Coloque o modelo treinado na pasta do app.")
            return None, None
        
        if not os.path.exists('features.pkl'):
            st.sidebar.warning("⚠️ Arquivo 'features.pkl' não encontrado! Coloque o arquivo de features na pasta do app.")
            return None, None
        
        modelo = joblib.load('modelo.pkl')
        features = joblib.load('features.pkl')
        
        st.sidebar.success(f"✅ Modelo carregado com {len(features)} features")
        
        return modelo, features
    
    except Exception as e:
        st.sidebar.error(f"❌ Erro ao carregar o modelo: {str(e)}")
        return None, None

modelo, features = carregar_modelo()

# ============================================================================
# CONFIGURACAO DA PAGINA
# ============================================================================

st.set_page_config(
    page_title="Classificador de Fertilidade do Solo - SiBCS",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CSS PERSONALIZADO - DESIGN MODERNO
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
    padding: 2rem 2rem 2rem 2rem !important;
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

div[data-testid="stMetric"] {
    background: linear-gradient(135deg, #ffffff 0%, #fafcff 100%) !important;
    border-radius: 20px !important;
    padding: 1.2rem !important;
    border: 1px solid rgba(74, 140, 92, 0.15) !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03) !important;
    transition: all 0.3s ease !important;
}

div[data-testid="stMetric"]:hover {
    transform: translateY(-3px) !important;
    border-color: #4a8c5c !important;
    box-shadow: 0 8px 25px rgba(74, 140, 92, 0.12) !important;
}

div[data-testid="stMetricLabel"] {
    color: #5a6e5a !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
}

div[data-testid="stMetricValue"] {
    color: #2d5a3b !important;
    font-weight: 800 !important;
}

.stAlert {
    border-radius: 16px !important;
    border: none !important;
    background: #fefdf7 !important;
    border-left: 4px solid #4a8c5c !important;
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

button[data-baseweb="tab"] {
    background: transparent !important;
    color: #5a6e5a !important;
    font-weight: 500 !important;
    border-radius: 30px !important;
    padding: 0.5rem 1.5rem !important;
    transition: all 0.2s ease !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    background: linear-gradient(95deg, #2d5a3b 0%, #4a8c5c 100%) !important;
    color: white !important;
    box-shadow: 0 2px 8px rgba(45, 90, 59, 0.2) !important;
}

.dataframe {
    background: #ffffff !important;
    border-radius: 16px !important;
    overflow: hidden !important;
    border: 1px solid #e8ede8 !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03) !important;
}

.dataframe th {
    background: linear-gradient(95deg, #2d5a3b 0%, #3a6b48 100%) !important;
    color: white !important;
    font-weight: 600 !important;
    padding: 12px !important;
}

.dataframe td {
    color: #2d3a2a !important;
    padding: 10px !important;
    background: #ffffff !important;
}

hr {
    margin: 2rem 0 !important;
    border: none !important;
    height: 2px !important;
    background: linear-gradient(90deg, transparent, #4a8c5c, #86efac, #4a8c5c, transparent) !important;
    border-radius: 5px !important;
}

.custom-header {
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.95), rgba(248, 250, 245, 0.95));
    backdrop-filter: blur(10px);
    border-radius: 28px;
    padding: 1.5rem 2rem;
    margin-bottom: 2rem;
    border: 1px solid rgba(74, 140, 92, 0.2);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
}

div[role="radiogroup"] {
    gap: 12px;
    justify-content: center;
    margin: 1.5rem 0;
}

div[role="radiogroup"] label {
    background: #ffffff !important;
    border-radius: 40px !important;
    padding: 0.5rem 1.5rem !important;
    border: 2px solid #e2e8f0 !important;
    color: #5a6e5a !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
}

div[role="radiogroup"] label:hover {
    border-color: #4a8c5c !important;
    background: #fafdf8 !important;
}

div[role="radiogroup"] label[data-baseweb="radio"]:has(input:checked) {
    background: linear-gradient(95deg, #2d5a3b 0%, #4a8c5c 100%) !important;
    color: white !important;
    border-color: transparent !important;
}

::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}

::-webkit-scrollbar-track {
    background: #e2e8f0;
    border-radius: 10px;
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(135deg, #4a8c5c, #86efac);
    border-radius: 10px;
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
</style>
""", unsafe_allow_html=True)

# ============================================================================
# CABECALHO PERSONALIZADO
# ============================================================================

st.markdown("""
<div class="custom-header">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
        <div>
            <h1 style="margin-bottom: 0.3rem; font-size: 2rem;">🌿 Classificador Inteligente de Fertilidade do Solo</h1>
            <p style="color: #5a6e5a; margin-bottom: 0;">Sistema Brasileiro de Classificação de Solos (SiBCS) · Embrapa</p>
        </div>
        <div class="version-badge">
            📊 Análise em Tempo Real
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.markdown("<div style='text-align: center; margin: 1rem 0;'>", unsafe_allow_html=True)
    st.image("https://cdn-icons-png.flaticon.com/512/2934/2934128.png", width=80)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### 📊 Sobre o Sistema")
    st.markdown("""
    Este classificador utiliza parâmetros do **SiBCS (Embrapa)** para:
    - ✅ Avaliação da fertilidade do solo
    - ✅ Classificação agrícola profissional
    - ✅ Recomendação de calagem precisa
    - ✅ Relatórios técnicos detalhados
    - ✅ Cálculo de adubação para vasos
    """)

    st.markdown("---")
    st.markdown("### 🤖 Status da IA")
    
    if not JOBLIB_AVAILABLE:
        st.error("⚠️ joblib não instalado")
        st.caption("Execute: pip install joblib")
    elif modelo is not None and features is not None:
        st.success("✅ IA carregada com sucesso!")
        st.caption(f"🎯 Features esperadas: {len(features)}")
        with st.expander("📋 Detalhes do modelo"):
            for i, f in enumerate(features[:10]):
                st.caption(f"{i+1}. {f}")
            if len(features) > 10:
                st.caption(f"... e mais {len(features)-10} features")
    else:
        st.warning("⚠️ IA não disponível")
        if JOBLIB_AVAILABLE:
            st.caption("Verifique os arquivos modelo.pkl e features.pkl")
        else:
            st.caption("Instale joblib para ativar a IA")

    st.markdown("---")
    st.caption("✨ Versão 7.0 — Com Adubação para Vasos")
    st.caption("Desenvolvido com Streamlit")

# ============================================================================
# SESSION STATE
# ============================================================================

if "dados_basicos" not in st.session_state:
    st.session_state.dados_basicos = {}

if "dados_calculados" not in st.session_state:
    st.session_state.dados_calculados = {}

if "dados_salvos" not in st.session_state:
    st.session_state.dados_salvos = False

if "classificacao_realizada" not in st.session_state:
    st.session_state.classificacao_realizada = False

# MENU
menu = st.radio(
    "Navegação",
    [
        "📊 1. Dados do Solo",
        "🌱 2. Classificação",
        "🧪 3. Adubação para Vaso",
        "📈 4. Relatório",
        "ℹ️ 5. Métodos"
    ],
    horizontal=True,
    label_visibility="collapsed"
)

# ============================================================================
# DICIONARIO DAS CULTURAS
# ============================================================================

necessidades_culturas = {
    "Soja": {"v_desejado": 60, "ph_min": 5.5, "ph_max": 6.5, "p_min": 15, "k_min": 0.35},
    "Milho": {"v_desejado": 65, "ph_min": 5.5, "ph_max": 6.5, "p_min": 20, "k_min": 0.40},
    "Feijão": {"v_desejado": 65, "ph_min": 5.5, "ph_max": 6.5, "p_min": 20, "k_min": 0.35},
    "Café": {"v_desejado": 70, "ph_min": 5.5, "ph_max": 6.5, "p_min": 25, "k_min": 0.40},
    "Pastagem": {"v_desejado": 50, "ph_min": 5.0, "ph_max": 6.0, "p_min": 10, "k_min": 0.25},
    "Algodão": {"v_desejado": 70, "ph_min": 5.5, "ph_max": 6.5, "p_min": 25, "k_min": 0.45},
    "Cana-de-açúcar": {"v_desejado": 60, "ph_min": 5.5, "ph_max": 6.5, "p_min": 15, "k_min": 0.30},
    "Sorgo": {"v_desejado": 55, "ph_min": 5.2, "ph_max": 6.2, "p_min": 12, "k_min": 0.30},
    "Trigo": {"v_desejado": 65, "ph_min": 5.5, "ph_max": 6.5, "p_min": 18, "k_min": 0.35},
    "Tomate": {"v_desejado": 80, "ph_min": 6.0, "ph_max": 6.8, "p_min": 30, "k_min": 0.50},
    "Eucalipto": {"v_desejado": 45, "ph_min": 5.0, "ph_max": 6.0, "p_min": 8, "k_min": 0.20},
    "Citrus": {"v_desejado": 70, "ph_min": 5.5, "ph_max": 6.5, "p_min": 20, "k_min": 0.35},
    "Arroz": {"v_desejado": 50, "ph_min": 5.0, "ph_max": 6.0, "p_min": 10, "k_min": 0.25}
}

recomendacao_n_ha = {
    "Soja": 20,
    "Milho": 120,
    "Feijão": 40,
    "Café": 180,
    "Pastagem": 80,
    "Algodão": 140,
    "Cana-de-açúcar": 100,
    "Sorgo": 90,
    "Trigo": 110,
    "Tomate": 150,
    "Eucalipto": 60,
    "Citrus": 130,
    "Arroz": 85
}

# ============================================================================
# FUNÇÃO PARA PREDIÇÃO DA IA
# ============================================================================

def fazer_predicao_ia(dados):
    """Faz a predição usando o modelo de IA carregado com todas as features"""
    
    if not JOBLIB_AVAILABLE:
        return None, "Biblioteca joblib não instalada"
    
    if modelo is None or features is None:
        return None, "Modelo não disponível"
    
    try:
        features_disponiveis = {
            "nitrogen": dados.get("nitrogen", 0),
            "phosphorus": dados.get("phosphorus", 0),
            "potassium": dados.get("potassium", 0),
            "ph": dados.get("ph", 7.0),
            "organic_matter": dados.get("organic_matter", 0),
            "bulk_density": dados.get("bulk_density", 0),
            "sand": dados.get("sand", 0),
            "silt": dados.get("silt", 0),
            "clay": dados.get("clay", 0),
            "calcium": dados.get("calcium", 0),
            "magnesium": dados.get("magnesium", 0),
            "aluminum": dados.get("aluminum", 0),
            "h_al": dados.get("h_al", 0),
            "particle_density": dados.get("particle_density", 2.65)
        }
        
        valores = []
        for feature in features:
            if feature in features_disponiveis:
                valores.append(features_disponiveis[feature])
            else:
                valores.append(0)
        
        entrada_ia = pd.DataFrame([valores], columns=features)
        predicao = modelo.predict(entrada_ia)

        def mapear_classe_fertilidade(valor):
            mapeamento = {
                0: "🔴 BAIXA FERTILIDADE",
                1: "🟢 ALTA FERTILIDADE"
            }
            if isinstance(valor, str):
                return valor
            return mapeamento.get(valor, f"Classe {valor}")
        
        if hasattr(modelo, 'classes_'):
            classe_original = modelo.classes_[predicao[0]]
            classe_legivel = mapear_classe_fertilidade(classe_original)
            return classe_legivel, "Sucesso"
        else:
            classe_legivel = mapear_classe_fertilidade(predicao[0])
            return classe_legivel, "Sucesso"
    
    except Exception as e:
        return None, f"Erro na predição: {str(e)}"

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

        try:
            if sand != "0.0" and silt != "0.0" and clay != "0.0":
                soma_textura = float(sand.replace(",", ".")) + float(silt.replace(",", ".")) + float(clay.replace(",", "."))
                if abs(soma_textura - 1000) > 10:
                    st.warning(f"⚠️ Soma da textura = {soma_textura:.0f} g/kg. O ideal é 1000 g/kg.")
        except:
            pass

    st.markdown("---")

    if st.button("💾 SALVAR DADOS BÁSICOS", key="salvar_basicos"):
        try:
            st.session_state.dados_basicos = {
                "nitrogen": float(nitrogen.replace(",", ".")),
                "phosphorus": float(phosphorus.replace(",", ".")),
                "potassium": float(potassium.replace(",", ".")),
                "organic_matter": float(organic_matter.replace(",", ".")),
                "bulk_density": float(bulk_density.replace(",", ".")),
                "particle_density": float(particle_density.replace(",", ".")),
                "sand": float(sand.replace(",", ".")),
                "silt": float(silt.replace(",", ".")),
                "clay": float(clay.replace(",", "."))
            }
            st.session_state.dados_salvos = True
            st.success("✅ Dados básicos salvos com sucesso! Agora vá para a aba 'Classificação'.")
        except ValueError as e:
            st.error(f"❌ Verifique os valores numéricos inseridos. Erro: {str(e)}")
        except Exception as e:
            st.error(f"❌ Erro inesperado: {str(e)}")

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
            
            st.session_state.dados_calculados = dados
            st.session_state.sb = sb
            st.session_state.ctc_potencial = ctc_potencial
            st.session_state.v_percent = v_percent
            st.session_state.m_percent = m_percent
            st.session_state.cultura_selecionada = cultura
            st.session_state.classificacao_realizada = True
            
            st.success("✅ Classificação realizada com sucesso!")
            
            col_r1, col_r2, col_r3 = st.columns(3)
            with col_r1:
                st.metric("pH do Solo", f"{dados['ph']:.1f}")
            with col_r2:
                st.metric("CTC Potencial", f"{ctc_potencial:.2f} cmolc/dm³")
            with col_r3:
                st.metric("Saturação por Bases (V%)", f"{v_percent:.1f}%")
            
            st.markdown("---")
            st.markdown("### 🤖 Classificação por IA")
            
            if JOBLIB_AVAILABLE and modelo is not None:
                with st.spinner("🔄 IA processando os dados do solo..."):
                    predicao, status = fazer_predicao_ia(dados)
                    if predicao:
                        st.success(f"🌾 **Classe prevista pela IA:** {predicao}")
                    else:
                        st.warning(f"⚠️ IA não pôde fazer a predição: {status}")
            else:
                st.info("ℹ️ Funcionalidade de IA não disponível. Instale a biblioteca 'joblib' para ativar a classificação por IA.")
                
        except Exception as e:
            st.error(f"❌ Erro na classificação: {str(e)}")
            st.code(traceback.format_exc())

# ============================================================================
# ABA 3 - ADUBAÇÃO PARA VASO
# ============================================================================

elif menu == "🧪 3. Adubação para Vaso":
    st.markdown("## 🧪 Cálculo de Adubação para Vaso")
    
    if not st.session_state.classificacao_realizada:
        st.warning("⚠️ Execute a classificação na ABA 2 primeiro para obter as recomendações baseadas na análise do solo!")
        st.info("📌 Isso é importante porque a recomendação de adubação considera os níveis atuais de fósforo e potássio do seu solo.")
        
        if st.button("📊 Usar dados de demonstração"):
            st.session_state.classificacao_realizada = True
            st.session_state.dados_calculados = {
                "phosphorus": 5.0,
                "potassium": 0.15,
                "clay": 200
            }
            st.session_state.cultura_selecionada = "Soja"
            st.rerun()
        st.stop()
    
    st.info("🌱 **Recomendação personalizada baseada na análise do seu solo!**")
    
    st.markdown("### 📏 Dimensões do Vaso")
    
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        altura_cm = st.number_input("Altura do vaso (cm)", min_value=5.0, max_value=100.0, value=20.0, step=1.0)
    with col_v2:
        diametro_cm = st.number_input("Diâmetro do vaso (cm)", min_value=5.0, max_value=50.0, value=10.0, step=1.0)
    
    raio_cm = diametro_cm / 2
    area_cm2 = math.pi * (raio_cm ** 2)
    area_m2 = area_cm2 / 10000
    
    st.caption(f"📐 Área do vaso: **{area_m2:.4f} m²** | Volume aproximado: **{(area_m2 * (altura_cm/100)):.3f} m³**")
    
    st.markdown("---")
    st.markdown("### 🌾 Recomendação de Adubação Nitrogenada")
    
    cultura = st.session_state.cultura_selecionada
    st.success(f"Cultura selecionada: **{cultura}**")
    
    dados = st.session_state.dados_calculados
    phosphorus_atual = dados.get("phosphorus", 0)
    potassium_atual = dados.get("potassium", 0)
    
    fator_ajuste = 1.0
    if phosphorus_atual < 15:
        fator_ajuste += 0.2
        st.info("⚠️ Fósforo baixo (+20% na adubação)")
    if potassium_atual < 0.25:
        fator_ajuste += 0.15
        st.info("⚠️ Potássio baixo (+15% na adubação)")
    
    base_n_ha = recomendacao_n_ha.get(cultura, 80)
    recomendacao_ajustada = base_n_ha * fator_ajuste
    
    gramas_por_vaso = calcular_adubacao_vaso(area_m2, recomendacao_ajustada, fator_cultura=1.0)
    
    st.markdown("---")
    st.markdown("### 📊 Resultado")
    
    col_res1, col_res2, col_res3 = st.columns(3)
    with col_res1:
        st.metric("Recomendação por hectare", f"{recomendacao_ajustada:.0f} kg/ha de N")
    with col_res2:
        st.metric("Quantidade para este vaso", f"{gramas_por_vaso:.2f} gramas de N")
    with col_res3:
        st.metric("Equivalente em ureia (45% N)", f"{(gramas_por_vaso / 0.45):.2f} gramas")
    
    st.markdown("---")
    st.markdown("#### 🧴 Modo de aplicação sugerido:")
    st.markdown(f"""
    - Dissolva **{gramas_por_vaso:.2f} gramas de nitrogênio** em água
    - Para ureia: use **{(gramas_por_vaso / 0.45):.2f} gramas**
    - Aplique dividido em 2-3 vezes durante o ciclo da cultura
    - Regue após a aplicação para melhor absorção
    """)
    
    st.caption("💡 *Nota: Soja não necessita de adubação nitrogenada significativa devido à fixação biológica*")

# ============================================================================
# ABA 4 - RELATÓRIO
# ============================================================================

elif menu == "📈 4. Relatório":
    st.markdown("## 📈 Relatório Técnico")

    if not st.session_state.classificacao_realizada:
        st.warning("⚠️ Execute primeiro a classificação na ABA 2.")
        st.stop()

    dados = st.session_state.dados_calculados
    sb = st.session_state.sb
    ctc_potencial = st.session_state.ctc_potencial
    v_percent = st.session_state.v_percent
    m_percent = st.session_state.m_percent
    cultura = st.session_state.cultura_selecionada

    relatorio = pd.DataFrame({
        "Parâmetro": [
            "pH", "Nitrogênio (N)", "Fósforo (P)", "Potássio (K+)",
            "Cálcio (Ca²⁺)", "Magnésio (Mg²⁺)", "Alumínio (Al³⁺)", "H + Al",
            "Soma de Bases (SB)", "CTC Potencial", "Saturação por Bases (V%)",
            "Saturação por Al (m%)", "Matéria Orgânica", "Densidade do Solo", "Areia", "Silte", "Argila"
        ],
        "Valor": [
            f"{dados['ph']:.1f}", f"{dados['nitrogen']:.1f} mg/dm³",
            f"{dados['phosphorus']:.1f} mg/dm³", f"{dados['potassium']:.2f} cmolc/dm³",
            f"{dados['calcium']:.2f} cmolc/dm³", f"{dados['magnesium']:.2f} cmolc/dm³",
            f"{dados['aluminum']:.2f} cmolc/dm³", f"{dados['h_al']:.2f} cmolc/dm³",
            f"{sb:.2f} cmolc/dm³", f"{ctc_potencial:.2f} cmolc/dm³",
            f"{v_percent:.1f}%", f"{m_percent:.1f}%",
            f"{dados['organic_matter']:.1f} g/kg", f"{dados['bulk_density']:.2f} g/cm³",
            f"{dados['sand']:.0f} g/kg", f"{dados['silt']:.0f} g/kg", f"{dados['clay']:.0f} g/kg"
        ]
    })

    st.dataframe(relatorio, hide_index=True, use_container_width=True)

    csv = relatorio.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Baixar Relatório (CSV)",
        data=csv,
        file_name="relatorio_solo.csv",
        mime="text/csv",
        key="download_csv"
    )

    st.markdown("---")
    st.markdown("## 🌾 Recomendações Agronômicas")
    st.success(f"✅ Cultura selecionada: {cultura}")

    v2 = necessidades_culturas[cultura]["v_desejado"]
    nc = max(((v2 - v_percent) * ctc_potencial) / 100, 0)
    prnt = 80
    nc_corrigida = nc * (100 / prnt)
    gesso = nc_corrigida * 0.5 if dados["clay"] >= 350 else 0

    st.info(f"🪨 Aplicar {nc_corrigida:.2f} t/ha de calcário com PRNT {prnt}%")
    
    if gesso > 0:
        st.warning(f"🌱 Recomenda-se gessagem de {gesso:.2f} t/ha")
    else:
        st.success("✅ Gessagem não necessária")

    if dados["phosphorus"] < 15:
        st.error("🔴 Necessária adubação fosfatada")
    else:
        st.success("✅ Fósforo em nível adequado")

    if dados["potassium"] < 0.30:
        st.error("🔴 Necessária adubação potássica")
    else:
        st.success("✅ Potássio em nível adequado")

# ============================================================================
# ABA 5 - MÉTODOS
# ============================================================================

elif menu == "ℹ️ 5. Métodos":
    st.markdown("## ℹ️ Métodos Utilizados")

    with st.expander("📊 Saturação por Bases (V%)"):
        st.markdown("### Fórmula:")
        st.latex(r"V\% = \frac{SB}{CTC} \times 100")
        st.markdown("Onde: SB = Soma de Bases, CTC = Capacidade de Troca de Cátions")

    with st.expander("🔬 Saturação por Alumínio (m%)"):
        st.markdown("### Fórmula:")
        st.latex(r"m\% = \frac{Al^{3+}}{CTC\ efetiva} \times 100")
        st.markdown("Onde: Al³⁺ = Alumínio trocável, CTC efetiva = SB + Al³⁺")

    with st.expander("🌾 Interpretação Agronômica"):
        st.markdown("""
        | V% | Interpretação |
        |---|---|---|
        | > 70 | Muito fértil |
        | 50-70 | Fértil |
        | 25-50 | Distrófico |
        | < 25 | Álico |
        """)

    with st.expander("🧪 Cálculo do pH"):
        st.markdown("""
        O pH é calculado considerando:
        - Cátions básicos (Ca, Mg, K) → aumentam o pH
        - Alumínio e H+Al → diminuem o pH
        - Matéria Orgânica → efeito tampão
        - **Valores zerados resultam em pH neutro (7.0)**
        """)

    with st.expander("🌱 Cálculo da Adubação para Vaso"):
        st.markdown("""
        **Fórmula utilizada:**kg_por_m2 = recomendacao_kg_ha / 10000
kg_vaso = kg_por_m2 * area_do_vaso_m2
gramas_vaso = kg_vaso * 1000

st.markdown("""
**Considerações:**

- Área do vaso calculada a partir do diâmetro (pi * r**2)
- Ajuste baseado nos níveis de P e K da análise
- Soja: 20 kg/ha (fixa N biologicamente)
- Milho: 120 kg/ha
- Tomate: 150 kg/ha
""")

with st.expander("🪨 Cálculo da Calagem"):
    st.markdown("### Fórmula utilizada:")
    
    st.latex(r"NC = \frac{(V2 - V1) \times CTC}{100}")
    
    st.markdown(""" Onde:

- **NC** = Necessidade de calcário
- **V2** = Saturação desejada
- **V1** = Saturação atual
- **CTC** = Capacidade de troca catiônica
""")

# ============================================================================
# RODAPÉ
# ============================================================================

st.markdown("---")

st.caption(
    "© 2026 - Classificador de Fertilidade do Solo | "
    "Créditos ao SiBCS - Embrapa | "
    "Inclui cálculo de adubação para vasos | "
    "Dados abertos"
)
