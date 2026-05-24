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

def gerar_pdf(cliente_info, itens):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 750, "OFICINA PRO - ORÇAMENTO")
    p.setFont("Helvetica", 12)
    p.drawString(100, 730, f"Cliente: {cliente_info['Nome']}")
    p.drawString(100, 715, f"Telefone: {cliente_info['Telefone']}")
    p.drawString(100, 700, f"Veículo: {cliente_info['Marca']} {cliente_info['Modelo']} - Placa: {cliente_info['Placa']}")
    p.line(100, 690, 500, 690)
    
    y = 670
    total = 0
    p.drawString(100, y, "Descrição")
    p.drawString(400, y, "Valor")
    y -= 20
    
    for item in itens:
        p.drawString(100, y, f"- {item['Peça']}")
        p.drawString(400, y, f"R$ {item['Venda']:.2f}")
        total += item['Venda']
        y -= 15
        if y < 50: p.showPage(); y = 750
        
    p.line(100, y, 500, y)
    p.setFont("Helvetica-Bold", 12)
    p.drawString(330, y-20, f"TOTAL: R$ {total:.2f}")
    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer

# --- CONTROLE DE NAVEGAÇÃO ---
if 'pagina' not in st.session_state:
    st.session_state.pagina = "Início"

# --- TÍTULO E DASHBOARD ---
st.title("⚙️ Oficina Pro")

c1, c2, c3 = st.columns(3)
with c1:
    if st.button("👤 Clientes", use_container_width=True): st.session_state.pagina = "Clientes"
with c2:
    if st.button("🔧 Diagnóstico", use_container_width=True): st.session_state.pagina = "Diagnóstico"
with c3:
    if st.button("📋 Histórico", use_container_width=True): st.session_state.pagina = "Histórico"

if st.button("➕ Criar novo orçamento", use_container_width=True, type="primary"):
    st.session_state.pagina = "Orçamento"

st.divider()

# --- LÓGICA DAS PÁGINAS ---
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
                st.success("Cliente salvo!")
                st.rerun()
    lista_cli = carregar_dados("clientes.json")
    if lista_cli: st.table(pd.DataFrame(lista_cli))

elif st.session_state.pagina == "Orçamento":
    st.header("💰 Novo Orçamento")
    lista_cli = carregar_dados("clientes.json")
    nomes = [c['Nome'] for c in lista_cli]
    cliente_nome = st.selectbox("Selecione o Cliente", [""] + nomes)
    
    # Busca dados do cliente selecionado
    cliente_data = next((c for c in lista_cli if c['Nome'] == cliente_nome), None)
    
    if cliente_data:
        st.info(f"**Veículo:** {cliente_data['Marca']} {cliente_data['Modelo']} | **Placa:** {cliente_data['Placa']} | **Tel:** {cliente_data['Telefone']}")
        
        with st.form("orc_form", clear_on_submit=True):
            peca = st.text_input("Peça/Serviço")
            venda = st.number_input("Preço R$", min_value=0.0)
            if st.form_submit_button("Adicionar Item"):
                dados = carregar_dados("orcamentos.json")
                dados.append({"Cliente": cliente_nome, "Peça": peca, "Venda": venda})
                salvar_dados("orcamentos.json", dados)
                st.rerun()
        
        # Filtra itens deste cliente para o PDF e Visualização
        orcamentos = carregar_dados("orcamentos.json")
        itens_cliente = [i for i in orcamentos if i['Cliente'] == cliente_nome]
        
        if itens_cliente:
            df_itens = pd.DataFrame(itens_cliente)
            st.table(df_itens[["Peça", "Venda"]])
            total_orc = sum(i['Venda'] for i in itens_cliente)
            st.subheader(f"Total: R$ {total_orc:.2f}")
            
            # Botão de PDF
            pdf = gerar_pdf(cliente_data, itens_cliente)
            st.download_button(label="📥 Baixar Orçamento PDF", data=pdf, file_name=f"Orcamento_{cliente_nome}.pdf", mime="application/pdf")

elif st.session_state.pagina == "Diagnóstico":
    st.header("🔧 Diagnóstico Técnico IA")
    v_diag = st.text_input("Veículo")
    p_diag = st.text_area("Descreva o sintoma ou erro")
    if st.button("Analisar com IA"):
        if v_diag and p_diag:
            with st.spinner("Consultando..."):
                st.write(chamar_gemini(f"Diagnóstico para {v_diag}: {p_diag}"))

elif st.session_state.pagina == "Histórico":
    st.header("💰 Financeiro & Histórico")
    orcamentos = carregar_dados("orcamentos.json")
    total_vendas = sum(item.get("Venda", 0) for item in orcamentos)
    despesas = carregar_dados("despesas.json")
    total_despesas = sum(d.get("Valor", 0) for d in despesas)
    
    col_a, col_b = st.columns(2)
    col_a.metric("Total Faturado", f"R$ {total_vendas:.2f}")
    col_b.metric("Lucro Bruto", f"R$ {total_vendas - total_despesas:.2f}")
    
    with st.expander("➕ Lançar Despesa"):
        with st.form("desp"):
            d_desc = st.text_input("Descrição")
            d_val = st.number_input("Valor", min_value=0.0)
            if st.form_submit_button("Salvar"):
                despesas.append({"Descrição": d_desc, "Valor": d_val})
                salvar_dados("despesas.json", despesas)
                st.rerun()
    
    st.subheader("Histórico")
    if orcamentos: st.table(pd.DataFrame(orcamentos))

if st.session_state.pagina != "Início":
    if st.button("⬅️ Voltar"):
        st.session_state.pagina = "Início"
        st.rerun()
