import streamlit as st
import requests
import json
import os
import base64
from datetime import datetime
from fpdf import FPDF
from PIL import Image
import io

# Configuração premium da página
st.set_page_config(
    page_title="Oficina Inteligente - Gestão Total", 
    page_icon="🚀",
    layout="centered"
)

# Nomes dos arquivos de banco de dados
ARQUIVO_BANCO = "historico_os.json"
ARQUIVO_CLIENTES = "clientes_veiculos.json"
ARQUIVO_CATALOGO = "catalogo_itens.json"
ARQUIVO_CONFIG = "config_oficina.json"

# Inicializa a lista de itens do orçamento na memória do navegador
if "itens_orcamento" not in st.session_state:
    st.session_state.itens_orcamento = []

# ==========================================
# FUNÇÕES DE BANCO DE DADOS (JSON)
# ==========================================
def carregar_json(arquivo):
    if os.path.exists(arquivo):
        with open(arquivo, "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return [] if "config" not in arquivo else {}
    return [] if "config" not in arquivo else {}

def salvar_json(arquivo, dados):
    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

def salvar_no_historico(cliente, veiculo, placa, tipo, relato, resultado, status="N/A"):
    historico = carregar_json(ARQUIVO_BANCO)
    nova_entrada = {
        "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "cliente": cliente,
        "veiculo": veiculo,
        "placa": placa.upper().strip(),
        "tipo": tipo,
        "relato": relato,
        "resultado": resultado,
        "status": status
    }
    historico.append(nova_entrada)
    salvar_json(ARQUIVO_BANCO, historico)

def salvar_cliente(nome, telefone, placa, marca, modelo, ano, motorizacao):
    clientes = carregar_json(ARQUIVO_CLIENTES)
    clientes = [c for c in clientes if c["placa"] != placa.upper().strip()]
    novo_cadastro = {
        "nome": nome.strip(), "telefone": telefone.strip(), "placa": placa.upper().strip(),
        "marca": marca.strip(), "modelo": modelo.strip(), "ano": ano.strip(), "motorizacao": motorizacao.strip()
    }
    clientes.append(novo_cadastro)
    salvar_json(ARQUIVO_CLIENTES, clientes)

def salvar_no_catalogo(tipo, descricao, preco_unitario):
    catalogo = carregar_json(ARQUIVO_CATALOGO)
    catalogo = [i for i in catalogo if i["descricao"].lower() != descricao.strip().lower()]
    novo_item = {
        "tipo": tipo,
        "descricao": descricao.strip(),
        "preco": float(preco_unitario)
    }
    catalogo.append(novo_item)
    salvar_json(ARQUIVO_CATALOGO, catalogo)

# ==========================================
# FUNÇÃO GERADORA DE PDF
# ==========================================
def generar_pdf_orcamento(dados_oficina, cliente, veiculo, placa, reclamacao, itens, total, bytes_logo=None):
    pdf = FPDF()
    pdf.add_page()
    
    if bytes_logo is not None:
        try:
            img_temp = "temp_logo_pdf.png"
            image = Image.open(io.BytesIO(bytes_logo))
            image.save(img_temp)
            pdf.image(img_temp, x=85, y=10, w=40)
            pdf.ln(25)
            if os.path.exists(img_temp): os.remove(img_temp)
        except: pass
            
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, dados_oficina.get('nome', 'OFICINA').upper(), ln=True, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, f"Endereço: {dados_oficina.get('endereco', '')}", ln=True, align="C")
    pdf.cell(0, 6, f"Telefone: {dados_oficina.get('telefone', '')}", ln=True, align="C")
    pdf.ln(10)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "DADOS DO ATENDIMENTO / ORÇAMENTO", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(95, 6, f"Cliente: {cliente}", ln=False)
    pdf.cell(95, 6, f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True)
    pdf.cell(95, 6, f"Veículo: {veiculo}", ln=False)
    pdf.cell(95, 6, f"Placa: {placa.upper()}", ln=True)
    pdf.ln(4)
    
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, "Reclamação Relatada pelo Cliente:", ln=True)
    pdf.set_font("Helvetica", "I", 10)
    pdf.multi_cell(0, 5, reclamacao if reclamacao else "Não informada.")
    pdf.ln(6)
    
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(110, 8, "Descrição do Item / Serviço", border=1, ln=False)
    pdf.cell(40, 8, "Quantidade", border=1, ln=False, align="C")
    pdf.cell(40, 8, "Total (R$)", border=1, ln=True, align="R")
    
    pdf.set_font("Helvetica", "", 10)
    for item in itens:
        pdf.cell(110, 7, item['descricao'], border=1, ln=False)
        pdf.cell(40, 7, item['quantidade'], border=1, ln=False, align="C")
        pdf.cell(40, 7, f"{item['valor']:.2f}", border=1, ln=True, align="R")
        
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(150, 8, "VALOR TOTAL DO ORÇAMENTO:", ln=False, align="R")
    pdf.cell(40, 8, f"R$ {total:.2f}", ln=True, align="R")
    
    return pdf.output()

