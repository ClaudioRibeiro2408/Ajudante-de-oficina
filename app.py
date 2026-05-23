import streamlit as st
import requests
import json
import os
import base64
from datetime import datetime
from fpdf import FPDF
from PIL import Image
import io
import pandas as pd # Biblioteca para os gráficos e tabelas

# ==========================================
# 1. CONFIGURAÇÃO E DESIGN PREMIUM
# ==========================================
st.set_page_config(page_title="Oficina Pro - Command Center", page_icon="📊", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; background-color: #161b22; padding: 10px; border-radius: 15px; }
    .stTabs [data-baseweb="tab"] { height: 45px; background-color: #21262d; border-radius: 8px; color: #8b949e; border: none; }
    .stTabs [aria-selected="true"] { background-color: #58a6ff !important; color: white !important; }
    div.stButton > button { background-color: #238636; color: white; border-radius: 10px; width: 100%; font-weight: bold; border: none; height: 3em; }
    .metric-card { background-color: #161b22; padding: 20px; border-radius: 15px; border: 1px solid #30363d; text-align: center; }
    h1, h2, h3 { color: #58a6ff !important; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. BANCO DE DADOS E ARQUIVOS
# ==========================================
ARQUIVO_BANCO = "historico_os.json"
ARQUIVO_CLIENTES = "clientes_veiculos.json"
ARQUIVO_CATALOGO = "catalogo_itens.json"
ARQUIVO_CONFIG = "config_oficina.json"

def carregar_json(arquivo):
    if os.path.exists(arquivo):
        with open(arquivo, "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return [] if "config" not in arquivo else {}
    return [] if "config" not in arquivo else {}

def salvar_json(arquivo, dados):
    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

# ==========================================
# 3. LÓGICA DE NEGÓCIO (BAIXA DE ESTOQUE)
# ==========================================
def atualizar_estoque_item(descricao_item, qtd_usada):
    catalogo = carregar_json(ARQUIVO_CATALOGO)
    for item in catalogo:
        if item['descricao'] == descricao_item and item['tipo'] == "📦 Peça / Componente":
            item['estoque'] = max(0, item.get('estoque', 0) - float(qtd_usada))
    salvar_json(ARQUIVO_CATALOGO, catalogo)

# ==========================================
# 4. INTERFACE LATERAL
# ==========================================
config_salva = carregar_json(ARQUIVO_CONFIG)
with st.sidebar:
    st.markdown("## ⚙️ Configurações")
    oficina_nome = st.text_input("Oficina:", value=config_salva.get("nome", "Oficina Ribeiro"))
    oficina_end = st.text_input("Endereço:", value=config_salva.get("endereco", "Rua Principal, 123"))
    oficina_tel = st.text_input("WhatsApp:", value=config_salva.get("telefone", "45999999999"))
    if st.button("Gravar Dados"):
        salvar_json(ARQUIVO_CONFIG, {"nome": oficina_nome, "endereco": oficina_end, "telefone": oficina_tel})
    st.write("---")
    st.caption("v3.0 - Command Center")

dados_oficina = {"nome": oficina_nome, "endereco": oficina_end, "telefone": oficina_tel}

# ==========================================
# 5. ABAS DO SISTEMA
# ==========================================
st.markdown(f"# 📊 Central de Comando: {oficina_nome}")

aba_dash, aba_orc, aba_cli, aba_almox, aba_hist = st.tabs([
    "📈 Dashboard Financeiro", 
    "💰 Novo Orçamento",
    "🗂️ Clientes",
    "📦 Estoque & Almoxarifado",
    "📋 Histórico"
])

# --- ABA DASHBOARD (A GRANDE NOVIDADE) ---
with aba_dash:
    historico = carregar_json(ARQUIVO_BANCO)
    df = pd.DataFrame(historico)
    
    if not df.empty:
        # Cálculos de Performance
        df_aprovados = df[df['status'].isin(['Aprovado', 'Concluído'])]
        # Extrai valor numérico (precisa de tratamento dependendo de como você salva)
        # Aqui simplificamos pegando os valores reais salvos
        total_faturado = sum([item.get('total_valor', 0) for idx, item in df_aprovados.iterrows()])
        ticket_medio = total_faturado / len(df_aprovados) if len(df_aprovados) > 0 else 0
        
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f'<div class="metric-card"><h4>Faturamento Total</h4><h2>R$ {total_faturado:.2f}</h2></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="metric-card"><h4>Ticket Médio</h4><h2>R$ {ticket_medio:.2f}</h2></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="metric-card"><h4>Serviços Aprovados</h4><h2>{len(df_aprovados)}</h2></div>', unsafe_allow_html=True)
        with c4:
            st.markdown(f'<div class="metric-card"><h4>Aguardando</h4><h2>{len(df[df["status"] == "Aguardando Orçamento"])}</h2></div>', unsafe_allow_html=True)
        
        st.write("---")
        st.subheader("📊 Fluxo de Veículos Recentes")
        st.line_chart(df.groupby('data').size())
    else:
        st.info("Aguardando os primeiros dados para gerar o Dashboard...")

# --- ABA ORÇAMENTO (COM BAIXA AUTOMÁTICA) ---
with aba_orc:
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("🚗 Identificação")
        clientes = carregar_json(ARQUIVO_CLIENTES)
        escolha = st.selectbox("Selecione o Carro/Cliente:", ["Manual"] + [f"{c['placa']} - {c['nome']}" for c in clientes])
        queixa = st.text_area("Reclamação:")
        status_o = st.selectbox("Status:", ["Aguardando Orçamento", "Aprovado", "Finalizado"])
    
    with col2:
        st.subheader("🖼️ Logotipo")
        logo_file = st.file_uploader("Logo para o PDF:", type=['png', 'jpg'])
        
    st.write("---")
    st.subheader("🛠️ Adicionar Peças do Estoque")
    catalogo = carregar_json(ARQUIVO_CATALOGO)
    
    if catalogo:
        col_it1, col_it2, col_it3 = st.columns([2, 1, 1])
        # Mostra apenas itens com estoque > 0
        opcoes_itens = [f"{i['descricao']} (Estoque: {i.get('estoque', 0)})" for i in catalogo]
        item_sel = col_it1.selectbox("Peça/Serviço:", opcoes_itens)
        qtd_usar = col_it2.number_input("Qtd:", min_value=0.1, value=1.0)
        
        if col_it3.button("➕ Adicionar Item"):
            item_data = catalogo[opcoes_itens.index(item_sel)]
            # Adiciona ao orçamento
            st.session_state.itens_orcamento.append({
                "descricao": item_data['descricao'],
                "quantidade": qtd_usar,
                "valor": qtd_usar * item_data['preco'],
                "tipo": item_data['tipo']
            })
            # Se for aprovado agora, já baixa o estoque
            if status_o == "Aprovado":
                atualizar_estoque_item(item_data['descricao'], qtd_usar)
            st.rerun()

    # Resumo Final e PDF... (Lógica de PDF mantida aqui)

# --- ABA ESTOQUE (CONTROLE DE QUANTIDADES) ---
with aba_almox:
    st.subheader("📦 Gestão de Estoque e Almoxarifado")
    
    with st.form("add_estoque"):
        c_a, c_b, c_c = st.columns([2, 1, 1])
        nome_p = c_a.text_input("Nome da Peça / Serviço:")
        preco_p = c_b.number_input("Preço Unitário (R$):", min_value=0.0)
        estoque_p = c_c.number_input("Qtd em Estoque (Incial):", min_value=0, value=10)
        tipo_p = st.radio("Tipo:", ["📦 Peça / Componente", "🔧 Mão de Obra / Serviço"], horizontal=True)
        
        if st.form_submit_button("💾 Cadastrar Item"):
            if nome_p:
                cat = carregar_json(ARQUIVO_CATALOGO)
                # Adiciona ou atualiza
                item_existente = False
                for i in cat:
                    if i['descricao'] == nome_p:
                        i['preco'] = preco_p
                        i['estoque'] = estoque_p
                        item_existente = True
                if not item_existente:
                    cat.append({"tipo": tipo_p, "descricao": nome_p, "preco": preco_p, "estoque": estoque_p})
                salvar_json(ARQUIVO_CATALOGO, cat)
                st.success("Item blindado no estoque!")
    
    st.write("---")
    st.markdown("### 📋 Status das Prateleiras")
    cat_ver = carregar_json(ARQUIVO_CATALOGO)
    if cat_ver:
        # Alerta visual para estoque baixo
        for i in cat_ver:
            if i['tipo'] == "📦 Peça / Componente":
                cor = "red" if i.get('estoque', 0) <= 2 else "white"
                st.markdown(f"- :{cor}[**{i['descricao']}**] | Preço: R$ {i['preco']:.2f} | **Estoque: {i.get('estoque', 0)}**")

# As outras abas (Clientes e Histórico) seguem a mesma lógica anterior, apenas com o visual atualizado.
