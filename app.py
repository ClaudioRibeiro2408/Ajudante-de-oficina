import streamlit as st
import requests
import json
import os
import base64
from datetime import datetime
from fpdf import FPDF

# Configuração premium da página
st.set_page_config(
    page_title="Oficina Inteligente - Gestão Total", 
    page_icon="🚀",
    layout="centered"
)

# Nomes dos arquivos de banco de dados
ARQUIVO_BANCO = "historico_os.json"
ARQUIVO_CLIENTES = "clientes_veiculos.json"

# Inicializa a lista de itens do orçamento na memória do navegador
if "itens_orcamento" not in st.session_state:
    st.session_state.itens_orcamento = []

# ==========================================
# FUNÇÕES DE BANCO DE DADOS (JSON)
# ==========================================
def carregar_historico():
    if os.path.exists(ARQUIVO_BANCO):
        with open(ARQUIVO_BANCO, "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return []
    return []

def salvar_no_historico(cliente, veiculo, placa, tipo, relato, resultado, status="N/A"):
    historico = carregar_historico()
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
    with open(ARQUIVO_BANCO, "w", encoding="utf-8") as f:
        json.dump(historico, f, ensure_ascii=False, indent=4)

def carregar_clientes():
    if os.path.exists(ARQUIVO_CLIENTES):
        with open(ARQUIVO_CLIENTES, "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return []
    return []

def salvar_cliente(nome, telefone, placa, marca, modelo, ano, motorizacao):
    clientes = carregar_clientes()
    # Verifica se a placa já existe para não duplicar, se existir substitui os dados
    clientes = [c for c in clientes if c["placa"] != placa.upper().strip()]
    
    novo_cadastro = {
        "nome": nome.strip(),
        "telefone": telefone.strip(),
        "placa": placa.upper().strip(),
        "marca": marca.strip(),
        "modelo": modelo.strip(),
        "ano": ano.strip(),
        "motorizacao": motorizacao.strip()
    }
    clientes.append(novo_cadastro)
    with open(ARQUIVO_CLIENTES, "w", encoding="utf-8") as f:
        json.dump(clientes, f, ensure_ascii=False, indent=4)

# ==========================================
# FUNÇÃO GERADORA DE PDF
# ==========================================
def generar_pdf_orcamento(dados_oficina, cliente, veiculo, placa, reclamacao, itens, total):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    
    # Cabeçalho da Oficina
    pdf.cell(0, 10, dados_oficina['nome'].upper(), ln=True, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, f"Endereço: {dados_oficina['endereco']}", ln=True, align="C")
    pdf.cell(0, 6, f"Telefone: {dados_oficina['telefone']}", ln=True, align="C")
    pdf.ln(10)
    
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    
    # Dados do Atendimento
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "DADOS DO ATENDIMENTO / ORÇAMENTO", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(95, 6, f"Cliente: {cliente}", ln=False)
    pdf.cell(95, 6, f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True)
    pdf.cell(95, 6, f"Veículo: {veiculo}", ln=False)
    pdf.cell(95, 6, f"Placa: {placa.upper()}", ln=True)
    pdf.ln(4)
    
    # Reclamação
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, "Reclamação Relatada pelo Cliente:", ln=True)
    pdf.set_font("Helvetica", "I", 10)
    pdf.multi_cell(0, 5, reclamacao if reclamacao else "Não informada.")
    pdf.ln(6)
    
    # Tabela
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

# Definição das 4 Abas do Sistema
aba_patio, aba_orcamento, aba_clientes, aba_historico = st.tabs([
    "🔧 Diagnóstico Técnico", 
    "💰 Gerar Orçamento",
    "🗂️ Clientes & Carros",
    "📊 Histórico & Status"
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
    if response.status_code == 200:
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    else: return f"Erro na API (Status {response.status_code})"

# ==========================================
# ABA 1: DIAGNÓSTICO E ENGENHARIA
# ==========================================
with aba_patio:
    st.subheader("🔧 Diagnóstico de Alta Performance")
    
    lista_cadastrados = carregar_clientes()
    modo_p = st.radio("Identificação do Veículo no Pátio:", ["Buscar Cliente Cadastrado", "Digitar Manualmente"], horizontal=True, key="modo_p")
    
    cli_p, veh_p, plc_p = "", "", ""
    
    if modo_p == "Buscar Cliente Cadastrado" and lista_cadastrados:
        opcoes_placa = [f"{c['placa']} - {c['nome']} ({c['modelo']})" for c in lista_cadastrados]
        selecionado = st.selectbox("Selecione o Veículo:", opcoes_placa, key="sel_p")
        idx = opcoes_placa.index(selecionado)
        dados_c = lista_cadastrados[idx]
        cli_p = dados_c["nome"]
        veh_p = f"{dados_c['marca']} {dados_c['modelo']} {dados_c['motorizacao']} {dados_c['ano']}"
        plc_p = dados_c["placa"]
        st.info(f"🚗 **Selecionado:** {veh_p} | **Cliente:** {cli_p}")
    else:
        if modo_p == "Buscar Cliente Cadastrado":
            st.warning("Nenhum cliente cadastrado ainda. Digite manualmente abaixo.")
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
# ABA 2: ORÇAMENTO COMERCIAL E LINK DINÂMICO
# ==========================================
with aba_orcamento:
    st.subheader("💰 Construtor de Orçamento Profissional")
    
    st.markdown("### 🏢 Dados do Emitente")
    col_of1, col_of2, col_of3 = st.columns([2, 2, 1.5])
    oficina_nome = col_of1.text_input("Nome da Oficina:", value="Oficina Mecânica")
    oficina_end = col_of2.text_input("Endereço:", value="Rua Principal, 123")
    oficina_tel = col_of3.text_input("Telefone:", value="(45) 99999-9999")
    dados_oficina = {"nome": oficina_nome, "endereco": oficina_end, "telefone": oficina_tel}

    st.write("---")
    st.markdown("### 🚗 Dados do Atendimento & Vínculo")
    
    lista_cadastrados = carregar_clientes()
    modo_o = st.radio("Como preencher os dados do veículo:", ["Buscar Cliente Cadastrado", "Digitar Manualmente"], horizontal=True, key="modo_o")
    
    cli_o, veh_o, plc_o = "", "", ""
    
    if modo_o == "Buscar Cliente Cadastrado" and lista_cadastrados:
        opcoes_placa = [f"{c['placa']} - {c['nome']} ({c['modelo']})" for c in lista_cadastrados]
        selecionado_o = st.selectbox("Selecione o Veículo pela Placa:", opcoes_placa, key="sel_o")
        idx_o = opcoes_placa.index(selecionado_o)
        dados_co = lista_cadastrados[idx_o]
        cli_o = dados_co["nome"]
        veh_o = f"{dados_co['marca']} {dados_co['modelo']} {dados_co['motorizacao']} {dados_co['ano']}"
        plc_o = dados_co["placa"]
        st.success(f"🔗 **Dados Vinculados com Sucesso!** Carro: {veh_o} | Cliente: {cli_o}")
    else:
        if modo_o == "Buscar Cliente Cadastrado":
            st.warning("Nenhum cliente no banco de dados. Digite manualmente abaixo.")
        c1, c2, c3 = st.columns([2, 2, 1])
        cli_o = c1.text_input("Cliente:", key="cli_o_man")
        veh_o = c2.text_input("Veículo (Marca/Modelo/Motor):", key="veh_o_man")
        plc_o = c3.text_input("Placa:", key="plc_o_man").upper()
    
    st.write("---")
    reclamacao_cliente = st.text_area("📋 Reclamação/Sintoma relatado pelo Cliente na Entrada:", placeholder="Ex: Barulho na suspensão ao passar em irregularidades.")
    status_atual = st.selectbox("📊 Status Inicial do Orçamento:", ["Aguardando Orçamento", "Aprovado", "Cancelado", "Aguardando Peças", "Concluído"])

    st.write("---")
    tipo_insercao = st.radio("Selecione o tipo de item para adicionar:", ["📦 Peça / Componente", "🔧 Mão de Obra / Serviço"], horizontal=True)
    
    if tipo_insercao == "📦 Peça / Componente":
        col_p1, col_p2, col_p3 = st.columns([2, 1, 1])
        nome_item = col_p1.text_input("Nome da Peça:")
        qtd = col_p2.number_input("Quantidade:", min_value=0.1, value=1.0, step=0.5)
        unidade = col_p3.selectbox("Unidade:", ["Unidade(s)", "Litro(s)"])
        
        col_p4, col_p5, col_p6 = st.columns([1, 1, 1])
        lado = col_p4.selectbox("Lado:", ["Não se aplica", "Lado Direito (LD)", "Lado Esquerdo (LE)", "Ambos os Lados"])
        posicao = col_p5.selectbox("Posição:", ["Não se aplica", "Dianteiro", "Traseiro"])
        preco_unit = col_p6.number_input("Preço Unitário (R$):", min_value=0.0, value=0.0, step=10.0)
        
        if st.button("➕ Adicionar Peça", use_container_width=True):
            if nome_item:
                detalhe_posicao = ""
                if lado != "Não se aplica": detalhe_posicao += f" - {lado}"
                if posicao != "Não se aplica": detalhe_posicao += f" {posicao}"
                item_formatado = {"tipo": "Peça", "descricao": f"{nome_item}{detalhe_posicao}", "quantidade": f"{qtd} {unidade}", "valor": qtd * preco_unit}
                st.session_state.itens_orcamento.append(item_formatado)
                st.success(f"'{nome_item}' adicionado!")
                st.rerun()

    else:
        col_m1, col_m2, col_m3 = st.columns([2, 1, 1])
        nome_servico = col_m1.text_input("Descrição do Serviço:")
        horas_trab = col_m2.number_input("Horas de Mão de Obra:", min_value=0.1, value=1.0, step=0.1)
        valor_hora = col_m3.number_input("Valor da Hora Técnica (R$):", min_value=0.0, value=150.0, step=10.0)
        
        if st.button("➕ Adicionar Serviço", use_container_width=True):
            if nome_servico:
                item_formatado = {"tipo": "Mão de Obra", "descricao": nome_servico, "quantidade": f"{horas_trab} h", "valor": horas_trab * valor_hora}
                st.session_state.itens_orcamento.append(item_formatado)
                st.success("Serviço adicionado!")
                st.rerun()

    st.write("---")
    st.subheader("📋 Resumo da Ordem de Serviço")
    
    total_acumulado = 0.0
    if st.session_state.itens_orcamento:
        for idx, item in enumerate(st.session_state.itens_orcamento):
            c_desc, c_qtd, c_val, c_del = st.columns([3, 1, 1, 0.5])
            c_desc.write(f"**{item['tipo']}:** {item['descricao']}")
            c_qtd.write(f"{item['quantidade']}")
            c_val.write(f"R$ {item['valor']:.2f}")
            if c_del.button("❌", key=f"del_{idx}"):
                st.session_state.itens_orcamento.pop(idx)
                st.rerun()
            total_acumulado += item["valor"]
            
        st.write(f"#### 💰 Total Geral Calculado: **R$ {total_acumulado:.2f}**")
    else: st.info("Nenhum item adicionado.")

    if st.session_state.itens_orcamento and st.button("🗑️ Limpar Tudo", type="secondary"):
        st.session_state.itens_orcamento = []
        st.rerun()

    st.write("---")
    
    if st.session_state.itens_orcamento:
        col_pdf, col_wa = st.columns(2)
        
        with col_pdf:
            bytes_pdf = generar_pdf_orcamento(dados_oficina, cli_o, veh_o, plc_o, reclamacao_cliente, st.session_state.itens_orcamento, total_acumulado)
            st.download_button(
                label="📥 Baixar Orçamento em PDF",
                data=bytes_pdf,
                file_name=f"Orcamento_{plc_o if plc_o else 'SemPlaca'}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
            
        with col_wa:
            if st.button("🚀 Formatar Texto de Venda (WhatsApp)", use_container_width=True):
                with st.spinner("Formatando..."):
                    texto_itens = "".join([f"- {i['tipo']}: {i['descricao']} ({i['quantidade']}) -> R$ {i['valor']:.2f}\n" for i in st.session_state.itens_orcamento])
                    contexto_o = f"Você é Diretor Comercial de oficina mecânica. Formate uma mensagem excelente para o cliente {cli_o} sobre o veículo {veh_o}. Queixa: {reclamacao_cliente}. Itens:\n{texto_itens}\nTotal: R$ {total_acumulado:.2f}"
                    res_o = chamar_gemini(contexto_o)
                    st.success("Texto pronto!")
                    st.markdown(res_o)
                    if plc_o: salvar_no_historico(cli_o, veh_o, plc_o, "💰 Orçamento", reclamacao_cliente, res_o, status_atual)

# ==========================================
# NOVA ABA 3: CADASTRO DE CLIENTES E VEÍCULOS
# ==========================================
with aba_clientes:
    st.subheader("🗂️ Cadastro Central de Clientes e Veículos")
    
    with st.form("form_cadastro_cliente", clear_on_submit=True):
        st.markdown("#### 👤 Dados do Proprietário")
        c_nome = st.text_input("Nome Completo do Cliente:")
        c_tel = st.text_input("Telefone/WhatsApp:")
        
        st.markdown("#### 🚗 Dados da Máquina")
        cc1, cc2, cc3 = st.columns([1, 2, 1])
        c_placa = cc1.text_input("Placa do Veículo:").upper().strip()
        c_marca = cc2.text_input("Marca (Ex: Volkswagen, Chevrolet):")
        c_modelo = cc3.text_input("Modelo (Ex: Golf, Onix, Up):")
        
        cc4, cc5 = st.columns(2)
        c_motor = cc4.text_input("Motorização (Ex: 1.0 TSI, 1.4 TSI, 1.6 MSI):")
        c_ano = cc5.text_input("Ano de Fabricação/Modelo (Ex: 2018/2019):")
        
        btn_cadastrar = st.form_submit_button("💾 Salvar Cadastro no Banco de Dados", use_container_width=True)
        
        if btn_cadastrar:
            if c_nome and c_placa and c_modelo:
                salvar_cliente(c_nome, c_tel, c_placa, c_marca, c_modelo, c_ano, c_motor)
                st.success(f"✅ Sucesso! Cliente '{c_nome}' e veículo de placa '{c_placa}' foram blindados no sistema!")
            else:
                st.error("Por favor, preencha pelo menos os campos essenciais: Nome, Placa e Modelo.")

    st.write("---")
    st.markdown("#### 🔍 Lista de Clientes e Frotas Cadastradas")
    banco_clientes = carregar_clientes()
    if banco_clientes:
        for c in reversed(banco_clientes):
            with st.expander(f"🚗 {c['placa']} - {c['nome']} ({c['modelo']})"):
                st.write(f"**Telefone:** {c['telefone']}")
                st.write(f"**Veículo:** {c['marca']} {c['modelo']} - Ano: {c['ano']}")
                st.write(f"**Motorização:** {c['motorizacao']}")
    else:
        st.info("Nenhum cliente registrado na base de dados.")

# ==========================================
# ABA 4: HISTÓRICO DE VEÍCULOS E STATUS
# ==========================================
with aba_historico:
    st.subheader("📊 Consulta de Histórico & Status das O.S.")
    busca = st.text_input("🔍 Digite a Placa para buscar:", key="busca_plc").upper().strip()
    historico = carregar_historico()
    
    if busca:
        resultados = [i for i in historico if i["placa"] == busca]
        if resultados:
            for item in reversed(resultados):
                badge_status = f"[{item.get('status', 'Orçamento')}]"
                with st.expander(f"📅 {item['data']} - {badge_status} {item['tipo']} ({item['veiculo']})"):
                    st.write(f"**Cliente:** {item['cliente']}")
                    st.write(f"**Queixa Registrada:** {item['relato']}")
                    st.write("**Resumo:**")
                    st.markdown(item['resultado'])
        else: st.warning("Nenhum registro para esta placa.")
    elif historico:
        st.write("Últimos atendimentos no pátio:")
        for item in list(reversed(historico))[:5]:
            badge_status = f"[{item.get('status', 'Orçamento')}]"
            with st.expander(f"📅 {item['data']} - Placa: {item['placa']} - {badge_status} {item['veiculo']}"):
                st.write(f"**Cliente:** {item['cliente']}")
                st.markdown(item['resultado'])