# Título Principal
st.title("🚀 Oficina Inteligente")
st.write("---")

# CONFIGURAÇÕES DA OFICINA SALVAS EM BANCO DE DADOS
config_salva = carregar_json(ARQUIVO_CONFIG)
st.sidebar.markdown("### 🏢 Identidade da Oficina")
oficina_nome = st.sidebar.text_input("Nome da Oficina:", value=config_salva.get("nome", "Ribeiro & Claudio Automotiva"))
oficina_end = st.sidebar.text_input("Endereço:", value=config_salva.get("endereco", "Rua Principal, 123"))
oficina_tel = st.sidebar.text_input("Telefone/WhatsApp:", value=config_salva.get("telefone", "(45) 99999-9999"))

if st.sidebar.button("💾 Salvar Dados da Oficina"):
    salvar_json(ARQUIVO_CONFIG, {"nome": oficina_nome, "endereco": oficina_end, "telefone": oficina_tel})
    st.sidebar.success("Dados da oficina gravados permanentemente!")

dados_oficina = {"nome": oficina_nome, "endereco": oficina_end, "telefone": oficina_tel}

# Definição das 5 Abas do Sistema
aba_patio, aba_orcamento, aba_clientes, aba_catalogo, aba_historico = st.tabs([
    "🔧 Pátio & Diagnóstico", 
    "💰 Gerar Orçamento",
    "🗂️ Clientes & Veículos",
    "📦 Almoxarifado & Serviços",
    "📊 Histórico Geral"
])

api_key = os.environ.get("GEMINI_API_KEY")

def chamar_gemini(contexto_prompt, midia=None):
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={api_key}"
    parts = []
    if midia:
        bytes_arquivo = midia.read()
        base64_arquivo = base64.b64encode(bytes_arquivo).decode('utf-8')
        parts.append({"inlineData": {"mimeType": midia.type, "data": base64_arquivo}})
        midia.seek(0)
    parts.append({"text": contexto_prompt})
    payload = {"contents": [{"parts": parts}]}
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200: return response.json()['candidates'][0]['content']['parts'][0]['text']
    else: return f"Erro na API (Status {response.status_code})"

# ==========================================
# ABA 1: DIAGNÓSTICO E ENGENHARIA
# ==========================================
with aba_patio:
    st.subheader("🔧 Diagnóstico de Alta Performance")
    lista_cadastrados = carregar_json(ARQUIVO_CLIENTES)
    modo_p = st.radio("Identificação do Veículo no Pátio:", ["Buscar Cliente Cadastrado", "Digitar Manualmente"], horizontal=True, key="modo_p")
    
    cli_p, veh_p, plc_p = "", "", ""
    if modo_p == "Buscar Cliente Cadastrado" and lista_cadastrados:
        opcoes_placa = [f"{c['placa']} - {c['nome']} ({c['modelo']})" for c in lista_cadastrados]
        selecionado = st.selectbox("Selecione o Veículo:", opcoes_placa, key="sel_p")
        dados_c = lista_cadastrados[opcoes_placa.index(selecionado)]
        cli_p = dados_c["nome"]
        veh_p = f"{dados_c['marca']} {dados_c['modelo']} {dados_c['motorizacao']} {dados_c['ano']}"
        plc_p = dados_c["placa"]
        st.info(f"🚗 **Selecionado:** {veh_p} | **Cliente:** {cli_p}")
    else:
        if modo_p == "Buscar Cliente Cadastrado": st.warning("Nenhum cliente cadastrado ainda.")
        c1, c2, c3 = st.columns([2, 2, 1])
        cli_p = c1.text_input("Cliente:", key="cli_p_man")
        veh_p = c2.text_input("Veículo (Marca/Mod/Motor):", key="veh_p_man")
        plc_p = c3.text_input("Placa:", key="plc_p_man").upper()

    st.write("---")
    prompt_p = st.text_area("Descreva o sintoma ou peça o esquema elétrico/ajuste de osciloscópio:")
    midia_p = st.file_uploader("Envie Foto/Vídeo/Áudio do defeito:", type=["png","jpg","jpeg","mp4","mov","avi","mp3","wav","m4a"])

    if st.button("Executar Análise de Engenharia", use_container_width=True):
        if not api_key: st.error("API Key ausente.")
        else:
            with st.spinner("🚀 Consultando Engenharia..."):
                diretriz = "Você é Engenheiro-Chefe especialista. Dê diagnóstico técnico, esquema elétrico e parametrização de osciloscópio."
                res = chamar_gemini(f"{diretriz}\nCarro:{veh_p}\nRelato:{prompt_p}", midia_p)
                st.markdown(res)
                if plc_p: salvar_no_historico(cli_p, veh_p, plc_p, "🔧 Diagnóstico", prompt_p, res)

