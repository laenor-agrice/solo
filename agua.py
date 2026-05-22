#Bloco 0 - Verificação e instalação automática de dependências
import subprocess
import sys
import importlib

def verificar_e_instalar(pacotes):
    """
    Verifica se os pacotes estão instalados e os instala automaticamente se necessário
    """
    pacotes_a_instalar = []
    
    for pacote in pacotes:
        nome_import = pacote.replace("-", "_")
        try:
            importlib.import_module(nome_import)
            print(f"✅ {pacote} já está instalado")
        except ImportError:
            pacotes_a_instalar.append(pacote)
            print(f"⚠️ {pacote} não encontrado. Será instalado...")
    
    if pacotes_a_instalar:
        print(f"\n📦 Instalando: {', '.join(pacotes_a_instalar)}")
        for pacote in pacotes_a_instalar:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pacote])
        print("\n✅ Todos os pacotes foram instalados com sucesso!")
        return True
    else:
        print("\n✅ Todos os pacotes já estão instalados!")
        return False

# Lista de pacotes necessários
pacotes_necessarios = [
    "streamlit",
    "pandas", 
    "numpy",
    "plotly",
    "folium",
    "streamlit-folium"
]

# Verificar e instalar dependências
print("🔍 Verificando dependências do sistema...")
precisa_reiniciar = verificar_e_instalar(pacotes_necessarios)

if precisa_reiniciar:
    print("\n🔄 As dependências foram instaladas. Reiniciando o script...")
    # Forçar reinicialização do script
    import os
    os.execv(sys.executable, [sys.executable] + sys.argv)

# Agora importar os pacotes (já devem estar disponíveis)
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import folium
from streamlit_folium import st_folium
from datetime import datetime
import json
import os

# Configuração da página
st.set_page_config(
    page_title="Sistema de Qualidade da Água",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Arquivo para persistência dos dados
DATA_FILE = "dados_qualidade_agua.json"

# Funções para carregar e salvar dados
def carregar_dados():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "cadastro": {},
        "analises": [],
        "levantamento": {},
        "usuario": {}
    }

def salvar_dados(dados):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

# Inicializar dados na sessão
if 'dados_app' not in st.session_state:
    st.session_state.dados_app = carregar_dados()


#Bloco 1 - Função de classificação da qualidade da água (baseado na CONAMA 357/2005)
def classificar_ponto(analise):
    """
    Classifica o ponto de acordo com a Resolução CONAMA 357/2005
    Retorna: classe, usos, cor_indicativa
    """
    classe = 1  # Começa assumindo Classe 1
    motivos = []
    
    # Parâmetros para água doce (padrão rios/lagos/represas)
    # Classe 1 - padrões mais restritivos
    # Classe 2 - padrões menos restritivos
    # Classe 3 - padrões para abastecimento após tratamento convencional
    # Classe 4 - padrões para navegação e harmonia paisagística
    
    # OD - Oxigênio Dissolvido (mg/L) - mínimo
    if 'od' in analise and analise['od'] is not None:
        od = analise['od']
        if od < 5.0:
            classe = max(classe, 3 if od < 4.0 else 2)
            motivos.append(f"OD baixo ({od} mg/L)")
        elif od < 6.0:
            classe = max(classe, 2)
            motivos.append(f"OD ({od} mg/L) abaixo da Classe 1")
    
    # pH
    if 'ph' in analise and analise['ph'] is not None:
        ph = analise['ph']
        if ph < 6.0 or ph > 9.0:
            classe = max(classe, 4)
            motivos.append(f"pH fora da faixa ({ph})")
        elif ph < 6.5 or ph > 8.5:
            classe = max(classe, 3)
            motivos.append(f"pH ({ph}) fora da faixa Classe 1/2")
    
    # DBO - Demanda Bioquímica de Oxigênio (mg/L)
    if 'dbo' in analise and analise['dbo'] is not None:
        dbo = analise['dbo']
        if dbo > 10.0:
            classe = max(classe, 4)
            motivos.append(f"DBO alta ({dbo} mg/L)")
        elif dbo > 5.0:
            classe = max(classe, 3)
            motivos.append(f"DBO ({dbo} mg/L) acima da Classe 2")
        elif dbo > 3.0:
            classe = max(classe, 2)
            motivos.append(f"DBO ({dbo} mg/L) acima da Classe 1")
    
    # Turbidez (NTU)
    if 'turbidez' in analise and analise['turbidez'] is not None:
        turb = analise['turbidez']
        if turb > 100:
            classe = max(classe, 4)
        elif turb > 40:
            classe = max(classe, 3)
        elif turb > 10:
            classe = max(classe, 2)
    
    # E. coli / Coliformes termotolerantes (NMP/100mL)
    if 'coliformes' in analise and analise['coliformes'] is not None:
        col = analise['coliformes']
        if col > 4000:
            classe = max(classe, 4)
            motivos.append(f"Coliformes altos ({col} NMP)")
        elif col > 1000:
            classe = max(classe, 3)
        elif col > 200:
            classe = max(classe, 2)
    
    # Fósforo Total (mg/L) - para lagos/represas
    if 'fosforo' in analise and analise['fosforo'] is not None:
        p = analise['fosforo']
        if p > 0.15:
            classe = max(classe, 3)
        elif p > 0.05:
            classe = max(classe, 2)
    
    # Nitrogênio Total (mg/L)
    if 'nitrogenio' in analise and analise['nitrogenio'] is not None:
        n = analise['nitrogenio']
        if n > 3.7:
            classe = max(classe, 3)
        elif n > 2.0:
            classe = max(classe, 2)
    
    # Definição da classe final
    if classe == 1:
        classe_texto = "Classe 1"
        cor = "🟢"
        usos = ["Abastecimento doméstico com desinfecção simples", "Proteção da vida aquática", "Irrigação"]
    elif classe == 2:
        classe_texto = "Classe 2"
        cor = "🟡"
        usos = ["Abastecimento com tratamento convencional", "Proteção da vida aquática", "Irrigação", "Recreação"]
    elif classe == 3:
        classe_texto = "Classe 3"
        cor = "🟠"
        usos = ["Abastecimento com tratamento convencional", "Irrigação", "Dessedentação de animais"]
    else:
        classe_texto = "Classe 4"
        cor = "🔴"
        usos = ["Navegação", "Harmonia paisagística", "Usos menos exigentes"]
    
    return classe_texto, cor, usos, motivos


