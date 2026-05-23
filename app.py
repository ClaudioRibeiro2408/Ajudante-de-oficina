import streamlit as st
import json
import os
import pandas as pd
import requests
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import datetime

# Configuração da Página
st.set_page_config(page_title="Oficina Pro - Gestão & IA", layout="wide")

# --- FUNÇÕES DE APOIO ---
def carregar_json(arquivo):
    if os.path.exists(arquivo):
        with open(arquivo, "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return []
    return []

def salvar_json(arquivo, dados):
    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

def chamar_gemini(prompt):
    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key: return "Erro: API Key não configurada."
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={api_key}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(url, json=payload)
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    except: return "Erro de comunicação com a IA."

# --- FUNÇÃO PARA GERAR O PDF ---
def gerar_pdf(dados_orcamento):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    largura, altura = letter
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, altura - 50, "ORÇAMENTO TÉCNICO - OFICINA PRO")
    p.line(50, altura - 60, 550, altura - 60)
    
    y = altura - 100
    total_geral = 0
    p.setFont("Helvetica", 10)
    for item in dados_orcamento:
        peca = item.get('Peça', 'Serviço')
        qtd = item.get('Qtd', 0)
        eixo = item.get('Eixo', '')
        lado = item.get('Lado', '')
        mo = item.get('Mão de Obra', 0)
        venda = item.get('Venda', 0)
        linha = f"{peca} | Qtd: {qtd} | {eixo} {lado} | MO: R${mo:.2f} | Venda: R${venda:.2f}"
        p.drawString(50, y, linha)
        total_geral += (venda * qtd) + mo
        y -= 20
    
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y - 20, f"TOTAL DO ORÇAMENTO: R$ {total_geral:.2f}")
    p.save()
    buffer.seek(0)
    return buffer

# --- INTERFACE ---
st.title("⚙️ Oficina Pro | Gestão e Diagnóstico IA")
aba1, aba2, aba3, aba4 = st.tabs(["👤 Clientes", "💰 Orçamento", "🔧 Diagnóstico", "📋 Histórico"])

# ABA 1: CLIENTES
with aba1:
    st.header("👤 Cadastro de Clientes")
    with st.form("form_cli", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            nome = st.text_input("Nome do Cliente")
            telefone = st.text_input("Telefone")
        with c2:
            marca = st.text_input("Marca")
            modelo = st.text_input("Modelo")
            motor = st.text_input
