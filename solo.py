# =========================================================
# AGROSOLO IA - SISTEMA INTELIGENTE DE FERTILIDADE DO SOLO
# =========================================================
# Desenvolvido para fins acadêmicos e educacionais.
# Base conceitual: Embrapa / SiBCS / Boletins Técnicos.
# =========================================================

import streamlit as st
import pandas as pd
import math
import os

# =========================================================
# CONFIGURAÇÃO DA PÁGINA
# =========================================================

st.set_page_config(
    page_title="AgroSolo IA",
    page_icon="🌱",
    layout="wide",
)

# =========================================================
# IA GENERATIVA (GEMINI)
# =========================================================

GEMINI_OK = False
modelo_gemini = None

try:
    import google.generativeai as genai

    API_KEY = os.getenv("GEMINI_API_KEY", "")

    if API_KEY:
        genai.configure(api_key=API_KEY)
        modelo_gemini = genai.GenerativeModel("gemini-1.5-flash")
        GEMINI_OK = True

except:
    GEMINI_OK = False

# =========================================================
# CSS MODERNO
# =========================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: linear-gradient(135deg,#071b11,#0c2d1d,#071b11);
    color: white;
}

.block-container{
    max-width: 100%;
    padding-top: 1rem;
    padding-bottom: 2rem;
}

h1,h2,h3,h4,h5{
    color:#9df5b3;
}

section[data-testid="stSidebar"]{
    background:#08150e;
}

div[data-baseweb="select"] > div{
    background:#10251a;
    border:1px solid #2d6a4f;
}

.stTextInput input,
.stNumberInput input{
    background:#10251a;
    color:white;
    border:1px solid #2d6a4f;
    border-radius:10px;
}