# ==========================================
# ABA 2: ORÇAMENTO COMERCIAL E LOGO DINÂMICA
# ==========================================
with aba_orcamento:
    st.markdown("### 🖼️ Logotipo do Orçamento")
    arquivo_logo = st.file_uploader("Selecione a imagem da logo da oficina para este documento:", type=["png", "jpg", "jpeg"])
    logo_para_pdf = None
    
    if arquivo_logo is not None:
        logo_bytes = arquivo_logo.read()
        logo_para_pdf = logo_bytes
        col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
        with col_l2: st.image(logo_bytes, use_container_width=True)
    else:
        st.markdown(f'<div style="background-color: #f0f2f6; padding: 15px; border-radius: 10px; text-align: center; border: 2px dashed #b3b3cc; margin-bottom: 20px;"><h3 style="color: #1e1e2f; margin: 0;">{oficina_nome.upper()}</h3></div>', unsafe_allow_html=True)

    st.markdown("### 🚗 Dados do Atendimento")
    lista_cadastrados = carregar_json(ARQUIVO_CLIENTES)
    modo_o = st.radio("Como preencher os dados do veículo:", ["Buscar Cliente Cadastrado", "Digitar Manualmente"], horizontal=True, key="modo_o")
    
    cli_o, veh_o, plc_o = "", "", ""
    if modo_o == "Buscar Cliente Cadastrado" and lista_cadastrados:
        opcoes_placa = [f"{c['placa']} - {c['nome']} ({c['modelo']})" for c in lista_cadastrados]
        selecionado_o = st.selectbox("Selecione o Veículo pela Placa:", opcoes_placa, key="sel_o")
        dados_co = lista_cadastrados[opcoes_placa.index(selecionado_o)]
        cli_o = dados_co["nome"]
        veh_o = f"{dados_co['marca']} {dados_co['modelo']} {dados_co['motorizacao']} {dados_co['ano']}"
        plc_o = dados_co["placa"]
        st.success(f"🔗 **Vinculado:** {veh_o} | **Cliente:** {cli_o}")
    else:
        if modo_o == "Buscar Cliente Cadastrado": st.warning("Nenhum cliente no banco de dados.")
        c1, c2, c3 = st.columns([2, 2, 1])
        cli_o = c1.text_input("Cliente:", key="cli_o_man")
        veh_o = c2.text_input("Veículo (Marca/Modelo/Motor):", key="veh_o_man")
        plc_o = c3.text_input("Placa:", key="plc_o_man").upper()
    
    st.write("---")
    reclamacao_cliente = st.text_area("📋 Reclamação/Sintoma relatado pelo Cliente na Entrada:")
    status_atual = st.selectbox("📊 Status Inicial:", ["Aguardando Orçamento", "Aprovado", "Cancelado", "Aguardando Peças", "Concluído"])

    st.write("---")
    st.markdown("### 🛠️ Inserção de Itens do Banco de Dados")
    
    catalogo_completo = carregar_json(ARQUIVO_CATALOGO)
    tipo_insercao = st.radio("Selecione o tipo de item para adicionar:", ["📦 Peça / Componente", "🔧 Mão de Obra / Serviço"], horizontal=True)
    
    itens_filtrados = [i for i in catalogo_completo if i["tipo"] == tipo_insercao]
    
    if itens_filtrados:
        opcoes_itens = [f"{i['descricao']} - (R$ {i['preco']:.2f})" for i in itens_filtrados]
        item_selecionado_db = st.selectbox(f"Selecione um(a) {tipo_insercao} cadastrado(a):", opcoes_itens)
        item_dados = itens_filtrados[opcoes_itens.index(item_selecionado_db)]
        
        col_f1, col_f2 = st.columns(2)
        qtd_db = col_f1.number_input("Quantidade / Horas:", min_value=0.1, value=1.0, step=0.5, key="qtd_db")
        preco_final_db = col_f2.number_input("Preço Unitário Confirmado (R$):", min_value=0.0, value=item_dados["preco"], step=10.0)
        
        if st.button(f"➕ Adicionar {tipo_insercao} ao Orçamento", use_container_width=True):
            unid = "Litro(s)" if "óleo" in item_dados["descricao"].lower() else "Unidade(s)" if tipo_insercao == "📦 Peça / Componente" else "h"
            item_formatado = {
                "tipo": "Peça" if "Peça" in tipo_insercao else "Mão de Obra",
                "descricao": item_dados["descricao"],
                "quantidade": f"{qtd_db} {unid}",
                "valor": qtd_db * preco_final_db
            }
            st.session_state.itens_orcamento.append(item_formatado)
            st.success(f"'{item_dados['descricao']}' adicionado!")
            st.rerun()
    else:
        st.info(f"Nenhum(a) {tipo_insercao} cadastrado no Almoxarifado ainda. Vá na aba 'Almoxarifado & Serviços' para alimentar o banco de dados.")

    st.write("---")
    st.subheader("📋 Resumo do Orçamento Atual")
    total_acumulado = 0.0
    if st.session_state.itens_orcamento:
        for idx, item in enumerate(st.session_state.itens_orcamento):
            c_desc, c_qtd, c_val, c_del = st.columns([3, 1, 1, 0.5])
            c_desc.write(f"**{item['tipo']}:** {item['descricao']}")
            c_qtd.write(f"{item.get('quantidade', '1')}")
            c_val.write(f"R$ {item['valor']:.2f}")
            if c_del.button("❌", key=f"del_{idx}"):
                st.session_state.itens_orcamento.pop(idx)
                st.rerun()
            total_acumulado += item["valor"]
        st.write(f"#### 💰 Total Geral Calculado: **R$ {total_acumulado:.2f}**")
    else: st.info("Nenhum item adicionado ao orçamento.")

    if st.session_state.itens_orcamento and st.button("🗑️ Limpar Orçamento", type="secondary"):
        st.session_state.itens_orcamento = []
        st.rerun()

    st.write("---")
    if st.session_state.itens_orcamento:
        col_pdf, col_wa = st.columns(2)
        with col_pdf:
            bytes_pdf = generar_pdf_orcamento(dados_oficina, cli_o, veh_o, plc_o, reclamacao_cliente, st.session_state.itens_orcamento, total_acumulado, logo_para_pdf)
            st.download_button(label="📥 Baixar Orçamento em PDF", data=bytes_pdf, file_name=f"Orcamento_{plc_o}.pdf", mime="application/pdf", use_container_width=True)
        with col_wa:
            if st.button("🚀 Formatar Texto de Venda (WhatsApp)", use_container_width=True):
                texto_itens = "".join([f"- {i['tipo']}: {i['descricao']} ({i.get('quantidade', '1')}) -> R$ {i['valor']:.2f}\n" for i in st.session_state.itens_orcamento])
                contexto_o = f"Você é Diretor Comercial de oficina mecânica. Formate uma mensagem excelente para o cliente {cli_o} sobre o veículo {veh_o}. Itens:\n{texto_itens}\nTotal: R$ {total_acumulado:.2f}"
                res_o = chamar_gemini(contexto_o)
                st.markdown(res_o)
                if plc_o: salvar_no_historico(cli_o, veh_o, plc_o, "💰 Orçamento", reclamacao_cliente, res_o, status_atual)

