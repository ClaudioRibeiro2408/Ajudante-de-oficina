import streamlit as st
import json
import os
import pandas as pd

# Configuração simples
st.set_page_config(page_title="Oficina Pro", layout="wide")

# Funções de Banco de Dados (as mesmas que funcionavam)
def carregar_json(arquivo):
    if os.path.exists(arquivo):
        with open(arquivo, "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return []
    return []

def salvar_json(arquivo, dados):
    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

# Título
st.title("⚙️ Sistema da Oficina")

# Abas
tab1, tab2, tab3, tab4 = st.tabs(["👥 Clientes", "📦 Almoxarifado", "💰 Orçamentos", "📋 Histórico"])

# ABA CLIENTES
with tab1:
    st.header("Cadastro de Clientes")
    nome = st.text_input("Nome do Cliente")
    placa = st.text_input("Placa do Veículo")
    if st.button("Salvar Cliente"):
        dados = carregar_json("clientes.json")
        dados.append({"Nome": nome, "Placa": placa})
        salvar_json("clientes.json", dados)
        st.success("Cliente salvo com sucesso!")
    
    st.table(pd.DataFrame(carregar_json("clientes.json")))

# ABA ALMOXARIFADO
with tab2:
    st.header("Almoxarifado")
    item = st.text_input("Nome da Peça")
    preco = st.number_input("Preço R$", value=0.0)
    if st.button("Salvar Peça"):
        dados = carregar_json("estoque.json")
        dados.append({"Peça": item, "Preço": preco})
        salvar_json("estoque.json", dados)
        st.success("Peça salva!")
    
    st.table(pd.DataFrame(carregar_json("estoque.json")))

# ABA ORÇAMENTOS E HISTÓRICO
with tab3:
    st.write("Em breve: Gerador de Orçamentos")
with tab4:
    st.write("Em breve: Histórico de Serviços")
