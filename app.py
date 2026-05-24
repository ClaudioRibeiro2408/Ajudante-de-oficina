import streamlit as st
import json
import os
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

# Configuração da Página
st.set_page_config(page_title="Oficina Pro", layout="centered")

# --- FUNÇÕES DE APOIO ---
def carregar_dados(arquivo):
    if not os.path.exists(arquivo): return []
    try:
        with open(arquivo, "r", encoding="utf-8") as f:
            return json.load(f)
    except: return []

def salvar_dados(arquivo, dados):
    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

# --- FUNÇÃO PDF ---
def gerar_pdf(cliente_info, itens_servicos, itens_pecas, total_serv, total_pecas, total_geral):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.setFont("Helvetica-Bold", 14)
    p.drawString(100, 750, "Performance Serviços Automotivos")
    p.setFont("Helvetica", 9)
    p.drawString(100, 738, "CNPJ: 64.242.276/0001-69 | Rua Nelly da Cruz Teixeira, 618, Foz do Iguaçu-PR")
    p.line(100, 730, 500, 730)
    p.setFont("Helvetica-Bold", 12)
    p.drawString(100, 710, "Orçamento 005-2026")
    p.setFont("Helvetica", 10)
    p.drawString(100, 695, f"Cliente: {cliente_info['Nome']}")
    p.drawString(100, 683, f"Tel: {cliente_info['Telefone']}")
    p.setFont("Helvetica-Bold", 10)
    p.drawString(100, 660, "Informações básicas")
    p.setFont("Helvetica", 9)
    p.drawString(100, 648, f"Marca: {cliente_info['Marca']}      Modelo: {cliente_info['Modelo']}")
    
    y = 620
    p.setFont("Helvetica-Bold", 10)
    p.drawString(100, y, "Serviços")
    y -= 15
    p.setFont("Helvetica", 9)
    for s in itens_servicos:
        p.drawString(100, y, f"{s['Peça']} | R$ {s['Venda']:.2f}")
        y -= 12
        
    y -= 20
    p.setFont("Helvetica-Bold", 10)
    p.drawString(100, y, "Peças")
    y -= 15
    p.setFont("Helvetica", 9)
    for p_item in itens_pecas:
        p.drawString(100, y, f"{p_item['Peça']} | R$ {p_item['Venda']:.2f}")
        y -= 12
        
    y -= 20
    p.setFont("Helvetica-Bold", 10)
    p.drawString(350, y, f"Total Serviços: R$ {total_serv:.2f}")
    p.drawString(350, y-15, f"Total Peças: R$ {total_pecas:.2f}")
    p.drawString(350, y-30, f"TOTAL GERAL: R$ {total_geral:.2f}")
    
    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer

# --- NAVEGAÇÃO FIXA ---
if 'pagina' not in st.session_state: st.session_state.pagina = "Início"

st.title("⚙️ Oficina Pro")
c1, c2, c3 = st.columns(3)
if c1.button("👤 Clientes", use_container_width=True): st.session_state.pagina = "Clientes"
if c2.button("🔧 Diagnóstico", use_container_width=True): st.session_state.pagina = "Diagnóstico"
if c3.button("📋 Histórico", use_container_width=True): st.session_state.pagina = "Histórico"

if st.button("➕ Criar novo orçamento", use_container_width=True, type="primary"): 
    st.session_state.pagina = "Orçamento"
st.divider()

# --- CONTEÚDO DAS PÁGINAS (Mantendo layout original) ---
if st.session_state.pagina == "Orçamento":
    st.header("💰 Novo Orçamento")
    lista_cli = carregar_dados("clientes.json")
    cliente = st.selectbox("Selecione o
