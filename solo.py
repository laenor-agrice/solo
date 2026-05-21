# =============================================================================
# APP: CLASSIFICADOR INTELIGENTE DE FERTILIDADE DO SOLO + IA AGRONÔMICA
# =============================================================================
# BLOCO 01 - IMPORTAÇÕES
# =============================================================================

import streamlit as st
import pandas as pd
import math

# =============================================================================
# BLOCO 02 - CONFIGURAÇÃO DA PÁGINA
# =============================================================================

st.set_page_config(
    page_title="Classificador Inteligente de Solo",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# BLOCO 03 - CSS / DESIGN MODERNO
# ALTERAR APENAS ESTE BLOCO PARA MUDAR VISUAL
# =============================================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

html, body, [class*="css"]{
    font-family:'Inter',sans-serif;
}

.stApp{
    background:linear-gradient(180deg,#07110b 0%,#0d1f14 100%);
    color:white;
}

.block-container{
    max-width:100% !important;
    padding-top:1rem;
    padding-bottom:2rem;
    padding-left:2rem;
    padding-right:2rem;
}

h1,h2,h3,h4,h5{
    color:#9AF5B0 !important;
    font-weight:800 !important;
}

p,label,span,div{
    color:#F1FFF5 !important;
}

.stTextInput input,
.stNumberInput input,
textarea{
    background:#102117 !important;
    border:1px solid #2f6b46 !important;
    border-radius:14px !important;
    color:white !important;
}

div[data-baseweb="select"] > div{
    background:#102117 !important;
    border:1px solid #2f6b46 !important;
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
    transition:0.3s;
}

.stButton > button:hover{
    transform:scale(1.02);
}

[data-testid="stMetric"]{
    background:rgba(255,255,255,0.04);
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
# BLOCO 04 - FUNÇÕES PRINCIPAIS
# ALTERAR CÁLCULOS AQUI
# =============================================================================

def calcular_ph(dados):

    try:

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

    except:
        return 5.5


def calcular_calagem(v_atual,v_desejado,ctc,prnt=80):

    if v_atual >= v_desejado:
        return 0

    nc = ((v_desejado - v_atual) * ctc) / 100

    nc = nc * (100/prnt)

    return round(nc,2)


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
# BLOCO 05 - IA AGRONÔMICA
# ALTERAR RESPOSTAS DA IA AQUI
# =============================================================================

def assistente_agronomico(pergunta,dados):

    pergunta = pergunta.lower()

    ph = dados.get("ph",5.5)
    p = dados.get("phosphorus",0)
    k = dados.get("potassium",0)
    cultura = dados.get("cultura","Não definida")

    if "ph" in pergunta or "acidez" in pergunta:

        if ph < 5.5:
            return f"""
🔴 Seu solo apresenta acidez elevada.

✔ pH atual: {ph}
✔ Cultura: {cultura}

RECOMENDAÇÕES:
- Realizar calagem
- Aplicar calcário 30-60 dias antes do plantio
- Incorporar na camada de 0-20 cm

A acidez reduz:
- disponibilidade de fósforo
- crescimento radicular
- produtividade
"""

        return f"""
🟢 O pH do solo está adequado.

✔ pH atual: {ph}
✔ Cultura: {cultura}
"""

    elif "fosforo" in pergunta or "fósforo" in pergunta:

        return f"""
🪨 O fósforo é essencial para:
- raízes
- energia da planta
- desenvolvimento inicial

✔ Aplicar preferencialmente:
- no sulco
- incorporado

✔ Fontes:
- MAP
- Superfosfato simples
- Superfosfato triplo
"""

    elif "potassio" in pergunta or "potássio" in pergunta:

        return f"""
🍌 O potássio auxilia:
- resistência da planta
- enchimento de grãos
- tolerância hídrica

✔ Aplicação:
- parcelada
- cobertura

✔ Fontes:
- KCl
- Sulfato de Potássio
"""

    elif "nitrogenio" in pergunta or "nitrogênio" in pergunta:

        return """
⚛️ O nitrogênio é responsável por:
- crescimento vegetativo
- produção de folhas
- vigor da cultura

✔ Aplicação recomendada:
- parcelada
- evitar perdas por volatilização

✔ Fontes:
- ureia
- sulfato de amônio
"""

    else:

        return """
🤖 Perguntas aceitas:

- pH
- acidez
- fósforo
- potássio
- nitrogênio
- matéria orgânica
- adubação
- calagem
- gessagem

A IA responde apenas dúvidas relacionadas ao sistema e fertilidade do solo.
"""

# =============================================================================
# BLOCO 06 - CULTURAS EMBRAPA
# ALTERAR CULTURAS AQUI
# =============================================================================

necessidades_culturas = {

    "Milho Grão":{
        "v_desejado":65,
        "p_min":20,
        "k_min":0.35,
        "n":120,
        "p":100,
        "k":80
    },

    "Milho Semente":{
        "v_desejado":70,
        "p_min":25,
        "k_min":0.40,
        "n":140,
        "p":120,
        "k":100
    },

    "Milheto":{
        "v_desejado":50,
        "p_min":12,
        "k_min":0.25,
        "n":70,
        "p":60,
        "k":50
    },

    "Sorgo":{
        "v_desejado":55,
        "p_min":15,
        "k_min":0.30,
        "n":90,
        "p":70,
        "k":60
    },

    "Café":{
        "v_desejado":70,
        "p_min":25,
        "k_min":0.40,
        "n":180,
        "p":120,
        "k":100
    },

    "Cana-de-açúcar":{
        "v_desejado":60,
        "p_min":15,
        "k_min":0.35,
        "n":100,
        "p":90,
        "k":120
    },

    "Arroz":{
        "v_desejado":50,
        "p_min":10,
        "k_min":0.25,
        "n":85,
        "p":60,
        "k":50
    },

    "Feijão":{
        "v_desejado":60,
        "p_min":18,
        "k_min":0.30,
        "n":60,
        "p":90,
        "k":70
    },

    "Trigo":{
        "v_desejado":65,
        "p_min":20,
        "k_min":0.35,
        "n":110,
        "p":80,
        "k":60
    },

    "Soja":{
        "v_desejado":60,
        "p_min":15,
        "k_min":0.30,
        "n":20,
        "p":80,
        "k":60
    },

    "Tomate":{
        "v_desejado":80,
        "p_min":30,
        "k_min":0.50,
        "n":150,
        "p":150,
        "k":120
    }

}

# =============================================================================
# BLOCO 07 - SESSION STATE
# =============================================================================

if "dados" not in st.session_state:
    st.session_state.dados = {}

# =============================================================================
# BLOCO 08 - HEADER
# =============================================================================

st.markdown("""
<div class='card'>
<h1>🌱 Classificador Inteligente de Fertilidade do Solo</h1>
<p>Sistema Agronômico Inteligente baseado em recomendações técnicas.</p>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# BLOCO 09 - TABS
# =============================================================================

abas = st.tabs([
    "📋 Cadastro",
    "🌱 Dados do Solo",
    "🧠 Classificação",
    "🧪 Adubação",
    "📈 Relatório",
    "🤖 Assistente IA"
])

# =============================================================================
# ABA 01 - CADASTRO
# =============================================================================

with abas[0]:

    st.markdown("## 📋 Cadastro")

    c1,c2 = st.columns(2)

    with c1:

        nome = st.text_input("Nome")
        fazenda = st.text_input("Fazenda")
        cidade = st.text_input("Cidade")

    with c2:

        estado = st.text_input("Estado")
        cep = st.text_input("CEP")

    st.info("Cadastro opcional.")

# =============================================================================
# ABA 02 - DADOS SOLO
# =============================================================================

with abas[1]:

    st.markdown("## 🌱 Dados do Solo")

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
        list(necessidades_culturas.keys())
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

        st.success("Dados salvos com sucesso.")

# =============================================================================
# ABA 03 - CLASSIFICAÇÃO
# =============================================================================

with abas[2]:

    st.markdown("## 🧠 Classificação")

    if st.session_state.dados:

        dados = st.session_state.dados

        sb = (
            dados["calcium"] +
            dados["magnesium"] +
            dados["potassium"]
        )

        ctc = sb + dados["h_al"]

        v = (sb / ctc) * 100 if ctc > 0 else 0

        c1,c2,c3 = st.columns(3)

        c1.metric("pH",dados["ph"])
        c2.metric("CTC",round(ctc,2))
        c3.metric("V%",round(v,1))

        if dados["ph"] < 5.5:
            st.error("🔴 Solo ácido.")

        elif v < 50:
            st.warning("🟠 Baixa saturação por bases.")

        else:
            st.success("🟢 Solo com fertilidade adequada.")

# =============================================================================
# ABA 04 - ADUBAÇÃO
# =============================================================================

with abas[3]:

    st.markdown("## 🧪 Recomendação de Adubação")

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

        c1,c2 = st.columns(2)

        with c1:

            st.metric("Calcário",f"{calagem} t/ha")
            st.metric("Gesso",f"{gesso} t/ha")

        with c2:

            st.metric("Nitrogênio",f"{info['n']} kg/ha")
            st.metric("Fósforo",f"{info['p']} kg/ha")
            st.metric("Potássio",f"{info['k']} kg/ha")

        st.markdown("---")

        st.markdown(f"""
### ⚛️ Nitrogênio (N)

✔ Recomendação:
{info['n']} kg/ha

✔ Aplicação:
Parcelado em 3 vezes:

- 30% no plantio
- 30% aos 30 dias
- 40% aos 60 dias

---

### 🪨 Fósforo (P₂O₅)

✔ Recomendação:
{info['p']} kg/ha

✔ Aplicação:
- Sulco de plantio
- Incorporado ao solo

---

### 🍌 Potássio (K₂O)

✔ Recomendação:
{info['k']} kg/ha

✔ Aplicação:
- 50% plantio
- 50% cobertura
""")

# =============================================================================
# ABA 05 - RELATÓRIO
# =============================================================================

with abas[4]:

    st.markdown("## 📈 Relatório Técnico")

    if st.session_state.dados:

        dados = st.session_state.dados

        relatorio = pd.DataFrame({

            "Parâmetro":[
                "pH",
                "Nitrogênio",
                "Fósforo",
                "Potássio",
                "Cálcio",
                "Magnésio",
                "Alumínio",
                "H + Al",
                "Matéria Orgânica",
                "Argila",
                "Cultura"
            ],

            "Valor":[
                dados["ph"],
                dados["nitrogen"],
                dados["phosphorus"],
                dados["potassium"],
                dados["calcium"],
                dados["magnesium"],
                dados["aluminum"],
                dados["h_al"],
                dados["organic_matter"],
                dados["clay"],
                dados["cultura"]
            ]
        })

        st.dataframe(
            relatorio,
            use_container_width=True,
            hide_index=True
        )

# =============================================================================
# ABA 06 - IA AGRONÔMICA
# =============================================================================

with abas[5]:

    st.markdown("## 🤖 Assistente IA Agronômico")

    pergunta = st.text_area(
        "Digite sua dúvida"
    )

    st.caption("""
⚠️ OBSERVAÇÃO:
A IA responde apenas dúvidas relacionadas:
- fertilidade do solo
- adubação
- calagem
- gessagem
- nutrientes
- funcionamento do sistema
""")

    if st.button("🚀 Perguntar para IA"):

        resposta = assistente_agronomico(
            pergunta,
            st.session_state.dados
        )

        st.success(resposta)

# =============================================================================
# BLOCO FINAL - RODAPÉ
# =============================================================================

st.markdown("---")

st.caption("""
© 2026 - Sistema Inteligente de Fertilidade do Solo
Baseado em recomendações agronômicas técnicas.
""")