#Bloco 2 - Função para avaliar o trecho do corpo hídrico
def avaliar_trecho(pontos_classificados):
    if not pontos_classificados:
        return "Sem dados", "⚪", []
    
    classes = [c for c, _, _, _ in pontos_classificados]
    # Classificação geral do trecho: pior classe encontrada
    indices = {"Classe 1": 1, "Classe 2": 2, "Classe 3": 3, "Classe 4": 4}
    pior = max(classes, key=lambda x: indices.get(x, 4))
    
    if pior == "Classe 1":
        status = "Excelente"
        cor = "🟢"
        recomendacao = "Qualidade preservada. Manter práticas de conservação."
    elif pior == "Classe 2":
        status = "Boa"
        cor = "🟡"
        recomendacao = "Qualidade satisfatória. Monitorar parâmetros críticos."
    elif pior == "Classe 3":
        status = "Regular"
        cor = "🟠"
        recomendacao = "Qualidade comprometida. Necessário tratamento convencional para abastecimento."
    else:
        status = "Ruim"
        cor = "🔴"
        recomendacao = "Qualidade severamente degradada. Intervenção prioritária necessária."
    
    return status, cor, [recomendacao]


#Bloco 3 - Função para gerar recomendações de manejo
def gerar_recomendacoes_manejo(levantamento, classificacao_geral, analises):
    recomendacoes = []
    
    # Baseado no levantamento de causas ambientais
    if levantamento:
        cobertura = levantamento.get('cobertura_solo', '').lower()
        tipo_solo = levantamento.get('tipo_solo', '').lower()
        atividades = levantamento.get('atividades', [])
        
        if 'pastagem' in cobertura or 'agricultura' in cobertura:
            recomendacoes.append("🌾 **Agricultura/Pastagem**: Implementar práticas de conservação do solo, como plantio direto, terraços e faixas de amortecimento (buffers) com vegetação nativa entre a área cultivada e o corpo d'água.")
        
        if 'urbano' in cobertura or 'esgoto' in str(levantamento):
            recomendacoes.append("🏙️ **Área Urbana/Esgoto**: Investir em saneamento básico, tratamento de esgoto e evitar lançamento in natura. Implementar sistemas de drenagem sustentável.")
        
        if 'mineracao' in str(atividades):
            recomendacoes.append("⛏️ **Mineração**: Controle de drenagem ácida, tratamento de efluentes e recuperação de áreas degradadas.")
        
        if 'barragem' in str(levantamento) or 'assoreamento' in str(levantamento):
            recomendacoes.append("🏞️ **Alteração hidrológica/Assoreamento**: Recompor mata ciliar, controlar erosão nas margens e implementar programas de desassoreamento controlado.")
        
        if 'queimada' in str(levantamento):
            recomendacoes.append("🔥 **Queimadas**: Desenvolver plano de prevenção e combate a incêndios. Recuperar áreas queimadas com espécies nativas.")
    
    # Baseado na classificação da água
    if classificacao_geral == "Ruim" or classificacao_geral == "Regular":
        recomendacoes.append("⚠️ **Qualidade da água crítica**: Priorizar ações emergenciais como isolamento da área de captação, tratamento intensivo e fiscalização de fontes poluidoras.")
        
    if "Classe 3" in classificacao_geral or "Classe 4" in classificacao_geral:
        recomendacoes.append("🔄 **Tratamento da água**: Adotar tratamento convencional (coagulação, floculação, decantação, filtração e desinfecção) antes de qualquer uso mais exigente.")
    
    # Recomendações específicas por parâmetro
    if analises:
        od_baixo = any(a.get('od', 10) < 5 for a in analises)
        dbo_alto = any(a.get('dbo', 0) > 5 for a in analises)
        fosforo_alto = any(a.get('fosforo', 0) > 0.1 for a in analises)
        
        if od_baixo or dbo_alto:
            recomendacoes.append("💨 **Baixo OD/Alta DBO**: Reduzir lançamento de matéria orgânica (esgoto, efluentes agroindustriais). Aumentar aeração natural com estruturas como quedas d'água artificiais.")
        
        if fosforo_alto:
            recomendacoes.append("🌿 **Eutrofização (Fósforo alto)**: Controlar fertilizantes na bacia, criar zonas úmidas construídas (wetlands) e evitar despejo de esgoto sem tratamento.")
    
    if not recomendacoes:
        recomendacoes.append("✅ **Boas práticas**: Manter a conservação da mata ciliar, monitorar periodicamente e evitar atividades potencialmente poluidoras nas proximidades.")
    
    return recomendacoes


#Bloco 4 - Função para usos possíveis da água
def usos_possiveis_agua(classificacao_por_ponto):
    usos_por_classe = {
        "Classe 1": ["✅ Abastecimento doméstico com desinfecção simples", "✅ Proteção da vida aquática (íntegra)", "✅ Irrigação de hortaliças", "✅ Recreação de contato primário (natação)", "✅ Aquicultura"],
        "Classe 2": ["✅ Abastecimento doméstico com tratamento convencional", "✅ Proteção da vida aquática (moderada)", "✅ Irrigação de hortaliças (com cautela)", "✅ Recreação de contato primário", "✅ Pecuária"],
        "Classe 3": ["⚠️ Abastecimento doméstico com tratamento convencional (com processos avançados)", "✅ Irrigação de culturas arbóreas", "✅ Dessedentação de animais", "✅ Recreação de contato secundário (remo)", "❌ Natação"],
        "Classe 4": ["✅ Navegação", "✅ Harmonia paisagística", "❌ Abastecimento humano direto", "❌ Irrigação de hortaliças", "❌ Contato primário (recreação)"]
    }
    
    resultados = {}
    for ponto, classe, _, _, _ in classificacao_por_ponto:
        resultados[ponto] = usos_por_classe.get(classe, usos_por_classe["Classe 4"])
    
    return resultados


