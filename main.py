import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, date, timedelta
import time as tm
import shutil
import os

# Configurar estilo do Matplotlib
plt.style.use('ggplot')

# Nome do arquivo CSV
arquivo_csv = 'exercicios_diarios.csv'
backup_csv = 'exercicios_diarios_backup.csv'

# Função para criar um backup dos dados
def criar_backup():
    if os.path.exists(arquivo_csv):
        shutil.copy(arquivo_csv, backup_csv)

# Carregar dados
def carregar_dados():
    try:
        df = pd.read_csv(arquivo_csv, parse_dates=['Dia'], dayfirst=True)
        df['Tipo de Exercício'] = df['Tipo de Exercício'].str.strip().str.lower()
    except FileNotFoundError:
        df = pd.DataFrame(columns=[
            'Dia',
            'Tipo de Exercício',
            'Repetições Totais',
            'Número de Séries',
            'Duração (min)',
            'Horário',
            'Intervalo entre Séries (min)'
        ])
        df.to_csv(arquivo_csv, index=False)
    return df

# Salvar dados
def salvar_dados(df):
    criar_backup()  # Criar um backup antes de salvar novos dados
    df_to_save = df.copy()
    # Converter a coluna 'Dia' para datetime, ignorando erros
    df_to_save['Dia'] = pd.to_datetime(df_to_save['Dia'], dayfirst=True, errors='coerce')
    # Remover linhas com datas inválidas
    df_to_save = df_to_save.dropna(subset=['Dia'])
    # Converter as datas para o formato desejado 'DD/MM/AAAA'
    df_to_save['Dia'] = df_to_save['Dia'].dt.strftime('%d/%m/%Y')
    df_to_save.to_csv(arquivo_csv, index=False)

# Função para adicionar exercício
def adicionar_exercicio():
    st.header("Adicionar Exercício")
    col1, col2 = st.columns(2)
    with col1:
        data_exercicio = st.date_input("Escolha a data", datetime.now())
    with col2:
        tipo_exercicio = st.selectbox("Escolha o tipo de exercício:", [
            'flexões', 'abdominal bicicleta','agachamento', 'corrida', 'pular corda', 'andar de bicicleta', 'prancha', 'barra sem peso', 'barra com peso'
        ])
    repeticoes_totais = st.number_input("Digite o número total de repetições:", min_value=0, step=1)
    numero_series = st.number_input("Digite o número de séries:", min_value=1, step=1)
    duracao = st.text_input("Digite a duração de cada série (em minutos): (Se não se aplica, deixe em branco)")
    horario = st.text_input("Digite o horário do exercício (HH:MM):")
    intervalo_series = st.number_input("Digite o tempo de intervalo entre as séries (em minutos):", min_value=0, step=10)

    if st.button("Adicionar Exercício"):
        if horario:
            try:
                datetime.strptime(horario, '%H:%M')
                nova_entrada = {
                    'Dia': data_exercicio,  # Mantém como datetime
                    'Tipo de Exercício': tipo_exercicio.strip().lower(),
                    'Repetições Totais': repeticoes_totais,
                    'Número de Séries': numero_series,
                    'Duração (min)': duracao if duracao else None,
                    'Horário': horario,
                    'Intervalo entre Séries (min)': intervalo_series
                }
                df = carregar_dados()
                df = pd.concat([df, pd.DataFrame([nova_entrada])], ignore_index=True)
                salvar_dados(df)
                st.success("Exercício adicionado com sucesso!")
            except ValueError:
                st.error("Formato de horário inválido. Use HH:MM.")
        else:
            st.error("Por favor, insira o horário do exercício.")

# Funções de plotagem
def plotar_progresso(df, exercicio, data_inicio, data_fim):
    # Filtrar os dados
    df_filtrado = df[
        (df['Tipo de Exercício'] == exercicio) &
        (df['Dia'] >= data_inicio) &
        (df['Dia'] <= data_fim)
    ]

    if df_filtrado.empty:
        st.write("Sem dados para o período selecionado.")
        return

    # Agrupar por dia e somar as repetições
    progresso_diario = df_filtrado.groupby('Dia')['Repetições Totais'].sum().reset_index()

    # Criar um intervalo de datas completo
    todas_as_datas = pd.date_range(start=data_inicio, end=data_fim)

    # Reindexar o DataFrame para incluir todas as datas, preenchendo com zero onde não há dados
    progresso_diario = progresso_diario.set_index('Dia').reindex(todas_as_datas, fill_value=0).rename_axis('Dia').reset_index()

    # Plotar o progresso
    plt.figure(figsize=(10, 5))
    plt.plot(progresso_diario['Dia'], progresso_diario['Repetições Totais'], marker='o')
    plt.title(f'Progresso de Repetições Totais para {exercicio.capitalize()}')
    plt.xlabel('Data')
    plt.ylabel('Repetições Totais')
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(plt)

def plotar_pizza_periodo_dia(df, exercicio, data_inicio, data_fim):
    df_filtrado = df[
        (df['Tipo de Exercício'] == exercicio) &
        (df['Dia'] >= data_inicio) &
        (df['Dia'] <= data_fim)
    ]
    if df_filtrado.empty:
        st.write("Sem dados para o período selecionado.")
        return
    def classificar_periodo(horario):
        try:
            hora = int(horario.split(':')[0])
            if 5 <= hora < 12:
                return 'Manhã'
            elif 12 <= hora < 18:
                return 'Tarde'
            else:
                return 'Noite'
        except:
            return 'Desconhecido'
    df_filtrado['Período do Dia'] = df_filtrado['Horário'].apply(classificar_periodo)
    distribuicao = df_filtrado['Período do Dia'].value_counts()
    plt.figure(figsize=(6, 6))
    plt.pie(distribuicao, labels=distribuicao.index, autopct='%1.1f%%', startangle=140)
    plt.axis('equal')
    st.pyplot(plt)

