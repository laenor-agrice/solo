import streamlit as st
import pandas as pd
import traceback
import sys
import math
import os

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
# FUNÇÕES AUXILIARES
# ============================================================================

def safe_float(valor, default=0.0):
    try:
        if valor is None or valor == "":
            return default
        return float(str(valor).replace(",", "."))
    except:
        return default

# ============================================================================
# FUNÇÃO DE CÁLCULO DO pH
# ============================================================================

def calcular_ph(dados):
    try:
        ca = max(dados.get('calcium', 0), 0)
        mg = max(dados.get('magnesium', 0), 0)
        k = max(dados.get('potassium', 0), 0)
        al = max(dados.get('aluminum', 0), 0)
        hal = max(dados.get('h_al', 0), 0)
        mo = max(dados.get('organic_matter', 0), 0)

        if ca == 0 and mg == 0 and k == 0 and al == 0 and hal == 0:
            return 7.0

        soma_bases = ca + mg + (k * 10)

        ph = (
            5.8
            + (soma_bases * 0.08)
            - (al * 0.25)
            - (hal * 0.05)
            + (mo * 0.003)
        )

        ph = max(4.0, min(7.5, ph))

        return round(ph, 1)

    except:
        return 5.5

# ============================================================================
# FUNÇÃO CALAGEM
# ============================================================================

def calcular_calagem(v_atual, v_desejado, ctc, prnt=80):
    try:
        if v_atual >= v_desejado:
            return 0

        nc = ((v_desejado - v_atual) * ctc) / 100
        nc_corrigida = nc * (100 / prnt)

        return round(max(nc_corrigida, 0), 2)

    except:
        return 0

# ============================================================================
# FUNÇÃO GESSAGEM
# ============================================================================

def calcular_gessagem(calagem_t_ha, clay_gkg):
    try:
        if clay_gkg >= 600:
            return round(calagem_t_ha * 0.7, 2)
        elif clay_gkg >= 350:
            return round(calagem_t_ha * 0.5, 2)
        elif clay_gkg >= 200:
            return round(calagem_t_ha * 0.3, 2)
        return 0
    except:
        return 0

# ============================================================================
# CONVERSÃO PARA VASO
# ============================================================================

def calcular_adubacao_vaso(area_vaso_m2, recomendacao_kg_ha):
    kg_por_m2 = recomendacao_kg_ha / 10000
    kg_vaso = kg_por_m2 * area_vaso_m2
    gramas_vaso = kg_vaso * 1000
    return round(gramas_vaso, 2)

# ============================================================================
# IA MAIS ROBUSTA
# ============================================================================

try:
    import joblib
    JOBLIB_AVAILABLE = True
except:
    JOBLIB_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except:
    NUMPY_AVAILABLE = False

@st.cache_resource
def carregar_modelo():
    try:
        if JOBLIB_AVAILABLE and os.path.exists("modelo.pkl") and os.path.exists("features.pkl"):
            modelo = joblib.load("modelo.pkl")
            features = joblib.load("features.pkl")
            return modelo, features
        return None, None
    except:
        return None, None

modelo, features = carregar_modelo()

# ============================================================================
# IA REFORÇADA
# ============================================================================

