elif st.session_state.pagina == "Histórico":
    st.header("💰 Financeiro & Histórico")
    
    # 1. Carregar dados
    orcamentos = carregar_dados("orcamentos.json")
    
    # 2. Resumo Financeiro (Total de Vendas)
    total_vendas = sum(item.get("Venda", 0) for item in orcamentos)
    
    col_a, col_b = st.columns(2)
    col_a.metric("Total Faturado", f"R$ {total_vendas:.2f}")
    
    # 3. Lançamento de Despesa Extra (Peças, Aluguel, etc)
    with st.expander("➕ Lançar Nova Despesa"):
        with st.form("despesa_form", clear_on_submit=True):
            descricao = st.text_input("Descrição da despesa")
            valor = st.number_input("Valor R$", min_value=0.0)
            if st.form_submit_button("Registrar Despesa"):
                despesas = carregar_dados("despesas.json")
                despesas.append({"Descrição": descricao, "Valor": valor})
                salvar_dados("despesas.json", despesas)
                st.success("Despesa salva!")
                st.rerun()

    # 4. Cálculo de Lucro Bruto
    despesas = carregar_dados("despesas.json")
    total_despesas = sum(d.get("Valor", 0) for d in despesas)
    lucro = total_vendas - total_despesas
    col_b.metric("Lucro (Vendas - Despesas)", f"R$ {lucro:.2f}", delta_color="normal")
    
    # 5. Tabelas
    st.subheader("Histórico de Orçamentos")
    if orcamentos:
        st.table(pd.DataFrame(orcamentos))
    
    st.subheader("Despesas Registradas")
    if despesas:
        st.table(pd.DataFrame(despesas))