#Bloco 5 - Aba 1: Cadastro
def aba_cadastro():
    st.header("📋 1. Cadastro de Usuário e Propriedade")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Dados do Usuário")
        nome = st.text_input("Nome completo", value=st.session_state.dados_app.get("usuario", {}).get("nome", ""))
        cpf_cnpj = st.text_input("CPF/CNPJ", value=st.session_state.dados_app.get("usuario", {}).get("cpf_cnpj", ""))
        email = st.text_input("E-mail", value=st.session_state.dados_app.get("usuario", {}).get("email", ""))
        telefone = st.text_input("Telefone", value=st.session_state.dados_app.get("usuario", {}).get("telefone", ""))
        
        st.subheader("Endereço")
        endereco = st.text_input("Logradouro", value=st.session_state.dados_app.get("usuario", {}).get("endereco", ""))
        cidade = st.text_input("Cidade", value=st.session_state.dados_app.get("usuario", {}).get("cidade", ""))
        estado = st.text_input("Estado (UF)", value=st.session_state.dados_app.get("usuario", {}).get("estado", ""))
        cep = st.text_input("CEP", value=st.session_state.dados_app.get("usuario", {}).get("cep", ""))
    
    with col2:
        st.subheader("Localização da Fazenda")
        fazenda_nome = st.text_input("Nome da Fazenda", value=st.session_state.dados_app.get("cadastro", {}).get("fazenda_nome", ""))
        fazenda_lat = st.number_input("Latitude (SIG BR - graus decimais)", value=st.session_state.dados_app.get("cadastro", {}).get("fazenda_lat", -15.0), format="%.6f")
        fazenda_lon = st.number_input("Longitude (SIG BR - graus decimais)", value=st.session_state.dados_app.get("cadastro", {}).get("fazenda_lon", -45.0), format="%.6f")
        
        st.subheader("Corpo Hídrico")
        corpo_nome = st.text_input("Nome do Rio/Lago/Represa", value=st.session_state.dados_app.get("cadastro", {}).get("corpo_nome", ""))
        corpo_tipo = st.selectbox("Tipo de corpo hídrico", ["Rio", "Lago", "Represa", "Córrego", "Outro"], 
                                  index=["Rio", "Lago", "Represa", "Córrego", "Outro"].index(st.session_state.dados_app.get("cadastro", {}).get("corpo_tipo", "Rio")))
    
    st.divider()
    if st.button("💾 Salvar Cadastro", type="primary"):
        st.session_state.dados_app["usuario"] = {
            "nome": nome, "cpf_cnpj": cpf_cnpj, "email": email, "telefone": telefone,
            "endereco": endereco, "cidade": cidade, "estado": estado, "cep": cep
        }
        st.session_state.dados_app["cadastro"] = {
            "fazenda_nome": fazenda_nome, "fazenda_lat": fazenda_lat, "fazenda_lon": fazenda_lon,
            "corpo_nome": corpo_nome, "corpo_tipo": corpo_tipo
        }
        salvar_dados(st.session_state.dados_app)
        st.success("Cadastro salvo com sucesso!")


