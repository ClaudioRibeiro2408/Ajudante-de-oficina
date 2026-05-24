import streamlit as st
import json
import os
import pandas as pd
from io import BytesIO
from reportlab.pdfgen import canvas

# --- FUNÇÕES DE DADOS ---
def carregar_json(nome):
    if not os.path.exists(nome): return []
    with open(nome, "r", encoding="utf-8") as f: return json.load(f)

def salvar_json(nome, dados):
    with open(nome, "w", encoding="utf-8") as f: json.dump(dados, f, ensure_ascii=False, indent=4)

# --- APP ---
st.title("Oficina Pro")

# Navegação Simples
pagina = st.sidebar.radio("Menu", ["Orçamento", "Clientes"])

if pagina == "Orçamento":
    st.header("Novo Orçamento")
    
    # Seleção de Cliente
    clientes = carregar_json("clientes.json")
    nome_cli = st.selectbox("Cliente", [""] + [c['Nome'] for c in clientes])
    
    # Formulário
    with st.form("orc", clear_on_submit=True):
        desc = st.text_input("Descrição")
        valor = st.number_input("Valor", min_value=0.0)
        tipo = st.selectbox("Tipo", ["Peça", "Serviço"])
        if st.form_submit_button("Adicionar"):
            db = carregar_json("orcamentos.json")
            db.append({"Cliente": nome_cli, "Desc": desc, "Valor": valor, "Tipo": tipo})
            salvar_json("orcamentos.json", db)
            st.rerun()

    # Exibição
    itens = [i for i in carregar_json("orcamentos.json") if i['Cliente'] == nome_cli]
    if itens:
        df = pd.DataFrame(itens)
        st.table(df)
        st.write(f"Total: R$ {df['Valor'].sum():.2f}")

elif pagina == "Clientes":
    st.header("Clientes")
    with st.form("cli"):
        nome = st.text_input("Nome")
        if st.form_submit_button("Salvar"):
            db = carregar_json("clientes.json")
            db.append({"Nome": nome})
            salvar_json("clientes.json", db)
            st.rerun()
