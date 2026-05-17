
import streamlit as st
import pandas as pd

# Configuração da página
st.set_page_config(
    page_title="Classificador de Fertilidade do Solo - SiBCS",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado - Fundo preto, caixas brancas, texto Times New Roman
st.markdown("""
<style>
    /* Fonte Times New Roman */
    * {
        font-family: 'Times New Roman', Times, serif !important;
    }
    
    .stApp {
        background-color: #0a0a0a !important;
    }
    .main > div {
        background-color: #0a0a0a !important;
    }
    .metric-card {
        background: linear-gradient(135deg, #ffffff, #f0f0f0) !important;
        padding: 1rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        transition: transform 0.3s;
        border: 1px solid #2ecc71;
    }
    .metric-card:hover {
        transform: translateY(-5px);
    }
    .metric-card h3 {
        color: #0d2e1d !important;
        font-weight: bold;
    }
    .metric-card h2 {
        color: #1a5f3e !important;
        font-weight: 900;
    }
    .metric-card p, .metric-card small {
        color: #2c5a3a !important;
    }
    .stButton button {
        background: linear-gradient(135deg, #1a5f3e, #2ecc71);
        color: white;
        font-weight: bold;
        border: none;
        border-radius: 30px;
        padding: 0.75rem 2rem;
        transition: all 0.3s;
        width: 100%;
    }
    .stButton button:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 15px rgba(46,204,113,0.4);
    }
    .stAlert {
        background-color: #ffffff !important;
        border-radius: 15px;
        border-left: 5px solid;
        padding: 1rem;
        color: #1a2a1a !important;
    }
    .stAlert p, .stAlert li, .stAlert div {
        color: #1a2a1a !important;
    }
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #f8f9fa, #e9ecef) !important;
        border-radius: 10px;
        color: #1a5f3e !important;
        font-weight: bold;
    }
    .streamlit-expanderHeader p {
        color: #1a5f3e !important;
    }
    .streamlit-expanderContent {
        background-color: #ffffff !important;
        border-radius: 0 0 10px 10px;
        padding: 15px;
    }
    .streamlit-expanderContent p, .streamlit-expanderContent li {
        color: #1a2a1a !important;
    }
    label, .stSlider label, .stNumberInput label, .stSelectbox label, .stRadio label {
        color: #a8e6cf !important;
        font-weight: 600 !important;
    }
    input, .stTextInput input, .stNumberInput input {
        color: #1a2a1a !important;
        background-color: #ffffff !important;
        border: 1px solid #2ecc71 !important;
        border-radius: 8px !important;
    }
    input:focus {
        border-color: #1a5f3e !important;
        box-shadow: 0 0 0 2px rgba(26,95,62,0.2) !important;
    }
    h1, h2, h3, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #2ecc71 !important;
    }
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a0a0a, #1a1a1a) !important;
        border-right: 1px solid #2ecc71;
    }
    .stSidebar .stMarkdown p, .stSidebar .stMarkdown li {
        color: #a8e6cf !important;
    }
    hr {
        margin: 2rem 0;
        background: linear-gradient(90deg, #1a5f3e, #2ecc71, #1a5f3e);
        height: 3px;
        border: none;
    }
    .dataframe {
        background-color: #ffffff !important;
        border-radius: 15px;
        overflow: hidden;
    }
    .dataframe th {
        background: linear-gradient(135deg, #1a5f3e, #2ecc71);
        color: white;
    }
    .dataframe td {
        color: #1a2a1a !important;
    }
    .result-card {
        background: linear-gradient(135deg, #ffffff, #f8f9fa) !important;
        padding: 1.5rem;
        border-radius: 20px;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        border: 2px solid #2ecc71;
    }
    .result-card h2, .result-card h3 {
        color: #1a5f3e !important;
        margin: 0;
    }
    .result-card p {
        color: #2c5a3a !important;
    }
    .result-number {
        font-size: 3rem;
        font-weight: bold;
        color: #1a5f3e;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #ffffff, #f8f9fa) !important;
        padding: 1rem;
        border-radius: 15px;
        border: 1px solid #2ecc71;
    }
    div[data-testid="stMetric"] label {
        color: #0d2e1d !important;
        font-weight: bold !important;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #1a5f3e !important;
        font-size: 1.8rem !important;
        font-weight: 900 !important;
    }
    .progress-container {
        background-color: #e9ecef;
        border-radius: 10px;
        margin: 10px 0;
        overflow: hidden;
    }
    .progress-bar {
        background: linear-gradient(90deg, #1a5f3e, #2ecc71);
        color: white;
        text-align: center;
        padding: 5px;
        border-radius: 10px;
        font-weight: bold;
    }
    .info-box {
        background: #ffffff !important;
        padding: 1rem;
        border-radius: 15px;
        border-left: 5px solid #28a745;
        margin: 1rem 0;
        color: #1a2a1a;
    }
    .warning-box {
        background: #ffffff !important;
        padding: 1rem;
        border-radius: 15px;
        border-left: 5px solid #ffc107;
        margin: 1rem 0;
        color: #856404;
    }
    .success-box {
        background: #ffffff !important;
        padding: 1rem;
        border-radius: 15px;
        border-left: 5px solid #17a2b8;
        margin: 1rem 0;
        color: #0c5460;
    }
    .calculo-box {
        background: #f0f4f0 !important;
        padding: 1rem;
        border-radius: 15px;
        border: 1px dashed #1a5f3e;
        margin: 1rem 0;
        font-family: monospace;
    }
    .calculo-box p {
        color: #1a2a1a !important;
        font-family: monospace !important;
    }
</style>
""", unsafe_allow_html=True)

# Cabeçalho
st.markdown("""
<div style="background: linear-gradient(135deg, #1a5f3e, #2ecc71); padding: 2rem; border-radius: 20px; color: white; text-align: center; margin-bottom: 2rem;">
    <h1 style="color: white;">🌾 Classificador Inteligente de Fertilidade do Solo</h1>
    <p style="font-size: 1.2rem;">Baseado no Sistema Brasileiro de Classificação de Solos (SiBCS) - Embrapa</p>
</div>
""", unsafe_allow_html=True)

# Menu
menu = st.radio(
    "Navegação",
    ["📊 1. Dados do Solo", "🌱 2. Classificação", "🧪 3. Calagem", "⚖️ 4. Gessagem", "📈 5. Relatório", "ℹ️ 6. Métodos"],
    horizontal=True,
    label_visibility="collapsed"
)

# Sidebar
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2934/2934128.png", width=80)
    st.markdown("### 📊 Sobre o Sistema")
    st.markdown("""
    Este classificador utiliza os parâmetros do **SiBCS (Embrapa)** para avaliar:
    - 🧪 Fertilidade do solo
    - 🔬 Acidez e alumínio tóxico
    - ⚖️ Densidade e compactação
    - 🧱 CTC e saturação por bases
    - 📈 Recomendação de calagem e gessagem
    """)
    st.markdown("---")
    st.caption("Versão 3.0 - Classificação Completa")
    st.caption("Unidades padrão: cmolc/dm³ para cátions")

# Inicializar session_state
if 'dados_basicos' not in st.session_state:
    st.session_state.dados_basicos = {}
if 'dados_acidez' not in st.session_state:
    st.session_state.dados_acidez = {}
if 'dados_calculados' not in st.session_state:
    st.session_state.dados_calculados = {}

# ============================================================================
# BLOCO 1: DADOS DO SOLO (Nutrientes, MO, Densidade, Textura)
# ============================================================================
if menu == "📊 1. Dados do Solo":
    st.markdown("## 📋 Etapa 1: Coleta de Dados Básicos do Solo")
    st.markdown("Preencha os dados abaixo. Os dados de **pH e acidez** serão solicitados na próxima aba.")
    
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown("### 🧪 Macronutrientes")
        st.caption("Unidades: mg/dm³ para N e P | cmolc/dm³ para K")
        
        nitrogen = st.text_input("🌱 Nitrogênio (N) - mg/dm³", value="30.0", key="n_basico",
                                help="N disponível - análise de laboratório")
        phosphorus = st.text_input("🔴 Fósforo (P) - mg/dm³", value="20.0", key="p_basico",
                                  help="P disponível - Mehlich-1 ou Resina")
        potassium = st.text_input("🟡 Potássio (K⁺) - cmolc/dm³", value="0.25", key="k_basico",
                                 help="K trocável - Atenção: valor em cmolc/dm³ (1 mmolc/dm³ = 0.1 cmolc/dm³)")
        
        st.markdown("### 🧫 Matéria Orgânica")
        organic_matter = st.text_input("🌿 Matéria Orgânica (MO) - g/kg", value="25.0", key="om_basico",
                                      help="Teor de matéria orgânica")
        
        st.markdown("### ⚖️ Densidade do Solo")
        bulk_density = st.text_input("📦 Densidade do Solo (Ds) - g/cm³", value="1.20", key="bd_basico",
                                    help="Relação massa/volume total")
        particle_density = st.text_input("💎 Densidade de Partícula (Dp) - g/cm³", value="2.65", key="pd_basico",
                                        help="Geralmente 2.65 g/cm³ para solos minerais")
    
    with col2:
        st.markdown("### 🏺 Textura do Solo (Opcional)")
        st.caption("Unidades: g/kg (gramas por quilo)")
        
        sand = st.text_input("🏖️ Areia - g/kg", value="350.0", key="sand_basico")
        silt = st.text_input("🏞️ Silte - g/kg", value="300.0", key="silt_basico")
        clay = st.text_input("🏺 Argila - g/kg", value="350.0", key="clay_basico")
        
        # Validar soma da textura
        try:
            soma = float(sand) + float(silt) + float(clay)
            if abs(soma - 1000) > 10:
                st.warning(f"⚠️ A soma areia+silte+argila = {soma:.0f} g/kg. O ideal é 1000 g/kg.")
        except:
            pass
    
    st.markdown("---")
    
    if st.button("✅ SALVAR DADOS BÁSICOS", use_container_width=True):
        try:
            # Converter K de cmolc/dm³ (já está na unidade correta)
            k_value = float(k_basico.replace(',', '.'))
            
            st.session_state.dados_basicos = {
                'nitrogen': float(nitrogen.replace(',', '.')),
                'phosphorus': float(phosphorus.replace(',', '.')),
                'potassium': k_value,
                'organic_matter': float(organic_matter.replace(',', '.')),
                'bulk_density': float(bulk_density.replace(',', '.')),
                'particle_density': float(particle_density.replace(',', '.')),
                'sand': float(sand.replace(',', '.')),
                'silt': float(silt.replace(',', '.')),
                'clay': float(clay.replace(',', '.'))
            }
            st.success("✅ Dados básicos salvos! Vá para a aba 'Classificação'.")
        except ValueError as e:
            st.error(f"❌ Erro: {e}. Use números com ponto decimal (ex: 1.5)")

# ============================================================================
# BLOCO 2: CLASSIFICAÇÃO (pH, Acidez, Cátions e Análise por Cultura)
# ============================================================================
elif menu == "🌱 2. Classificação":
    
    if not st.session_state.dados_basicos:
        st.warning("⚠️ Por favor, preencha os dados básicos primeiro na aba 'Dados do Solo'.")
        st.stop()
    
    st.markdown("## 📋 Etapa 2: Dados de pH, Acidez e Cátions Trocáveis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🧪 pH e Acidez do Solo")
        ph = st.text_input("🧪 pH do Solo (CaCl₂ ou H₂O)", value="6.0", key="ph_acidez")
        aluminum = st.text_input("⚠️ Alumínio (Al³⁺) - cmolc/dm³", value="0.50", key="al_acidez",
                                help="Alumínio trocável - tóxico para plantas")
        h_al = st.text_input("📊 H + Al - cmolc/dm³", value="3.50", key="hal_acidez",
                            help="Acidez potencial - H + Al trocáveis")
    
    with col2:
        st.markdown("### 🧱 Cátions Trocáveis (cmolc/dm³)")
        calcium = st.text_input("🥛 Cálcio (Ca²⁺) - cmolc/dm³", value="3.00", key="ca_acidez")
        magnesium = st.text_input("🧂 Magnésio (Mg²⁺) - cmolc/dm³", value="1.50", key="mg_acidez")
    
    # Seleção de cultura para análise de adequação
    st.markdown("---")
    st.markdown("### 🌾 Cultura a ser avaliada")
    
    cultura = st.selectbox("Selecione a cultura para verificar se o solo é ideal:", [
        "Soja", "Milho (grão)", "Milho (doce)", "Milho (semente)", 
        "Feijão", "Café", "Algodão", "Cana-de-açúcar", 
        "Milheto", "Sorgo", "Tomate", "Alho", "Cebola",
        "Trigo", "Arroz", "Pastagem", "Batata", "Mandioca"
    ])
    
    # Dicionário com necessidades das culturas (V% ideal, N, P, K)
    necessidades_culturas = {
        "Soja": {"v_desejado": 60, "n_min": 40, "p_min": 15, "k_min": 0.35, "ph_min": 5.5, "ph_max": 6.5},
        "Milho (grão)": {"v_desejado": 65, "n_min": 50, "p_min": 20, "k_min": 0.40, "ph_min": 5.5, "ph_max": 6.5},
        "Milho (doce)": {"v_desejado": 65, "n_min": 60, "p_min": 25, "k_min": 0.45, "ph_min": 5.8, "ph_max": 6.8},
        "Milho (semente)": {"v_desejado": 65, "n_min": 55, "p_min": 22, "k_min": 0.42, "ph_min": 5.5, "ph_max": 6.5},
        "Feijão": {"v_desejado": 65, "n_min": 35, "p_min": 20, "k_min": 0.35, "ph_min": 5.5, "ph_max": 6.5},
        "Café": {"v_desejado": 70, "n_min": 40, "p_min": 25, "k_min": 0.40, "ph_min": 5.5, "ph_max": 6.5},
        "Algodão": {"v_desejado": 65, "n_min": 45, "p_min": 20, "k_min": 0.40, "ph_min": 5.5, "ph_max": 7.0},
        "Cana-de-açúcar": {"v_desejado": 60, "n_min": 40, "p_min": 15, "k_min": 0.35, "ph_min": 5.5, "ph_max": 6.5},
        "Milheto": {"v_desejado": 45, "n_min": 30, "p_min": 10, "k_min": 0.25, "ph_min": 5.0, "ph_max": 6.5},
        "Sorgo": {"v_desejado": 60, "n_min": 40, "p_min": 15, "k_min": 0.35, "ph_min": 5.5, "ph_max": 6.5},
        "Tomate": {"v_desejado": 70, "n_min": 50, "p_min": 30, "k_min": 0.45, "ph_min": 5.8, "ph_max": 6.8},
        "Alho": {"v_desejado": 65, "n_min": 40, "p_min": 20, "k_min": 0.40, "ph_min": 5.8, "ph_max": 6.8},
        "Cebola": {"v_desejado": 65, "n_min": 40, "p_min": 20, "k_min": 0.40, "ph_min": 5.8, "ph_max": 6.8},
        "Trigo": {"v_desejado": 65, "n_min": 45, "p_min": 18, "k_min": 0.38, "ph_min": 5.5, "ph_max": 6.5},
        "Arroz": {"v_desejado": 55, "n_min": 35, "p_min": 12, "k_min": 0.30, "ph_min": 5.0, "ph_max": 6.0},
        "Pastagem": {"v_desejado": 50, "n_min": 30, "p_min": 10, "k_min": 0.25, "ph_min": 5.0, "ph_max": 6.5},
        "Batata": {"v_desejado": 65, "n_min": 50, "p_min": 25, "k_min": 0.45, "ph_min": 5.2, "ph_max": 6.0},
        "Mandioca": {"v_desejado": 55, "n_min": 30, "p_min": 10, "k_min": 0.30, "ph_min": 4.8, "ph_max": 6.0}
    }
    
    st.markdown("---")
    
    if st.button("🔬 CALCULAR CLASSIFICAÇÃO E ADEQUAÇÃO", use_container_width=True):
        try:
            # Combinar dados
            dados = st.session_state.dados_basicos.copy()
            dados['ph'] = float(ph.replace(',', '.'))
            dados['aluminum'] = float(aluminum.replace(',', '.'))
            dados['h_al'] = float(h_al.replace(',', '.'))
            dados['calcium'] = float(calcium.replace(',', '.'))
            dados['magnesium'] = float(magnesium.replace(',', '.'))
            st.session_state.dados_calculados = dados
            
            # Cálculos
            sb = dados['calcium'] + dados['magnesium'] + dados['potassium']
            ctc_efetiva = sb + dados['aluminum']
            ctc_potencial = sb + dados['h_al']
            v_percent = (sb / ctc_potencial * 100) if ctc_potencial > 0 else 0
            m_percent = (dados['aluminum'] / ctc_efetiva * 100) if ctc_efetiva > 0 else 0
            
            # Salvar resultados
            st.session_state.v_percent = v_percent
            st.session_state.ctc_potencial = ctc_potencial
            st.session_state.sb = sb
            st.session_state.m_percent = m_percent
            
            # Adequação para a cultura selecionada
            nec = necessidades_culturas.get(cultura, necessidades_culturas["Soja"])
            adequacoes = []
            
            if v_percent >= nec["v_desejado"]:
                adequacoes.append(f"✅ V% = {v_percent:.1f}% (ideal ≥ {nec['v_desejado']}%)")
            else:
                adequacoes.append(f"❌ V% = {v_percent:.1f}% (necessário ≥ {nec['v_desejado']}%) - Recomenda-se calagem")
            
            if dados['nitrogen'] >= nec["n_min"]:
                adequacoes.append(f"✅ N = {dados['nitrogen']:.1f} mg/dm³ (ideal ≥ {nec['n_min']} mg/dm³)")
            else:
                adequacoes.append(f"❌ N = {dados['nitrogen']:.1f} mg/dm³ (necessário ≥ {nec['n_min']} mg/dm³)")
            
            if dados['phosphorus'] >= nec["p_min"]:
                adequacoes.append(f"✅ P = {dados['phosphorus']:.1f} mg/dm³ (ideal ≥ {nec['p_min']} mg/dm³)")
            else:
                adequacoes.append(f"❌ P = {dados['phosphorus']:.1f} mg/dm³ (necessário ≥ {nec['p_min']} mg/dm³)")
            
            if dados['potassium'] >= nec["k_min"]:
                adequacoes.append(f"✅ K = {dados['potassium']:.2f} cmolc/dm³ (ideal ≥ {nec['k_min']} cmolc/dm³)")
            else:
                adequacoes.append(f"❌ K = {dados['potassium']:.2f} cmolc/dm³ (necessário ≥ {nec['k_min']} cmolc/dm³)")
            
            if nec["ph_min"] <= dados['ph'] <= nec["ph_max"]:
                adequacoes.append(f"✅ pH = {dados['ph']:.1f} (ideal entre {nec['ph_min']}-{nec['ph_max']})")
            else:
                adequacoes.append(f"❌ pH = {dados['ph']:.1f} (ideal entre {nec['ph_min']}-{nec['ph_max']})")
            
            st.session_state.adequacoes = adequacoes
            st.session_state.cultura_selecionada = cultura
            
            st.success("✅ Cálculos realizados! Veja os resultados abaixo.")
            
        except ValueError as e:
            st.error(f"❌ Erro ao converter dados: {e}")
    
    # Exibir resultados
    if st.session_state.get('v_percent') is not None:
        dados = st.session_state.dados_calculados
        v_percent = st.session_state.v_percent
        ctc_potencial = st.session_state.ctc_potencial
        sb = st.session_state.sb
        m_percent = st.session_state.m_percent
        
        st.markdown("---")
        st.markdown("## 📊 Resultado da Classificação")
        
        # Cards
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>🟢 Soma de Bases (SB)</h3>
                <h2>{sb:.2f}</h2>
                <small>cmolc/dm³</small>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h3>🟡 CTC Potencial (pH 7,0)</h3>
                <h2>{ctc_potencial:.2f}</h2>
                <small>cmolc/dm³</small>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h3>🟢 Saturação por Bases (V%)</h3>
                <h2>{v_percent:.1f}%</h2>
                <small>SB / CTC × 100</small>
            </div>
            """, unsafe_allow_html=True)
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <h3>🔴 Saturação por Al (m%)</h3>
                <h2>{m_percent:.1f}%</h2>
                <small>Al³⁺ / CTC_efetiva × 100</small>
            </div>
            """, unsafe_allow_html=True)
        
        # Barra de progresso V%
        st.markdown("### 📊 Índice de Fertilidade do Solo (V%)")
        progress_html = f"""
        <div class="progress-container">
            <div class="progress-bar" style="width: {min(v_percent, 100)}%;">
                {v_percent:.1f}%
            </div>
        </div>
        """
        st.markdown(progress_html, unsafe_allow_html=True)
        
        col_a, col_b, col_c, col_d, col_e = st.columns(5)
        with col_a: st.caption("0% (Álico)")
        with col_b: st.caption("25%")
        with col_c: st.caption("50%")
        with col_d: st.caption("70%")
        with col_e: st.caption("100% (Eutrófico)")
        
        # Classificação SiBCS
        if v_percent >= 70:
            classe = "Eutrófico (Muito Fértil)"
            recomendacao = "Solo excelente para cultivo de alta produtividade."
        elif v_percent >= 50:
            classe = "Eutrófico (Fértil)"
            recomendacao = "Solo fértil, apto para a maioria das culturas."
        elif v_percent >= 25:
            classe = "Distrófico (Baixa Fertilidade)"
            recomendacao = "Solo com baixa fertilidade natural. Recomenda-se calagem e adubação."
        else:
            classe = "Álico (Muito Pobre)"
            recomendacao = "Solo muito pobre. Necessita correção intensiva."
        
        st.markdown(f"""
        <div class="result-card">
            <h2>📌 Classificação do Solo (SiBCS)</h2>
            <p class="result-number">{classe}</p>
            <p>{recomendacao}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Adequação para cultura selecionada
        st.markdown("### 🌾 Adequação do Solo para " + st.session_state.get('cultura_selecionada', cultura))
        
        for a in st.session_state.get('adequacoes', []):
            if "✅" in a:
                st.success(a)
            else:
                st.error(a)
        
        # Score de fertilidade
        score = 0
        if dados['nitrogen'] > 40: score += 2
        if dados['phosphorus'] > 25: score += 2
        if dados['potassium'] > 0.35: score += 2
        if v_percent >= 50: score += 5
        elif v_percent >= 25: score += 2.5
        if dados['aluminum'] < 0.5: score += 4
        elif dados['aluminum'] < 1.0: score += 2
        if 1.0 <= dados['bulk_density'] <= 1.3: score += 3
        elif dados['bulk_density'] < 1.6: score += 1.5
        if 5.5 <= dados['ph'] <= 6.5: score += 2
        
        if score >= 12:
            st.markdown(f"""
            <div class="result-card">
                <h2>🟢 RESULTADO FINAL</h2>
                <p class="result-number">ALTA FERTILIDADE</p>
                <p>Score: {score:.1f}/20 pontos</p>
            </div>
            """, unsafe_allow_html=True)
        elif score >= 7:
            st.markdown(f"""
            <div class="result-card">
                <h2>🟡 RESULTADO FINAL</h2>
                <p class="result-number">FERTILIDADE MÉDIA</p>
                <p>Score: {score:.1f}/20 pontos</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="result-card">
                <h2>🔴 RESULTADO FINAL</h2>
                <p class="result-number">BAIXA FERTILIDADE</p>
                <p>Score: {score:.1f}/20 pontos</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.session_state.score = score


**Quando indicar:**
        - Al^3+ > 0,5 cmolc/dm3
        - Ca^2+ < 1,0 cmolc/dm3
        - Saturação por Al (m%) > 20%

with st.expander("🌾 Tabela de Necessidades por Cultura"):
st.markdown("""
| Cultura | V% Ideal | N mínimo | P mínimo | K mínimo | pH ideal |
|---------|----------|----------|----------|----------|----------|
| **Soja** | 60% | 40 mg/dm³ | 15 mg/dm³ | 0,35 cmolc/dm³ | 5,5-6,5 |
| **Milho (grão)** | 65% | 50 mg/dm³ | 20 mg/dm³ | 0,40 cmolc/dm³ | 5,5-6,5 |
| **Milho (doce)** | 65% | 60 mg/dm³ | 25 mg/dm³ | 0,45 cmolc/dm³ | 5,8-6,8 |
| **Feijão** | 65% | 35 mg/dm³ | 20 mg/dm³ | 0,35 cmolc/dm³ | 5,5-6,5 |
| **Café** | 70% | 40 mg/dm³ | 25 mg/dm³ | 0,40 cmolc/dm³ | 5,5-6,5 |
| **Algodão** | 65% | 45 mg/dm³ | 20 mg/dm³ | 0,40 cmolc/dm³ | 5,5-7,0 |
| **Cana-de-açúcar** | 60% | 40 mg/dm³ | 15 mg/dm³ | 0,35 cmolc/dm³ | 5,5-6,5 |
| **Milheto** | 45% | 30 mg/dm³ | 10 mg/dm³ | 0,25 cmolc/dm³ | 5,0-6,5 |
| **Sorgo** | 60% | 40 mg/dm³ | 15 mg/dm³ | 0,35 cmolc/dm³ | 5,5-6,5 |
| **Tomate** | 70% | 50 mg/dm³ | 30 mg/dm³ | 0,45 cmolc/dm³ | 5,8-6,8 |
| **Alho** | 65% | 40 mg/dm³ | 20 mg/dm³ | 0,40 cmolc/dm³ | 5,8-6,8 |
| **Cebola** | 65% | 40 mg/dm³ | 20 mg/dm³ | 0,40 cmolc/dm³ | 5,8-6,8 |
""")

with st.expander("📏 Unidades de Medida Utilizadas"):
st.markdown("""
| Parâmetro | Unidade | Equivalência |
|-----------|---------|--------------|
| **Nitrogênio (N)** | mg/dm³ | 1 mg/dm³ = 1 ppm |
| **Fósforo (P)** | mg/dm³ | 1 mg/dm³ = 1 ppm |
| **Potássio (K⁺)** | cmolc/dm³ | 1 cmolc/dm³ = 10 mmolc/dm³ |
| **Cálcio (Ca²⁺)** | cmolc/dm³ | 1 cmolc/dm³ = 10 mmolc/dm³ |
| **Magnésio (Mg²⁺)** | cmolc/dm³ | 1 cmolc/dm³ = 10 mmolc/dm³ |
| **Alumínio (Al³⁺)** | cmolc/dm³ | - |
| **CTC** | cmolc/dm³ | - |
| **Matéria Orgânica** | g/kg | 1 g/kg = 0,1% |
| **Densidade** | g/cm³ | - |
| **Textura** | g/kg | Soma deve ser 1000 g/kg |
""")

st.markdown("---")
st.caption("© 2025 - Classificador de Fertilidade do Solo | Baseado no SiBCS - Embrapa")