#Bloco 6 - Aba 2: Análises Básicas (para classificação CONAMA)
def aba_analises():
    st.header("🧪 2. Análises Básicas de Qualidade da Água")
    st.caption("Preencha os parâmetros essenciais para classificação conforme CONAMA 357/2005. Mínimo 1 ponto, máximo 10.")
    
    # Inicializar lista de análises na sessão se não existir
    if 'analises_temp' not in st.session_state:
        st.session_state.analises_temp = st.session_state.dados_app.get("analises", [])
        if not st.session_state.analises_temp:
            st.session_state.analises_temp = []
    
    # Controle de quantos pontos existem
    num_pontos = len(st.session_state.analises_temp)
    if num_pontos == 0:
        num_pontos = 1
        st.session_state.analises_temp = [{}]
    
    # Layout para cada ponto
    for i in range(num_pontos):
        with st.expander(f"📌 Ponto de Coleta {i+1}", expanded=(i == num_pontos-1)):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📍 Identificação do Ponto**")
                ponto_nome = st.text_input(f"Nome/ID do ponto {i+1}", key=f"nome_{i}", 
                                           value=st.session_state.analises_temp[i].get("nome", f"Ponto {i+1}"))
                ponto_lat = st.number_input(f"Latitude (ponto {i+1})", key=f"lat_{i}", format="%.6f",
                                            value=st.session_state.analises_temp[i].get("lat", -15.0))
                ponto_lon = st.number_input(f"Longitude (ponto {i+1})", key=f"lon_{i}", format="%.6f",
                                            value=st.session_state.analises_temp[i].get("lon", -45.0))
                data_coleta = st.date_input(f"Data da coleta {i+1}", key=f"data_{i}",
                                            value=datetime.strptime(st.session_state.analises_temp[i].get("data", datetime.now().strftime("%Y-%m-%d")), "%Y-%m-%d") if st.session_state.analises_temp[i].get("data") else datetime.now())
            
            with col2:
                st.markdown("**📊 Parâmetros Físico-Químicos Básicos**")
                temperatura = st.number_input(f"Temperatura (°C)", key=f"temp_{i}", value=float(st.session_state.analises_temp[i].get("temperatura", 25.0)), step=0.1)
                ph = st.number_input(f"pH", key=f"ph_{i}", value=float(st.session_state.analises_temp[i].get("ph", 7.0)), step=0.1)
                turbidez = st.number_input(f"Turbidez (NTU)", key=f"turbidez_{i}", value=float(st.session_state.analises_temp[i].get("turbidez", 5.0)), step=0.1)
                cor_aparente = st.number_input(f"Cor Aparente (mg/L Pt-Co)", key=f"cor_aparente_{i}", value=int(st.session_state.analises_temp[i].get("cor_aparente", 10)), step=5)
                cor_verdadeira = st.number_input(f"Cor Verdadeira (mg/L Pt-Co)", key=f"cor_verdadeira_{i}", value=int(st.session_state.analises_temp[i].get("cor_verdadeira", 5)), step=5)
            
            st.markdown("---")
            col3, col4 = st.columns(2)
            
            with col3:
                st.markdown("**💨 Oxigênio e Demanda**")
                od = st.number_input(f"Oxigênio Dissolvido - OD (mg/L)", key=f"od_{i}", value=float(st.session_state.analises_temp[i].get("od", 7.0)), step=0.1)
                dbo = st.number_input(f"DBO₅,₂₀ (mg/L)", key=f"dbo_{i}", value=float(st.session_state.analises_temp[i].get("dbo", 2.0)), step=0.1)
                dqo = st.number_input(f"DQO (mg/L)", key=f"dqo_{i}", value=float(st.session_state.analises_temp[i].get("dqo", 10.0)), step=1.0)
                
                st.markdown("**🧫 Nutrientes**")
                nitrogenio_amoniacal = st.number_input(f"Nitrogênio Amoniacal Total (mg/L N)", key=f"nh3_{i}", value=float(st.session_state.analises_temp[i].get("nitrogenio_amoniacal", 0.5)), step=0.1)
                nitrato = st.number_input(f"Nitrato (mg/L N)", key=f"no3_{i}", value=float(st.session_state.analises_temp[i].get("nitrato", 1.0)), step=0.1)
                nitrito = st.number_input(f"Nitrito (mg/L N)", key=f"no2_{i}", value=float(st.session_state.analises_temp[i].get("nitrito", 0.05)), step=0.01)
                nitrogenio_total = st.number_input(f"Nitrogênio Total (mg/L N)", key=f"n_total_{i}", value=float(st.session_state.analises_temp[i].get("nitrogenio_total", 1.0)), step=0.1)
                fosforo_total = st.number_input(f"Fósforo Total (mg/L P)", key=f"p_total_{i}", value=float(st.session_state.analises_temp[i].get("fosforo_total", 0.03)), step=0.01, format="%.4f")
                fosfato_total = st.number_input(f"Fosfato Total (mg/L)", key=f"po4_{i}", value=float(st.session_state.analises_temp[i].get("fosfato_total", 0.1)), step=0.01)
            
            with col4:
                st.markdown("**🦠 Indicadores Biológicos**")
                coliformes = st.number_input(f"Coliformes Termotolerantes (NMP/100mL)", key=f"col_{i}", value=int(st.session_state.analises_temp[i].get("coliformes", 50)), step=10)
                e_coli = st.number_input(f"Escherichia coli - E. coli (NMP/100mL)", key=f"ecoli_{i}", value=int(st.session_state.analises_temp[i].get("e_coli", 50)), step=10)
                clorofila_a = st.number_input(f"Clorofila-a (µg/L)", key=f"clorofila_{i}", value=float(st.session_state.analises_temp[i].get("clorofila_a", 5.0)), step=1.0)
                
                st.markdown("**⚡ Outros Parâmetros Físico-Químicos**")
                condutividade = st.number_input(f"Condutividade Elétrica (µS/cm)", key=f"cond_{i}", value=float(st.session_state.analises_temp[i].get("condutividade", 100.0)), step=10.0)
                std = st.number_input(f"Sólidos Totais Dissolvidos - STD (mg/L)", key=f"std_{i}", value=int(st.session_state.analises_temp[i].get("std", 200)), step=10)
                sst = st.number_input(f"Sólidos Suspensos Totais - SST (mg/L)", key=f"sst_{i}", value=int(st.session_state.analises_temp[i].get("sst", 50)), step=10)
                alcalinidade = st.number_input(f"Alcalinidade (mg/L CaCO₃)", key=f"alc_{i}", value=float(st.session_state.analises_temp[i].get("alcalinidade", 50.0)), step=10.0)
                dureza = st.number_input(f"Dureza Total (mg/L CaCO₃)", key=f"dur_{i}", value=float(st.session_state.analises_temp[i].get("dureza", 100.0)), step=10.0)
                cloretos = st.number_input(f"Cloretos (mg/L Cl)", key=f"cl_{i}", value=float(st.session_state.analises_temp[i].get("cloretos", 50.0)), step=10.0)
            
            # Salvar no dicionário temporário
            st.session_state.analises_temp[i] = {
                "nome": ponto_nome, "lat": ponto_lat, "lon": ponto_lon, "data": str(data_coleta),
                "temperatura": temperatura, "ph": ph, "turbidez": turbidez,
                "cor_aparente": cor_aparente, "cor_verdadeira": cor_verdadeira,
                "od": od, "dbo": dbo, "dqo": dqo,
                "nitrogenio_amoniacal": nitrogenio_amoniacal, "nitrato": nitrato, "nitrito": nitrito,
                "nitrogenio_total": nitrogenio_total, "fosforo_total": fosforo_total, "fosfato_total": fosfato_total,
                "coliformes": coliformes, "e_coli": e_coli, "clorofila_a": clorofila_a,
                "condutividade": condutividade, "std": std, "sst": sst,
                "alcalinidade": alcalinidade, "dureza": dureza, "cloretos": cloretos
            }
    
    # Botões para adicionar/remover pontos
    col_b1, col_b2, col_b3 = st.columns([1, 1, 2])
    with col_b1:
        if len(st.session_state.analises_temp) < 10 and st.button("➕ Adicionar outro ponto"):
            st.session_state.analises_temp.append({})
            st.rerun()
    with col_b2:
        if len(st.session_state.analises_temp) > 1 and st.button("➖ Remover último ponto"):
            st.session_state.analises_temp.pop()
            st.rerun()
    
    st.divider()
    if st.button("💾 Salvar todas as análises básicas", type="primary"):
        st.session_state.dados_app["analises"] = st.session_state.analises_temp
        salvar_dados(st.session_state.dados_app)
        st.success(f"{len(st.session_state.analises_temp)} ponto(s) de coleta salvo(s) com sucesso!")


