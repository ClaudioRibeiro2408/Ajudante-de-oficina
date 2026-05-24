import streamlit as st
import json
import os
import pandas as pd
import requests

st.set_page_config(page_title="Oficina Pro", layout="centered")

def carregar_dados(arquivo):
    if not os.path.exists(arquivo): return []
    try:
        with open(arquivo, "r", encoding="utf-8") as f: return json.load(f)
    except: return []

def salvar_dados(arquivo, dados):
    with open(arquivo, "w", encoding="utf-8") as f: json.dump(dados, f, ensure_ascii=False, indent=4)

if 'pagina' not in st.session_state: st.session_state.pagina = "Início"

st.title("⚙️ Oficina Pro")

c1, c2, c3 = st.columns(3)
if c1.button("👤 Clientes", use_container_width=True): st.session_state.pagina = "Clientes"
if c2.button("🔧 Diagnóstico", use_container_width=True): st.session_state.pagina = "Diagnóstico"
if c3.button("📋 Histórico", use_container_width=True): st.session_state.pagina = "Histórico"
if st.button("➕ Novo Orçamento", use_container_width=True, type="primary"): st.session_state.pagina = "Orçamento"
st.divider()

if st.session_state.pagina == "Orçamento":
    st.header("💰 Novo Orçamento")
    lista_cli = carregar_dados("clientes.json")
    cliente = st.selectbox("Selecione o Cliente", [""] + [c['Nome'] for c in lista_cli])
    
    with st.form("orc_form", clear_on_submit=True):
        tipo = st.radio("Tipo", ["Peça", "Serviço"], horizontal=True)
        peca = st.text_input("Qual é o item?")
        detalhes = st.text_area("Detalhes (opcional)")
        c1, c2 = st.columns(2)
        unidade = c1.text_input("Unidade (un, kg, hora)")
        qtd = c2.number_input("Quantidade", min_value=1, value=1)
        st.markdown("---")
        st.subheader("Custo & Lucro")
        c_custo, c_margem = st.columns(2)
        custo_un = c_custo.number_input("Custo unitário (R$)", min_value=0.0)
        margem_pct = c_margem.number_input("Margem (%)", min_value=0.0)
        preco_venda = custo_un * (1 + (margem_pct / 100))
        st.write(f"**Sugestão de venda: R$ {preco_venda:.2f}**")
        venda_final = st.number_input("Preço de venda final (R$)", value=float(preco_venda), min_value=0.0)
        salvar_no_cat = st.checkbox("Salvar no meu catálogo")
        
        if st.form_submit_button("Adicionar ao pedido"):
            if cliente and peca:
                dados = carregar_dados("orcamentos.json")
                dados.append({
                    "Cliente": cliente, "Peça": peca, "Custo": custo_un, 
                    "Venda": venda_final, "Qtd": qtd, "Tipo": tipo
                })
                salvar_dados("orcamentos.json", dados)
                if salvar_no_cat:
                    cat = carregar_dados("catalogo.json")
                    cat.append({"Tipo": tipo, "Nome": peca, "Custo": custo_un, "Venda": venda_final})
                    salvar_dados("catalogo.json", cat)
                st.rerun()
            else: st.error("Preencha o cliente e o nome do item!")

    lista_orc = carregar_dados("orcamentos.json")
    if lista_orc: st.table(pd.DataFrame([i for i in lista_orc if i['Cliente'] == cliente]))

elif st.session_state.pagina != "Início":
    if st.button("⬅️ Voltar"): st.session_state.pagina = "Início"; st.rerun()
