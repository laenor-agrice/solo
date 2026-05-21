# ============================================================================
# IMPORTAÇÕES
# ============================================================================

import streamlit as st
import pandas as pd
import google.generativeai as genai

# ============================================================================
# CONFIGURAÇÃO DA API GEMINI
# ============================================================================

GEMINI_API_KEY = "SUA_API_KEY_AQUI"

genai.configure(api_key=GEMINI_API_KEY)

modelo_gemini = genai.GenerativeModel("gemini-1.5-flash")

# ============================================================================
# FUNÇÃO IA GENERATIVA COM GEMINI
# ============================================================================

def gerar_resposta_ia(pergunta, dados_solo=None):

    try:

        contexto = ""

        if dados_solo:

            contexto = f"""
            Dados atuais do solo:

            Nitrogênio: {dados_solo.get('nitrogen', 'N/A')}
            Fósforo: {dados_solo.get('phosphorus', 'N/A')}
            Potássio: {dados_solo.get('potassium', 'N/A')}
            pH: {dados_solo.get('ph', 'N/A')}
            Alumínio: {dados_solo.get('aluminum', 'N/A')}
            Cálcio: {dados_solo.get('calcium', 'N/A')}
            Magnésio: {dados_solo.get('magnesium', 'N/A')}
            Argila: {dados_solo.get('clay', 'N/A')}
            Silte: {dados_solo.get('silt', 'N/A')}
            Areia: {dados_solo.get('sand', 'N/A')}

            """

        prompt = f"""
        Você é um especialista em fertilidade do solo, agricultura,
        manejo agrícola, SiBCS e interpretação agronômica.

        {contexto}

        Pergunta do usuário:
        {pergunta}

        Responda de forma técnica, clara e objetiva.
        """

        resposta = modelo_gemini.generate_content(prompt)

        return resposta.text

    except Exception as erro:

        return f"❌ Erro na IA Gemini: {erro}"

# ============================================================================
# ABA 3 - ASSISTENTE IA
# ============================================================================

elif menu == "🤖 3. Assistente IA":

    st.markdown("## 🤖 Assistente Inteligente de Solos")

    st.markdown("""
    <div class="card">
        Faça perguntas relacionadas à fertilidade, nutrientes,
        manejo, classificação do solo e interpretação agronômica.
    </div>
    """, unsafe_allow_html=True)

    pergunta = st.text_area(
        "💬 Digite sua pergunta para a IA:",
        height=180,
        placeholder="Exemplo: O que significa V% no solo?"
    )

    if st.button("🚀 GERAR RESPOSTA IA"):

        if pergunta.strip() == "":

            st.warning("⚠️ Digite uma pergunta.")

        else:

            dados_atuais = {}

            if "dados_calculados" in st.session_state:
                dados_atuais = st.session_state.dados_calculados

            resposta = gerar_resposta_ia(
                pergunta,
                dados_atuais
            )

            st.markdown(f"""
            <div class="result-card">
                <h2>🤖 Resposta da IA Gemini</h2>
                <p style="font-size:1.1rem;">
                    {resposta}
                </p>
            </div>
            """, unsafe_allow_html=True)
