import streamlit as st
import pandas as pd
from datetime import datetime, date
import os

# Configuração inicial
st.set_page_config(page_title="Studio LuaMar - Financeiro", layout="wide")

# Caminhos dos arquivos
clientes_path = "clientes.xlsx"
receitas_path = "receitas.xlsx"
despesas_path = "despesas.xlsx"

# Função para formatar datas no padrão brasileiro
def formatar_data(data):
    if isinstance(data, (datetime, date)):
        return data.strftime("%d/%m/%Y")
    return data

# Função para carregar ou criar os DataFrames
def carregar_dados():
    # DataFrames padrão (estrutura inicial)
    clientes_df = pd.DataFrame(columns=["Nome", "Telefone", "Último Atendimento", "Serviço"])
    receitas_df = pd.DataFrame(columns=["Data", "Cliente", "Serviço", "Valor", "Pago", "Forma de Pagamento", "Observação"])
    despesas_df = pd.DataFrame(columns=["Data", "Categoria", "Descrição", "Valor", "Forma de Pagamento", "Observação"])
    
    # Carregar clientes (se existir)
    if os.path.exists(clientes_path):
        clientes_df = pd.read_excel(clientes_path)
        if "Último Atendimento" in clientes_df.columns:
            clientes_df["Último Atendimento"] = pd.to_datetime(clientes_df["Último Atendimento"], errors="coerce")
    
    # Carregar receitas (se existir)
    if os.path.exists(receitas_path):
        receitas_df = pd.read_excel(receitas_path)
        receitas_df["Data"] = pd.to_datetime(receitas_df["Data"], errors="coerce")
    
    # Carregar despesas (se existir)
    if os.path.exists(despesas_path):
        despesas_df = pd.read_excel(despesas_path)
        despesas_df["Data"] = pd.to_datetime(despesas_df["Data"], errors="coerce")
    
    return clientes_df, receitas_df, despesas_df

# Carregar dados
clientes_df, receitas_df, despesas_df = carregar_dados()

# Interface principal
st.title("Studio LuaMar - Controle Financeiro")

# Abas para organização
tab1, tab2, tab3 = st.tabs(["📈 Receitas", "💸 Despesas", "📊 Relatórios"])

# TAB 1: RECEITAS (ATENDIMENTOS)
with tab1:
    st.header("Controle de Receitas")
    
    # Formulário de novo atendimento
    with st.expander("➕ Novo Atendimento", expanded=True):
        with st.form("novo_atendimento"):
            col1, col2 = st.columns(2)
            with col1:
                nome = st.text_input("Nome do Cliente*")
                telefone = st.text_input("Telefone")
                servico = st.selectbox("Serviço*", ["Maquiagem", "Extensão de Cílios", "Sobrancelha", "Outro"])
            with col2:
                valor = st.number_input("Valor (R$)*", min_value=0.0, format="%.2f")
                pago = st.selectbox("Pagamento Realizado?*", ["Sim", "Não"])
                forma_pagamento = st.selectbox("Forma de Pagamento", ["Pix", "Dinheiro", "Cartão", "Outro"])
                data = st.date_input("Data do Atendimento*", datetime.now())
            observacao = st.text_area("Observação")
            enviar = st.form_submit_button("Registrar Atendimento")

        if enviar and nome and servico and valor:
            # Adiciona às receitas
            nova_receita = pd.DataFrame([{
                "Data": pd.to_datetime(data),
                "Cliente": nome,
                "Serviço": servico,
                "Valor": valor,
                "Pago": pago,
                "Forma de Pagamento": forma_pagamento,
                "Observação": observacao
            }])
            receitas_df = pd.concat([receitas_df, nova_receita], ignore_index=True)
            receitas_df.to_excel(receitas_path, index=False)

            # Atualiza cliente
            novo_cliente = pd.DataFrame([{
                "Nome": nome,
                "Telefone": telefone,
                "Último Atendimento": data,
                "Serviço": servico
            }])
            clientes_df = pd.concat([clientes_df, novo_cliente], ignore_index=True)
            clientes_df.drop_duplicates(subset="Nome", keep="last", inplace=True)
            clientes_df.to_excel(clientes_path, index=False)

            st.success("Atendimento registrado com sucesso!")
            st.rerun()

    # Histórico de atendimentos
    st.subheader("Histórico de Atendimentos")
    if not receitas_df.empty:
        receitas_exibicao = receitas_df.copy()
        receitas_exibicao["Data"] = receitas_exibicao["Data"].apply(formatar_data)
        st.dataframe(receitas_exibicao)
    else:
        st.info("Nenhum atendimento registrado ainda.")

