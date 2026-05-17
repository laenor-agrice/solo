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

# Inicializar session_state
if 'dados_calculados' not in st.session_state:
    st.session_state.dados_calculados = {}

if 'dados_basicos_salvos' not in st.session_state:
    st.session_state.dados_basicos_salvos = False

# ========== SEÇÃO 1: DADOS DO SOLO ==========
if menu == "📊 Dados do Solo":
    st.markdown("## 📋 Coleta de Dados do Solo")
    st.markdown("Preencha as informações básicas primeiro. Após salvar, você poderá inserir os dados de acidez e cátions.")
    
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown("### 🧪 Nutrientes e Química Básica")
        
        nitrogen = st.number_input(
            "🌱 Nitrogênio (mg/dm³)", 
            min_value=0.0, max_value=500.0, value=30.0, step=5.0,
            key="nitrogen",
            help="N disponível - análise de laboratório"
        )
        phosphorus = st.number_input(
            "🔴 Fósforo (mg/dm³)", 
            min_value=0.0, max_value=300.0, value=20.0, step=2.0,
            key="phosphorus",
            help="P disponível (Mehlich-1 ou Resina)"
        )
        potassium = st.number_input(
            "🟡 Potássio (mmolc/dm³)", 
            min_value=0.0, max_value=200.0, value=25.0, step=2.0,
            key="potassium",
            help="K trocável"
        )
        
        st.markdown("### 🧫 Matéria Orgânica")
        organic_matter = st.number_input(
            "🌿 Matéria Orgânica (g/kg)", 
            min_value=0.0, max_value=200.0, value=25.0, step=5.0,
            key="organic_matter",
            help="MO - método Walkley-Black"
        )
        
        st.markdown("### ⚖️ Densidade do Solo")
        bulk_density = st.number_input(
            "📦 Densidade do Solo (g/cm³)", 
            min_value=0.5, max_value=2.5, value=1.2, step=0.05,
            key="bulk_density",
            help="Ds - relação massa/volume total"
        )
        particle_density = st.number_input(
            "💎 Densidade de Partícula (g/cm³)", 
            min_value=2.0, max_value=3.0, value=2.65, step=0.05,
            key="particle_density",
            help="Dp - geralmente 2.65 g/cm³ para solos minerais"
        )
    
    with col2:
        st.markdown("### 🏺 Textura do Solo (Opcional)")
        st.caption("Preencha para análise completa da dinâmica de nutrientes")
        
        sand = st.number_input(
            "🏖️ Areia (g/kg)", 
            min_value=0.0, max_value=1000.0, value=350.0, step=10.0,
            key="sand",
            help="Teor de areia total"
        )
        silt = st.number_input(
            "🏞️ Silte (g/kg)", 
            min_value=0.0, max_value=1000.0, value=300.0, step=10.0,
            key="silt",
            help="Teor de silte"
        )
        clay = st.number_input(
            "🏺 Argila (g/kg)", 
            min_value=0.0, max_value=1000.0, value=350.0, step=10.0,
            key="clay",
            help="Teor de argila"
        )
        
        # Validar soma da textura
        soma_textura = sand + silt + clay
        if soma_textura > 0 and abs(soma_textura - 1000) > 10:
            st.warning(f"⚠️ A soma de areia + silte + argila é {soma_textura} g/kg. O ideal é 1000 g/kg.")
        
        st.markdown("### 🧪 pH do Solo")
        ph = st.slider(
            "🧪 pH do Solo (CaCl₂ ou H₂O)", 
            min_value=3.0, max_value=9.0, value=6.0, step=0.1,
            key="ph",
            help="Ideal para maioria das culturas: 5.5-6.5"
        )
    
    st.markdown("---")
    
    # Botão para salvar dados básicos
    if st.button("✅ Salvar Dados Básicos e Continuar", use_container_width=True):
        st.session_state.dados_basicos = {
            'nitrogen': nitrogen, 'phosphorus': phosphorus, 'potassium': potassium,
            'ph': ph, 'organic_matter': organic_matter,
            'bulk_density': bulk_density, 'particle_density': particle_density,
            'sand': sand, 'silt': silt, 'clay': clay
        }
        st.session_state.dados_basicos_salvos = True
        st.success("✅ Dados básicos salvos! Agora preencha os dados de acidez e cátions abaixo.")
    
    # ========== SEGUNDA PARTE: ACIDEZ E CÁTIONS (aparece só após salvar) ==========
    if st.session_state.dados_basicos_salvos:
        st.markdown("---")
        st.markdown("## 🔬 Dados de Acidez e Cátions Trocáveis")
        st.markdown("Preencha os dados da análise de solo para acidez e cátions.")
        
        col3, col4 = st.columns(2)
        
        with col3:
            st.markdown("### 🔬 Acidez do Solo")
            aluminum = st.number_input(
                "⚠️ Alumínio (Al³⁺) (cmolc/dm³)", 
                min_value=0.0, max_value=15.0, value=0.5, step=0.1,
                key="aluminum",
                help="Alumínio trocável - extraído com KCl 1M"
            )
            h_al = st.number_input(
                "📊 H + Al (cmolc/dm³)", 
                min_value=0.0, max_value=30.0, value=3.5, step=0.5,
                key="h_al",
                help="Acidez potencial - extraído com acetato de cálcio pH 7.0"
            )
        
        with col4:
            st.markdown("### 🧱 Cátions Trocáveis")
            calcium = st.number_input(
                "🥛 Cálcio (Ca²⁺) (cmolc/dm³)", 
                min_value=0.0, max_value=25.0, value=3.0, step=0.5,
                key="calcium",
                help="Cálcio trocável - extraído com KCl 1M"
            )
            magnesium = st.number_input(
                "🧂 Magnésio (Mg²⁺) (cmolc/dm³)", 
                min_value=0.0, max_value=15.0, value=1.5, step=0.5,
                key="magnesium",
                help="Magnésio trocável - extraído com KCl 1M"
            )
        
        if st.button("💾 Salvar Dados de Acidez e Finalizar", use_container_width=True):
            st.session_state.dados_calculados = {
                **st.session_state.dados_basicos,
                'aluminum': aluminum, 'h_al': h_al,
                'calcium': calcium, 'magnesium': magnesium
            }
            st.success("✅ Todos os dados salvos com sucesso! Vá para a aba 'Classificação'.")
    
    # Tabela de referência
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
        | **Textura** | Arenoso | Média | Argilosa | Muito Argilosa | - |
        """)

# ========== SEÇÃO 2: CLASSIFICAÇÃO ==========
elif menu == "🌱 Classificação":
    
    if not st.session_state.dados_calculados:
        st.warning("⚠️ Por favor, preencha TODOS os dados do solo primeiro na aba '📊 Dados do Solo'.")
        st.stop()
    
    dados = st.session_state.dados_calculados
    
    # ========== CÁLCULOS ==========
    # Soma de Bases (SB)
    sb = dados['calcium'] + dados['magnesium'] + dados['potassium']
    
    # CTC efetiva
    ctc_efetiva = sb + dados['aluminum']
    
    # CTC potencial
    ctc_potencial = sb + dados['h_al']
    
    # Saturação por Bases (V%)
    if ctc_potencial > 0:
        v_percent = (sb / ctc_potencial) * 100
    else:
        v_percent = 0
    
    # Saturação por Alumínio (m%)
    if ctc_efetiva > 0:
        m_percent = (dados['aluminum'] / ctc_efetiva) * 100
    else:
        m_percent = 0
    
    # Relação Ca/Mg
    if dados['magnesium'] > 0:
        ca_mg_ratio = dados['calcium'] / dados['magnesium']
    else:
        ca_mg_ratio = 0
    
    # Porosidade
    if dados['particle_density'] > 0:
        porosity = (1 - dados['bulk_density'] / dados['particle_density']) * 100
    else:
        porosity = 0
    
    # Classe textural (opcional)
    if dados.get('sand', 0) > 0 and dados.get('clay', 0) > 0:
        if dados['clay'] > 600:
            textura = "Muito Argilosa"
        elif dados['clay'] > 350:
            textura = "Argilosa"
        elif dados['clay'] > 150:
            textura = "Média"
        else:
            textura = "Arenosa"
    else:
        textura = "Não informada"
    
    # ========== EXIBIÇÃO ==========
    st.markdown("## 📊 Resultado da Classificação")
    
    # Explicação dos cálculos
    with st.expander("📐 Como os cálculos são realizados?"):
        st.markdown(f"""
        **1. Soma de Bases (SB)** = Ca²⁺ + Mg²⁺ + K⁺
        - {dados['calcium']:.2f} + {dados['magnesium']:.2f} + {dados['potassium']:.2f} = **{sb:.2f} cmolc/dm³**
        
        **2. CTC potencial** = SB + H+Al
        - {sb:.2f} + {dados['h_al']:.2f} = **{ctc_potencial:.2f} cmolc/dm³**
        
        **3. Saturação por Bases (V%)** = (SB / CTC) × 100
        - ({sb:.2f} / {ctc_potencial:.2f}) × 100 = **{v_percent:.1f}%**
        
        **4. Saturação por Alumínio (m%)** = (Al³⁺ / CTC_efetiva) × 100
        - ({dados['aluminum']:.2f} / {ctc_efetiva:.2f}) × 100 = **{m_percent:.1f}%**
        """)
    
    # Cards de métricas
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>🟢 SB</h3>
            <h2>{sb:.2f}</h2>
            <small>Soma de Bases (cmolc/dm³)</small>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>🟡 CTC</h3>
            <h2>{ctc_potencial:.2f}</h2>
            <small>CTC potencial (cmolc/dm³)</small>
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
            <small>Saturação por Alumínio</small>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Informações adicionais de textura
    st.markdown(f"""
    <div class="info-box">
        <h3>🏺 Informações Complementares</h3>
        <p><strong>Classe Textural:</strong> {textura}</p>
        <p><strong>Porosidade Total:</strong> {porosity:.1f}%</p>
        <p><strong>Relação Ca/Mg:</strong> {ca_mg_ratio:.2f} (Ideal: 2:1 a 4:1)</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Classificação do solo baseada no V%
    if v_percent >= 70:
        classe_v = "🟢 **Eutrófico (Muito Fértil)** - V% > 70%"
        cor_classe = "success-box"
    elif v_percent >= 50:
        classe_v = "🟢 **Eutrófico (Fértil)** - V% entre 50-70%"
        cor_classe = "success-box"
    elif v_percent >= 25:
        classe_v = "🟡 **Distrófico (Baixa Fertilidade)** - V% entre 25-50%"
        cor_classe = "warning-box"
    else:
        classe_v = "🔴 **Álico (Muito Pobre)** - V% < 25%"
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
    st.session_state.sb = sb

