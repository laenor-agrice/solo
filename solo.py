import streamlit as st
import pandas as pd

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
# CAIXAS DOS RESULTADOS
# ============================================================================

st.markdown("""
<style>

/* ==========================================================================
   CONTAINER DOS RESULTADOS
========================================================================== */

.analysis-box {
    background: linear-gradient(145deg, #0f172a, #111827);
    border: 2px solid #2563eb;
    border-left: 6px solid #60a5fa;
    border-radius: 18px;
    padding: 22px;
    margin-top: 18px;
    margin-bottom: 18px;
    box-shadow: 0 0 18px rgba(37,99,235,0.18);
    transition: all 0.3s ease;
}

/* Efeito hover */

.analysis-box:hover {
    transform: translateY(-3px);
    box-shadow: 0 0 28px rgba(96,165,250,0.35);
}

/* Título do resultado */

.analysis-box h3 {
    color: #60a5fa !important;
    font-size: 1.3rem;
    font-weight: 800;
    margin-bottom: 12px;
}

/* Texto interno */

.analysis-box p {
    color: #ffffff !important;
    font-size: 1.05rem;
    line-height: 1.6;
    margin-bottom: 8px;
}

/* Número destacado */

.analysis-highlight {
    color: #93c5fd !important;
    font-size: 2rem;
    font-weight: 900;
}

/* Linha separadora */

.analysis-divider {
    height: 2px;
    background: linear-gradient(to right, #2563eb, transparent);
    margin: 12px 0;
    border-radius: 10px;
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

# ============================================================================
# MENU
# ============================================================================

menu = st.radio(
    "Navegacao",
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
        "n_min": 40,
        "p_min": 15,
        "k_min": 0.35,
        "ph_min": 5.5,
        "ph_max": 6.5
    },
    "Milho (grao)": {
        "v_desejado": 65,
        "n_min": 50,
        "p_min": 20,
        "k_min": 0.40,
        "ph_min": 5.5,
        "ph_max": 6.5
    },
    "Feijao": {
        "v_desejado": 65,
        "n_min": 35,
        "p_min": 20,
        "k_min": 0.35,
        "ph_min": 5.5,
        "ph_max": 6.5
    },
    "Cafe": {
        "v_desejado": 70,
        "n_min": 40,
        "p_min": 25,
        "k_min": 0.40,
        "ph_min": 5.5,
        "ph_max": 6.5
    },
    "Pastagem": {
        "v_desejado": 50,
        "n_min": 30,
        "p_min": 10,
        "k_min": 0.25,
        "ph_min": 5.0,
        "ph_max": 6.5
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

        sand = st.text_input("🏖️ Areia (g/kg)", value="350", key="sand_input")
        silt = st.text_input("🏞️ Silte (g/kg)", value="300", key="silt_input")
        clay = st.text_input("🏺 Argila (g/kg)", value="350", key="clay_input")

        try:
            soma_textura = (
                float(sand.replace(",", ".")) +
                float(silt.replace(",", ".")) +
                float(clay.replace(",", "."))
            )

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

            st.success("✅ Dados basicos salvos com sucesso! Vá para a aba 'Classificacao'.")

        except ValueError:
            st.error("❌ Verifique os valores numericos inseridos. Use ponto decimal (ex: 1.5)")

# ============================================================================
# ABA 2 - CLASSIFICACAO
# ============================================================================

elif menu == "🌱 2. Classificacao":

    if not st.session_state.dados_basicos:
        st.warning("⚠️ Preencha primeiro os dados basicos na aba 'Dados do Solo'.")
        st.stop()

    st.markdown("## 🌱 Classificacao da Fertilidade")

    col1, col2 = st.columns(2)

    with col1:

        ph = st.text_input(
            "🧪 pH do Solo",
            value="6.0",
            key="ph_input"
        )

        aluminum = st.text_input(
            "⚠️ Aluminio (Al3+) - cmolc/dm3",
            value="0.50",
            key="al_input"
        )

        h_al = st.text_input(
            "📊 H + Al - cmolc/dm3",
            value="3.50",
            key="hal_input"
        )

    with col2:

        calcium = st.text_input(
            "🥛 Calcio (Ca2+) - cmolc/dm3",
            value="3.00",
            key="ca_input"
        )

        magnesium = st.text_input(
            "🧂 Magnesio (Mg2+) - cmolc/dm3",
            value="1.50",
            key="mg_input"
        )

        cultura = st.selectbox(
            "🌾 Cultura",
            list(necessidades_culturas.keys()),
            key="cultura_select"
        )

    st.markdown("---")

    if st.button("🔬 CALCULAR CLASSIFICACAO", key="calcular_classificacao"):

        try:
            dados = st.session_state.dados_basicos.copy()

            dados["ph"] = float(ph.replace(",", "."))
            dados["aluminum"] = float(aluminum.replace(",", "."))
            dados["h_al"] = float(h_al.replace(",", "."))
            dados["calcium"] = float(calcium.replace(",", "."))
            dados["magnesium"] = float(magnesium.replace(",", "."))

            sb = dados["calcium"] + dados["magnesium"] + dados["potassium"]
            ctc_efetiva = sb + dados["aluminum"]
            ctc_potencial = sb + dados["h_al"]
            v_percent = (sb / ctc_potencial * 100) if ctc_potencial > 0 else 0
            m_percent = (dados["aluminum"] / ctc_efetiva * 100) if ctc_efetiva > 0 else 0

            st.session_state.dados_calculados = dados
            st.session_state.sb = sb
            st.session_state.ctc_potencial = ctc_potencial
            st.session_state.v_percent = v_percent
            st.session_state.m_percent = m_percent
            st.session_state.cultura = cultura

            st.success("✅ Classificacao realizada com sucesso!")

        except ValueError as e:
            st.error(f"❌ Erro ao converter os dados: {e}")

    # ========================
    # EXIBIR RESULTADOS
    # ========================

    if "v_percent" in st.session_state:

        dados = st.session_state.dados_calculados
        sb = st.session_state.sb
        ctc_potencial = st.session_state.ctc_potencial
        v_percent = st.session_state.v_percent
        m_percent = st.session_state.m_percent

        st.markdown("---")
        st.markdown("## 📊 Resultados da Analise")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>🟢 Soma de Bases (SB)</h3>
                <h2>{sb:.2f}</h2>
                <small>cmolc/dm3</small>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h3>🟡 CTC Potencial</h3>
                <h2>{ctc_potencial:.2f}</h2>
                <small>cmolc/dm3</small>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h3>🟢 Saturacao por Bases</h3>
                <h2>{v_percent:.1f}%</h2>
                <small>V%</small>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <h3>🔴 Saturacao por Al</h3>
                <h2>{m_percent:.1f}%</h2>
                <small>m%</small>
            </div>
            """, unsafe_allow_html=True)

        # Barra de progresso
        st.markdown("### 📈 Indice de Fertilidade (V%)")

        progress_html = f"""
        <div class="progress-container">
            <div class="progress-bar" style="width:{min(v_percent, 100)}%;">
                {v_percent:.1f}%
            </div>
        </div>
        """
        st.markdown(progress_html, unsafe_allow_html=True)

        # Classificacao
        if v_percent >= 70:
            classe = "Eutrofico (Muito Fertil)"
            cor = "🟢"
        elif v_percent >= 50:
            classe = "Eutrofico (Fertil)"
            cor = "🟢"
        elif v_percent >= 25:
            classe = "Distrofico (Baixa Fertilidade)"
            cor = "🟡"
        else:
            classe = "Alico (Muito Pobre)"
            cor = "🔴"

        resultado_html = f"""
        <div class="result-card">
            <h2>{cor} Classificacao SiBCS</h2>
            <p class="result-number">{classe}</p>
        </div>
        """
        st.markdown(resultado_html, unsafe_allow_html=True)

        # Adequacao
        st.markdown("## 🌾 Adequacao da Cultura")
        nec = necessidades_culturas[st.session_state.cultura]

        if v_percent >= nec["v_desejado"]:
            st.success(f"✅ V% = {v_percent:.1f}% - Adequado para {st.session_state.cultura}")
        else:
            st.error(f"❌ V% = {v_percent:.1f}% - Necessario calagem para {st.session_state.cultura}")

        if dados["phosphorus"] >= nec["p_min"]:
            st.success(f"✅ Fosforo = {dados['phosphorus']:.1f} mg/dm3 - Adequado")
        else:
            st.error(f"❌ Fosforo = {dados['phosphorus']:.1f} mg/dm3 - Abaixo do ideal")

        if dados["potassium"] >= nec["k_min"]:
            st.success(f"✅ Potassio = {dados['potassium']:.2f} cmolc/dm3 - Adequado")
        else:
            st.error(f"❌ Potassio = {dados['potassium']:.2f} cmolc/dm3 - Abaixo do ideal")

        if nec["ph_min"] <= dados["ph"] <= nec["ph_max"]:
            st.success(f"✅ pH = {dados['ph']:.1f} - Adequado")
        else:
            st.error(f"❌ pH = {dados['ph']:.1f} - Fora da faixa ideal")

        # Score
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

        st.markdown("---")

        if score >= 15:
            resultado = "🟢 ALTA FERTILIDADE"
        elif score >= 8:
            resultado = "🟡 FERTILIDADE MEDIA"
        else:
            resultado = "🔴 BAIXA FERTILIDADE"

        resultado_final_html = f"""
        <div class="result-card">
            <h2>RESULTADO FINAL</h2>
            <p class="result-number">{resultado}</p>
            <p>Score: {score}/20 pontos</p>
        </div>
        """
        st.markdown(resultado_final_html, unsafe_allow_html=True)

