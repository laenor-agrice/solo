import streamlit as st
import pandas as pd
import joblib
# ==================================
# CARREGAR MODELO IA
# ==================================

modelo = joblib.load('modelo.pkl')

features = joblib.load('features.pkl')
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

/* Título do card */

.result-card h2 {
    color: #60a5fa !important;
    font-size: 2rem !important;
    font-weight: 800 !important;
}

/* Texto do card */

.result-card p {
    color: #ffffff !important;
    font-size: 1.15rem !important;
    font-weight: 500 !important;
}

/* Número principal */

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

/* Hover */

.result-box:hover {
    transform: translateY(-4px);
    box-shadow: 0 0 28px rgba(96,165,250,0.35) !important;
}

/* Título */

.result-title {
    color: #93c5fd !important;
    font-size: 1.15rem !important;
    font-weight: 700 !important;
    margin-bottom: 15px !important;
}

/* Valor */

.result-value {
    color: #ffffff !important;
    font-size: 2.3rem !important;
    font-weight: 900 !important;
    margin-bottom: 8px !important;
}

/* Unidade */

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

#=============================================================
# ABA 2
#=============================================================

st.markdown("""
<style>

/* =========================
   CARDS MÉTRICOS
========================= */

.metric-card{
    background: linear-gradient(145deg, #111827, #1f2937);
    border: 2px solid #2563eb;
    border-radius: 18px;
    padding: 20px;
    text-align: center;
    box-shadow: 0 0 15px rgba(37,99,235,0.2);
    margin-bottom: 15px;
}

.metric-card h3{
    color: #93c5fd;
    font-size: 1rem;
    margin-bottom: 10px;
}

.metric-card h2{
    color: white;
    font-size: 2rem;
    font-weight: 800;
}

.metric-card small{
    color: #cbd5e1;
}

/* =========================
   BARRA DE PROGRESSO
========================= */

.progress-container{
    width: 100%;
    background-color: #1f2937;
    border-radius: 30px;
    overflow: hidden;
    margin-top: 15px;
    margin-bottom: 25px;
    border: 2px solid #2563eb;
}

.progress-bar{
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
# CAIXAS DOS RESULTADOS PRINCIPAIS
# ============================================================================

st.markdown("""
<style>

/* Cards dos resultados */

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

/* Hover */

.result-box:hover {
    transform: translateY(-4px);
    box-shadow: 0 0 28px rgba(96,165,250,0.35) !important;
}

/* Título */

.result-title {
    color: #93c5fd !important;
    font-size: 1.15rem !important;
    font-weight: 700 !important;
    margin-bottom: 15px !important;
}

/* Valor */

.result-value {
    color: #ffffff !important;
    font-size: 2.3rem !important;
    font-weight: 900 !important;
    margin-bottom: 8px !important;
}

/* Unidade */

.result-unit {
    color: #cbd5e1 !important;
    font-size: 0.95rem !important;
    font-weight: 500 !important;
}

</style>
""", unsafe_allow_html=True)

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.image(
        "https://cdn-icons-png.flaticon.com/512/2934/2934128.png",
        width=80
    )

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

    st.caption("Versao 3.0")
    st.caption("Desenvolvido em Streamlit")

# ============================================================================
# SESSION STATE
# ============================================================================

if "dados_basicos" not in st.session_state:
    st.session_state.dados_basicos = {}

if "dados_calculados" not in st.session_state:
    st.session_state.dados_calculados = {}

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

    "Soja": {
        "v_desejado": 60,
        "ph_min": 5.5,
        "ph_max": 6.5,
        "p_min": 15,
        "k_min": 0.35
    },

    "Milho": {
        "v_desejado": 65,
        "ph_min": 5.5,
        "ph_max": 6.5,
        "p_min": 20,
        "k_min": 0.40
    },

    "Feijao": {
        "v_desejado": 65,
        "ph_min": 5.5,
        "ph_max": 6.5,
        "p_min": 20,
        "k_min": 0.35
    },

    "Cafe": {
        "v_desejado": 70,
        "ph_min": 5.5,
        "ph_max": 6.5,
        "p_min": 25,
        "k_min": 0.40
    },

    "Pastagem": {
        "v_desejado": 50,
        "ph_min": 5.0,
        "ph_max": 6.0,
        "p_min": 10,
        "k_min": 0.25
    },

    "Algodao": {
        "v_desejado": 70,
        "ph_min": 5.5,
        "ph_max": 6.5,
        "p_min": 25,
        "k_min": 0.45
    },

    "Cana-de-acucar": {
        "v_desejado": 60,
        "ph_min": 5.5,
        "ph_max": 6.5,
        "p_min": 15,
        "k_min": 0.30
    },

    "Sorgo": {
        "v_desejado": 55,
        "ph_min": 5.2,
        "ph_max": 6.2,
        "p_min": 12,
        "k_min": 0.30
    },

    "Trigo": {
        "v_desejado": 65,
        "ph_min": 5.5,
        "ph_max": 6.5,
        "p_min": 18,
        "k_min": 0.35
    },

    "Tomate": {
        "v_desejado": 80,
        "ph_min": 6.0,
        "ph_max": 6.8,
        "p_min": 30,
        "k_min": 0.50
    },

    "Eucalipto": {
        "v_desejado": 45,
        "ph_min": 5.0,
        "ph_max": 6.0,
        "p_min": 8,
        "k_min": 0.20
    },

    "Citrus": {
        "v_desejado": 70,
        "ph_min": 5.5,
        "ph_max": 6.5,
        "p_min": 20,
        "k_min": 0.35
    },

    "Arroz": {
        "v_desejado": 50,
        "ph_min": 5.0,
        "ph_max": 6.0,
        "p_min": 10,
        "k_min": 0.25
    }
}

# ============================================================================
# ABA 1 - DADOS DO SOLO
# ============================================================================

if menu == "📊 1. Dados do Solo":

    st.markdown("## 📋 Dados Basicos do Solo")

    col1, col2 = st.columns(2)

    with col1:

        st.markdown("### 🧪 Macronutrientes")

        nitrogen = st.text_input(
            "🌱 Nitrogenio (N) - mg/dm3",
            value="30.0",
            key="n_input"
        )

        phosphorus = st.text_input(
            "🔴 Fosforo (P) - mg/dm3",
            value="20.0",
            key="p_input"
        )

        potassium = st.text_input(
            "🟡 Potassio (K+) - cmolc/dm3",
            value="0.25",
            key="k_input"
        )

        st.markdown("### 🌿 Materia Organica")

        organic_matter = st.text_input(
            "🌱 Materia Organica (g/kg)",
            value="25.0",
            key="om_input"
        )

    with col2:

        st.markdown("### ⚖️ Densidade")

        bulk_density = st.text_input(
            "📦 Densidade do Solo (g/cm3)",
            value="1.20",
            key="bd_input"
        )

        particle_density = st.text_input(
            "💎 Densidade de Particula (g/cm3)",
            value="2.65",
            key="pd_input"
        )

        st.markdown("### 🏺 Textura")

        sand = st.text_input(
            "🏖️ Areia (g/kg)",
            value="350",
            key="sand_input"
        )

        silt = st.text_input(
            "🏞️ Silte (g/kg)",
            value="300",
            key="silt_input"
        )

        clay = st.text_input(
            "🏺 Argila (g/kg)",
            value="350",
            key="clay_input"
        )

        # SOMA DA TEXTURA
        try:

            soma_textura = (
                float(sand.replace(",", ".")) +
                float(silt.replace(",", ".")) +
                float(clay.replace(",", "."))
            )

            if abs(soma_textura - 1000) > 10:

                st.warning(
                    f"⚠️ Soma da textura = {soma_textura:.0f} g/kg. "
                    "O ideal é 1000 g/kg."
                )

        except:
            pass

    st.markdown("---")

    # BOTÃO SALVAR
    if st.button(
        "✅ SALVAR DADOS BASICOS",
        key="salvar_basicos"
    ):

        try:

            st.session_state.dados_basicos = {

                "nitrogen": float(
                    nitrogen.replace(",", ".")
                ),

                "phosphorus": float(
                    phosphorus.replace(",", ".")
                ),

                "potassium": float(
                    potassium.replace(",", ".")
                ),

                "organic_matter": float(
                    organic_matter.replace(",", ".")
                ),

                "bulk_density": float(
                    bulk_density.replace(",", ".")
                ),

                "particle_density": float(
                    particle_density.replace(",", ".")
                ),

                "sand": float(
                    sand.replace(",", ".")
                ),

                "silt": float(
                    silt.replace(",", ".")
                ),

                "clay": float(
                    clay.replace(",", ".")
                )
            }

            # FLAG DE CONFIRMACAO
            st.session_state.dados_salvos = True

            st.success(
                "✅ Dados básicos salvos com sucesso! "
                "Agora vá para a aba 'Classificação'."
            )

        except ValueError:

            st.error(
                "❌ Verifique os valores numéricos inseridos."
            )
# ============================================================================
# ABA 2 - CLASSIFICACAO
# ============================================================================

elif menu == "🌱 2. Classificacao":

    # VERIFICA SE OS DADOS FORAM SALVOS
    if (
        "dados_basicos" not in st.session_state
        or not st.session_state.dados_basicos
    ):
        st.warning("⚠️ Preencha e salve os dados na ABA 1.")
        st.stop()

    st.markdown("## 🌱 Classificação da Fertilidade")

    col1, col2 = st.columns(2)

    # ==========================================================
    # COLUNA 1
    # ==========================================================

    with col1:

        ph = st.text_input(
            "🧪 pH do Solo",
            value="6.0"
        )

        aluminum = st.text_input(
            "⚠️ Alumínio (Al³⁺) - cmolc/dm³",
            value="0.50"
        )

        h_al = st.text_input(
            "📊 H + Al - cmolc/dm³",
            value="3.50"
        )

    # ==========================================================
    # COLUNA 2
    # ==========================================================

    with col2:

        calcium = st.text_input(
            "🥛 Cálcio (Ca²⁺)",
            value="3.00"
        )

        magnesium = st.text_input(
            "🧂 Magnésio (Mg²⁺)",
            value="1.50"
        )

        cultura = st.selectbox(
            "🌾 Cultura",
            list(necessidades_culturas.keys())
        )

    st.markdown("---")

    # ==========================================================
    # BOTAO CALCULAR
    # ==========================================================

    if st.button("🔬 CALCULAR CLASSIFICACAO"):

        try:

            dados = st.session_state.dados_basicos.copy()

            dados["ph"] = float(ph.replace(",", "."))
            dados["aluminum"] = float(aluminum.replace(",", "."))
            dados["h_al"] = float(h_al.replace(",", "."))
            dados["calcium"] = float(calcium.replace(",", "."))
            dados["magnesium"] = float(magnesium.replace(",", "."))

            # ==================================================
            # CALCULOS
            # ==================================================

            sb = (
                dados["calcium"]
                + dados["magnesium"]
                + dados["potassium"]
            )

            ctc_efetiva = sb + dados["aluminum"]

            ctc_potencial = sb + dados["h_al"]

            if ctc_potencial > 0:
                v_percent = (sb / ctc_potencial) * 100
            else:
                v_percent = 0

            if ctc_efetiva > 0:
                m_percent = (
                    dados["aluminum"] / ctc_efetiva
                ) * 100
            else:
                m_percent = 0

            # ==================================================
            # SESSION STATE
            # ==================================================

            st.session_state.dados_calculados = dados
            st.session_state.sb = sb
            st.session_state.ctc_potencial = ctc_potencial
            st.session_state.v_percent = v_percent
            st.session_state.m_percent = m_percent
            st.session_state.cultura = cultura

            st.success("✅ Classificação realizada com sucesso!")
# ==================================================
# IA - CLASSIFICAÇÃO AUTOMÁTICA
# ==================================================

entrada_ia = pd.DataFrame([[

    dados["nitrogen"],
    dados["phosphorus"],
    dados["potassium"],
    dados["ph"],
    dados["organic_matter"],
    dados["bulk_density"]

]], columns=features)

pred_ia = modelo.predict(entrada_ia)

st.markdown("---")

st.markdown("## 🤖 Inteligência Artificial")

st.success(f"Classe prevista pela IA: {pred_ia[0]}")

    # ==========================================================
    # MOSTRAR RESULTADOS
    # ==========================================================

    if "v_percent" in st.session_state:

        dados = st.session_state.dados_calculados

        sb = st.session_state.sb
        ctc_potencial = st.session_state.ctc_potencial
        v_percent = st.session_state.v_percent
        m_percent = st.session_state.m_percent

        st.markdown("---")
        st.markdown("## 📊 Resultados")

        col1, col2, col3, col4 = st.columns(4)

        # ======================================================
        # CARD SB
        # ======================================================

        with col1:

            st.markdown(f"""
            <div class="metric-card">
                <h3>SB</h3>
                <h2>{sb:.2f}</h2>
                <small>cmolc/dm³</small>
            </div>
            """, unsafe_allow_html=True)

        # ======================================================
        # CARD CTC
        # ======================================================

        with col2:

            st.markdown(f"""
            <div class="metric-card">
                <h3>CTC Potencial</h3>
                <h2>{ctc_potencial:.2f}</h2>
                <small>cmolc/dm³</small>
            </div>
            """, unsafe_allow_html=True)

        # ======================================================
        # CARD V%
        # ======================================================

        with col3:

            st.markdown(f"""
            <div class="metric-card">
                <h3>V%</h3>
                <h2>{v_percent:.1f}%</h2>
                <small>Saturação por Bases</small>
            </div>
            """, unsafe_allow_html=True)

        # ======================================================
        # CARD m%
        # ======================================================

        with col4:

            st.markdown(f"""
            <div class="metric-card">
                <h3>m%</h3>
                <h2>{m_percent:.1f}%</h2>
                <small>Saturação por Al</small>
            </div>
            """, unsafe_allow_html=True)

        # ======================================================
        # BARRA DE FERTILIDADE
        # ======================================================

        st.markdown("### 📈 Índice de Fertilidade")

        st.markdown(f"""
        <div class="progress-container">
            <div class="progress-bar"
                 style="width:{min(v_percent, 100)}%;">
                 {v_percent:.1f}%
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ======================================================
        # CLASSIFICACAO
        # ======================================================

        if v_percent >= 70:
            classe = "Eutrófico (Muito Fértil)"
            cor = "🟢"

        elif v_percent >= 50:
            classe = "Eutrófico"
            cor = "🟢"

        elif v_percent >= 25:
            classe = "Distrófico"
            cor = "🟡"

        else:
            classe = "Álico"
            cor = "🔴"

        st.markdown(f"""
        <div class="result-card">
            <h2>{cor} Classificação SiBCS</h2>
            <p class="result-number">
                {classe}
            </p>
        </div>
        """, unsafe_allow_html=True)

        # ======================================================
        # ADEQUACAO
        # ======================================================

        st.markdown("## 🌾 Adequação da Cultura")

        nec = necessidades_culturas[
            st.session_state.cultura
        ]

        if v_percent >= nec["v_desejado"]:
            st.success("✅ Saturação por bases adequada")
        else:
            st.error("❌ Necessidade de calagem")

        if dados["phosphorus"] >= nec["p_min"]:
            st.success("✅ Fósforo adequado")
        else:
            st.error("❌ Fósforo abaixo do ideal")

        if dados["potassium"] >= nec["k_min"]:
            st.success("✅ Potássio adequado")
        else:
            st.error("❌ Potássio abaixo do ideal")

        if nec["ph_min"] <= dados["ph"] <= nec["ph_max"]:
            st.success("✅ pH adequado")
        else:
            st.error("❌ pH fora da faixa ideal")

        # ======================================================
        # SCORE
        # ======================================================

        score = 0

        if v_percent >= 70:
            score += 5

        elif v_percent >= 50:
            score += 3

        if dados["phosphorus"] >= 20:
            score += 3

        if dados["potassium"] >= 0.35:
            score += 3

        if dados["aluminum"] < 0.5:
            score += 4

        if 5.5 <= dados["ph"] <= 6.5:
            score += 5

        # ======================================================
        # RESULTADO FINAL
        # ======================================================

        st.markdown("---")

        if score >= 15:
            resultado = "🟢 ALTA FERTILIDADE"

        elif score >= 8:
            resultado = "🟡 FERTILIDADE MÉDIA"

        else:
            resultado = "🔴 BAIXA FERTILIDADE"

        st.markdown(f"""
        <div class="result-card">
            <h2>RESULTADO FINAL</h2>
            <p class="result-number">
                {resultado}
            </p>
            <p>Score: {score}/20</p>
        </div>
        """, unsafe_allow_html=True)

# ============================================================================
# ABA 3 - RELATORIO
# ============================================================================

elif menu == "📈 3. Relatorio":

    st.markdown("## 📈 Relatorio Tecnico")

    # ==========================================================
    # VERIFICACOES
    # ==========================================================

    if (
        "v_percent" not in st.session_state
        or "dados_calculados" not in st.session_state
        or "cultura" not in st.session_state
    ):

        st.warning(
            "⚠️ Execute primeiro a classificação na ABA 2."
        )

        st.stop()

    # ==========================================================
    # DADOS
    # ==========================================================

    dados = st.session_state.dados_calculados

    sb = st.session_state.sb
    ctc_potencial = st.session_state.ctc_potencial
    v_percent = st.session_state.v_percent
    m_percent = st.session_state.m_percent
    cultura = st.session_state.cultura

    # ==========================================================
    # DATAFRAME
    # ==========================================================

    relatorio = pd.DataFrame({

        "Parametro": [
            "pH",
            "Nitrogenio (N)",
            "Fosforo (P)",
            "Potassio (K+)",
            "Calcio (Ca2+)",
            "Magnesio (Mg2+)",
            "Aluminio (Al3+)",
            "H + Al",
            "Soma de Bases (SB)",
            "CTC Potencial",
            "Saturacao por Bases (V%)",
            "Saturacao por Al (m%)",
            "Materia Organica",
            "Densidade do Solo"
        ],

        "Valor": [
            f"{dados['ph']:.1f}",
            f"{dados['nitrogen']:.1f} mg/dm3",
            f"{dados['phosphorus']:.1f} mg/dm3",
            f"{dados['potassium']:.2f} cmolc/dm3",
            f"{dados['calcium']:.2f} cmolc/dm3",
            f"{dados['magnesium']:.2f} cmolc/dm3",
            f"{dados['aluminum']:.2f} cmolc/dm3",
            f"{dados['h_al']:.2f} cmolc/dm3",
            f"{sb:.2f} cmolc/dm3",
            f"{ctc_potencial:.2f} cmolc/dm3",
            f"{v_percent:.1f}%",
            f"{m_percent:.1f}%",
            f"{dados['organic_matter']:.1f} g/kg",
            f"{dados['bulk_density']:.2f} g/cm3"
        ]
    })

    st.dataframe(
        relatorio,
        hide_index=True,
        use_container_width=True
    )

    # ==========================================================
    # DOWNLOAD CSV
    # ==========================================================

    csv = relatorio.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="📥 Baixar Relatorio (CSV)",
        data=csv,
        file_name="relatorio_solo.csv",
        mime="text/csv",
        key="download_csv"
    )

    # ==========================================================
    # RECOMENDACOES
    # ==========================================================

    st.markdown("---")
    st.markdown("## 🌾 Recomendações Agronômicas")

    st.success(
        f"✅ Cultura selecionada: {cultura}"
    )

    # ==========================================================
    # CALAGEM
    # ==========================================================

    v2 = necessidades_culturas[
        cultura
    ]["v_desejado"]

    nc = (
        (v2 - v_percent)
        * ctc_potencial
    ) / 100

    if nc < 0:
        nc = 0

    prnt = 80

    nc_corrigida = nc * (100 / prnt)

    # ==========================================================
    # GESSAGEM
    # ==========================================================

    if dados["clay"] >= 350:
        gesso = nc_corrigida * 0.5
    else:
        gesso = 0

    # ==========================================================
    # SESSION STATE
    # ==========================================================

    st.session_state.nc_corrigida = nc_corrigida
    st.session_state.prnt = prnt
    st.session_state.gesso = gesso

    # ==========================================================
    # RESULTADOS
    # ==========================================================

    st.info(
        f"🪨 Aplicar {nc_corrigida:.2f} t/ha "
        f"de calcário com PRNT {prnt}%"
    )

    if gesso > 0:

        st.warning(
            f"🌱 Recomenda-se gessagem de "
            f"{gesso:.2f} t/ha"
        )

    else:

        st.success(
            "✅ Gessagem não necessária"
        )

    # ==========================================================
    # ADUBACAO
    # ==========================================================

    if dados["phosphorus"] < 15:

        st.error(
            "🔴 Necessária adubação fosfatada"
        )

    else:

        st.success(
            "✅ Fósforo em nível adequado"
        )

    if dados["potassium"] < 0.30:

        st.error(
            "🔴 Necessária adubação potássica"
        )

    else:

        st.success(
            "✅ Potássio em nível adequado"
        )