#Bloco 7 - Aba 3: Análises Avançadas (Parâmetros complementares)
def aba_analises_avancadas():
    st.header("🔬 3. Análises Avançadas de Qualidade da Água")
    st.caption("Parâmetros complementares para avaliação detalhada (Metais, Toxicidade, Microcontaminantes, etc.) - Base: CONAMA 357/2005 e Portaria 888/2021")
    
    # Inicializar lista de análises avançadas na sessão
    if 'analises_avancadas_temp' not in st.session_state:
        st.session_state.analises_avancadas_temp = st.session_state.dados_app.get("analises_avancadas", [])
        if not st.session_state.analises_avancadas_temp:
            st.session_state.analises_avancadas_temp = [{}]
    
    num_pontos = len(st.session_state.analises_avancadas_temp)
    
    for i in range(num_pontos):
        with st.expander(f"🔬 Parâmetros Avançados - Ponto {i+1}", expanded=(i == num_pontos-1)):
            
            # Referência do ponto
            ponto_ref = st.text_input(f"Referência do ponto (nome/ID) {i+1}", key=f"ref_av_{i}",
                                      value=st.session_state.analises_avancadas_temp[i].get("ponto_ref", f"Ponto {i+1}"))
            
            st.markdown("---")
            st.markdown("### 🦠 Indicadores Microbiológicos e Biológicos")
            col1, col2 = st.columns(2)
            
            with col1:
                densidade_ciano = st.number_input(f"Densidade de Cianobactérias (cel/mL)", key=f"ciano_{i}",
                                                  value=float(st.session_state.analises_avancadas_temp[i].get("densidade_ciano", 0)), step=100.0)
                enterococos = st.number_input(f"Enterococos (NMP/100mL)", key=f"enter_{i}",
                                             value=int(st.session_state.analises_avancadas_temp[i].get("enterococos", 0)), step=10)
                transparencia = st.number_input(f"Transparência - Disco de Secchi (m)", key=f"secchi_{i}",
                                               value=float(st.session_state.analises_avancadas_temp[i].get("transparencia", 2.0)), step=0.1)
            
            with col2:
                toxicidade_aguda = st.selectbox(f"Toxicidade Aguda", ["Não detectada", "Detectada", "Não analisado"],
                                               key=f"tox_ag_{i}", index=["Não detectada", "Detectada", "Não analisado"].index(
                                                   st.session_state.analises_avancadas_temp[i].get("toxicidade_aguda", "Não analisado")))
                toxicidade_cronica = st.selectbox(f"Toxicidade Crônica", ["Não detectada", "Detectada", "Não analisado"],
                                                 key=f"tox_cr_{i}", index=["Não detectada", "Detectada", "Não analisado"].index(
                                                     st.session_state.analises_avancadas_temp[i].get("toxicidade_cronica", "Não analisado")))
            
            st.markdown("---")
            st.markdown("### 🧪 Ânions e Parâmetros Inorgânicos")
            col3, col4 = st.columns(2)
            
            with col3:
                sulfatos = st.number_input(f"Sulfatos (mg/L SO₄)", key=f"sulf_{i}", value=float(st.session_state.analises_avancadas_temp[i].get("sulfatos", 50.0)), step=10.0)
                fluoreto = st.number_input(f"Fluoreto (mg/L F)", key=f"fluor_{i}", value=float(st.session_state.analises_avancadas_temp[i].get("fluoreto", 0.5)), step=0.1)
                cianeto = st.number_input(f"Cianeto (mg/L CN)", key=f"cn_{i}", value=float(st.session_state.analises_avancadas_temp[i].get("cianeto", 0.0)), step=0.01)
                sulfeto = st.number_input(f"Sulfeto (mg/L S²⁻)", key=f"sulfeto_{i}", value=float(st.session_state.analises_avancadas_temp[i].get("sulfeto", 0.0)), step=0.01)
            
            with col4:
                cloro_residual = st.number_input(f"Cloro Residual Livre (mg/L Cl)", key=f"cloro_{i}", value=float(st.session_state.analises_avancadas_temp[i].get("cloro_residual", 0.0)), step=0.1)
                orp = st.number_input(f"Potencial de Oxirredução - ORP (mV)", key=f"orp_{i}", value=int(st.session_state.analises_avancadas_temp[i].get("orp", 0)), step=10)
                salinidade = st.number_input(f"Salinidade (PSU)", key=f"salin_{i}", value=float(st.session_state.analises_avancadas_temp[i].get("salinidade", 0.0)), step=0.1)
            
            st.markdown("---")
            st.markdown("### 💧 Cátions e Metais")
            col5, col6 = st.columns(2)
            
            with col5:
                st.markdown("**Metais Alcalinos e Alcalinos Terrosos**")
                sodio = st.number_input(f"Sódio (mg/L Na)", key=f"na_{i}", value=float(st.session_state.analises_avancadas_temp[i].get("sodio", 20.0)), step=5.0)
                potassio = st.number_input(f"Potássio (mg/L K)", key=f"k_{i}", value=float(st.session_state.analises_avancadas_temp[i].get("potassio", 10.0)), step=5.0)
                calcio = st.number_input(f"Cálcio (mg/L Ca)", key=f"ca_{i}", value=float(st.session_state.analises_avancadas_temp[i].get("calcio", 30.0)), step=10.0)
                magnesio = st.number_input(f"Magnésio (mg/L Mg)", key=f"mg_{i}", value=float(st.session_state.analises_avancadas_temp[i].get("magnesio", 15.0)), step=5.0)
                bario = st.number_input(f"Bário (mg/L Ba)", key=f"ba_{i}", value=float(st.session_state.analises_avancadas_temp[i].get("bario", 0.1)), step=0.05)
                boro = st.number_input(f"Boro (mg/L B)", key=f"b_{i}", value=float(st.session_state.analises_avancadas_temp[i].get("boro", 0.1)), step=0.05)
            
            with col6:
                st.markdown("**Metais Pesados e Tóxicos**")
                ferro = st.number_input(f"Ferro Total (mg/L Fe)", key=f"fe_{i}", value=float(st.session_state.analises_avancadas_temp[i].get("ferro", 0.3)), step=0.1)
                manganes = st.number_input(f"Manganês (mg/L Mn)", key=f"mn_{i}", value=float(st.session_state.analises_avancadas_temp[i].get("manganes", 0.1)), step=0.05)
                aluminio = st.number_input(f"Alumínio (mg/L Al)", key=f"al_{i}", value=float(st.session_state.analises_avancadas_temp[i].get("aluminio", 0.1)), step=0.05)
                zinco = st.number_input(f"Zinco (mg/L Zn)", key=f"zn_{i}", value=float(st.session_state.analises_avancadas_temp[i].get("zinco", 0.05)), step=0.01)
                cobre = st.number_input(f"Cobre (mg/L Cu)", key=f"cu_{i}", value=float(st.session_state.analises_avancadas_temp[i].get("cobre", 0.01)), step=0.01)
                chumbo = st.number_input(f"Chumbo (mg/L Pb)", key=f"pb_{i}", value=float(st.session_state.analises_avancadas_temp[i].get("chumbo", 0.001)), step=0.001, format="%.4f")
                cadmio = st.number_input(f"Cádmio (mg/L Cd)", key=f"cd_{i}", value=float(st.session_state.analises_avancadas_temp[i].get("cadmio", 0.0005)), step=0.0005, format="%.4f")
                mercurio = st.number_input(f"Mercúrio (mg/L Hg)", key=f"hg_{i}", value=float(st.session_state.analises_avancadas_temp[i].get("mercurio", 0.0001)), step=0.0001, format="%.4f")
                arsenio = st.number_input(f"Arsênio (mg/L As)", key=f"as_{i}", value=float(st.session_state.analises_avancadas_temp[i].get("arsenio", 0.001)), step=0.001, format="%.4f")
                cromo = st.number_input(f"Cromo Total (mg/L Cr)", key=f"cr_{i}", value=float(st.session_state.analises_avancadas_temp[i].get("cromo", 0.01)), step=0.01)
                niquel = st.number_input(f"Níquel (mg/L Ni)", key=f"ni_{i}", value=float(st.session_state.analises_avancadas_temp[i].get("niquel", 0.005)), step=0.005, format="%.4f")
                selenio = st.number_input(f"Selênio (mg/L Se)", key=f"se_{i}", value=float(st.session_state.analises_avancadas_temp[i].get("selenio", 0.001)), step=0.001, format="%.4f")
                prata = st.number_input(f"Prata (mg/L Ag)", key=f"ag_{i}", value=float(st.session_state.analises_avancadas_temp[i].get("prata", 0.0005)), step=0.0005, format="%.4f")
                antimonio = st.number_input(f"Antimônio (mg/L Sb)", key=f"sb_{i}", value=float(st.session_state.analises_avancadas_temp[i].get("antimonio", 0.001)), step=0.001, format="%.4f")
            
            st.markdown("---")
            st.markdown("### 🧴 Compostos Orgânicos e Microcontaminantes")
            col7, col8 = st.columns(2)
            
            with col7:
                st.markdown("**Fenóis e Surfactantes**")
                fenomen = st.number_input(f"Fenóis Totais (mg/L)", key=f"fenol_{i}", value=float(st.session_state.analises_avancadas_temp[i].get("fenois", 0.0)), step=0.001, format="%.4f")
                surfactantes = st.number_input(f"Surfactantes (mg/L LAS)", key=f"surf_{i}", value=float(st.session_state.analises_avancadas_temp[i].get("surfactantes", 0.0)), step=0.1)
                
                st.markdown("**Óleos e Hidrocarbonetos**")
                oleos_graxas = st.number_input(f"Óleos e Graxas (mg/L)", key=f"oleo_{i}", value=float(st.session_state.analises_avancadas_temp[i].get("oleos_graxas", 0.0)), step=0.5)
                hidrocarbonetos = st.number_input(f"Hidrocarbonetos Totais (mg/L)", key=f"hc_{i}", value=float(st.session_state.analises_avancadas_temp[i].get("hidrocarbonetos", 0.0)), step=0.1)
                
                st.markdown("**Solventes e Aromáticos**")
                benzeno = st.number_input(f"Benzeno (µg/L)", key=f"benz_{i}", value=float(st.session_state.analises_avancadas_temp[i].get("benzeno", 0.0)), step=1.0)
                tolueno = st.number_input(f"Tolueno (µg/L)", key=f"tol_{i}", value=float(st.session_state.analises_avancadas_temp[i].get("tolueno", 0.0)), step=1.0)
                xileno = st.number_input(f"Xileno (µg/L)", key=f"xil_{i}", value=float(st.session_state.analises_avancadas_temp[i].get("xileno", 0.0)), step=1.0)
                etilbenzeno = st.number_input(f"Etilbenzeno (µg/L)", key=f"etil_{i}", value=float(st.session_state.analises_avancadas_temp[i].get("etilbenzeno", 0.0)), step=1.0)
            
            with col8:
                st.markdown("**Trihalometanos (THM)**")
                thms = st.number_input(f"Trihalometanos Totais (µg/L)", key=f"thm_{i}", value=float(st.session_state.analises_avancadas_temp[i].get("trihalometanos", 0.0)), step=1.0)
                
                st.markdown("**Pesticidas e Agrotóxicos**")
                pesticidas = st.text_input(f"Pesticidas (especificar)", key=f"pest_{i}", 
                                          value=st.session_state.analises_avancadas_temp[i].get("pesticidas", "Não detectado"))
                herbicidas = st.text_input(f"Herbicidas (especificar)", key=f"herb_{i}",
                                          value=st.session_state.analises_avancadas_temp[i].get("herbicidas", "Não detectado"))
                organofosforados = st.text_input(f"Organofosforados (especificar)", key=f"org_{i}",
                                                value=st.session_state.analises_avancadas_temp[i].get("organofosforados", "Não detectado"))
                carbamatos = st.text_input(f"Carbamatos (especificar)", key=f"carb_{i}",
                                          value=st.session_state.analises_avancadas_temp[i].get("carbamatos", "Não detectado"))
            
            st.markdown("---")
            st.markdown("### 📊 Índices e Parâmetros Integradores")
            col9, col10 = st.columns(2)
            
            with col9:
                cot = st.number_input(f"Carbono Orgânico Total - COT (mg/L)", key=f"cot_{i}", 
                                     value=float(st.session_state.analises_avancadas_temp[i].get("cot", 5.0)), step=1.0)
                iqa = st.number_input(f"Índice de Qualidade da Água - IQA (0-100)", key=f"iqa_{i}",
                                     value=float(st.session_state.analises_avancadas_temp[i].get("iqa", 70.0)), step=1.0, min_value=0.0, max_value=100.0)
            
            with col10:
                iet = st.selectbox(f"Índice de Estado Trófico - IET", ["Ultraoligotrófico", "Oligotrófico", "Mesotrófico", "Eutrófico", "Hipereutrófico", "Não calculado"],
                                  key=f"iet_{i}", index=["Ultraoligotrófico", "Oligotrófico", "Mesotrófico", "Eutrófico", "Hipereutrófico", "Não calculado"].index(
                                      st.session_state.analises_avancadas_temp[i].get("iet", "Não calculado")))
                radioatividade = st.text_input(f"Radioatividade (alfa/beta total)", key=f"rad_{i}",
                                              value=st.session_state.analises_avancadas_temp[i].get("radioatividade", "Não detectada"))
            
            # Salvar no dicionário temporário
            st.session_state.analises_avancadas_temp[i] = {
                "ponto_ref": ponto_ref,
                "densidade_ciano": densidade_ciano, "enterococos": enterococos, "transparencia": transparencia,
                "toxicidade_aguda": toxicidade_aguda, "toxicidade_cronica": toxicidade_cronica,
                "sulfatos": sulfatos, "fluoreto": fluoreto, "cianeto": cianeto, "sulfeto": sulfeto,
                "cloro_residual": cloro_residual, "orp": orp, "salinidade": salinidade,
                "sodio": sodio, "potassio": potassio, "calcio": calcio, "magnesio": magnesio,
                "bario": bario, "boro": boro,
                "ferro": ferro, "manganes": manganes, "aluminio": aluminio, "zinco": zinco,
                "cobre": cobre, "chumbo": chumbo, "cadmio": cadmio, "mercurio": mercurio,
                "arsenio": arsenio, "cromo": cromo, "niquel": niquel, "selenio": selenio,
                "prata": prata, "antimonio": antimonio,
                "fenois": fenomen, "surfactantes": surfactantes, "oleos_graxas": oleos_graxas,
                "hidrocarbonetos": hidrocarbonetos, "benzeno": benzeno, "tolueno": tolueno,
                "xileno": xileno, "etilbenzeno": etilbenzeno, "trihalometanos": thms,
                "pesticidas": pesticidas, "herbicidas": herbicidas, "organofosforados": organofosforados,
                "carbamatos": carbamatos, "cot": cot, "iqa": iqa, "iet": iet, "radioatividade": radioatividade
            }
    
    # Botões para adicionar/remover pontos
    col_b1, col_b2 = st.columns([1, 1])
    with col_b1:
        if len(st.session_state.analises_avancadas_temp) < 10 and st.button("➕ Adicionar outro ponto (avançado)"):
            st.session_state.analises_avancadas_temp.append({})
            st.rerun()
    with col_b2:
        if len(st.session_state.analises_avancadas_temp) > 1 and st.button("➖ Remover último ponto (avançado)"):
            st.session_state.analises_avancadas_temp.pop()
            st.rerun()
    
    st.divider()
    if st.button("💾 Salvar todas as análises avançadas", type="primary"):
        st.session_state.dados_app["analises_avancadas"] = st.session_state.analises_avancadas_temp
        salvar_dados(st.session_state.dados_app)
        st.success(f"{len(st.session_state.analises_avancadas_temp)} ponto(s) de análise avançada salvo(s) com sucesso!")