def fazer_predicao_ia(dados):

    try:

        ph = dados.get("ph", 5.5)
        v_percent = dados.get("v_percent", 50)
        al = dados.get("aluminum", 0)
        p = dados.get("phosphorus", 0)
        k = dados.get("potassium", 0)
        mo = dados.get("organic_matter", 0)
        clay = dados.get("clay", 0)
        ca = dados.get("calcium", 0)
        mg = dados.get("magnesium", 0)

        score = 0

        # pH
        if 5.5 <= ph <= 6.5:
            score += 3
        elif 5.0 <= ph <= 7.0:
            score += 2
        else:
            score -= 2

        # Saturação por bases
        if v_percent >= 65:
            score += 3
        elif v_percent >= 50:
            score += 2
        elif v_percent >= 35:
            score += 1
        else:
            score -= 2

        # Alumínio
        if al <= 0.2:
            score += 2
        elif al <= 0.5:
            score += 1
        else:
            score -= 2

        # Fósforo
        if p >= 15:
            score += 2
        elif p >= 8:
            score += 1
        else:
            score -= 1

        # Potássio
        if k >= 0.35:
            score += 2
        elif k >= 0.20:
            score += 1
        else:
            score -= 1

        # Matéria orgânica
        if mo >= 30:
            score += 2
        elif mo >= 20:
            score += 1

        # Textura
        if 150 <= clay <= 650:
            score += 1

        # Ca + Mg
        if (ca + mg) >= 3:
            score += 1

        # Resultado final
        if score >= 10:
            return "🟢 ALTA FERTILIDADE", "Excelente potencial agrícola"

        elif score >= 6:
            return "🟡 MÉDIA FERTILIDADE", "Solo com potencial moderado"

        else:
            return "🔴 BAIXA FERTILIDADE", "Solo necessita correção"

    except Exception as e:
        return "⚠️ NÃO FOI POSSÍVEL CLASSIFICAR", str(e)

# ============================================================================
# CSS MODERNO
# ============================================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* FUNDO */

