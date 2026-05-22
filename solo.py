# ============================================================================
# IMPORTAÇÕES
# ============================================================================

import streamlit as st
import pandas as pd
import requests
import json
import time

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

GEMINI_API_KEY = "AIzaSyAkj0m6HFJxX9hGNopoUiUxWDgPJrMkQww"  # ← INSIRA SUA CHAVE AQUI!

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
# CSS PERSONALIZADO - CORRIGIDO (INPUTS COM TEXTO VISÍVEL)
# ============================================================================

st.markdown("""
<style>
    /* ========== RESET E FONTES ========== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,300;14..32,400;14..32,500;14..32,600;14..32,700&display=swap');
    
    * {
        font-family: 'Inter', 'Segoe UI', sans-serif !important;
    }
    
    /* ========== FUNDO PRINCIPAL ========== */
    .stApp {
        background: radial-gradient(circle at 20% 30%, #0a0f1e, #05070f);
        color: #ffffff;
    }
    
    /* ========== SIDEBAR MAIS COMPACTA ========== */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(10,15,30,0.98) 0%, rgba(5,7,15,0.98) 100%);
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(46,204,113,0.2);
        box-shadow: 4px 0 30px rgba(0,0,0,0.3);
        min-width: 280px;
    }
    
    /* ========== TÍTULOS ========== */
    h1, h2, h3, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        background: linear-gradient(135deg, #2ecc71, #27ae60);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
    }
    
    h1 {
        font-size: 2.2rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    h2 {
        font-size: 1.5rem !important;
        margin-top: 0.5rem !important;
    }
    
    /* ========== TEXTO GERAL ========== */
    p, span, div, label, .stMarkdown, .stText, .stCaption {
        color: #e2e8f0 !important;
        line-height: 1.5;
    }
    
    /* ========== INPUTS CORRIGIDOS - TEXTO PRETO VISÍVEL ========== */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stDateInput > div > div > input {
        background: rgba(255,255,255,0.9) !important;
        border: 1px solid rgba(46,204,113,0.4) !important;
        border-radius: 12px !important;
        padding: 10px 14px !important;
        color: #1a1a2e !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #2ecc71 !important;
        box-shadow: 0 0 0 2px rgba(46,204,113,0.3) !important;
        outline: none !important;
    }
    
    /* Placeholder mais claro */
    .stTextInput > div > div > input::placeholder {
        color: #666 !important;
    }
    
        /* Selectbox corrigido - FUNDO ESCURO COM TEXTO BRANCO */
    .stSelectbox > div > div {
        background: rgba(20, 20, 40, 0.95) !important;
        border: 1px solid rgba(46,204,113,0.4) !important;
        border-radius: 12px !important;
        color: white !important;
    }
    
    .stSelectbox > div > div > div {
        color: white !important;
    }
    
    .stSelectbox > div > div > div[role="combobox"] {
        color: white !important;
    }
    
    /* Opções do dropdown (lista suspensa) */
    div[data-baseweb="select"] > div {
        background: rgba(20, 20, 40, 0.98) !important;
        backdrop-filter: blur(10px);
    }
    
    div[data-baseweb="select"] ul {
        background: rgba(15, 15, 30, 0.98) !important;
    }
    
    div[data-baseweb="select"] li {
        color: white !important;
        background: transparent !important;
    }
    
    div[data-baseweb="select"] li:hover {
        background: rgba(46,204,113,0.2) !important;
    }
    
    div[data-baseweb="select"] li[aria-selected="true"] {
        background: rgba(46,204,113,0.3) !important;
        color: #2ecc71 !important;
    }
    
    .stSelectbox label {
        color: #e2e8f0 !important;
    }
    
    /* ========== BOTÕES COM ANIMAÇÃO E TEXTO CLARO ========== */
    .stButton button {
        background: linear-gradient(135deg, #1e8f4a, #2ecc71);
        border: none;
        border-radius: 40px;
        padding: 12px 24px;
        font-weight: 600;
        font-size: 15px;
        color: white !important;
        transition: all 0.3s cubic-bezier(0.2, 0.9, 0.4, 1.1);
        cursor: pointer;
        box-shadow: 0 4px 15px rgba(46,204,113,0.3);
        width: 100%;
    }
    
    .stButton button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(46,204,113,0.4);
        background: linear-gradient(135deg, #2ecc71, #27ae60);
    }
    
    .stButton button:active {
        transform: translateY(2px);
    }
    
    /* ========== CARDS MAIS COMPACTOS ========== */
    .stContainer, .element-container:has(.stExpander), div[data-testid="stExpander"] {
        background: rgba(255,255,255,0.05);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        border: 1px solid rgba(255,255,255,0.08);
        margin-bottom: 0.8rem;
        transition: all 0.3s ease;
    }
    
    /* Expander header */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, rgba(46,204,113,0.15), rgba(46,204,113,0.05));
        border-radius: 20px;
        font-weight: 600;
        color: #2ecc71 !important;
        padding: 12px 16px;
    }
    
    /* ========== MÉTRICAS BONITAS ========== */
    .metric-card {
        background: linear-gradient(145deg, rgba(255,255,255,0.08), rgba(255,255,255,0.03));
        border-radius: 16px;
        padding: 0.8rem;
        text-align: center;
        border: 1px solid rgba(46,204,113,0.3);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-3px);
        border-color: rgba(46,204,113,0.6);
    }
    
    /* ========== TABS MODERNAS ========== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255,255,255,0.03);
        padding: 4px;
        border-radius: 50px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 40px;
        padding: 8px 16px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #1e8f4a, #2ecc71);
        color: white !important;
    }
    
    /* ========== RESULT CARD ========== */
    .result-card {
        background: linear-gradient(145deg, rgba(46,204,113,0.12), rgba(255,255,255,0.04));
        border: 1px solid rgba(46,204,113,0.4);
        border-radius: 20px;
        padding: 1.5rem;
        margin-top: 1rem;
    }
    
    /* ========== DIAGNÓSTICO CARD ========== */
    .diagnostico-card {
        background: linear-gradient(135deg, rgba(46,204,113,0.1), rgba(46,204,113,0.05));
        border-left: 4px solid #2ecc71;
        border-radius: 16px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    /* ========== ANIMAÇÕES ========== */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeInUp 0.4s ease;
    }
    
    /* ========== SCROLLBAR ========== */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255,255,255,0.05);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #2ecc71, #1e8f4a);
        border-radius: 10px;
    }
    
    /* ========== DATA FRAME ========== */
    .stDataFrame, .stTable {
        background: rgba(255,255,255,0.03);
        border-radius: 16px;
        overflow: hidden;
    }
    
    /* ========== ALERTAS ========== */
    .stAlert {
        border-radius: 16px;
        border-left: 4px solid #2ecc71;
        background: rgba(46,204,113,0.1);
    }
    
    /* ========== HERO BANNER MAIS COMPACTO ========== */
    .hero-banner {
        background: linear-gradient(135deg, rgba(46,204,113,0.12), rgba(46,204,113,0.04));
        border: 1px solid rgba(46,204,113,0.3);
        border-radius: 24px;
        padding: 1rem;
        text-align: center;
        margin-bottom: 1rem;
        backdrop-filter: blur(10px);
    }
    
    .hero-banner h1 {
        font-size: 1.8rem;
        margin-bottom: 0.25rem;
    }
    
    .hero-banner p {
        font-size: 0.9rem;
        opacity: 0.8;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# CABEÇALHO HERO - MAIS COMPACTO
# ============================================================================

st.markdown("""
<div class="hero-banner">
    <h1>🌾 Classificador Inteligente de Fertilidade do Solo</h1>
    <p>Sistema baseado no SiBCS - Embrapa e Integração com IA Gemini</p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# SIDEBAR - MENU MAIS LIMPO
# ============================================================================

with st.sidebar:
    st.image(
        "https://cdn-icons-png.flaticon.com/512/2909/2909763.png",
        width=70
    )
    
    st.markdown("### 🌱 Sistema Inteligente")
    st.markdown("""
    • Avaliação da fertilidade  
    • Cálculo de V% e m%  
    • Classificação SiBCS  
    • Relatório técnico  
    • IA Gemini integrada  
    """)
    
    st.markdown("---")
    
    if st.button("🔧 Testar Conexão API", use_container_width=True):
        with st.spinner("Testando..."):
            modelos = listar_modelos_disponiveis()
            if modelos:
                st.success(f"✅ API conectada!")
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
# MENU HORIZONTAL MAIS COMPACTO
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
# FUNÇÃO PARA GERAR DIAGNÓSTICO AMIGÁVEL
# ============================================================================

def gerar_diagnostico(dados, cultura_req):
    """Gera um diagnóstico amigável para o usuário"""
    diagnostico = []
    
    ph_atual = dados.get('ph', 0)
    if ph_atual < cultura_req['ph_min']:
        diagnostico.append(f"🔴 **pH ácido:** {ph_atual:.1f} (ideal: {cultura_req['ph_min']}-{cultura_req['ph_max']}). A calagem ajudará a corrigir.")
    elif ph_atual > cultura_req['ph_max']:
        diagnostico.append(f"🟡 **pH alcalino:** {ph_atual:.1f} (ideal: {cultura_req['ph_min']}-{cultura_req['ph_max']}). Pode afetar disponibilidade de nutrientes.")
    else:
        diagnostico.append(f"🟢 **pH adequado:** {ph_atual:.1f} dentro da faixa ideal.")
    
    v_atual = dados.get('v_porcentagem', 0)
    if v_atual < cultura_req['v_desejado']:
        diagnostico.append(f"🔴 **Saturação por bases baixa:** {v_atual:.1f}% (ideal: ≥{cultura_req['v_desejado']}%). Solo precisa de calagem.")
    else:
        diagnostico.append(f"🟢 **Saturação por bases adequada:** {v_atual:.1f}% (ideal: ≥{cultura_req['v_desejado']}%).")
    
    n_atual = dados.get('nitrogen', 0)
    if n_atual < cultura_req['n_min']:
        diagnostico.append(f"🔴 **Nitrogênio baixo:** {n_atual} mg/dm³ (mínimo: {cultura_req['n_min']}). Adubação nitrogenada necessária.")
    else:
        diagnostico.append(f"🟢 **Nitrogênio adequado:** {n_atual} mg/dm³.")
    
    p_atual = dados.get('phosphorus', 0)
    if p_atual < cultura_req['p_min']:
        diagnostico.append(f"🔴 **Fósforo baixo:** {p_atual} mg/dm³ (mínimo: {cultura_req['p_min']}). Adubação fosfatada necessária.")
    else:
        diagnostico.append(f"🟢 **Fósforo adequado:** {p_atual} mg/dm³.")
    
    k_atual = dados.get('potassium', 0)
    if k_atual < cultura_req['k_min']:
        diagnostico.append(f"🔴 **Potássio baixo:** {k_atual:.2f} cmolc/dm³ (mínimo: {cultura_req['k_min']}). Adubação potássica necessária.")
    else:
        diagnostico.append(f"🟢 **Potássio adequado:** {k_atual:.2f} cmolc/dm³.")
    
    return diagnostico

# ============================================================================
# FUNÇÕES DE RECOMENDAÇÃO DE ADUBAÇÃO E CALAGEM
# ============================================================================

def calcular_necessidade_calagem(v_atual, v_desejado, ctc, prnt=85):
    """Calcula a necessidade de calagem em t/ha com PRNT personalizável"""
    if v_atual >= v_desejado:
        return 0, "✅ Solo já atingiu V% desejado. Não necessita calagem.", 0
    
    f = 100 / prnt
    nc = (ctc * (v_desejado - v_atual) / 100) * f
    nc = round(nc * 2) / 2
    
    if nc <= 1.0:
        tempo_espera = 30
    elif nc <= 2.0:
        tempo_espera = 45
    elif nc <= 4.0:
        tempo_espera = 60
    else:
        tempo_espera = 90
    
    if nc > 0:
        recomendacao = f"🔹 **Calagem necessária:** {nc:.1f} t/ha de calcário (PRNT {prnt}%)"
        if nc > 5:
            recomendacao += " - Aplicar parcelado em 2 anos"
        return nc, recomendacao, tempo_espera
    else:
        return 0, "Calagem não necessária", 0

def recomendar_adubacao_nitrogenio(cultura, n_atual, n_min):
    if n_atual >= n_min:
        return "✅ N adequado. Adubação de manutenção: 30-50 kg/ha de N"
    
    deficiencia = n_min - n_atual
    
    if cultura in ["Tomate", "Alface", "Batata", "Milho Semente"]:
        kg_ha = deficiencia + 60
        recomendacao = f"Alta demanda. Aplicar {kg_ha:.0f} kg/ha de N"
    elif cultura in ["Café", "Cana-de-açúcar", "Milho Grão"]:
        kg_ha = deficiencia + 40
        recomendacao = f"Média demanda. Aplicar {kg_ha:.0f} kg/ha de N"
    else:
        kg_ha = deficiencia + 20
        recomendacao = f"Baixa demanda. Aplicar {kg_ha:.0f} kg/ha de N"
    
    return f"❌ N baixo ({n_atual} < {n_min}). {recomendacao}"

def recomendar_adubacao_fosforo(cultura, p_atual, p_min):
    if p_atual >= p_min:
        return "✅ P adequado. Adubação de manutenção: 40-80 kg/ha de P2O5"
    
    deficiencia = p_min - p_atual
    
    if cultura in ["Tomate", "Batata", "Soja"]:
        kg_ha = deficiencia + 80
        recomendacao = f"Alta demanda. Aplicar {kg_ha:.0f} kg/ha de P2O5"
    elif cultura in ["Café", "Cana-de-açúcar"]:
        kg_ha = deficiencia + 60
        recomendacao = f"Média demanda. Aplicar {kg_ha:.0f} kg/ha de P2O5"
    else:
        kg_ha = deficiencia + 40
        recomendacao = f"Baixa demanda. Aplicar {kg_ha:.0f} kg/ha de P2O5"
    
    return f"❌ P baixo ({p_atual} < {p_min}). {recomendacao}"

def recomendar_adubacao_potassio(cultura, k_atual, k_min):
    if k_atual >= k_min:
        return "✅ K adequado. Adubação de manutenção: 40-60 kg/ha de K2O"
    
    deficiencia = k_min - k_atual
    
    if cultura in ["Tomate", "Batata", "Café", "Cana-de-açúcar"]:
        kg_ha = deficiencia + 60
        recomendacao = f"Alta demanda. Aplicar {kg_ha:.0f} kg/ha de K2O"
    elif cultura in ["Soja", "Milho Grão", "Algodão"]:
        kg_ha = deficiencia + 40
        recomendacao = f"Média demanda. Aplicar {kg_ha:.0f} kg/ha de K2O"
    else:
        kg_ha = deficiencia + 30
        recomendacao = f"Baixa demanda. Aplicar {kg_ha:.0f} kg/ha de K2O"
    
    return f"❌ K baixo ({k_atual:.2f} < {k_min:.2f}). {recomendacao}"

# ============================================================================
# ABA 1 - DADOS DO SOLO (CAMPOS MAIS COMPACTOS)
# ============================================================================

if menu == "📊 1. Dados do Solo":
    st.markdown("### 📋 Dados Básicos do Solo")
    st.caption("Preencha os campos abaixo com os resultados da análise de solo")

    col1, col2 = st.columns(2)

    with col1:
        with st.container(border=True):
            st.markdown("**📊 Parâmetros Químicos**")
            nitrogen = st.text_input("🌱 Nitrogênio (mg/dm³)", value="30")
            phosphorus = st.text_input("🔴 Fósforo (mg/dm³)", value="20")
            potassium = st.text_input("🟡 Potássio (cmolc/dm³)", value="0.25")
            ph = st.text_input("🧪 pH (água)", value="6.0")

    with col2:
        with st.container(border=True):
            st.markdown("**⚗️ Cátions e Acidez**")
            aluminum = st.text_input("⚠️ Alumínio (cmolc/dm³)", value="0.5")
            calcium = st.text_input("🥛 Cálcio (cmolc/dm³)", value="3.0")
            magnesium = st.text_input("🧂 Magnésio (cmolc/dm³)", value="1.5")
            h_al = st.text_input("📊 H + Al (cmolc/dm³)", value="3.5")

    with st.container(border=True):
        st.markdown("**🏞️ Textura do Solo**")
        st.caption("⚠️ A soma de Areia + Silte + Argila deve ser igual a 100%")
        col3, col4, col5 = st.columns(3)
        with col3:
            sand = st.number_input("🏖️ Areia (%)", min_value=0, max_value=100, value=35, step=5)
        with col4:
            silt = st.number_input("🏞️ Silte (%)", min_value=0, max_value=100, value=30, step=5)
        with col5:
            clay = st.number_input("🧱 Argila (%)", min_value=0, max_value=100, value=35, step=5)
        
        # Validação da soma da textura
        soma_textura = sand + silt + clay
        if soma_textura != 100:
            st.warning(f"⚠️ **Atenção:** A soma das frações é {soma_textura}%. O ideal é 100%. Ajuste os valores.")
        else:
            st.success(f"✅ Textura válida! Areia: {sand}%, Silte: {silt}%, Argila: {clay}%")
    
    st.caption("💡 Após salvar os dados, vá para a aba 'Classificação' para ver as recomendações.")

    if st.button("✅ SALVAR DADOS", use_container_width=True):
        # Verificar textura antes de salvar
        soma_textura = sand + silt + clay
        if soma_textura != 100:
            st.error(f"❌ **Erro na textura do solo:** A soma das frações é {soma_textura}%, mas deve ser exatamente 100%. Corrija os valores antes de salvar.")
        else:
            with st.spinner("💾 Salvando e processando dados..."):
                time.sleep(0.5)
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
                        "sand": sand,
                        "silt": silt,
                        "clay": clay
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
                    
                    st.success("✅ Dados salvos com sucesso! Vá para a aba **Classificação**.")
                    
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
# ABA 2 - CLASSIFICAÇÃO (CORRIGIDA - COM INTERAÇÃO E DIAGNÓSTICO)
# ============================================================================

elif menu == "🌱 2. Classificação":
    st.markdown("### 🌱 Classificação e Recomendações")
    
    if not st.session_state.dados_basicos:
        st.warning("⚠️ Por favor, vá até a aba 'Dados do Solo' e insira as informações primeiro!")
    else:
        dados = st.session_state.dados_basicos
        
        # Métricas principais
        col_metric1, col_metric2, col_metric3, col_metric4, col_metric5 = st.columns(5)
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
        
        # Exibir textura do solo
        st.info(f"🏞️ **Textura do solo:** Areia: {dados.get('sand', 0)}% | Silte: {dados.get('silt', 0)}% | Argila: {dados.get('clay', 0)}%")
        
        v = dados.get('v_porcentagem', 0)
        classificacao = classificar_fertilidade(v)
        st.info(f"📌 **Classificação geral do solo:** {classificacao}")
        
        st.markdown("---")
        
        st.markdown("### 🌾 Selecione a Cultura")
        cultura = st.selectbox("Cultura planejada", list(necessidades_culturas.keys()))
        
        if cultura:
            req = necessidades_culturas[cultura]
            
            # ========== DIAGNÓSTICO AMIGÁVEL ==========
            st.markdown("### 📋 Diagnóstico do Solo para a Cultura Selecionada")
            diagnostico = gerar_diagnostico(dados, req)
            
            with st.container(border=True):
                for diag in diagnostico:
                    st.markdown(diag)
            
            st.markdown("---")
            
            # TABS CORRIGIDAS (CALAGEM, ADUBAÇÃO, MANEJO FUNCIONANDO)
            tab1, tab2, tab3 = st.tabs(["🧪 Calagem", "🌱 Adubação", "📝 Manejo Geral"])
            
                        with tab1:
                st.markdown("#### 🧪 Recomendação de Calagem")
                
                ctc = dados.get('ctc', 0)
                v_atual = dados.get('v_porcentagem', 0)
                
                col_prnt1, col_prnt2 = st.columns([2, 1])
                with col_prnt1:
                    prnt_calcario = st.slider(
                        "PRNT do Calcário (%)", 
                        min_value=50, 
                        max_value=100, 
                        value=85, 
                        step=5,
                        help="Poder Relativo de Neutralização Total. Quanto menor o PRNT, maior a quantidade necessária."
                    )
                with col_prnt2:
                    st.metric("Fator de correção", f"{100/prnt_calcario:.2f}")
                
                nc, rec_calagem, tempo_espera = calcular_necessidade_calagem(v_atual, req['v_desejado'], ctc, prnt_calcario)
                
                st.info(f"**V% atual:** {v_atual:.1f}% | **V% desejado:** {req['v_desejado']}% | **CTC:** {ctc:.2f} cmolc/dm³")
                
                if nc > 0:
                    st.success(f"### {rec_calagem}")
                    
                    # Detalhamento da Calagem em container separado
                    st.markdown("**📋 Detalhamento da Calagem:**")
                    col_det1, col_det2, col_det3 = st.columns(3)
                    with col_det1:
                        st.metric("Necessidade", f"{nc:.1f} t/ha de calcário")
                    with col_det2:
                        st.metric("PRNT considerado", f"{prnt_calcario}%")
                    with col_det3:
                        st.metric("Tempo de espera mínimo", f"{tempo_espera} dias")
                    
                    # Tabela de tempo de espera em expander separado, sem elementos conflitantes
                    st.markdown("---")
                    with st.expander("⏰ Ver tabela de tempo de espera por dose"):
                        st.markdown("""
                        | Dose de calcário (t/ha) | Tempo de espera mínimo |
                        |------------------------|----------------------|
                        | Até 1.0 t/ha | 30 dias |
                        | 1.1 - 2.0 t/ha | 45 dias |
                        | 2.1 - 4.0 t/ha | 60 dias |
                        | Acima de 4.0 t/ha | 90 dias (parcelar) |
                        """)
                else:
                    st.success(rec_calagem)
            
            with tab2:
                st.markdown("#### 🌱 Recomendação de Adubação")
                
                with st.container(border=True):
                    st.markdown("**Nitrogênio (N)**")
                    n_atual = dados.get('nitrogen', 0)
                    st.info(recomendar_adubacao_nitrogenio(cultura, n_atual, req['n_min']))
                
                with st.container(border=True):
                    st.markdown("**Fósforo (P)**")
                    p_atual = dados.get('phosphorus', 0)
                    st.info(recomendar_adubacao_fosforo(cultura, p_atual, req['p_min']))
                
                with st.container(border=True):
                    st.markdown("**Potássio (K)**")
                    k_atual = dados.get('potassium', 0)
                    st.info(recomendar_adubacao_potassio(cultura, k_atual, req['k_min']))
            
            with tab3:
                st.markdown("#### 📝 Manejo Geral Recomendado")
                
                with st.container(border=True):
                    st.markdown("**🔧 Práticas de manejo sugeridas:**")
                    
                    if v_atual < req['v_desejado']:
                        st.markdown("- ✅ Realizar calagem conforme recomendação acima")
                    
                    if dados.get('ph', 0) < 5.5:
                        st.markdown("- ✅ Corrigir acidez do solo com calcário")
                    
                    if dados.get('m_porcentagem', 0) > 15:
                        st.markdown("- ✅ Atenção à toxicidade por alumínio")
                    
                    st.markdown("- ✅ Realizar análise de solo anualmente")
                    st.markdown("- ✅ Manter cobertura morta para conservação da umidade")
                    st.markdown("- ✅ Rotacionar culturas para evitar exaustão do solo")
                    st.markdown("- ✅ Utilizar adubos verdes (crotalária, mucuna) para recuperação")
                
                with st.container(border=True):
                    st.markdown("**📅 Época de aplicação:**")
                    st.markdown("- Calcário: Aplicar 60-90 dias antes do plantio")
                    st.markdown("- Adubo orgânico: Aplicar 30 dias antes do plantio")
                    st.markdown("- Adubo químico: Aplicar no plantio e em cobertura conforme cultura")

# ============================================================================
# ABA 3 - IA
# ============================================================================

elif menu == "🤖 3. Assistente IA":
    st.markdown("### 🤖 Assistente IA Gemini")
    st.caption("Faça perguntas sobre fertilidade do solo, manejo, culturas e práticas agrícolas")

    if not st.session_state.dados_basicos:
        st.info("ℹ️ Para melhores respostas, preencha os dados do solo na aba 'Dados do Solo' primeiro!")

    pergunta = st.text_area(
        "💬 Faça sua pergunta sobre fertilidade do solo, manejo ou culturas:",
        height=100,
        placeholder="Exemplo: Qual a recomendação de calagem para um solo com pH 5.0? Como interpretar o V%?"
    )

    if st.button("🚀 GERAR RESPOSTA", use_container_width=True):
        if not pergunta:
            st.warning("⚠️ Por favor, digite uma pergunta!")
        else:
            with st.spinner("🤖 Consultando IA Gemini. Analisando seus dados..."):
                resposta = gerar_resposta_ia(
                    pergunta,
                    st.session_state.dados_basicos if st.session_state.dados_basicos else None
                )
                
                st.markdown(f"""
                <div class="result-card">
                    <h3 style="text-align: center; margin-bottom: 1rem;">🤖 Resposta da IA</h3>
                    <div style="margin-top: 10px;">
                        {resposta}
                    </div>
                </div>
                """, unsafe_allow_html=True)

# ============================================================================
# ABA 4 - RELATÓRIO
# ============================================================================

elif menu == "📈 4. Relatório":
    st.markdown("### 📈 Relatório Técnico")

    if st.session_state.dados_basicos:
        dados = st.session_state.dados_basicos
        
        relatorio_data = {
            "Parâmetro": [
                "Nitrogênio (N)", "Fósforo (P)", "Potássio (K)",
                "pH", "Alumínio (Al)", "Cálcio (Ca)", "Magnésio (Mg)",
                "H + Al", "Areia (%)", "Silte (%)", "Argila (%)",
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
                f"{dados.get('sand', 'N/A')}%",
                f"{dados.get('silt', 'N/A')}%",
                f"{dados.get('clay', 'N/A')}%",
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
    st.markdown("### ℹ️ Métodos Utilizados")
    
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
    st.caption("© 2026 - Sistema Inteligente de Fertilidade do Solo | Fins Acadêmicos")
    st.caption("🤖 IA Gemini do Google • 🌱 Metodologias Embrapa • 📊 SiBCS")
    st.caption("📧 Contato: [laenor@outlook.com](mailto:laenor@outlook.com)")
