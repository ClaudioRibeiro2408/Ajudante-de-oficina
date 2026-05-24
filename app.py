# --- MÓDULO DE DIAGNÓSTICO ---
st.divider()
st.subheader("🔧 Diagnóstico Rápido")

veiculo = st.text_input("Qual o modelo do carro?")
queixa = st.text_area("Descreva o problema:")

if st.button("Gerar Análise"):
    if veiculo and queixa:
        # Aqui fazemos uma análise lógica baseada em palavras-chave
        # Sem depender de APIs externas por enquanto para evitar erros
        q = queixa.lower()
        if "barulho" in q and "freio" in q:
            resultado = "Possível causa: Pastilhas de freio gastas ou falta de lubrificação no cáliper."
        elif "falha" in q and "motor" in q:
            resultado = "Possível causa: Velas de ignição ou bobinas com defeito."
        else:
            resultado = "Recomendada inspeção no scanner automotivo para verificar falhas de sensores."
        
        st.info(f"Análise para {veiculo}: {resultado}")
    else:
        st.error("Por favor, preencha o modelo e o problema.")