def plotar_top5_horarios(df, exercicio, data_inicio, data_fim):
    df_filtrado = df[
        (df['Tipo de Exercício'] == exercicio) &
        (df['Dia'] >= data_inicio) &
        (df['Dia'] <= data_fim)
    ]
    if df_filtrado.empty:
        st.write("Sem dados para o período selecionado.")
        return
    horarios = df_filtrado['Horário'].value_counts().head(5)
    plt.figure(figsize=(8, 4))
    sns.barplot(x=horarios.index, y=horarios.values)
    plt.title(f'Top 5 Horários Mais Usados para {exercicio.capitalize()}')
    plt.xlabel('Horário')
    plt.ylabel('Frequência')
    st.pyplot(plt)

def calcular_metricas(df, exercicio, data_inicio, data_fim):
    df_filtrado = df[
        (df['Tipo de Exercício'] == exercicio) &
        (df['Dia'] >= data_inicio) &
        (df['Dia'] <= data_fim)
    ]
    if df_filtrado.empty:
        return 0, 0, None, 0
    total_repeticoes = df_filtrado['Repetições Totais'].sum()
    dias_unicos = df_filtrado['Dia'].nunique()
    media_repeticoes = total_repeticoes / dias_unicos if dias_unicos else 0
    progresso_diario = df_filtrado.groupby('Dia')['Repetições Totais'].sum().reset_index()
    dia_mais_repeticoes = progresso_diario.loc[progresso_diario['Repetições Totais'].idxmax(), 'Dia']
    repeticoes_dia_mais = progresso_diario['Repetições Totais'].max()
    return total_repeticoes, media_repeticoes, dia_mais_repeticoes, repeticoes_dia_mais

# Carregar dados
df = carregar_dados()

# Interface do aplicativo
st.title("Relatório Físico")

# Seção para adicionar exercícios
adicionar_exercicio()

# Seção para visualizar estatísticas
st.header("Estatísticas")

if not df.empty:
    df['Tipo de Exercício'] = df['Tipo de Exercício'].str.strip().str.lower()
    df = df.sort_values('Dia')
    exercicios_disponiveis = df['Tipo de Exercício'].unique()
    exercicio_selecionado = st.selectbox("Selecione o exercício:", exercicios_disponiveis)
    periodo_opcoes = ['7 dias', '14 dias', '30 dias', 'Personalizado']
    periodo_selecionado = st.selectbox("Selecione o período:", periodo_opcoes)

    if periodo_selecionado == 'Personalizado':
        col1, col2 = st.columns(2)
        with col1:
            data_minima = df['Dia'].min()
            if pd.isna(data_minima):
                data_minima = datetime.today()
            data_inicio = st.date_input("Data de início", data_minima.date(), key="data_inicio_personalizado")
        with col2:
            data_maxima = df['Dia'].max()
            if pd.isna(data_maxima):
                data_maxima = datetime.today()
            data_fim = st.date_input("Data de fim", data_maxima.date(), key="data_fim_personalizado")
    else:
        dias = int(periodo_selecionado.split()[0])
        data_maxima = df['Dia'].max()
        if pd.isna(data_maxima):
            data_maxima = datetime.today()
        data_fim = data_maxima.date()
        data_inicio = data_fim - timedelta(days=dias)

    # Converter datas para datetime
    data_inicio_dt = pd.to_datetime(data_inicio)
    data_fim_dt = pd.to_datetime(data_fim)

    # Filtrar os dados
    df_filtrado = df[
        (df['Tipo de Exercício'] == exercicio_selecionado.lower()) &
        (df['Dia'] >= data_inicio_dt) &
        (df['Dia'] <= data_fim_dt)
    ]

    if not df_filtrado.empty:
        total_repeticoes, media_repeticoes, dia_mais_repeticoes, repeticoes_dia_mais = calcular_metricas(
            df, exercicio_selecionado.lower(), data_inicio_dt, data_fim_dt)
        # Mostrar métricas
        st.subheader("Métricas do Período Selecionado")
        st.write(f"**Total de Repetições:** {total_repeticoes}")
        st.write(f"**Média de Repetições por Dia:** {media_repeticoes:.2f}")
        if dia_mais_repeticoes is not None:
            st.write(f"**Dia com Mais Repetições:** {dia_mais_repeticoes.strftime('%d/%m/%Y')} com {repeticoes_dia_mais} repetições")
        else:
            st.write("**Dia com Mais Repetições:** N/A")

        # Mostrar gráficos
        st.subheader("Progresso de Repetições Totais")
        plotar_progresso(df, exercicio_selecionado.lower(), data_inicio_dt, data_fim_dt)

        st.subheader("Gráfico de Pizza dos Períodos do Dia")
        plotar_pizza_periodo_dia(df, exercicio_selecionado.lower(), data_inicio_dt, data_fim_dt)

        st.subheader("Top 5 Horários Mais Usados")
        plotar_top5_horarios(df, exercicio_selecionado.lower(), data_inicio_dt, data_fim_dt)
    else:
        st.warning("Nenhum dado disponível para o período selecionado.")
else:
    st.warning("Nenhum dado disponível. Adicione exercícios para visualizar os gráficos.")