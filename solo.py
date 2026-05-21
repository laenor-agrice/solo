# ============================================================================
# IMPORTAÇÕES
# ============================================================================

import streamlit as st
import pandas as pd
import requests

# ============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================================

st.set_page_config(
    page_title="Classificador Inteligente de Fertilidade do Solo",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CONFIGURAÇÃO GEMINI API
# ============================================================================

GEMINI_API_KEY = "SUA_API_KEY_AQUI"

# ============================================================================
# FUNÇÃO IA GEMINI VIA REQUESTS
# ============================================================================

def gerar_resposta_ia(pergunta, dados_solo=None):

    try:

        contexto = ""

        if dados_solo:

            contexto = f"""
            Dados atuais do solo:

            Nitrogênio: {dados_solo.get('nitrogen', 'N/A')}
            Fósforo: {dados_solo.get('phosphorus', 'N/A')}
            Potássio: {dados_solo.get('potassium', 'N/A')}
            pH: {dados_solo.get('ph', 'N/A')}
            Alumínio: {dados_solo.get('aluminum', 'N/A')}
            Cálcio: {dados_solo.get('calcium', 'N/A')}
            Magnésio: {dados_solo.get('magnesium', 'N/A')}
            Argila: {dados_solo.get('clay', 'N/A')}
            Silte: {dados_solo.get('silt', 'N/A')}
            Areia: {dados_solo.get('sand', 'N/A')}
            """

        prompt = f"""
        Você é um especialista em:
        - Fertilidade do solo
        - SiBCS
        - Manejo agrícola
        - Nutrição de plantas
        - Interpretação agronômica

        Utilize os dados abaixo para responder:

        {contexto}

        Pergunta:
        {pergunta}

        Responda de forma técnica, clara e objetiva.
        """

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

        headers = {
            "Content-Type": "application/json"
        }

        data = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ]
        }

        response = requests.post(
            url,
            headers=headers,
            json=data
        )

        resultado = response.json()

        resposta = resultado["candidates"][0]["content"]["parts"][0]["text"]

        return resposta

    except Exception as erro:

        return f"❌ Erro na IA Gemini: {erro}"

# ============================================================================
# CSS PERSONALIZADO MODERNO
# ============================================================================

st.markdown("""
<style>

    * {
        font-family: 'Segoe UI', sans-serif !important;
    }

    .stApp {
        background: linear-gradient(135deg, #050505, #0f172a);
        color: white;
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #071019, #0f172a);
        border-right: 1px solid rgba(46,204,113,0.3);
    }

    h1, h2, h3, h4, h5, h6 {
        color: #2ecc71 !important;
        font-weight: 700 !important;
    }

    p, span, div, label {
        color: #f5f5f5 !important;
    }

    .stTextInput > div > div > input {
        background-color: rgba(255,255,255,0.08);
        color: white !important;
        border-radius: 12px;
        border: 1px solid rgba(46,204,113,0.4);
        padding: 12px;
    }

    .stSelectbox > div > div {
        background-color: rgba(255,255,255,0.08);
        border-radius: 12px;
    }

    textarea {
        background-color: rgba(255,255,255,0.08) !important;
        color: white !important;
        border-radius: 12px !important;
        border: 1px solid rgba(46,204,113,0.4) !important;
    }

    .stButton button {
        width: 100%;
        border: none;
        border-radius: 14px;
        padding: 0.85rem 1rem;
        background: linear-gradient(135deg, #16a34a, #22c55e);
        color: white;
        font-weight: bold;
        transition: 0.3s;
        box-shadow: 0px 4px 15px rgba(34,197,94,0.25);
    }

    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0px 6px 20px rgba(34,197,94,0.4);
    }

    .card {
        background: rgba(255,255,255,0.05);
        backdrop-filter: blur(10px);
        border-radius: 22px;
        padding: 1.5rem;
        border: 1px solid rgba(255,255,255,0.08);
        box-shadow: 0px 8px 25px rgba(0,0,0,0.25);
        margin-bottom: 1rem;
    }

    .metric-card {
        background: linear-gradient(145deg, rgba(255,255,255,0.08), rgba(255,255,255,0.03));
        border-radius: 20px;
        padding: 1.5rem;
        text-align: center;
        border: 1px solid rgba(46,204,113,0.3);
        backdrop-filter: blur(8px);
    }

    .metric-card h2 {
        color: #2ecc71 !important;
        font-size: 2rem;
    }

    .metric-card h3 {
        color: white !important;
    }

    .result-card {
        background: linear-gradient(145deg, rgba(34,197,94,0.12), rgba(255,255,255,0.04));
        border: 1px solid rgba(46,204,113,0.4);
        border-radius: 22px;
        padding: 2rem;
        text-align: center;
        margin-top: 1rem;
    }

    .result-number {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2ecc71 !important;
    }

    .progress-container {
        width: 100%;
        background-color: rgba(255,255,255,0.08);
        border-radius: 50px;
        overflow: hidden;
        margin-top: 10px;
        margin-bottom: 10px;
    }

    .progress-bar {
        background: linear-gradient(90deg, #16a34a, #4ade80);
        color: white;
        text-align: center;
        padding: 10px;
        font-weight: bold;
        border-radius: 50px;
    }

    .hero {
        background: linear-gradient(135deg, rgba(34,197,94,0.2), rgba(59,130,246,0.15));
        border: 1px solid rgba(255,255,255,0.08);
        padding: 2rem;
        border-radius: 28px;
        text-align: center;
        margin-bottom: 2rem;
        backdrop-filter: blur(10px);
    }

</style>
""", unsafe_allow_html=True)

