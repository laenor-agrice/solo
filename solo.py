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
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CSS PERSONALIZADO - DESIGN MODERNO, CLEAN E SOFISTICADO
# ============================================================================

st.markdown("""
<style>
/* Fonte moderna */
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

* {
    font-family: 'Outfit', sans-serif;
}

/* Fundo gradiente suave */
.stApp {
    background: linear-gradient(135deg, #f5f7fa 0%, #eef2f7 100%) !important;
}

/* Container principal com efeito glass moderno */
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

/* Títulos elegantes */
h1, h2, h3 {
    background: linear-gradient(120deg, #2d5a3b 0%, #4a8c5c 100%) !important;
    -webkit-background-clip: text !important;
    background-clip: text !important;
    color: transparent !important;
    font-weight: 700 !important;
    letter-spacing: -0.3px !important;
}

/* Sidebar moderna */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a3022 0%, #0e1e14 100%) !important;
    border-right: none !important;
    box-shadow: 4px 0 20px rgba(0, 0, 0, 0.05) !important;
}

section[data-testid="stSidebar"] * {
    color: #e8f0e5 !important;
}

/* Campos de input modernos */
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
    font-size: 0.95rem !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02) !important;
}

/* Input com valor preenchido (diferente de 0) */
.stTextInput input:not([value="0"]):not([value="0.0"]),
.stNumberInput input:not([value="0"]):not([value="0.0"]) {
    background: linear-gradient(95deg, #f0fdf4 0%, #ecfdf5 100%) !important;
    border-color: #86efac !important;
    box-shadow: 0 0 0 3px rgba(134, 239, 172, 0.1) !important;
}

/* Focus state */
.stTextInput input:focus, 
.stNumberInput input:focus,
div[data-baseweb="select"] > div:focus-within {
    border-color: #4a8c5c !important;
    box-shadow: 0 0 0 4px rgba(74, 140, 92, 0.15) !important;
    outline: none !important;
    transform: translateY(-1px);
}

/* Botões com gradiente moderno */
.stButton > button {
    background: linear-gradient(95deg, #2d5a3b 0%, #4a8c5c 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 40px !important;
    padding: 0.7rem 2rem !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 12px rgba(45, 90, 59, 0.2) !important;
    letter-spacing: 0.3px !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 20px rgba(45, 90, 59, 0.3) !important;
    background: linear-gradient(95deg, #234a2f 0%, #3d7a4f 100%) !important;
}

/* Cards de métricas elegantes */
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
    letter-spacing: 0.3px !important;
}

div[data-testid="stMetricValue"] {
    color: #2d5a3b !important;
    font-weight: 800 !important;
    font-size: 1.8rem !important;
}

/* Alertas elegantes */
.stAlert {
    border-radius: 16px !important;
    border: none !important;
    background: #fefdf7 !important;
    border-left: 4px solid #4a8c5c !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04) !important;
}

/* Expander moderno */
.streamlit-expanderHeader {
    background: #ffffff !important;
    border-radius: 16px !important;
    color: #2d5a3b !important;
    font-weight: 600 !important;
    border: 1px solid #e2e8f0 !important;
    transition: all 0.2s ease !important;
}

.streamlit-expanderHeader:hover {
    border-color: #4a8c5c !important;
    background: #fafdf8 !important;
}

.streamlit-expanderContent {
    background: #ffffff !important;
    border-radius: 0 0 16px 16px !important;
    border: 1px solid #e2e8f0 !important;
    border-top: none !important;
}

/* Tabs horizontais */
button[data-baseweb="tab"] {
    background: transparent !important;
    color: #5a6e5a !important;
    font-weight: 500 !important;
    border-radius: 30px !important;
    padding: 0.5rem 1.5rem !important;
    transition: all 0.2s ease !important;
    margin: 0 2px !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    background: linear-gradient(95deg, #2d5a3b 0%, #4a8c5c 100%) !important;
    color: white !important;
    box-shadow: 0 2px 8px rgba(45, 90, 59, 0.2) !important;
}

/* Dataframe clean */
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
    font-size: 0.85rem !important;
}

.dataframe td {
    color: #2d3a2a !important;
    padding: 10px !important;
    background: #ffffff !important;
    border-bottom: 1px solid #f0f2f0 !important;
}

/* Linha divisória */
hr {
    margin: 2rem 0 !important;
    border: none !important;
    height: 2px !important;
    background: linear-gradient(90deg, transparent, #4a8c5c, #86efac, #4a8c5c, transparent) !important;
    border-radius: 5px !important;
}

/* Cabeçalho principal */
.custom-header {
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.95), rgba(248, 250, 245, 0.95));
    backdrop-filter: blur(10px);
    border-radius: 28px;
    padding: 1.5rem 2rem;
    margin-bottom: 2rem;
    border: 1px solid rgba(74, 140, 92, 0.2);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
}

/* Radio buttons horizontais */
div[role="radiogroup"] {
    gap: 12px;
    justify-content: center;
    margin: 1.5rem 0;
    background: transparent;
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

/* Scrollbar elegante */
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

::-webkit-scrollbar-thumb:hover {
    background: #2d5a3b;
}

/* Selectbox */
div[data-baseweb="select"] ul {
    background: white !important;
    border-radius: 12px !important;
    border: 1px solid #e2e8f0 !important;
}

/* Badge */
.version-badge {
    background: linear-gradient(95deg, #e8f5e9, #d4edda);
    color: #2d5a3b;
    border-radius: 40px;
    padding: 0.25rem 1rem;
    font-size: 0.7rem;
    font-weight: 600;
    display: inline-block;
}

/* Labels dos inputs */
label {
    color: #4a5b44 !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    margin-bottom: 0.3rem !important;
}

/* Info box */
.stInfo {
    background: #e8f5e9 !important;
    color: #2d5a3b !important;
}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# JAVASCRIPT PARA DESTAQUE DE CAMPOS PREENCHIDOS
# ============================================================================

st.markdown("""
<script>
// Monitora mudanças nos inputs e aplica classe quando diferente de 0
document.addEventListener('DOMContentLoaded', function() {
    const inputs = document.querySelectorAll('input');
    inputs.forEach(input => {
        function checkValue() {
            if (input.value && input.value !== '0' && input.value !== '0.0') {
                input.classList.add('filled');
            } else {
                input.classList.remove('filled');
            }
        }
        input.addEventListener('input', checkValue);
        checkValue();
    });
});
</script>
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
    - ✅ Cálculo de CTC e saturação por bases
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
    st.caption("✨ Versão 6.0 — Design Sofisticado")
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

# MENU
menu = st.radio(
    "Navegação",
    [
        "📊 1. Dados do Solo",
        "🌱 2. Classificação",
        "📈 3. Relatório",
        "ℹ️ 4. Métodos"
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
        particle_density = st.text_input("Densidade de Partícula (g/cm³)", value="0.0", key="pd_input")
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
    if "dados_basicos" not in st.session_state or not st.session_state.dados_basicos:
        st.warning("⚠️ Preencha e salve os dados na ABA 1.")
        st.stop()

    st.markdown("## 🌱 Classificação da Fertilidade")

    col1, col2 = st.columns(2)

    with col1:
        aluminum = st.text_input("Alumínio (Al³⁺) - cmolc/dm³", value="0.0")
        h_al = st.text_input("H + Al - cmolc/dm³", value="0.0")

    with col2:
        calcium = st.text_input("Cálcio (Ca²⁺) - cmolc/dm³", value="0.0")
        magnesium = st.text_input("Magnésio (Mg²⁺) - cmolc/dm³", value="0.0")
        cultura = st.selectbox("🌾 Cultura", list(necessidades_culturas.keys()))

    st.markdown("---")

    try:
        dados = st.session_state.dados_basicos.copy()
        dados["aluminum"] = float(aluminum.replace(",", "."))
        dados["h_al"] = float(h_al.replace(",", "."))
        dados["calcium"] = float(calcium.replace(",", "."))
        dados["magnesium"] = float(magnesium.replace(",", "."))

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
# ABA 3 - RELATÓRIO
# ============================================================================

elif menu == "📈 3. Relatório":
    st.markdown("## 📈 Relatório Técnico")

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
        "Parâmetro": [
            "pH", "Nitrogênio (N)", "Fósforo (P)", "Potássio (K+)",
            "Cálcio (Ca²⁺)", "Magnésio (Mg²⁺)", "Alumínio (Al³⁺)", "H + Al",
            "Soma de Bases (SB)", "CTC Potencial", "Saturação por Bases (V%)",
            "Saturação por Al (m%)", "Matéria Orgânica", "Densidade do Solo"
        ],
        "Valor": [
            f"{dados['ph']:.1f}", f"{dados['nitrogen']:.1f} mg/dm³",
            f"{dados['phosphorus']:.1f} mg/dm³", f"{dados['potassium']:.2f} cmolc/dm³",
            f"{dados['calcium']:.2f} cmolc/dm³", f"{dados['magnesium']:.2f} cmolc/dm³",
            f"{dados['aluminum']:.2f} cmolc/dm³", f"{dados['h_al']:.2f} cmolc/dm³",
            f"{sb:.2f} cmolc/dm³", f"{ctc_potencial:.2f} cmolc/dm³",
            f"{v_percent:.1f}%", f"{m_percent:.1f}%",
            f"{dados['organic_matter']:.1f} g/kg", f"{dados['bulk_density']:.2f} g/cm³"
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
# ABA 4 - MÉTODOS
# ============================================================================

elif menu == "ℹ️ 4. Métodos":
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
st.caption("© 2026 - Classificador de Fertilidade do Solo | Créditos ao SiBCS - Embrapa | Ferramenta acadêmica | Dados abertos")
