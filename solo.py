
**Onde:**
- **Al3+** = Aluminio trocavel (cmolc/dm3)
- **CTC_efetiva** = SB + Al3+ (cmolc/dm3)
""")

with st.expander("🌾 Tabela de Necessidades por Cultura"):
st.markdown("""
| Cultura | V% Ideal | N min | P min | K min | pH ideal |
|---------|----------|-------|-------|-------|----------|
| **Soja** | 60% | 40 mg/dm3 | 15 mg/dm3 | 0,35 cmolc/dm3 | 5,5-6,5 |
| **Milho (grao)** | 65% | 50 mg/dm3 | 20 mg/dm3 | 0,40 cmolc/dm3 | 5,5-6,5 |
| **Feijao** | 65% | 35 mg/dm3 | 20 mg/dm3 | 0,35 cmolc/dm3 | 5,5-6,5 |
| **Cafe** | 70% | 40 mg/dm3 | 25 mg/dm3 | 0,40 cmolc/dm3 | 5,5-6,5 |
| **Pastagem** | 50% | 30 mg/dm3 | 10 mg/dm3 | 0,25 cmolc/dm3 | 5,0-6,5 |
""")

with st.expander("📏 Unidades de Medida"):
st.markdown("""
| Parametro | Unidade | Equivalencia |
|-----------|---------|--------------|
| Nitrogenio (N) | mg/dm3 | 1 mg/dm3 = 1 ppm |
| Fosforo (P) | mg/dm3 | 1 mg/dm3 = 1 ppm |
| Potassio (K+) | cmolc/dm3 | 1 cmolc/dm3 = 10 mmolc/dm3 |
| Calcio (Ca2+) | cmolc/dm3 | 1 cmolc/dm3 = 10 mmolc/dm3 |
| Magnesio (Mg2+) | cmolc/dm3 | 1 cmolc/dm3 = 10 mmolc/dm3 |
| Aluminio (Al3+) | cmolc/dm3 | - |
| CTC | cmolc/dm3 | - |
| Materia Organica | g/kg | 1 g/kg = 0,1% |
| Densidade | g/cm3 | - |
""")

# ============================================================================
# RODAPE
# ============================================================================

st.markdown("---")
st.caption("© 2026 - Classificador de Fertilidade do Solo | Baseado no SiBCS - Embrapa")