# ============================================================================
# CABEÇALHO
# ============================================================================

st.markdown("""
<div class="hero">
    <h1 style="color:white !important;">
        🌾 Classificador Inteligente de Fertilidade do Solo
    </h1>

    <p style="font-size:1.2rem; color:white !important;">
        Sistema Inteligente baseado no SiBCS - Embrapa
    </p>

    <p style="color:#d1fae5 !important;">
        📊 Análise • 🤖 IA Gemini • 🌱 Fertilidade • 📈 Relatórios
    </p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:

    st.image(
        "https://cdn-icons-png.flaticon.com/512/2909/2909763.png",
        width=110
    )

    st.markdown("## 🌱 Sistema Inteligente")

    st.markdown("""
✅ Avaliação da fertilidade  
✅ Cálculo de V% e m%  
✅ Classificação SiBCS  
✅ Relatório técnico  
✅ IA Gemini integrada  
    """)

# ============================================================================
# SESSION STATE
# ============================================================================

if "dados_basicos" not in st.session_state:
    st.session_state.dados_basicos = {}

if "dados_calculados" not in st.session_state:
    st.session_state.dados_calculados = {}

# ============================================================================
# MENU
# ============================================================================

menu = st.radio(
    "Menu",
    [
        "📊 1. Dados do Solo",
        "🌱 2. Classificação",
        "🤖 3. Assistente IA",
        "📈 4. Relatório",
        "ℹ️ 5. Métodos"
    ],
    horizontal=True,
    label_visibility="collapsed"
)

# ============================================================================
# CULTURAS
# ============================================================================

necessidades_culturas = {
    "Soja": {
        "v_desejado": 75,
        "n_min": 40,
        "p_min": 25,
        "k_min": 0.4,
        "ph_min": 5.8,
        "ph_max": 6.5
    },
    "Milho Grão": {
        "v_desejado": 70,
        "n_min": 45,
        "p_min": 30,
        "k_min": 0.45,
        "ph_min": 5.6,
        "ph_max": 6.8
    },
    "Milho Semente": {
        "v_desejado": 75,
        "n_min": 50,
        "p_min": 35,
        "k_min": 0.5,
        "ph_min": 5.8,
        "ph_max": 6.8
    },
    "Trigo": {
        "v_desejado": 65,
        "n_min": 35,
        "p_min": 25,
        "k_min": 0.4,
        "ph_min": 5.5,
        "ph_max": 6.5
    },
    "Sorgo": {
        "v_desejado": 65,
        "n_min": 35,
        "p_min": 20,
        "k_min": 0.35,
        "ph_min": 5.5,
        "ph_max": 6.5
    },
    "Milheto": {
        "v_desejado": 60,
        "n_min": 30,
        "p_min": 18,
        "k_min": 0.3,
        "ph_min": 5.2,
        "ph_max": 6.2
    },
    "Cana-de-açúcar": {
        "v_desejado": 65,
        "n_min": 35,
        "p_min": 20,
        "k_min": 0.35,
        "ph_min": 5.5,
        "ph_max": 6.5
    },
    "Café": {
        "v_desejado": 70,
        "n_min": 40,
        "p_min": 25,
        "k_min": 0.4,
        "ph_min": 5.8,
        "ph_max": 6.3
    },
    "Arroz": {
        "v_desejado": 65,
        "n_min": 35,
        "p_min": 20,
        "k_min": 0.35,
        "ph_min": 5.5,
        "ph_max": 6.5
    },
    "Feijão": {
        "v_desejado": 65,
        "n_min": 35,
        "p_min": 20,
        "k_min": 0.35,
        "ph_min": 5.5,
        "ph_max": 6.5
    },
    "Algodão": {
        "v_desejado": 70,
        "n_min": 40,
        "p_min": 25,
        "k_min": 0.4,
        "ph_min": 5.8,
        "ph_max": 6.8
    },
    "Tomate": {
        "v_desejado": 85,
        "n_min": 50,
        "p_min": 35,
        "k_min": 0.5,
        "ph_min": 5.8,
        "ph_max": 6.8
    },
    "Alface": {
        "v_desejado": 80,
        "n_min": 45,
        "p_min": 30,
        "k_min": 0.45,
        "ph_min": 6.0,
        "ph_max": 7.0
    },
    "Cenoura": {
        "v_desejado": 75,
        "n_min": 40,
        "p_min": 25,
        "k_min": 0.4,
        "ph_min": 5.8,
        "ph_max": 6.8
    },
    "Batata": {
        "v_desejado": 80,
        "n_min": 45,
        "p_min": 30,
        "k_min": 0.45,
        "ph_min": 5.5,
        "ph_max": 6.5
    },
    "Cebola": {
        "v_desejado": 75,
        "n_min": 40,
        "p_min": 25,
        "k_min": 0.4,
        "ph_min": 6.0,
        "ph_max": 7.0
    },
    "Pimentão": {
        "v_desejado": 80,
        "n_min": 45,
        "p_min": 30,
        "k_min": 0.45,
        "ph_min": 5.8,
        "ph_max": 6.8
    },
    "Couve-flor": {
        "v_desejado": 75,
        "n_min": 40,
        "p_min": 25,
        "k_min": 0.4,
        "ph_min": 6.0,
        "ph_max": 7.0
    },
    "Mandioca": {
        "v_desejado": 60,
        "n_min": 30,
        "p_min": 15,
        "k_min": 0.3,
        "ph_min": 5.0,
        "ph_max": 6.5
    }
}

# ============================================================================
# ABA 1 - DADOS DO SOLO
# ============================================================================

if menu == "📊 1. Dados do Solo":

    st.markdown("## 📋 Dados Básicos do Solo")

    col1, col2 = st.columns(2)

    with col1:

        nitrogen = st.text_input("🌱 Nitrogênio", value="30")
        phosphorus = st.text_input("🔴 Fósforo", value="20")
        potassium = st.text_input("🟡 Potássio", value="0.25")

    with col2:

        sand = st.text_input("🏖️ Areia", value="350")
        silt = st.text_input("🏞️ Silte", value="300")
        clay = st.text_input("🧱 Argila", value="350")

    if st.button("✅ SALVAR DADOS"):

        st.session_state.dados_basicos = {

            "nitrogen": float(nitrogen),
            "phosphorus": float(phosphorus),
            "potassium": float(potassium),
            "sand": float(sand),
            "silt": float(silt),
            "clay": float(clay)
        }

        st.success("✅ Dados salvos!")

# ============================================================================
# ABA 2 - CLASSIFICAÇÃO
# ============================================================================

elif menu == "🌱 2. Classificação":

    st.markdown("## 🌱 Classificação")

    ph = st.text_input("🧪 pH", value="6.0")
    aluminum = st.text_input("⚠️ Alumínio", value="0.5")
    calcium = st.text_input("🥛 Cálcio", value="3.0")
    magnesium = st.text_input("🧂 Magnésio", value="1.5")
    h_al = st.text_input("📊 H + Al", value="3.5")

    cultura = st.selectbox(
        "🌾 Cultura",
        list(necessidades_culturas.keys())
    )

# ============================================================================
# ABA 3 - IA
# ============================================================================

elif menu == "🤖 3. Assistente IA":

    st.markdown("## 🤖 Assistente IA Gemini")

    pergunta = st.text_area(
        "💬 Faça sua pergunta:"
    )

    if st.button("🚀 GERAR RESPOSTA"):

        resposta = gerar_resposta_ia(
            pergunta,
            st.session_state.dados_basicos
        )

        st.markdown(f"""
        <div class="result-card">
            <h2>🤖 Resposta da IA</h2>
            <p>{resposta}</p>
        </div>
        """, unsafe_allow_html=True)

# ============================================================================
# ABA 4 - RELATÓRIO
# ============================================================================

elif menu == "📈 4. Relatório":

    st.markdown("## 📈 Relatório Técnico")

    if st.session_state.dados_basicos:

        relatorio = pd.DataFrame(
            st.session_state.dados_basicos.items(),
            columns=["Parâmetro", "Valor"]
        )

        st.dataframe(
            relatorio,
            use_container_width=True
        )

# ============================================================================
# ABA 5 - MÉTODOS
# ============================================================================

elif menu == "ℹ️ 5. Métodos":

    st.markdown("## ℹ️ Métodos Utilizados")

    st.markdown("""
    - Saturação por bases (V%)
    - Saturação por alumínio (m%)
    - Interpretação SiBCS
    - IA Gemini integrada
    """)

# ============================================================================
# RODAPÉ
# ============================================================================

st.markdown("---")

st.caption(
    "© 2026 - Sistema Inteligente de Fertilidade do Solo"
)
