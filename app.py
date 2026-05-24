import streamlit as st
import json
import os
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

st.set_page_config(page_title="Oficina Pro", layout="wide")

# --- FUNÇÕES ---
def carregar_dados(arquivo):
    if not os.path.exists(arquivo): return []
    try:
        with open(arquivo, "r", encoding="utf-8") as f:
            return json.load(f)
    except: return []

def salvar_dados(arquivo, dados):
    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

# --- INTERFACE ---
st.title("⚙️ Oficina Pro")
aba1, aba2 = st.tabs(["👤 Clientes", "💰 Orçamento"])

# ABA 1: CLIENTES COM NOVOS CAMPOS
with aba1:
    st.header("👤 Cadastro de Cliente")
    with st.form("cli_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        nome = col1.text_input("Nome do Cliente")
        telefone = col1.text_input("Telefone")
        marca = col2.text_input("Marca do Veículo")
        modelo = col2.text_input("Modelo do Veículo")
        placa = col2.text_input("Placa")
        
        if st.form_submit_button("Salvar Cliente"):
            if nome:
                dados = carregar_dados("clientes.json")
                dados.append({
                    "Nome": nome, "Telefone": telefone, 
                    "Marca": marca, "Modelo": modelo, "Placa": placa
                })
                salvar_dados("clientes.json", dados)
                st.success("Cliente salvo!")
                st.rerun()
            else:
                st.error("O Nome é obrigatório.")
    
    lista_cli = carregar_dados("clientes.json")
    if lista_cli:
        st.table(pd.DataFrame(lista_cli))

# ABA 2: ORÇAMENTO (MANTIDO)
with aba2:
    st.header("💰 Orçamento")
    lista_cli = carregar_dados("clientes.json")
    nomes = [c['Nome'] for c in lista_cli]
    cliente = st.selectbox("Selecione o Cliente", [""] + nomes)
    
    with st.form("orc_form", clear_on_submit=True):
        peca = st.text_input("Peça/Serviço")
        venda = st.number_input("Preço", min_value=0.0)
        if st.form_submit_button("Adicionar"):
            if cliente:
                dados = carregar_dados("orcamentos.json")
                dados.append({"Cliente": cliente, "Peça": peca, "Venda": venda})
                salvar_dados("orcamentos.json", dados)
                st.rerun()
            else:
                st.error("Selecione o cliente primeiro!")
    
    lista_orc = carregar_dados("orcamentos.json")
    if lista_orc:
        # Filtra apenas do cliente selecionado
        df_filtrado = pd.DataFrame([i for i in lista_orc if i['Cliente'] == cliente])
        if not df_filtrado.empty:
            st.table(df_filtrado)
