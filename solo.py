# =============================================================================
# 🌿 AGROSOLO 
# Sistema Inteligente de Fertilidade do Solo
# Desenvolvido com Streamlit
# =====================# =============================================================================
# 🌿 IA SOLOS
# Sistema Inteligente de Fertilidade do Solo
# =============================================================================

# =============================================================================
# 📦 IMPORTAÇÕES
# =============================================================================

import streamlit as st
import pandas as pd
import math

# =============================================================================
# 📊 PLOTLY
# =============================================================================

try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except:
    PLOTLY_AVAILABLE = False

# =============================================================================
# 🤖 GEMINI IA
# =============================================================================

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except:
    GEMINI_AVAILABLE = False

# =============================================================================
# ⚙️ CONFIGURAÇÃO
# =============================================================================

st.set_page_config(
    page_title="AgroSolo IA",
    page_icon="🌿",
    layout="wide"
)

# =============================================================================
# 🎨 CSS MODERNO
# =============================================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;700;800&display=swap');

html, body, [class*="css"]{
    font-family:'Inter',sans-serif;
}

.stApp{
    background:linear-gradient(135deg,#081c15 0%,#0d281d 50%,#081c15 100%);
}

.block-container{
    max-width:100% !important;
    padding-top:1rem;
    padding-left:2rem;
    padding-right:2rem;
}

h1,h2,h3,h4,h5{
    color:#b7ffcb !important;
    font-weight:800 !important;
}

p,span,label,div{
    color:white !important;
}

section[data-testid="stSidebar"]{
    background:#07130d;
}

.stTextInput input,
.stNumberInput input,
textarea{
    background:#10251a !important;
    border:1px solid #45b36b !important;
    border-radius:14px !important;
    color:white !important;
}

div[data-baseweb="select"] > div{
    background:#10251a !important;
    border:1px solid #45b36b !important;
    border-radius:14px !important;
}

div[data-baseweb="select"] *{
    color:white !important;
}

.stButton > button{
    background:linear-gradient(90deg,#2f7d54,#49bf74);
    border:none;
    border-radius:14px;
    color:white;
    font-weight:700;
    padding:0.8rem;
    width:100%;
}

[data-testid="stMetric"]{
    background:rgba(255,255,255,0.05);
    border-radius:18px;
    padding:1rem;
    border:1px solid rgba(255,255,255,0.08);
}

.card{
    background:rgba(255,255,255,0.04);
    border-radius:22px;
    padding:1.5rem;
    border:1px solid rgba(255,255,255,0.08);
    margin-bottom:1rem;
}

button[data-baseweb="tab"]{
    color:white !important;
    font-weight:700 !important;
}

button[data-baseweb="tab"][aria-selected="true"]{
    background:#2f7d54 !important;
    border-radius:14px;
}

</style>
""", unsafe_allow_html=True)

# =============================================================================
# 🌾 CULTURAS EMBRAPA
# =============================================================================

necessidades_culturas = {

    "Arroz":{
        "v":50,
        "n":85,
        "p":60,
        "k":50,
        "plantio":"Outubro a Dezembro"
    },

    "Café":{
        "v":70,
        "n":180,
        "p":120,
        "k":100,
        "plantio":"Outubro a Março"
    },

    "Cana-de-açúcar":{
        "v":60,
        "n":100,
        "p":90,
        "k":120,
        "plantio":"Janeiro a Março"
    },

    "Feijão":{
        "v":60,
        "n":60,
        "p":90,
        "k":70,
        "plantio":"Setembro a Novembro"
    },

    "Milheto":{
        "v":50,
        "n":70,
        "p":60,
        "k":50,
        "plantio":"Outubro a Janeiro"
    },

    "Milho Grão":{
        "v":65,
        "n":120,
        "p":100,
        "k":80,
        "plantio":"Setembro a Dezembro"
    },

    "Milho Semente":{
        "v":70,
        "n":140,
        "p":120,
        "k":100,
        "plantio":"Setembro a Novembro"
    },

    "Soja":{
        "v":60,
        "n":20,
        "p":80,
        "k":60,
        "plantio":"Outubro a Dezembro"
    },

    "Sorgo":{
        "v":55,
        "n":90,
        "p":70,
        "k":60,
        "plantio":"Outubro a Janeiro"
    },

    "Tomate":{
        "v":80,
        "n":150,
        "p":150,
        "k":120,
        "plantio":"Ano todo"
    },

    "Trigo":{
        "v":65,
        "n":110,
        "p":80,
        "k":60,
        "plantio":"Abril a Junho"
    }

}

# =============================================================================
# 🧪 FUNÇÕES
# =============================================================================

def calcular_ph(dados):

    acidez = (
        dados["aluminum"] * 0.3 +
        dados["h_al"] * 0.1
    )

    bases = (
        dados["calcium"] * 0.2 +
        dados["magnesium"] * 0.15 +
        dados["potassium"] * 0.5
    )

    ph = 5.5 + bases - acidez

    return round(max(4.0,min(7.5,ph)),1)

# =============================================================================
# 🪨 CALAGEM
# =============================================================================

def calcular_calagem(v_atual,v_desejado,ctc):

    if v_atual >= v_desejado:
        return 0

    nc = ((v_desejado - v_atual) * ctc) / 100

    return round(nc * 1.25,2)

# =============================================================================
# 💎 GESSAGEM
# =============================================================================

def calcular_gessagem(calagem,argila):

    if argila >= 350:
        return round(calagem * 0.5,2)

    elif argila >= 200:
        return round(calagem * 0.3,2)

    return 0

# =============================================================================
# 🧫 ADUBAÇÃO VASO
# =============================================================================

def calcular_adubacao_vaso(area,recomendacao):

    kg_m2 = recomendacao / 10000

    g = kg_m2 * area * 1000

    return round(g,2)

# =============================================================================
# 🤖 IA FERTILIDADE
# =============================================================================

def classificar_fertilidade(ph,v,mo):

    score = 0

    if ph >= 5.5 and ph <= 6.5:
        score += 1

    if v >= 50:
        score += 1

    if mo >= 25:
        score += 1

    if score == 3:
        return "🟢 Alta Fertilidade"

    elif score == 2:
        return "🟡 Média Fertilidade"

    else:
        return "🔴 Baixa Fertilidade"

# =============================================================================
# 🤖 SIDEBAR IA GEMINI
# =============================================================================

modelo_gemini = None

with st.sidebar:

    st.markdown("## 🤖 Assistente IA")

    st.caption("""
Conecte sua API KEY Gemini
para ativar respostas inteligentes.
""")

    api_key = st.text_input(
        "API KEY Gemini",
        type="password"
    )

    if GEMINI_AVAILABLE:

        if api_key:

            try:

                genai.configure(api_key=api_key)

                modelo_gemini = genai.GenerativeModel(
                    "gemini-1.5-flash"
                )

                st.success("✅ IA conectada.")

            except:

                st.error("❌ Erro ao conectar IA.")

        else:

            st.warning("""
⚠️ Insira sua API KEY Gemini.
""")

    else:

        st.error("""
Biblioteca não instalada.

Instale:
pip install google-generativeai
""")

# =============================================================================
# 🤖 FUNÇÃO IA
# =============================================================================

def assistente_agronomico(pergunta,dados):

    if modelo_gemini is None:

        return """
⚠️ IA não conectada.

Passos:

1. Instale:
pip install google-generativeai

2. Gere API:
https://aistudio.google.com/app/apikey

3. Cole API KEY na sidebar.
"""

    contexto = f"""

Você é um engenheiro agrônomo especialista da Embrapa.

Responda apenas sobre:
- fertilidade do solo
- adubação
- manejo
- compactação
- erosão
- nutrientes
- agricultura

Dados do solo:
pH: {dados.get('ph')}
Matéria Orgânica: {dados.get('organic_matter')}
Argila: {dados.get('clay')}
Cultura: {dados.get('cultura')}

Explique de forma técnica e didática.
"""

    resposta = modelo_gemini.generate_content(
        contexto + "\nPergunta: " + pergunta
    )

    return resposta.text

# =============================================================================
# 💾 SESSION STATE
# =============================================================================

if "dados" not in st.session_state:
    st.session_state.dados = {}

# =============================================================================
# 🌿 HEADER
# =============================================================================

st.markdown("""
<div class='card'>
<h1>🌿 AgroSolo IA Premium</h1>
<p>Sistema Inteligente de Fertilidade do Solo</p>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# 📑 ABAS
# =============================================================================

tabs = st.tabs([
    "🪪 Cadastro",
    "🌱 Solo",
    "🧠 Fertilidade",
    "🧪 Adubação",
    "📊 Relatório",
    "🤖 IA Agronômica"
])

# =============================================================================
# 🪪 ABA CADASTRO
# =============================================================================

with tabs[0]:

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
# 🌱 ABA SOLO
# =============================================================================

with tabs[1]:

    st.subheader("🌱 Dados do Solo")

    col1,col2,col3 = st.columns(3)

    with col1:

        nitrogen = st.number_input("Nitrogênio",0.0)
        phosphorus = st.number_input("Fósforo",0.0)
        potassium = st.number_input("Potássio",0.0)

    with col2:

        calcium = st.number_input("Cálcio",0.0)
        magnesium = st.number_input("Magnésio",0.0)
        aluminum = st.number_input("Alumínio",0.0)

    with col3:

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

        st.success("✅ Dados salvos.")

# =============================================================================
# 🧠 ABA FERTILIDADE
# =============================================================================

with tabs[2]:

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

        classificacao = classificar_fertilidade(
            ph,
            v,
            dados["organic_matter"]
        )

        c1,c2,c3 = st.columns(3)

        c1.metric("🧪 pH",ph)
        c2.metric("🌿 V%",round(v,1))
        c3.metric("🍂 Matéria Orgânica",dados["organic_matter"])

        st.markdown("---")

        if "Alta" in classificacao:
            st.success(classificacao)

        elif "Média" in classificacao:
            st.warning(classificacao)

        else:
            st.error(classificacao)

        # =============================================================================
        # 📊 GRÁFICO PIZZA
        # =============================================================================

        st.markdown("## 📊 Visualização da Fertilidade")

        st.caption("""
O gráfico mostra participação relativa
dos principais indicadores do solo.
""")

        grafico_df = pd.DataFrame({

            "Indicador":[
                "pH",
                "V%",
                "Matéria Orgânica"
            ],

            "Valor":[
                ph,
                round(v,1),
                dados["organic_matter"]
            ]
        })

        if PLOTLY_AVAILABLE:

            fig = px.pie(
                grafico_df,
                names="Indicador",
                values="Valor",
                hole=0.45,
                title="Indicadores da Fertilidade"
            )

            fig.update_layout(
                paper_bgcolor="#081c15",
                font_color="white",
                title_font_size=24
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        else:

            st.warning("""
Instale Plotly:

pip install plotly
""")

            st.dataframe(grafico_df)

# =============================================================================
# 🧪 ABA ADUBAÇÃO
# =============================================================================

with tabs[3]:

    st.subheader("🧪 Recomendação de Adubação")

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
            info["v"],
            ctc
        )

        gessagem = calcular_gessagem(
            calagem,
            dados["clay"]
        )

        st.metric("🪨 Calagem",f"{calagem} t/ha")
        st.metric("💎 Gessagem",f"{gessagem} t/ha")

        st.markdown("---")

        st.markdown(f"""
# ⚛️ Nitrogênio

### Recomendação
{info["n"]} kg/ha

### Aplicação
- 30% plantio
- 30% aos 30 dias
- 40% aos 60 dias

### Função
Crescimento vegetativo.

---

# 🪨 Fósforo

### Recomendação
{info["p"]} kg/ha

### Aplicação
- Aplicar no sulco
- Incorporar ao solo

### Função
Formação radicular.

---

# 🍌 Potássio

### Recomendação
{info["k"]} kg/ha

### Aplicação
- 50% plantio
- 50% cobertura

### Função
Resistência e produtividade.
""")

        st.markdown("---")

        # =============================================================================
        # 🧫 ADUBAÇÃO VASO
        # =============================================================================

        st.subheader("🧫 Adubação para Vasos")

        c1,c2 = st.columns(2)

        with c1:

            altura = st.number_input(
                "Altura do vaso (cm)",
                5.0
            )

        with c2:

            raio = st.number_input(
                "Raio do vaso (cm)",
                5.0
            )

        area = math.pi * ((raio ** 2) / 10000)

        n_vaso = calcular_adubacao_vaso(area,info["n"])
        p_vaso = calcular_adubacao_vaso(area,info["p"])
        k_vaso = calcular_adubacao_vaso(area,info["k"])

        st.success(f"⚛️ Nitrogênio: {n_vaso:.2f} g")
        st.success(f"🪨 Fósforo: {p_vaso:.2f} g")
        st.success(f"🍌 Potássio: {k_vaso:.2f} g")

# =============================================================================
# 📊 ABA RELATÓRIO
# =============================================================================

with tabs[4]:

    st.subheader("📊 Relatório Técnico")

    if st.session_state.dados:

        dados = st.session_state.dados

        cultura = dados["cultura"]

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
                necessidades_culturas[cultura]["plantio"]
            ]
        })

        st.dataframe(
            relatorio,
            use_container_width=True,
            hide_index=True
        )

