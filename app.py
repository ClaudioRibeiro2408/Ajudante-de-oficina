import streamlit as st

st.set_page_config(page_title="Oficina Pro", layout="centered")

st.title("⚙️ Oficina Pro - Modo de Segurança")

st.write("O sistema está rodando!")

if st.button("Testar Funcionalidade"):
    st.success("O Python está funcionando perfeitamente.")
