import streamlit as st
import json
import os
import pandas as pd
import requests
from fpdf import FPDF
from datetime import datetime

st.set_page_config(page_title="Oficina Pro", layout="centered")

# --- FUNÇÕES ---
def carregar_dados(arquivo):
    if not os.path.exists(arquivo): return []
    try:
        with open(arquivo, "r", encoding="utf-8") as f: return json.load(f)
    except: return []

def salvar_dados(arquivo, dados):
    with open(arquivo, "w", encoding="utf-8") as f: json.dump(dados, f, ensure_ascii=False, indent=4)

def chamar_gemini(prompt):
    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key: return "Erro: Chave API não configurada."
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={api_key}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(url, json=payload)
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    except: return "Erro de comunicação com a IA."

# --- NAVEGAÇÃO ---
if 'pagina' not in st.session_state: st.session_state.pagina = "Início"
st.title("⚙️ Oficina Pro")

# [Código de navegação mantido...]
c1, c2, c3 = st.columns(3)
if c1.button("👤 Clientes", use_container_width=True): st.session_state.pagina = "Clientes"
if c2.button("🔧 Diagnóstico", use_container_width=True): st.session_state.pagina = "Diagnóstico"
if c3.button("📋 Histórico", use_container_width=True): st.session_state.pagina = "Histórico"
if st.button("➕ Novo Orçamento", type="primary", use_container_width=True): st.session_state.pagina = "Orçamento"
st.divider()

# --- PÁGINA ORÇAMENTO (COM NOVO PDF) ---
if st.session_state.pagina == "Orçamento":
    st.header("💰 Novo Orçamento")
    lista_cli = carregar_dados("clientes.json")
    cliente_selecionado = st.selectbox("Selecione o Cliente", [""] + [c['Nome'] for c in lista_cli])
    
    with st.form("orc_form", clear_on_submit=True):
        tipo = st.radio("Tipo", ["Peça", "Serviço"], horizontal=True)
        item = st.text_input("Qual é o item?")
        c1, c2 = st.columns(2)
        unidade = c1.selectbox("Unidade", ["un", "kg", "litro", "metro", "hora", "par"])
        qtd = c2.number_input("Quantidade", min_value=1, value=1)
        
        c_custo, c_venda = st.columns(2)
        custo = c_custo.number_input("Custo unitário (R$)", min_value=0.0, value=0.0)
        venda = c_venda.number_input("Venda final (R$)", min_value=0.0, value=0.0)
        
        submit = st.form_submit_button("Adicionar ao pedido")
        
    if submit:
        d = carregar_dados("orcamentos.json")
        d.append({"Cliente": cliente_selecionado, "Tipo": tipo, "Item": item, "Venda": venda, "Qtd": qtd, "Unidade": unidade})
        salvar_dados("orcamentos.json", d); st.rerun()
    
    lista = carregar_dados("orcamentos.json")
    itens_cliente = [i for i in lista if i['Cliente'] == cliente_selecionado]
    
    if itens_cliente:
        st.table(pd.DataFrame(itens_cliente))
        
       # --- NOVO BLOCO PREMIUM ---
        if st.button("📄 Gerar PDF Profissional"):
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib import colors
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            
            caminho = "orcamento.pdf"
            doc = SimpleDocTemplate(caminho, pagesize=A4)
            elementos = []
            estilos = getSampleStyleSheet()

            # Estilo personalizado
            titulo_estilo = ParagraphStyle('titulo', fontSize=18, alignment=1, textColor=colors.HexColor('#2c3e50'))
            elementos.append(Paragraph("Performance Servicos Automotivos", titulo_estilo))
            elementos.append(Spacer(1, 10))
            
            # Dados da tabela
            dados = [["Descricao", "Unid.", "Preco Unit.", "Qtd.", "Total"]]
            total_geral = 0
            for it in itens_cliente:
                p = float(it.get('Venda', 0))
                q = int(it.get('Qtd', 1))
                t = p * q
                total_geral += t
                dados.append([it.get('Item', ''), it.get('Unidade', ''), f"R$ {p:.2f}", str(q), f"R$ {t:.2f}"])

            tabela = Table(dados, colWidths=[180, 50, 80, 50, 80])
            tabela.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]))
            elementos.append(tabela)
            elementos.append(Spacer(1, 20))
            elementos.append(Paragraph(f"TOTAL GERAL: R$ {total_geral:.2f}", ParagraphStyle('total', fontSize=14, alignment=2)))
            
            doc.build(elementos)
            st.success("PDF gerado com sucesso!")
            with open(caminho, "rb") as f:
                st.download_button("Baixar PDF Premium", f, "orcamento.pdf")
# [Restante do código de Clientes, Diagnóstico e Histórico...]
if st.session_state.pagina == "Clientes":
    # (Código de clientes...)
    pass
elif st.session_state.pagina == "Diagnóstico":
    # (Código de diagnóstico...)
    pass
elif st.session_state.pagina == "Histórico":
    # (Código de histórico...)
    pass