# =============================================================================
# 🤖 ABA IA
# =============================================================================

with tabs[5]:

    st.subheader("🤖 IA Agronômica")

    pergunta = st.text_area(
        "Digite sua dúvida"
    )

    st.caption("""
A IA responde apenas:
- fertilidade
- adubação
- manejo
- erosão
- compactação
- nutrientes
""")

    if st.button("🚀 Perguntar"):

        resposta = assistente_agronomico(
            pergunta,
            st.session_state.dados
        )

        st.success(resposta)

# =============================================================================
# 🌿 RODAPÉ
# =============================================================================

st.markdown("---")

st.caption("""
© 2026 - AgroSolo IA Premium
Sistema Inteligente de Fertilidade do Solo
""")========================================================

# =============================================================================
# 📦 IMPORTAÇÕES
# =============================================================================

import streamlit as st
import pandas as pd
import math

# =============================================================================
# 📊 PLOTLY (GRÁFICOS MODERNOS)
# =============================================================================

try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except:
    PLOTLY_AVAILABLE = False

# =============================================================================
# 🤖 GEMINI IA (GOOGLE)
# =============================================================================

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except:
    GEMINI_AVAILABLE = False

# =============================================================================
# ⚙️ CONFIGURAÇÃO DA PÁGINA
# =============================================================================

