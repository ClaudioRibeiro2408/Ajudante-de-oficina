import streamlit as st
import json
import os
import pandas as pd
import requests

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

# --- NAVEGAÇÃO ---
if 'pagina' not in st.session_state: st.session_state.pagina = "Início"

st.title("⚙️ Oficina Pro")

c1, c2, c3 = st.columns(3)
with c1:
    if st.button("👤 Clientes", use_container_width=True): st.session_state.pagina = "Clientes"
with c2:
    if st.button("🔧 Diagnóstico", use_container_width=True): st.session_state.pagina = "Diagnóstico"
with c3:
    if st.button("📋 Histórico", use_container_width=True): st.session_state.pagina = "Histórico"

if st.button("➕ Criar novo orçamento", use_container_width=True, type="primary"): st.session_state.pagina = "Orçamento"

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
                st.success("Cliente salvo!")
                st.rerun()
    lista_cli = carregar_dados("clientes.json")
    if lista_cli: st.table(pd.DataFrame(lista_cli))

elif st.session_state.pagina == "Orçamento":
    st.header("💰 Novo Orçamento")
    lista_cli = carregar_dados("clientes.json")
    nomes = [c['Nome'] for c in lista_cli]
    cliente = st.selectbox("Selecione o Cliente", [""] + nomes)
    with st.form("orc_form", clear_on_submit=True):
        tipo = st.radio("Tipo do item", ["Serviço", "Peça"], horizontal=True)
        peca = st.text_input("Peça/Serviço")
        venda = st.number_input("Preço R$", min_value=0.0)
        obs = st.text_area("Observações")
        if st.form_submit_button("Adicionar"):
            if cliente:
                dados = carregar_dados("orcamentos.json")
                dados.append({"Cliente": cliente, "Peça": peca, "Venda": venda, "Obs": obs, "Tipo": tipo})
                salvar_dados("orcamentos.json", dados)
                st.rerun()
            else: 
                st.error("Selecione um cliente primeiro!")
    lista_orc = carregar_dados("orcamentos.json")
    itens_filtrados = [i for i in lista_orc if i['Cliente'] == cliente]
    if itens_filtrados: 
        df = pd.DataFrame(itens_filtrados)
        st.table(df[['Tipo', 'Peça', 'Venda', 'Obs']])

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
    total_vendas = sum(float(item.get("Venda", 0)) for item in orcamentos) if orcamentos else 0.0
    total_despesas = sum(float(d.get("Valor", 0)) for d in despesas) if despesas else 0.0
    col_a, col_b = st.columns(2)
    col_a.metric("Total Faturado", f"R$ {total_vendas:.2f}")
    col_b.metric("Lucro", f"R$ {total_vendas - total_despesas:.2f}")
    with st.expander("➕ Lançar Despesa"):
        with st.form("desp_form", clear_on_submit=True):
            d_desc = st.text_input("Descrição")
            d_val = st.number_input("Valor", min_value=0.0)
            if st.form_submit_button("Salvar"):
                despesas.append({"Descrição": d_desc, "Valor": d_val})
                salvar_dados("despesas.json", despesas)
                st.rerun()
    st.subheader("Histórico de Orçamentos")
    if orcamentos: st.table(pd.DataFrame(orcamentos))

if st.session_state.pagina != "Início":
    if st.button("⬅️ Voltar"): st.session_state.pagina = "Início"; st.rerun()
