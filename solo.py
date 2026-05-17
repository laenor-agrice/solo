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
    .result-card {
        background: linear-gradient(135deg, #1a5f3e, #2ecc71);
        padding: 1.5rem;
        border-radius: 20px;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    }
    .result-card h2, .result-card h3, .result-card p {
        color: white !important;
        margin: 0;
    }
    .result-number {
        font-size: 3rem;
        font-weight: bold;
        color: #f1c40f;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
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
    .stAlert {
        border-radius: 15px;
        border-left: 5px solid;
        padding: 1rem;
    }
    .stAlert p {
        font-size: 1rem;
        line-height: 1.5;
    }
    .highlight {
        font-size: 2.5rem;
        font-weight: bold;
        color: #f1c40f;
    }
    .subtext {
        font-size: 0.9rem;
        color: #a8e6cf;
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
    
    # Cards de métricas
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>🟢 Soma de Bases</h3>
            <h2>{sb:.2f}</h2>
            <small>cmolc/dm³</small>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>🟡 CTC Potencial</h3>
            <h2>{ctc_potencial:.2f}</h2>
            <small>cmolc/dm³</small>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>🟢 Saturação por Bases</h3>
            <h2>{v_percent:.1f}%</h2>
            <small>V%</small>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3>🔴 Saturação por Al</h3>
            <h2>{m_percent:.1f}%</h2>
            <small>m%</small>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Informações complementares
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info(f"🏺 **Classe Textural:** {textura}")
    with col2:
        st.info(f"⚖️ **Porosidade:** {porosity:.1f}%")
    with col3:
        st.info(f"📊 **Relação Ca/Mg:** {ca_mg_ratio:.2f} (Ideal: 2:1 a 4:1)")
    
    st.markdown("---")
    
    # Classificação V%
    if v_percent >= 70:
        classe_v = "Eutrófico (Muito Fértil)"
        cor_classe = "success-box"
        emoji = "🟢"
        recomendacao = "Solo excelente! Mantenha os níveis com adubações de manutenção."
    elif v_percent >= 50:
        classe_v = "Eutrófico (Fértil)"
        cor_classe = "success-box"
        emoji = "🟢"
        recomendacao = "Solo fértil, apto para cultivo de alta produtividade."
    elif v_percent >= 25:
        classe_v = "Distrófico (Baixa Fertilidade)"
        cor_classe = "warning-box"
        emoji = "🟡"
        recomendacao = "Solo com baixa fertilidade natural. Recomenda-se calagem e adubação corretiva."
    else:
        classe_v = "Álico (Muito Pobre)"
        cor_classe = "info-box"
        emoji = "🔴"
        recomendacao = "Solo muito pobre. Necessita correção intensiva com calagem e gessagem."
    
    st.markdown(f"""
    <div class="{cor_classe}">
        <h3>{emoji} Classificação SiBCS: {classe_v}</h3>
        <p><strong>V% atual:</strong> {v_percent:.1f}%</p>
        <p>{recomendacao}</p>
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
    
    # Resultado final
    if score >= 12:
        st.markdown(f"""
        <div class="result-card">
            <h2>🟢 RESULTADO: ALTA FERTILIDADE</h2>
            <p class="result-number">Score: {score:.1f} / 20 pontos</p>
            <p>✅ Solo fértil segundo critérios do SiBCS. Apto para cultivo de alta produtividade.</p>
        </div>
        """, unsafe_allow_html=True)
    elif score >= 7:
        st.markdown(f"""
        <div class="result-card" style="background: linear-gradient(135deg, #856404, #ffc107);">
            <h2>🟡 RESULTADO: FERTILIDADE MÉDIA</h2>
            <p class="result-number">Score: {score:.1f} / 20 pontos</p>
            <p>⚠️ Solo com potencial, mas necessita manejo adequado e correções localizadas.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="result-card" style="background: linear-gradient(135deg, #721c24, #e74c3c);">
            <h2>🔴 RESULTADO: BAIXA FERTILIDADE</h2>
            <p class="result-number">Score: {score:.1f} / 20 pontos</p>
            <p>❌ Solo necessita correção e manejo intensivo. Recomenda-se calagem e adubação.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Salvar para outras abas
    st.session_state.v_percent = v_percent
    st.session_state.ctc_potencial = ctc_potencial
    st.session_state.m_percent = m_percent
    st.session_state.sb = sb
    st.session_state.score = score

# ========== SEÇÃO 3: CALAGEM ==========
elif menu == "🧪 Calagem":
    
    if not st.session_state.dados_calculados:
        st.warning("⚠️ Por favor, preencha e salve os dados do solo primeiro na aba '📊 Dados do Solo'.")
        st.stop()
    
    v_percent = st.session_state.get('v_percent', 0)
    ctc_potencial = st.session_state.get('ctc_potencial', 0)
    score = st.session_state.get('score', 0)
    
    st.markdown("## 🧪 Recomendação de Calagem Agrícola")
    st.markdown("A calagem é a prática de aplicação de calcário para corrigir a acidez do solo e elevar a saturação por bases.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        profundidade = st.radio(
            "📏 Profundidade de incorporação:",
            ["0-10 cm", "10-15 cm", "15-20 cm"],
            horizontal=True
        )
        fator_profundidade = {"0-10 cm": 1.0, "10-15 cm": 1.5, "15-20 cm": 2.0}
        prnt = st.number_input("📦 PRNT do calcário (%)", min_value=50.0, max_value=100.0, value=85.0, step=1.0,
                               help="Poder Relativo de Neutralização Total - informado na nota fiscal do calcário")
    
    with col2:
        cultura = st.selectbox("🌾 Cultura a ser cultivada:", [
            "Soja", "Milho", "Feijão", "Trigo", "Arroz", "Café", "Cana-de-açúcar",
            "Pastagem", "Batata", "Mandioca", "Tomate", "Alface", "Cebola", "Algodão"
        ])
    
    v_desejado_culturas = {
        "Soja": 60, "Milho": 65, "Feijão": 65, "Trigo": 65, "Arroz": 55,
        "Café": 70, "Cana-de-açúcar": 60, "Pastagem": 55, "Batata": 65,
        "Mandioca": 55, "Tomate": 70, "Alface": 65, "Cebola": 65, "Algodão": 65
    }
    v_desejado = v_desejado_culturas.get(cultura, 60)
    
    # Exibir situação atual
    st.markdown("---")
    st.markdown("### 📊 Situação Atual do Solo")
    
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("📌 V% atual", f"{v_percent:.1f}%", delta=f"Faltam {max(0, v_desejado - v_percent):.1f}% para o ideal")
    with col_b:
        st.metric("🎯 V% desejado para " + cultura, f"{v_desejado}%")
    with col_c:
        st.metric("🧮 CTC potencial", f"{ctc_potencial:.2f} cmolc/dm³")
    
    st.markdown("---")
    
    if v_percent < v_desejado:
        nc = (v_desejado - v_percent) * ctc_potencial / 100
        nc_corrigido = nc * (100 / prnt)
        nc_final = nc_corrigido * fator_profundidade[profundidade]
        
        st.markdown(f"""
        <div class="warning-box">
            <h3 style="color: #856404;">⚠️ É RECOMENDADO CALAGEM</h3>
            <p><strong>Motivo:</strong> V% atual ({v_percent:.1f}%) está abaixo do ideal para {cultura} ({v_desejado}%)</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Card com resultado
        st.markdown(f"""
        <div class="result-card" style="background: linear-gradient(135deg, #1a5f3e, #2ecc71);">
            <h2>📦 QUANTIDADE DE CALCÁRIO</h2>
            <p class="result-number">{nc_final:.1f} t/ha</p>
            <p>Considerando profundidade de {profundidade} e PRNT = {prnt:.0f}%</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("📖 Ver detalhes do cálculo"):
            st.markdown(f"""
            **Passo a passo do cálculo:**
            
            1. **Necessidade de calagem base (0-10cm, PRNT 100%):**
               - NC = (V_desejado - V_atual) × CTC / 100
               - NC = ({v_desejado} - {v_percent:.1f}) × {ctc_potencial:.2f} / 100
               - NC = **{nc:.2f} t/ha**
            
            2. **Ajuste pelo PRNT do calcário ({prnt:.0f}%):**
               - NC_corrigido = NC × (100 / PRNT)
               - NC_corrigido = {nc:.2f} × (100 / {prnt:.0f})
               - NC_corrigido = **{nc_corrigido:.2f} t/ha**
            
            3. **Ajuste pela profundidade ({profundidade}):**
               - NC_final = NC_corrigido × Fator_profundidade
               - NC_final = {nc_corrigido:.2f} × {fator_profundidade[profundidade]}
               - NC_final = **{nc_final:.2f} t/ha**
            """)
        
        with st.expander("📖 Recomendações de Aplicação"):
            st.markdown(f"""
            ✅ **Época ideal:** 60-90 dias antes do plantio
            ✅ **Incorporação:** Incorporar na profundidade de {profundidade}
            ✅ **PRNT utilizado:** {prnt:.0f}%
            ✅ **Resultado esperado:** Solo atingirá V% = {v_desejado}%
            ✅ **Umidade do solo:** Aplicar com solo úmido para melhor reação
            ✅ **Uniformidade:** Distribuir uniformemente em área total
            """)
    else:
        st.markdown(f"""
        <div class="success-box">
            <h3 style="color: #155724;">✅ NÃO HÁ NECESSIDADE DE CALAGEM</h3>
            <p>V% atual ({v_percent:.1f}%) já está no nível ideal para {cultura} ({v_desejado}%)</p>
            <p>O solo já apresenta boas condições de fertilidade para a cultura selecionada.</p>
        </div>
        """, unsafe_allow_html=True)

# ========== SEÇÃO 4: GESSAGEM ==========
elif menu == "⚖️ Gessagem":
    
    if not st.session_state.dados_calculados:
        st.warning("⚠️ Por favor, preencha e salve os dados do solo primeiro na aba '📊 Dados do Solo'.")
        st.stop()
    
    dados = st.session_state.dados_calculados
    m_percent = st.session_state.get('m_percent', 0)
    v_percent = st.session_state.get('v_percent', 0)
    
    st.markdown("## ⚖️ Recomendação de Gessagem Agrícola")
    st.markdown("A gessagem é indicada para solos com problemas de alumínio tóxico ou cálcio deficiente em profundidade.")
    
    # Cards com indicadores atuais
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("⚠️ Alumínio (Al³⁺)", f"{dados['aluminum']:.2f} cmolc/dm³", 
                  delta="Ideal: < 0.5", delta_color="inverse")
    with col2:
        st.metric("🥛 Cálcio (Ca²⁺)", f"{dados['calcium']:.2f} cmolc/dm³",
                  delta="Ideal: > 1.5", delta_color="inverse")
    with col3:
        st.metric("📊 Saturação Al (m%)", f"{m_percent:.1f}%",
                  delta="Ideal: < 20%", delta_color="inverse")
    with col4:
        st.metric("🟢 V% atual", f"{v_percent:.1f}%")
    
    st.markdown("---")
    
    # Verificar necessidade
    motivos = []
    if dados['aluminum'] > 0.5:
        motivos.append(f"• Alumínio alto: {dados['aluminum']:.2f} cmolc/dm³ (limite ideal: ≤ 0.5)")
    if dados['calcium'] < 1.0:
        motivos.append(f"• Cálcio muito baixo: {dados['calcium']:.2f} cmolc/dm³ (limite ideal: ≥ 1.5)")
    if m_percent > 20:
        motivos.append(f"• Saturação por Alumínio alta: {m_percent:.1f}% (limite ideal: ≤ 20%)")
    if v_percent < 35 and dados['aluminum'] > 0.3:
        motivos.append("• Subsuperfície provavelmente ácida (V% baixo + Al³⁺ presente)")
    
    if motivos:
        # Cálculo da necessidade de gessagem
        ng_al = dados['aluminum'] * 1.5
        if dados['calcium'] < 2.0:
            ng_ca = (2.0 - dados['calcium']) * 1.5
        else:
            ng_ca = 0
        ng_total = ng_al + ng_ca
        
        st.markdown(f"""
        <div class="warning-box">
            <h3 style="color: #856404;">⚠️ É RECOMENDADO GESSAGEM</h3>
            <p><strong>Motivo(s):</strong></p>
        </div>
        """, unsafe_allow_html=True)
        
        for motivo in motivos:
            st.warning(motivo)
        
        # Card com resultado
        st.markdown(f"""
        <div class="result-card" style="background: linear-gradient(135deg, #1a5f3e, #2ecc71);">
            <h2>📦 QUANTIDADE DE GESSO AGRÍCOLA</h2>
            <p class="result-number">{ng_total:.1f} t/ha</p>
            <p>Considerando aplicação superficial (sem incorporação)</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("📖 Ver detalhes do cálculo"):
            st.markdown(f"""
            **Cálculo da necessidade de gessagem (método Embrapa):**
            
            1. **Necessidade para neutralizar Al³⁺:**
               - NG_Al = Al³⁺ × 1.5
               - NG_Al = {dados['aluminum']:.2f} × 1.5 = **{ng_al:.2f} t/ha**
            
            2. **Necessidade para suprir Cálcio (se Ca²⁺ < 2.0):**
               - NG_Ca = (2.0 - Ca²⁺) × 1.5
               - NG_Ca = (2.0 - {dados['calcium']:.2f}) × 1.5 = **{ng_ca:.2f} t/ha**
            
            3. **Necessidade total:**
               - NG_total = NG_Al + NG_Ca
               - NG_total = {ng_al:.2f} + {ng_ca:.2f} = **{ng_total:.2f} t/ha**
            """)
        
        with st.expander("📖 Recomendações de Aplicação"):
            st.markdown("""
            ✅ **Época:** Aplicar após a calagem (30-60 dias de intervalo)
            ✅ **Aplicação:** A lanço, SEM incorporar (deixar na superfície)
            ✅ **Benefícios:** Neutraliza Al³⁺ em profundidade, fornece Ca²⁺ e S
            ✅ **Profundidade de ação:** Atua até 40cm de profundidade
            ✅ **Cuidado:** Não exagerar na dose para evitar lixiviação de bases
            """)
    else:
        st.markdown(f"""
        <div class="success-box">
            <h3 style="color: #155724;">✅ NÃO HÁ NECESSIDADE DE GESSAGEM</h3>
            <p>Os parâmetros estão dentro dos limites ideais:</p>
            <p>• Al³⁺ = {dados['aluminum']:.2f} cmolc/dm³ (≤ 0.5)</p>
            <p>• Ca²⁺ = {dados['calcium']:.2f} cmolc/dm³ (≥ 1.5)</p>
            <p>• m% = {m_percent:.1f}% (≤ 20%)</p>
        </div>
        """, unsafe_allow_html=True)

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
    score = st
