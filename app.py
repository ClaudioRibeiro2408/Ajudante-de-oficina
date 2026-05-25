import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Oficina Pro", layout="centered")
st.title("⚙️ Oficina Pro - Diagnóstico")

# A configuração da API é feita dentro de uma função, não no carregamento da página
def consultar_ia(veiculo, dtc, descricao):
    try:
        # Aumentamos o tempo de espera e mantemos a conexão limpa
        genai.configure(
            api_key=st.secrets["GOOGLE_API_KEY"],
            client_options={'api_endpoint': 'https://generativelanguage.googleapis.com'}
        )
        
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"Mecânico especialista. Veículo: {veiculo}. DTC: {dtc}. Problema: {descricao}. Me dê o diagnóstico."
        
        # Chamada com timeout explícito
        response = model.generate_content(prompt, request_options={"timeout": 600})
        return response.text
    except Exception as e:
        return f"Falha na resposta: {str(e)}"

# Interface que sempre carrega
veiculo = st.text_input("Veículo:")
dtc = st.text_input("DTC:")
descricao = st.text_area("Descrição:")

if st.button("Consultar"):
    with st.spinner("Conectando..."):
        resultado = consultar_ia(veiculo, dtc, descricao)
        st.write(resultado)
