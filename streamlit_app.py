import streamlit as st
import pandas as pd
import os
from datetime import datetime
from calendar import month_name
import matplotlib.pyplot as plt

# Função para carregar os dados e converter a coluna 'Data' para datetime
def carregar_dados():
    if os.path.exists('votos.csv'):
        df = pd.read_csv('votos.csv')
        df['Data'] = pd.to_datetime(df['Data'])  # Converter coluna 'Data' para datetime
    else:
        df = pd.DataFrame(columns=['Opção', 'Votos', 'Data'])
    
    return df

# Função para salvar votos em arquivo CSV
def salvar_votos():
    now = datetime.now()
    
    # Carregar votos existentes
    df_existente = carregar_dados()

    # Dados dos novos votos
    novos_votos = {
        'Opção': [],
        'Votos': [],
        'Data': []
    }

    for opcao, votos in st.session_state.votos.items():
        novos_votos['Opção'].append(opcao)
        novos_votos['Votos'].append(votos)
        novos_votos['Data'].append(now.strftime('%Y-%m-%d %H:%M:%S'))

    df_novos = pd.DataFrame(novos_votos)
    
    # Concatenar os dados existentes com os novos e salvar no arquivo
    df_concatenado = pd.concat([df_existente, df_novos], ignore_index=True)
    df_concatenado.to_csv('votos.csv', index=False)

# Inicializar contadores de votos se não existirem na sessão
if 'votos' not in st.session_state:
    st.session_state.votos = {'Péssimo': 0, 'Ruim': 0, 'Regular': 0, 'Bom': 0, 'Ótimo': 0}

# Função para atualizar votos
def votar(opcao):
    st.session_state.votos[opcao] += 1
    salvar_votos()

    # Mostrar mensagem de sucesso por 1 segundo
    mensagem = st.empty()
    mensagem.success(f'Voto registrado: {opcao}')
    st.session_state.last_message = mensagem  # Salvar mensagem para possível limpeza posterior

    # Limpar a mensagem após 1 segundo
    st.session_state.timeout = 1
    st.session_state.last_update = st.session_state.timeout

# Função para mostrar a tela principal
def tela_principal():
    st.markdown("""
        <style>
        .content {
            text-align: center;
            height: 100vh; /* Altura total da viewport */
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }
        .button-container {
            width: 100%;
            display: flex;
            justify-content: space-around;
            align-items: flex-start;
            flex-wrap: wrap;
            margin-top: 20px;
        }
        .stButton button {
            width: 100px;
            height: 40px;
            font-size: 16px;
            font-weight: bold;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            margin-top: 10px;
        }
        .stButton button:hover {
            background-color: #45a049;
        }
        .footer-button {
            width: 150px;
            background-color: #007BFF;
            color: white;
            border: none;
            border-radius: 5px;
            height: 30px;
            cursor: pointer;
            font-size: 14px;
            font-weight: bold;
            margin-top: 20px;
            margin-bottom: 20px;
        }
        .small-button {
            background-color: #007BFF;
            color: white;
            border: none;
            border-radius: 5px;
            height: 25px;
            cursor: pointer;
            font-size: 12px;
            font-weight: bold;
            padding: 0 10px;
        }
        </style>
        """, unsafe_allow_html=True)

    st.title('Como estava o almoço hoje?')
    st.markdown('<div class="content">', unsafe_allow_html=True)

    # Mostrar as opções de votação e os botões
    with st.markdown('<div class="button-container">', unsafe_allow_html=True):
        if st.button('Péssimo'):
            votar('Péssimo')
        if st.button('Ruim'):
            votar('Ruim')
        if st.button('Regular'):
            votar('Regular')
        if st.button('Bom'):
            votar('Bom')
        if st.button('Ótimo'):
            votar('Ótimo')

    st.markdown('</div>', unsafe_allow_html=True)

    # Botão invisível para controlar o fluxo da aplicação
    if st.button('Relatórios', key='ver_relatorios_hidden'):
        st.session_state.page = 'resultados'

# Função para filtrar os resultados por mês
def filtrar_por_mes(df, mes):
    if mes == 'Todos':  # Se selecionar 'Todos'
        return df
    else:
        return df[df['Data'].dt.month == mes]

