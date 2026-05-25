import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Oficina Pro", layout="wide")
st.title("⚙️ Oficina Pro")

# Configuração explícita para usar a versão v1 (estável)
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"], api_version="v1")
    # Usamos o modelo 'gemini-1.5-flash' com a versão v1 configurada acima
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Erro na configuração: {e}")

dtc = st.text_input("DTC:")
veiculo = st.text_input("Veículo:")
btn = st.button("Consultar")

if btn:
    try:
        response = model.generate_content(f"Como mecânico, analise o {veiculo} com código {dtc}. Seja técnico e preciso.")
        st.markdown(response.text)
    except Exception as e:
        st.error(f"Erro na consulta: {e}")
