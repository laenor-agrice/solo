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

# Menu com radio buttons
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

# Inicializar session_state com valores padrão
if 'dados_calculados' not in st.session_state:
    st.session_state.dados_calculados = {}

if 'dados_basicos_salvos' not in st.session_state:
    st.session_state.dados_basicos_salvos = False

# ========== SEÇÃO 1: DADOS DO SOLO ==========
if menu == "📊 Dados do Solo":
    st.markdown("## 📋 Coleta de Dados do Solo")
    st.markdown("Preencha todas as informações abaixo. Após salvar, os dados serão usados nas outras abas.")
    
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown("### 🧪 Nutrientes e Química Básica")
        
        nitrogen = st.text_input(
            "🌱 Nitrogênio (mg/dm³)", 
            value=str(st.session_state.dados_calculados.get('nitrogen', '30.0')),
            key="nitrogen_input"
        )
        
        phosphorus = st.text_input(
            "🔴 Fósforo (mg/dm³)", 
            value=str(st.session_state.dados_calculados.get('phosphorus', '20.0')),
            key="phosphorus_input"
        )
        
        potassium = st.text_input(
            "🟡 Potássio (mmolc/dm³)", 
            value=str(st.session_state.dados_calculados.get('potassium', '25.0')),
            key="potassium_input"
        )
        
        st.markdown("### 🧫 Matéria Orgânica")
        organic_matter = st.text_input(
            "🌿 Matéria Orgânica (g/kg)", 
            value=str(st.session_state.dados_calculados.get('organic_matter', '25.0')),
            key="organic_matter_input"
        )
        
        st.markdown("### ⚖️ Densidade do Solo")
        bulk_density = st.text_input(
            "📦 Densidade do Solo (g/cm³)", 
            value=str(st.session_state.dados_calculados.get('bulk_density', '1.20')),
            key="bulk_density_input"
        )
        particle_density = st.text_input(
            "💎 Densidade de Partícula (g/cm³)", 
            value=str(st.session_state.dados_calculados.get('particle_density', '2.65')),
            key="particle_density_input"
        )
    
    with col2:
        st.markdown("### 🏺 Textura do Solo (Opcional)")
        st.caption("Preencha para análise da dinâmica de nutrientes")
        
        sand = st.text_input(
            "🏖️ Areia (g/kg)", 
            value=str(st.session_state.dados_calculados.get('sand', '350.0')),
            key="sand_input"
        )
        silt = st.text_input(
            "🏞️ Silte (g/kg)", 
            value=str(st.session_state.dados_calculados.get('silt', '300.0')),
            key="silt_input"
        )
        clay = st.text_input(
            "🏺 Argila (g/kg)", 
            value=str(st.session_state.dados_calculados.get('clay', '350.0')),
            key="clay_input"
        )
        
        st.markdown("### 🧪 pH do Solo")
        ph = st.text_input(
            "🧪 pH do Solo (CaCl₂ ou H₂O)", 
            value=str(st.session_state.dados_calculados.get('ph', '6.0')),
            key="ph_input"
        )
        
        st.markdown("### 🔬 Acidez do Solo")
        aluminum = st.text_input(
            "⚠️ Alumínio (Al³⁺) (cmolc/dm³)", 
            value=str(st.session_state.dados_calculados.get('aluminum', '0.50')),
            key="aluminum_input"
        )
        h_al = st.text_input(
            "📊 H + Al (cmolc/dm³)", 
            value=str(st.session_state.dados_calculados.get('h_al', '3.50')),
            key="h_al_input"
        )
        
        st.markdown("### 🧱 Cátions Trocáveis")
        calcium = st.text_input(
            "🥛 Cálcio (Ca²⁺) (cmolc/dm³)", 
            value=str(st.session_state.dados_calculados.get('calcium', '3.00')),
            key="calcium_input"
        )
        magnesium = st.text_input(
            "🧂 Magnésio (Mg²⁺) (cmolc/dm³)", 
            value=str(st.session_state.dados_calculados.get('magnesium', '1.50')),
            key="magnesium_input"
        )
    
    st.markdown("---")
    
    # Botão para salvar
    if st.button("💾 SALVAR TODOS OS DADOS", use_container_width=True):
        try:
            st.session_state.dados_calculados = {
                'nitrogen': float(nitrogen.replace(',', '.')),
                'phosphorus': float(phosphorus.replace(',', '.')),
                'potassium': float(potassium.replace(',', '.')),
                'ph': float(ph.replace(',', '.')),
                'organic_matter': float(organic_matter.replace(',', '.')),
                'bulk_density': float(bulk_density.replace(',', '.')),
                'particle_density': float(particle_density.replace(',', '.')),
                'sand': float(sand.replace(',', '.')),
                'silt': float(silt.replace(',', '.')),
                'clay': float(clay.replace(',', '.')),
                'aluminum': float(aluminum.replace(',', '.')),
                'h_al': float(h_al.replace(',', '.')),
                'calcium': float(calcium.replace(',', '.')),
                'magnesium': float(magnesium.replace(',', '.'))
            }
            st.session_state.dados_basicos_salvos = True
            st.success("✅ Todos os dados salvos com sucesso! Vá para a aba 'Classificação'.")
        except ValueError as e:
            st.error(f"❌ Erro ao converter dados. Use números com ponto decimal (ex: 1.5). Erro: {e}")
    
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
        st.warning("⚠️ Por favor, preencha e salve os dados do solo primeiro na aba '📊 Dados do Solo'.")
        st.stop()
    
    dados = st.session_state.dados_calculados
    
    # Cálculos
    sb = dados['calcium'] + dados['magnesium'] + dados['potassium']
    ctc_efetiva = sb + dados['aluminum']
    ctc_potencial = sb + dados['h_al']
    
    if ctc_potencial > 0:
        v_percent = (sb / ctc_potencial) * 100
    else:
        v_percent = 0
    
    if ctc_efetiva > 0:
        m_percent = (dados['aluminum'] / ctc_efetiva) * 100
    else:
        m_percent = 0
    
    if dados['magnesium'] > 0:
        ca_mg_ratio = dados['calcium'] / dados['magnesium']
    else:
        ca_mg_ratio = 0
    
    if dados['particle_density'] > 0:
        porosity = (1 - dados['bulk_density'] / dados['particle_density']) * 100
    else:
        porosity = 0
    
    # Classe textural
    if dados.get('clay', 0) > 600:
        textura = "Muito Argilosa"
    elif dados.get('clay', 0) > 350:
        textura = "Argilosa"
    elif dados.get('clay', 0) > 150:
        textura = "Média"
    else:
        textura = "Arenosa" if dados.get('clay', 0) > 0 else "Não informada"
    
    st.markdown("## 📊 Resultado da Classificação")
    
    with st.expander("📐 Como os cálculos são realizados?"):
        st.markdown(f"""
        **1. Soma de Bases (SB)** = Ca²⁺ + Mg²⁺ + K⁺ = **{sb:.2f} cmolc/dm³**
        **2. CTC potencial** = SB + H+Al = **{ctc_potencial:.2f} cmolc/dm³**
        **3. Saturação por Bases (V%)** = (SB / CTC) × 100 = **{v_percent:.1f}%**
        **4. Saturação por Alumínio (m%)** = (Al³⁺ / CTC_efetiva) × 100 = **{m_percent:.1f}%**
        """)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🟢 SB", f"{sb:.2f} cmolc/dm³")
    with col2:
        st.metric("🟡 CTC", f"{ctc_potencial:.2f} cmolc/dm³")
    with col3:
        st.metric("🟢 V%", f"{v_percent:.1f}%")
    with col4:
        st.metric("🔴 m%", f"{m_percent:.1f}%")
    
    st.markdown("---")
    
    st.markdown(f"""
    <div class="info-box">
        <h3>🏺 Informações Complementares</h3>
        <p><strong>Classe Textural:</strong> {textura}</p>
        <p><strong>Porosidade Total:</strong> {porosity:.1f}%</p>
        <p><strong>Relação Ca/Mg:</strong> {ca_mg_ratio:.2f} (Ideal: 2:1 a 4:1)</p>
    </div>
    """, unsafe_allow_html=True)
    
    if v_percent >= 70:
        classe_v = "🟢 Eutrófico (Muito Fértil) - V% > 70%"
        cor_classe = "success-box"
    elif v_percent >= 50:
        classe_v = "🟢 Eutrófico (Fértil) - V% entre 50-70%"
        cor_classe = "success-box"
    elif v_percent >= 25:
        classe_v = "🟡 Distrófico (Baixa Fertilidade) - V% entre 25-50%"
        cor_classe = "warning-box"
    else:
        classe_v = "🔴 Álico (Muito Pobre) - V% < 25%"
        cor_classe = "info-box"
    
    st.markdown(f"""
    <div class="{cor_classe}">
        <h3>📌 Classificação do Solo (SiBCS)</h3>
        <p>{classe_v}</p>
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
    
    st.markdown("---")
    
    if score >= 12:
        st.markdown(f"""
        <div class="success-box">
            <h2 style="color: #155724;">🟢 RESULTADO: ALTA FERTILIDADE</h2>
            <p>Score: {score:.1f}/20 pontos</p>
            <p>✅ Solo fértil segundo critérios do SiBCS.</p>
        </div>
        """, unsafe_allow_html=True)
    elif score >= 7:
        st.markdown(f"""
        <div class="warning-box">
            <h2 style="color: #856404;">🟡 RESULTADO: FERTILIDADE MÉDIA</h2>
            <p>Score: {score:.1f}/20 pontos</p>
            <p>⚠️ Necessita manejo adequado.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="info-box">
            <h2 style="color: #721c24;">🔴 RESULTADO: BAIXA FERTILIDADE</h2>
            <p>Score: {score:.1f}/20 pontos</p>
            <p>❌ Correção do solo necessária.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Salvar para outras abas
    st.session_state.v_percent = v_percent
    st.session_state.ctc_potencial = ctc_potencial
    st.session_state.m_percent = m_percent
    st.session_state.sb = sb

# ========== SEÇÃO 3: CALAGEM ==========
elif menu == "🧪 Calagem":
    
    if not st.session_state.dados_calculados:
        st.warning("⚠️ Por favor, preencha e salve os dados do solo primeiro na aba '📊 Dados do Solo'.")
        st.stop()
    
    v_percent = st.session_state.get('v_percent', 0)
    ctc_potencial = st.session_state.get('ctc_potencial', 0)
    
    st.markdown("## 🧪 Recomendação de Calagem")
    
    col1, col2 = st.columns(2)
    
    with col1:
        profundidade = st.radio(
            "Profundidade de incorporação:",
            ["0-10 cm", "10-15 cm", "15-20 cm"],
            horizontal=True
        )
        fator_profundidade = {"0-10 cm": 1.0, "10-15 cm": 1.5, "15-20 cm": 2.0}
        prnt = st.number_input("PRNT do calcário (%)", min_value=50.0, max_value=100.0, value=85.0, step=1.0)
    
    with col2:
        cultura = st.selectbox("Cultura a ser cultivada:", [
            "Soja", "Milho", "Feijão", "Trigo", "Arroz", "Café", "Cana-de-açúcar",
            "Pastagem", "Batata", "Mandioca", "Tomate", "Alface"
        ])
    
    v_desejado_culturas = {
        "Soja": 60, "Milho": 65, "Feijão": 65, "Trigo": 65, "Arroz": 55,
        "Café": 70, "Cana-de-açúcar": 60, "Pastagem": 55, "Batata": 65,
        "Mandioca": 55, "Tomate": 70, "Alface": 65
    }
    v_desejado = v_desejado_culturas.get(cultura, 60)
    
    st.info(f"📌 {cultura} - V% desejado: {v_desejado}% | V% atual: {v_percent:.1f}%")
    
    st.markdown("---")
    
    if v_percent < v_desejado:
        nc = (v_desejado - v_percent) * ctc_potencial / 100
        nc_corrigido = nc * (100 / prnt)
        nc_final = nc_corrigido * fator_profundidade[profundidade]
        
        st.warning("⚠️ É RECOMENDADO CALAGEM")
        st.success(f"✅ Quantidade final de calcário: {nc_final:.1f} t/ha")
        
        with st.expander("📖 Recomendações de Aplicação"):
            st.markdown(f"""
            - **Época ideal:** 60-90 dias antes do plantio
            - **Incorporação:** Incorporar na profundidade de {profundidade}
            - **PRNT utilizado:** {prnt:.0f}%
            - **Resultado esperado:** Solo atingirá V% = {v_desejado}%
            """)
    else:
        st.success("✅ NÃO HÁ NECESSIDADE DE CALAGEM")
        st.write(f"V% atual ({v_percent:.1f}%) já está no nível ideal para {cultura} ({v_desejado}%)")

# ========== SEÇÃO 4: GESSAGEM ==========
elif menu == "⚖️ Gessagem":
    
    if not st.session_state.dados_calculados:
        st.warning("⚠️ Por favor, preencha e salve os dados do solo primeiro na aba '📊 Dados do Solo'.")
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
        
        st.warning("⚠️ É RECOMENDADO GESSAGEM")
        st.success(f"✅ Quantidade de gesso agrícola: {ng_total:.1f} t/ha")
        
        with st.expander("📖 Recomendações de Aplicação"):
            st.markdown("""
            - **Época:** Aplicar após a calagem (30-60 dias de intervalo)
            - **Aplicação:** A lanço, SEM incorporar (deixar na superfície)
            - **Benefícios:** Neutraliza Al³⁺ em profundidade, fornece Ca²⁺ e S
            """)
    else:
        st.success("✅ NÃO HÁ NECESSIDADE DE GESSAGEM")
        st.write("Os parâmetros estão dentro dos limites ideais.")

# ========== SEÇÃO 5: RELATÓRIO ==========
elif menu == "📈 Relatório":
    
    if not st.session_state.dados_calculados:
        st.warning("⚠️ Por favor, preencha e salve os dados do solo primeiro na aba '📊 Dados do Solo'.")
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
        "Valor": [f"{dados['nitrogen']:.1f} mg/dm³", f"{dados['phosphorus']:.1f} mg/dm³",
                 f"{dados['potassium']:.1f} mmolc/dm³", f"{dados['calcium']:.1f} cmolc/dm³",
                 f"{dados['magnesium']:.1f} cmolc/dm³", f"{dados['ph']:.1f}",
                 f"{dados['aluminum']:.2f} cmolc/dm³", f"{dados['h_al']:.2f} cmolc/dm³",
                 f"{sb:.2f} cmolc/dm³", f"{ctc_potencial:.2f} cmolc/dm³",
                 f"{v_percent:.1f}%", f"{dados['organic_matter']:.1f} g/kg",
                 f"{dados['bulk_density']:.2f} g/cm³",
                 f"{dados['sand']:.1f} g/kg", f"{dados['silt']:.1f} g/kg",
                 f"{dados['clay']:.1f} g/kg"]
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

# ========== CORREÇÃO DE VISIBILIDADE ==========
st.markdown("""
<style>
    .stMarkdown p, .stMarkdown li { color: #ffffff !important; }
    div[data-testid="stMetric"] label { color: #a8e6cf !important; font-weight: bold !important; }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] { color: #2ecc71 !important; font-size: 1.5rem !important; font-weight: 900 !important; }
    .stAlert p, .stAlert li { color: #1a2a1a !important; }
    .streamlit-expanderHeader p { color: white !important; }
    .streamlit-expanderContent p, .streamlit-expanderContent li { color: #1a2a1a !important; }
    label, .stSlider label, .stNumberInput label, .stSelectbox label, .stRadio label { color: #a8e6cf !important; font-weight: 600 !important; }
    input { color: white !important; background-color: #2c3e50 !important; border: 1px solid #2ecc71 !important; border-radius: 8px !important; }
    h1, h2, h3, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 { color: #2ecc71 !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("---")
st.caption("© 2025 - Classificador de Fertilidade do Solo | Baseado no SiBCS - Embrapa")