# ==========================================
# ABA 3: CADASTRO DE CLIENTES E VEÍCULOS
# ==========================================
with aba_clientes:
    st.subheader("🗂️ Cadastro Central de Clientes e Veículos")
    with st.form("form_cadastro_cliente", clear_on_submit=True):
        st.markdown("#### 👤 Dados do Proprietário")
        c_nome = st.text_input("Nome Completo do Cliente:")
        c_tel = st.text_input("Telefone/WhatsApp:")
        st.markdown("#### 🚗 Dados do Veículo")
        cc1, cc2, cc3 = st.columns([1, 2, 1])
        c_placa = cc1.text_input("Placa do Veículo:").upper().strip()
        c_marca = cc2.text_input("Marca (Ex: Volkswagen, Chevrolet):")
        c_modelo = cc3.text_input("Modelo (Ex: Golf, Up):")
        cc4, cc5 = st.columns(2)
        c_motor = cc4.text_input("Motorização (Ex: 1.0 TSI, 1.4 TSI):")
        c_ano = cc5.text_input("Ano (Ex: 2019/2020):")
        
        if st.form_submit_button("💾 Salvar Cadastro no Banco de Dados", use_container_width=True):
            if c_nome and c_placa and c_modelo:
                salvar_cliente(c_nome, c_tel, c_placa, c_marca, c_modelo, c_ano, c_motor)
                st.success(f"✅ Cliente '{c_nome}' cadastrado com sucesso!")
            else: st.error("Preencha Nome, Placa e Modelo.")

    st.write("---")
    st.markdown("#### 🔍 Clientes Cadastrados no Banco")
    banco_clientes = carregar_json(ARQUIVO_CLIENTES)
    if banco_clientes:
        for c in reversed(banco_clientes):
            with st.expander(f"🚗 {c['placa']} - {c['nome']} ({c['modelo']})"):
                st.write(f"**Telefone:** {c['telefone']} | **Motor:** {c['motorizacao']} | **Ano:** {c['ano']}")
    else: st.info("Nenhum cliente registrado.")

