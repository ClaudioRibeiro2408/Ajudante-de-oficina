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
        
        if st.button("📄 Gerar PDF Profissional"):
            pdf = FPDF()
            pdf.add_page()
            
            # --- CABEÇALHO ---
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(0, 10, "Performance Serviços Automotivos", ln=True)
            pdf.set_font("Arial", size=9)
            pdf.cell(0, 5, "64.242.276/0001-69 | Rua Nelly da Cruz Teixeira, 618", ln=True)
            pdf.cell(0, 5, "Foz do Iguaçu - PR | (45) 99804-2742", ln=True)
            pdf.line(10, 32, 200, 32)
            
            # --- INFO ORÇAMENTO ---
            pdf.ln(10)
            pdf.set_font("Arial", 'B', 12)
            pdf.set_fill_color(200, 200, 200)
            pdf.cell(0, 8, f"Orçamento {datetime.now().strftime('%y%m%d')}", ln=True, fill=True)
            pdf.set_font("Arial", '', 10)
            pdf.cell(0, 8, f"Cliente: {cliente_selecionado}", ln=True)
            
            # --- INFORMAÇÕES BÁSICAS ---
            pdf.ln(5)
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(0, 6, "Informações básicas", ln=True)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(2)
            pdf.set_font("Arial", '', 9)
            # Aqui você pode buscar os dados do cliente se tiver salvo no JSON dele
            pdf.cell(95, 6, "Marca: (Conforme cadastro)", ln=0)
            pdf.cell(95, 6, "Modelo: (Conforme cadastro)", ln=1)

            # --- TABELAS ---
            def desenhar_tabela(titulo, tipo_item):
                pdf.ln(5)
                pdf.set_font("Arial", 'B', 10)
                pdf.cell(0, 6, titulo, ln=True)
                pdf.set_font("Arial", 'B', 8)
                # Cabeçalhos da tabela
                pdf.cell(80, 6, "Descrição", border=1, fill=True)
                pdf.cell(20, 6, "Unid.", border=1, fill=True)
                pdf.cell(30, 6, "Preço Unit.", border=1, fill=True)
                pdf.cell(20, 6, "Qtd.", border=1, fill=True)
                pdf.cell(30, 6, "Preço", border=1, fill=True)
                pdf.ln()
                
                pdf.set_font("Arial", '', 8)
                soma = 0
                for it in [i for i in itens_cliente if i.get('Tipo') == tipo_item]:
                    preco = float(it.get('Venda', 0))
                    total_linha = preco * int(it.get('Qtd', 1))
                    pdf.cell(80, 6, it.get('Item', ''), border=1)
                    pdf.cell(20, 6, it.get('Unidade', ''), border=1)
                    pdf.cell(30, 6, f"R$ {preco:.2f}", border=1)
                    pdf.cell(20, 6, str(it.get('Qtd', '')), border=1)
                    pdf.cell(30, 6, f"R$ {total_linha:.2f}", border=1)
                    pdf.ln()
                    soma += total_linha
                return soma

            tot_serv = desenhar_tabela("Serviços", "Serviço")
            tot_pecas = desenhar_tabela("Peças", "Peça")
            
            # --- RODAPÉ DE TOTAIS E ASSINATURA ---
            pdf.ln(10)
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(150, 6, "Total Serviços", border=1, align='R')
            pdf.cell(30, 6, f"R$ {tot_serv:.2f}", border=1, ln=True)
            pdf.cell(150, 6, "Total Peças", border=1, align='R')
            pdf.cell(30, 6, f"R$ {tot_pecas:.2f}", border=1, ln=True)
            pdf.set_fill_color(230, 230, 230)
            pdf.cell(150, 6, "TOTAL GERAL", border=1, align='R', fill=True)
            pdf.cell(30, 6, f"R$ {tot_serv + tot_pecas:.2f}", border=1, fill=True, ln=True)
            
            pdf.ln(20)
            pdf.cell(90, 5, "_________________________________", align='C')
            pdf.cell(90, 5, "_________________________________", align='C', ln=True)
            pdf.cell(90, 5, "Performance Serviços Automotivos", align='C')
            pdf.cell(90, 5, f"{cliente_selecionado}", align='C', ln=True)
            
            pdf.output("orcamento.pdf")
            st.success("PDF gerado!")
            with open("orcamento.pdf", "rb") as f:
                st.download_button("📥 Baixar PDF", f, "orcamento.pdf")

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