.stButton button{
    background:linear-gradient(90deg,#2d6a4f,#40916c);
    color:white;
    border:none;
    border-radius:12px;
    font-weight:600;
}

.metric-card{
    background:#10251a;
    padding:1rem;
    border-radius:16px;
    border:1px solid #2d6a4f;
}

.info-box{
    background:#10251a;
    border-left:4px solid #52b788;
    padding:1rem;
    border-radius:12px;
}

footer{
    visibility:hidden;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# CULTURAS EM ORDEM ALFABÉTICA
# =========================================================

culturas = {
    "Arroz": {
        "n": 90,
        "p": 70,
        "k": 60,
        "plantio": "Setembro a Novembro"
    },

    "Café": {
        "n": 180,
        "p": 120,
        "k": 100,
        "plantio": "Outubro a Dezembro"
    },

    "Cana-de-açúcar": {
        "n": 120,
        "p": 100,
        "k": 120,
        "plantio": "Janeiro a Março"
    },

    "Feijão": {
        "n": 80,
        "p": 90,
        "k": 70,
        "plantio": "Abril a Julho"
    },

    "Milheto": {
        "n": 60,
        "p": 50,
        "k": 40,
        "plantio": "Setembro a Novembro"
    },

    "Milho Grão": {
        "n": 140,
        "p": 100,
        "k": 90,
        "plantio": "Setembro a Dezembro"
    },

    "Milho Semente": {
        "n": 150,
        "p": 110,
        "k": 100,
        "plantio": "Setembro a Dezembro"
    },

    "Soja": {
        "n": 20,
        "p": 90,
        "k": 80,
        "plantio": "Outubro a Dezembro"
    },

    "Sorgo": {
        "n": 80,
        "p": 60,
        "k": 50,
        "plantio": "Setembro a Novembro"
    },

    "Tomate": {
        "n": 180,
        "p": 150,
        "k": 130,
        "plantio": "Ano todo"
    },

    "Trigo": {
        "n": 120,
        "p": 80,
        "k": 70,
        "plantio": "Maio a Julho"
    }
}

# =========================================================
# FUNÇÕES
# =========================================================

def calcular_ph(ca, mg, k, al, hal):
    try:
        base = (ca + mg + k) * 0.25
        acidez = (al + hal) * 0.15
        ph = 5.5 + base - acidez
        return max(4.0, min(7.5, round(ph,1)))
    except:
        return 5.5

def classificar_fertilidade(v, ph):
    score = 0

    if ph >= 5.5:
        score += 1

    if v >= 60:
        score += 1

    if score == 2:
        return "🟢 Alta Fertilidade"

    elif score == 1:
        return "🟡 Média Fertilidade"

    return "🔴 Baixa Fertilidade"

def calcular_calagem(v_atual, v_desejado, ctc):
    if v_atual >= v_desejado:
        return 0
    return round(((v_desejado - v_atual) * ctc)/100,2)

def calcular_gessagem(clay, calagem):
    if clay >= 350:
        return round(calagem*0.5,2)
    return 0

def adubacao_vaso(area, dose):
    return round((dose/10000)*area*1000,2)

# =========================================================
# HEADER
# =========================================================

st.markdown("""
<h1 style='text-align:center;'>🌱 AgroSolo IA</h1>
<p style='text-align:center;color:#9df5b3;font-size:18px;'>
Sistema Inteligente de Fertilidade do Solo
</p>
""", unsafe_allow_html=True)

# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.header("⚙️ Sistema")

    if GEMINI_OK:
        st.success("IA conectada com Gemini.")
    else:
        st.warning("IA não conectada.")
        st.caption("Defina GEMINI_API_KEY nas variáveis de ambiente.")

    st.markdown("---")

    st.markdown("""
### 📘 Recursos

- Classificação do solo
- Recomendações NPK
- Calagem
- Gessagem
- Adubação para vasos
- IA para dúvidas agrícolas
- Relatório técnico
""")

# =========================================================
# ABAS
# =========================================================

abas = st.tabs([
    "📋 Cadastro",
    "🌱 Solo",
    "🧪 Vaso",
    "📊 Relatório",
    "🤖 IA Agrícola"
])

# =========================================================
# ABA 1
# =========================================================

with abas[0]:

    st.subheader("📋 Cadastro do Usuário")

    col1,col2,col3 = st.columns(3)

    with col1:
        nome = st.text_input("Nome")

    with col2:
        fazenda = st.text_input("Fazenda")

    with col3:
        cidade = st.text_input("Cidade")

    col4,col5 = st.columns(2)

    with col4:
        estado = st.text_input("Estado")

    with col5:
        cep = st.text_input("CEP")

    st.info("O preenchimento é opcional.")

# =========================================================
# ABA 2
# =========================================================

with abas[1]:

    st.subheader("🌱 Dados do Solo")

    cultura = st.selectbox(
        "🌾 Cultura",
        sorted(culturas.keys())
    )

    col1,col2,col3 = st.columns(3)

    with col1:
        n = st.number_input("Nitrogênio",0.0)
        p = st.number_input("Fósforo",0.0)
        k = st.number_input("Potássio",0.0)

    with col2:
        ca = st.number_input("Cálcio",0.0)
        mg = st.number_input("Magnésio",0.0)
        al = st.number_input("Alumínio",0.0)

    with col3:
        hal = st.number_input("H + Al",0.0)
        clay = st.number_input("Argila g/kg",0.0)
        mo = st.number_input("Matéria Orgânica",0.0)

    if st.button("🔬 Classificar Solo"):

        ph = calcular_ph(ca,mg,k,al,hal)

        sb = ca + mg + k
        ctc = sb + hal

        if ctc > 0:
            v = (sb/ctc)*100
        else:
            v = 0

        fertilidade = classificar_fertilidade(v,ph)

        st.session_state["dados"] = {
            "ph":ph,
            "v":v,
            "ctc":ctc,
            "cultura":cultura,
            "clay":clay
        }

        st.success("Classificação concluída.")

        c1,c2,c3 = st.columns(3)

        with c1:
            st.metric("pH",ph)

        with c2:
            st.metric("V%",round(v,1))

        with c3:
            st.metric("CTC",round(ctc,1))

        st.markdown("---")

        st.subheader("📈 Indicador Visual")

        pizza = pd.DataFrame({
            "Classe":["Acidez","Bases","Matéria Orgânica"],
            "Valor":[max(1,7-ph), max(1,v), max(1,mo)]
        })

        st.plotly_chart({
            "data":[
                {
                    "labels":pizza["Classe"],
                    "values":pizza["Valor"],
                    "type":"pie"
                }
            ],
            "layout":{
                "paper_bgcolor":"#071b11",
                "font":{"color":"white"},
                "title":"Indicadores de Fertilidade"
            }
        }, use_container_width=True)

        st.markdown(f"""
<div class='info-box'>
<h4>{fertilidade}</h4>

<p><b>O gráfico representa:</b></p>

<ul>
<li><b>Acidez:</b> influência do pH.</li>
<li><b>Bases:</b> fertilidade química do solo.</li>
<li><b>Matéria Orgânica:</b> qualidade biológica.</li>
</ul>

</div>
""", unsafe_allow_html=True)

        st.markdown("---")

        st.subheader("🌾 Recomendação")

        dados_cultura = culturas[cultura]

        calagem = calcular_calagem(v,60,ctc)
        gessagem = calcular_gessagem(clay,calagem)

        st.markdown(f"""
### 🪨 Calagem
Aplicar aproximadamente **{calagem} t/ha** de calcário.

### 💎 Gessagem
Aplicar aproximadamente **{gessagem} t/ha** de gesso agrícola.

### ⚛️ Nitrogênio (N)
Aplicar **{dados_cultura['n']} kg/ha** parcelado:
- 30% no plantio
- 40% aos 30 dias
- 30% aos 60 dias

### 🪨 Fósforo (P₂O₅)
Aplicar **{dados_cultura['p']} kg/ha**
preferencialmente no sulco de plantio.

### 🍌 Potássio (K₂O)
Aplicar **{dados_cultura['k']} kg/ha**
parcelado entre plantio e cobertura.

### 📅 Melhor época de plantio
**{dados_cultura['plantio']}**
""")

# =========================================================
# ABA 3
# =========================================================

with abas[2]:

    st.subheader("🧪 Adubação para Vasos")

    altura = st.number_input("Altura do vaso (cm)",1.0)
    raio = st.number_input("Raio do vaso (cm)",1.0)

    area = math.pi*(raio**2)/10000

    st.write(f"Área do vaso: {area:.4f} m²")

    if "dados" in st.session_state:

        cultura = st.session_state["dados"]["cultura"]

        dados_cultura = culturas[cultura]

        n_vaso = adubacao_vaso(area,dados_cultura["n"])
        p_vaso = adubacao_vaso(area,dados_cultura["p"])
        k_vaso = adubacao_vaso(area,dados_cultura["k"])

        st.success(f"""
Nitrogênio: {n_vaso:.2f} g

Fósforo: {p_vaso:.2f} g

Potássio: {k_vaso:.2f} g
""")

# =========================================================
# ABA 4
# =========================================================

with abas[3]:

    st.subheader("📊 Relatório Técnico")

    if "dados" in st.session_state:

        dados = st.session_state["dados"]

        tabela = pd.DataFrame({
            "Parâmetro":[
                "Cultura",
                "pH",
                "V%",
                "CTC"
            ],
            "Valor":[
                dados["cultura"],
                dados["ph"],
                round(dados["v"],1),
                round(dados["ctc"],1)
            ]
        })

        st.dataframe(tabela,use_container_width=True)

# =========================================================
# ABA 5
# =========================================================

with abas[4]:

    st.subheader("🤖 IA Agrícola")

    pergunta = st.text_area(
        "Digite sua dúvida",
        placeholder="""
Exemplos:

- Porque fazer calagem?
- Como evitar compactação?
- Qual importância do nitrogênio?
- Como evitar erosão?
"""
    )

    st.caption("""
A IA responde apenas dúvidas relacionadas ao sistema,
fertilidade do solo, adubação, manejo e interpretação agrícola.
""")

    if st.button("Perguntar à IA"):

        if not GEMINI_OK:
            st.error("IA não conectada.")
        else:

            prompt = f"""
Você é um engenheiro agrônomo especialista da Embrapa.

Responda de forma técnica, clara e objetiva.

Pergunta:
{pergunta}
"""

            try:
                resposta = modelo_gemini.generate_content(prompt)

                st.success(resposta.text)

            except Exception as e:
                st.error(f"Erro IA: {e}")

# =========================================================
# RODAPÉ
# =========================================================

st.markdown("---")

st.caption("""
© 2026 - AgroSolo IA

Sistema acadêmico e educacional sem fins lucrativos.

Ferramenta desenvolvida para estudos agronômicos,
fertilidade do solo e apoio técnico.

O uso da API Gemini segue os termos da Google AI.
A responsabilidade pelas respostas geradas pela IA
é exclusivamente informativa e educacional.
""")
