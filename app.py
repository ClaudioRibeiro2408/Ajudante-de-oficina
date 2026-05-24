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

# --- NAVEGAÇÃO ---
if 'pagina' not in st.session_state: st.session_state.pagina = "Início"
st.title("⚙️ Oficina Pro")

c1, c2, c3 = st.columns(3)
if c1.button("👤 Clientes"): st.session_state.pagina = "Clientes"
if c2.button("🔧 Diagnóstico"): st.session_state.pagina = "Diagnóstico"
if c3.button("📋 Histórico"): st.session_state.pagina = "Histórico"

if st.button("➕ Criar novo orçamento", type="primary"): 
    st.session_state.pagina = "Orçamento"
st.divider()

# --- PÁGINAS ---
if st.session_state.pagina == "Clientes":
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
                dados.append({"Nome": nome, "Telefone": telefone, "Marca": marca, "Modelo": modelo, "Placa": placa})
                salvar_dados("clientes.json", dados)
                st.success("Cliente salvo!"); st.rerun()

elif st.session_state.pagina == "Orçamento":
    st.header("💰 Novo Orçamento")
    lista_cli = carregar_dados("clientes.json")
    nomes = [c['Nome'] for c in lista_cli]
    cliente = st.selectbox("Selecione o Cliente", [""] + nomes)
    cliente_data = next((c for c in lista_cli if c['Nome'] == cliente), None)
    
    with st.form("orc_form", clear_on_submit=True):
        tipo = st.radio("Tipo do item", ["Serviço", "Peça"])
        peca = st.text_input("Descrição")
        venda = st.number_input("Preço R$", min_value=0.0)
        if st.form_submit_button("Adicionar"):
            if cliente:
                dados = carregar_dados("orcamentos.json")
                dados.append({"Cliente": cliente, "Peça": peca, "Venda": venda, "Tipo": tipo})
                salvar_dados("orcamentos.json", dados)
                st.rerun()
            else: st.error("Selecione um cliente!")
            
    lista_orc = carregar_dados("orcamentos.json")
    itens_cli = [i for i in lista_orc if i['Cliente'] == cliente]
    if itens_cli:
        st.table(pd.DataFrame(itens_cli))
        if st.button("📥 Gerar PDF"):
            s = [i for i in itens_cli if i['Tipo'] == "Serviço"]
            pe = [i for i in itens_cli if i['Tipo'] == "Peça"]
            ts = sum(i['Venda'] for i in s)
            tp = sum(i['Venda'] for i in pe)
            pdf = gerar_pdf(cliente_data, s, pe, ts, tp, ts+tp)
            st.download_button("Baixar PDF", pdf, "orcamento.pdf")

elif st.session_state.pagina == "Diagnóstico":
    st.header("🔧 Diagnóstico Técnico IA")
    v_diag = st.text_input("Veículo")
    p_diag = st.text_area("Descreva o sintoma")
    if st.button("Analisar com IA"):
        if v_diag and p_diag:
            with st.spinner("Consultando..."):
                st.write(chamar_gemini(f"Diagnóstico para {v_diag}: {p_diag}"))

elif st.session_state.pagina == "Histórico":
    st.header("💰 Financeiro & Histórico")
    orcamentos = carregar_dados("orcamentos.json")
    despesas = carregar_dados("despesas.json")
    tv = sum(float(i.get("Venda", 0)) for i in orcamentos)
    td = sum(float(d.get("Valor", 0)) for d in despesas)
    
    c_a, c_b = st.columns(2)
    c_a.metric("Total Faturado", f"R$ {tv:.2f}")
    c_b.metric("Lucro", f"R$ {tv - td:.2f}")
    
    with st.expander("➕ Lançar Despesa"):
        with st.form("desp_form", clear_on_submit=True):
            d_desc = st.text_input("Descrição")
            d_val = st.number_input("Valor", min_value=0.0)
            if st.form_submit_button("Salvar"):
                despesas.append({"Descrição": d_desc, "Valor": d_val})
                salvar_dados("despesas.json", despesas); st.rerun()
    if orcamentos: st.table(pd.DataFrame(orcamentos))

if st.session_state.pagina != "Início":
    if st.button("⬅️ Voltar"): st.session_state.pagina = "Início"; st.rerun()
