import streamlit as st
import pandas as pd
import math
import matplotlib.pyplot as plt

# =========================================================
# CONFIGURAÇÃO DA PÁGINA
# =========================================================

st.set_page_config(
    page_title="AgroSolo IA",
    page_icon="🌱",
    layout="wide"
)

# =========================================================
# CSS MODERNO
# =========================================================

st.markdown("""
<style>

.stApp {
    background: linear-gradient(135deg,#071b11,#0d2818,#071b11);
    color: white;
}

.block-container {
    padding-top: 1rem;
    max-width: 100%;
}

h1,h2,h3,h4,h5 {
    color: #9df5b3 !important;
}

.stButton>button {
    background: linear-gradient(90deg,#1d8348,#27ae60);
    color: white;
    border-radius: 12px;
    border: none;
    font-weight: bold;
    padding: 0.7rem 1rem;
}

.stTextInput input,
.stNumberInput input,
textarea {
    border-radius: 12px !important;
    border: 2px solid #2ecc71 !important;
}

div[data-baseweb="select"] > div {
    border-radius: 12px !important;
    border: 2px solid #2ecc71 !important;
}

.metric-card {
    background: rgba(255,255,255,0.05);
    border-radius: 16px;
    padding: 1rem;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# CULTURAS
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
        "k": 140,
        "plantio": "Outubro a Dezembro"
    },

    "Cana-de-açúcar": {
        "n": 120,
        "p": 100,
        "k": 140,
        "plantio": "Janeiro a Março"
    },

    "Feijão": {
        "n": 80,
        "p": 80,
        "k": 60,
        "plantio": "Agosto a Outubro"
    },

    "Milheto": {
        "n": 70,
        "p": 60,
        "k": 50,
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
        "n": 100,
        "p": 70,
        "k": 60,
        "plantio": "Setembro a Novembro"
    },

    "Tomate": {
        "n": 180,
        "p": 160,
        "k": 180,
        "plantio": "Ano todo"
    },

    "Trigo": {
        "n": 120,
        "p": 90,
        "k": 70,
        "plantio": "Abril a Junho"
    }
}

# =========================================================
# FUNÇÕES
# =========================================================

def calcular_ph(ca, mg, al, hal, k):
    ph = 7 + ((ca + mg + k) * 0.1) - ((al + hal) * 0.08)
    return round(max(4.0, min(7.5, ph)), 1)

def calcular_v(sb, ctc):
    if ctc == 0:
        return 0
    return round((sb / ctc) * 100, 1)

def classificar_fertilidade(ph, v):

    if ph < 5.2 or v < 40:
        return "🔴 Baixa Fertilidade"

    elif 40 <= v < 65:
        return "🟡 Média Fertilidade"

    else:
        return "🟢 Alta Fertilidade"

def resposta_ia(pergunta):

    pergunta = pergunta.lower()

    respostas = {

        "calagem":
        "A calagem corrige a acidez do solo, aumenta o pH e melhora a disponibilidade de nutrientes.",

        "gessagem":
        "A gessagem reduz toxidez por alumínio em profundidade e melhora o crescimento radicular.",

        "fertilidade":
        "A fertilidade do solo influencia diretamente produtividade, raízes e absorção de nutrientes.",

        "compactação":
        "Evite excesso de máquinas e utilize cobertura vegetal para reduzir compactação.",

        "erosão":
        "Cobertura vegetal e plantio em nível ajudam a evitar erosão.",

        "matéria orgânica":
        "A matéria orgânica melhora retenção de água, microbiologia e estrutura do solo.",

        "nitrogênio":
        "O nitrogênio deve ser parcelado para reduzir perdas por volatilização e lixiviação.",

        "fósforo":
        "O fósforo é essencial para raízes e desenvolvimento inicial.",

        "potássio":
        "O potássio melhora resistência da planta e enchimento de grãos."
    }

    for chave in respostas:
        if chave in pergunta:
            return respostas[chave]

    return "Pergunta fora do escopo do sistema."

# =========================================================
# HEADER
# =========================================================

st.title("🌱 AgroSolo IA")
st.markdown("### Sistema Inteligente de Fertilidade do Solo")

# =========================================================
# ABAS
# =========================================================

aba1, aba2, aba3, aba4, aba5 = st.tabs([
    "📋 Cadastro",
    "🌱 Classificação",
    "🧪 Adubação",
    "📊 Relatório",
    "🤖 IA"
])

# =========================================================
# ABA 1
# =========================================================

with aba1:

    st.header("📋 Cadastro")

    col1, col2 = st.columns(2)

    with col1:
        nome = st.text_input("Nome")
        fazenda = st.text_input("Fazenda")
        cidade = st.text_input("Cidade")

    with col2:
        estado = st.text_input("Estado")
        cep = st.text_input("CEP")

        cultura = st.selectbox(
            "🌾 Cultura",
            sorted(culturas.keys())
        )

    st.markdown("---")

    st.header("🌱 Dados do Solo")

    c1, c2, c3 = st.columns(3)

    with c1:
        n = st.number_input("Nitrogênio", 0.0)
        p = st.number_input("Fósforo", 0.0)
        k = st.number_input("Potássio", 0.0)

    with c2:
        ca = st.number_input("Cálcio", 0.0)
        mg = st.number_input("Magnésio", 0.0)
        al = st.number_input("Alumínio", 0.0)

    with c3:
        hal = st.number_input("H+Al", 0.0)
        mo = st.number_input("Matéria Orgânica", 0.0)
        argila = st.number_input("Argila g/kg", 0.0)

    if st.button("💾 Salvar Dados"):

        st.session_state["dados"] = {
            "nome": nome,
            "fazenda": fazenda,
            "cidade": cidade,
            "estado": estado,
            "cep": cep,
            "cultura": cultura,
            "n": n,
            "p": p,
            "k": k,
            "ca": ca,
            "mg": mg,
            "al": al,
            "hal": hal,
            "mo": mo,
            "argila": argila
        }

        st.success("Dados salvos com sucesso.")

# =========================================================
# ABA 2
# =========================================================

with aba2:

    st.header("🌱 Classificação da Fertilidade")

    if "dados" not in st.session_state:

        st.warning("Preencha os dados primeiro.")

    else:

        dados = st.session_state["dados"]

        sb = dados["ca"] + dados["mg"] + dados["k"]
        ctc = sb + dados["hal"]

        ph = calcular_ph(
            dados["ca"],
            dados["mg"],
            dados["al"],
            dados["hal"],
            dados["k"]
        )

        v = calcular_v(sb, ctc)

        fertilidade = classificar_fertilidade(ph, v)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("pH", ph)

        with col2:
            st.metric("V%", v)

        with col3:
            st.metric("CTC", round(ctc,2))

        st.success(f"Classificação IA: {fertilidade}")

        st.markdown("---")

        st.subheader("📊 Indicador Visual")

        fig, ax = plt.subplots(figsize=(5,5))

        valores = [
            max(dados["n"],1),
            max(dados["p"],1),
            max(dados["k"],1)
        ]

        labels = [
            "Nitrogênio",
            "Fósforo",
            "Potássio"
        ]

        ax.pie(
            valores,
            labels=labels,
            autopct='%1.1f%%'
        )

        st.pyplot(fig)

        st.info(
            "O gráfico representa a participação relativa dos nutrientes N, P e K presentes no solo."
        )

# =========================================================
# ABA 3
# =========================================================

with aba3:

    st.header("🧪 Adubação")

    if "dados" not in st.session_state:

        st.warning("Preencha os dados primeiro.")

    else:

        dados = st.session_state["dados"]

        cultura = dados["cultura"]

        info = culturas[cultura]

        st.subheader(f"🌾 Cultura: {cultura}")

        st.markdown(f"### 📅 Melhor época de plantio")
        st.success(info["plantio"])

        st.markdown("---")

        st.subheader("📦 Recomendação de Campo")

        st.write(
            f"⚛️ Nitrogênio: {info['n']} kg/ha "
            "(parcelado aos 30, 60 e 90 dias)"
        )

        st.write(
            f"🪨 Fósforo: {info['p']} kg/ha "
            "(aplicação no plantio)"
        )

        st.write(
            f"🍌 Potássio: {info['k']} kg/ha "
            "(50% plantio e 50% cobertura)"
        )

        st.markdown("---")

        st.subheader("🪴 Cálculo para Vasos")

        altura = st.number_input(
            "Altura do vaso (cm)",
            min_value=1.0
        )

        raio = st.number_input(
            "Raio do vaso (cm)",
            min_value=1.0
        )

        area = math.pi * (raio ** 2)

        volume = area * altura

        fator = volume / 100000

        n_vaso = round(info["n"] * fator, 2)
        p_vaso = round(info["p"] * fator, 2)
        k_vaso = round(info["k"] * fator, 2)

        st.success(f"⚛️ Nitrogênio no vaso: {n_vaso} g")
        st.success(f"🪨 Fósforo no vaso: {p_vaso} g")
        st.success(f"🍌 Potássio no vaso: {k_vaso} g")

# =========================================================
# ABA 4
# =========================================================

with aba4:

    st.header("📊 Relatório Técnico")

    if "dados" not in st.session_state:

        st.warning("Sem dados.")

    else:

        dados = st.session_state["dados"]

        tabela = pd.DataFrame({
            "Parâmetro": list(dados.keys()),
            "Valor": list(dados.values())
        })

        st.dataframe(
            tabela,
            use_container_width=True
        )

        csv = tabela.to_csv(index=False).encode("utf-8")

        st.download_button(
            "📥 Baixar Relatório",
            csv,
            "relatorio.csv",
            "text/csv"
        )

# =========================================================
# ABA 5
# =========================================================

with aba5:

    st.header("🤖 IA Agrícola")

    st.info(
        "Esta IA responde apenas dúvidas sobre fertilidade, "
        "adubação, manejo do solo, calagem e gessagem."
    )

    pergunta = st.text_area(
        "Digite sua dúvida"
    )

    if st.button("Responder"):

        resposta = resposta_ia(pergunta)

        st.success(resposta)

        st.markdown("---")

        st.subheader("📚 Perguntas sugeridas")

        st.write("• Porque fazer calagem?")
        st.write("• Porque a fertilidade é importante?")
        st.write("• Como evitar compactação?")
        st.write("• Como evitar erosão?")
        st.write("• Porque parcelar nitrogênio?")
        st.write("• Qual importância do fósforo?")
        st.write("• Qual importância do potássio?")

# =========================================================
# RODAPÉ
# =========================================================

st.markdown("---")

st.caption("""
Sistema acadêmico e educacional sem fins lucrativos.

Ferramenta desenvolvida para estudos agronômicos,
fertilidade do solo e apoio técnico.

As respostas da IA possuem caráter informativo.
""")
