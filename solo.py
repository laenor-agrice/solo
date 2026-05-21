# ============================================================================
# IMPORTAÇÕES
# ============================================================================

import streamlit as st
import pandas as pd
import requests
import json

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

GEMINI_API_KEY = "AIzaSyBibLbN2e3gmzLlNb81wSr7GHrDqkiU6fw"

# ============================================================================
# FUNÇÃO PARA LISTAR MODELOS DISPONÍVEIS
# ============================================================================

def listar_modelos_disponiveis():
    """Lista todos os modelos Gemini disponíveis para sua chave"""
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={GEMINI_API_KEY}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            modelos = response.json()
            nomes_modelos = []
            
            for model in modelos.get('models', []):
                nome = model.get('name', '').replace('models/', '')
                if 'gemini' in nome and 'generateContent' in str(model.get('supportedGenerationMethods', [])):
                    nomes_modelos.append(nome)
            
            return nomes_modelos
        else:
            return []
    except Exception as e:
        return []

# ============================================================================
# FUNÇÃO IA GEMINI
# ============================================================================

def gerar_resposta_ia(pergunta, dados_solo=None):
    """Função com detecção automática do modelo"""
    
    if not GEMINI_API_KEY or GEMINI_API_KEY == "SUA_API_KEY_AQUI":
        return "⚠️ **API Key não configurada!** Configure sua chave no código."
    
    try:
        modelos = listar_modelos_disponiveis()
        
        if not modelos:
            return "❌ **Nenhum modelo Gemini disponível!** Verifique sua API Key."
        
        modelo = modelos[0]
        
        contexto = ""
        if dados_solo and len(dados_solo) > 0:
            contexto = f"""
            Dados do solo analisado:
            - pH: {dados_solo.get('ph', 'N/A')}
            - Saturação por bases (V%): {dados_solo.get('v_porcentagem', 0):.1f}%
            - Saturação por alumínio (m%): {dados_solo.get('m_porcentagem', 0):.1f}%
            - Nitrogênio (N): {dados_solo.get('nitrogen', 'N/A')} mg/dm³
            - Fósforo (P): {dados_solo.get('phosphorus', 'N/A')} mg/dm³
            - Potássio (K): {dados_solo.get('potassium', 'N/A')} cmolc/dm³
            - Cálcio (Ca): {dados_solo.get('calcium', 'N/A')} cmolc/dm³
            - Magnésio (Mg): {dados_solo.get('magnesium', 'N/A')} cmolc/dm³
            - Alumínio (Al): {dados_solo.get('aluminum', 'N/A')} cmolc/dm³
            - H+Al: {dados_solo.get('h_al', 'N/A')} cmolc/dm³
            - Soma de Bases (SB): {dados_solo.get('sb', 0):.2f} cmolc/dm³
            - CTC Potencial: {dados_solo.get('ctc', 0):.2f} cmolc/dm³
            """
        
        prompt = f"""Você é um engenheiro agrônomo especialista em fertilidade do solo, SiBCS e manejo agrícola.

{contexto}

PERGUNTA DO USUÁRIO: {pergunta}

INSTRUÇÕES:
- Responda em português do Brasil
- Seja técnico, claro e objetivo
- Dê recomendações práticas quando possível
- Se não souber algo, diga honestamente
- Use linguagem acessível para produtores rurais

RESPOSTA:"""
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent?key={GEMINI_API_KEY}"
        
        headers = {"Content-Type": "application/json"}
        
        data = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ]
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            resultado = response.json()
            
            if "candidates" in resultado and len(resultado["candidates"]) > 0:
                candidate = resultado["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    if len(candidate["content"]["parts"]) > 0:
                        resposta = candidate["content"]["parts"][0].get("text", "")
                        return resposta
            
            return "❌ Não foi possível extrair a resposta da IA."
        
        elif response.status_code == 401:
            return "❌ **Erro de autenticação (401):** API Key inválida."
        elif response.status_code == 403:
            return "❌ **Acesso negado (403):** Ative a API Gemini."
        elif response.status_code == 429:
            return "❌ **Limite excedido (429):** Muitas requisições. Aguarde."
        else:
            return f"❌ **Erro {response.status_code}**"
    
    except Exception as erro:
        return f"❌ **Erro:** {str(erro)}"

# ============================================================================
# CSS PERSONALIZADO MODERNO (DESIGN APRIMORADO)
# ============================================================================

st.markdown("""
<style>
    * {
        font-family: 'Segoe UI', sans-serif !important;
    }

    .stApp {
        background: linear-gradient(135deg, #0a0a0a, #1a1a2e);
        color: white;
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0f1a, #1a1a2e);
        border-right: 1px solid rgba(46,204,113,0.3);
    }

    h1, h2, h3, h4, h5, h6 {
        color: #2ecc71 !important;
        font-weight: 700 !important;
    }

    p, span, div, label {
        color: #e0e0e0 !important;
    }

    /* Containers com borda arredondada */
    div.element-container:has(.stButton) {
        border-radius: 12px;
    }

    /* Inputs */
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

    /* Botões */
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

    /* Cards */
    .stContainer {
        background: rgba(255,255,255,0.03);
        backdrop-filter: blur(10px);
        border-radius: 22px;
        border: 1px solid rgba(255,255,255,0.08);
        box-shadow: 0px 8px 25px rgba(0,0,0,0.25);
    }

    /* Resultado da IA */
    .result-card {
        background: linear-gradient(145deg, rgba(34,197,94,0.12), rgba(255,255,255,0.04));
        border: 1px solid rgba(46,204,113,0.4);
        border-radius: 22px;
        padding: 2rem;
        text-align: left;
        margin-top: 1rem;
    }

    /* Hero Section */
    .hero {
        background: linear-gradient(135deg, rgba(34,197,94,0.15), rgba(59,130,246,0.1));
        border: 1px solid rgba(255,255,255,0.08);
        padding: 2rem;
        border-radius: 28px;
        text-align: center;
        margin-bottom: 2rem;
        backdrop-filter: blur(10px);
    }
    
    .hero h1 {
        color: white !important;
        font-size: 2.5rem;
    }
    
    .hero p {
        color: white !important;
        font-size: 1.1rem;
    }

    /* Métricas */
    .metric-card {
        background: linear-gradient(145deg, rgba(255,255,255,0.08), rgba(255,255,255,0.03));
        border-radius: 20px;
        padding: 1.2rem;
        text-align: center;
        border: 1px solid rgba(46,204,113,0.3);
    }

    .metric-card h2 {
        color: #2ecc71 !important;
        font-size: 1.8rem;
        margin-bottom: 0.5rem;
    }

    .metric-card h3 {
        color: white !important;
        font-size: 0.9rem;
    }

    /* Expander */
    .streamlit-expanderHeader {
        background-color: rgba(46,204,113,0.1);
        border-radius: 12px;
        font-weight: bold;
    }

    /* Abas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(255,255,255,0.05);
        border-radius: 12px;
        padding: 8px 16px;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: rgba(46,204,113,0.2);
        color: #2ecc71 !important;
    }

    hr {
        margin: 1.5rem 0;
        border-color: rgba(255,255,255,0.1);
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# CABEÇALHO HERO
# ============================================================================

with st.container(border=True):
    st.title("🌾 Classificador Inteligente de Fertilidade do Solo")
    st.write("### Sistema baseado no SiBCS - Embrapa • Análise • IA Gemini • Fertilidade • Relatórios")

# OU com uma imagem de solo/plantação (se quiser manter):
# CAPA - ALTURA MÉDIA (METADE DO BANNER PADRÃO)
with st.container(border=True):
    st.markdown(
        """
        <div style="text-align: center;">
            <img src="https://rehagro.com.br/blog/wp-content/uploads/2025/02/capa-adubacao-base.jpg" 
                 style="width: 100%; max-height: 380px; object-fit: cover; border-radius: 8px;">
            <p style="margin-top: 8px; font-size: 23px; color: #aaa;">🌱 Análise Inteligente do Solo</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("### Sistema baseado no SiBCS - Embrapa")
    
st.write("")  # Espaçamento

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.image(
        "https://cdn-icons-png.flaticon.com/512/2909/2909763.png",
        width=90
    )
    
    st.markdown("## 🌱 Sistema Inteligente")
    st.markdown("""
    ✅ Avaliação da fertilidade  
    ✅ Cálculo de V% e m%  
    ✅ Classificação SiBCS  
    ✅ Relatório técnico  
    ✅ IA Gemini integrada  
    """)
    
    st.markdown("---")
    
    if st.button("🔧 Testar Conexão API", use_container_width=True):
        with st.spinner("Testando..."):
            modelos = listar_modelos_disponiveis()
            if modelos:
                st.success(f"✅ API conectada! Modelo: {modelos[0]}")
            else:
                st.error("❌ Falha na conexão. Verifique sua API Key.")

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
    "Alface": {"v_desejado": 80, "n_min": 45, "p_min": 30, "k_min": 0.45, "ph_min": 6.0, "ph_max": 7.0},
    "Algodão": {"v_desejado": 70, "n_min": 40, "p_min": 25, "k_min": 0.4, "ph_min": 5.8, "ph_max": 6.8},
    "Arroz": {"v_desejado": 65, "n_min": 35, "p_min": 20, "k_min": 0.35, "ph_min": 5.5, "ph_max": 6.5},
    "Batata": {"v_desejado": 80, "n_min": 45, "p_min": 30, "k_min": 0.45, "ph_min": 5.5, "ph_max": 6.5},
    "Café": {"v_desejado": 70, "n_min": 40, "p_min": 25, "k_min": 0.4, "ph_min": 5.8, "ph_max": 6.3},
    "Cana-de-açúcar": {"v_desejado": 65, "n_min": 35, "p_min": 20, "k_min": 0.35, "ph_min": 5.5, "ph_max": 6.5},
    "Cebola": {"v_desejado": 75, "n_min": 40, "p_min": 25, "k_min": 0.4, "ph_min": 6.0, "ph_max": 7.0},
    "Cenoura": {"v_desejado": 75, "n_min": 40, "p_min": 25, "k_min": 0.4, "ph_min": 5.8, "ph_max": 6.8},
    "Couve-flor": {"v_desejado": 75, "n_min": 40, "p_min": 25, "k_min": 0.4, "ph_min": 6.0, "ph_max": 7.0},
    "Feijão": {"v_desejado": 65, "n_min": 35, "p_min": 20, "k_min": 0.35, "ph_min": 5.5, "ph_max": 6.5},
    "Mandioca": {"v_desejado": 60, "n_min": 30, "p_min": 15, "k_min": 0.3, "ph_min": 5.0, "ph_max": 6.5},
    "Milheto": {"v_desejado": 60, "n_min": 30, "p_min": 18, "k_min": 0.3, "ph_min": 5.2, "ph_max": 6.2},
    "Milho Grão": {"v_desejado": 70, "n_min": 45, "p_min": 30, "k_min": 0.45, "ph_min": 5.6, "ph_max": 6.8},
    "Milho Semente": {"v_desejado": 75, "n_min": 50, "p_min": 35, "k_min": 0.5, "ph_min": 5.8, "ph_max": 6.8},
    "Pimentão": {"v_desejado": 80, "n_min": 45, "p_min": 30, "k_min": 0.45, "ph_min": 5.8, "ph_max": 6.8},
    "Soja": {"v_desejado": 75, "n_min": 40, "p_min": 25, "k_min": 0.4, "ph_min": 5.8, "ph_max": 6.5},
    "Sorgo": {"v_desejado": 65, "n_min": 35, "p_min": 20, "k_min": 0.35, "ph_min": 5.5, "ph_max": 6.5},
    "Tomate": {"v_desejado": 85, "n_min": 50, "p_min": 35, "k_min": 0.5, "ph_min": 5.8, "ph_max": 6.8},
    "Trigo": {"v_desejado": 65, "n_min": 35, "p_min": 25, "k_min": 0.4, "ph_min": 5.5, "ph_max": 6.5}
}

# ============================================================================
# FUNÇÕES DE CÁLCULO
# ============================================================================

def calcular_sb(ca, mg, k):
    return ca + mg + k

def calcular_tct_potencial(sb, h_al):
    return sb + h_al

def calcular_v_porcentagem(sb, tct_potencial):
    if tct_potencial == 0:
        return 0
    return (sb / tct_potencial) * 100

def calcular_m_porcentagem(al, sb):
    if (al + sb) == 0:
        return 0
    return (al / (al + sb)) * 100

def classificar_fertilidade(v_porcentagem):
    if v_porcentagem < 50:
        return "Baixa fertilidade (V% < 50)"
    elif v_porcentagem < 70:
        return "Fertilidade média (V% entre 50 e 70)"
    elif v_porcentagem < 85:
        return "Fertilidade boa (V% entre 70 e 85)"
    else:
        return "Fertilidade muito boa (V% > 85)"

# ============================================================================
# FUNÇÕES DE RECOMENDAÇÃO DE ADUBAÇÃO E CALAGEM
# ============================================================================

def calcular_necessidade_calagem(v_atual, v_desejado, ctc):
    """Calcula a necessidade de calagem em t/ha"""
    if v_atual >= v_desejado:
        return 0, "✅ Solo já atingiu V% desejado. Não necessita calagem."
    
    f = 100/85
    nc = (ctc * (v_desejado - v_atual) / 100) * f
    nc = round(nc * 2) / 2
    
    if nc > 0:
        recomendacao = f"🔹 **Calagem necessária:** {nc:.1f} t/ha de calcário (PRNT 85%)"
        if nc > 5:
            recomendacao += " - Aplicar parcelado em 2 anos"
    else:
        recomendacao = "Calagem não necessária"
    
    return nc, recomendacao

def recomendar_adubacao_nitrogenio(cultura, n_atual, n_min):
    """Recomenda adubação nitrogenada (N)"""
    if n_atual >= n_min:
        return "✅ N adequado. Adubação de manutenção: 30-50 kg/ha de N"
    
    deficiencia = n_min - n_atual
    
    if cultura in ["Tomate", "Alface", "Batata", "Milho Semente"]:
        recomendacao = f"Alta demanda. Aplicar {deficiencia + 60:.0f} kg/ha de N (parcelado)"
    elif cultura in ["Café", "Cana-de-açúcar", "Milho Grão"]:
        recomendacao = f"Média demanda. Aplicar {deficiencia + 40:.0f} kg/ha de N"
    else:
        recomendacao = f"Baixa demanda. Aplicar {deficiencia + 20:.0f} kg/ha de N"
    
    return f"❌ N baixo ({n_atual} < {n_min}). {recomendacao}"

def recomendar_adubacao_fosforo(cultura, p_atual, p_min):
    """Recomenda adubação fosfatada (P2O5)"""
    if p_atual >= p_min:
        return "✅ P adequado. Adubação de manutenção: 40-80 kg/ha de P2O5"
    
    deficiencia = p_min - p_atual
    
    if cultura in ["Tomate", "Batata", "Soja"]:
        recomendacao = f"Alta demanda. Aplicar {deficiencia + 80:.0f} kg/ha de P2O5"
    elif cultura in ["Café", "Cana-de-açúcar"]:
        recomendacao = f"Média demanda. Aplicar {deficiencia + 60:.0f} kg/ha de P2O5"
    else:
        recomendacao = f"Baixa demanda. Aplicar {deficiencia + 40:.0f} kg/ha de P2O5"
    
    return f"❌ P baixo ({p_atual} < {p_min}). {recomendacao}"

def recomendar_adubacao_potassio(cultura, k_atual, k_min):
    """Recomenda adubação potássica (K2O)"""
    if k_atual >= k_min:
        return "✅ K adequado. Adubação de manutenção: 40-60 kg/ha de K2O"
    
    deficiencia = k_min - k_atual
    
    if cultura in ["Tomate", "Batata", "Café", "Cana-de-açúcar"]:
        recomendacao = f"Alta demanda. Aplicar {deficiencia + 60:.0f} kg/ha de K2O"
    elif cultura in ["Soja", "Milho Grão", "Algodão"]:
        recomendacao = f"Média demanda. Aplicar {deficiencia + 40:.0f} kg/ha de K2O"
    else:
        recomendacao = f"Baixa demanda. Aplicar {deficiencia + 30:.0f} kg/ha de K2O"
    
    return f"❌ K baixo ({k_atual:.2f} < {k_min:.2f}). {recomendacao}"

def recomendar_manejo_geral(dados):
    """Recomendações gerais de manejo"""
    recomendacoes_gerais = []
    
    ph = dados.get('ph', 0)
    m = dados.get('m_porcentagem', 0)
    areia = dados.get('sand', 0)
    argila = dados.get('clay', 0)
    
    if ph < 5.0:
        recomendacoes_gerais.append("🔴 **Acidez muito forte** - Calagem urgente!")
    elif ph < 5.5:
        recomendacoes_gerais.append("🟠 **Acidez forte** - Calagem necessária.")
    elif ph > 7.0:
        recomendacoes_gerais.append("🟡 **pH elevado** - Evitar calagem.")
    
    if m > 30:
        recomendacoes_gerais.append("⚠️ **Alta saturação por Al (m%)** - Calagem urgente!")
    elif m > 15:
        recomendacoes_gerais.append("⚠️ **Média saturação por Al (m%)** - Calagem recomendada.")
    
    if areia > 600:
        recomendacoes_gerais.append("🏖️ **Solo arenoso** - Adubação parcelada (3-4 vezes).")
    elif argila > 400:
        recomendacoes_gerais.append("🧱 **Solo argiloso** - Maior retenção de nutrientes.")
    
    return recomendacoes_gerais

# ============================================================================
# ABA 1 - DADOS DO SOLO
# ============================================================================

if menu == "📊 1. Dados do Solo":
    st.markdown("## 📋 Dados Básicos do Solo")

    col1, col2 = st.columns(2)

    with col1:
        with st.container(border=True):
            st.subheader("📊 Parâmetros Químicos")
            nitrogen = st.text_input("🌱 Nitrogênio (mg/dm³)", value="30")
            phosphorus = st.text_input("🔴 Fósforo (mg/dm³)", value="20")
            potassium = st.text_input("🟡 Potássio (cmolc/dm³)", value="0.25")
            ph = st.text_input("🧪 pH (água)", value="6.0")

    with col2:
        with st.container(border=True):
            st.subheader("⚗️ Cátions e Acidez")
            aluminum = st.text_input("⚠️ Alumínio (cmolc/dm³)", value="0.5")
            calcium = st.text_input("🥛 Cálcio (cmolc/dm³)", value="3.0")
            magnesium = st.text_input("🧂 Magnésio (cmolc/dm³)", value="1.5")
            h_al = st.text_input("📊 H + Al (cmolc/dm³)", value="3.5")

    with st.container(border=True):
        st.subheader("🏞️ Textura do Solo")
        col3, col4, col5 = st.columns(3)
        with col3:
            sand = st.text_input("🏖️ Areia (g/kg)", value="350")
        with col4:
            silt = st.text_input("🏞️ Silte (g/kg)", value="300")
        with col5:
            clay = st.text_input("🧱 Argila (g/kg)", value="350")

    if st.button("✅ SALVAR DADOS", use_container_width=True):
        try:
            dados = {
                "nitrogen": float(nitrogen),
                "phosphorus": float(phosphorus),
                "potassium": float(potassium),
                "ph": float(ph),
                "aluminum": float(aluminum),
                "calcium": float(calcium),
                "magnesium": float(magnesium),
                "h_al": float(h_al),
                "sand": float(sand),
                "silt": float(silt),
                "clay": float(clay)
            }
            
            sb = calcular_sb(dados["calcium"], dados["magnesium"], dados["potassium"])
            ctc = calcular_tct_potencial(sb, dados["h_al"])
            v = calcular_v_porcentagem(sb, ctc)
            m = calcular_m_porcentagem(dados["aluminum"], sb)
            
            dados["sb"] = sb
            dados["ctc"] = ctc
            dados["v_porcentagem"] = v
            dados["m_porcentagem"] = m
            
            st.session_state.dados_basicos = dados
            
            st.success("✅ Dados salvos com sucesso!")
            
            st.markdown("### 📊 Resumo dos Cálculos")
            col_a, col_b, col_c, col_d = st.columns(4)
            with col_a:
                st.metric("SB (Soma de Bases)", f"{sb:.2f} cmolc/dm³")
            with col_b:
                st.metric("CTC (Potencial)", f"{ctc:.2f} cmolc/dm³")
            with col_c:
                st.metric("V% (Saturação)", f"{v:.1f}%")
            with col_d:
                st.metric("m% (Alumínio)", f"{m:.1f}%")
                
        except ValueError:
            st.error("❌ Erro: Verifique se todos os valores são números válidos!")

# ============================================================================
# ABA 2 - CLASSIFICAÇÃO
# ============================================================================

elif menu == "🌱 2. Classificação":
    st.markdown("## 🌱 Classificação e Recomendações")
    
    if not st.session_state.dados_basicos:
        st.warning("⚠️ Por favor, vá até a aba 'Dados do Solo' e insira as informações primeiro!")
    else:
        dados = st.session_state.dados_basicos
        
        st.markdown("### 📊 Dados Atuais do Solo")
        
        col_metric1, col_metric2, col_metric3, col_metric4, col_metric5, col_metric6 = st.columns(6)
        with col_metric1:
            st.metric("pH", f"{dados.get('ph', 'N/A')}")
        with col_metric2:
            st.metric("V%", f"{dados.get('v_porcentagem', 0):.1f}%")
        with col_metric3:
            st.metric("m%", f"{dados.get('m_porcentagem', 0):.1f}%")
        with col_metric4:
            st.metric("N", f"{dados.get('nitrogen', 'N/A')} mg/dm³")
        with col_metric5:
            st.metric("P", f"{dados.get('phosphorus', 'N/A')} mg/dm³")
        with col_metric6:
            st.metric("K", f"{dados.get('potassium', 'N/A')} cmolc/dm³")
        
        v = dados.get('v_porcentagem', 0)
        classificacao = classificar_fertilidade(v)
        st.info(f"📌 **Classificação:** {classificacao}")
        
        st.markdown("---")
        
        st.markdown("### 🌾 Selecione a Cultura")
        cultura = st.selectbox("Cultura planejada", list(necessidades_culturas.keys()))
        
        if cultura:
            req = necessidades_culturas[cultura]
            
            tab1, tab2, tab3, tab4 = st.tabs([
                "📋 Análise do Solo", 
                "🧪 Calagem", 
                "🌱 Adubação", 
                "📝 Manejo Geral"
            ])
            
            with tab1:
                st.markdown("#### ✅ Condições do Solo para a Cultura")
                
                ph_atual = dados.get('ph', 0)
                ph_ok = req['ph_min'] <= ph_atual <= req['ph_max']
                v_atual = dados.get('v_porcentagem', 0)
                v_ok = v_atual >= req['v_desejado']
                n_atual = dados.get('nitrogen', 0)
                n_ok = n_atual >= req['n_min']
                p_atual = dados.get('phosphorus', 0)
                p_ok = p_atual >= req['p_min']
                k_atual = dados.get('potassium', 0)
                k_ok = k_atual >= req['k_min']
                
                col_a, col_b = st.columns(2)
                
                with col_a:
                    with st.container(border=True):
                        st.markdown("**Parâmetros Químicos:**")
                        st.markdown(f"- **pH:** {ph_atual:.1f} (Ideal: {req['ph_min']}-{req['ph_max']}) → {'✅ OK' if ph_ok else '❌ Ajustar'}")
                        st.markdown(f"- **V%:** {v_atual:.1f}% (Desejado: ≥{req['v_desejado']}%) → {'✅ OK' if v_ok else '❌ Baixo'}")
                        st.markdown(f"- **m%:** {dados.get('m_porcentagem', 0):.1f}% → {'✅ OK' if dados.get('m_porcentagem', 0) < 15 else '⚠️ Atenção'}")
                
                with col_b:
                    with st.container(border=True):
                        st.markdown("**Nutrientes:**")
                        st.markdown(f"- **N:** {n_atual} mg/dm³ (Mínimo: {req['n_min']}) → {'✅ OK' if n_ok else '❌ Baixo'}")
                        st.markdown(f"- **P:** {p_atual} mg/dm³ (Mínimo: {req['p_min']}) → {'✅ OK' if p_ok else '❌ Baixo'}")
                        st.markdown(f"- **K:** {k_atual:.2f} cmolc/dm³ (Mínimo: {req['k_min']}) → {'✅ OK' if k_ok else '❌ Baixo'}")
            
            with tab2:
                st.markdown("#### 🧪 Recomendação de Calagem")
                
                ctc = dados.get('ctc', 0)
                v_atual = dados.get('v_porcentagem', 0)
                nc, rec_calagem = calcular_necessidade_calagem(v_atual, req['v_desejado'], ctc)
                
                st.info(f"**V% atual:** {v_atual:.1f}% | **V% desejado:** {req['v_desejado']}% | **CTC:** {ctc:.2f} cmolc/dm³")
                
                if nc > 0:
                    st.success(f"### {rec_calagem}")
                    with st.container(border=True):
                        st.markdown(f"""
                        **📋 Detalhamento:**
                        - Necessidade: {nc:.1f} t/ha
                        - PRNT considerado: 85%
                        - Época: 60-90 dias antes do plantio
                        """)
                else:
                    st.success(rec_calagem)
            
            with tab3:
                st.markdown("#### 🌱 Recomendação de Adubação")
                
                col_n, col_p, col_k = st.columns(3)
                
                with col_n:
                    with st.container(border=True):
                        st.markdown("**🥬 Nitrogênio (N)**")
                        rec_n = recomendar_adubacao_nitrogenio(cultura, n_atual, req['n_min'])
                        if "✅" in rec_n:
                            st.success(rec_n)
                        else:
                            st.error(rec_n)
                
                with col_p:
                    with st.container(border=True):
                        st.markdown("**🪨 Fósforo (P₂O₅)**")
                        rec_p = recomendar_adubacao_fosforo(cultura, p_atual, req['p_min'])
                        if "✅" in rec_p:
                            st.success(rec_p)
                        else:
                            st.error(rec_p)
                
                with col_k:
                    with st.container(border=True):
                        st.markdown("**🍌 Potássio (K₂O)**")
                        rec_k = recomendar_adubacao_potassio(cultura, k_atual, req['k_min'])
                        if "✅" in rec_k:
                            st.success(rec_k)
                        else:
                            st.error(rec_k)
            
            with tab4:
                st.markdown("#### 📝 Recomendações de Manejo Geral")
                
                recomendacoes_gerais = recomendar_manejo_geral(dados)
                
                if recomendacoes_gerais:
                    for rec in recomendacoes_gerais:
                        st.info(rec)
                else:
                    st.success("✅ Solo com boas condições físicas e químicas!")
                
                st.markdown("---")
                st.markdown(f"#### 🌟 Dica para {cultura}")
                st.info("Realize análise de solo anualmente para monitorar a fertilidade e ajustar as recomendações.")

# ============================================================================
# ABA 3 - IA
# ============================================================================

elif menu == "🤖 3. Assistente IA":
    st.markdown("## 🤖 Assistente IA Gemini")

    if not st.session_state.dados_basicos:
        st.info("ℹ️ Para melhores respostas, preencha os dados do solo na aba 'Dados do Solo' primeiro!")

    pergunta = st.text_area(
        "💬 Faça sua pergunta sobre fertilidade do solo, manejo ou culturas:",
        height=150,
        placeholder="Exemplo: Qual a recomendação de calagem para um solo com pH 5.0? Como interpretar o V%?"
    )

    if st.button("🚀 GERAR RESPOSTA", use_container_width=True):
        if not pergunta:
            st.warning("⚠️ Por favor, digite uma pergunta!")
        else:
            with st.spinner("🤖 Consultando IA Gemini..."):
                resposta = gerar_resposta_ia(
                    pergunta,
                    st.session_state.dados_basicos if st.session_state.dados_basicos else None
                )
                
                st.markdown(f"""
                <div class="result-card">
                    <h2 style="text-align: center;">🤖 Resposta da IA</h2>
                    <div style="margin-top: 20px;">
                        {resposta}
                    </div>
                </div>
                """, unsafe_allow_html=True)

# ============================================================================
# ABA 4 - RELATÓRIO
# ============================================================================

elif menu == "📈 4. Relatório":
    st.markdown("## 📈 Relatório Técnico")

    if st.session_state.dados_basicos:
        dados = st.session_state.dados_basicos
        
        relatorio_data = {
            "Parâmetro": [
                "Nitrogênio (N)", "Fósforo (P)", "Potássio (K)",
                "pH", "Alumínio (Al)", "Cálcio (Ca)", "Magnésio (Mg)",
                "H + Al", "Areia", "Silte", "Argila",
                "Soma de Bases (SB)", "CTC Potencial", "V (%)", "m (%)"
            ],
            "Valor": [
                f"{dados.get('nitrogen', 'N/A')} mg/dm³",
                f"{dados.get('phosphorus', 'N/A')} mg/dm³",
                f"{dados.get('potassium', 'N/A')} cmolc/dm³",
                f"{dados.get('ph', 'N/A')}",
                f"{dados.get('aluminum', 'N/A')} cmolc/dm³",
                f"{dados.get('calcium', 'N/A')} cmolc/dm³",
                f"{dados.get('magnesium', 'N/A')} cmolc/dm³",
                f"{dados.get('h_al', 'N/A')} cmolc/dm³",
                f"{dados.get('sand', 'N/A')} g/kg",
                f"{dados.get('silt', 'N/A')} g/kg",
                f"{dados.get('clay', 'N/A')} g/kg",
                f"{dados.get('sb', 0):.2f} cmolc/dm³",
                f"{dados.get('ctc', 0):.2f} cmolc/dm³",
                f"{dados.get('v_porcentagem', 0):.1f}%",
                f"{dados.get('m_porcentagem', 0):.1f}%"
            ]
        }
        
        relatorio = pd.DataFrame(relatorio_data)
        
        st.dataframe(relatorio, use_container_width=True, hide_index=True)
        
        csv = relatorio.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Baixar Relatório (CSV)",
            data=csv,
            file_name="relatorio_solo.csv",
            mime="text/csv"
        )
    else:
        st.info("ℹ️ Nenhum dado cadastrado. Vá até a aba 'Dados do Solo' para inserir as informações.")