# ============================================================================
# ABA 3 - RELATORIO
# ============================================================================

elif menu == "📈 3. Relatorio":

    st.markdown("## 📈 Relatorio Tecnico")

    if "v_percent" not in st.session_state:
        st.warning("⚠️ Execute a classificacao primeiro na aba 'Classificacao'.")
    else:
        dados = st.session_state.dados_calculados

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
                f"{st.session_state.sb:.2f} cmolc/dm3",
                f"{st.session_state.ctc_potencial:.2f} cmolc/dm3",
                f"{st.session_state.v_percent:.1f}%",
                f"{st.session_state.m_percent:.1f}%",
                f"{dados['organic_matter']:.1f} g/kg",
                f"{dados['bulk_density']:.2f} g/cm3"
            ]
        })

        st.dataframe(relatorio, hide_index=True, use_container_width=True)

        csv = relatorio.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Baixar Relatorio (CSV)",
            data=csv,
            file_name="relatorio_solo.csv",
            mime="text/csv",
            key="download_csv"
        )

# ============================================================================
# MÉTODOS
# ============================================================================

elif menu == "ℹ️ 4. Métodos":

    st.markdown("## ℹ️ Métodos Utilizados")

    with st.expander("📊 Saturação por Bases (V%)"):

        st.markdown("""
### Fórmula:

V% = (SB / CTC) × 100

Onde:

- SB = Soma de Bases
- CTC = Capacidade de Troca de Cátions
        """)

    with st.expander("🔬 Saturação por Alumínio (m%)"):

        st.markdown("""
### Fórmula:

m% = (Al³⁺ / CTC efetiva) × 100
        """)

    with st.expander("🌾 Interpretação Agronômica"):

        st.markdown("""
| V% | Interpretação |
|---|---|
| > 70 | Muito fértil |
| 50-70 | Fértil |
| 25-50 | Distrófico |
| < 25 | Álico |
        """)

# ============================================================================
# RODAPÉ
# ============================================================================

st.markdown("---")

st.caption(
    "© 2026 - Classificador de Fertilidade do Solo | SiBCS - Embrapa"
)
