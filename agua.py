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


#Bloco 6 - Aba 2: Análises
def aba_analises():
    st.header("🧪 2. Análises de Qualidade da Água")
    st.caption("Preencha os parâmetros para cada ponto de coleta. No mínimo 1 ponto, máximo 10.")
    
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
            col1, col2, col3 = st.columns(3)
            
            # Dados básicos do ponto
            ponto_nome = st.text_input(f"Nome/ID do ponto {i+1}", key=f"nome_{i}", 
                                       value=st.session_state.analises_temp[i].get("nome", f"Ponto {i+1}"))
            ponto_lat = st.number_input(f"Latitude (ponto {i+1})", key=f"lat_{i}", format="%.6f",
                                        value=st.session_state.analises_temp[i].get("lat", -15.0))
            ponto_lon = st.number_input(f"Longitude (ponto {i+1})", key=f"lon_{i}", format="%.6f",
                                        value=st.session_state.analises_temp[i].get("lon", -45.0))
            data_coleta = st.date_input(f"Data da coleta {i+1}", key=f"data_{i}",
                                        value=datetime.strptime(st.session_state.analises_temp[i].get("data", datetime.now().strftime("%Y-%m-%d")), "%Y-%m-%d") if st.session_state.analises_temp[i].get("data") else datetime.now())
            
            col4, col5 = st.columns(2)
            with col4:
                st.markdown("**Parâmetros Físico-Químicos**")
                od = st.number_input(f"Oxigênio Dissolvido - OD (mg/L)", key=f"od_{i}", value=float(st.session_state.analises_temp[i].get("od", 7.0)), step=0.1)
                ph = st.number_input(f"pH", key=f"ph_{i}", value=float(st.session_state.analises_temp[i].get("ph", 7.0)), step=0.1)
                dbo = st.number_input(f"DBO (mg/L)", key=f"dbo_{i}", value=float(st.session_state.analises_temp[i].get("dbo", 2.0)), step=0.1)
                turbidez = st.number_input(f"Turbidez (NTU)", key=f"turbidez_{i}", value=float(st.session_state.analises_temp[i].get("turbidez", 5.0)), step=0.1)
                temperatura = st.number_input(f"Temperatura (°C)", key=f"temp_{i}", value=float(st.session_state.analises_temp[i].get("temperatura", 25.0)), step=0.1)
            
            with col5:
                st.markdown("**Parâmetros Biológicos e Nutrientes**")
                coliformes = st.number_input(f"E. coli/Coliformes (NMP/100mL)", key=f"col_{i}", value=int(st.session_state.analises_temp[i].get("coliformes", 50)), step=10)
                fosforo = st.number_input(f"Fósforo Total (mg/L)", key=f"p_{i}", value=float(st.session_state.analises_temp[i].get("fosforo", 0.03)), step=0.01, format="%.4f")
                nitrogenio = st.number_input(f"Nitrogênio Total (mg/L)", key=f"n_{i}", value=float(st.session_state.analises_temp[i].get("nitrogenio", 0.5)), step=0.1)
                cor_aparente = st.number_input(f"Cor Aparente (mg/L Pt-Co)", key=f"cor_{i}", value=int(st.session_state.analises_temp[i].get("cor_aparente", 10)), step=5)
                residuo_total = st.number_input(f"Resíduo Total (mg/L)", key=f"res_{i}", value=int(st.session_state.analises_temp[i].get("residuo_total", 200)), step=50)
            
            # Salvar no dicionário temporário
            st.session_state.analises_temp[i] = {
                "nome": ponto_nome, "lat": ponto_lat, "lon": ponto_lon, "data": str(data_coleta),
                "od": od, "ph": ph, "dbo": dbo, "turbidez": turbidez, "temperatura": temperatura,
                "coliformes": coliformes, "fosforo": fosforo, "nitrogenio": nitrogenio,
                "cor_aparente": cor_aparente, "residuo_total": residuo_total
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
    if st.button("💾 Salvar todas as análises", type="primary"):
        st.session_state.dados_app["analises"] = st.session_state.analises_temp
        salvar_dados(st.session_state.dados_app)
        st.success(f"{len(st.session_state.analises_temp)} ponto(s) de coleta salvo(s) com sucesso!")


#Bloco 7 - Aba 3: Levantamento Ambiental
def aba_levantamento():
    st.header("🌍 3. Levantamento de Causas Ambientais")
    
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
                                   ["Não","Altas Preciptações", "Secas prolongadas", "Queimadas", "Ventos fortes"],
                                   index=["Não", "Altas Preciptações", "Secas prolongadas", "Queimadas", "Ventos fortes"].index(lev.get("eventos_extremos", "Não")))
    
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


