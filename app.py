import streamlit as st
import json
import os
import pandas as pd
import requests
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import datetime

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
    if not api_key: return "Erro: API Key não encontrada."
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={api_key}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(url, json=payload)
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    except: return "Erro ao processar diagnóstico."

# --- FUNÇÃO PARA GERAR O PDF PROFISSIONAL ---
def gerar_pdf(dados_orcamento):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    largura, altura = letter

    # Cabeçalho
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, altura - 50, "ORÇAMENTO TÉCNICO - OFICINA PRO")
    p.setFont("Helvetica", 10)
    p.drawString(50, altura - 65, f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    p.line(50, altura - 75, largura - 50, altura - 75)

    # Títulos da Tabela no PDF
    p.setFont("Helvetica-Bold", 11)
    p.drawString(50, altura - 100, "Descrição da Peça/Serviço")
    p.drawString(300, altura - 100, "Qtd")
    p.drawString(350, altura - 100, "Posição")
    p.drawString(450, altura - 100, "M. Obra")
    p.drawString(520, altura - 100, "V. Unit")

    # Itens
    y = altura - 120
    total_geral = 0
    p.setFont("Helvetica", 10)
    
    for item in dados_orcamento:
        p.drawString(50, y, str(item['Peça'])[:40])
        p.drawString(300, y, str(item['Qtd']))
        p.drawString(350, y, f"{item['Eixo']} {item['Lado']}")
        p.drawString(450, y, f"R$ {item['Mão de Obra']:.2f}")
        p.drawString(520, y, f"R$ {item['Venda']:.2f}")
        
        total_item = (item['Venda'] * item['Qtd']) + item['Mão de Obra']
        total_geral += total_item
        y -= 20
        if y < 50: # Nova página se ficar muito longo
            p.showPage()
            y = altura - 50

    # Total Final
    p.line(50, y - 10, largura - 50, y - 10)
    p.setFont("Helvetica-Bold", 12)
    p.drawString(350, y - 30, f"TOTAL DO ORÇAMENTO: R$ {total_geral:.2f}")

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer

# --- INTERFACE ---
st.title("⚙️ Oficina Pro | Gestão e Diagnóstico IA")
aba1, aba2, aba3, aba4 = st.tabs(["👤 Clientes", "💰 Orçamento", "🔧 Diagnóstico", "📋 Histórico"])

# ABA 1: CLIENTES (MANTIDA)
with aba1:
    st.header("👤 Cadastro de Clientes")
    with st.form("form_cli", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            nome = st.text_input("Nome do Cliente")
            telefone = st.text_input("Telefone")
        with c2:
            marca = st.text_input("Marca")
            modelo = st.text_input("Modelo")
            motor = st.text_input("Motor")
        if st.form_submit_button("Salvar Cliente"):
            dados = carregar_json("clientes.json")
            dados.append({"Nome": nome, "Telefone": telefone, "Marca": marca, "Modelo": modelo, "Motor": motor})
            salvar_json("clientes.json", dados)
            st.success("Cliente Salvo!")
    st.table(pd.DataFrame(carregar_json("clientes.json")))

# ABA 2: ORÇAMENTO (TODA NOVA)
with aba2:
    st.header("💰 Orçamento e PDF")
    
    # Formulário de entrada
    with st.form("form_orc", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            peca = st.text_input("Peça ou Serviço")
            v_pago = st.number_input("Custo (Interno) R$", min_value=0.0)
            v_venda = st.number_input("Venda (Para Cliente) R$", min_value=0.0)
            qtd = st.number_input("Qtd/Litros", min_value=0.1, value=1.0)
        with col2:
            eixo = st.selectbox("Eixo", ["Nenhum", "Dianteira", "Traseira"])
            lado = st.selectbox("Lado", ["Nenhum", "Direito", "Esquerdo"])
            horas_mo = st.number_input("Mão de Obra (Horas)", min_value=0.0)
            v_hora = st.number_input("Valor da Hora R$", value=100.0)
        
        if st.form_submit_button("Adicionar Item"):
            lucro = v_venda - v_pago
            total_mo = horas_mo * v_hora
            dados = carregar_json("orcamentos.json")
            dados.append({
                "Peça": peca, "Custo": v_pago, "Venda": v_venda, 
                "Qtd": qtd, "Eixo": eixo, "Lado": lado, "Mão de Obra": total_mo
            })
            salvar_json("orcamentos.json", dados)
            st.rerun()

    # Visualização e PDF
    lista_orc = carregar_json("orcamentos.json")
    if lista_orc:
        df = pd.DataFrame(lista_orc)
        st.subheader("Itens Lançados")
        # Na tela você vê tudo, incluindo o custo
        st.dataframe(df)
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("Limpar Orçamento"):
                salvar_json("orcamentos.json", [])
                st.rerun()
        with col_btn2:
            # Gerar PDF
            pdf_file = gerar_pdf(lista_orc)
            st.download_button(
                label="📥 Baixar Orçamento em PDF",
                data=pdf_file,
                file_name=f"Orcamento_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf"
            )

# ABA 3 e 4 (MANTIDAS)
with aba3:
    st.header("🔧 Diagnóstico IA")
    v = st.text_input("Veículo")
    p = st.text_area("Problema")
    if st.button("Analisar"):
        st.write(chamar_gemini(f"Diagnóstico para {v}: {p}"))

with aba4:
    st.header("📋 Histórico")
    st.write("Sistema pronto.")