.stApp {
    background: linear-gradient(135deg, #07140f 0%, #0b1f16 50%, #10251c 100%);
    color: white;
}

/* CONTAINER */

.block-container {
    padding-top: 1rem !important;
    padding-bottom: 2rem !important;
    max-width: 100% !important;
    width: 100% !important;
}

/* TEXTOS */

h1, h2, h3, h4, h5 {
    color: #ffffff !important;
    font-weight: 800 !important;
}

p, label, span, div {
    color: #d7f5df !important;
}

/* SIDEBAR */

section[data-testid="stSidebar"] {
    background: #071b12 !important;
    border-right: 1px solid rgba(255,255,255,0.08);
}

/* INPUTS */

.stTextInput input,
.stNumberInput input,
textarea {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    color: white !important;
    border-radius: 14px !important;
    padding: 12px !important;
}

/* SELECTBOX SIMPLES */

div[data-baseweb="select"] > div {
    background: rgba(255,255,255,0.06) !important;
    border-radius: 14px !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    color: white !important;
}

/* BOTÕES */

.stButton button {
    background: linear-gradient(90deg,#1f7a52,#29a36a) !important;
    color: white !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 12px 20px !important;
    font-weight: 700 !important;
    width: 100%;
}

/* TABS */

.stTabs [data-baseweb="tab-list"] {
    gap: 10px;
    background: transparent;
}

.stTabs [data-baseweb="tab"] {
    background: rgba(255,255,255,0.06) !important;
    border-radius: 12px !important;
    padding: 12px 18px !important;
    color: white !important;
    font-weight: 700 !important;
    font-size: 15px !important;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(90deg,#1f7a52,#29a36a) !important;
}

/* MÉTRICAS */

div[data-testid="metric-container"] {
    background: rgba(255,255,255,0.06);
    border-radius: 18px;
    padding: 18px;
    border: 1px solid rgba(255,255,255,0.08);
}

/* DATAFRAME */

[data-testid="stDataFrame"] {
    border-radius: 16px !important;
    overflow: hidden;
}

/* HEADER */

.header-box {
    background: linear-gradient(135deg,#123524,#1b4b34);
    border-radius: 24px;
    padding: 30px;
    margin-bottom: 20px;
}

/* CARDS */

.card {
    background: rgba(255,255,255,0.06);
    border-radius: 18px;
    padding: 20px;
    border: 1px solid rgba(255,255,255,0.08);
}

/* RADIO */

div[role="radiogroup"] {
    gap: 8px;
}

div[role="radiogroup"] label {
    background: rgba(255,255,255,0.06);
    border-radius: 12px;
    padding: 10px 16px;
}

/* SCROLL */

::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-thumb {
    background: #1f7a52;
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)

# ============================================================================
# HEADER
# ============================================================================

st.markdown("""
<div class="header-box">
    <h1>🌱 Classificador Inteligente de Fertilidade do Solo</h1>
    <p>Sistema avançado de análise agrícola • SiBCS • Embrapa</p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:

    st.markdown("## 🌾 Sistema Agrícola")

    st.markdown("""
    ✅ Classificação Inteligente  
    ✅ Correção de Solo  
    ✅ Adubação NPK  
    ✅ Relatórios Técnicos  
    ✅ Conversão para Vasos  
    """)

    st.markdown("---")

    if modelo is not None:
        st.success("🤖 IA carregada")
    else:
        st.warning("⚠️ IA local não encontrada")

    st.markdown("---")

    st.caption("Versão 10.0")

# ============================================================================
# SESSION STATE
# ============================================================================

if "dados_basicos" not in st.session_state:
    st.session_state.dados_basicos = {}

if "dados_calculados" not in st.session_state:
    st.session_state.dados_calculados = {}

if "classificacao_realizada" not in st.session_state:
    st.session_state.classificacao_realizada = False

# ============================================================================
# CULTURAS
# ============================================================================

necessidades_culturas = {
    "Soja": {"v_desejado": 60, "p_min": 15, "k_min": 0.35, "p_rec": 80, "k_rec": 60, "n_base": 20},
    "Milho": {"v_desejado": 65, "p_min": 20, "k_min": 0.40, "p_rec": 100, "k_rec": 80, "n_base": 120},
    "Feijão": {"v_desejado": 65, "p_min": 20, "k_min": 0.35, "p_rec": 80, "k_rec": 60, "n_base": 40},
    "Café": {"v_desejado": 70, "p_min": 25, "k_min": 0.40, "p_rec": 120, "k_rec": 100, "n_base": 180},
    "Pastagem": {"v_desejado": 50, "p_min": 10, "k_min": 0.25, "p_rec": 60, "k_rec": 50, "n_base": 80},
    "Algodão": {"v_desejado": 70, "p_min": 25, "k_min": 0.45, "p_rec": 120, "k_rec": 100, "n_base": 140},
    "Tomate": {"v_desejado": 80, "p_min": 30, "k_min": 0.50, "p_rec": 150, "k_rec": 120, "n_base": 150},
    "Arroz": {"v_desejado": 50, "p_min": 10, "k_min": 0.25, "p_rec": 60, "k_rec": 50, "n_base": 85}
}

# ============================================================================
# TABS
# ============================================================================

tabs = st.tabs([
    "📝 Cadastro",
    "📊 Dados do Solo",
    "🌱 Classificação",
    "🧪 Adubação Vaso",
    "📈 Relatório",
    "🎯 Recomendações"
])

# ============================================================================
# ABA CADASTRO
# ============================================================================

with tabs[0]:

    st.subheader("📝 Cadastro do Produtor (Opcional)")

    col1, col2 = st.columns(2)

    with col1:
        nome = st.text_input("Nome")
        fazenda = st.text_input("Fazenda")
        cidade = st.text_input("Cidade")

    with col2:
        estado = st.text_input("Estado")
        cep = st.text_input("CEP")

    st.info("ℹ️ O preenchimento é opcional e não impede continuar.")

    st.session_state.cadastro = {
        "nome": nome,
        "fazenda": fazenda,
        "cidade": cidade,
        "estado": estado,
        "cep": cep
    }

# ============================================================================
# ABA DADOS SOLO
# ============================================================================

with tabs[1]:

    st.subheader("📊 Dados do Solo")

    col1, col2, col3 = st.columns(3)

    with col1:
        nitrogen = st.number_input("Nitrogênio (mg/dm³)", 0.0, 1000.0, 0.0)
        phosphorus = st.number_input("Fósforo (mg/dm³)", 0.0, 1000.0, 0.0)
        potassium = st.number_input("Potássio (cmolc/dm³)", 0.0, 100.0, 0.0)

    with col2:
        organic_matter = st.number_input("Matéria Orgânica (g/kg)", 0.0, 200.0, 0.0)
        bulk_density = st.number_input("Densidade do Solo", 0.0, 5.0, 1.2)
        particle_density = st.number_input("Densidade Partícula", 0.0, 5.0, 2.65)

    with col3:
        sand = st.number_input("Areia (g/kg)", 0.0, 1000.0, 0.0)
        silt = st.number_input("Silte (g/kg)", 0.0, 1000.0, 0.0)
        clay = st.number_input("Argila (g/kg)", 0.0, 1000.0, 0.0)

    if st.button("💾 Salvar Dados Básicos"):

        st.session_state.dados_basicos = {
            "nitrogen": nitrogen,
            "phosphorus": phosphorus,
            "potassium": potassium,
            "organic_matter": organic_matter,
            "bulk_density": bulk_density,
            "particle_density": particle_density,
            "sand": sand,
            "silt": silt,
            "clay": clay
        }

        st.success("✅ Dados básicos salvos!")

# ============================================================================
# ABA CLASSIFICAÇÃO
# ============================================================================

with tabs[2]:

    st.subheader("🌱 Classificação da Fertilidade")

    if not st.session_state.dados_basicos:
        st.warning("⚠️ Salve os dados do solo primeiro.")
    else:

        col1, col2 = st.columns(2)

        with col1:
            aluminum = st.number_input("Alumínio (cmolc/dm³)", 0.0, 100.0, 0.0)
            h_al = st.number_input("H + Al", 0.0, 100.0, 0.0)

        with col2:
            calcium = st.number_input("Cálcio", 0.0, 100.0, 0.0)
            magnesium = st.number_input("Magnésio", 0.0, 100.0, 0.0)

        cultura = st.selectbox(
            "🌾 Cultura",
            list(necessidades_culturas.keys())
        )

        if st.button("🔬 Realizar Classificação"):

            dados = st.session_state.dados_basicos.copy()

            dados["aluminum"] = aluminum
            dados["h_al"] = h_al
            dados["calcium"] = calcium
            dados["magnesium"] = magnesium
            dados["cultura"] = cultura

            dados["ph"] = calcular_ph(dados)

            sb = calcium + magnesium + dados["potassium"]

            ctc = sb + h_al

            v_percent = (sb / ctc) * 100 if ctc > 0 else 0

            dados["v_percent"] = v_percent

            predicao, explicacao = fazer_predicao_ia(dados)

            st.session_state.dados_calculados = dados
            st.session_state.classificacao_realizada = True
            st.session_state.predicao = predicao
            st.session_state.explicacao = explicacao
            st.session_state.ctc = ctc
            st.session_state.sb = sb
            st.session_state.v_percent = v_percent
            st.session_state.cultura = cultura

            colm1, colm2, colm3 = st.columns(3)

            colm1.metric("pH", f"{dados['ph']:.1f}")
            colm2.metric("CTC", f"{ctc:.2f}")
            colm3.metric("V%", f"{v_percent:.1f}%")

            st.success(f"🤖 {predicao}")
            st.info(explicacao)

# ============================================================================
# ABA ADUBAÇÃO VASO
# ============================================================================

with tabs[3]:

    st.subheader("🧪 Adubação para Vasos")

    if not st.session_state.classificacao_realizada:

        st.warning("⚠️ Realize a classificação primeiro.")

    else:

        altura = st.number_input("Altura do vaso (cm)", 5.0, 100.0, 20.0)
        diametro = st.number_input("Diâmetro do vaso (cm)", 5.0, 100.0, 10.0)

        area = math.pi * ((diametro / 2) ** 2) / 10000

        cultura = st.session_state.cultura

        dados_cultura = necessidades_culturas[cultura]

        n_vaso = calcular_adubacao_vaso(area, dados_cultura["n_base"])
        p_vaso = calcular_adubacao_vaso(area, dados_cultura["p_rec"])
        k_vaso = calcular_adubacao_vaso(area, dados_cultura["k_rec"])

        col1, col2, col3 = st.columns(3)

        col1.metric("N", f"{n_vaso:.2f} g")
        col2.metric("P₂O₅", f"{p_vaso:.2f} g")
        col3.metric("K₂O", f"{k_vaso:.2f} g")

# ============================================================================
# ABA RELATÓRIO
# ============================================================================

with tabs[4]:

    st.subheader("📈 Relatório Completo")

    if not st.session_state.classificacao_realizada:

        st.warning("⚠️ Realize a classificação primeiro.")

    else:

        dados = st.session_state.dados_calculados

        cadastro = st.session_state.get("cadastro", {})

        relatorio = pd.DataFrame({

            "Informação": [

                "Nome",
                "Fazenda",
                "Cidade",
                "Estado",
                "CEP",
                "Cultura",
                "pH",
                "Nitrogênio",
                "Fósforo",
                "Potássio",
                "Cálcio",
                "Magnésio",
                "Alumínio",
                "H + Al",
                "CTC",
                "V%",
                "Matéria Orgânica",
                "Areia",
                "Silte",
                "Argila",
                "Classificação IA"

            ],

            "Valor": [

                cadastro.get("nome", ""),
                cadastro.get("fazenda", ""),
                cadastro.get("cidade", ""),
                cadastro.get("estado", ""),
                cadastro.get("cep", ""),
                st.session_state.cultura,
                dados["ph"],
                dados["nitrogen"],
                dados["phosphorus"],
                dados["potassium"],
                dados["calcium"],
                dados["magnesium"],
                dados["aluminum"],
                dados["h_al"],
                st.session_state.ctc,
                st.session_state.v_percent,
                dados["organic_matter"],
                dados["sand"],
                dados["silt"],
                dados["clay"],
                st.session_state.predicao

            ]

        })

        st.dataframe(relatorio, use_container_width=True, hide_index=True)

        csv = relatorio.to_csv(index=False).encode("utf-8")

        st.download_button(
            "📥 Baixar Relatório CSV",
            csv,
            "relatorio_solo.csv",
            "text/csv"
        )

# ============================================================================
# ABA RECOMENDAÇÕES
# ============================================================================

with tabs[5]:

    st.subheader("🎯 Recomendações Técnicas")

    if not st.session_state.classificacao_realizada:

        st.warning("⚠️ Realize a classificação primeiro.")

    else:

        cultura = st.session_state.cultura

        dados_cultura = necessidades_culturas[cultura]

        dados = st.session_state.dados_calculados

        v_atual = st.session_state.v_percent
        ctc = st.session_state.ctc

        calagem = calcular_calagem(
            v_atual,
            dados_cultura["v_desejado"],
            ctc
        )

        gessagem = calcular_gessagem(
            calagem,
            dados["clay"]
        )

        st.markdown("### 🪨 Correção do Solo")

        col1, col2 = st.columns(2)

        col1.metric("Calagem", f"{calagem:.2f} t/ha")
        col2.metric("Gessagem", f"{gessagem:.2f} t/ha")

        st.markdown("---")

        st.markdown("### 🌱 Adubação Recomendada")

        coln1, coln2, coln3 = st.columns(3)

        coln1.metric("Nitrogênio", f"{dados_cultura['n_base']} kg/ha")
        coln2.metric("Fósforo", f"{dados_cultura['p_rec']} kg/ha")
        coln3.metric("Potássio", f"{dados_cultura['k_rec']} kg/ha")

        resumo = pd.DataFrame({

            "Recomendação": [
                "Calagem",
                "Gessagem",
                "Nitrogênio",
                "Fósforo",
                "Potássio"
            ],

            "Dose": [
                f"{calagem:.2f} t/ha",
                f"{gessagem:.2f} t/ha",
                f"{dados_cultura['n_base']} kg/ha",
                f"{dados_cultura['p_rec']} kg/ha",
                f"{dados_cultura['k_rec']} kg/ha"
            ]

        })

        st.dataframe(resumo, use_container_width=True, hide_index=True)

# ============================================================================
# RODAPÉ
# ============================================================================

st.markdown("---")

st.caption(
    "© 2026 • Classificador Inteligente de Fertilidade do Solo • Embrapa • Versão 10.0"
)
