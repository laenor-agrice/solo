import streamlit as st
import pandas as pd

# Configuração da página
st.set_page_config(
    page_title="Classificador de Fertilidade do Solo - SiBCS",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1a5f3e, #2ecc71);
        padding: 2rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .metric-card {
        background: linear-gradient(135deg, #f8f9fa, #e9ecef);
        padding: 1rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        transition: transform 0.3s;
    }
    .metric-card:hover {
        transform: translateY(-5px);
    }
    .stButton button {
        background: linear-gradient(135deg, #1a5f3e, #2ecc71);
        color: white;
        font-weight: bold;
        border: none;
        border-radius: 30px;
        padding: 0.75rem 2rem;
        transition: all 0.3s;
    }
    .stButton button:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 15px rgba(46,204,113,0.3);
    }
    .info-box {
        background: linear-gradient(135deg, #d4edda, #c3e6cb);
        padding: 1rem;
        border-radius: 15px;
        border-left: 5px solid #28a745;
        margin: 1rem 0;
    }
    .warning-box {
        background: linear-gradient(135deg, #fff3cd, #ffeaa7);
        padding: 1rem;
        border-radius: 15px;
        border-left: 5px solid #ffc107;
        margin: 1rem 0;
    }
    .success-box {
        background: linear-gradient(135deg, #d1ecf1, #bee5eb);
        padding: 1rem;
        border-radius: 15px;
        border-left: 5px solid #17a2b8;
        margin: 1rem 0;
    }
    h1, h2, h3 {
        color: #1a5f3e;
    }
    hr {
        margin: 2rem 0;
        background: linear-gradient(90deg, #1a5f3e, #2ecc71, #1a5f3e);
        height: 3px;
        border: none;
    }
    div.stButton > button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Cabeçalho
st.markdown("""
<div class="main-header">
    <h1 style="color: white;">🌾 Classificador Inteligente de Fertilidade do Solo</h1>
    <p style="font-size: 1.2rem;">Baseado no Sistema Brasileiro de Classificação de Solos (SiBCS) - Embrapa</p>
</div>
""", unsafe_allow_html=True)

# Menu com radio buttons (alternativa ao option_menu)
menu = st.radio(
    "Navegação",
    ["📊 Dados do Solo", "🌱 Classificação", "🧪 Calagem", "⚖️ Gessagem", "📈 Relatório"],
    horizontal=True,
    label_visibility="collapsed"
)

# Sidebar com informações
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
    st.caption("Desenvolvido com base na literatura Embrapa")

# Inicializar session_state
if 'dados_calculados' not in st.session_state:
    st.session_state.dados_calculados = {}

# ========== SEÇÃO 1: DADOS DO SOLO ==========
if menu == "📊 Dados do Solo":
    st.markdown("## 📋 Coleta de Dados do Solo")
    st.markdown("Preencha todas as informações abaixo para uma análise completa.")
    
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown("### 🧪 Nutrientes e Química")
        
        nitrogen = st.number_input(
            "🌱 Nitrogênio (mg/dm³)", 
            min_value=0.0, max_value=500.0, value=30.0, step=5.0,
            key="nitrogen"
        )
        phosphorus = st.number_input(
            "🔴 Fósforo (mg/dm³)", 
            min_value=0.0, max_value=300.0, value=20.0, step=2.0,
            key="phosphorus"
        )
        potassium = st.number_input(
            "🟡 Potássio (mmolc/dm³)", 
            min_value=0.0, max_value=200.0, value=25.0, step=2.0,
            key="potassium"
        )
        
        st.markdown("### 🧫 Matéria Orgânica")
        organic_matter = st.number_input(
            "🌿 Matéria Orgânica (g/kg)", 
            min_value=0.0, max_value=200.0, value=25.0, step=5.0,
            key="organic_matter"
        )
        clay = st.number_input(
            "🏺 Argila (g/kg)", 
            min_value=0.0, max_value=900.0, value=350.0, step=10.0,
            key="clay"
        )
        
    with col2:
        st.markdown("### 🔬 Acidez e Bases")
        
        ph = st.slider(
            "🧪 pH do Solo (CaCl₂)", 
            min_value=3.0, max_value=9.0, value=6.0, step=0.1,
            key="ph"
        )
        
        aluminum = st.number_input(
            "⚠️ Alumínio (Al³⁺) (cmolc/dm³)", 
            min_value=0.0, max_value=15.0, value=0.5, step=0.1,
            key="aluminum"
        )
        
        h_al = st.number_input(
            "📊 H + Al (cmolc/dm³)", 
            min_value=0.0, max_value=30.0, value=3.5, step=0.5,
            key="h_al"
        )
        
        st.markdown("### 🧱 Cátions Trocáveis")
        
        calcium = st.number_input(
            "🥛 Cálcio (Ca²⁺) (cmolc/dm³)", 
            min_value=0.0, max_value=25.0, value=3.0, step=0.5,
            key="calcium"
        )
        magnesium = st.number_input(
            "🧂 Magnésio (Mg²⁺) (cmolc/dm³)", 
            min_value=0.0, max_value=15.0, value=1.5, step=0.5,
            key="magnesium"
        )
        
        st.markdown("### ⚖️ Densidade do Solo")
        
        bulk_density = st.number_input(
            "📦 Densidade do Solo (g/cm³)", 
            min_value=0.5, max_value=2.5, value=1.2, step=0.05,
            key="bulk_density"
        )
        particle_density = st.number_input(
            "💎 Densidade de Partícula (g/cm³)", 
            min_value=2.0, max_value=3.0, value=2.65, step=0.05,
            key="particle_density"
        )
    
    st.markdown("---")
    
    if st.button("✅ Salvar Dados e Continuar", use_container_width=True):
        st.session_state.dados_calculados = {
            'nitrogen': nitrogen, 'phosphorus': phosphorus, 'potassium': potassium,
            'ph': ph, 'aluminum': aluminum, 'h_al': h_al,
            'calcium': calcium, 'magnesium': magnesium, 'clay': clay,
            'bulk_density': bulk_density, 'particle_density': particle_density,
            'organic_matter': organic_matter
        }
        st.success("✅ Dados salvos com sucesso! Vá para a aba 'Classificação'.")
    
    with st.expander("📖 Tabela de Referência - Níveis Críticos"):
        st.markdown("""
        | Parâmetro | Muito Baixo | Baixo | Médio | Bom | Muito Bom |
        |-----------|-------------|-------|-------|-----|-----------|
        | **N (mg/dm³)** | < 15 | 15-25 | 25-40 | 40-60 | > 60 |
        | **P (mg/dm³)** | < 5 | 5-10 | 10-20 | 20-40 | > 40 |
        | **K (mmolc/dm³)** | < 15 | 15-25 | 25-40 | 40-60 | > 60 |
        | **pH** | < 4.5 | 4.5-5.0 | 5.0-5.5 | 5.5-6.5 | > 6.5 |
        | **Al³⁺ (cmolc/dm³)** | > 1.5 | 1.0-1.5 | 0.5-1.0 | 0.2-0.5 | < 0.2 |
        | **V%** | < 25 | 25-40 | 40-55 | 55-70 | > 70 |
        """)

# ========== SEÇÃO 2: CLASSIFICAÇÃO ==========
elif menu == "🌱 Classificação":
    
    if not st.session_state.dados_calculados:
        st.warning("⚠️ Por favor, preencha os dados do solo primeiro na aba '📊 Dados do Solo'.")
        st.stop()
    
    dados = st.session_state.dados_calculados
    
    # Cálculos
    sb = dados['calcium'] + dados['magnesium'] + dados['potassium']
    ctc_efetiva = sb + dados['aluminum']
    ctc_potencial = sb + dados['h_al']
    v_percent = (sb / ctc_potencial * 100) if ctc_potencial > 0 else 0
    m_percent = (dados['aluminum'] / ctc_efetiva * 100) if ctc_efetiva > 0 else 0
    
    st.markdown("## 📊 Resultado da Classificação")
    
    # Cards de métricas
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>🟢 V%</h3>
            <h2>{v_percent:.1f}%</h2>
            <small>Saturação por Bases</small>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>🔴 Al³⁺</h3>
            <h2>{dados['aluminum']:.2f}</h2>
            <small>cmolc/dm³</small>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>🧱 CTC</h3>
            <h2>{ctc_potencial:.2f}</h2>
            <small>cmolc/dm³</small>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3>⚖️ Densidade</h3>
            <h2>{dados['bulk_density']:.2f}</h2>
            <small>g/cm³</small>
        </div>
        """, unsafe_allow_html=True)
    
    # Score
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
    
    st.markdown("---")
    
    if score >= 12:
        st.markdown(f"""
        <div class="success-box">
            <h2 style="color: #155724;">🟢 RESULTADO: ALTA FERTILIDADE</h2>
            <p>Score: {score:.1f}/20 pontos</p>
            <p>✅ Solo fértil segundo critérios do SiBCS. Apto para cultivo de alta produtividade.</p>
        </div>
        """, unsafe_allow_html=True)
    elif score >= 7:
        st.markdown(f"""
        <div class="warning-box">
            <h2 style="color: #856404;">🟡 RESULTADO: FERTILIDADE MÉDIA</h2>
            <p>Score: {score:.1f}/20 pontos</p>
            <p>⚠️ Solo com potencial, mas necessita manejo adequado e correções localizadas.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="info-box">
            <h2 style="color: #721c24;">🔴 RESULTADO: BAIXA FERTILIDADE</h2>
            <p>Score: {score:.1f}/20 pontos</p>
            <p>❌ Solo necessita correção e manejo intensivo. Recomenda-se calagem e adubação.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Salvar para outras abas
    st.session_state.v_percent = v_percent
    st.session_state.ctc_potencial = ctc_potencial
    st.session_state.m_percent = m_percent

# ========== SEÇÃO 3: CALAGEM ==========
elif menu == "🧪 Calagem":
    
    if not st.session_state.dados_calculados:
        st.warning("⚠️ Por favor, preencha os dados do solo primeiro na aba '📊 Dados do Solo'.")
        st.stop()
    
    dados = st.session_state.dados_calculados
    v_percent = st.session_state.get('v_percent', 0)
    ctc_potencial = st.session_state.get('ctc_potencial', 0)
    
    st.markdown("## 🧪 Recomendação de Calagem")
    
    col1, col2 = st.columns(2)
    
    with col1:
        profundidade = st.radio(
            "📏 Profundidade de incorporação:",
            ["0-10 cm", "10-15 cm", "15-20 cm"],
            horizontal=True
        )
        fator_profundidade = {"0-10 cm": 1.0, "10-15 cm": 1.5, "15-20 cm": 2.0}
        
        # PRNT como caixa para digitar
        prnt = st.number_input(
            "📦 PRNT do calcário (%)",
            min_value=50.0, max_value=100.0, value=85.0, step=1.0,
            help="Poder Relativo de Neutralização Total - informe o valor do seu calcário"
        )
    
    with col2:
        cultura = st.selectbox(
            "🌾 Cultura a ser cultivada:",
            [
                "Soja", "Milho", "Feijão", "Trigo", "Arroz", "Algodão", "Café",
                "Cana-de-açúcar", "Pastagem (Braquiária)", "Milheto", "Crotalária",
                "Batata", "Mandioca", "Tomate"
            ]
        )
    
    v_desejado_culturas = {
        "Soja": 60, "Milho": 65, "Feijão": 65, "Trigo": 65, "Arroz": 55,
        "Algodão": 65, "Café": 70, "Cana-de-açúcar": 60, "Pastagem (Braquiária)": 50,
        "Milheto": 45, "Crotalária": 50, "Batata": 65, "Mandioca": 55, "Tomate": 70
    }
    v_desejado = v_desejado_culturas.get(cultura, 55)
    
    st.info(f"📌 **{cultura}** - Saturação por bases desejada: **{v_desejado}%**")
    
    col_a, col_b, col_c = st.columns(3)
    with col_a: st.metric("V% atual", f"{v_percent:.1f}%")
    with col_b: st.metric("CTC potencial", f"{ctc_potencial:.2f} cmolc/dm³")
    with col_c: st.metric("PRNT", f"{prnt:.0f}%")
    
    st.markdown("---")
    
    if v_percent < v_desejado:
        nc = (v_desejado - v_percent) * ctc_potencial / 100
        nc_corrigido = nc * (100 / prnt)
        nc_final = nc_corrigido * fator_profundidade[profundidade]
        
        st.markdown(f"""
        <div class="warning-box">
            <h3 style="color: #856404;">⚠️ É RECOMENDADO CALAGEM</h3>
            <p>V% atual ({v_percent:.1f}%) está abaixo do ideal para {cultura} ({v_desejado}%)</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.success(f"✅ **Quantidade final de calcário a aplicar: {nc_final:.1f} t/ha**")
        
        with st.expander("📖 Recomendações de Aplicação"):
            st.markdown(f"""
            - **Época ideal:** 60-90 dias antes do plantio
            - **Incorporação:** Incorporar na profundidade de {profundidade}
            - **PRNT utilizado:** {prnt:.0f}%
            - **Resultado esperado:** Solo atingirá V% = {v_desejado}%
            """)
    else:
        st.success(f"### ✅ NÃO HÁ NECESSIDADE DE CALAGEM")
        st.write(f"V% atual ({v_percent:.1f}%) já está no nível ideal para {cultura} ({v_desejado}%)")

# ========== SEÇÃO 4: GESSAGEM ==========
elif menu == "⚖️ Gessagem":
    
    if not st.session_state.dados_calculados:
        st.warning("⚠️ Por favor, preencha os dados do solo primeiro na aba '📊 Dados do Solo'.")
        st.stop()
    
    dados = st.session_state.dados_calculados
    m_percent = st.session_state.get('m_percent', 0)
    
    st.markdown("## ⚖️ Recomendação de Gessagem")
    
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("Alumínio (Al³⁺)", f"{dados['aluminum']:.2f} cmolc/dm³")
    with col2: st.metric("Cálcio (Ca²⁺)", f"{dados['calcium']:.2f} cmolc/dm³")
    with col3: st.metric("Saturação Al (m%)", f"{m_percent:.1f}%")
    
    st.markdown("---")
    
    if dados['aluminum'] > 0.5 or dados['calcium'] < 1.0 or m_percent > 20:
        ng_al = dados['aluminum'] * 1.5
        if dados['calcium'] < 2.0:
            ng_ca = (2.0 - dados['calcium']) * 1.5
        else:
            ng_ca = 0
        ng_total = ng_al + ng_ca
        
        st.markdown(f"""
        <div class="warning-box">
            <h3 style="color: #856404;">⚠️ É RECOMENDADO GESSAGEM</h3>
        </div>
        """, unsafe_allow_html=True)
        
        st.success(f"✅ **Quantidade de gesso agrícola: {ng_total:.1f} t/ha**")
        
        with st.expander("📖 Recomendações de Aplicação"):
            st.markdown("""
            - **Época:** Aplicar após a calagem (30-60 dias de intervalo)
            - **Aplicação:** A lanço, SEM incorporar (deixar na superfície)
            - **Benefícios:** Neutraliza Al³⁺ em profundidade, fornece Ca²⁺ e S
            """)
    else:
        st.success(f"### ✅ NÃO HÁ NECESSIDADE DE GESSAGEM")
        st.write("Os parâmetros estão dentro dos limites ideais.")

# ========== SEÇÃO 5: RELATÓRIO ==========
elif menu == "📈 Relatório":
    
    if not st.session_state.dados_calculados:
        st.warning("⚠️ Por favor, preencha os dados do solo primeiro.")
        st.stop()
    
    st.markdown("## 📋 Relatório Completo da Análise")
    
    dados = st.session_state.dados_calculados
    v_percent = st.session_state.get('v_percent', 0)
    
    resumo = pd.DataFrame({
        "Parâmetro": ["Nitrogênio (N)", "Fósforo (P)", "Potássio (K)", 
                     "Cálcio (Ca)", "Magnésio (Mg)", "pH", "Alumínio (Al³⁺)",
                     "CTC Potencial", "Saturação por Bases (V%)", "Matéria Orgânica",
                     "Densidade do Solo"],
        "Valor": [f"{dados['nitrogen']:.1f} mg/dm³", f"{dados['phosphorus']:.1f} mg/dm³",
                 f"{dados['potassium']:.1f} mmolc/dm³", f"{dados['calcium']:.1f} cmolc/dm³",
                 f"{dados['magnesium']:.1f} cmolc/dm³", f"{dados['ph']:.1f}",
                 f"{dados['aluminum']:.2f} cmolc/dm³", 
                 f"{st.session_state.get('ctc_potencial', 0):.2f} cmolc/dm³",
                 f"{v_percent:.1f}%", f"{dados['organic_matter']:.1f} g/kg",
                 f"{dados['bulk_density']:.2f} g/cm³"]
    })
    
    st.dataframe(resumo, hide_index=True, use_container_width=True)
    
    csv = resumo.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Baixar Relatório (CSV)",
        data=csv,
        file_name="analise_solo.csv",
        mime="text/csv",
        use_container_width=True
    )

# ========== ESTILOS ADICIONAIS PARA CORRIGIR BRANCO ==========
st.markdown("""
<style>
    /* Fundo geral da página */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 100%);
    }
    
    /* Cards de métricas */
    div[data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: bold !important;
        color: #1a5f3e !important;
    }
    
    div[data-testid="stMetricLabel"] {
        font-size: 1rem !important;
        color: #2c3e50 !important;
    }
    
    /* Botões */
    .stButton button {
        background: linear-gradient(135deg, #1a5f3e, #2ecc71) !important;
        color: white !important;
        border: none !important;
        border-radius: 30px !important;
        padding: 0.75rem 2rem !important;
        font-weight: bold !important;
        transition: all 0.3s !important;
    }
    
    .stButton button:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 15px rgba(46,204,113,0.4);
    }
    
    /* Abas/Radio buttons */
    .stRadio > div {
        gap: 10px;
    }
    
    .stRadio label {
        background: white;
        padding: 8px 20px;
        border-radius: 30px;
        border: 1px solid #dee2e6;
        transition: all 0.3s;
    }
    
    .stRadio label:hover {
        background: #e9ecef;
        transform: translateY(-2px);
    }
    
    .stRadio [data-baseweb="radio"]:checked + label {
        background: linear-gradient(135deg, #1a5f3e, #2ecc71);
        color: white;
        border: none;
    }
    
    /* Títulos */
    h1, h2, h3, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #1a5f3e !important;
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #f8f9fa, #e9ecef);
        border-radius: 10px;
        font-weight: bold;
        color: #1a5f3e;
    }
    
    /* Alertas/Snackbars */
    .stAlert {
        border-radius: 15px;
        border-left: 5px solid;
    }
    
    /* Inputs numéricos */
    div[data-baseweb="input"] input {
        border-radius: 10px !important;
        border: 1px solid #ced4da !important;
    }
    
    div[data-baseweb="input"] input:focus {
        border-color: #2ecc71 !important;
        box-shadow: 0 0 0 2px rgba(46,204,113,0.2) !important;
    }
    
    /* Sliders */
    div[data-testid="stSlider"] {
        padding: 10px 0;
    }
    
    div[data-testid="stSlider"] > div {
        background: linear-gradient(90deg, #1a5f3e, #2ecc71);
    }
    
    /* DataFrames */
    .dataframe {
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    .dataframe th {
        background: linear-gradient(135deg, #1a5f3e, #2ecc71);
        color: white;
        font-weight: bold;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8f9fa, #e9ecef);
        border-right: 1px solid #dee2e6;
    }
    
    section[data-testid="stSidebar"] .stMarkdown {
        color: #2c3e50;
    }
    
    /* Separadores */
    hr {
        margin: 2rem 0;
        background: linear-gradient(90deg, #1a5f3e, #2ecc71, #1a5f3e);
        height: 3px;
        border: none;
    }
    
    /* Cards de resultado */
    .success-box, .warning-box, .info-box {
        padding: 1.5rem;
        border-radius: 20px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .success-box {
        background: linear-gradient(135deg, #d4edda, #c3e6cb);
        border-left: 8px solid #28a745;
    }
    
    .warning-box {
        background: linear-gradient(135deg, #fff3cd, #ffeaa7);
        border-left: 8px solid #ffc107;
    }
    
    .info-box {
        background: linear-gradient(135deg, #d1ecf1, #bee5eb);
        border-left: 8px solid #17a2b8;
    }
    
    /* Métricas em grid */
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        transition: transform 0.3s;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
    }
    
    /* Footer */
    footer {
        background: linear-gradient(135deg, #1a5f3e, #2ecc71);
        color: white;
        padding: 1rem;
        border-radius: 15px;
        text-align: center;
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Footer estilizado
st.markdown("""
<footer>
    <p>🌾 Classificador de Fertilidade do Solo - Baseado no SiBCS (Embrapa)</p>
    <p style="font-size: 0.8rem;">© 2025 - Todos os direitos reservados</p>
</footer>
""", unsafe_allow_html=True)

st.markdown("---")
st.caption("© 2025 - Classificador de Fertilidade do Solo | Baseado no SiBCS - Embrapa")











