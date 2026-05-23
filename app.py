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
    
    # URL CORRETA baseada na sua lista de modelos disponíveis
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

aba1, aba2, aba3, aba4 = st.tabs(["👤 Clientes", "📦 Estoque", "🔧 Diagnóstico Técnico", "📋 Histórico"])

# ABA 1: CLIENTES
with aba1:
    st.header("👤 Cadastro de Clientes")
    
    with st.form("form_cli", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome do Cliente")
            telefone = st.text_input("Telefone")
        with col2:
            marca = st.text_input("Marca")
            modelo = st.text_input("Modelo do Veículo")
            motor = st.text_input("Motorização")
            
        if st.form_submit_button("Salvar Cliente"):
            if nome and telefone:
                # Carrega o histórico atual
                dados = carregar_json("clientes.json")
                # Adiciona o novo cliente
                novo_cliente = {
                    "Nome": nome,
                    "Telefone": telefone,
                    "Marca": marca,
                    "Modelo": modelo,
                    "Motor": motor
                }
                dados.append(novo_cliente)
                # Salva
                salvar_json("clientes.json", dados)
                st.success(f"Cliente {nome} salvo com sucesso!")
            else:
                st.error("Nome e Telefone são obrigatórios.")

    st.subheader("Clientes Cadastrados")
    lista_clientes = carregar_json("clientes.json")
    if lista_clientes:
        st.table(pd.DataFrame(lista_clientes))
    else:
        st.info("Nenhum cliente cadastrado ainda.")

with aba2:
    st.header("Almoxarifado")
    with st.form("form_estoque"):
        item = st.text_input("Nome da Peça")
        preco = st.number_input("Preço R$", value=0.0)
        if st.form_submit_button("Salvar Peça"):
            dados = carregar_json("estoque.json")
            dados.append({"Peça": item, "Preço": preco})
            salvar_json("estoque.json", dados)
            st.rerun()
    st.table(pd.DataFrame(carregar_json("estoque.json")))

with aba3:
    st.header("🔧 Diagnóstico Técnico Inteligente")
    veiculo = st.text_input("Veículo/Modelo")
    problema = st.text_area("Descreva o sintoma ou falha")
    
    if st.button("Buscar Diagnóstico IA"):
        if veiculo and problema:
            with st.spinner("Analisando com Gemini 3.5..."):
                prompt = f"O mecânico está diagnosticando um {veiculo}. O problema é: {problema}. Liste 3 causas prováveis e testes técnicos."
                resultado = chamar_gemini(prompt)
                st.markdown("### 💡 Resultado da Análise:")
                st.write(resultado)
        else:
            st.error("Preencha veículo e problema.")

with aba4:
    st.header("📋 Histórico Geral")
    st.info("Sistema ativo.")
