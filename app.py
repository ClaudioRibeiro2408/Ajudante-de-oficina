import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Oficina Pro", layout="centered")
st.title("⚙️ Oficina Pro - Diagnóstico")

# A configuração da API é feita dentro de uma função, não no carregamento da página
def consultar_ia(veiculo, dtc, descricao):
    try:
        # Configuração com endpoint forçado para evitar o v1beta
        genai.configure(
            api_key=st.secrets["GOOGLE_API_KEY"],
            client_options={'api_endpoint': 'https://generativelanguage.googleapis.com'}
        )
        
        # Tentamos listar os modelos disponíveis para saber o nome correto
        # Isso evita o erro de 'not found'
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"Mecânico especialista: {veiculo}, DTC {dtc}. Descrição: {descricao}. Me dê o diagnóstico técnico."
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Erro técnico: {str(e)}"

# Interface que sempre carrega
veiculo = st.text_input("Veículo:")
dtc = st.text_input("DTC:")
descricao = st.text_area("Descrição:")

if st.button("Consultar"):
    with st.spinner("Conectando..."):
        resultado = consultar_ia(veiculo, dtc, descricao)
        st.write(resultado)
