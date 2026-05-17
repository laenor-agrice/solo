import streamlit as st
import pandas as pd
import traceback
import sys

# ============================================================================
# FUNÇÃO PARA CALCULAR pH BASEADO NOS NUTRIENTES
# ============================================================================

def calcular_ph(dados):
    """
    Calcula o pH do solo com base nos nutrientes e matéria orgânica
    Fórmula adaptada para solos tropicais
    """
    try:
        # Fatores que influenciam o pH
        # Quanto maior a matéria orgânica, mais ácido (se não corrigido)
        # Quanto maior os cátions (Ca, Mg, K), mais alcalino
        
        # Fatores de acidez (contribuem para pH baixo)
        fator_acidez = (
            dados.get('aluminum', 0.5) * 0.3 +  # Alumínio é ácido
            dados.get('h_al', 3.5) * 0.1         # H+Al contribui para acidez
        )
        
        # Fatores de basicidade (contribuem para pH alto)
        fator_basicidade = (
            dados.get('calcium', 3.0) * 0.2 +
            dados.get('magnesium', 1.5) * 0.15 +
            dados.get('potassium', 0.25) * 0.5
        )
        
        # Matéria orgânica (pode acidificar ou tamponar)
        om = dados.get('organic_matter', 25) / 100  # Normalizar
        
        # Cálculo do pH base (valores entre 4.5 e 7.5)
        ph_base = 5.5 + (fator_basicidade - fator_acidez) - (om * 0.5)
        
        # Limitar o pH entre 4.0 e 8.0 (valores realistas)
        ph = max(4.0, min(8.0, ph_base))
        
        return round(ph, 1)
    
    except Exception:
        # Valor padrão caso erro no cálculo
        return 6.0

# ============================================================================
# TRATAMENTO DE ERROS DE IMPORTAÇÃO
# ============================================================================

# Tentativa segura de importar joblib
try:
    import joblib
    JOBLIB_AVAILABLE = True
except ImportError:
    JOBLIB_AVAILABLE = False
    joblib = None

# Tentativa segura de importar outras bibliotecas
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None

# ============================================================================
# FUNÇÃO PARA CARREGAR MODELO COM TRATAMENTO DE ERRO
# ============================================================================

@st.cache_resource
def carregar_modelo():
    """Carrega o modelo e features com tratamento de erro"""
    
    # Verificar se a biblioteca necessária está disponível
    if not JOBLIB_AVAILABLE:
        st.warning("⚠️ Biblioteca 'joblib' não encontrada. Instale com: pip install joblib")
        return None, None
    
    try:
        # Verifica se os arquivos existem
        import os
        
        if not os.path.exists('modelo.pkl'):
            st.warning("⚠️ Arquivo 'modelo.pkl' não encontrado! Coloque o modelo treinado na pasta do app.")
            return None, None
        
        if not os.path.exists('features.pkl'):
            st.warning("⚠️ Arquivo 'features.pkl' não encontrado! Coloque o arquivo de features na pasta do app.")
            return None, None
        
        modelo = joblib.load('modelo.pkl')
        features = joblib.load('features.pkl')
        
        # Mostrar quantas features o modelo espera
        st.sidebar.info(f"📊 Modelo treinado com {len(features)} features")
        
        return modelo, features
    
    except Exception as e:
        st.error(f"❌ Erro ao carregar o modelo de IA: {str(e)}")
        st.code(traceback.format_exc())
        return None, None

# Carregar modelo e features
modelo, features = carregar_modelo()

# ============================================================================
# CONFIGURACAO DA PAGINA
# ============================================================================

