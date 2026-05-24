import streamlit as st

# Configuração básica
st.set_page_config(page_title="Oficina Pro", layout="centered")

# Cabeçalho
st.title("⚙️ Oficina Pro")
st.subheader("Performance Serviços Automotivos")

# Formulário de entrada simples
st.divider()
st.write("### Novo Diagnóstico")

modelo_carro = st.text_input("Modelo do veículo:")
data_servico = st.date_input("Data:")
descricao_problema = st.text_area("Descrição do problema:")

# Botão que apenas exibe o que você digitou
if st.button("Registrar Diagnóstico"):
    if modelo_carro and descricao_problema:
        st.success("Diagnóstico registrado com sucesso!")
        st.write(f"**Veículo:** {modelo_carro}")
        st.write(f"**Data:** {data_servico}")
        st.write(f"**Descrição:** {descricao_problema}")
    else:
        st.error("Por favor, preencha o modelo e a descrição.")

# Rodapé
st.divider()
st.caption("Foz do Iguaçu - PR")
