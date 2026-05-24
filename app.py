import streamlit as st
import json
import os
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from datetime import datetime

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Oficina Pro", layout="centered")

# --- FUNÇÕES DE DADOS ---
def carregar_dados(arquivo):
    if not os.path.exists(arquivo): return []
    try:
        with open(arquivo, "r", encoding="utf-8") as f: return json.load(f)
    except: return []

# --- FUNÇÃO DE GERAÇÃO DE PDF (Layout Profissional) ---
def gerar_pdf_final(cliente_nome, itens, arquivo="orcamento.pdf"):
    c = canvas.Canvas(arquivo, pagesize=A4)
    w, h = A4
    
    # 1. CABEÇALHO
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, h - 50, "Performance Serviços Automotivos")
    c.setFont("Helvetica", 9)
    c.drawString(50, h - 65, "64.242.276/0001-69 | Rua Nelly da Cruz Teixeira, 618")
    c.drawString(50, h - 77, "Foz do Iguaçu - PR | (45) 99804-2742")
    c.line(50, h - 85, 550, h - 85)
    
    # 2. DADOS DO CLIENTE
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, h - 110, f"Cliente: {cliente_nome}")
    c.line(50, h - 115, 550, h - 115)
    
    # 3. TABELA
    y = h - 140
    c.setFont("Helvetica-Bold", 10)
    c.rect(50, y - 10, 500, 20, fill=1, fillColor=colors.lightgrey)
    c.drawString(60, y - 3, "DESCRIÇÃO")
    c.drawString(350, y - 3, "UNID.")
    c.drawString(450, y - 3, "TOTAL")
    
    # 4. ITENS
    c.setFont("Helvetica", 10)
    y -= 30
    total_geral = 0
    for it in itens:
        preco = float(it.get('Venda', 0))
        qtd = int(it.get('Qtd', 1))
        total_linha = preco * qtd
        total_geral += total_linha
        c.drawString(60, y, str(it.get('Item', '')))
        c.drawString(350, y, str(it.get('Unidade', '')))
        c.drawString(450, y, f"R$ {total_linha:.2f}")
        y -= 20
    
    # 5. RODAPÉ
    c.line(50, y, 550, y)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(400, y - 20, f"TOTAL GERAL: R$ {total_geral:.2f}")
    c.setFont("Helvetica", 8)
    c.drawString(100, 100, "__________________________")
    c.drawString(110, 85, "Performance Serviços")
    c.drawString(350, 100, "__________________________")
    c.drawString(370, 85, "Assinatura do Cliente")
    c.save()

# --- NAVEGAÇÃO ---
if 'pagina' not in st.session_state: st.session_state.pagina = "Início"

st.title("⚙️ Oficina Pro")
c1, c2, c3, c4 = st.columns(4)
if c1.button("👤 Clientes"): st.session_state.pagina = "Clientes"
if c2.button("🔧 Diagnóstico"): st.session_state.pagina = "Diagnóstico"
if c3.button("📋 Histórico"): st.session_state.pagina = "Histórico"
