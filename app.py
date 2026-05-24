import streamlit as st
import json
import os
import pandas as pd
import requests
from fpdf import FPDF

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

c1, c2, c3 = st.columns(3)
if c1.button("👤 Clientes", use_container_width=True): st.session_state.pagina = "Clientes"
if c2.button("🔧 Diagnóstico", use_container_width=True): st.session_state.pagina = "Diagnóstico"
if c3.button("📋 Histórico", use_container_width=True): st.session_state.pagina = "Histórico"
if st.button("➕ Novo Orçamento", type="primary", use_container_width=True): st.session_state.pagina = "Orçamento"
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
        if st.form_submit_button("Salvar"):
            d = carregar_dados("clientes.json")
            d.append({"Nome": nome, "Telefone": telefone, "Marca": marca, "Modelo": modelo, "Placa": placa})
            salvar_dados("clientes.json", d); st.rerun()
    st.table(pd.DataFrame(carregar_dados("clientes.json")))

elif st.session_state.pagina == "Orçamento":
    st.header("💰 Novo Orçamento")
    lista_cli = carregar_dados("clientes.json")
    cliente_selecionado = st.selectbox("Selecione o Cliente", [""] + [c['Nome'] for c in lista_cli])
    
    with st.form("orc_form", clear_on_submit=True):
        tipo = st.radio("Tipo", ["Peça", "Serviço"], horizontal=True)
        item = st.text_input("Qual é o item?")
        detalhes = st.text_area("Detalhes (opcional)")
        c1, c2 = st.columns(2)
        unidade = c1.selectbox("Unidade", ["un", "kg", "litro", "metro", "hora", "par"])
        qtd = c2.number_input("Quantidade", min_value=1, value=1)
        
        st.subheader("Custo & Lucro")
        c_custo, c_venda = st.columns(2)
        custo = c_custo.number_input("Custo unitário (R$)", min_value=0.0, value=0.0)
        venda = c_venda.number_input("Venda final (R$)", min_value=0.0, value=0.0)
        
        if custo > 0 and venda > 0:
            margem = ((venda - custo) / venda) * 100
            st.info(f"💰 Margem de lucro: **{margem:.2f}%**")
        
        with st.expander("Outros detalhes"):
            marca = st.text_input("Marca")
            cod_b = st.text_input("Código de barras")
            cod_i = st.text_input("Código interno")
            
        salvar_cat = st.checkbox("Salvar no catálogo")
        submit = st.form_submit_button("Adicionar ao pedido")
        
    if submit:
        if cliente_selecionado and item:
            d = carregar_dados("orcamentos.json")
            d.append({
                "Cliente": cliente_selecionado, "Tipo": tipo, "Item": item, "Venda": venda, 
                "Qtd": qtd, "Unidade": unidade, "Custo": custo, "Marca": marca, 
                "Margem": f"{((venda - custo) / venda * 100) if venda > 0 else 0:.2f}%"
            })
            salvar_dados("orcamentos.json", d); st.rerun()
        else:
            st.error("Selecione um cliente e descreva o item.")
    
    lista = carregar_dados("orcamentos.json")
    itens_cliente = [i for i in lista if i['Cliente'] == cliente_selecionado]
    if itens_cliente:
        st.table(pd.DataFrame(itens_cliente))
        if st.button("📄 Gerar PDF"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(200, 10, txt=f"Orcamento: {cliente_selecionado}", ln=True, align='C')
            pdf.set_font("Arial", size=12)
            
            for it in itens_cliente:
                # Usamos .get() com valores padrão para evitar o KeyError
                item_nome = it.get('Item', 'N/A')
                qtd = it.get('Qtd', 0)
                unid = it.get('Unidade', '')
                venda = it.get('Venda', 0.0)
                
                texto = f"{item_nome} - {qtd} {unid} | R$ {float(venda):.2f}"
                pdf.cell(200, 10, txt=texto, ln=True)
                
            pdf.output("orcamento.pdf")
            st.success("PDF Gerado!")
            msg = f"Ola, segue o orcamento para {cliente_selecionado}."
            st.link_button("Enviar via WhatsApp", f"https://wa.me/?text={msg}")

elif st.session_state.pagina == "Diagnóstico":
    st.header("🔧 Diagnóstico Técnico IA")
    v_diag = st.text_input("Veículo")
    p_diag = st.text_area("Descreva o sintoma")
    if st.button("Analisar com IA"):
        with st.spinner("Consultando..."):
            st.write(chamar_gemini(f"Diagnóstico para {v_diag}: {p_diag}"))

elif st.session_state.pagina == "Histórico":
    st.header("📋 Financeiro & Histórico")
    orc = carregar_dados("orcamentos.json")
    desp = carregar_dados("despesas.json")
    tot_v = sum(float(i.get("Venda", 0)) for i in orc)
    tot_d = sum(float(i.get("Valor", 0)) for i in desp)
    col_a, col_b = st.columns(2)
    col_a.metric("Total Faturado", f"R$ {tot_v:.2f}")
    col_b.metric("Lucro Bruto", f"R$ {tot_v - tot_d:.2f}")
    with st.expander("➕ Lançar Despesa"):
        with st.form("desp_form", clear_on_submit=True):
            d_desc = st.text_input("Descrição")
            d_val = st.number_input("Valor")
            if st.form_submit_button("Salvar Despesa"):
                desp.append({"Descrição": d_desc, "Valor": d_val})
                salvar_dados("despesas.json", desp); st.rerun()
    st.table(pd.DataFrame(orc))

if st.session_state.pagina != "Início":
    if st.button("⬅️ Voltar"): st.session_state.pagina = "Início"; st.rerun()