st.set_page_config(
    page_title="Classificador de Fertilidade do Solo - SiBCS",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CSS PERSONALIZADO - DESIGN ESCURO PROFISSIONAL
# ============================================================================

st.markdown("""
<style>

/* ==========================================================================
   FUNDO GERAL
========================================================================== */

.stApp {
    background: #050816 !important;
    color: #ffffff !important;
    font-family: 'Segoe UI', sans-serif !important;
}

.main > div {
    background: #050816 !important;
}

/* ==========================================================================
   TEXTOS GERAIS
========================================================================== */

html, body, p, span, div, li {
    color: #ffffff !important;
}

/* ==========================================================================
   TITULOS
========================================================================== */

h1, h2, h3, h4, h5, h6 {
    color: #4da6ff !important;
    font-weight: 700 !important;
}

/* ==========================================================================
   SIDEBAR
========================================================================== */

section[data-testid="stSidebar"] {
    background: #0b132b !important;
    border-right: 2px solid #2563eb !important;
}

section[data-testid="stSidebar"] * {
    color: #ffffff !important;
}

/* ==========================================================================
   INPUTS
========================================================================== */

.stTextInput input,
.stNumberInput input,
textarea,
input {
    background-color: #ffffff !important;
    color: #000000 !important;
    border: 2px solid #2563eb !important;
    border-radius: 10px !important;
    padding: 10px !important;
    font-weight: 600 !important;
}

/* ==========================================================================
   SELECTBOX
========================================================================== */

.stSelectbox div[data-baseweb="select"] {
    background-color: #ffffff !important;
    border-radius: 10px !important;
    border: 2px solid #2563eb !important;
}

.stSelectbox span {
    color: #000000 !important;
    font-weight: 600 !important;
}

/* ==========================================================================
   LABELS
========================================================================== */

label {
    color: #dbeafe !important;
    font-weight: 600 !important;
}

/* ==========================================================================
   BOTÕES
========================================================================== */

.stButton button {
    background: linear-gradient(135deg, #2563eb, #1e40af) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.7rem 1.5rem !important;
    font-weight: bold !important;
    transition: 0.3s ease !important;
}

.stButton button:hover {
    transform: translateY(-2px);
    box-shadow: 0 0 15px rgba(37, 99, 235, 0.6);
}

/* ==========================================================================
   CARD RESULTADO
========================================================================== */

.result-card {
    background: linear-gradient(145deg, #0f172a, #111827) !important;
    border: 2px solid #2563eb !important;
    border-radius: 18px !important;
    padding: 25px !important;
    margin-top: 20px !important;
    box-shadow: 0 0 20px rgba(37,99,235,0.25) !important;
}

.result-card h2 {
    color: #60a5fa !important;
    font-size: 2rem !important;
    font-weight: 800 !important;
}

.result-card p {
    color: #ffffff !important;
    font-size: 1.15rem !important;
    font-weight: 500 !important;
}

.result-number {
    color: #ffffff !important;
    font-size: 2.8rem !important;
    font-weight: 900 !important;
}

/* ==========================================================================
   CAIXAS DOS RESULTADOS PRINCIPAIS
========================================================================== */

.result-box {
    background: linear-gradient(145deg, #0f172a, #111827) !important;
    border: 2px solid #2563eb !important;
    border-radius: 18px !important;
    padding: 22px !important;
    margin-bottom: 15px !important;
    box-shadow: 0 0 18px rgba(37,99,235,0.18) !important;
    transition: all 0.3s ease !important;
    text-align: center !important;
}

.result-box:hover {
    transform: translateY(-4px);
    box-shadow: 0 0 28px rgba(96,165,250,0.35) !important;
}

.result-title {
    color: #93c5fd !important;
    font-size: 1.15rem !important;
    font-weight: 700 !important;
    margin-bottom: 15px !important;
}

.result-value {
    color: #ffffff !important;
    font-size: 2.3rem !important;
    font-weight: 900 !important;
    margin-bottom: 8px !important;
}

.result-unit {
    color: #cbd5e1 !important;
    font-size: 0.95rem !important;
    font-weight: 500 !important;
}

/* ==========================================================================
   METRICS STREAMLIT
========================================================================== */

div[data-testid="stMetric"] {
    background: #111827 !important;
    border: 2px solid #2563eb !important;
    border-radius: 16px !important;
    padding: 1rem !important;
    box-shadow: 0 0 15px rgba(37,99,235,0.15);
}

div[data-testid="stMetricLabel"] {
    color: #93c5fd !important;
    font-weight: 700 !important;
}

div[data-testid="stMetricValue"] {
    color: #ffffff !important;
    font-size: 2rem !important;
    font-weight: 900 !important;
}

div[data-testid="stMetricDelta"] {
    color: #22c55e !important;
}

/* ==========================================================================
   DATAFRAME
========================================================================== */

.dataframe {
    background-color: #ffffff !important;
    border-radius: 12px !important;
    overflow: hidden !important;
}

.dataframe th {
    background: #1e3a8a !important;
    color: white !important;
    font-weight: bold !important;
}

.dataframe td {
    background: #ffffff !important;
    color: #000000 !important;
}

/* ==========================================================================
   ALERTAS
========================================================================== */

.stAlert {
    border-radius: 14px !important;
    border: none !important;
    font-weight: 600 !important;
}

/* ==========================================================================
   EXPANDER
========================================================================== */

.streamlit-expanderHeader {
    background: #1e3a8a !important;
    color: white !important;
    border-radius: 10px !important;
    font-weight: bold !important;
}

.streamlit-expanderContent {
    background: #0f172a !important;
    border-radius: 0 0 10px 10px !important;
}

.streamlit-expanderContent p,
.streamlit-expanderContent li {
    color: #ffffff !important;
}

/* ==========================================================================
   RADIO BUTTONS
========================================================================== */

.stRadio label {
    color: #ffffff !important;
}

/* ==========================================================================
   LINHA
========================================================================== */

hr {
    border: none !important;
    height: 2px !important;
    background: linear-gradient(to right, #2563eb, #60a5fa) !important;
}

/* ==========================================================================
   TABS
========================================================================== */

button[data-baseweb="tab"] {
    background-color: #111827 !important;
    color: #ffffff !important;
    border-radius: 10px 10px 0 0 !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    background-color: #2563eb !important;
    color: white !important;
}

/* ==========================================================================
   SCROLLBAR
========================================================================== */

::-webkit-scrollbar {
    width: 10px;
}

::-webkit-scrollbar-track {
    background: #0f172a;
}

::-webkit-scrollbar-thumb {
    background: #2563eb;
    border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
    background: #60a5fa;
}

</style>
""", unsafe_allow_html=True)

# =============================================================
# CSS ADICIONAL - CARDS MÉTRICOS E BARRA DE PROGRESSO
# =============================================================

st.markdown("""
<style>

.metric-card {
    background: linear-gradient(145deg, #111827, #1f2937);
    border: 2px solid #2563eb;
    border-radius: 18px;
    padding: 20px;
    text-align: center;
    box-shadow: 0 0 15px rgba(37,99,235,0.2);
    margin-bottom: 15px;
}

.metric-card h3 {
    color: #93c5fd;
    font-size: 1rem;
    margin-bottom: 10px;
}

.metric-card h2 {
    color: white;
    font-size: 2rem;
    font-weight: 800;
}

.metric-card small {
    color: #cbd5e1;
}

.progress-container {
    width: 100%;
    background-color: #1f2937;
    border-radius: 30px;
    overflow: hidden;
    margin-top: 15px;
    margin-bottom: 25px;
    border: 2px solid #2563eb;
}

.progress-bar {
    background: linear-gradient(90deg, #2563eb, #60a5fa);
    color: white;
    text-align: center;
    padding: 12px;
    font-weight: bold;
    font-size: 1rem;
}

</style>
""", unsafe_allow_html=True)

# ============================================================================
# CABECALHO
# ============================================================================

st.markdown("""
<div style="background: linear-gradient(135deg, #1a5f3e, #2ecc71); padding: 2rem; border-radius: 20px; text-align: center; margin-bottom: 2rem;">
    <h1 style="color: white;">🌾 Classificador Inteligente de Fertilidade do Solo</h1>
    <p style="font-size: 1.2rem; color: white;">Baseado no Sistema Brasileiro de Classificacao de Solos (SiBCS) - Embrapa</p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2934/2934128.png", width=80)

    st.markdown("### 📊 Sobre o Sistema")
    st.markdown("""
    Este classificador utiliza parametros do **SiBCS (Embrapa)** para:
    - ✅ Avaliacao da fertilidade do solo
    - ✅ Classificacao agricola
    - ✅ Recomendacao de calagem
    - ✅ Relatorios tecnicos
    - ✅ Calculo de CTC e saturacao por bases
    """)

    st.markdown("---")
    st.markdown("### 🤖 Status da IA")
    
    if not JOBLIB_AVAILABLE:
        st.error("⚠️ joblib não instalado")
        st.caption("Execute: pip install joblib")
    elif modelo is not None and features is not None:
        st.success("✅ IA carregada com sucesso!")
        st.caption(f"Features esperadas: {len(features)}")
        with st.expander("📋 Features do modelo"):
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
    st.caption("Versao 3.0")
    st.caption("Desenvolvido em Streamlit")

# ============================================================================
# SESSION STATE
# ============================================================================

if "dados_basicos" not in st.session_state:
    st.session_state.dados_basicos = {}

if "dados_calculados" not in st.session_state:
    st.session_state.dados_calculados = {}

if "dados_salvos" not in st.session_state:
    st.session_state.dados_salvos = False

# MENU
menu = st.radio(
    "Navegação",
    [
        "📊 1. Dados do Solo",
        "🌱 2. Classificacao",
        "📈 3. Relatorio",
        "ℹ️ 4. Metodos"
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
    "Feijao": {"v_desejado": 65, "ph_min": 5.5, "ph_max": 6.5, "p_min": 20, "k_min": 0.35},
    "Cafe": {"v_desejado": 70, "ph_min": 5.5, "ph_max": 6.5, "p_min": 25, "k_min": 0.40},
    "Pastagem": {"v_desejado": 50, "ph_min": 5.0, "ph_max": 6.0, "p_min": 10, "k_min": 0.25},
    "Algodao": {"v_desejado": 70, "ph_min": 5.5, "ph_max": 6.5, "p_min": 25, "k_min": 0.45},
    "Cana-de-acucar": {"v_desejado": 60, "ph_min": 5.5, "ph_max": 6.5, "p_min": 15, "k_min": 0.30},
    "Sorgo": {"v_desejado": 55, "ph_min": 5.2, "ph_max": 6.2, "p_min": 12, "k_min": 0.30},
    "Trigo": {"v_desejado": 65, "ph_min": 5.5, "ph_max": 6.5, "p_min": 18, "k_min": 0.35},
    "Tomate": {"v_desejado": 80, "ph_min": 6.0, "ph_max": 6.8, "p_min": 30, "k_min": 0.50},
    "Eucalipto": {"v_desejado": 45, "ph_min": 5.0, "ph_max": 6.0, "p_min": 8, "k_min": 0.20},
    "Citrus": {"v_desejado": 70, "ph_min": 5.5, "ph_max": 6.5, "p_min": 20, "k_min": 0.35},
    "Arroz": {"v_desejado": 50, "ph_min": 5.0, "ph_max": 6.0, "p_min": 10, "k_min": 0.25}
}

# ============================================================================
# FUNÇÃO PARA PREDIÇÃO DA IA - CORRIGIDA PARA USAR TODAS AS FEATURES
# ============================================================================

def fazer_predicao_ia(dados):
    """Faz a predição usando o modelo de IA carregado com todas as features"""
    
    # Verificar se joblib está disponível
    if not JOBLIB_AVAILABLE:
        return None, "Biblioteca joblib não instalada"
    
    if modelo is None or features is None:
        return None, "Modelo não disponível"
    
    try:
        # Features que temos no sistema
        features_disponiveis = {
            "nitrogen": dados.get("nitrogen", 0),
            "phosphorus": dados.get("phosphorus", 0),
            "potassium": dados.get("potassium", 0),
            "ph": dados.get("ph", 6.0),
            "organic_matter": dados.get("organic_matter", 25),
            "bulk_density": dados.get("bulk_density", 1.2),
            "sand": dados.get("sand", 350),
            "silt": dados.get("silt", 300),
            "clay": dados.get("clay", 350),
            "calcium": dados.get("calcium", 3.0),
            "magnesium": dados.get("magnesium", 1.5),
            "aluminum": dados.get("aluminum", 0.5),
            "h_al": dados.get("h_al", 3.5),
            "particle_density": dados.get("particle_density", 2.65)
        }
        
        # Criar array na ordem correta das features do modelo
        valores = []
        features_faltando = []
        
        for feature in features:
            if feature in features_disponiveis:
                valores.append(features_disponiveis[feature])
            else:
                valores.append(0)
                features_faltando.append(feature)
        
        # Criar DataFrame com a ordem correta
        entrada_ia = pd.DataFrame([valores], columns=features)
        
        # Fazer predição
        predicao = modelo.predict(entrada_ia)

        # Mapeamento de classes para texto legível
        def mapear_classe_fertilidade(valor):
            """Converte valores numéricos da IA em texto legível"""
            mapeamento = {
                0: "🔴 BAIXA FERTILIDADE",
                1: "🟢 ALTA FERTILIDADE"
            }
            
            # Se for string ou outro valor, tenta converter
            if isinstance(valor, str):
                return valor
            
            return mapeamento.get(valor, f"Classe {valor}")
        
        # Aplicar o mapeamento
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
    st.markdown("## 📋 Dados Basicos do Solo")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🧪 Macronutrientes")
        nitrogen = st.text_input("🌱 Nitrogenio (N) - mg/dm3", value="30.0", key="n_input")
        phosphorus = st.text_input("🔴 Fosforo (P) - mg/dm3", value="20.0", key="p_input")
        potassium = st.text_input("🟡 Potassio (K+) - cmolc/dm3", value="0.25", key="k_input")
        st.markdown("### 🌿 Materia Organica")
        organic_matter = st.text_input("🌱 Materia Organica (g/kg)", value="25.0", key="om_input")

    with col2:
        st.markdown("### ⚖️ Densidade")
        bulk_density = st.text_input("📦 Densidade do Solo (g/cm3)", value="1.20", key="bd_input")
        particle_density = st.text_input("💎 Densidade de Particula (g/cm3)", value="2.65", key="pd_input")
        st.markdown("### 🏺 Textura")
        sand = st.text_input("🏖️ Areia (g/kg)", value="350", key="sand_input")
        silt = st.text_input("🏞️ Silte (g/kg)", value="300", key="silt_input")
        clay = st.text_input("🏺 Argila (g/kg)", value="350", key="clay_input")

        try:
            soma_textura = float(sand.replace(",", ".")) + float(silt.replace(",", ".")) + float(clay.replace(",", "."))
            if abs(soma_textura - 1000) > 10:
                st.warning(f"⚠️ Soma da textura = {soma_textura:.0f} g/kg. O ideal é 1000 g/kg.")
        except:
            pass

    st.markdown("---")

    if st.button("✅ SALVAR DADOS BASICOS", key="salvar_basicos"):
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
# ABA 2 - CLASSIFICACAO
# ============================================================================

elif menu == "🌱 2. Classificacao":
    if "dados_basicos" not in st.session_state or not st.session_state.dados_basicos:
        st.warning("⚠️ Preencha e salve os dados na ABA 1.")
        st.stop()

    st.markdown("## 🌱 Classificação da Fertilidade")

    col1, col2 = st.columns(2)

    with col1:
        aluminum = st.text_input("⚠️ Alumínio (Al³⁺) - cmolc/dm³", value="0.50")
        h_al = st.text_input("📊 H + Al - cmolc/dm³", value="3.50")

    with col2:
        calcium = st.text_input("🥛 Cálcio (Ca²⁺)", value="3.00")
        magnesium = st.text_input("🧂 Magnésio (Mg²⁺)", value="1.50")
        cultura = st.selectbox("🌾 Cultura", list(necessidades_culturas.keys()))

    st.markdown("---")

    try:
        dados = st.session_state.dados_basicos.copy()
        dados["aluminum"] = float(aluminum.replace(",", "."))
        dados["h_al"] = float(h_al.replace(",", "."))
        dados["calcium"] = float(calcium.replace(",", "."))
        dados["magnesium"] = float(magnesium.replace(",", "."))

        # CALCULAR O pH AUTOMATICAMENTE
        def calcular_ph(dados):
            """Calcula o pH baseado nos nutrientes do solo"""
            try:
                fator_acidez = dados.get('aluminum', 0.5) * 0.3
                fator_basicidade = (
                    dados.get('calcium', 3.0) * 0.2 +
                    dados.get('magnesium', 1.5) * 0.15 +
                    dados.get('potassium', 0.25) * 0.5
                )
                om = dados.get('organic_matter', 25) / 100
                ph_base = 5.5 + (fator_basicidade - fator_acidez) - (om * 0.5)
                ph = max(4.0, min(8.0, ph_base))
                return round(ph, 1)
            except Exception:
                return 6.0
        
        dados["ph"] = calcular_ph(dados)
        st.info(f"🧪 pH calculado automaticamente: **{dados['ph']}**")

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
        st.session_state.cultura = cultura

        st.success("✅ Classificação realizada com sucesso!")

                st.markdown("---")
        st.markdown("## 🤖 Inteligência Artificial")
        
        if JOBLIB_AVAILABLE:
            if modelo is not None and features is not None:
                with st.spinner("🔄 IA processando os dados do solo..."):
                    predicao, status = fazer_predicao_ia(dados)
                
                if predicao is not None:
                    st.success(f"🌾 **Classe prevista pela IA:** {predicao}")
                    
                    with st.expander("ℹ️ Sobre a classificação da IA"):
                        st.markdown(f"""
                        **Modelo:** RandomForestClassifier  
                        **Features utilizadas:** {len(features)} parâmetros do solo  
                        
                        A IA analisou os seguintes parâmetros principais:
                        - Nitrogênio (N): {dados['nitrogen']} mg/dm³
                        - Fósforo (P): {dados['phosphorus']} mg/dm³
                        - Potássio (K+): {dados['potassium']} cmolc/dm³
                        - pH: {dados['ph']}
                        - Matéria Orgânica: {dados['organic_matter']} g/kg
                        - Densidade: {dados['bulk_density']} g/cm³
                        - Textura: Areia {dados['sand']} | Silte {dados['silt']} | Argila {dados['clay']} g/kg
                        """)
                else:
                    st.warning(f"⚠️ IA não pôde fazer a predição: {status}")
            else:
                st.warning("⚠️ Modelo de IA não disponível. Verifique os arquivos 'modelo.pkl' e 'features.pkl'.")
        else:
            st.info("ℹ️ Funcionalidade de IA não disponível. Instale a biblioteca 'joblib' para ativar a classificação por IA.")

    except ValueError as e:
        st.error(f"❌ Verifique os valores digitados. Erro: {str(e)}")
    except Exception as e:
        st.error(f"❌ Erro inesperado: {str(e)}")
        st.code(traceback.format_exc())

# ============================================================================
# ABA 3 - RELATORIO
# ============================================================================

elif menu == "📈 3. Relatorio":
    st.markdown("## 📈 Relatorio Tecnico")

    if "v_percent" not in st.session_state or "dados_calculados" not in st.session_state or "cultura" not in st.session_state:
        st.warning("⚠️ Execute primeiro a classificação na ABA 2.")
        st.stop()

    dados = st.session_state.dados_calculados
    sb = st.session_state.sb
    ctc_potencial = st.session_state.ctc_potencial
    v_percent = st.session_state.v_percent
    m_percent = st.session_state.m_percent
    cultura = st.session_state.cultura

    relatorio = pd.DataFrame({
        "Parametro": [
            "pH", "Nitrogenio (N)", "Fosforo (P)", "Potassio (K+)",
            "Calcio (Ca2+)", "Magnesio (Mg2+)", "Aluminio (Al3+)", "H + Al",
            "Soma de Bases (SB)", "CTC Potencial", "Saturacao por Bases (V%)",
            "Saturacao por Al (m%)", "Materia Organica", "Densidade do Solo"
        ],
        "Valor": [
            f"{dados['ph']:.1f}", f"{dados['nitrogen']:.1f} mg/dm3",
            f"{dados['phosphorus']:.1f} mg/dm3", f"{dados['potassium']:.2f} cmolc/dm3",
            f"{dados['calcium']:.2f} cmolc/dm3", f"{dados['magnesium']:.2f} cmolc/dm3",
            f"{dados['aluminum']:.2f} cmolc/dm3", f"{dados['h_al']:.2f} cmolc/dm3",
            f"{sb:.2f} cmolc/dm3", f"{ctc_potencial:.2f} cmolc/dm3",
            f"{v_percent:.1f}%", f"{m_percent:.1f}%",
            f"{dados['organic_matter']:.1f} g/kg", f"{dados['bulk_density']:.2f} g/cm3"
        ]
    })

    st.dataframe(relatorio, hide_index=True, use_container_width=True)

    csv = relatorio.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Baixar Relatorio (CSV)",
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
# ABA 4 - METODOS
# ============================================================================

elif menu == "ℹ️ 4. Metodos":
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

    with st.expander("🪨 Cálculo da Calagem"):
        st.markdown("### Fórmula utilizada:")
        st.latex(r"NC = \frac{(V_2 - V_1) \times CTC}{100}")
        st.markdown("Onde: NC = Necessidade de calcário, V₂ = Saturação desejada, V₁ = Saturação atual, CTC = Capacidade de troca catiônica")

    with st.expander("🌱 Cálculo da Gessagem"):
        st.markdown("### Critério utilizado:")
        st.markdown("- Solos com argila > 350 g/kg")
        st.markdown("- Gessagem = 50% da dose de calcário")

# ============================================================================
# RODAPÉ
# ============================================================================

st.markdown("---")
st.caption("© 2026 - Classificador de Fertilidade do Solo | Créditos ao SiBCS - Embrapa | Ferramenta acadêmica | Direitos reservados")
