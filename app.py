import streamlit as st
import json
import os
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime

# --- CONFIGURAÇÃO E DADOS ---
st.set_page_config(page_title="Oficina Pro", layout="centered")

def carregar_dados(arquivo):
    if not os.path.exists(arquivo): return []
    try:
        with open(arquivo, "r", encoding="utf-8") as f: return json.load(f)
    except: return []

def salvar_dados(arquivo, dados):
    with open(arquivo, "w", encoding="utf-8") as f: json.dump(dados, f, ensure_ascii=False, indent=4)

# --- FUNÇÃO DE GERAÇÃO DE PDF (Canvas Profissional) ---
def gerar_pdf_final(cliente_nome, itens, arquivo="orcamento.pdf"):
    c = canvas.Canvas(arquivo, pagesize=A4)
    # Cabeçalho
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 800, "Performance Serviços Automotivos")
    c.setFont("Helvetica", 9)
    c.drawString(50, 785, "64.242.276/0001-69 | Rua Nelly da Cruz Teixeira, 618")
    c.drawString(50, 773, "Foz do Iguaçu - PR | (45) 99804-2742")
    c.line(50, 760, 550, 760)
    # Conteúdo
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 730, f"Orçamento para: {cliente_nome}")
    c.setFont("Helvetica", 10)
    y = 700
    for it in itens:
        c.drawString(50, y, f"{it.get('Item')} - {it.get('Qtd')} {it.get('Unidade')} - R$ {float(it.get('Venda', 0)):.2f}")
        y -= 20
    c.save()

# --- NAVEGAÇÃO ---
if 'pagina' not in st.session_state: st.session_state.pagina = "Início"

st.title("⚙️ Oficina Pro")
c1, c2, c3, c4 = st.columns(4)
if c1.button("👤 Clientes"): st.session_state.pagina = "Clientes"
if c2.button("🔧 Diagnóstico"): st.session_state.pagina = "Diagnóstico"
if c3.button("📋 Histórico"): st.session_state.pagina = "Histórico"
if c4.button("➕ Orçamento"): st.session_state.pagina = "Orçamento"
st.divider()

# --- PÁGINAS ---
if st.session_state.pagina == "Clientes":
    st.header("👤 Clientes")
    # ... (seu código de clientes aqui)
    st.table(pd.DataFrame(carregar_dados("clientes.json")))

elif st.session_state.pagina == "Orçamento":
    st.header("💰 Orçamento")
    lista_cli = carregar_dados("clientes.json")
    cliente = st.selectbox("Cliente", [c['Nome'] for c in lista_cli] if lista_cli else [])
    
    if st.button("📄 Gerar PDF"):
        itens = [i for i in carregar_dados("orcamentos.json") if i['Cliente'] == cliente]
        gerar_pdf_final(cliente, itens)
        with open("orcamento.pdf", "rb") as f:
            st.download_button("Baixar PDF", f, "orcamento.pdf")

elif st.session_state.pagina == "Diagnóstico":
    st.header("🔧 Diagnóstico")
    # ... (seu código de diagnóstico)

elif st.session_state.pagina == "Histórico":
    st.header("📋 Histórico")
    st.table(pd.DataFrame(carregar_dados("orcamentos.json")))
