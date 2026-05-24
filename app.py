import streamlit as st

st.set_page_config(page_title="Oficina Pro", layout="centered")

st.title("⚙️ Oficina Pro - Diagnóstico Técnico")

# Campos fixos
veiculo = st.text_input("Modelo do carro:")
sintoma = st.text_area("O que o carro está apresentando?")

if st.button("Consultar Base Técnica"):
    if veiculo and sintoma:
        s = sintoma.lower()
        
        # Base de conhecimento técnica rápida
        if "freio" in s:
            diagnostico = "Verificar espessura de pastilhas, nível de fluido e presença de ar no sistema."
        elif "motor" in s or "falha" in s:
            diagnostico = "Testar velas, cabos de ignição e pressão da linha de combustível."
        elif "bateria" in s or "partida" in s:
            diagnostico = "Verificar voltagem da bateria (ideal 12.6V) e funcionamento do motor de arranque."
        elif "aquecimento" in s or "temperatura" in s:
            diagnostico = "Checar nível de líquido de arrefecimento, válvula termostática e ventoinha."
        else:
            diagnostico = "Sintoma não mapeado na base rápida. Recomenda-se teste de rodagem e scanner para leitura de erros."
            
        st.subheader("Diagnóstico Sugerido:")
        st.write(f"Para o veículo {veiculo}:")
        st.info(diagnostico)
    else:
        st.warning("Preencha o modelo e o sintoma para obter uma resposta.")