# ============================================================================
# ABA 5 - MÉTODOS
# ============================================================================

elif menu == "ℹ️ 5. Métodos":
    st.markdown("## ℹ️ Métodos Utilizados")
    
    with st.container(border=True):
        st.markdown("""
        ### 📐 Fórmulas e Interpretações
        
        | Parâmetro | Fórmula | Interpretação |
        |-----------|---------|---------------|
        | **Soma de Bases (SB)** | SB = Ca²⁺ + Mg²⁺ + K⁺ (cmolc/dm³) | Indica a quantidade de cátions básicos |
        | **CTC Potencial (T)** | T = SB + (H+Al) (cmolc/dm³) | Capacidade máxima de troca catiônica |
        | **Saturação por Bases (V%)** | V% = (SB/T) × 100 | Fertilidade do solo |
        | **Saturação por Alumínio (m%)** | m% = (Al³⁺ / (Al³⁺ + SB)) × 100 | Toxicidade por alumínio |
        """)
    
    with st.container(border=True):
        st.markdown("""
        ### 🌡️ Classificação do V%
        
        - **V% < 50%** → Baixa fertilidade (solos ácidos)
        - **50% ≤ V% < 70%** → Fertilidade média
        - **70% ≤ V% < 85%** → Fertilidade boa
        - **V% ≥ 85%** → Fertilidade muito boa
        """)
    
    with st.container(border=True):
        st.markdown("""
        ### 🧪 pH e Disponibilidade de Nutrientes
        
        - **pH < 5.5** → Alumínio tóxico, baixa disponibilidade de P, Ca, Mg
        - **pH 5.5 - 6.5** → Faixa ideal para maioria das culturas
        - **pH > 6.5** → Pode reduzir disponibilidade de micronutrientes
        """)
    
    with st.container(border=True):
        st.markdown("""
        ### 📚 Referências
        
        - SiBCS - Sistema Brasileiro de Classificação de Solos (Embrapa)
        - Manual de Adubação e Calagem (CONAB)
        - Recomendações técnicas para as principais culturas
        """)
    
    st.markdown("---")
    st.markdown("### 🤖 IA Gemini")
    st.markdown("""
    O assistente utiliza o modelo **Gemini** do Google para:
    - Interpretar laudos de análise de solo
    - Recomendar práticas de manejo
    - Sugerir correções de fertilidade
    - Esclarecer dúvidas sobre nutrição de plantas
    """)

# ============================================================================
# RODAPÉ
# ============================================================================

st.markdown("---")

col_rodape1, col_rodape2, col_rodape3 = st.columns([1, 2, 1])
with col_rodape2:
    st.caption("© 2026 - Sistema Inteligente de Fertilidade do Solo | Baseado em metodologias Embrapa")
    st.caption("📧 Contato: [solo@pesquisa.agr.br](mailto:solo@pesquisa.agr.br)")
