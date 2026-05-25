import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Oficina Pro", layout="wide")
st.title("⚙️ Oficina Pro")

# Configuração da chave
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Usando um alias de modelo genérico que o próprio SDK do Google resolve
model_name = 'gemini-1.5-flash' 

dtc = st.text_input("DTC:")
veiculo = st.text_input("Veículo:")
btn = st.button("Consultar")

if btn:
    try:
        # Tenta instanciar o modelo
        model = genai.GenerativeModel(model_name)
        
        # Faz a chamada
        response = model.generate_content(f"Como mecânico, analise o {veiculo} com código {dtc}. Seja técnico e preciso.")
        st.markdown(response.text)
        
    except Exception as e:
        st.error(f"Erro técnico: {e}")
        st.write("---")
        st.write("Para resolver, verifique:")
        st.write("1. Sua conta em https://aistudio.google.com/ precisa ter os termos de uso aceitos.")
        st.write("2. Verifique se sua conta não está em uma região com restrições.")
        
