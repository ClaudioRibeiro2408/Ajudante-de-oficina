import streamlit as st

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Oficina Pro", layout="centered")

# --- CABEÇALHO ---
st.title("⚙️ Oficina Pro")
st.write("Sistema de Diagnóstico Automotivo")

st.divider()

# --- MÓDULO DE DIAGNÓSTICO ---
st.subheader("🔧 Diagnóstico Rápido")

# Campos de entrada
veiculo = st.text_input("Qual o modelo do carro?")
queixa = st.text_area("Descreva o problema:")

# Botão de ação
if st.button("Gerar Análise"):
    if veiculo and queixa:
        # Normalização dos textos para análise
        q = queixa.lower()
        
        # Lógica de Diagnóstico Aprimorada
        if "freio" in q or "pastilha" in q or "disco" in q:
            resultado = f"No {veiculo}, o sistema de freios exige atenção imediata. Verifique desgaste de pastilhas (<3mm) e possíveis vibrações no pedal que indiquem empenamento dos discos."
            
        elif "motor" in q or "falha" in q or "velas" in q:
            resultado = f"Para um {veiculo}, falhas de motor sugerem verificar velas de ignição e bobinas. Se for falha em marcha lenta, limpe o corpo de borboleta."
            
        elif "aquecendo" in q or "temperatura" in q:
            resultado = f"Atenção: superaquecimento no {veiculo} pode ser grave. Verifique o nível do aditivo, mangueiras e se a ventoinha arma corretamente."
            
        elif "suspensão" in q or "batendo" in q:
            resultado = f"Sons na suspensão do {veiculo} geralmente indicam buchas de bandeja estouradas, bieletas com folga ou amortecedores vencidos."
            
        elif "partida" in q or "bateria" in q:
            resultado = f"Problema de partida no {veiculo}: teste a voltagem da bateria e verifique o motor de arranque. Se houver giro lento, pode ser mal contato nos bornes."
            
        else:
            resultado = f"Como o sintoma relatado não é comum para o {veiculo}, recomendo: 1. Escaneamento via OBDII para verificar códigos de erro. 2. Verificação de histórico de manutenções. 3. Teste de rodagem."
        
        # Exibição do resultado
        st.success(f"Análise para {veiculo}:")
        st.info(resultado)
    else:
        st.warning("Por favor, preencha o modelo do veículo e descreva o problema.")

# --- RODAPÉ ---
st.divider()
st.caption("Performance Serviços Automotivos - Foz do Iguaçu")