#Bloco 8 - Aba 4: Levantamento Ambiental
def aba_levantamento():
    st.header("🌍 4. Levantamento de Causas Ambientais")
    
    # Carregar dados existentes
    lev = st.session_state.dados_app.get("levantamento", {})
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Características da Bacia")
        cobertura_solo = st.selectbox("Cobertura do solo predominante", 
                                      ["Florestada", "Pastagem", "Agricultura", "Urbana", "Área degradada", "Mista"],
                                      index=["Florestada", "Pastagem", "Agricultura", "Urbana", "Área degradada", "Mista"].index(lev.get("cobertura_solo", "Florestada")))
        
        tipo_solo = st.selectbox("Tipo de solo predominante",
                                 ["Argiloso", "Arenoso", "Siltoso", "Orgânico", "Latossolo", "Outro"],
                                 index=["Argiloso", "Arenoso", "Siltoso", "Orgânico", "Latossolo", "Outro"].index(lev.get("tipo_solo", "Argiloso")))
        
        relevo = st.selectbox("Relevo da região",
                              ["Plano", "Suave ondulado", "Ondulado", "Fortemente ondulado", "Montanhoso"],
                              index=["Plano", "Suave ondulado", "Ondulado", "Fortemente ondulado", "Montanhoso"].index(lev.get("relevo", "Plano")))
    
    with col2:
        st.subheader("Atividades e Impactos")
        uso_ocupacao = st.multiselect("Uso e ocupação do solo na bacia",
                                      ["Desmatamento", "Urbanização", "Pastagem extensiva", "Agricultura intensiva", "Mineração", "Silvicultura"],
                                      default=lev.get("uso_ocupacao", []))
        
        fontes_poluicao = st.multiselect("Fontes de poluição/degradação identificadas",
                                         ["Esgoto doméstico", "Efluente industrial", "Agrotóxicos/fertilizantes", "Resíduos sólidos", "Mineração", "Dragagem", "Queimadas", "Assoreamento"],
                                         default=lev.get("fontes_poluicao", []))
        
        alteracoes = st.multiselect("Alterações no regime hidrológico",
                                   ["Barragens", "Retirada de mata ciliar", "Canalização", "Drenagem de várzeas"],
                                   default=lev.get("alteracoes", []))
    
    st.subheader("Informações Complementares")
    eventos_extremos = st.selectbox("Ocorrência de eventos extremos recentes",
                                   ["Não", "Enxurradas", "Secas prolongadas", "Queimadas", "Ventos fortes"],
                                   index=["Não", "Enxurradas", "Secas prolongadas", "Queimadas", "Ventos fortes"].index(lev.get("eventos_extremos", "Não")))
    
    observacoes = st.text_area("Observações adicionais (ex: afloramento rochoso com metais, histórico de contaminação)", 
                               value=lev.get("observacoes", ""))
    
    st.divider()
    if st.button("💾 Salvar Levantamento Ambiental", type="primary"):
        st.session_state.dados_app["levantamento"] = {
            "cobertura_solo": cobertura_solo, "tipo_solo": tipo_solo, "relevo": relevo,
            "uso_ocupacao": uso_ocupacao, "fontes_poluicao": fontes_poluicao,
            "alteracoes": alteracoes, "eventos_extremos": eventos_extremos,
            "observacoes": observacoes
        }
        salvar_dados(st.session_state.dados_app)
        st.success("Levantamento salvo com sucesso!")