#Bloco 8 - Aba 4: Mapa de Localização
def aba_mapa():
    st.header("🗺️ 4. Mapa de Localização")
    #st.markdown("""
   # **Instruções para Google Maps**:  
   # - O mapa abaixo usa OpenStreetMap por padrão (sem necessidade de chave).  
    #- Para usar Google Maps como base, obtenha uma chave de API em [Google Cloud Console](https://console.cloud.google.com/), ative a Maps JavaScript API e insira a chave abaixo.
    """)#
    
    chave_gmaps = st.text_input("AIzaSyCbBzrvMUD8EZLO7v9EoYM9jiTmDDvDs9I", type="password", 
                                help="Se não informar, será usado OpenStreetMap.")
    
    # Coletar coordenadas do cadastro e pontos
    cad = st.session_state.dados_app.get("cadastro", {})
    fazenda_coords = (cad.get("fazenda_lat", -15.0), cad.get("fazenda_lon", -45.0))
    fazenda_nome = cad.get("fazenda_nome", "Fazenda")
    corpo_nome = cad.get("corpo_nome", "Corpo hídrico")
    
    analises = st.session_state.dados_app.get("analises", [])
    
    # Criar mapa centralizado na fazenda
    m = folium.Map(location=[fazenda_coords[0], fazenda_coords[1]], zoom_start=13, 
                   control_scale=True)
    
    # Adicionar marcador da fazenda
    folium.Marker(
        location=[fazenda_coords[0], fazenda_coords[1]],
        popup=f"🏠 {fazenda_nome}",
        icon=folium.Icon(color="green", icon="home", prefix='fa'),
        tooltip="Fazenda"
    ).add_to(m)
    
    # Adicionar marcador do corpo hídrico (aproximado - mesmo ponto ou poderia ser outro)
    folium.Marker(
        location=[fazenda_coords[0]+0.002, fazenda_coords[1]+0.003],
        popup=f"💧 {corpo_nome}",
        icon=folium.Icon(color="blue", icon="tint", prefix='fa'),
        tooltip="Corpo hídrico"
    ).add_to(m)
    
    # Adicionar pontos de coleta
    for i, ponto in enumerate(analises):
        lat = ponto.get("lat")
        lon = ponto.get("lon")
        if lat and lon:
            classe, cor, _, _ = classificar_ponto(ponto)
            cor_icon = "darkgreen" if "Classe 1" in classe else "orange" if "Classe 2" in classe else "red"
            popup_text = f"📌 {ponto.get('nome', f'Ponto {i+1}')}<br>Data: {ponto.get('data', 'N/A')}<br>Classe: {classe}<br>OD: {ponto.get('od', 'N/A')} mg/L<br>pH: {ponto.get('ph', 'N/A')}"
            folium.Marker(
                location=[lat, lon],
                popup=popup_text,
                icon=folium.Icon(color=cor_icon, icon="water", prefix='fa'),
                tooltip=ponto.get('nome', f'Ponto {i+1}')
            ).add_to(m)
    
    # Se houver chave do Google Maps, tentar adicionar tile layer (requer chave)
    if chave_gmaps and chave_gmaps.strip():
        try:
            folium.TileLayer(
                tiles=f"https://mt1.google.com/vt/lyrs=m&x={{x}}&y={{y}}&z={{z}}&key={chave_gmaps}",
                attr="Google Maps",
                name="Google Maps",
                overlay=False,
                control=True
            ).add_to(m)
            st.success("Camada do Google Maps adicionada (requer chave válida).")
        except Exception as e:
            st.warning(f"Não foi possível adicionar o Google Maps: {e}")
    
    folium.LayerControl().add_to(m)
    
    st_folium(m, width=900, height=600)
    
    # Tabela de coordenadas dos pontos
    if analises:
        st.subheader("Coordenadas dos pontos de coleta (SIRGAS 2000 - graus decimais)")
        df_pontos = pd.DataFrame([{
            "Ponto": p.get("nome", f"Ponto {i+1}"),
            "Latitude": p.get("lat", "N/A"),
            "Longitude": p.get("lon", "N/A"),
            "Data": p.get("data", "N/A")
        } for i, p in enumerate(analises)])
        st.dataframe(df_pontos, use_container_width=True)
    else:
        st.info("Nenhum ponto de coleta cadastrado ainda. Vá para a aba 'Análises'.")


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