# ==========================================
# ABA 4: ALMOXARIFADO & SERVIÇOS (BANCO DE DADOS DE ITENS)
# ==========================================
with aba_catalogo:
    st.subheader("📦 Banco de Dados de Peças & Serviços")
    st.write("Cadastre aqui os itens que você mais usa na oficina para não ter que digitar os preços todas as vezes.")
    
    with st.form("form_catalogo", clear_on_submit=True):
        tipo_cat = st.radio("Tipo de Item:", ["📦 Peça / Componente", "🔧 Mão de Obra / Serviço"], horizontal=True)
        desc_cat = st.text_input("Descrição do Item / Nome do Serviço:", placeholder="Ex: Óleo 5W40 VW 508.88 ou Diagnóstico Eletrônico Integrado")
        val_cat = st.number_input("Preço de Venda / Valor do Serviço Padrão (R$):", min_value=0.0, value=0.0, step=10.0)
        
        if st.form_submit_button("💾 Gravar no Almoxarifado"):
            if desc_cat:
                salvar_no_catalogo(tipo_cat, desc_cat, val_cat)
                st.success(f"✅ '{desc_cat}' foi blindado no seu banco de dados!")
            else: st.error("Digite uma descrição para o item.")

    st.write("---")
    st.markdown("#### 🔍 Itens na Memória do Sistema")
    banco_itens = carregar_json(ARQUIVO_CATALOGO)
    if banco_itens:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**📦 Peças Cadastradas:**")
            for i in [x for x in banco_itens if x["tipo"] == "📦 Peça / Componente"]:
                st.text(f"• {i['descricao']} - R$ {i['preco']:.2f}")
        with col2:
            st.markdown("**🔧 Serviços Cadastrados:**")
            for i in [x for x in banco_itens if x["tipo"] == "🔧 Mão de Obra / Serviço"]:
                st.text(f"• {i['descricao']} - R$ {i['preco']:.2f}")
    else: st.info("Nenhum item cadastrado no almoxarifado ainda.")

# ==========================================
# ABA 5: HISTÓRICO GERAL
# ==========================================
with aba_historico:
    st.subheader("📊 Consulta de Histórico & Status das O.S.")
    busca = st.text_input("🔍 Digite a Placa para buscar:", key="busca_plc").upper().strip()
    historico = carregar_json(ARQUIVO_BANCO)
    
    if busca:
        resultados = [i for i in historico if i["placa"] == busca]
        if resultados:
            for item in reversed(resultados):
                with st.expander(f"📅 {item['data']} - [{item.get('status', 'N/A')}] {item['tipo']} ({item['veiculo']})"):
                    st.write(f"**Cliente:** {item['cliente']} | **Queixa:** {item['relato']}")
                    st.markdown(item['resultado'])
        else: st.warning("Nenhum registro para esta placa.")
    elif historico:
        for item in list(reversed(historico))[:5]:
            with st.expander(f"📅 {item['data']} - Placa: {item['placa']} - {item['veiculo']}"):
                st.markdown(item['resultado'])
