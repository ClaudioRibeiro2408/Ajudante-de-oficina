import streamlit as st

def pagina_diagnostico():
    st.header("🔧 Diagnóstico Automotivo com IA")
    
    veiculo = st.text_input("Modelo do Veículo")
    sintomas = st.text_area("Descreva os sintomas (ex: barulho no motor, falhando na partida)")
    
    if st.button("Analisar com IA"):
        if not sintomas:
            st.warning("Por favor, descreva os sintomas primeiro.")
        else:
            # Aqui entra a chamada para a IA
            with st.spinner("Analisando sintomas..."):
                # Exemplo de lógica simples (pode ser substituída por API da OpenAI)
                diagnostico = sugerir_diagnostico(veiculo, sintomas)
                st.success("Diagnóstico Sugerido:")
                st.write(diagnostico)

def sugerir_diagnostico(veiculo, sintomas):
    # Simulação da IA
    sintomas = sintomas.lower()
    if "barulho" in sintomas and "motor" in sintomas:
        return "Possíveis causas: Correia dentada frouxa, tuchos desregulados ou problema na polia."
    elif "falha" in sintomas and "partida" in sintomas:
        return "Possíveis causas: Bateria fraca, velas gastas ou filtro de combustível obstruído."
    else:
        return "Recomendada inspeção física. Verifique sistema de ignição e injeção eletrônica."

# Para chamar no seu app principal, use:
# if st.session_state.pagina == "Diagnóstico": pagina_diagnostico()
