import streamlit as st
import json
import os
import pandas as pd
import requests
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

def chamar_gemini(prompt):
    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key: return "Erro: Chave API não configurada."
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={api_key}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(url, json=payload)
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    except: return "Erro de comunicação com a IA."

# --- FUNÇÃO PDF PROFISSIONAL ---
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

# --- NAVEGAÇÃO E PÁGINAS ---
if 'pagina' not in st.session_state: st.session_state.pagina = "Início"
st.title("⚙️ Oficina Pro")

# [MANTENDO A ESTRUTURA DOS BOTÕES DE NAVEGAÇÃO]
c1, c2, c3 = st.columns(3)
if c1.button("👤 Clientes"): st.session_state.pagina = "Clientes"
if c2.button("🔧 Diagnóstico"): st.session_state.pagina = "Diagnóstico"
if c3.button("📋 Histórico"): st.session_state.pagina = "Histórico"
if st.button("➕ Criar novo orçamento", type="primary"): st.session_state.pagina = "Orçamento"
st.divider()

if st.session_state.pagina == "Orçamento":
    st.header("💰 Novo Orçamento")
    lista_cli = carregar_dados("clientes.json")
    cliente_nome = st.selectbox("Selecione o Cliente", [""] + [c['Nome'] for c in lista_cli])
    cliente_data = next((c for c in lista_cli if c['Nome'] == cliente_nome), None)
    
    if cliente_data:
        with st.form("orc_form", clear_on_submit=True):
            tipo = st.radio("Tipo", ["Peça", "Serviço"])
            peca = st.text_input("Descrição")
            venda = st.number_input("Valor R$", min_value=0.0)
            if st.form_submit_button("Adicionar"):
                dados = carregar_dados("orcamentos.json")
                dados.append({"Cliente": cliente_nome, "Peça": peca, "Venda": venda, "Tipo": tipo})
                salvar_dados("orcamentos.json", dados)
                st.rerun()

        itens = [i for i in carregar_dados("orcamentos.json") if i['Cliente'] == cliente_nome]
        servs = [i for i in itens if i['Tipo'] == "Serviço"]
        pecas = [i for i in itens if i['Tipo'] == "Peça"]
        tot_s = sum(i['Venda'] for i in servs)
        tot_p = sum(i['Venda'] for i in pecas)
        
        st.table(pd.DataFrame(itens))
        if st.button("📥 Gerar PDF"):
            pdf = gerar_pdf(cliente_data, servs, pecas, tot_s, tot_p, tot_s + tot_p)
            st.download_button("Clique aqui para baixar", pdf, "orcamento.pdf", "application/pdf")

# (Adicione as outras páginas: Clientes, Diagnóstico, Histórico como já estavam)
