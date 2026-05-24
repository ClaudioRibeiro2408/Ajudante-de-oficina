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
        # Lógica de diagnóstico simplificada
        q = queixa.lower()
        
        if "barulho" in q and "freio" in q:
            resultado = "Possível causa: Pastilhas de freio gastas, discos empenados ou falta de lubrificação no cáliper."
        elif "falha" in q and "motor" in q:
            resultado = "Possível causa: Velas de ignição gastas, bobinas com defeito ou bico injetor obstruído."
        elif "aquecendo" in q or "temperatura" in q:
            resultado = "Possível causa: Nível baixo de aditivo, válvula termostática travada ou ventoinha com defeito."
        elif "partida" in q or "não liga" in q:
            resultado = "Possível causa: Bateria descarregada, motor de arranque ou falha no sistema de combustível."
        else:
            resultado = "Sintoma genérico. Recomendada inspeção detalhada via scanner automotivo para leitura de falhas (DTCs)."
        
        # Exibição do resultado
        st.success(f"Análise para {veiculo}:")
        st.info(resultado)
    else:
        st.warning("Por favor, preencha o modelo do veículo e descreva o problema.")

# --- RODAPÉ ---
st.divider()
st.caption("Performance Serviços Automotivos - Foz do Iguaçu")
