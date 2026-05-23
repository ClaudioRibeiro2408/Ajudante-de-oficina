import streamlit as st
import requests
import json
import os
import base64
from datetime import datetime

# Configuração premium da página
st.set_page_config(
    page_title="Oficina Inteligente - Gestão Total", 
    page_icon="🚀",
    layout="centered"
)

# Nome do arquivo de banco de dados
ARQUIVO_BANCO = "historico_os.json"

# Inicializa a lista de itens do orçamento na memória do navegador
if "itens_orcamento" not in st.session_state:
    st.session_state.itens_orcamento = []

# Funções de Banco de Dados
def carregar_historico():
    if os.path.exists(ARQUIVO_BANCO):
        with open(ARQUIVO_BANCO, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return []
    return []

def salvar_no_historico(cliente, veiculo, placa, tipo, relato, resultado):
    historico = carregar_historico()
    nova_entrada = {
        "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "cliente": cliente,
        "veiculo": veiculo,
        "placa": placa.upper().strip(),
        "tipo": tipo,
        "relato": relato,
        "resultado": resultado
    }
    historico.append(nova_entrada)
    with open(ARQUIVO_BANCO, "w", encoding="utf-8") as f:
        json.dump(historico, f, ensure_ascii=False, indent=4)

# Título Principal
st.title("🚀 Oficina Inteligente")
st.write("---")

# Definição das 3 Abas
aba_patio, aba_orcamento, aba_historico = st.tabs([
    "🔧 Diagnóstico Técnico", 
    "💰 Gerar Orçamento", 
    "🗂️ Histórico de Veículos"
])

# Chave da API
api_key = os.environ.get("GEMINI_API_KEY")

# Função de IA Multimodal
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
    else:
        return f"Erro na API (Status {response.status_code})"

# ==========================================
# ABA 1: DIAGNÓSTICO E ENGENHARIA
# ==========================================
with aba_patio:
    st.subheader("🔧 Diagnóstico de Alta Performance")
    c1, c2, c3 = st.columns([2, 2, 1])
    cli_p = c1.text_input("Cliente:", key="cli_p")
    veh_p = c2.text_input("Veículo:", key="veh_p")
    plc_p = c3.text_input("Placa:", key="plc_p").upper()

    prompt_p = st.text_area("Descreva o sintoma ou peça o esquema elétrico/ajuste de osciloscópio:")
    midia_p = st.file_uploader("Envie Foto/Vídeo/Áudio do defeito:", type=["png","jpg","jpeg","mp4","mov","avi","mp3","wav","m4a"])

    if st.button("Executar Análise de Engenharia", use_container_width=True):
        if not api_key:
            st.error("API Key ausente.")
        else:
            with st.spinner("🚀 Consultando Engenharia de Fábrica..."):
                diretriz = "Você é Engenheiro-Chefe. Dê diagnóstico, esquema elétrico e parametrização de osciloscópio (Tempo/Tensão/Conexão). Títulos: ### 📋 Dados, ### ⚡ Análise, ### 🛠️ Elétrica, ### 🔬 Osciloscópio, ### 💡 Diagnóstico."
                res = chamar_gemini(f"{diretriz}\nCarro:{veh_p}\nRelato:{prompt_p}", midia_p)
                st.markdown(res)
                if plc_p:
                    salvar_no_historico(cli_p, veh_p, plc_p, "🔧 Diagnóstico", prompt_p, res)

# ==========================================
# ABA 2: ORÇAMENTO COMERCIAL DINÂMICO
# ==========================================
with aba_orcamento:
    st.subheader("💰 Construtor de Orçamento Avançado")
    
    # Identificação básica do atendimento
    c1, c2, c3 = st.columns([2, 2, 1])
    cli_o = c1.text_input("Cliente:", key="cli_o")
    veh_o = c2.text_input("Veículo:", key="veh_o")
    plc_o = c3.text_input("Placa:", key="plc_o").upper()

    st.write("---")
    
    # Menu seletor para o tipo de entrada
    tipo_insercao = st.radio("Selecione o tipo de item para adicionar:", ["📦 Peça / Componente", "🔧 Mão de Obra / Serviço"], horizontal=True)
    
    if tipo_insercao == "📦 Peça / Componente":
        col_p1, col_p2, col_p3 = st.columns([2, 1, 1])
        nome_item = col_p1.text_input("Nome da Peça:", placeholder="Ex: Amortecedor, Óleo 5W40, Pastilha...")
        qtd = col_p2.number_input("Quantidade:", min_value=0.1, value=1.0, step=0.5)
        unidade = col_p3.selectbox("Unidade:", ["Unidade(s)", "Litro(s)"])
        
        col_p4, col_p5, col_p6 = st.columns([1, 1, 1])
        lado = col_p4.selectbox("Lado (Se aplicável):", ["Não se aplica", "Lado Direito (LD)", "Lado Esquerdo (LE)", "Ambos os Lados"])
        posicao = col_p5.selectbox("Posição (Se aplicável):", ["Não se aplica", "Dianteiro", "Traseiro"])
        preco_unit = col_p6.number_input("Preço Unitário (R$):", min_value=0.0, value=0.0, step=10.0)
        
        if st.button("➕ Adicionar Peça ao Orçamento", use_container_width=True):
            if nome_item:
                detalhe_posicao = ""
                if lado != "Não se aplica": detalhe_posicao += f" - {lado}"
                if posicao != "Não se aplica": detalhe_posicao += f" {posicao}"
                
                valor_total_item = qtd * preco_unit
                item_formatado = {
                    "tipo": "Peça",
                    "descricao": f"{nome_item}{detalhe_posicao}",
                    "quantidade": f"{qtd} {unidade}",
                    "valor": valor_total_item
                }
                st.session_state.itens_orcamento.append(item_formatado)
                st.success(f"'{nome_item}' adicionado!")
            else:
                st.error("Digite o nome da peça.")

    else:
        col_m1, col_m2, col_m3 = st.columns([2, 1, 1])
        nome_servico = col_m1.text_input("Descrição do Serviço:", placeholder="Ex: Substituição de Amortecedores, Diagnóstico Avançado...")
        horas_trab = col_m2.number_input("Horas de Mão de Obra (Fracionável):", min_value=0.1, value=1.0, step=0.1, help="Ex: 1.5 significa 1 hora e 30 minutos")
        valor_hora = col_m3.number_input("Valor da Hora Técnica (R$):", min_value=0.0, value=150.0, step=10.0)
        
        if st.button("➕ Adicionar Serviço ao Orçamento", use_container_width=True):
            if nome_servico:
                valor_total_servico = horas_trab * valor_hora
                item_formatado = {
                    "tipo": "Mão de Obra",
                    "descricao": nome_servico,
                    "quantidade": f"{horas_trab} h",
                    "valor": valor_total_servico
                }
                st.session_state.itens_orcamento.append(item_formatado)
                st.success(f"Serviço '{nome_servico}' adicionado!")
            else:
                st.error("Digite a descrição do serviço.")

    st.write("---")
    st.subheader("📋 Itens Adicionados na O.S. Atual")
    
    # Exibe a lista parcial na tela para o mecânico acompanhar
    total_acumulado = 0.0
    if st.session_state.itens_orcamento:
        for idx, item in enumerate(st.session_state.itens_orcamento):
            c_desc, c_qtd, c_val, c_del = st.columns([3, 1, 1, 0.5])
            c_desc.write(f"**{item['tipo']}:** {item['descricao']}")
            c_qtd.write(f"Qtd: {item['quantidade']}")
            c_val.write(f"R$ {item['valor']:.2f}")
            if c_del.button("❌", key=f"del_{idx}"):
                st.session_state.itens_orcamento.pop(idx)
                st.rerun()
            total_acumulado += item["valor"]
            
        st.write(f"#### 💰 Total Parcial Calculado: **R$ {total_acumulado:.2f}**")
    else:
        st.info("Nenhum item adicionado ainda.")

    # Botão para limpar a lista atual
    if st.session_state.itens_orcamento and st.button("🗑️ Limpar Todo o Orçamento", type="secondary"):
        st.session_state.itens_orcamento = []
        st.rerun()

    st.write("---")
    
    # Envio e processamento final da IA
    if st.button("🚀 Gerar Texto de Orçamento Premium para WhatsApp", use_container_width=True):
        if not api_key:
            st.error("API Key ausente.")
        elif not st.session_state.itens_orcamento:
            st.error("Adicione pelo menos um item antes de gerar o orçamento final.")
        else:
            with st.spinner("✍️ Convertendo a lista técnica em texto de alto padrão de vendas..."):
                # Transforma a lista estruturada em texto legível para passar para a IA
                texto_itens_para_ia = ""
                for item in st.session_state.itens_orcamento:
                    texto_itens_para_ia += f"- {item['tipo']}: {item['descricao']} | Qtd: {item['quantidade']} | Valor calculado: R$ {item['valor']:.2f}\n"
                
                contexto_o = f"""
                Você é o Diretor Comercial de uma oficina de alto desempenho. Sua missão é estruturar uma mensagem impecável de orçamento para enviar no WhatsApp do cliente.
                
                DIRETRIZES DA MENSAGEM:
                1. Comece com uma saudação formal, educada e limpa para o cliente.
                2. Apresente os itens (Peças e Serviços) de forma extremamente organizada, mantendo os lados (Direito/Esquerdo) e posições (Dianteiro/Traseiro) informados, bem como as frações de horas trabalhadas de forma amigável.
                3. Adicione uma breve explicação profissional sobre o porquê de usar componentes novos e os riscos de não efetuar o reparo sugerido.
                4. Exiba o TOTAL GERAL que deve bater exatamente com o valor calculado pelo sistema.
                5. Termine informando os prazos de garantia padrão da oficina e se colocando à disposição.
                
                DADOS DO ATENDIMENTO:
                Cliente: {cli_o}
                Veículo: {veh_o}
                Lista de Itens Calculados:\n{texto_itens_para_ia}
                VALOR TOTAL DO SISTEMA: R$ {total_acumulado:.2f}
                """
                res_o = chamar_gemini(contexto_o)
                st.success("Orçamento Final Formatado com Sucesso!")
                st.markdown(res_o)
                st.balloons()
                
                if plc_o:
                    salvar_no_historico(cli_o, veh_o, plc_o, "💰 Orçamento", texto_itens_para_ia, res_o)

# ==========================================
# ABA 3: HISTÓRICO DE VEÍCULOS
# ==========================================
with aba_historico:
    st.subheader("🗂️ Consulta de Histórico")
    busca = st.text_input("🔍 Digite a Placa:", key="busca_plc").upper().strip()
    historico = carregar_historico()
    
    if busca:
        resultados = [i for i in historico if i["placa"] == busca]
        if resultados:
            for item in reversed(resultados):
                with st.expander(f"📅 {item['data']} - {item['tipo']} ({item['veiculo']})"):
                    st.write(f"**Cliente:** {item['cliente']}")
                    st.markdown(item['resultado'])
        else:
            st.warning("Nenhum registro para esta placa.")
    elif historico:
        st.write("Últimos 5 atendimentos gerais no pátio:")
        for item in list(reversed(historico))[:5]:
            with st.expander(f"📅 {item['data']} - Placa: {item['placa']} - {item['veiculo']} ({item['tipo']})"):
                st.write(f"**Cliente:** {item['cliente']}")
                st.markdown(item['resultado'])
