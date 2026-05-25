import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Oficina Pro", layout="wide")
st.title("⚙️ Oficina Pro")

# Configuração simples
api_key = st.secrets.get("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

dtc = st.text_input("DTC:")
veiculo = st.text_input("Veículo:")
btn = st.button("Consultar")

if btn:
    try:
        # Usamos o método mais básico de inicialização
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(f"Analise o {veiculo} com código {dtc}. Seja técnico.")
        st.markdown(response.text)
    except Exception as e:
        st.error(f"Erro: {e}")
