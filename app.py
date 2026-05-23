import streamlit as st
import json
import os
import pandas as pd

# Configuração da página
st.set_page_config(page_title="Oficina Pro", layout="wide")

# Funções de Banco de Dados
def carregar_json(arquivo):
    if os.path.exists(arquivo):
        with open(arquivo, "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return []
    return []

def salvar_json(arquivo, dados):
    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

# Títulos e Abas
st.title("⚙️ Oficina Inteligente Pro")
aba_dash, aba_orc, aba_cli, aba_almox, aba_hist = st.tabs([
    "📈 Dashboard", "💰 Orçamentos", "🗂️ Clientes", "📦 Estoque", "📋 Histórico"
])

# --- ABA DASHBOARD ---
with aba_dash:
    st.subheader("📊 Indicadores de Performance")
    historico = carregar_json("historico_os.json")
    if historico:
        df = pd.DataFrame(historico)
        st.metric("Total de O.S. Registradas", len(df))
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Sem dados de histórico ainda.")

# --- ABA CLIENTES ---
with aba_cli:
    st.subheader("👤 Cadastro de Clientes")
    with st.form("form_cliente"):
        nome = st.text_input("Nome do Cliente")
        placa = st.text_input("Placa do Veículo")
        if st.form_submit_button("💾 Salvar Cliente"):
            clientes = carregar_json("clientes_veiculos.json")
            clientes.append({"nome": nome, "placa": placa})
            salvar_json("clientes_veiculos.json", clientes)
            st.success("Cliente salvo!")
    
    clientes = carregar_json("clientes_veiculos.json")
    if clientes:
        st.dataframe(pd.DataFrame(clientes), use_container_width=True)

# --- ABA ESTOQUE ---
with aba_almox:
    st.subheader("📦 Almoxarifado")
    with st.form("add_estoque"):
        desc = st.text_input("Nome da Peça")
        preco = st.number_input("Preço", value=0.0)
        qtd = st.number_input("Quantidade Inicial", value=10)
        if st.form_submit_button("Cadastrar Item"):
            cat = carregar_json("catalogo_itens.json")
            cat.append({"descricao": desc, "preco": preco, "estoque": qtd})
            salvar_json("catalogo_itens.json", cat)
            st.rerun()
    
    cat = carregar_json("catalogo_itens.json")
    if cat:
        st.dataframe(pd.DataFrame(cat), use_container_width=True)

with aba_orc:
    st.write("Aba de orçamentos em manutenção para otimização.")
with aba_hist:
    st.write("Aba de histórico em manutenção para otimização.")
