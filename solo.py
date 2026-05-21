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
# FUNÇÃO IA GEMINI - VERSÃO CORRIGIDA
# ============================================================================

def gerar_resposta_ia(pergunta, dados_solo=None):
    """Função corrigida com detecção automática do modelo"""
    
    # Verificar se a chave é válida
    if not GEMINI_API_KEY or GEMINI_API_KEY == "SUA_API_KEY_AQUI":
        return "⚠️ **API Key não configurada!** Configure sua chave no código."
    
    try:
        # Obter modelo disponível
        modelos = listar_modelos_disponiveis()
        
        if not modelos:
            return "❌ **Nenhum modelo Gemini disponível!** Verifique sua API Key."
        
        # Escolher o primeiro modelo disponível (geralmente gemini-1.5-flash)
        modelo = modelos[0]
        
        # Preparar contexto dos dados do solo
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
            - CTC Potencial: {dados_solo.get('tct', 0):.2f} cmolc/dm³
            """
        
        # Construir o prompt completo
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
        
        # URL com o modelo correto
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent?key={GEMINI_API_KEY}"
        
        # Headers da requisição
        headers = {
            "Content-Type": "application/json"
        }
        
        # Corpo da requisição
        data = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ]
        }
        
        # Fazer a requisição
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        # Verificar resposta
        if response.status_code == 200:
            resultado = response.json()
            
            # Extrair a resposta de forma segura
            if "candidates" in resultado and len(resultado["candidates"]) > 0:
                candidate = resultado["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    if len(candidate["content"]["parts"]) > 0:
                        resposta = candidate["content"]["parts"][0].get("text", "")
                        return resposta
            
            return "❌ Não foi possível extrair a resposta da IA."
        
        elif response.status_code == 401:
            return "❌ **Erro de autenticação (401):** API Key inválida. Verifique sua chave."
        
        elif response.status_code == 403:
            return "❌ **Acesso negado (403):** Ative a API Gemini no Google Cloud Console."
        
        elif response.status_code == 429:
            return "❌ **Limite excedido (429):** Muitas requisições. Aguarde alguns minutos."
        
        else:
            erro_detalhado = ""
            try:
                erro_json = response.json()
                erro_detalhado = erro_json.get('error', {}).get('message', 'Erro desconhecido')
            except:
                erro_detalhado = response.text[:200]
            
            return f"❌ **Erro {response.status_code}:** {erro_detalhado}"
    
    except requests.exceptions.Timeout:
        return "⏰ **Tempo limite excedido!** A API demorou muito para responder. Tente novamente."
    
    except requests.exceptions.ConnectionError:
        return "🌐 **Erro de conexão!** Verifique sua internet e tente novamente."
    
    except Exception as erro:
        return f"❌ **Erro inesperado:** {str(erro)}"

# ============================================================================
# CSS PERSONALIZADO MODERNO
# ============================================================================

st.markdown("""
<style>
    * {
        font-family: 'Segoe UI', sans-serif !important;
    }

    .stApp {
        background: linear-gradient(135deg, #050505, #0f172a);
        color: white;
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #071019, #0f172a);
        border-right: 1px solid rgba(46,204,113,0.3);
    }

    h1, h2, h3, h4, h5, h6 {
        color: #2ecc71 !important;
        font-weight: 700 !important;
    }

    p, span, div, label {
        color: #f5f5f5 !important;
    }

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

    .result-card {
        background: linear-gradient(145deg, rgba(34,197,94,0.12), rgba(255,255,255,0.04));
        border: 1px solid rgba(46,204,113,0.4);
        border-radius: 22px;
        padding: 2rem;
        text-align: left;
        margin-top: 1rem;
    }

    .hero {
        background: linear-gradient(135deg, rgba(34,197,94,0.2), rgba(59,130,246,0.15));
        border: 1px solid rgba(255,255,255,0.08);
        padding: 2rem;
        border-radius: 28px;
        text-align: center;
        margin-bottom: 2rem;
        backdrop-filter: blur(10px);
    }
    
    .hero h1 {
        color: white !important;
    }
    
    .hero p {
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# CABEÇALHO
# ============================================================================

st.markdown("""
<div class="hero">
    <h1>🌾 Classificador Inteligente de Fertilidade do Solo</h1>
    <p style="font-size:1.2rem;">
        Sistema Inteligente baseado no SiBCS - Embrapa
    </p>
    <p>
        📊 Análise • 🤖 IA Gemini • 🌱 Fertilidade • 📈 Relatórios
    </p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.image(
        "https://cdn-icons-png.flaticon.com/512/2909/2909763.png",
        width=110
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
    
    # Botão para testar a API
    if st.button("🔧 Testar Conexão API"):
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
# CULTURAS (EM ORDEM ALFABÉTICA)
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
# ABA 1 - DADOS DO SOLO
# ============================================================================

if menu == "📊 1. Dados do Solo":
    st.markdown("## 📋 Dados Básicos do Solo")

    col1, col2 = st.columns(2)

    with col1:
        nitrogen = st.text_input("🌱 Nitrogênio (mg/dm³)", value="30")
        phosphorus = st.text_input("🔴 Fósforo (mg/dm³)", value="20")
        potassium = st.text_input("🟡 Potássio (cmolc/dm³)", value="0.25")
        ph = st.text_input("🧪 pH (água)", value="6.0")

    with col2:
        aluminum = st.text_input("⚠️ Alumínio (cmolc/dm³)", value="0.5")
        calcium = st.text_input("🥛 Cálcio (cmolc/dm³)", value="3.0")
        magnesium = st.text_input("🧂 Magnésio (cmolc/dm³)", value="1.5")
        h_al = st.text_input("📊 H + Al (cmolc/dm³)", value="3.5")

    col3, col4 = st.columns(2)
    with col3:
        sand = st.text_input("🏖️ Areia (g/kg)", value="350")
    with col4:
        silt = st.text_input("🏞️ Silte (g/kg)", value="300")
        clay = st.text_input("🧱 Argila (g/kg)", value="350")

    if st.button("✅ SALVAR DADOS"):
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
            tct = calcular_tct_potencial(sb, dados["h_al"])
            v = calcular_v_porcentagem(sb, tct)
            m = calcular_m_porcentagem(dados["aluminum"], sb)
            
            dados["sb"] = sb
            dados["tct"] = tct
            dados["v_porcentagem"] = v
            dados["m_porcentagem"] = m
            
            st.session_state.dados_basicos = dados
            
            st.success("✅ Dados salvos com sucesso!")
            
            st.markdown("### 📊 Resumo dos Cálculos")
            col_a, col_b, col_c, col_d = st.columns(4)
            with col_a:
                st.metric("SB (Soma de Bases)", f"{sb:.2f} cmolc/dm³")
            with col_b:
                st.metric("TCT (Potencial)", f"{tct:.2f} cmolc/dm³")
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
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("pH", f"{dados.get('ph', 'N/A')}")
            st.metric("V%", f"{dados.get('v_porcentagem', 0):.1f}%")
            st.metric("m%", f"{dados.get('m_porcentagem', 0):.1f}%")
        with col2:
            st.metric("N", f"{dados.get('nitrogen', 'N/A')} mg/dm³")
            st.metric("P", f"{dados.get('phosphorus', 'N/A')} mg/dm³")
            st.metric("K", f"{dados.get('potassium', 'N/A')} cmolc/dm³")
        with col3:
            st.metric("Ca", f"{dados.get('calcium', 'N/A')} cmolc/dm³")
            st.metric("Mg", f"{dados.get('magnesium', 'N/A')} cmolc/dm³")
            st.metric("Al", f"{dados.get('aluminum', 'N/A')} cmolc/dm³")
        
        v = dados.get('v_porcentagem', 0)
        classificacao = classificar_fertilidade(v)
        st.info(f"📌 **Classificação:** {classificacao}")
        
        st.markdown("---")
        
        st.markdown("### 🌾 Selecione a Cultura")
        cultura = st.selectbox("Cultura planejada", list(necessidades_culturas.keys()))
        
        if cultura:
            req = necessidades_culturas[cultura]
            
            st.markdown(f"### 📋 Recomendações para {cultura}")
            
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
                st.markdown("#### ✅ Condições Ideais")
                st.markdown(f"- **pH:** {req['ph_min']} - {req['ph_max']} → {'✅ OK' if ph_ok else '❌ Ajustar'}")
                st.markdown(f"- **V%:** ≥ {req['v_desejado']}% → {'✅ OK' if v_ok else '❌ Baixo'}")
                st.markdown(f"- **N:** ≥ {req['n_min']} mg/dm³ → {'✅ OK' if n_ok else '❌ Baixo'}")
            
            with col_b:
                st.markdown(f"- **P:** ≥ {req['p_min']} mg/dm³ → {'✅ OK' if p_ok else '❌ Baixo'}")
                st.markdown(f"- **K:** ≥ {req['k_min']} cmolc/dm³ → {'✅ OK' if k_ok else '❌ Baixo'}")
            
            st.markdown("#### 💡 Recomendações de Manejo")
            recomendacoes = []
            
            if not ph_ok:
                if ph_atual < req['ph_min']:
                    recomendacoes.append(f"🔹 **Calagem necessária:** pH atual {ph_atual:.1f} está abaixo do ideal ({req['ph_min']}-{req['ph_max']}). Aplicar calcário para elevar o pH.")
                else:
                    recomendacoes.append(f"🔹 **pH elevado:** pH atual {ph_atual:.1f} está acima do ideal. Evitar calcário.")
            
            if not v_ok:
                recomendacoes.append(f"🔹 **Saturação por bases baixa:** V% atual {v_atual:.1f}% < {req['v_desejado']}%. Recomenda-se calagem e adubação corretiva.")
            
            if not n_ok:
                recomendacoes.append(f"🔹 **Nitrogênio insuficiente:** {n_atual} < {req['n_min']} mg/dm³. Aplicar adubo nitrogenado (ex: ureia, sulfato de amônio).")
            
            if not p_ok:
                recomendacoes.append(f"🔹 **Fósforo insuficiente:** {p_atual} < {req['p_min']} mg/dm³. Aplicar fósforo (ex: superfosfato simples ou triplo).")
            
            if not k_ok:
                recomendacoes.append(f"🔹 **Potássio insuficiente:** {k_atual} < {req['k_min']} cmolc/dm³. Aplicar cloreto de potássio (KCl).")
            
            if all([ph_ok, v_ok, n_ok, p_ok, k_ok]):
                recomendacoes.append("🎉 **Solo adequado para a cultura!** Apenas mantenha a adubação de manutenção.")
            
            for rec in recomendacoes:
                st.markdown(rec)

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
        placeholder="Exemplo: Qual a recomendação de calagem para um solo com pH 5.0? Como interpretar o V%? Qual a cultura mais adequada para meu solo?"
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
                "Soma de Bases (SB)", "TCT Potencial", "V (%)", "m (%)"
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
                f"{dados.get('tct', 0):.2f} cmolc/dm³",
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
    st.markdown("""
    ### 📐 Fórmulas e Interpretações
    
    | Parâmetro | Fórmula | Interpretação |
    |-----------|---------|---------------|
    | **Soma de Bases (SB)** | SB = Ca²⁺ + Mg²⁺ + K⁺ (cmolc/dm³) | Indica a quantidade de cátions básicos |
    | **TCT Potencial (T)** | T = SB + (H+Al) (cmolc/dm³) | Capacidade máxima de troca catiônica |
    | **Saturação por Bases (V%)** | V% = (SB/T) × 100 | Fertilidade do solo |
    | **Saturação por Alumínio (m%)** | m% = (Al³⁺ / (Al³⁺ + SB)) × 100 | Toxicidade por alumínio |
    
    ### 🌡️ Classificação do V%
    
    - **V% < 50%** → Baixa fertilidade (solos ácidos)
    - **50% ≤ V% < 70%** → Fertilidade média
    - **70% ≤ V% < 85%** → Fertilidade boa
    - **V% ≥ 85%** → Fertilidade muito boa
    
    ### 🧪 pH e Disponibilidade de Nutrientes
    
    - **pH < 5.5** → Alumínio tóxico, baixa disponibilidade de P, Ca, Mg
    - **pH 5.5 - 6.5** → Faixa ideal para maioria das culturas
    - **pH > 6.5** → Pode reduzir disponibilidade de micronutrientes
    
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
st.caption("© 2026 - Sistema Inteligente de Fertilidade do Solo | Baseado em metodologias Embrapa")
