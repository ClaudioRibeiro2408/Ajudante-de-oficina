import streamlit as st
import google.generativeai as genai

# Configuração da página
st.set_page_config(page_title="Oficina Pro - Diagnóstico Técnico", layout="wide")

# Configuração da API via Streamlit Secrets
# Certifique-se de que no seu arquivo de secrets tenha: GOOGLE_API_KEY = "sua_chave_aqui"
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("Erro na configuração da API: Verifique o arquivo de secrets.")

st.title("⚙️ Oficina Pro - Diagnóstico Técnico")
st.write("Sistema de consulta técnica para DTCs, esquemas e osciloscópio.")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Entrada de Dados")
    dtc = st.text_input("Código de Falha (DTC) Ex: P0300:")
    veiculo = st.text_input("Modelo e Motorização:")
    tarefa = st.selectbox("O que você precisa?", 
                          ["Diagnóstico Completo", 
                           "Causas Prováveis", 
                           "Esquema Elétrico (Descrição)", 
                           "Dicas de Osciloscópio (Sinais e Conexão)"])
    
    btn_analisar = st.button("Consultar Base Técnica")

with col2:
    st.subheader("Resultado")
    if btn_analisar:
        if dtc and veiculo:
            prompt = f"""
            Você é um engenheiro automotivo especialista com anos de experiência em diagnóstico avançado.
            Veículo: {veiculo}.
            Código DTC: {dtc}.
            Tarefa solicitada: {tarefa}.
            
            Instruções:
            1. Seja técnico e preciso.
            2. Se for 'Dicas de Osciloscópio', forneça: pinagem, configuração de volts/div e tempo/div, e o formato de onda esperado (ex: quadrado, senoidal).
            3. Se for 'Esquema Elétrico', descreva as conexões e cores de fios padrão.
            4. Se for 'Diagnóstico Completo', siga uma ordem lógica: verificação elétrica -> verificação mecânica -> teste final.
            """
            
            with st.spinner("Consultando manuais técnicos e bases de dados..."):
                try:
                    response = model.generate_content(prompt)
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Erro ao consultar a IA: {e}")
        else:
            st.warning("Preencha o código DTC e o modelo do veículo.")

# Rodapé
st.divider()
st.caption("Performance Serviços Automotivos - Diagnóstico de Alta Precisão")
