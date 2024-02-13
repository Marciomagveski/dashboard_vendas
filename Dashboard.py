import streamlit as st
import requests 
import pandas as pd 
import plotly.express as px 

import streamlit as st

st.set_page_config(
    page_title="Ex-stream-ly Cool App",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)

with open("styles.css") as f:
    st.markdown(f"<style> {f.read()} </sytle>", unsafe_allow_html=True)




def formata_numero(valor, prefixo = ''):
    for unidade in ['', 'mil']:
        if valor <1000:
            return f'{prefixo} {valor:.2f} {unidade}'
        valor /= 1000
    return f'{prefixo} {valor:.2f} milhões'

st.title('Dashboard de Vendas :shopping_trolley:')

url = 'https://labdados.com/produtos'
regioes = ['Brasil', 'Centro-Oeste', 'Nordeste', 'Norte', 'Sudeste', 'Sul']

st.sidebar.title('Filtros')
regiao = st.sidebar.selectbox('Região', regioes)

if regiao == 'Brasil':
    regiao = ''

todos_anos = st.sidebar.checkbox('Dados de todo o período', value=True)

if todos_anos:
    ano = ''
else:
    ano = st.sidebar.slider('Ano', 2020, 2023)


query_string = {'regiao': regiao.lower(), 'ano':ano}


response = requests.get(url, params=query_string)
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format = '%d/%m/%Y')


#Filtro Vendedores
filtro_vendedores = st.sidebar.multiselect('Vendedores', dados['Vendedor'].unique())
if filtro_vendedores:
    dados = dados[dados['Vendedor'].isin(filtro_vendedores)]



### Tabelas Receitas

receita_estados = dados.groupby('Local da compra')[['Preço']].sum()
receita_estados = dados.drop_duplicates(subset= 'Local da compra')[['Local da compra', 'lat', 'lon']].merge(receita_estados, left_on='Local da compra', right_index=True).sort_values('Preço', ascending=False)

receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq = 'M'))['Preço'].sum().reset_index()
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mes'] = receita_mensal['Data da Compra'].dt.month_name()

receita_categorias = dados.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço', ascending=False)



### Tabelas de quantidade





### Tabelas Vendedores


vendedores = pd.DataFrame(dados.groupby('Vendedor')['Preço'].agg(['sum','count']))




##Graficos



fig_mapa_receita = px.scatter_geo(receita_estados,
                                  lat = 'lat',
                                  lon = 'lon',
                                  scope = 'south america',
                                  size = 'Preço',
                                  template = 'seaborn',
                                  hover_name = 'Local da compra',
                                  hover_data = {'lat': False, 'lon': False},
                                  title = 'Receita por Estado')



fig_receita_mensal = px.line(receita_mensal,
                             x = 'Mes',
                             y = 'Preço',
                             markers = True,
                             range_y = (0, receita_mensal.max()),
                             color = 'Ano',
                             line_dash = 'Ano',
                             title = 'Receita mensal')

fig_receita_mensal.update_layout(yaxis_title = 'Receita')




fig_receitas_estados = px.bar(receita_estados.head(),
                              x = 'Local da compra',
                              y = 'Preço',
                              text_auto = True,
                              title = 'Top estados (receita)')


fig_receitas_estados.update_layout(yaxis_title = 'Receita')




fig_receitas_categorias = px.bar(receita_categorias,
                                text_auto = True,
                                title = 'Receita por categorias')

fig_receitas_categorias.update_layout(yaxis_title = 'Receita')




# Aba Vendedores










## Visualização no Streamlit

aba1, aba2, aba3 = st.tabs(["Receita", "Quantidade de Vendas", "Vendedores"])

#Aba 1

with aba1:
    coluna1, coluna2 = st.columns(2)

with coluna1:
    st.metric("Receita Total", formata_numero(dados['Preço'].sum(), 'R$'))
    st.plotly_chart(fig_mapa_receita, use_container_width=True)
    st.plotly_chart(fig_receitas_estados, use_container_width=True)
   
with coluna2:
    st.metric("Quantidade de Vendas", formata_numero(dados.shape[0]))
    st.plotly_chart(fig_receita_mensal, use_container_width=True)
    st.plotly_chart(fig_receitas_categorias, use_container_width=True)


#Aba 2 quantidade
    
with aba2:
    coluna1, coluna2 = st.columns(2)

with coluna1:
    st.metric("Receita Total", formata_numero(dados['Preço'].sum(), 'R$'))
 
   
with coluna2:
    st.metric("Quantidade de Vendas", formata_numero(dados.shape[0]))
   

#Aba 3 vendedores

with aba3:
    qtde_vendedores = st.number_input('Quantidade de Vendedores', 2, 10, 5)
    coluna1, coluna2 = st.columns(2)

with coluna1:
    st.metric("Receita Total", formata_numero(dados['Preço'].sum(), 'R$'))
    fig_receita_vendedores = px.bar(vendedores[['sum']].sort_values('sum', ascending=False).head(qtde_vendedores),
                                    x = 'sum',
                                    y=vendedores[['sum']].sort_values(['sum'], ascending=False).head(qtde_vendedores).index,
                                    text_auto=True,
                                    title=f'Top {qtde_vendedores} vendedores (receita)'
                                    )
    st.plotly_chart(fig_receita_vendedores)
    


   
with coluna2:
    st.metric("Quantidade de Vendas", formata_numero(dados.shape[0]))
    fig_vendas_vendedores = px.bar(vendedores[['count']].sort_values('count', ascending=False).head(qtde_vendedores),
                                    x = 'count',
                                    y=vendedores[['count']].sort_values(['count'], ascending=False).head(qtde_vendedores).index,
                                    text_auto=True,
                                    title=f'Top {qtde_vendedores} vendedores (Quantidade)'
                                    )
    st.plotly_chart(fig_vendas_vendedores)


# Criação de colunas