# TAB 2: DESPESAS
with tab2:
    st.header("Controle de Despesas")
    
    # Formulário de nova despesa
    with st.expander("➕ Nova Despesa", expanded=True):
        with st.form("nova_despesa"):
            col1, col2 = st.columns(2)
            with col1:
                categoria = st.selectbox("Categoria*", ["Material", "Aluguel", "Salários", "Manutenção", "Outros"])
                descricao = st.text_input("Descrição*")
            with col2:
                valor = st.number_input("Valor (R$)*", min_value=0.0, format="%.2f")
                forma_pagamento = st.selectbox("Forma de Pagamento*", ["Pix", "Dinheiro", "Cartão", "Outro"])
                data = st.date_input("Data*", datetime.now())
            observacao = st.text_area("Observação")
            enviar = st.form_submit_button("Registrar Despesa")

        if enviar and categoria and descricao and valor:
            nova_despesa = pd.DataFrame([{
                "Data": pd.to_datetime(data),
                "Categoria": categoria,
                "Descrição": descricao,
                "Valor": valor,
                "Forma de Pagamento": forma_pagamento,
                "Observação": observacao
            }])
            despesas_df = pd.concat([despesas_df, nova_despesa], ignore_index=True)
            despesas_df.to_excel(despesas_path, index=False)
            st.success("Despesa registrada com sucesso!")
            st.rerun()

    # Histórico de despesas
    st.subheader("Histórico de Despesas")
    if not despesas_df.empty:
        despesas_exibicao = despesas_df.copy()
        despesas_exibicao["Data"] = despesas_exibicao["Data"].apply(formatar_data)
        st.dataframe(despesas_exibicao)
    else:
        st.info("Nenhuma despesa registrada ainda.")

# TAB 3: RELATÓRIOS
with tab3:
    st.header("Relatórios Financeiros")
    
    if not receitas_df.empty or not despesas_df.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Resumo Mensal")
            
            # Verifica e converte datas se necessário
            if not pd.api.types.is_datetime64_any_dtype(receitas_df['Data']):
                receitas_df['Data'] = pd.to_datetime(receitas_df['Data'], errors='coerce')
            
            # Lista de meses disponíveis (versão corrigida)
            meses_disponiveis = ["Todos"] + sorted(
                list(set(receitas_df["Data"].dt.strftime("%m/%Y").dropna().unique()))
            )
            mes = st.selectbox("Selecione o mês", meses_disponiveis, index=0)
            
            # Cálculos financeiros
            if mes == "Todos":
                total_receitas = receitas_df["Valor"].sum()
                total_despesas = despesas_df["Valor"].sum()
            else:
                mes_selecionado = mes
                total_receitas = receitas_df[receitas_df["Data"].dt.strftime("%m/%Y") == mes]["Valor"].sum()
                total_despesas = despesas_df[despesas_df["Data"].dt.strftime("%m/%Y") == mes]["Valor"].sum()
            
            st.metric("Total Receitas", f"R$ {total_receitas:,.2f}")
            st.metric("Total Despesas", f"R$ {total_despesas:,.2f}")
            st.metric("Lucro Líquido", f"R$ {total_receitas - total_despesas:,.2f}",
                     delta_color="inverse" if (total_receitas - total_despesas) < 0 else "normal")
        
        with col2:
            st.subheader("Distribuição por Categoria")
            if not despesas_df.empty:
                st.bar_chart(despesas_df.groupby("Categoria")["Valor"].sum())
            else:
                st.info("Nenhuma despesa para exibir gráfico.")
    else:
        st.info("Nenhum dado disponível para gerar relatórios.")

# Rodapé
st.divider()
st.caption("Sistema de Gestão Financeira - Studio LuaMar | Desenvolvido com Streamlit")