#Bloco 9 - Aba 5: Relatório de Classificação
def aba_relatorio():
    st.header("📊 5. Relatório de Classificação da Qualidade da Água")
    
    analises = st.session_state.dados_app.get("analises", [])
    if not analises:
        st.warning("Nenhuma análise cadastrada. Por favor, cadastre pelo menos um ponto na aba 'Análises'.")
        return
    
    # Classificar cada ponto
    pontos_classificados = []
    for i, ponto in enumerate(analises):
        classe, cor, usos, motivos = classificar_ponto(ponto)
        pontos_classificados.append((ponto.get("nome", f"Ponto {i+1}"), classe, cor, usos, motivos))
    
    # Avaliação geral do trecho
    status_geral, cor_geral, recomendacoes_gerais = avaliar_trecho(pontos_classificados)
    
    # Exibir resumo geral
    st.subheader(f"📌 Classificação Geral do Trecho do {st.session_state.dados_app.get('cadastro', {}).get('corpo_nome', 'Corpo Hídrico')}")
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown(f"<div style='text-align: center; background-color: {'#d4edda' if status_geral == 'Excelente' else '#fff3cd' if status_geral == 'Boa' else '#ffe5b4' if status_geral == 'Regular' else '#f8d7da'}; padding: 20px; border-radius: 10px;'>"
                    f"<h1>{cor_geral} {status_geral}</h1>"
                    f"<p>{recomendacoes_gerais[0]}</p>"
                    f"</div>", unsafe_allow_html=True)
    
    st.divider()
    
    # Detalhamento por ponto
    st.subheader("📋 Classificação por Ponto de Coleta")
    for nome, classe, cor, usos, motivos in pontos_classificados:
        with st.expander(f"{cor} {nome} - {classe}"):
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("**Usos recomendados para esta classe:**")
                for uso in usos[:4]:
                    st.write(f"- {uso}")
            with col_b:
                if motivos:
                    st.markdown("**Fatores que influenciaram a classificação:**")
                    for m in motivos[:3]:
                        st.write(f"- {m}")
    
    # Tabela comparativa dos parâmetros
    st.subheader("📈 Tabela de Parâmetros Medidos")
    df_analises = pd.DataFrame(analises)
    colunas_mostrar = ["nome", "data", "od", "ph", "dbo", "turbidez", "coliformes", "fosforo", "nitrogenio"]
    # Verificar quais colunas existem no DataFrame
    colunas_existentes = [c for c in colunas_mostrar if c in df_analises.columns]
    df_exibicao = df_analises[colunas_existentes]
    st.dataframe(df_exibicao, use_container_width=True)
    
    # Referência legal
    with st.expander("📜 Base Legal utilizada (Resolução CONAMA 357/2005)"):
        st.markdown("""
        A classificação foi realizada com base nos limites da **Resolução CONAMA nº 357/2005** para águas doces:
        - **Classe 1**: OD ≥ 6 mg/L, DBO ≤ 3 mg/L, pH 6-9, E. coli ≤ 200 NMP/100mL, Turbidez ≤ 10 NTU
        - **Classe 2**: OD ≥ 5 mg/L, DBO ≤ 5 mg/L, pH 6-9, E. coli ≤ 1000 NMP/100mL, Turbidez ≤ 40 NTU
        - **Classe 3**: OD ≥ 4 mg/L, DBO ≤ 10 mg/L, pH 6-9, E. coli ≤ 4000 NMP/100mL, Turbidez ≤ 100 NTU
        - **Classe 4**: padrões menos restritivos (navegação, paisagismo)
        
        *Outras leis e normativos aplicáveis: Lei 9.433/1997 (PNRH), Portaria 888/2021 (potabilidade), Lei 11.445/2007 (saneamento).*
        """)


