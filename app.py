import streamlit as st

st.set_page_config(page_title="Oficina Pro", layout="centered")
st.title("⚙️ Oficina Pro")

veiculo = st.text_input("Modelo do carro:")
sintoma = st.text_area("Descreva o sintoma:")

if st.button("Analisar"):
    s = sintoma.lower()
    
    # Lista de verificações
    encontrou = False
    
    if "freio" in s:
        st.write("✅ **Verificação de Freio:** Pastilhas, discos e fluído.")
        encontrou = True
    if "motor" in s:
        st.write("✅ **Verificação de Motor:** Velas, bobinas e bicos.")
        encontrou = True
    if "suspensão" in s or "barulho" in s:
        st.write("✅ **Verificação de Suspensão:** Buchas, bieletas e amortecedores.")
        encontrou = True
    if "partida" in s or "bateria" in s:
        st.write("✅ **Verificação de Partida:** Bateria, motor de arranque e alternador.")
        encontrou = True

    if not encontrou:
        st.warning("Não identifiquei o problema nas categorias comuns. Use o scanner para leitura de erros (DTCs).")
