import streamlit as st
import pandas as pd

# Configuração da página
st.set_page_config(
    page_title="Classificador de Fertilidade do Solo - SiBCS",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado - Fundo preto, caixas brancas, texto verde escuro
st.markdown("""
<style>
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
    ["📊 Dados do Solo", "🌱 Classificação", "🧪 Calagem", "⚖️ Gessagem", "📈 Relatório"],
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
    st.caption("Versão 2.0 - Classificação Completa")

# Inicializar session_state
if 'dados_basicos' not in st.session_state:
    st.session_state.dados_basicos = {}
if 'dados_acidez' not in st.session_state:
    st.session_state.dados_acidez = {}
if 'dados_calculados' not in st.session_state:
    st.session_state.dados_calculados = {}

# ========== SEÇÃO 1: DADOS DO SOLO (APENAS NUTRIENTES, MO, DENSIDADE, TEXTURA) ==========
if menu == "📊 Dados do Solo":
    st.markdown("## 📋 Coleta de Dados do Solo - Parte 1")
    st.markdown("Preencha os dados básicos. Os dados de **pH e acidez** serão solicitados na próxima aba.")
    
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown("### 🧪 Nutrientes")
        nitrogen = st.text_input("🌱 Nitrogênio (mg/dm³)", value="30.0", key="n_basico")
        phosphorus = st.text_input("🔴 Fósforo (mg/dm³)", value="20.0", key="p_basico")
        potassium = st.text_input("🟡 Potássio (mmolc/dm³)", value="25.0", key="k_basico")
        
        st.markdown("### 🧫 Matéria Orgânica")
        organic_matter = st.text_input("🌿 Matéria Orgânica (g/kg)", value="25.0", key="om_basico")
        
        st.markdown("### ⚖️ Densidade do Solo")
        bulk_density = st.text_input("📦 Densidade do Solo (g/cm³)", value="1.20", key="bd_basico")
        particle_density = st.text_input("💎 Densidade de Partícula (g/cm³)", value="2.65", key="pd_basico")
    
    with col2:
        st.markdown("### 🏺 Textura do Solo (Opcional)")
        st.caption("Preencha para análise da dinâmica de nutrientes")
        sand = st.text_input("🏖️ Areia (g/kg)", value="350.0", key="sand_basico")
        silt = st.text_input("🏞️ Silte (g/kg)", value="300.0", key="silt_basico")
        clay = st.text_input("🏺 Argila (g/kg)", value="350.0", key="clay_basico")
    
    st.markdown("---")
    
    if st.button("✅ SALVAR DADOS BÁSICOS", use_container_width=True):
        try:
            st.session_state.dados_basicos = {
                'nitrogen': float(nitrogen.replace(',', '.')),
                'phosphorus': float(phosphorus.replace(',', '.')),
                'potassium': float(potassium.replace(',', '.')),
                'organic_matter': float(organic_matter.replace(',', '.')),
                'bulk_density': float(bulk_density.replace(',', '.')),
                'particle_density': float(particle_density.replace(',', '.')),
                'sand': float(sand.replace(',', '.')),
                'silt': float(silt.replace(',', '.')),
                'clay': float(clay.replace(',', '.'))
            }
            st.success("✅ Dados básicos salvos! Vá para a aba 'Classificação' para inserir pH e acidez.")
        except ValueError as e:
            st.error(f"❌ Erro: {e}. Use números com ponto decimal (ex: 1.5)")

# ========== SEÇÃO 2: CLASSIFICAÇÃO (COM pH, ACIDEZ E CÁTIONS) ==========
elif menu == "🌱 Classificação":
    
    if not st.session_state.dados_basicos:
        st.warning("⚠️ Por favor, preencha os dados básicos primeiro na aba '📊 Dados do Solo'.")
        st.stop()
    
    st.markdown("## 📋 Dados de pH, Acidez e Cátions Trocáveis - Parte 2")
    st.markdown("Preencha os dados da análise de solo para completar a classificação.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🧪 pH e Acidez do Solo")
        ph = st.text_input("🧪 pH do Solo (CaCl₂ ou H₂O)", value="6.0", key="ph_acidez", 
                          help="Ideal para maioria das culturas: 5.5-6.5")
        aluminum = st.text_input("⚠️ Alumínio (Al³⁺) (cmolc/dm³)", value="0.50", key="al_acidez",
                                help="Alumínio trocável - tóxico para plantas")
        h_al = st.text_input("📊 H + Al (cmolc/dm³)", value="3.50", key="hal_acidez",
                            help="Acidez potencial - H + Al trocáveis")
    
    with col2:
        st.markdown("### 🧱 Cátions Trocáveis")
        calcium = st.text_input("🥛 Cálcio (Ca²⁺) (cmolc/dm³)", value="3.00", key="ca_acidez",
                               help="Cálcio trocável")
        magnesium = st.text_input("🧂 Magnésio (Mg²⁺) (cmolc/dm³)", value="1.50", key="mg_acidez",
                                 help="Magnésio trocável")
    
    st.markdown("---")
    
    if st.button("🔬 CALCULAR CLASSIFICAÇÃO", use_container_width=True):
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
            
            st.success("✅ Cálculos realizados! Veja os resultados abaixo.")
            
        except ValueError as e:
            st.error(f"❌ Erro ao converter dados: {e}. Use números com ponto decimal (ex: 1.5)")
    
    # Exibir resultados se já tiver sido calculado
    if st.session_state.get('v_percent') is not None:
        dados = st.session_state.dados_calculados
        v_percent = st.session_state.v_percent
        ctc_potencial = st.session_state.ctc_potencial
        sb = st.session_state.sb
        m_percent = st.session_state.m_percent
        
        st.markdown("---")
        st.markdown("## 📊 Resultado da Classificação")
        
        # Cards de métricas
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>🟢 SB</h3>
                <h2>{sb:.2f}</h2>
                <small>Soma de Bases</small>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h3>🟡 CTC</h3>
                <h2>{ctc_potencial:.2f}</h2>
                <small>CTC potencial</small>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h3>🟢 V%</h3>
                <h2>{v_percent:.1f}%</h2>
                <small>Saturação por Bases</small>
            </div>
            """, unsafe_allow_html=True)
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <h3>🔴 m%</h3>
                <h2>{m_percent:.1f}%</h2>
                <small>Saturação por Al</small>
            </div>
            """, unsafe_allow_html=True)
        
        # BARRA DE PROGRESSO VISUAL
        st.markdown("### 📊 Indicador de Fertilidade (V%)")
        
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
            cor = "success"
        elif v_percent >= 50:
            classe = "Eutrófico (Fértil)"
            cor = "success"
        elif v_percent >= 25:
            classe = "Distrófico (Baixa Fertilidade)"
            cor = "warning"
        else:
            classe = "Álico (Muito Pobre)"
            cor = "error"
        
        st.markdown(f"""
        <div class="result-card">
            <h2>📌 Classificação SiBCS</h2>
            <p class="result-number">{classe}</p>
            <p>V% = {v_percent:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Score de fertilidade
        score = 0
        if dados['nitrogen'] > 40: score += 2
        if dados['phosphorus'] > 25: score += 2
        if dados['potassium'] > 35: score += 2
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

# ========== SEÇÃO 3: CALAGEM ==========
elif menu == "🧪 Calagem":
    
    if st.session_state.get('v_percent') is None:
        st.warning("⚠️ Por favor, complete a classificação primeiro na aba '🌱 Classificação'.")
        st.stop()
    
    v_percent = st.session_state.v_percent
    ctc_potencial = st.session_state.ctc_potencial
    
    st.markdown("## 🧪 Recomendação de Calagem")
    
    col1, col2 = st.columns(2)
    
    with col1:
        profundidade = st.radio("Profundidade:", ["0-10 cm", "10-15 cm", "15-20 cm"], horizontal=True)
        fator_profundidade = {"0-10 cm": 1.0, "10-15 cm": 1.5, "15-20 cm": 2.0}
        prnt = st.number_input("PRNT do calcário (%)", min_value=50.0, max_value=100.0, value=85.0, step=1.0)
    
    with col2:
        cultura = st.selectbox("Cultura:", ["Soja", "Milho", "Feijão", "Trigo", "Arroz", "Café", "Cana-de-açúcar"])
    
    v_desejado = {"Soja": 60, "Milho": 65, "Feijão": 65, "Trigo": 65, "Arroz": 55, "Café": 70, "Cana-de-açúcar": 60}.get(cultura, 60)
    
    st.markdown(f"""
    <div class="info-box">
        <p><strong>📊 Situação atual:</strong> V% = {v_percent:.1f}% | V% desejado para {cultura} = {v_desejado}%</p>
    </div>
    """, unsafe_allow_html=True)
    
    if v_percent < v_desejado:
        nc = (v_desejado - v_percent) * ctc_potencial / 100
        nc_final = nc * (100 / prnt) * fator_profundidade[profundidade]
        
        st.markdown(f"""
        <div class="result-card">
            <h2>📦 QUANTIDADE DE CALCÁRIO</h2>
            <p class="result-number">{nc_final:.1f} t/ha</p>
            <p>Profundidade: {profundidade} | PRNT: {prnt:.0f}%</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="success-box">
            <h3>✅ NÃO HÁ NECESSIDADE DE CALAGEM</h3>
            <p>O solo já apresenta V% adequado para a cultura selecionada.</p>
        </div>
        """, unsafe_allow_html=True)

# ========== SEÇÃO 4: GESSAGEM ==========
elif menu == "⚖️ Gessagem":
    
    if not st.session_state.dados_calculados:
        st.warning("⚠️ Por favor, complete a classificação primeiro na aba '🌱 Classificação'.")
        st.stop()
    
    dados = st.session_state.dados_calculados
    
    st.markdown("## ⚖️ Recomendação de Gessagem")
    
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("Alumínio (Al³⁺)", f"{dados['aluminum']:.2f} cmolc/dm³")
    with col2: st.metric("Cálcio (Ca²⁺)", f"{dados['calcium']:.2f} cmolc/dm³")
    with col3: st.metric("V% atual", f"{st.session_state.get('v_percent', 0):.1f}%")
    
    if dados['aluminum'] > 0.5 or dados['calcium'] < 1.0:
        ng_total = dados['aluminum'] * 1.5
        if dados['calcium'] < 2.0:
            ng_total += (2.0 - dados['calcium']) * 1.5
        
        st.markdown(f"""
        <div class="result-card">
            <h2>📦 QUANTIDADE DE GESSO</h2>
            <p class="result-number">{ng_total:.1f} t/ha</p>
            <p>Gesso agrícola para aplicação superficial</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="success-box">
            <h3>✅ NÃO HÁ NECESSIDADE DE GESSAGEM</h3>
            <p>Os parâmetros estão dentro dos limites ideais.</p>
        </div>
        """, unsafe_allow_html=True)

# ========== SEÇÃO 5: RELATÓRIO ==========
elif menu == "📈 Relatório":
    
    if not st.session_state.dados_calculados:
        st.warning("⚠️ Por favor, complete a classificação primeiro na aba '🌱 Classificação'.")
        st.stop()
    
    st.markdown("## 📋 Relatório Completo da Análise")
    
    dados = st.session_state.dados_calculados
    v_percent = st.session_state.get('v_percent', 0)
    ctc_potencial = st.session_state.get('ctc_potencial', 0)
    sb = st.session_state.get('sb', 0)
    
    resumo = pd.DataFrame({
        "Parâmetro": ["Nitrogênio (N)", "Fósforo (P)", "Potássio (K)", 
                     "Cálcio (Ca)", "Magnésio (Mg)", "pH", "Alumínio (Al³⁺)",
                     "H + Al", "Soma de Bases (SB)", "CTC Potencial",
                     "Saturação por Bases (V%)", "Matéria Orgânica",
                     "Densidade do Solo", "Areia", "Silte", "Argila"],
        "Valor": [
            f"{dados['nitrogen']:.1f} mg/dm³",
            f"{dados['phosphorus']:.1f} mg/dm³",
            f"{dados['potassium']:.1f} mmolc/dm³",
            f"{dados['calcium']:.1f} cmolc/dm³",
            f"{dados['magnesium']:.1f} cmolc/dm³",
            f"{dados['ph']:.1f}",
            f"{dados['aluminum']:.2f} cmolc/dm³",
            f"{dados['h_al']:.2f} cmolc/dm³",
            f"{sb:.2f} cmolc/dm³",
            f"{ctc_potencial:.2f} cmolc/dm³",
            f"{v_percent:.1f}%",
            f"{dados['organic_matter']:.1f} g/kg",
            f"{dados['bulk_density']:.2f} g/cm³",
            f"{dados['sand']:.1f} g/kg",
            f"{dados['silt']:.1f} g/kg",
            f"{dados['clay']:.1f} g/kg"
        ]
    })
    
    st.dataframe(resumo, hide_index=True, use_container_width=True)
    
    csv = resumo.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Baixar Relatório (CSV)", csv, "analise_solo.csv", "text/csv", use_container_width=True)

st.markdown("---")
st.caption("© 2025 - Classificador de Fertilidade do Solo | Baseado no SiBCS - Embrapa")
