import streamlit as st
import google.generativeai as genai

st.title("⚙️ Oficina Pro")

# Configuração Pura
api_key = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=api_key)

# Usamos a constante de modelo do pacote para evitar erros de digitação
model = genai.GenerativeModel('gemini-1.5-flash')

veiculo = st.text_input("Veículo:")
dtc = st.text_input("DTC:")
descricao = st.text_area("Descrição do sintoma:")

if st.button("Gerar Diagnóstico"):
    if not api_key:
        st.error("Chave API não configurada.")
    else:
        try:
            with st.spinner("Consultando a base técnica..."):
                prompt = f"Como mecânico especialista, analise o {veiculo} com falha {dtc}. Sintoma: {descricao}. Me dê o diagnóstico e procedimentos de teste."
                response = model.generate_content(prompt)
                st.markdown("### Diagnóstico:")
                st.write(response.text)
        except Exception as e:
            st.error(f"Erro na conexão: {e}")
