import streamlit as st
import json
import os
import pandas as pd

# Configuração da Página
st.set_page_config(page_title="Oficina Pro - Gestão & Diagnóstico", layout="wide")

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

# Título do Sistema
st.title("⚙️ Oficina Pro | Gestão e Diagnóstico")

# Definição das Abas (Reincluindo o Diagnóstico Técnico)
aba1, aba2, aba3, aba4 = st.tabs(["👤 Clientes", "📦 Estoque", "🔧 Diagnóstico Técnico", "📋 Histórico"])

# ABA 1: CLIENTES
with aba1:
    st.header("Cadastro de Clientes")
    nome = st.text_input("Nome do Cliente", key="nome_cliente")
    placa = st.text_input("Placa do Veículo", key="placa_cliente")
    if st.button("Salvar Cliente"):
        dados = carregar_json("clientes.json")
        dados.append({"Nome": nome, "Placa": placa})
        salvar_json("clientes.json", dados)
        st.success("Cliente salvo!")
    st.table(pd.DataFrame(carregar_json("clientes.json")))

# ABA 2: ESTOQUE
with aba2:
    st.header("Almoxarifado")
    item = st.text_input("Nome da Peça", key="peca_nome")
    preco = st.number_input("Preço R$", value=0.0, key="peca_preco")
    if st.button("Salvar Peça"):
        dados = carregar_json("estoque.json")
        dados.append({"Peça": item, "Preço": preco})
        salvar_json("estoque.json", dados)
        st.success("Peça salva!")
    st.table(pd.DataFrame(carregar_json("estoque.json")))

# ABA 3: DIAGNÓSTICO TÉCNICO (O que tinha sumido)
with aba3:
    st.header("🔧 Diagnóstico Técnico")
    st.write("Insira os dados do veículo e o problema para a análise técnica.")
    
    veiculo_diag = st.text_input("Veículo/Modelo")
    problema_diag = st.text_area("Descrição da Falha ou Sintomas")
    
    if st.button("Executar Diagnóstico"):
        # Aqui ficará a lógica de análise do Gemini
        st.info(f"Analisando falha em {veiculo_diag}...")
        st.warning("Funcionalidade de diagnóstico integrada. Insira as observações técnicas.")
    
    # Campo para salvar o diagnóstico no histórico
    if st.button("Registrar no Histórico"):
        dados_diag = carregar_json("historico.json")
        dados_diag.append({"Veículo": veiculo_diag, "Problema": problema_diag, "Status": "Diagnosticado"})
        salvar_json("historico.json", dados_diag)
        st.success("Diagnóstico registrado no histórico!")

# ABA 4: HISTÓRICO
with aba4:
    st.header("📋 Histórico Geral")
    st.table(pd.DataFrame(carregar_json("historico.json")))
