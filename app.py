import streamlit as st
import json
import os
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

st.set_page_config(page_title="Oficina Pro", layout="centered")

def carregar_dados(arquivo):
    if not os.path.exists(arquivo): return []
    try:
        with open(arquivo, "r", encoding="utf-8") as f: return json.load(f)
    except: return []

def salvar_dados(arquivo, dados):
    with open(arquivo, "w", encoding="utf-8") as f: json.dump(dados, f, ensure_ascii=False, indent=4)

def gerar_pdf(c_info, s_itens, p_itens, t_s, t_p, t_g):
    buf = BytesIO()
    p = canvas.Canvas(buf, pagesize=letter)
    p.setFont("Helvetica-Bold", 14)
    p.drawString(100, 750, "Performance Serviços Automotivos")
    p.setFont("Helvetica", 9)
    p.drawString(100, 738, "CNPJ: 64.242.276/0001-69 | Foz do Iguaçu-PR")
    p.line(100, 730, 500, 730)
    p.setFont("Helvetica-Bold", 12)
    p.drawString(100, 710, "Orçamento")
    p.setFont("Helvetica", 10)
    p.drawString(100, 695, f"Cliente: {c_info.get('Nome', '')}")
    p.setFont("Helvetica-Bold", 10)
    p.drawString(100, 670, "Serviços:")
    y = 655
    for s in s_itens:
        p.drawString(100, y, f"{s.get('Peça', '')} - R$ {s.get('Venda', 0):.2f}")
        y -= 15
    p.drawString(100, y-10, f"Total Serviços: R$ {t_s:.2f}")
    p.drawString(100, y-30, f"Total Peças: R$ {t_p:.2f}")
    p.drawString(100, y-50, f"TOTAL GERAL: R$ {t_g:.2f}")
    p.showPage()
    p.save()
    buf.seek(0)
    return buf

if 'pagina' not in st.session_state: st.session_state.pagina = "Início"

st.title("⚙️ Oficina Pro")
c1, c2, c3 = st.columns(3)
if c1.button("👤 Clientes"): st.session_state.pagina = "Clientes"
if c2.button("🔧 Diagnóstico"): st.session_state.pagina = "Diagnóstico"
if c3.button("📋 Histórico"): st.session_state.pagina = "Histórico"
if st.button("➕ Novo Orçamento", type="primary"): st.session_state.pagina = "Orçamento"
st.divider()

if st.session_state.pagina == "Orçamento":
    st.header("💰 Orçamento")
    cli = carregar_dados("clientes.json")
    n = st.selectbox("Cliente", [""] + [c['Nome'] for c in cli])
    c_d = next((c for c in cli if c['Nome'] == n), {})
    with st.form("f", clear_on_submit=True):
        t = st.radio("Tipo", ["Serviço", "Peça"], horizontal=True)
        d = st.text_input("Descrição")
        v = st.number_input("Valor R$", min_value=0.0)
        if st.form_submit_button("Adicionar"):
            db = carregar_dados("orcamentos.json")
            db.append({"Cliente": n, "Peça": d, "Venda": v, "Tipo": t})
            salvar_dados("orcamentos.json", db); st.rerun()
    it = [i for i in carregar_dados("orcamentos.json") if i['Cliente'] == n]
    if it:
        st.table(pd.DataFrame(it))
        s = [i for i in it if i['Tipo'] == "Serviço"]
        p = [i for i in it if i['Tipo'] == "Peça"]
        ts, tp = sum(i['Venda'] for i in s), sum(i['Venda'] for i in p)
        pdf = gerar_pdf(c_d, s, p, ts, tp, ts + tp)
        st.download_button("📥 Baixar PDF", pdf, "orcamento.pdf")

elif st.session_state.pagina != "Início":
    if st.button("⬅️ Voltar"): st.session_state.pagina = "Início"; st.rerun()
