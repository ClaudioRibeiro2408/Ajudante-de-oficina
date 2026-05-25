import streamlit as st
import google.generativeai as genai

# Configuração da página
st.set_page_config(page_title="Oficina Pro - Diagnóstico Técnico", layout="wide")

# Inicialização da API com o modelo estável
# Inicialização da API automática (busca o modelo disponível na sua conta)
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    
    # Esta linha busca o primeiro modelo disponível que suporte geração de conteúdo
    models = [m for m in genai.list_models() if "generateContent" in m.supported_methods]
    # Pega o primeiro da lista que for do tipo 'gemini'
    model_name = next((m.name for m in models if "gemini" in m.name), "gemini-1.5-flash")
    
    model = genai.GenerativeModel(model_name)
    st.sidebar.write(f"Modelo ativo: {model_name}") # Para você saber qual ele escolheu
except Exception as e:
    st.error(f"Erro ao conectar na API: {e}")
    st.stop()

st.title("⚙️ Oficina Pro - Diagnóstico Técnico")

# Interface
col1, col2 = st.columns([1, 2])

with col1:
    dtc = st.text_input("Código de Falha (DTC) Ex: P0300:")
    veiculo = st.text_input("Modelo e Motorização:")
    tarefa = st.selectbox("O que você precisa?", 
                          ["Diagnóstico Completo", 
                           "Causas Prováveis", 
                           "Esquema Elétrico (Descrição)", 
                           "Dicas de Osciloscópio (Sinais e Conexão)"])
    
    btn_analisar = st.button("Consultar Base Técnica")

with col2:
    if btn_analisar:
        if dtc and veiculo:
            prompt = f"Como mecânico especialista, analise o {veiculo} com código {dtc}. Objetivo: {tarefa}. Seja técnico e preciso."
            with st.spinner("Consultando manuais..."):
                try:
                    response = model.generate_content(prompt)
                    st.markdown("### Resultado:")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"Erro ao consultar a IA: {e}")
        else:
            st.warning("Preencha o DTC e o modelo.")