# Função para filtrar os resultados por dia
def filtrar_por_dia(df, dia):
    if dia == 'Todos':  # Se selecionar 'Todos'
        return df
    else:
        return df[df['Data'].dt.strftime('%d/%m/%Y') == dia]

# Função para calcular indicadores
def calcular_indicadores(df):
    total_votos = df['Votos'].sum()
    if total_votos > 0:
        pessimo = df[df['Opção'] == 'Péssimo']['Votos'].sum()
        ruim = df[df['Opção'] == 'Ruim']['Votos'].sum()
        regular = df[df['Opção'] == 'Regular']['Votos'].sum()
        bom = df[df['Opção'] == 'Bom']['Votos'].sum()
        otimo = df[df['Opção'] == 'Ótimo']['Votos'].sum()
    else:
        pessimo = 0
        ruim = 0
        regular = 0
        bom = 0
        otimo = 0
    
    return pessimo, ruim, regular, bom, otimo, total_votos

# Função para mostrar a tela de resultados
def tela_resultados():
    st.title('Resultados')

    # Carregar dados do arquivo votos.csv
    df = carregar_dados()

    # Filtro por mês
    meses = ['Todos'] + list(range(1, 13))
    mes_selecionado = st.selectbox('Filtrar por mês:', meses)

    df_filtrado_mes = filtrar_por_mes(df, mes_selecionado)

    # Filtro por dia
    dias = ['Todos'] + df_filtrado_mes['Data'].dt.strftime('%d/%m/%Y').unique().tolist() if not df_filtrado_mes.empty else ['Todos']
    dia_selecionado = st.selectbox('Filtrar por dia:', dias)

    df_filtrado = filtrar_por_dia(df_filtrado_mes, dia_selecionado)

    if df_filtrado.empty:
        st.write('Nenhum dado disponível para os filtros selecionados.')
    else:
        # Mostrar tabela com resultados filtrados (primeiras 6 linhas)
        st.dataframe(df_filtrado.head(6), width=700)

        # Calcular indicadores
        pessimo, ruim, regular, bom, otimo, total_votos = calcular_indicadores(df_filtrado)

        # Gráfico de pizza com percentual de votos
        st.write('### Percentual de Votos por Opção')
        sizes = [pessimo, ruim, regular, bom, otimo]
        labels = ['Péssimo', 'Ruim', 'Regular', 'Bom', 'Ótimo']
        colors = ['red', 'brown', 'yellow', 'lightgreen', 'darkgreen']
        explode = (0.1, 0, 0, 0, 0)  # explode 1st slice (Péssimo)

        fig1, ax1 = plt.subplots(figsize=(4, 3))
        ax1.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=140)
        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        st.pyplot(fig1)

        # Gráfico de barras com quantidade de votos
        st.write('### Quantidade de Votos do Mês')
        fig2, ax2 = plt.subplots()
        ax2.bar(['Péssimo', 'Ruim', 'Regular', 'Bom', 'Ótimo'], [pessimo, ruim, regular, bom, otimo], color=['red', 'brown', 'yellow', 'lightgreen', 'darkgreen'])
        for i, v in enumerate([pessimo, ruim, regular, bom, otimo]):
            ax2.text(i, v + 0.1, str(v), ha='center', va='bottom')
        st.pyplot(fig2)

        # Mostrar quantidade total de votos
        st.write(f'### Total de Votos: {total_votos}')
        
        # Resumo dos votos
        st.write('### Resumo dos Votos')
        for opcao, quantidade in zip(['Péssimo', 'Ruim', 'Regular', 'Bom', 'Ótimo'], [pessimo, ruim, regular, bom, otimo]):
            percentual = (quantidade / total_votos) * 100 if total_votos > 0 else 0
            st.write(f'{opcao}: {quantidade} votos ({percentual:.2f}%)')

# Controlar fluxo da aplicação
if 'page' not in st.session_state:
    st.session_state.page = 'principal'

if st.session_state.page == 'principal':
    tela_principal()
elif st.session_state.page == 'resultados':
    tela_resultados()
