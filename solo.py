import streamlit as st
import pandas as pd
import traceback
import sys
import math

# ============================================================================
# FUNÇÃO PARA CALCULAR pH BASEADO NOS NUTRIENTES (CORRIGIDA)
# ============================================================================

def calcular_ph(dados):
    """
    Calcula o pH do solo com base nos nutrientes e matéria orgânica
    Fórmula adaptada para solos tropicais
    """
    try:
        # Verificar se todos os valores são zero
        if (dados.get('calcium', 0) == 0 and 
            dados.get('magnesium', 0) == 0 and 
            dados.get('potassium', 0) == 0 and
            dados.get('aluminum', 0) == 0 and
            dados.get('h_al', 0) == 0):
            return 7.0  # Solo neutro quando tudo está zerado
        
        # Fatores de acidez (contribuem para pH baixo)
        fator_acidez = (
            dados.get('aluminum', 0.5) * 0.3 +
            dados.get('h_al', 3.5) * 0.1
        )
        
        # Fatores de basicidade (contribuem para pH alto)
        fator_basicidade = (
            dados.get('calcium', 3.0) * 0.2 +
            dados.get('magnesium', 1.5) * 0.15 +
            dados.get('potassium', 0.25) * 0.5
        )
        
        # Matéria orgânica (pode acidificar ou tamponar)
        om = dados.get('organic_matter', 25) / 100
        
        # Cálculo do pH base
        ph_base = 5.5 + (fator_basicidade - fator_acidez) - (om * 0.5)
        
        # Limitar o pH entre 4.0 e 8.0
        ph = max(4.0, min(8.0, ph_base))
        
        return round(ph, 1)
    
    except Exception:
        return 7.0  # Valor padrão neutro

# ============================================================================
# FUNÇÃO PARA CALCULAR ADUBAÇÃO PARA VASO
# ============================================================================

def calcular_adubacao_vaso(area_vaso_m2, recomendacao_kg_ha, fator_cultura=1.0):
    """
    Calcula a quantidade de adubo para um vaso baseado na recomendação por hectare
    
    Parâmetros:
    - area_vaso_m2: área do vaso em metros quadrados
    - recomendacao_kg_ha: recomendação de adubo em kg/ha
    - fator_cultura: fator de correção por cultura (ex: soja fixa N, então precisa menos)
    
    Retorna:
    - quantidade em gramas para o vaso
    """
    # 1 hectare = 10.000 m²
    # kg/ha para kg/m²
    kg_por_m2 = recomendacao_kg_ha / 10000
    
    # kg para o vaso
    kg_vaso = kg_por_m2 * area_vaso_m2
    
    # Converter para gramas e aplicar fator de cultura
    gramas_vaso = kg_vaso * 1000 * fator_cultura
    
    return round(gramas_vaso, 2)

# ============================================================================
# TRATAMENTO DE ERROS DE IMPORTAÇÃO
# ============================================================================

try:
    import joblib
    JOBLIB_AVAILABLE = True
except ImportError:
    JOBLIB_AVAILABLE = False
    joblib = None

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None

# ============================================================================
# FUNÇÃO PARA CARREGAR MODELO
# ============================================================================

@st.cache_resource
def carregar_modelo():
    """Carrega o modelo e features com tratamento de erro"""
    
    if not JOBLIB_AVAILABLE:
        st.warning("⚠️ Biblioteca 'joblib' não encontrada. Instale com: pip install joblib")
        return None, None
    
    try:
        import os
        
        if not os.path.exists('modelo.pkl'):
            st.warning("⚠️ Arquivo 'modelo.pkl' não encontrado!")
            return None, None
        
        if not os.path.exists('features.pkl'):
            st.warning("⚠️ Arquivo 'features.pkl' não encontrado!")
            return None, None
        
        modelo = joblib.load('modelo.pkl')
        features = joblib.load('features.pkl')
        
        st.sidebar.info(f"📊 Modelo treinado com {len(features)} features")
        
        return modelo, features
    
    except Exception as e:
        st.error(f"❌ Erro ao carregar o modelo: {str(e)}")
        return None, None

modelo, features = carregar_modelo()

# ============================================================================
# CONFIGURACAO DA PAGINA
# ============================================================================