st.set_page_config(
    page_title="AgroSolo IA",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# 🎨 CSS MODERNO
# =============================================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;700;800&display=swap');

html, body, [class*="css"]{
    font-family:'Inter',sans-serif;
}

.stApp{
    background:linear-gradient(135deg,#081c15 0%,#0f2d1f 50%,#081c15 100%);
}

.block-container{
    max-width:100% !important;
    padding-top:1rem;
    padding-left:2rem;
    padding-right:2rem;
}

h1,h2,h3,h4,h5,h6{
    color:#b7ffcb !important;
    font-weight:800 !important;
}

p,span,label,div{
    color:white !important;
}

section[data-testid="stSidebar"]{
    background:#07130d;
    border-right:1px solid rgba(255,255,255,0.08);
}

.stTextInput input,
.stNumberInput input,
textarea{
    background:#10251a !important;
    border:1px solid #43a06b !important;
    border-radius:14px !important;
    color:white !important;
}

div[data-baseweb="select"] > div{
    background:#10251a !important;
    border:1px solid #43a06b !important;
    border-radius:14px !important;
}

div[data-baseweb="select"] *{
    color:white !important;
}

.stButton > button{
    background:linear-gradient(90deg,#2e7d52,#45b36b);
    border:none;
    border-radius:14px;
    color:white;
    font-weight:700;
    padding:0.8rem;
    width:100%;
}

[data-testid="stMetric"]{
    background:rgba(255,255,255,0.04);
    border:1px solid rgba(255,255,255,0.08);
    border-radius:18px;
    padding:1rem;
}

.card{
    background:rgba(255,255,255,0.04);
    border-radius:20px;
    padding:1.5rem;
    border:1px solid rgba(255,255,255,0.08);
    margin-bottom:1rem;
}

button[data-baseweb="tab"]{
    font-size:16px !important;
    font-weight:700 !important;
    color:white !important;
}

button[data-baseweb="tab"][aria-selected="true"]{
    background:#2f7d54 !important;
    border-radius:14px;
}

hr{
    border:none;
    height:1px;
    background:rgba(255,255,255,0.08);
}

</style>
""", unsafe_allow_html=True)

# =============================================================================
# 🌾 CULTURAS EMBRAPA (ORDEM ALFABÉTICA)
# =============================================================================

necessidades_culturas = {

    "Arroz":{
        "v":50,
        "n":85,
        "p":60,
        "k":50,
        "plantio":"Outubro a Dezembro"
    },

    "Café":{
        "v":70,
        "n":180,
        "p":120,
        "k":100,
        "plantio":"Outubro a Março"
    },

    "Cana-de-açúcar":{
        "v":60,
        "n":100,
        "p":90,
        "k":120,
        "plantio":"Janeiro a Março"
    },

    "Feijão":{
        "v":60,
        "n":60,
        "p":90,
        "k":70,
        "plantio":"Setembro a Novembro"
    },

    "Milheto":{
        "v":50,
        "n":70,
        "p":60,
        "k":50,
        "plantio":"Outubro a Janeiro"
    },

    "Milho Grão":{
        "v":65,
        "n":120,
        "p":100,
        "k":80,
        "plantio":"Setembro a Dezembro"
    },

    "Milho Semente":{
        "v":70,
        "n":140,
        "p":120,
        "k":100,
        "plantio":"Setembro a Novembro"
    },

    "Soja":{
        "v":60,
        "n":20,
        "p":80,
        "k":60,
        "plantio":"Outubro a Dezembro"
    },

    "Sorgo":{
        "v":55,
        "n":90,
        "p":70,
        "k":60,
        "plantio":"Outubro a Janeiro"
    },

    "Tomate":{
        "v":80,
        "n":150,
        "p":150,
        "k":120,
        "plantio":"Ano todo"
    },

    "Trigo":{
        "v":65,
        "n":110,
        "p":80,
        "k":60,
        "plantio":"Abril a Junho"
    }

}

# =============================================================================
# 🧪 FUNÇÕES AGRONÔMICAS
# =============================================================================

def calcular_ph(dados):

    acidez = (
        dados["aluminum"] * 0.3 +
        dados["h_al"] * 0.1
    )

    bases = (
        dados["calcium"] * 0.2 +
        dados["magnesium"] * 0.15 +
        dados["potassium"] * 0.5
    )

    ph = 5.5 + bases - acidez

    return round(max(4.0,min(7.5,ph)),1)

# =============================================================================
# 🪨 CALAGEM
# =============================================================================

def calcular_calagem(v_atual,v_desejado,ctc):

    if v_atual >= v_desejado:
        return 0

    nc = ((v_desejado - v_atual) * ctc) / 100

    return round(nc * 1.25,2)

# =============================================================================
# 💎 GESSAGEM
# =============================================================================

def calcular_gessagem(calagem,argila):

    if argila >= 350:
        return round(calagem * 0.5,2)

    elif argila >= 200:
        return round(calagem * 0.3,2)

    return 0

# =============================================================================
# 🧫 ADUBAÇÃO PARA VASO
# =============================================================================

def calcular_adubacao_vaso(area,recomendacao):

    kg_m2 = recomendacao / 10000

    g = kg_m2 * area * 1000

    return round(g,2)

# =============================================================================
# 🤖 IA DE FERTILIDADE
# =============================================================================

def classificar_fertilidade(ph,v,materia):

    score = 0

    if ph >= 5.5 and ph <= 6.5:
        score += 1

    if v >= 50:
        score += 1

    if materia >= 25:
        score += 1

    if score == 3:
        return "🟢 Alta Fertilidade"

    elif score == 2:
        return "🟡 Média Fertilidade"

    else:
        return "🔴 Baixa Fertilidade"

# =============================================================================
# 🤖 GEMINI IA
# =============================================================================

modelo_gemini = None

with st.sidebar:

    st.markdown("## 🤖 Configuração IA")

    api_key = st.text_input(
        "API KEY Gemini",
        type="password"
    )

    if GEMINI_AVAILABLE and api_key:

        try:

            genai.configure(api_key=api_key)

            modelo_gemini = genai.GenerativeModel("gemini-pro")

            st.success("IA conectada.")

        except:

            st.error("Erro ao conectar IA.")

    else:

        st.info("Adicione API KEY Gemini.")

# =============================================================================
# 💬 ASSISTENTE IA
# =============================================================================

def assistente_agronomico(pergunta,dados):

    if modelo_gemini is None:

        return """
⚠️ IA não conectada.

Instale:
pip install google-generativeai

Depois adicione sua API KEY Gemini.
"""

    contexto = f"""

Você é um engenheiro agrônomo especialista em:
- fertilidade do solo
- manejo
- adubação
- Embrapa
- agricultura tropical

Dados atuais do solo:

pH: {dados.get('ph')}
Matéria Orgânica: {dados.get('organic_matter')}
Argila: {dados.get('clay')}
Cultura: {dados.get('cultura')}

Responda apenas sobre:
- fertilidade
- adubação
- manejo
- solo
- compactação
- erosão
- nutrientes

Seja didático.
"""

    resposta = modelo_gemini.generate_content(
        contexto + "\nPergunta:" + pergunta
    )

    return resposta.text

# =============================================================================
# 💾 SESSION STATE
# =============================================================================

if "dados" not in st.session_state:
    st.session_state.dados = {}

# =============================================================================
# 🌿 HEADER
# =============================================================================

st.markdown("""
<div class='card'>
<h1>🌿 AgroSolo IA Premium</h1>
<p>
Sistema Inteligente de Classificação de Fertilidade do Solo
</p>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# 📑 TABS
# =============================================================================

tabs = st.tabs([
    "🪪 Cadastro",
    "🌱 Solo",
    "🧠 Fertilidade",
    "🧪 Adubação",
    "📊 Relatório",
    "🤖 Assistente IA"
])

# =============================================================================
# 🪪 ABA CADASTRO
# =============================================================================

with tabs[0]:

    st.subheader("🪪 Cadastro do Usuário")

    st.caption("""
Não obrigatório.
Utilizado apenas para identificação do relatório.
""")

    c1,c2 = st.columns(2)

    with c1:

        nome = st.text_input("Nome")
        fazenda = st.text_input("Fazenda")
        cidade = st.text_input("Cidade")

    with c2:

        estado = st.text_input("Estado")
        cep = st.text_input("CEP")

# =============================================================================
# 🌱 ABA SOLO
# =============================================================================

with tabs[1]:

    st.subheader("🌱 Dados do Solo")

    st.markdown("""
### 📘 O que preencher?

- Nitrogênio → fertilidade nitrogenada
- Fósforo → disponibilidade energética
- Potássio → resistência e produtividade
- Alumínio → toxicidade
- Matéria Orgânica → saúde do solo
""")

    col1,col2,col3 = st.columns(3)

    with col1:

        nitrogen = st.number_input("Nitrogênio",0.0)
        phosphorus = st.number_input("Fósforo",0.0)
        potassium = st.number_input("Potássio",0.0)

    with col2:

        calcium = st.number_input("Cálcio",0.0)
        magnesium = st.number_input("Magnésio",0.0)
        aluminum = st.number_input("Alumínio",0.0)

    with col3:

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

        st.success("Dados salvos com sucesso.")

# =============================================================================
# 🧠 ABA FERTILIDADE
# =============================================================================

with tabs[2]:

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

        classificacao = classificar_fertilidade(
            ph,
            v,
            dados["organic_matter"]
        )

        c1,c2,c3 = st.columns(3)

        c1.metric("🧪 pH",ph)
        c2.metric("🌿 V%",round(v,1))
        c3.metric("🍂 Matéria Orgânica",dados["organic_matter"])

        st.markdown("---")

        if "Alta" in classificacao:
            st.success(classificacao)

        elif "Média" in classificacao:
            st.warning(classificacao)

        else:
            st.error(classificacao)

        # =============================================================================
        # 📊 GRÁFICO DIDÁTICO
        # =============================================================================

        st.markdown("## 📊 Indicadores de Fertilidade")

        grafico_df = pd.DataFrame({

            "Indicador":[
                "pH",
                "V%",
                "Matéria Orgânica"
            ],

            "Valor":[
                ph,
                round(v,1),
                dados["organic_matter"]
            ]
        })

        st.markdown("""
### 📘 Como interpretar?

- Eixo X → indicadores do solo
- Eixo Y → valores da análise

Quanto maior:
- V%
- matéria orgânica

melhor a fertilidade.
""")

        if PLOTLY_AVAILABLE:

            fig = px.bar(
                grafico_df,
                x="Indicador",
                y="Valor",
                color="Indicador",
                text="Valor",
                title="Análise Visual da Fertilidade"
            )

            fig.update_layout(
                paper_bgcolor="#081c15",
                plot_bgcolor="#081c15",
                font_color="white",
                title_font_size=24
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        else:

            st.warning("""
Plotly não instalado.

Instale:
pip install plotly
""")

            st.bar_chart(
                grafico_df.set_index("Indicador")
            )

# =============================================================================
# 🧪 ABA ADUBAÇÃO
# =============================================================================

with tabs[3]:

    st.subheader("🧪 Recomendação de Adubação")

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
            info["v"],
            ctc
        )

        gessagem = calcular_gessagem(
            calagem,
            dados["clay"]
        )

        st.metric("🪨 Calagem",f"{calagem} t/ha")
        st.metric("💎 Gessagem",f"{gessagem} t/ha")

        st.markdown("---")

        st.markdown(f"""
# ⚛️ Nitrogênio (N)

### Recomendação:
{info["n"]} kg/ha

### Como aplicar?
- 30% no plantio
- 30% aos 30 dias
- 40% aos 60 dias

### Importância:
Responsável pelo crescimento vegetativo.

---

# 🪨 Fósforo (P₂O₅)

### Recomendação:
{info["p"]} kg/ha

### Como aplicar?
- Aplicação no sulco
- Incorporado ao solo

### Importância:
Desenvolvimento radicular.

---

# 🍌 Potássio (K₂O)

### Recomendação:
{info["k"]} kg/ha

### Como aplicar?
- 50% no plantio
- 50% em cobertura

### Importância:
Resistência e produtividade.
""")

        st.markdown("---")

        # =============================================================================
        # 🧫 ADUBAÇÃO PARA VASO
        # =============================================================================

        st.subheader("🧫 Adubação para Vasos")

        st.caption("""
Utilizado para experimentos e pesquisas.
""")

        c1,c2 = st.columns(2)

        with c1:

            altura = st.number_input(
                "Altura do vaso (cm)",
                5.0
            )

        with c2:

            raio = st.number_input(
                "Raio do vaso (cm)",
                5.0
            )

        area = math.pi * ((raio ** 2) / 10000)

        n_vaso = calcular_adubacao_vaso(
            area,
            info["n"]
        )

        p_vaso = calcular_adubacao_vaso(
            area,
            info["p"]
        )

        k_vaso = calcular_adubacao_vaso(
            area,
            info["k"]
        )

        st.success(f"⚛️ Nitrogênio: {n_vaso:.2f} g")
        st.success(f"🪨 Fósforo: {p_vaso:.2f} g")
        st.success(f"🍌 Potássio: {k_vaso:.2f} g")

# =============================================================================
# 📊 RELATÓRIO
# =============================================================================

with tabs[4]:

    st.subheader("📊 Relatório Técnico")

    if st.session_state.dados:

        dados = st.session_state.dados

        cultura = dados["cultura"]

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
                necessidades_culturas[cultura]["plantio"]
            ]
        })

        st.dataframe(
            relatorio,
            use_container_width=True,
            hide_index=True
        )

        csv = relatorio.to_csv(index=False).encode("utf-8")

        st.download_button(
            "📥 Baixar Relatório CSV",
            csv,
            "relatorio_solo.csv",
            "text/csv"
        )

# =============================================================================
# 🤖 ASSISTENTE IA
# =============================================================================

with tabs[5]:

    st.subheader("🤖 Assistente Agronômico IA")

    pergunta = st.text_area(
        "Digite sua dúvida"
    )

    st.caption("""
⚠️ A IA responde apenas:
- fertilidade
- solo
- nutrientes
- manejo
- adubação
- compactação
- erosão
""")

    if st.button("🚀 Perguntar à IA"):

        resposta = assistente_agronomico(
            pergunta,
            st.session_state.dados
        )

        st.success(resposta)

# =============================================================================
# 🌿 RODAPÉ
# =============================================================================

st.markdown("---")

st.caption("""
© 2026 - AgroSolo IA Premium
Sistema Inteligente de Fertilidade do Solo
""")
