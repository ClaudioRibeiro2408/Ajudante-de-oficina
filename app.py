import streamlit as st
import json
import os
import pandas as pd
import requests
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import date

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

# --- PDF PROFISSIONAL ---
def gerar_pdf(cliente_info, itens, obs, data):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    # Cabeçalho Oficina
    p.setFont("Helvetica-Bold", 18)
    p.drawString(100, 750, "OFICINA PRO - ORÇAMENTO")
    p.setFont("Helvetica", 10)
    p.drawString(100, 735, "Rua do Mecânico, 123 - Foz do Iguaçu - PR")
    p.drawString(100, 720, "Contato: (45) 99999-9999")
    p.line(100, 710, 500, 710)
    
    # Dados Cliente
    p.setFont("Helvetica-Bold", 12)
    p.drawString(100, 690, f"Data: {data}")
    p.drawString(100, 675, f"Cliente: {cliente_info['Nome']}")
    p.drawString(100, 660, f"Telefone: {cliente_info['Telefone']}")
    p.drawString(100, 645, f"Veículo: {cliente_info['Marca']} {cliente_info['Modelo']} | Placa: {cliente_info['Placa']}")
    p.line(100, 635, 500, 635)
    
    # Itens
    y = 615
    p.setFont("Helvetica-Bold", 12)
    p.drawString(100, y, "Descrição do Serviço/Peça")
    p.drawString(400, y, "Valor")
    y -= 20
    p.setFont("Helvetica", 12)
    total = 0
    for item in itens:
        p.drawString(100, y, f"- {item['Peça']}")
        p.drawString(400, y, f"R$ {item['Venda']:.2f}")
        total += item['Venda']
        y -= 20
    
    p.line(100, y, 500, y)
    p.setFont("Helvetica-Bold", 12)
    p.drawString(330, y-20, f"TOTAL: R$ {total:.2f}")
    
    # Observações
    p.setFont("Helvetica-Oblique", 10)
    p.drawString(100, y-60, f"Observações: {obs}")
    
    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer

# --- NAVEGAÇÃO E LÓGICA (Simplificada para manter a estrutura) ---
if 'pagina' not in st.session_state: st.session_state.pagina = "Início"

st.title("⚙️ Oficina Pro")

# [MANTIVE A ESTRUTURA DE BOTÕES QUE DEFINIMOS]
c1, c2, c3 = st.columns(3)
with c1:
    if st.button("👤 Clientes", use_container_width=True): st.session_state.pagina = "Clientes"
with c2:
    if st.button("🔧 Diagnóstico", use_container_width=True): st.session_state.pagina = "Diagnóstico"
with c3:
    if st.button("📋 Histórico", use_container_width=True): st.session_state.pagina = "Histórico"

if st.button("➕ Criar novo orçamento", use_container_width=True, type="primary"): st.session_state.pagina = "Orçamento"

st.divider()

# --- PÁGINA ORÇAMENTO COM CAMPOS COMPLETOS ---
if st.session_state.pagina == "Orçamento":
    st.header("💰 Novo Orçamento")
    lista_cli = carregar_dados("clientes.json")
    nomes = [c['Nome'] for c in lista_cli]
    cliente_nome = st.selectbox("Selecione o Cliente", [""] + nomes)
    
    cliente_data = next((c for c in lista_cli if c['Nome'] == cliente_nome), None)
    
    if cliente_data:
        st.write(f"**Veículo:** {cliente_data['Marca']} {cliente_data['Modelo']} | **Placa:** {cliente_data['Placa']}")
        
        with st.form("orc_form", clear_on_submit=True):
            peca = st.text_input("Peça ou Serviço")
            venda = st.number_input("Valor R$", min_value=0.0)
            obs = st.text_area("Observações/Garantia")
            if st.form_submit_button("Adicionar"):
                dados = carregar_dados("orcamentos.json")
                dados.append({"Cliente": cliente_nome, "Peça": peca, "Venda": venda, "Obs": obs})
                salvar_dados("orcamentos.json", dados)
                st.rerun()

        itens = [i for i in carregar_dados("orcamentos.json") if i['Cliente'] == cliente_nome]
        if itens:
            st.table(pd.DataFrame(itens)[["Peça", "Venda"]])
            total = sum(i['Venda'] for i in itens)
            st.subheader(f"Total: R$ {total:.2f}")
            
            # PDF com data atual
            data_atual = date.today().strftime("%d/%m/%Y")
            pdf = gerar_pdf(cliente_data, itens, itens[0]['Obs'], data_atual)
            st.download_button("📥 Baixar PDF do Orçamento", data=pdf, file_name=f"Orcamento_{cliente_nome}.pdf")

# (Aqui você mantém as outras partes: Clientes, Diagnóstico, Histórico que já funcionavam)
# ...
