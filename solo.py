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

            dados["ph"] = calcular_ph(dados)
            
            sb = dados["calcium"] + dados["magnesium"] + dados["potassium"]
            ctc_potencial = sb + dados["h_al"]
            v_percent = (sb / ctc_potencial) * 100 if ctc_potencial > 0 else 0
            
            st.session_state.dados_calculados = dados
            st.session_state.sb = sb
            st.session_state.ctc_potencial = ctc_potencial
            st.session_state.v_percent = v_percent
            st.session_state.cultura_selecionada = cultura
            st.session_state.classificacao_realizada = True
            
            st.success("✅ Classificação realizada com sucesso!")
            
            col_r1, col_r2, col_r3 = st.columns(3)
            with col_r1:
                st.metric("pH do Solo", f"{dados['ph']:.1f}")
            with col_r2:
                st.metric("CTC Potencial", f"{ctc_potencial:.2f} cmolc/dm³")
            with col_r3:
                st.metric("Saturação por Bases (V%)", f"{v_percent:.1f}%")
            
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
# ABA 3 - ADUBAÇÃO PARA VASO
# ============================================================================

elif menu == "🧪 3. Adubação para Vaso":
    st.markdown("## 🧪 Cálculo de Adubação para Vaso")
    
    if not st.session_state.classificacao_realizada:
        st.warning("⚠️ Execute a classificação na ABA 2 primeiro para obter as recomendações baseadas na análise do solo!")
        
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
    
    st.markdown("### 📏 Dimensões do Vaso")
    
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        altura_cm = st.number_input("Altura do vaso (cm)", min_value=5.0, max_value=100.0, value=20.0, step=1.0)
    with col_v2:
        diametro_cm = st.number_input("Diâmetro do vaso (cm)", min_value=5.0, max_value=50.0, value=10.0, step=1.0)
    
    raio_cm = diametro_cm / 2
    area_cm2 = math.pi * (raio_cm ** 2)
    area_m2 = area_cm2 / 10000
    
    st.caption(f"📐 Área do vaso: **{area_m2:.4f} m²** | Volume aproximado: **{(area_m2 * (altura_cm/100)):.3f} m³**")
    
    st.markdown("---")
    st.markdown("### 🌾 Recomendação de Adubação Nitrogenada")
    
    cultura = st.session_state.cultura_selecionada
    st.success(f"Cultura selecionada: **{cultura}**")
    
    dados = st.session_state.dados_calculados
    phosphorus_atual = dados.get("phosphorus", 0)
    potassium_atual = dados.get("potassium", 0)
    
    fator_ajuste = 1.0
    if phosphorus_atual < 15:
        fator_ajuste += 0.2
        st.info("⚠️ Fósforo baixo (+20% na adubação)")
    if potassium_atual < 0.25:
        fator_ajuste += 0.15
        st.info("⚠️ Potássio baixo (+15% na adubação)")
    
    base_n_ha = recomendacao_n_ha.get(cultura, 80)
    recomendacao_ajustada = base_n_ha * fator_ajuste
    
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
        st.markdown("Onde: SB = Soma de Bases, CTC = Capacidade de Troca de Cátions")
    
    with st.expander("🧪 Cálculo do pH"):
        st.markdown("""
        O pH é calculado considerando:
        - Cátions básicos (Ca, Mg, K) → aumentam o pH
        - Alumínio e H+Al → diminuem o pH
        - Matéria Orgânica → efeito tampão
        - **Valores zerados resultam em pH neutro (7.0)**
        """)
    
    with st.expander("🌱 Cálculo da Adubação para Vaso"):
        st.markdown("""
        **Fórmula utilizada:**kg_por_m2 = recomendacao_kg_ha / 10000
kg_vaso = kg_por_m2 * area_do_vaso_m2
gramas_vaso = kg_vaso * 1000

st.markdown("""
**Considerações:**
- Área do vaso calculada a partir do diâmetro (π × r²)
- Ajuste baseado nos níveis de P e K da análise
""")

with st.expander("🪨 Cálculo da Calagem"):
    st.latex(r"NC = \frac{(V_2 - V_1) \times CTC}{100}")

# ============================================================================
# RODAPÉ
# ============================================================================

st.markdown("---")
st.caption(
    "© 2026 - Classificador de Fertilidade do Solo | "
    "Créditos ao SiBCS - Embrapa | "
    "Inclui cálculo de adubação para vasos"
)
