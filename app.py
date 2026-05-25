import streamlit as st
import google.generativeai as genai
import PIL.Image

st.set_page_config(page_title="Oficina Pro", layout="wide")
st.title("⚙️ Oficina Pro - Diagnóstico Técnico")

# Configuração da API
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("Erro na configuração da API. Verifique sua chave no Streamlit Secrets.")

# --- Interface ---
dtc = st.text_input("DTC / Código de Falha:")
veiculo = st.text_input("Veículo e Motorização:")
sintomas = st.text_area("Descreva o problema ou o que você já testou:")
arquivo = st.file_uploader("Opcional: Envie uma imagem (osciloscópio, conector, etc.)", type=['jpg', 'png'])

btn = st.button("Consultar Diagnóstico")

if btn:
    if not dtc or not veiculo:
        st.warning("Preencha pelo menos o DTC e o Veículo.")
    else:
        try:
            with st.spinner("Consultando base técnica..."):
                prompt = f"""
                Atue como um Engenheiro de Diagnóstico Automotivo Especialista.
                Veículo: {veiculo}
                DTC: {dtc}
                Sintomas/Testes realizados: {sintomas}
                
                Forneça:
                1. Possíveis causas técnicas (ordenadas pela mais provável).
                2. Procedimento de teste recomendado (Multímetro/Osciloscópio).
                3. O que verificar no esquema elétrico (ponto de atenção).
                4. Dica prática de reparador.
                """
                
                # Lógica para enviar com ou sem imagem
                if arquivo:
                    img = PIL.Image.open(arquivo)
                    response = model.generate_content([prompt, img])
                else:
                    response = model.generate_content(prompt)
                
                st.markdown("### 🛠️ Diagnóstico Sugerido:")
                st.write(response.text)
                
        except Exception as e:
            st.error(f"Erro na consulta: {e}")
            st.info("Nota: Se este erro for '404', o Gemini ainda não está liberado para sua chave atual.")