#Bloco 10 - Aba 6: Manejos e Usos Possíveis
def aba_manejos():
    st.header("🌱 6. Possíveis Manejos e Usos da Água")
    
    analises = st.session_state.dados_app.get("analises", [])
    levantamento = st.session_state.dados_app.get("levantamento", {})
    
    if not analises:
        st.warning("Nenhuma análise cadastrada. Cadastre pontos na aba 'Análises' primeiro.")
        return
    
    # Classificação por ponto
    pontos_classificados = []
    for i, ponto in enumerate(analises):
        classe, cor, usos, _ = classificar_ponto(ponto)
        pontos_classificados.append((ponto.get("nome", f"Ponto {i+1}"), classe, cor, usos, []))
    
    status_geral, _, _ = avaliar_trecho(pontos_classificados)
    
    # Gerar recomendações de manejo
    recomendacoes = gerar_recomendacoes_manejo(levantamento, status_geral, analises)
    
    st.subheader("🛠️ Recomendações de Manejo para Melhoria da Qualidade da Água")
    for rec in recomendacoes:
        st.markdown(rec)
    
    st.divider()
    
    # Usos possíveis por classe (por ponto)
    st.subheader("💧 Usos Possíveis para a Água por Ponto de Coleta")
    usos_por_ponto = usos_possiveis_agua(pontos_classificados)
    
    for ponto, lista_usos in usos_por_ponto.items():
        with st.expander(f"📌 {ponto}"):
            for uso in lista_usos:
                st.write(uso)
    
    st.divider()
    
    # Tabela síntese com classificação e usos principais
    st.subheader("📋 Síntese Final dos Pontos")
    sintese = []
    for nome, classe, cor, usos, _ in pontos_classificados:
        sintese.append({
            "Ponto": nome,
            "Classe": classe,
            "Principal uso sugerido": usos[0] if usos else "Não recomendado",
            "Restrição": "Baixa" if "Classe 1" in classe else "Média" if "Classe 2" in classe else "Alta" if "Classe 3" in classe else "Severa"
        })
    df_sintese = pd.DataFrame(sintese)
    st.dataframe(df_sintese, use_container_width=True)


#Bloco 11 - Função principal (main)
def main():
    st.sidebar.title("💧 Sistema de Qualidade da Água")
    st.sidebar.markdown("---")
    st.sidebar.image("https://img.icons8.com/fluency/96/water-quality.png", width=80)
    st.sidebar.markdown("""
    **Módulos do sistema:**  
    - Cadastro de usuário  
    - Análises físico-químicas  
    - Levantamento ambiental  
    - Mapa interativo  
    - Relatório de classificação  
    - Manejos e usos  
    """)
    
    abas = st.sidebar.radio(
        "Navegação",
        ["📋 Cadastro", "🧪 Análises", "🌍 Levantamento", "🗺️ Mapa", "📊 Relatório", "🌱 Manejos e Usos"]
    )
    
    if abas == "📋 Cadastro":
        aba_cadastro()
    elif abas == "🧪 Análises":
        aba_analises()
    elif abas == "🌍 Levantamento":
        aba_levantamento()
    elif abas == "🗺️ Mapa":
        aba_mapa()
    elif abas == "📊 Relatório":
        aba_relatorio()
    elif abas == "🌱 Manejos e Usos":
        aba_manejos()
    
    # Rodapé
    st.sidebar.markdown("---")
    st.sidebar.caption(f"Dados salvos localmente em '{DATA_FILE}'")
    st.sidebar.caption("Leis base: CONAMA 357/2005, Lei 9.433/1997, Portaria 888/2021")


#Bloco 12 - Ponto de entrada da aplicação
if __name__ == "__main__":
    main()
