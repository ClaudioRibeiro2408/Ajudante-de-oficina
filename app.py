import streamlit as st
import json
import os
import pandas as pd
import requests

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
    if not api_key:
        return "Erro: Chave API não configurada."
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={api_key}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"Erro na API ({response.status_code}): {response.text}"
    except Exception as e:
        return f"Erro de conexão: {str(e)}"

# --- INTERFACE ---
st.title("⚙️ Oficina Pro | Gestão e Diagnóstico IA")

aba1, aba2, aba3, aba4 = st.tabs(["👤 Clientes", "💰 Orçamento", "🔧 Diagnóstico", "📋 Histórico"])

# ABA 1: CLIENTES
with aba1:
    st.header("👤 Cadastro de Clientes")
    with st.form("form_cli", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome do Cliente")
            telefone = st.text_input("Telefone")
        with col2:
            marca = st.text_input("Marca do Veículo")
            modelo = st.text_input("Modelo")
            motor = st.text_input("Motorização")
            
        if st.form_submit_button("Salvar Cliente"):
            if nome and telefone:
                dados = carregar_json("clientes.json")
                dados.append({"Nome": nome, "Telefone": telefone, "Marca": marca, "Modelo": modelo, "Motor": motor})
                salvar_json("clientes.json", dados)
                st.success(f"Cliente {nome} salvo!")
            else:
                st.error("Nome e Telefone obrigatórios.")
    st.table(pd.DataFrame(carregar_json("clientes.json")))

# ABA 2: ORÇAMENTO
with aba2:
    st.header("💰 Orçamento Técnico")
    with st.form("form_orc", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            peca = st.text_input("Peça")
            valor_pago = st.number_input("Valor Pago (Custo) R$", min_value=0.0, format="%.2f")
            valor_venda = st.number_input("Valor de Venda R$", min_value=0.0, format="%.2f")
            qtd_medida = st.number_input("Quantidade (Unidade ou Litros)", min_value=0.0)
        with col2:
            eixo = st.selectbox("Eixo", ["Nenhum", "Dianteira", "Traseira"])
            lado = st.selectbox("Lado", ["Nenhum", "Direito", "Esquerdo"])
            horas = st
