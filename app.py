import streamlit as st
import google.generativeai as genai
import PIL.Image

st.set_page_config(page_title="Oficina Pro - Diagnóstico", layout="centered")
st.title("⚙️ Oficina Pro - Diagnóstico Técnico")

# Configuração da API
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# Campos de entrada
veiculo = st.text_input("Veículo/Motor:")
dtc = st.text_input("Código de Falha (DTC):")
descricao = st.text_area("O que está acontecendo ou o que já foi testado?")
arquivo = st.file_uploader("Opcional: Subir foto do componente/osciloscópio", type=['jpg', 'png'])

if st.button("Executar Diagnóstico"):
    if not veiculo or not dtc:
        st.error("Por favor, preencha o Veículo e o DTC.")
    else:
        with st.spinner("Analisando dados técnicos..."):
            prompt = f"""
            Atue como um mecânico de elite. Analise o veículo {veiculo} com o código {dtc}.
            Histórico: {descricao}.
            
            Entregue:
            1. Diagnóstico provável.
            2. Pontos de teste elétrico (pinagem/voltagem).
            3. Dica de reparo prático.
            """
            
            try:
                if arquivo:
                    img = PIL.Image.open(arquivo)
                    response = model.generate_content([prompt, img])
                else:
                    response = model.generate_content(prompt)
                
                st.markdown("### 🛠️ Resultado do Diagnóstico")
                st.write(response.text)
            except Exception as e:
                st.error(f"Erro na geração: {e}")