# ========== SEÇÃO 3: CALAGEM ==========
elif menu == "🧪 Calagem":
    
    if not st.session_state.dados_calculados:
        st.warning("⚠️ Por favor, preencha TODOS os dados do solo primeiro na aba '📊 Dados do Solo'.")
        st.stop()
    
    dados = st.session_state.dados_calculados
    v_percent = st.session_state.get('v_percent', 0)
    ctc_potencial = st.session_state.get('ctc_potencial', 0)
    sb = st.session_state.get('sb', 0)
    
    st.markdown("## 🧪 Recomendação de Calagem")
    
    with st.expander("📐 Como a Necessidade de Calagem é calculada?"):
        st.markdown(f"""
        **Fórmula:** NC (t/ha) = (V_desejado - V_atual) × CTC_potencial / 100
        
        - **V_atual:** {v_percent:.1f}%
        - **CTC_potencial:** {ctc_potencial:.2f} cmolc/dm³
        - **V_desejado:** Varia conforme a cultura
        """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        profundidade = st.radio(
            "📏 Profundidade de incorporação:",
            ["0-10 cm", "10-15 cm", "15-20 cm"],
            horizontal=True
        )
        fator_profundidade = {"0-10 cm": 1.0, "10-15 cm": 1.5, "15-20 cm": 2.0}
        
        prnt = st.number_input(
            "📦 PRNT do calcário (%)",
            min_value=50.0, max_value=100.0, value=85.0, step=1.0,
            help="Poder Relativo de Neutralização Total"
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
        st.warning("⚠️ Por favor, preencha TODOS os dados do solo primeiro na aba '📊 Dados do Solo'.")
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
        st.warning("⚠️ Por favor, preencha TODOS os dados do solo primeiro.")
        st.stop()
    
    st.markdown("## 📋 Relatório Completo da Análise")
    
    dados = st.session_state.dados_calculados
    v_percent = st.session_state.get('v_percent', 0)
    ctc_potencial = st.session_state.get('ctc_potencial', 0)
    sb = st.session_state.get('sb', 0)
    
    # Classe textural
    if dados.get('sand', 0) > 0 and dados.get('clay', 0) > 0:
        if dados['clay'] > 600:
            textura = "Muito Argilosa"
        elif dados['clay'] > 350:
            textura = "Argilosa"
        elif dados['clay'] > 150:
            textura = "Média"
        else:
            textura = "Arenosa"
    else:
        textura = "Não informada"
    
    resumo = pd.DataFrame({
        "Parâmetro": ["Nitrogênio (N)", "Fósforo (P)", "Potássio (K)", 
                     "Cálcio (Ca)", "Magnésio (Mg)", "pH", "Alumínio (Al³⁺)",
                     "H + Al", "Soma de Bases (SB)", "CTC Potencial",
                     "Saturação por Bases (V%)", "Matéria Orgânica",
                     "Densidade do Solo", "Classe Textural", "Relação Ca/Mg"],
        "Valor": [f"{dados['nitrogen']:.1f} mg/dm³", f"{dados['phosphorus']:.1f} mg/dm³",
                 f"{dados['potassium']:.1f} mmolc/dm³", f"{dados['calcium']:.1f} cmolc/dm³",
                 f"{dados['magnesium']:.1f} cmolc/dm³", f"{dados['ph']:.1f}",
                 f"{dados['aluminum']:.2f} cmolc/dm³", f"{dados['h_al']:.2f} cmolc/dm³",
                 f"{sb:.2f} cmolc/dm³", f"{ctc_potencial:.2f} cmolc/dm³",
                 f"{v_percent:.1f}%", f"{dados['organic_matter']:.1f} g/kg",
                 f"{dados['bulk_density']:.2f} g/cm³", textura,
                 f"{dados['calcium']/dados['magnesium']:.2f}" if dados['magnesium'] > 0 else "N/A"]
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
    /* Garantir texto branco em todo o conteúdo escuro */
    .stMarkdown p, .stMarkdown li, .stMarkdown span, .stMarkdown div {
        color: #ffffff !important;
    }
    
    /* Métricas */
    div[data-testid="stMetric"] label {
        color: #a8e6cf !important;
        font-weight: bold !important;
    }
    
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #2ecc71 !important;
        font-size: 2rem !important;
        font-weight: 900 !important;
    }
    
    /* Alertas */
    .stAlert p, .stAlert li {
        color: #1a2a1a !important;
    }
    
    /* Expanders */
    .streamlit-expanderHeader p {
        color: white !important;
    }
    
    .streamlit-expanderContent p, .streamlit-expanderContent li {
        color: #1a2a1a !important;
    }
    
    /* Labels */
    label, .stSlider label, .stNumberInput label, .stSelectbox label, .stRadio label {
        color: #a8e6cf !important;
        font-weight: 600 !important;
    }
    
    /* Inputs */
    input {
        color: white !important;
        background-color: #2c3e50 !important;
       