st.set_page_config(
    page_title="Classificador de Fertilidade do Solo - SiBCS",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CSS PERSONALIZADO - DESIGN MODERNO
# ============================================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

* {
    font-family: 'Outfit', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #f5f7fa 0%, #eef2f7 100%) !important;
}

.main .block-container {
    background: rgba(255, 255, 255, 0.92) !important;
    backdrop-filter: blur(10px) !important;
    border-radius: 32px !important;
    padding: 2rem !important;
    margin-top: 1rem !important;
    margin-bottom: 2rem !important;
    box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.08) !important;
    border: 1px solid rgba(255, 255, 255, 0.3) !important;
}

h1, h2, h3 {
    background: linear-gradient(120deg, #2d5a3b 0%, #4a8c5c 100%) !important;
    -webkit-background-clip: text !important;
    background-clip: text !important;
    color: transparent !important;
    font-weight: 700 !important;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a3022 0%, #0e1e14 100%) !important;
    border-right: none !important;
    box-shadow: 4px 0 20px rgba(0, 0, 0, 0.05) !important;
}

section[data-testid="stSidebar"] * {
    color: #e8f0e5 !important;
}

.stTextInput input, 
.stNumberInput input, 
textarea, 
input,
div[data-baseweb="select"] > div {
    background-color: #ffffff !important;
    border: 2px solid #e2e8f0 !important;
    border-radius: 14px !important;
    padding: 12px 16px !important;
    color: #1a2a1f !important;
    font-weight: 500 !important;
    transition: all 0.3s ease !important;
}

.stTextInput input:not([value="0"]):not([value="0.0"]),
.stNumberInput input:not([value="0"]):not([value="0.0"]) {
    background: linear-gradient(95deg, #f0fdf4 0%, #ecfdf5 100%) !important;
    border-color: #86efac !important;
}

.stTextInput input:focus, 
.stNumberInput input:focus {
    border-color: #4a8c5c !important;
    box-shadow: 0 0 0 4px rgba(74, 140, 92, 0.15) !important;
    outline: none !important;
}

.stButton > button {
    background: linear-gradient(95deg, #2d5a3b 0%, #4a8c5c 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 40px !important;
    padding: 0.7rem 2rem !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 12px rgba(45, 90, 59, 0.2) !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 20px rgba(45, 90, 59, 0.3) !important;
}

div[data-testid="stMetric"] {
    background: linear-gradient(135deg, #ffffff 0%, #fafcff 100%) !important;
    border-radius: 20px !important;
    padding: 1.2rem !important;
    border: 1px solid rgba(74, 140, 92, 0.15) !important;
}

.dataframe {
    background: #ffffff !important;
    border-radius: 16px !important;
    border: 1px solid #e8ede8 !important;
}

.dataframe th {
    background: linear-gradient(95deg, #2d5a3b 0%, #3a6b48 100%) !important;
    color: white !important;
}

.custom-header {
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.95), rgba(248, 250, 245, 0.95));
    backdrop-filter: blur(10px);
    border-radius: 28px;
    padding: 1.5rem 2rem;
    margin-bottom: 2rem;
    border: 1px solid rgba(74, 140, 92, 0.2);
}

button[data-baseweb="tab"] {
    background: transparent !important;
    color: #5a6e5a !important;
    font-weight: 500 !important;
    border-radius: 30px !important;
    padding: 0.5rem 1.5rem !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    background: linear-gradient(95deg, #2d5a3b 0%, #4a8c5c 100%) !important;
    color: white !important;
}

hr {
    margin: 2rem 0 !important;
    border: none !important;
    height: 2px !important;
    background: linear-gradient(90deg, transparent, #4a8c5c, #86efac, #4a8c5c, transparent) !important;
}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# CABECALHO
# ============================================================================

st.markdown("""
<div class="custom-header">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
        <div>
            <h1 style="margin-bottom: 0.3rem;">🌿 Classificador Inteligente de Fertilidade do Solo</h1>
            <p style="color: #5a6e5a;">Sistema Brasileiro de Classificação de Solos (SiBCS) · Embrapa</p>
        </div>
        <div style="background: linear-gradient(95deg, #e8f5e9, #d4edda); padding: 0.25rem 1rem; border-radius: 40px;">
            <span style="color: #2d5a3b; font-weight: 600;">📊 Análise em Tempo Real</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2934/2934128.png", width=80)
    st.markdown("### 📊 Sobre o Sistema")
    st.markdown("""
    Este classificador utiliza parâmetros do **SiBCS (Embrapa)** para:
    - ✅ Avaliação da fertilidade do solo
    - ✅ Classificação agrícola profissional
    - ✅ Recomendação de calagem precisa
    - ✅ Relatórios técnicos detalhados
    - ✅ Cálculo de adubação para vasos
    """)
    st.markdown("---")
    st.markdown("### 🤖 Status da IA")
    
    if not JOBLIB_AVAILABLE:
        st.error("⚠️ joblib não instalado")
    elif modelo is not None and features is not None:
        st.success("✅ IA carregada com sucesso!")
        st.caption(f"🎯 Features: {len(features)}")
    else:
        st.warning("⚠️ IA não disponível")
    
    st.markdown("---")
    st.caption("✨ Versão 7.0 — Com Adubação para Vasos")
    st.caption("Desenvolvido com Streamlit")

# ============================================================================
# SESSION STATE (GARANTINDO CONEXÃO ENTRE ABAS)
# ============================================================================

if "dados_basicos" not in st.session_state:
    st.session_state.dados_basicos = {
        "nitrogen": 0.0, "phosphorus": 0.0, "potassium": 0.0,
        "organic_matter": 0.0, "bulk_density": 0.0, "particle_density": 0.0,
        "sand": 0.0, "silt": 0.0, "clay": 0.0
    }

if "dados_calculados" not in st.session_state:
    st.session_state.dados_calculados = {}

if "dados_salvos" not in st.session_state:
    st.session_state.dados_salvos = False

if "classificacao_realizada" not in st.session_state:
    st.session_state.classificacao_realizada = False

# MENU (5 ABAS AGORA)
menu = st.radio(
    "Navegação",
    [
        "📊 1. Dados do Solo",
        "🌱 2. Classificação",
        "🧪 3. Adubação para Vaso",
        "📈 4. Relatório",
        "ℹ️ 5. Métodos"
    ],
    horizontal=True,
    label_visibility="collapsed"
)

# ============================================================================
# DICIONARIO DAS CULTURAS
# ============================================================================

necessidades_culturas = {
    "Soja": {"v_desejado": 60, "ph_min": 5.5, "ph_max": 6.5, "p_min": 15, "k_min": 0.35, "fator_n": 0.3},
    "Milho": {"v_desejado": 65, "ph_min": 5.5, "ph_max": 6.5, "p_min": 20, "k_min": 0.40, "fator_n": 1.0},
    "Feijão": {"v_desejado": 65, "ph_min": 5.5, "ph_max": 6.5, "p_min": 20, "k_min": 0.35, "fator_n": 0.4},
    "Café": {"v_desejado": 70, "ph_min": 5.5, "ph_max": 6.5, "p_min": 25, "k_min": 0.40, "fator_n": 0.8},
    "Pastagem": {"v_desejado": 50, "ph_min": 5.0, "ph_max": 6.0, "p_min": 10, "k_min": 0.25, "fator_n": 0.6},
    "Tomate": {"v_desejado": 80, "ph_min": 6.0, "ph_max": 6.8, "p_min": 30, "k_min": 0.50, "fator_n": 1.2}
}

# ============================================================================
# FUNÇÃO PARA PREDIÇÃO DA IA
# ============================================================================

def fazer_predicao_ia(dados):
    if not JOBLIB_AVAILABLE or modelo is None or features is None:
        return None, "IA não disponível"
    
    try:
        features_disponiveis = {
            "nitrogen": dados.get("nitrogen", 0),
            "phosphorus": dados.get("phosphorus", 0),
            "potassium": dados.get("potassium", 0),
            "ph": dados.get("ph", 7.0),
            "organic_matter": dados.get("organic_matter", 0),
            "bulk_density": dados.get("bulk_density", 0),
            "sand": dados.get("sand", 0),
            "silt": dados.get("silt", 0),
            "clay": dados.get("clay", 0),
            "calcium": dados.get("calcium", 0),
            "magnesium": dados.get("magnesium", 0),
            "aluminum": dados.get("aluminum", 0),
            "h_al": dados.get("h_al", 0),
            "particle_density": dados.get("particle_density", 0)
        }
        
        valores = []
        for feature in features:
            valores.append(features_disponiveis.get(feature, 0))
        
        entrada_ia = pd.DataFrame([valores], columns=features)
        predicao = modelo.predict(entrada_ia)
        
        mapeamento = {0: "🔴 BAIXA FERTILIDADE", 1: "🟢 ALTA FERTILIDADE"}
        classe = mapeamento.get(predicao[0], f"Classe {predicao[0]}")
        
        return classe, "Sucesso"
    except Exception as e:
        return None, f"Erro: {str(e)}"

# ============================================================================
# ABA 1 - DADOS DO SOLO
# ============================================================================

if menu == "📊 1. Dados do Solo":
    st.markdown("## 📋 Dados Básicos do Solo")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🌱 Macronutrientes")
        nitrogen = st.text_input("Nitrogênio (N) - mg/dm³", value="0.0", key="n_input")
        phosphorus = st.text_input("Fósforo (P) - mg/dm³", value="0.0", key="p_input")
        potassium = st.text_input("Potássio (K+) - cmolc/dm³", value="0.0", key="k_input")
        st.markdown("### 🍂 Matéria Orgânica")
        organic_matter = st.text_input("Matéria Orgânica (g/kg)", value="0.0", key="om_input")

    with col2:
        st.markdown("### 📦 Densidade do Solo")
        bulk_density = st.text_input("Densidade do Solo (g/cm³)", value="0.0", key="bd_input")
        particle_density = st.text_input("Densidade de Partícula (g/cm³)", value="0.0", key="pd_input")
        st.markdown("### 🧱 Composição Textural")
        sand = st.text_input("Areia (g/kg)", value="0.0", key="sand_input")
        silt = st.text_input("Silte (g/kg)", value="0.0", key="silt_input")
        clay = st.text_input("Argila (g/kg)", value="0.0", key="clay_input")

    st.markdown("---")

    if st.button("💾 SALVAR DADOS BÁSICOS", key="salvar_basicos"):
        try:
            st.session_state.dados_basicos = {
                "nitrogen": float(nitrogen.replace(",", ".")),
                "phosphorus": float(phosphorus.replace(",", ".")),
                "potassium": float(potassium.replace(",", ".")),
                "organic_matter": float(organic_matter.replace(",", ".")),
                "bulk_density": float(bulk_density.replace(",", ".")),
                "particle_density": float(particle_density.replace(",", ".")),
                "sand": float(sand.replace(",", ".")),
                "silt": float(silt.replace(",", ".")),
                "clay": float(clay.replace(",", "."))
            }
            st.session_state.dados_salvos = True
            st.success("✅ Dados básicos salvos! Vá para aba 'Classificação'.")
        except Exception as e:
            st.error(f"❌ Erro: {str(e)}")

# ============================================================================
# ABA 2 - CLASSIFICAÇÃO
# ============================================================================

elif menu == "🌱 2. Classificação":
    if not st.session_state.dados_salvos:
        st.warning("⚠️ Preencha e salve os dados na ABA 1 primeiro!")
        st.stop()

    st.markdown("## 🌱 Classificação da Fertilidade")

    col1, col2 = st.columns(2)

    with col1:
        aluminum = st.text_input("Alumínio (Al³⁺) - cmolc/dm³", value="0.0", key="al_input")
        h_al = st.text_input("H + Al - cmolc/dm³", value="0.0", key="hal_input")

    with col2:
        calcium = st.text_input("Cálcio (Ca²⁺) - cmolc/dm³", value="0.0", key="ca_input")
        magnesium = st.text_input("Magnésio (Mg²⁺) - cmolc/dm³", value="0.0", key="mg_input")
        cultura = st.selectbox("🌾 Cultura", list(necessidades_culturas.keys()), key="cultura_select")

    st.markdown("---")

    if st.button("🔬 REALIZAR CLASSIFICAÇÃO", key="classificar"):
        try:
            dados = st.session_state.dados_basicos.copy()
            dados["aluminum"] = float(aluminum.replace(",", "."))
            dados["h_al"] = float(h_al.replace(",", "."))
            dados["calcium"] = float(calcium.replace(",", "."))
            dados["magnesium"] = float(magnesium.replace(",", "."))
            dados["cultura"] = cultura

            # Calcular pH
            dados["ph"] = calcular_ph(dados)
            
            # Calcular indicadores
            sb = dados["calcium"] + dados["magnesium"] + dados["potassium"]
            ctc_potencial = sb + dados["h_al"]
            v_percent = (sb / ctc_potencial) * 100 if ctc_potencial > 0 else 0
            
            # Salvar no session state
            st.session_state.dados_calculados = dados
            st.session_state.sb = sb
            st.session_state.ctc_potencial = ctc_potencial
            st.session_state.v_percent = v_percent
            st.session_state.cultura_selecionada = cultura
            st.session_state.classificacao_realizada = True
            
            # Exibir resultados
            st.success("✅ Classificação realizada com sucesso!")
            
            col_r1, col_r2, col_r3 = st.columns(3)
            with col_r1:
                st.metric("pH do Solo", f"{dados['ph']:.1f}")
            with col_r2:
                st.metric("CTC Potencial", f"{ctc_potencial:.2f} cmolc/dm³")
            with col_r3:
                st.metric("Saturação por Bases (V%)", f"{v_percent:.1f}%")
            
            # IA
            st.markdown("---")
            st.markdown("### 🤖 Classificação por IA")
            
            if JOBLIB_AVAILABLE and modelo is not None:
                with st.spinner("Processando..."):
                    predicao, status = fazer_predicao_ia(dados)
                    if predicao:
                        st.success(f"**Classe prevista:** {predicao}")
                    else:
                        st.warning(f"IA não disponível: {status}")
            else:
                st.info("ℹ️ Modelo de IA não disponível")
                
        except Exception as e:
            st.error(f"❌ Erro na classificação: {str(e)}")

# ============================================================================
# ABA 3 - ADUBAÇÃO PARA VASO (NOVA)
# ============================================================================

elif menu == "🧪 3. Adubação para Vaso":
    st.markdown("## 🧪 Cálculo de Adubação para Vaso")
    
    if not st.session_state.classificacao_realizada:
        st.warning("⚠️ Execute a classificação na ABA 2 primeiro para obter as recomendações baseadas na análise do solo!")
        st.info("📌 Isso é importante porque a recomendação de adubação considera os níveis atuais de fósforo e potássio do seu solo.")
        
        # Opção para usar dados padrão
        if st.button("📊 Usar dados de demonstração"):
            st.session_state.classificacao_realizada = True
            st.session_state.dados_calculados = {
                "phosphorus": 5.0,
                "potassium": 0.15,
                "clay": 200
            }
            st.session_state.cultura_selecionada = "Soja"
            st.rerun()
        st.stop()
    
    st.info("🌱 **Recomendação personalizada baseada na análise do seu solo!**")
    
    # Dados do vaso
    st.markdown("### 📏 Dimensões do Vaso")
    
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        altura_cm = st.number_input("Altura do vaso (cm)", min_value=5.0, max_value=100.0, value=20.0, step=1.0)
    with col_v2:
        diametro_cm = st.number_input("Diâmetro do vaso (cm)", min_value=5.0, max_value=50.0, value=10.0, step=1.0)
    
    # Calcular área do vaso
    raio_cm = diametro_cm / 2
    area_cm2 = math.pi * (raio_cm ** 2)
    area_m2 = area_cm2 / 10000  # Converter para metros quadrados
    
    st.caption(f"📐 Área do vaso: **{area_m2:.4f} m²** | Volume aproximado: **{(area_m2 * (altura_cm/100)):.3f} m³**")
    
    st.markdown("---")
    st.markdown("### 🌾 Recomendação de Adubação Nitrogenada")
    
    cultura = st.session_state.cultura_selecionada
    st.success(f"Cultura selecionada: **{cultura}**")
    
    # Fator de correção baseado na análise de solo
    dados = st.session_state.dados_calculados
    phosphorus_atual = dados.get("phosphorus", 0)
    potassium_atual = dados.get("potassium", 0)
    
    # Recomendação base de N para cada cultura (kg/ha)
    recomendacao_n_ha = {
        "Soja": 20,      # Soja fixa N, precisa pouco
        "Milho": 120,
        "Feijão": 40,
        "Café": 180,
        "Pastagem": 80,
        "Tomate": 150
    }
    
    # Ajuste baseado nos níveis de P e K do solo
    fator_ajuste = 1.0
    if phosphorus_atual < 15:
        fator_ajuste += 0.2
        st.info("⚠️ Fósforo baixo (+20% na adubação)")
    if potassium_atual < 0.25:
        fator_ajuste += 0.15
        st.info("⚠️ Potássio baixo (+15% na adubação)")
    
    base_n_ha = recomendacao_n_ha.get(cultura, 80)
    recomendacao_ajustada = base_n_ha * fator_ajuste
    
    # Calcular para o vaso
    gramas_por_vaso = calcular_adubacao_vaso(area_m2, recomendacao_ajustada, fator_cultura=1.0)
    
    st.markdown("---")
    st.markdown("### 📊 Resultado")
    
    col_res1, col_res2, col_res3 = st.columns(3)
    with col_res1:
        st.metric("Recomendação por hectare", f"{recomendacao_ajustada:.0f} kg/ha de N")
    with col_res2:
        st.metric("Quantidade para este vaso", f"{gramas_por_vaso:.2f} gramas de N")
    with col_res3:
        st.metric("Equivalente em ureia (45% N)", f"{(gramas_por_vaso / 0.45):.2f} gramas")
    
    st.markdown("---")
    st.markdown("#### 🧴 Modo de aplicação sugerido:")
    st.markdown(f"""
    - Dissolva **{gramas_por_vaso:.2f} gramas de nitrogênio** em água
    - Para ureia: use **{(gramas_por_vaso / 0.45):.2f} gramas**
    - Aplique dividido em 2-3 vezes durante o ciclo da cultura
    - Regue após a aplicação para melhor absorção
    """)
    
    st.caption("💡 *Nota: Soja não necessita de adubação nitrogenada significativa devido à fixação biológica*")

# ============================================================================
# ABA 4 - RELATÓRIO
# ============================================================================

elif menu == "📈 4. Relatório":
    if not st.session_state.classificacao_realizada:
        st.warning("⚠️ Execute a classificação na ABA 2 primeiro!")
        st.stop()
    
    st.markdown("## 📈 Relatório Técnico")
    
    dados = st.session_state.dados_calculados
    sb = st.session_state.sb
    ctc_potencial = st.session_state.ctc_potencial
    v_percent = st.session_state.v_percent
    
    relatorio = pd.DataFrame({
        "Parâmetro": ["pH", "Nitrogênio (N)", "Fósforo (P)", "Potássio (K+)",
                      "Cálcio (Ca²⁺)", "Magnésio (Mg²⁺)", "Alumínio (Al³⁺)", "H + Al",
                      "Soma de Bases (SB)", "CTC Potencial", "Saturação por Bases (V%)",
                      "Matéria Orgânica", "Argila"],
        "Valor": [
            f"{dados['ph']:.1f}", f"{dados['nitrogen']:.1f} mg/dm³",
            f"{dados['phosphorus']:.1f} mg/dm³", f"{dados['potassium']:.2f} cmolc/dm³",
            f"{dados['calcium']:.2f} cmolc/dm³", f"{dados['magnesium']:.2f} cmolc/dm³",
            f"{dados['aluminum']:.2f} cmolc/dm³", f"{dados['h_al']:.2f} cmolc/dm³",
            f"{sb:.2f} cmolc/dm³", f"{ctc_potencial:.2f} cmolc/dm³",
            f"{v_percent:.1f}%", f"{dados['organic_matter']:.1f} g/kg",
            f"{dados['clay']:.0f} g/kg"
        ]
    })
    
    st.dataframe(relatorio, hide_index=True, use_container_width=True)
    
    csv = relatorio.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Baixar Relatório (CSV)", data=csv, file_name="relatorio_solo.csv", mime="text/csv")

# ============================================================================
# ABA 5 - MÉTODOS
# ============================================================================

elif menu == "ℹ️ 5. Métodos":
    st.markdown("## ℹ️ Métodos Utilizados")
    
    with st.expander("📊 Saturação por Bases (V%)"):
        st.latex(r"V\% = \frac{SB}{CTC} \times 100")
    
    with st.expander("🧪 Cálculo do pH"):
        st.markdown("""
        O pH é calculado considerando:
        - Cátions básicos (Ca, Mg, K) → aumentam o pH
        - Alumínio e H+Al → diminuem o pH
        - Matéria Orgânica → efeito tampão
        - Valores zerados resultam em pH neutro (7.0)
        """)
    
    with st.expander("🌱 Cálculo da Adubação para Vaso"):
        st.markdown("""
        **Fórmula utilizada:**kg_por_m² = recomendação_kg_ha / 10000
kg_vaso = kg_por_m² × área_do_vaso_m²
gramas_vaso = kg_vaso × 1000 × fator_cultura
**Considerações:**
- Área do vaso calculada a partir do diâmetro (π × r²)
- Ajuste baseado nos níveis de P e K da análise
- Fator específico por cultura (soja fixa N, precisa menos)
""")

# ============================================================================
# RODAPÉ
# ============================================================================

st.markdown("---")
st.caption("© 2026 - Classificador de Fertilidade do Solo | Créditos ao SiBCS - Embrapa | Inclui cálculo de adubação para vasos")
