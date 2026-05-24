import streamlit as st
import json
import os
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

st.set_page_config(page_title="Oficina Pro", layout="wide")

# --- FUNÇÕES DE PERSISTÊNCIA ---
def carregar_dados(arquivo):
    if not os.path.exists(arquivo): return []
    with open(arquivo, "r", encoding="utf-8") as f:
        try: return json.load(f)
        except: return []

def salvar_dados(arquivo, dados):
    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

# --- FUNÇÃO PDF ---
def gerar_pdf(cliente_nome, dados_orcamento):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, 750, f"ORÇAMENTO - {cliente_nome}")
    p.setFont("Helvetica", 10)
    
    y = 700
    total = 0
    for item in dados_orcamento:
        p.drawString(50, y, f"{item.get('Peça')} | Qtd: {item.get('Qtd')} | MO: R${item.get('Mão de Obra', 0):.2f} | Venda: R${item.get('Venda', 0):.2f}")
        total += (item.get('Venda', 0) * item.get('Qtd', 0)) + item.get('Mão de Obra', 0)
        y -= 20
    
    p.drawString(50, y - 20, f"TOTAL: R$ {total:.2f}")
    p.save()
    buffer.seek(0)
    return buffer

# --- INTERFACE ---
aba1, aba2 = st.tabs(["👤 Clientes", "💰 Orçamento"])

# ABA 1: CLIENTES
with aba1:
    st.header("👤 Clientes")
    with st.form("cli_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        nome = c1.text_input("Nome do Cliente")
        placa = c2.text_input("Placa do Veículo")
        if st.form_submit_button("Salvar"):
            dados = carregar_dados("clientes.json")
            dados.append({"Nome": nome, "Placa": placa})
            salvar_dados("clientes.json", dados)
            st.rerun()
    st.table(pd.DataFrame(carregar_dados("clientes.json")))

# ABA 2: ORÇAMENTO
with aba2:
    st.header("💰 Orçamento")
    clientes = [c['Nome'] for c in carregar_dados("clientes.json")]
    
    cliente_selecionado = st.selectbox("Selecione o Cliente", [""] + clientes)
    
    with st.form("orc_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        peca = c1.text_input("Peça/Serviço")
        v_venda = c1.number_input("Preço Venda", min_value=0.0)
        qtd = c2.number_input("Qtd", value=1.0)
        mo = c2.number_input("Mão de Obra", value=0.0)
        
        if st.form_submit_button("Adicionar"):
            if cliente_selecionado:
                dados = carregar_dados("orcamentos.json")
                dados.append({"Cliente": cliente_selecionado, "Peça": peca, "Venda": v_venda, "Qtd": qtd, "Mão de Obra": mo})
                salvar_dados("orcamentos.json", dados)
                st.rerun()
            else:
                st.error("Selecione um cliente primeiro!")

    lista = [i for i in carregar_dados("orcamentos.json") if i['Cliente'] == cliente_selecionado]
    if lista:
        st.table(pd.DataFrame(lista))
        if st.button("Gerar PDF"):
            st.download_button("Baixar", gerar_pdf(cliente_selecionado, lista), "orcamento.pdf", "application/pdf")
