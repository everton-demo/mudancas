# importar bibliotecas
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import pandas as pd
from datetime import timedelta
import plotly.express as px
import math

# emojis: https://www.webfx.com/tools/emoji-cheat-sheet/
st.set_page_config(page_title="Mudanças ABAP", page_icon=":bar_chart:", layout="wide")

# https://github.com/Sven-Bo/streamlit-sales-dashboard-with-userauthentication/blob/master/app.py
# https://github.com/luhborba/streamlite-login/blob/master/app.py
# https://github.com/mkhorasani/Streamlit-Authenticator
# https://www.youtube.com/watch?v=oWxAZoyyzCc&t=39s
# https://discuss.streamlit.io/t/deploying-streamlit-authenticator-via-streamlit-community-cloud/39085
# --- USER AUTHENTICATION ---
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# Pre-hashing all plain text passwords once
#hashed_passwords = stauth.Hasher.hash_passwords(config['credentials'])
#hashed_passwords

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

try:
    authenticator.login()
except Exception as e:
    st.error(e)

if st.session_state["authentication_status"] is False:
    st.error('Usuário/Senha inválido')
elif st.session_state["authentication_status"] is None:
    st.warning('Informar usuário e senha')
elif st.session_state["authentication_status"]:
    #st.write(f'Bem Vindo *{st.session_state["name"]}*')

    # criar as funções de carregamento de dados
    @st.cache_data
    def carregar_mudancas():
        base = pd.read_csv("MUDANCAS.csv", sep=";",  decimal=",", encoding='latin-1')
        base["Código"] = base["Código"].astype('str')
        base["Ano"] = base["Ano"].astype('str')
        #base["Mês"] = base["Mês"].astype('int')
        return base

    dados = carregar_mudancas()
    dados_filtrados = dados

    authenticator.logout("Logout", "sidebar")

    # criar a interface do streamlit
    st.write(f"""
    # Mudanças implantadas em PRD entre 2023 e 2025
    """)

    # prepara as visualizações = filtros
    st.sidebar.header("Filtros")

    # filtro de ano
    filtro_ano = dados.sort_values("Ano")
    filtro_ano = filtro_ano["Ano"].unique()
    ano = st.sidebar.multiselect("Ano", filtro_ano)
    if ano:
        dados_filtrados = dados[dados["Ano"].isin(ano)]

    # filtro de mês
    mes_inicial = dados_filtrados["Mês"].min()
    mes_final = dados_filtrados["Mês"].max()
    mes_intervalo = st.sidebar.slider("Período", 
                                    min_value=mes_inicial, 
                                    max_value=mes_final,
                                    value=(mes_inicial, mes_final), #tupla
                                    step=1)

    dados_filtrados = dados_filtrados[dados_filtrados["Mês"].between(mes_intervalo[0], mes_intervalo[1])]

    # filtro de analista
    filtro_analista = dados_filtrados.sort_values("Analista")
    filtro_analista = filtro_analista["Analista"].unique()
    analista = st.sidebar.selectbox("Analista", filtro_analista, index=None)
    if analista:
        dados_filtrados = dados_filtrados[dados_filtrados["Analista"] == analista]

    # filtro de módulo
    filtro_modulo = dados_filtrados.sort_values("Módulo")
    filtro_modulo = filtro_modulo["Módulo"].unique()
    modulo = st.sidebar.selectbox("Módulo", filtro_modulo, index=None)
    if modulo:
        dados_filtrados = dados_filtrados[dados_filtrados["Módulo"] == modulo]

    # filtro de solicitante
    filtro_solicitante = dados_filtrados.sort_values("Solicitante")
    filtro_solicitante = filtro_solicitante["Solicitante"].unique()
    solicitante = st.sidebar.selectbox("Solicitante", filtro_solicitante, index=None)
    if solicitante:
        dados_filtrados = dados_filtrados[dados_filtrados["Solicitante"] == solicitante]

    # filtro de diretoria
    filtro_diretoria = dados_filtrados.sort_values("Diretoria")
    filtro_diretoria = filtro_diretoria["Diretoria"].unique()
    diretoria = st.sidebar.selectbox("Diretoria", filtro_diretoria, index=None)
    if diretoria:
        dados_filtrados = dados_filtrados[dados_filtrados["Diretoria"] == diretoria]

    # filtro de horas ABAP
    horas_abap = st.sidebar.checkbox("Horas ABAP (TOP 10)")
    if horas_abap:
        dados_filtrados = dados_filtrados.sort_values("Horas").tail(10)

    # criar os gráficos
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)
    col5, col6 = st.columns(2)
    col7, col8 = st.columns(2)

    # https://plotly.com/python/bar-charts/

    # Mudanças por Analista
    anl_total = dados_filtrados.groupby("Analista")[["Count"]].sum().reset_index()
    fig_mud_anl = px.bar(anl_total, x="Analista", y="Count",
                    title="Mudanças por Analista", 
                    labels={'Count': 'Total'},
                    text_auto=True)
    fig_mud_anl.update_xaxes(categoryorder="total descending")
    #fig_mud_anl.update_traces(textposition='outside',texttemplate='%{text:.2s}')
    fig_mud_anl.update_traces(textposition="outside")
    #fig_mud_anl.update_layout(xaxis_tickangle=-45)
    fig_mud_anl.update_yaxes(showticklabels=False)
    col1.plotly_chart(fig_mud_anl, use_container_width=True)

    # Horas ABAP por analista
    anl_horas = dados_filtrados.groupby("Analista")[["Horas"]].sum().reset_index()
    fig_mud_anl_hor = px.bar(anl_horas, x="Analista", y="Horas",
                    title="Horas ABAP por Analista", 
                    text_auto=True)
    fig_mud_anl_hor.update_xaxes(categoryorder="total descending")
    fig_mud_anl_hor.update_traces(textposition="outside")
    fig_mud_anl_hor.update_yaxes(showticklabels=False)
    col2.plotly_chart(fig_mud_anl_hor, use_container_width=True)

    # Mudanças por Módulo
    mod_total = dados_filtrados.groupby("Módulo")[["Count"]].sum().reset_index()
    fig_mud_mod = px.bar(mod_total, x="Módulo", y="Count",
                    title="Mudanças por Módulo",
                    labels={'Count': 'Total'},
                    text_auto=True)
    fig_mud_mod.update_xaxes(categoryorder="total descending")
    fig_mud_mod.update_yaxes(showticklabels=False)
    fig_mud_mod.update_traces(textposition="outside")
    col3.plotly_chart(fig_mud_mod, use_container_width=True)

    # Horas ABAP por Módulo
    mod_horas = dados_filtrados.groupby("Módulo")[["Horas"]].sum().reset_index()
    fig_mud_mod_hor = px.bar(mod_horas, x="Módulo", y="Horas",
                    title="Horas ABAP por Módulo",
                    text_auto=True)
    fig_mud_mod_hor.update_xaxes(categoryorder="total descending")
    fig_mud_mod_hor.update_yaxes(showticklabels=False)
    fig_mud_mod_hor.update_traces(textposition="outside")
    col4.plotly_chart(fig_mud_mod_hor, use_container_width=True)

    # Mudanças por Diretoria
    dir_total = dados_filtrados.groupby("Diretoria")[["Count"]].sum().reset_index()
    fig_mud_dir = px.bar(dir_total, x="Count", y="Diretoria",
                    title="Mudanças por Diretoria",
                    labels={'Count': 'Total'},
                    text_auto=True)
    fig_mud_dir.update_xaxes(showticklabels=False)
    fig_mud_dir.update_yaxes(categoryorder="total ascending")
    fig_mud_dir.update_traces(textposition="outside")
    col5.plotly_chart(fig_mud_dir, use_container_width=True)

    # Horas ABAP por Diretoria
    dir_horas = dados_filtrados.groupby("Diretoria")[["Horas"]].sum().reset_index()
    fig_mud_dir_hor = px.bar(dir_horas, x="Horas", y="Diretoria",
                    title="Horas ABAP por Diretoria",
                    text_auto=True)
    fig_mud_dir_hor.update_xaxes(showticklabels=False)
    fig_mud_dir_hor.update_yaxes(categoryorder="total ascending")
    fig_mud_dir_hor.update_traces(textposition="outside")
    col6.plotly_chart(fig_mud_dir_hor, use_container_width=True)

    # Mudanças por Solicitante
    sol_total = dados_filtrados.groupby("Solicitante")[["Count"]].sum().reset_index()
    sol_total = sol_total.sort_values("Count").tail(10)
    fig_mud_sol = px.bar(sol_total, x="Count", y="Solicitante",
                    title="Mudanças por Solicitante (TOP 10)",
                    labels={'Count': 'Total'},
                    text_auto=True)
                    #height=1000)
    fig_mud_sol.update_xaxes(showticklabels=False)
    fig_mud_sol.update_yaxes(categoryorder="total ascending")
    fig_mud_sol.update_traces(textposition="outside") #, textfont_size=20, textangle=0, cliponaxis=False)
    col7.plotly_chart(fig_mud_sol, use_container_width=True)

    # Mudanças por Mês
    mes_total = dados_filtrados.groupby("Mês")[["Count"]].sum().reset_index()
    fig_mud_mes = px.bar(mes_total, x="Mês", y="Count",
                    title="Mudanças por Mês",
                    #barmode='stack',
    #Para colocar as barras lado a lado usamos barmode='group', enquanto para barras empilhadas usamos o barmode='stack'.
                    orientation="v",
                    labels={'Count': 'Total'},
                    text_auto=True)
    fig_mud_mes.update_xaxes(categoryorder="total descending")
    fig_mud_mes.update_yaxes(showticklabels=False)
    fig_mud_mes.update_traces(textposition="outside")
    # para aparecer todos os valores no eixo x:
    fig_mud_mes.update_layout(xaxis = dict(linecolor='rgba(0,0,0,1)', # adicionando linha em y = 0
                            tickmode = 'array',                     # alterando o modo dos ticks
                            tickvals = mes_total['Mês'],            # setando a posição do tick de x
                            ticktext = mes_total['Mês']))           # setando o valor do tick de x
    col8.plotly_chart(fig_mud_mes, use_container_width=True)
    # https://andersonmdcanteli.github.io/Dashboards-com-Plotly-Express/
    # https://andersonmdcanteli.github.io/Dashboards-com-Plotly-Express-Parte-2/
    # https://andersonmdcanteli.github.io/Dashboards-com-Plotly-Express-Parte-3/

    # exibir dataframe
    st.dataframe(dados_filtrados) #.head(10))

    nr_mudancas = len(dados_filtrados.index)
    st.sidebar.write(f"""
    ### {nr_mudancas} mudanças selecionadas
    """)



