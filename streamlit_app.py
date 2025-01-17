import streamlit as st
import pandas as pd
import os
from datetime import datetime
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
def salvar_votos(nova_votacao):
    df_existente = carregar_dados()
    df_novo = pd.DataFrame([nova_votacao])
    df_concatenado = pd.concat([df_existente, df_novo], ignore_index=True)
    df_concatenado.to_csv('votos.csv', index=False)

# Inicializar contadores de votos e última votação se não existirem na sessão
if 'votos' not in st.session_state:
    st.session_state.votos = {'Péssimo': 0, 'Ruim': 0, 'Regular': 0, 'Bom': 0, 'Ótimo': 0}
if 'ultima_votacao' not in st.session_state:
    st.session_state.ultima_votacao = None

# Função para atualizar votos
def votar(opcao):
    agora = datetime.now()
    nova_votacao = {'Opção': opcao, 'Votos': 1, 'Data': agora.strftime('%Y-%m-%d %H:%M:%S')}
    salvar_votos(nova_votacao)
    st.session_state.ultima_votacao = agora
    st.session_state.votos[opcao] += 1
    st.success(f'Voto registrado: {opcao}')

# Função para mostrar a tela principal
def tela_principal():
    st.markdown("""
        <style>
        .main-container {
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .content {
            text-align: center;
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

    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.title('Como estava o almoço hoje?')
    st.markdown('<div class="content">', unsafe_allow_html=True)

    # Mostrar as opções de votação e os botões
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.image('pessimo.png', width=100)
        if st.button('Péssimo', key='pessimo_button'):
            votar('Péssimo')

    with col2:
        st.image('ruim.png', width=100)
        if st.button('Ruim', key='ruim_button'):
            votar('Ruim')

    with col3:
        st.image('regular.png', width=100)
        if st.button('Regular', key='regular_button'):
            votar('Regular')

    with col4:
        st.image('bom.png', width=100)
        if st.button('Bom', key='bom_button'):
            votar('Bom')

    with col5:
        st.image('otimo.png', width=100)
        if st.button('Ótimo', key='otimo_button'):
            votar('Ótimo')

    st.markdown('</div>', unsafe_allow_html=True)

    # Botão para visualizar os resultados
    st.markdown('<br>', unsafe_allow_html=True)
    st.markdown('<br>', unsafe_allow_html=True)
    st.markdown('<br>', unsafe_allow_html=True)

    # Botão invisível para controlar o fluxo da aplicação
    st.markdown('<div style="visibility: hidden;">', unsafe_allow_html=True)
    if st.button('Relatórios', key='ver_relatorios_hidden'):
        st.session_state.page = 'resultados'
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# Função para filtrar os resultados por mês
def filtrar_por_mes(df, mes):
    if mes == 'Todos':
        return df
    else:
        return df[df['Data'].dt.month == mes]

# Função para filtrar os resultados por dia
def filtrar_por_dia(df, dia):
    if dia == 'Todos':
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

    # Layout em duas colunas para filtros
    col1, col2 = st.columns(2)

    # Filtro por mês
    meses = ['Todos'] + list(range(1, 13))
    mes_selecionado = col1.selectbox('Filtrar por mês:', meses)

    df_filtrado_mes = filtrar_por_mes(df, mes_selecionado)

    # Filtro por dia
    dias = ['Todos'] + df_filtrado_mes['Data'].dt.strftime('%d/%m/%Y').unique().tolist() if not df_filtrado_mes.empty else ['Todos']
    dia_selecionado = col2.selectbox('Filtrar por dia:', dias)

    df_filtrado = filtrar_por_dia(df_filtrado_mes, dia_selecionado)

    # Layout em duas colunas para gráficos
    col3, col4 = st.columns(2)

    if df_filtrado.empty:
        st.write('Nenhum dado disponível para os filtros selecionados.')
    else:
        # Calcular indicadores
        pessimo, ruim, regular, bom, otimo, total_votos = calcular_indicadores(df_filtrado)
        
        # Gráfico de pizza com percentual de votos
        col3.write('### Percentual de Votos por Opção')
        sizes = [pessimo, ruim, regular, bom, otimo]
        labels = ['Péssimo', 'Ruim', 'Regular', 'Bom', 'Ótimo']
        colors = ['red', 'brown', 'yellow', 'lightgreen', 'darkgreen']
        explode = (0.1, 0, 0, 0, 0)

        fig1, ax1 = plt.subplots(figsize=(4, 3))
        ax1.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=140)
        ax1.axis('equal')
        col3.pyplot(fig1)

        # Gráfico de barras com quantidade de votos
        col4.write('### Quantidade de Votos do Mês')
        fig2, ax2 = plt.subplots()
        ax2.bar(['Péssimo', 'Ruim', 'Regular', 'Bom', 'Ótimo'], [pessimo, ruim, regular, bom, otimo], color=['red', 'brown', 'yellow', 'lightgreen', 'darkgreen'])
        for i, v in enumerate([pessimo, ruim, regular, bom, otimo]):
            ax2.text(i, v + 0.1, str(v), ha='center')
        col4.pyplot(fig2)

        # Layout em duas colunas para resumo dos votos e tabela
        col5, col6 = st.columns([2, 1])

        # Mostrar tabela com resultados filtrados (primeiras 6 linhas)
        col5.dataframe(df_filtrado.head(999), width=700)

        # Mostrar quantidade total de votos
        col6.write(f'### Total de Votos: {total_votos}')

        # Mostrar indicadores
        col6.write('### Indicadores de Votos')
        col6.write(f'- Péssimo: {pessimo}')
        col6.write(f'- Ruim: {ruim}')
        col6.write(f'- Regular: {regular}')
        col6.write(f'- Bom: {bom}')
        col6.write(f'- Ótimo: {otimo}')

    # Botão para voltar para tela principal
    st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
    if st.button('Voltar para Votação', key='voltar_votacao_button'):
        st.session_state.page = 'principal'
    st.markdown('</div>', unsafe_allow_html=True)

# Função principal para controle da navegação entre telas
def main():
    if 'page' not in st.session_state:
        st.session_state.page = 'principal'
    
    if st.session_state.page == 'principal':
        tela_principal()
    elif st.session_state.page == 'resultados':
        tela_resultados()

if __name__ == "__main__":
    main()
