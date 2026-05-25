import streamlit as st

st.set_page_config(page_title="Oficina Pro", layout="wide")
st.title("⚙️ Oficina Pro - Diagnóstico Técnico")

# Interface básica sem conexão inicial
dtc = st.text_input("Código de Falha (DTC):")
veiculo = st.text_input("Modelo:")
btn = st.button("Consultar Base Técnica")

if btn:
    st.write("Tentando conectar à API...")
    try:
        import google.generativeai as genai
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(f"Analise o {veiculo} com código {dtc}.")
        st.write(response.text)
    except Exception as e:
        st.error(f"Erro na conexão: {e}")