# ============================================================================
# MÉTODOS
# ============================================================================

elif menu == "ℹ️ 4. Métodos":

    st.markdown("## ℹ️ Métodos Utilizados")

    # ==========================================================
    # SATURAÇÃO POR BASES
    # ==========================================================

    with st.expander("📊 Saturação por Bases (V%)"):

        st.markdown("### Fórmula:")

        st.latex(
            r"V\% = \frac{SB}{CTC} \times 100"
        )

        st.markdown("""
Onde:

- SB = Soma de Bases
- CTC = Capacidade de Troca de Cátions
        """)

    # ==========================================================
    # SATURAÇÃO POR ALUMÍNIO
    # ==========================================================

    with st.expander("🔬 Saturação por Alumínio (m%)"):

        st.markdown("### Fórmula:")

        st.latex(
            r"m\% = \frac{Al^{3+}}{CTC\ efetiva} \times 100"
        )

        st.markdown("""
Onde:

- Al³⁺ = Alumínio trocável
- CTC efetiva = SB + Al³⁺
        """)

    # ==========================================================
    # INTERPRETAÇÃO
    # ==========================================================

    with st.expander("🌾 Interpretação Agronômica"):

        st.markdown("""
| V% | Interpretação |
|---|---|
| > 70 | Muito fértil |
| 50-70 | Fértil |
| 25-50 | Distrófico |
| < 25 | Álico |
        """)

    # ==========================================================
    # CALAGEM
    # ==========================================================

    with st.expander("🪨 Cálculo da Calagem"):

        st.markdown("### Fórmula utilizada:")

        st.latex(
            r"NC = \frac{(V_2 - V_1) \times CTC}{100}"
        )

        st.markdown("""
Onde:

- NC = Necessidade de calcário
- V₂ = Saturação desejada
- V₁ = Saturação atual
- CTC = Capacidade de troca catiônica
        """)

    # ==========================================================
    # GESSAGEM
    # ==========================================================

    with st.expander("🌱 Cálculo da Gessagem"):

        st.markdown("""
### Critério utilizado:

- Solos com argila > 350 g/kg
- Gessagem = 50% da dose de calcário
        """)
# ============================================================================
# RODAPÉ
# ============================================================================

st.markdown("---")

st.caption(
    "© 2026 - Classificador de Fertilidade do Solo | Créditos ao SiBCS - Embrapa"
)
