# =============================================================================
# APP: AGROSOLO IA
# =============================================================================

import streamlit as st
import pandas as pd
import math

# =============================================================================
# BLOCO - PROTEÇÃO PLOTLY
# =============================================================================

try:
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except:
    PLOTLY_AVAILABLE = False

# =============================================================================
# CONFIGURAÇÃO DA PÁGINA
# =============================================================================

st.set_page_config(
    page_title="AgroSolo IA",
    page_icon="🌿",
    layout="wide"
)

# =============================================================================
# CSS MODERNO
# =============================================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;700;800&display=swap');

html, body, [class*="css"]{
    font-family:'Inter',sans-serif;
}

.stApp{
    background:linear-gradient(180deg,#06110c 0%,#102419 100%);
}

.block-container{
    max-width:100% !important;
    padding-top:1rem;
    padding-left:2rem;
    padding-right:2rem;
}

h1,h2,h3,h4,h5{
    color:#9DFFB0 !important;
    font-weight:800 !important;
}

p,label,span,div{
    color:#F1FFF5 !important;
}

.stTextInput input,
.stNumberInput input,
textarea{
    background:#102117 !important;
    border:1px solid #3f8f5d !important;
    border-radius:14px !important;
    color:white !important;
}

div[data-baseweb="select"] > div{
    background:#102117 !important;
    border:1px solid #3f8f5d !important;
    border-radius:14px !important;
}

div[data-baseweb="select"] *{
    color:white !important;
}

.stButton > button{
    width:100%;
    border:none;
    border-radius:14px;
    padding:0.8rem;
    background:linear-gradient(90deg,#2f6b46,#46a36a);
    color:white;
    font-weight:700;
}

[data-testid="stMetric"]{
    background:rgba(255,255,255,0.05);
    border-radius:18px;
    padding:1rem;
    border:1px solid rgba(255,255,255,0.08);
}

.card{
    background:rgba(255,255,255,0.04);
    border-radius:20px;
    padding:1.5rem;
    border:1px solid rgba(255,255,255,0.08);
    margin-bottom:1rem;
}

button[data-baseweb="tab"]{
    color:white !important;
    font-weight:700 !important;
}

button[data-baseweb="tab"][aria-selected="true"]{
    background:#2f6b46 !important;
    border-radius:12px;
}

section[data-testid="stSidebar"]{
    background:#08130d;
}

</style>
""", unsafe_allow_html=True)

# =============================================================================
# CULTURAS EMBRAPA
# =============================================================================

necessidades_culturas = {

    "Arroz":{
        "v_desejado":50,
        "n":85,
        "p":60,
        "k":50,
        "plantio":"Outubro a Dezembro"
    },

    "Café":{
        "v_desejado":70,
        "n":180,
        "p":120,
        "k":100,
        "plantio":"Outubro a Março"
    },

    "Cana-de-açúcar":{
        "v_desejado":60,
        "n":100,
        "p":90,
        "k":120,
        "plantio":"Janeiro a Março"
    },

    "Feijão":{
        "v_desejado":60,
        "n":60,
        "p":90,
        "k":70,
        "plantio":"Setembro a Novembro"
    },

    "Milheto":{
        "v_desejado":50,
        "n":70,
        "p":60,
        "k":50,
        "plantio":"Outubro a Janeiro"
    },

    "Milho Grão":{
        "v_desejado":65,
        "n":120,
        "p":100,
        "k":80,
        "plantio":"Setembro a Dezembro"
    },

    "Milho Semente":{
        "v_desejado":70,
        "n":140,
        "p":120,
        "k":100,
        "plantio":"Setembro a Novembro"
    },

    "Soja":{
        "v_desejado":60,
        "n":20,
        "p":80,
        "k":60,
        "plantio":"Outubro a Dezembro"
    },

    "Sorgo":{
        "v_desejado":55,
        "n":90,
        "p":70,
        "k":60,
        "plantio":"Outubro a Janeiro"
    },

    "Tomate":{
        "v_desejado":80,
        "n":150,
        "p":150,
        "k":120,
        "plantio":"Ano todo"
    },

    "Trigo":{
        "v_desejado":65,
        "n":110,
        "p":80,
        "k":60,
        "plantio":"Abril a Junho"
    }

}

# =============================================================================
# FUNÇÕES
# =============================================================================

def calcular_ph(dados):

    fator_acidez = (
        dados.get("aluminum",0) * 0.25 +
        dados.get("h_al",0) * 0.08
    )

    fator_base = (
        dados.get("calcium",0) * 0.22 +
        dados.get("magnesium",0) * 0.18 +
        dados.get("potassium",0) * 0.45
    )

    om = dados.get("organic_matter",0) / 100

    ph = 5.5 + fator_base - fator_acidez - (om * 0.2)

    return round(max(4.0,min(7.5,ph)),1)

def calcular_calagem(v_atual,v_desejado,ctc):

    if v_atual >= v_desejado:
        return 0

    nc = ((v_desejado - v_atual) * ctc) / 100

    return round(nc * 1.25,2)

def calcular_gessagem(calagem,argila):

    if argila >= 350:
        return round(calagem * 0.5,2)

    elif argila >= 200:
        return round(calagem * 0.3,2)

    return 0

def calcular_adubacao_vaso(area,recomendacao):

    kg_m2 = recomendacao / 10000

    g = kg_m2 * area * 1000

    return round(g,2)

# =============================================================================
# IA AGRONÔMICA
# =============================================================================

def assistente_agronomico(pergunta,dados):

    pergunta = pergunta.lower()

    if "calagem" in pergunta:

        return """
🪨 A calagem corrige a acidez do solo e melhora a disponibilidade de nutrientes.
"""

    elif "gessagem" in pergunta:

        return """
💎 A gessagem melhora o perfil do solo e reduz alumínio em profundidade.
"""

    elif "fertilidade" in pergunta:

        return """
🌿 Fertilidade adequada aumenta produtividade e eficiência da adubação.
"""

    elif "matéria" in pergunta:

        return """
🍂 Aumente matéria orgânica usando:
- palhada
- esterco
- plantas de cobertura
"""

    elif "compactação" in pergunta:

        return """
🚜 Evite compactação:
- reduzir tráfego
- evitar solo úmido
- usar cobertura vegetal
"""

    elif "erosão" in pergunta:

        return """
🌧 Evite erosão:
- curvas de nível
- plantio direto
- cobertura do solo
"""

    elif "nitrogênio" in pergunta:

        return """
⚛️ Nitrogênio deve ser parcelado para reduzir perdas.
"""

    else:

        return """
🤖 Perguntas aceitas:
- calagem
- gessagem
- fertilidade
- matéria orgânica
- compactação
- erosão
- nitrogênio
"""

# =============================================================================
# SESSION STATE
# =============================================================================

if "dados" not in st.session_state:
    st.session_state.dados = {}

# =============================================================================
# HEADER
# =============================================================================

st.markdown("""
<div class='card'>
<h1>🌿 AgroSolo IA</h1>
<p>Classificador Inteligente de Fertilidade do Solo</p>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# TABS
# =============================================================================

abas = st.tabs([
    "🪪 Cadastro",
    "🌱 Solo",
    "🧠 Fertilidade",
    "🧪 Adubação",
    "📊 Relatório",
    "🤖 IA Agronômica"
])

# =============================================================================
# ABA CADASTRO
# =============================================================================

with abas[0]:

    st.subheader("🪪 Cadastro")

    c1,c2 = st.columns(2)

    with c1:
        nome = st.text_input("Nome")
        fazenda = st.text_input("Fazenda")
        cidade = st.text_input("Cidade")

    with c2:
        estado = st.text_input("Estado")
        cep = st.text_input("CEP")

# =============================================================================
# ABA SOLO
# =============================================================================

with abas[1]:

    st.subheader("🌱 Dados do Solo")

    c1,c2,c3 = st.columns(3)

    with c1:
        nitrogen = st.number_input("Nitrogênio",0.0)
        phosphorus = st.number_input("Fósforo",0.0)
        potassium = st.number_input("Potássio",0.0)

    with c2:
        calcium = st.number_input("Cálcio",0.0)
        magnesium = st.number_input("Magnésio",0.0)
        aluminum = st.number_input("Alumínio",0.0)

    with c3:
        h_al = st.number_input("H + Al",0.0)
        organic_matter = st.number_input("Matéria Orgânica",0.0)
        clay = st.number_input("Argila",0.0)

    cultura = st.selectbox(
        "🌾 Cultura",
        sorted(list(necessidades_culturas.keys()))
    )

    if st.button("💾 Salvar Dados"):

        dados = {

            "nitrogen":nitrogen,
            "phosphorus":phosphorus,
            "potassium":potassium,
            "calcium":calcium,
            "magnesium":magnesium,
            "aluminum":aluminum,
            "h_al":h_al,
            "organic_matter":organic_matter,
            "clay":clay,
            "cultura":cultura
        }

        dados["ph"] = calcular_ph(dados)

        st.session_state.dados = dados

        st.success("Dados salvos.")

# =============================================================================
# ABA FERTILIDADE
# =============================================================================

with abas[2]:

    st.subheader("🧠 Classificação Inteligente")

    if st.session_state.dados:

        dados = st.session_state.dados

        sb = (
            dados["calcium"] +
            dados["magnesium"] +
            dados["potassium"]
        )

        ctc = sb + dados["h_al"]

        v = (sb / ctc) * 100 if ctc > 0 else 0

        ph = dados["ph"]

        c1,c2,c3 = st.columns(3)

        c1.metric("🧪 pH",ph)
        c2.metric("🌿 V%",round(v,1))
        c3.metric("🪨 CTC",round(ctc,2))

        if ph < 5.5 or v < 50:

            st.error("🔴 BAIXA FERTILIDADE")

            st.info("""
🤖 IA:
O solo apresenta limitações químicas.
Recomenda-se correção com calagem.
""")

        else:

            st.success("🟢 BOA FERTILIDADE")

        if PLOTLY_AVAILABLE:

            grafico = pd.DataFrame({
                "Indicador":["pH","V%","MO"],
                "Valor":[ph,v,dados["organic_matter"]]
            })

            fig = px.bar(
                grafico,
                x="Indicador",
                y="Valor",
                title="Indicadores de Fertilidade"
            )

            st.plotly_chart(fig,use_container_width=True)

        else:

            st.warning("⚠️ Plotly não instalado.")

            st.bar_chart({
                "Valor":[ph,v,dados["organic_matter"]]
            })

# =============================================================================
# ABA ADUBAÇÃO
# =============================================================================

with abas[3]:

    st.subheader("🧪 Adubação")

    if st.session_state.dados:

        dados = st.session_state.dados

        cultura = dados["cultura"]

        info = necessidades_culturas[cultura]

        sb = (
            dados["calcium"] +
            dados["magnesium"] +
            dados["potassium"]
        )

        ctc = sb + dados["h_al"]

        v = (sb / ctc) * 100 if ctc > 0 else 0

        calagem = calcular_calagem(
            v,
            info["v_desejado"],
            ctc
        )

        gesso = calcular_gessagem(
            calagem,
            dados["clay"]
        )

        st.metric("🪨 Calcário",f"{calagem} t/ha")
        st.metric("💎 Gesso",f"{gesso} t/ha")

        st.markdown(f"""
### ⚛️ Nitrogênio
✔ {info['n']} kg/ha

Aplicação:
- 30% plantio
- 30% aos 30 dias
- 40% aos 60 dias

---

### 🪨 Fósforo
✔ {info['p']} kg/ha

Aplicação:
- sulco
- incorporado

---

### 🍌 Potássio
✔ {info['k']} kg/ha

Aplicação:
- 50% plantio
- 50% cobertura
""")

        st.markdown("---")

        st.subheader("🧫 Adubação para Vaso")

        c1,c2 = st.columns(2)

        with c1:
            altura = st.number_input("Altura do vaso (cm)",5.0)

        with c2:
            raio = st.number_input("Raio do vaso (cm)",5.0)

        area = math.pi * ((raio ** 2) / 10000)

        n_vaso = calcular_adubacao_vaso(area,info["n"])
        p_vaso = calcular_adubacao_vaso(area,info["p"])
        k_vaso = calcular_adubacao_vaso(area,info["k"])

        st.success(f"Nitrogênio: {n_vaso:.2f} g")
        st.success(f"Fósforo: {p_vaso:.2f} g")
        st.success(f"Potássio: {k_vaso:.2f} g")

# =============================================================================
# ABA RELATÓRIO
# =============================================================================

with abas[4]:

    st.subheader("📊 Relatório")

    if st.session_state.dados:

        dados = st.session_state.dados

        cultura = dados["cultura"]

        plantio = necessidades_culturas[cultura]["plantio"]

        relatorio = pd.DataFrame({

            "Parâmetro":[
                "pH",
                "Nitrogênio",
                "Fósforo",
                "Potássio",
                "Cálcio",
                "Magnésio",
                "Alumínio",
                "Matéria Orgânica",
                "Argila",
                "Cultura",
                "Plantio"
            ],

            "Valor":[
                dados["ph"],
                dados["nitrogen"],
                dados["phosphorus"],
                dados["potassium"],
                dados["calcium"],
                dados["magnesium"],
                dados["aluminum"],
                dados["organic_matter"],
                dados["clay"],
                cultura,
                plantio
            ]
        })

        st.dataframe(
            relatorio,
            use_container_width=True,
            hide_index=True
        )

# =============================================================================
# ABA IA
# =============================================================================

with abas[5]:

    st.subheader("🤖 IA Agronômica")

    pergunta = st.text_area(
        "Digite sua dúvida"
    )

    st.caption("""
⚠️ IA focada apenas em:
- solo
- fertilidade
- adubação
- manejo
- nutrientes
""")

    if st.button("🚀 Perguntar"):

        resposta = assistente_agronomico(
            pergunta,
            st.session_state.dados
        )

        st.success(resposta)

# =============================================================================
# RODAPÉ
# =============================================================================

st.markdown("---")

st.caption("""
© 2026 - AgroSolo IA
Sistema Inteligente de Fertilidade do Solo
""")
