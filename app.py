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

# Agora temos 4 abas novamente, mas a segunda é 'Orçamento'
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

# ABA 2: ORÇAMENTO (Substituindo o Estoque)
with aba2:
    st.header("💰 Gerador de Orçamentos")
    with st.form("form_orc", clear_on_submit=True):
        cliente_orc = st.text_input("Nome do Cliente")
        servico = st.text_area("Descrição dos Serviços")
        valor = st.number_input("Valor Total (R$)", min_value=0.0, format="%.2f")
        
        if st.form_submit_button("Salvar Orçamento"):
            dados = carregar_json("orcamentos.json")
            dados.append({"Cliente": cliente_orc, "Serviço": servico, "Valor": valor})
            salvar_json("orcamentos.json", dados)
            st.success("Orçamento salvo com sucesso!")
            
    st.subheader("Histórico de Orçamentos")
    st.table(pd.DataFrame(carregar_json("orcamentos.json")))

# ABA 3: DIAGNÓSTICO
with aba3:
    st.header("🔧 Diagnóstico Técnico IA")
    veiculo = st.text_input("Veículo/Modelo")
    problema = st.text_area("Sintoma ou falha")
    if st.button("Buscar Diagnóstico"):
        if veiculo and problema:
            resultado = chamar_gemini(f"Diagnóstico para {veiculo}: {problema}")
            st.markdown("### 💡 Resultado:")
            st.write(resultado)

# ABA 4: HISTÓRICO
with aba4:
    st.header("📋 Histórico Geral")
    st.info("Sistema ativo e operante.")
