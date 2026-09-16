import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da página (deve ser a 1ª linha do Streamlit)
st.set_page_config(page_title="Painel Estratégico CBMERJ", page_icon="🚒", layout="wide")

# 2. Carregamento de Dados
@st.cache_data
def load_data():
    # Substitua 'dados.csv' pelo nome exato do seu arquivo se não tiver renomeado
    df = pd.read_csv('dados.csv', sep=';') 
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("Arquivo de dados não encontrado. Verifique o nome na pasta.")
    st.stop()

# --- BARRA LATERAL (MENU E FILTROS) ---
# Adiciona o brasão (puxando da internet para dar um visual oficial)
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/c/cc/Bras%C3%A3o_CBMERJ.png/240px-Bras%C3%A3o_CBMERJ.png", width=120)
st.sidebar.title("Filtros Operacionais")
st.sidebar.markdown("Use as opções abaixo para refinar os dados da Operação **PLUVIAM**.")

# Filtros clicáveis
unidades_disponiveis = df['Unidade Agrupadora'].unique().tolist()
unidade_selecionada = st.sidebar.multiselect("Selecione o GBM/CBA:", unidades_disponiveis, default=unidades_disponiveis)

estados_disponiveis = df['Estado'].unique().tolist()
estado_selecionado = st.sidebar.multiselect("Status de Conservação:", estados_disponiveis, default=estados_disponiveis)

# Aplicando os filtros na base de dados
df_filtrado = df[(df['Unidade Agrupadora'].isin(unidade_selecionada)) & (df['Estado'].isin(estado_selecionado))]

# --- ÁREA PRINCIPAL DO DASHBOARD ---
st.title("🚒 Painel de Controle Logístico - CBMERJ")
st.markdown("Visão consolidada para gestão de recursos e pronta resposta.")
st.divider() # Linha de separação

# --- CARDS DE INDICADORES (KPIs) ---
col1, col2, col3, col4 = st.columns(4)
total_materiais = len(df_filtrado)
operando = len(df_filtrado[df_filtrado['Estado'] == 'operando'])
acautelado = len(df_filtrado[df_filtrado['Estado'] == 'acautelado'])

col1.metric("Total de Itens", f"{total_materiais:,}".replace(',','.'))
col2.metric("🟢 Operando", f"{operando:,}".replace(',','.'))
col3.metric("🟡 Acautelados", f"{acautelado:,}".replace(',','.'))
col4.metric("📈 Taxa de Prontidão", f"{(operando/total_materiais*100):.1f}%" if total_materiais > 0 else "0%")

st.markdown("<br>", unsafe_allow_html=True) # Espaçamento

# --- ABAS DE NAVEGAÇÃO ---
aba1, aba2, aba3 = st.tabs(["📊 Visão Geral", "🏢 Distribuição por Unidade", "📋 Base de Dados e Exportação"])

with aba1:
    colA, colB = st.columns(2)
    
    with colA:
        # Gráfico de Donut (Pizza vazada) Interativo
        estado_counts = df_filtrado['Estado'].value_counts().reset_index()
        estado_counts.columns = ['Estado', 'Quantidade']
        
        fig_pie = px.pie(estado_counts, values='Quantidade', names='Estado', 
                         title='Proporção por Status',
                         color_discrete_sequence=px.colors.sequential.Reds_r,
                         hole=0.4) 
        fig_pie.update_traces(textposition='inside', textinfo='percent+label', hoverinfo='label+percent+value')
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with colB:
        # Gráfico de Barras Horizontal Interativo
        top_materiais = df_filtrado['Material'].value_counts().head(10).reset_index()
        top_materiais.columns = ['Material', 'Quantidade']
        
        fig_bar = px.bar(top_materiais, x='Quantidade', y='Material', orientation='h',
                         title='Top 10 Equipamentos Mais Comuns',
                         color='Quantidade', color_continuous_scale='Reds')
        fig_bar.update_layout(yaxis={'categoryorder':'total ascending'}) # Ordena do maior pro menor visualmente
        st.plotly_chart(fig_bar, use_container_width=True)

with aba2:
    if not unidade_selecionada:
        st.warning("Selecione pelo menos uma unidade na barra lateral.")
    else:
        unidade_counts = df_filtrado['Unidade Agrupadora'].value_counts().reset_index()
        unidade_counts.columns = ['Unidade Agrupadora', 'Quantidade']
        
        fig_unidade = px.bar(unidade_counts, x='Unidade Agrupadora', y='Quantidade',
                             title='Volume Total de Material por GBM/CBA',
                             text_auto=True, color='Quantidade', color_continuous_scale='YlOrRd')
        st.plotly_chart(fig_unidade, use_container_width=True)
        
with aba3:
    st.subheader("Explorador de Dados")
    st.markdown("Tabela completa com base nos filtros selecionados. Clique nas colunas para ordenar.")
    # Tabela interativa
    st.dataframe(df_filtrado, use_container_width=True, height=350)
    
    # Botão de download real
    csv = df_filtrado.to_csv(index=False, sep=';').encode('utf-8')
    st.download_button(
        label="📥 Baixar Relatório Filtrado (CSV)",
        data=csv,
        file_name='relatorio_cbmerj_filtrado.csv',
        mime='text/csv',
        type="primary" # Deixa o botão destacado na cor padrão
    )