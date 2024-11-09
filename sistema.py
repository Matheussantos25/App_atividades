import streamlit as st
import csv
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, time, date, timedelta
import seaborn as sns

print(plt.style.available)
# Configurar estilo do Matplotlib para evitar problemas com Streamlit
plt.style.use('ggplot')

# Nome dos arquivos CSV
arquivo_csv = 'exercicios_diarios.csv'
arquivo_tarefas = 'tarefas_diarias.csv'

# Cabeçalhos dos CSVs
cabecalho_exercicios = ['Dia', 'Tipo de Exercício', 'Repetições Totais', 'Número de Séries', 'Duração (min)', 'Horário', 'Intervalo entre Séries (min)']
cabecalho_tarefas = ['Data da Tarefa', 'Tipo de Exercício', 'Objetivo Repetições', 'Objetivo Séries', 'Status da Tarefa', 'Penalidade']

@st.cache_data
def load_data():
    try:
        df_exercicios = pd.read_csv('exercicios_diarios.csv')
        df_tarefas = pd.read_csv('tarefas_diarias.csv')
    except FileNotFoundError:
        df_exercicios = pd.DataFrame(columns=cabecalho_exercicios)
        df_tarefas = pd.DataFrame(columns=cabecalho_tarefas)
        df_exercicios.to_csv('exercicios_diarios.csv', index=False)
        df_tarefas.to_csv('tarefas_diarias.csv', index=False)
    return df_exercicios, df_tarefas

# Função para adicionar um novo registro de exercício
def adicionar_exercicio(data_exercicio, tipo_exercicio, repeticoes_totais, numero_series, duracao, horario, intervalo_series):
    df_exercicios, _ = load_data()
    novo_exercicio = pd.DataFrame({
        'Dia': [data_exercicio.strftime('%d/%m/%Y')],
        'Tipo de Exercício': [tipo_exercicio],
        'Repetições Totais': [repeticoes_totais],
        'Número de Séries': [numero_series],
        'Duração (min)': [duracao],
        'Horário': [horario],
        'Intervalo entre Séries (min)': [intervalo_series]
    })
    df_exercicios = pd.concat([df_exercicios, novo_exercicio], ignore_index=True)
    df_exercicios.to_csv('exercicios_diarios.csv', index=False)
    return df_exercicios

# Função para categorizar o período do dia
def categorizar_periodo_dia(horario):
    if isinstance(horario, time):
        if time(5, 0) <= horario < time(12, 0):
            return 'Manhã'
        elif time(12, 0) <= horario < time(18, 0):
            return 'Tarde'
        elif time(18, 0) <= horario <= time(23, 59):
            return 'Noite'
        else:
            return 'Madrugada'
    return 'Madrugada'

# Função para carregar e processar dados dos exercícios
def carregar_dados_exercicios():
    try:
        df = pd.read_csv(arquivo_csv, encoding='utf-8')
    except (UnicodeDecodeError, FileNotFoundError):
        df = pd.DataFrame(columns=cabecalho_exercicios)
        return df

    # Converter a coluna 'Dia' para datetime
    df['Dia'] = pd.to_datetime(df['Dia'], format='%d/%m/%Y')

    # Converter a coluna 'Horário' para datetime.time
    df['Horário'] = pd.to_datetime(df['Horário'], format='%H:%M', errors='coerce').dt.time

    # Adicionar a coluna 'Período do Dia'
    df['Período do Dia'] = df['Horário'].apply(categorizar_periodo_dia)

    # Converter colunas numéricas para tipos apropriados
    colunas_numericas = ['Repetições Totais', 'Número de Séries', 'Duração (min)', 'Intervalo entre Séries (min)']
    for coluna in colunas_numericas:
        df[coluna] = pd.to_numeric(df[coluna], errors='coerce').fillna(0)

    return df

# Função para carregar e processar dados das tarefas
def carregar_dados_tarefas():
    try:
        df = pd.read_csv(arquivo_tarefas, encoding='utf-8')
    except (UnicodeDecodeError, FileNotFoundError):
        df = pd.DataFrame(columns=cabecalho_tarefas)
    return df

# Função para gerar tarefas diárias
def gerar_tarefas_diarias(df_exercicios, df_tarefas):
    # Supondo que novas_tarefas seja um DataFrame
    novas_tarefas = pd.DataFrame({
        'Data da Tarefa': [date.today()],
        'Tipo de Exercício': ['Corrida'],
        'Objetivo Repetições': [10],
        'Objetivo Séries': [3],
        'Status da Tarefa': ['Pendente'],
        'Penalidade': [0]
    })
    
    df_tarefas = pd.concat([df_tarefas, novas_tarefas], ignore_index=True)
    return df_tarefas

# Função para aplicar penalidades
def aplicar_penalidades(df_tarefas):
    data_ontem = (date.today() - timedelta(days=1)).strftime('%d/%m/%Y')
    tarefas_nao_concluidas = df_tarefas[(df_tarefas['Data da Tarefa'] == data_ontem) & (df_tarefas['Status da Tarefa'] != 'Concluída')]

    if not tarefas_nao_concluidas.empty:
        for index, tarefa in tarefas_nao_concluidas.iterrows():
            # Aplicar penalidade (por exemplo, aumentar o objetivo das próximas tarefas)
            df_tarefas.at[index, 'Penalidade'] = 'Objetivo aumentado devido à não conclusão'

    df_tarefas.to_csv(arquivo_tarefas, index=False)
    return df_tarefas

# Função para calcular métricas do período selecionado
def calcular_metricas(df, tipo_exercicio, data_inicio, data_fim):
    df_filtrado = df[(df['Tipo de Exercício'] == tipo_exercicio) & 
                     (df['Dia'] >= data_inicio) & (df['Dia'] <= data_fim)]
    
    if not df_filtrado.empty:
        total_repeticoes = df_filtrado['Repetições Totais'].sum()
        media_repeticoes = df_filtrado['Repetições Totais'].mean()
        dia_mais_repeticoes = df_filtrado.loc[df_filtrado['Repetições Totais'].idxmax()]['Dia']
        repeticoes_dia_mais = df_filtrado['Repetições Totais'].max()
        
        return total_repeticoes, media_repeticoes, dia_mais_repeticoes, repeticoes_dia_mais
    else:
        return 0, 0, None, 0

# Função para plotar gráfico de progresso com base na data
def plotar_progresso(df, tipo_exercicio, periodo, data_inicio, data_fim):
    if not df.empty:
        df_filtrado = df[df['Tipo de Exercício'] == tipo_exercicio]
        df_filtrado = df_filtrado[(df_filtrado['Dia'] >= data_inicio) & (df_filtrado['Dia'] <= data_fim)]

        if df_filtrado.empty:
            st.warning("Nenhum dado disponível para o período selecionado.")
            return

        # Selecionar apenas colunas numéricas para soma
        colunas_numericas = ['Repetições Totais', 'Número de Séries', 'Duração (min)', 'Intervalo entre Séries (min)']
        
        if periodo == 'Diário':
            df_agrupado = df_filtrado.groupby('Dia')[colunas_numericas].sum().reset_index()
            x = df_agrupado['Dia']
            xlabel = 'Data'
            plt.figure(figsize=(12, 6))
            plt.plot(x, df_agrupado['Repetições Totais'], marker='o', linestyle='-', color='b')
            plt.title(f"Progresso de {tipo_exercicio} por {periodo}")
            plt.xlabel(xlabel)
            plt.ylabel("Repetições Totais")
            plt.grid(True)
            plt.tight_layout()
        elif periodo == 'Semana':
            df_agrupado = df_filtrado.resample('W-MON', on='Dia')[colunas_numericas].sum().reset_index()
            x = df_agrupado['Dia'].dt.strftime('Semana %U')
            xlabel = 'Semana'
            plt.figure(figsize=(12, 6))
            plt.bar(x, df_agrupado['Repetições Totais'], color='skyblue')
            for i, v in enumerate(df_agrupado['Repetições Totais']):
                plt.text(i, v + 5, str(v), ha='center', va='bottom')
            plt.title(f"Progresso de {tipo_exercicio} por {periodo}")
            plt.xlabel(xlabel)
            plt.ylabel("Repetições Totais")
            plt.grid(axis='y')
            plt.tight_layout()
        elif periodo == 'Mês':
            df_agrupado = df_filtrado.resample('M', on='Dia')[colunas_numericas].sum().reset_index()
            x = df_agrupado['Dia'].dt.strftime('%m/%Y')
            xlabel = 'Mês'
            plt.figure(figsize=(12, 6))
            plt.bar(x, df_agrupado['Repetições Totais'], color='skyblue')
            for i, v in enumerate(df_agrupado['Repetições Totais']):
                plt.text(i, v + 5, str(v), ha='center', va='bottom')
            plt.title(f"Progresso de {tipo_exercicio} por {periodo}")
            plt.xlabel(xlabel)
            plt.ylabel("Repetições Totais")
            plt.grid(axis='y')
            plt.tight_layout()
        elif periodo == 'Semestre':
            df_filtrado['Semestre'] = df_filtrado['Dia'].dt.to_period('6M')
            df_agrupado = df_filtrado.groupby('Semestre')[colunas_numericas].sum().reset_index()
            x = df_agrupado['Semestre'].astype(str)
            xlabel = 'Semestre'
            plt.figure(figsize=(12, 6))
            plt.bar(x, df_agrupado['Repetições Totais'], color='skyblue')
            for i, v in enumerate(df_agrupado['Repetições Totais']):
                plt.text(i, v + 5, str(v), ha='center', va='bottom')
            plt.title(f"Progresso de {tipo_exercicio} por {periodo}")
            plt.xlabel(xlabel)
            plt.ylabel("Repetições Totais")
            plt.grid(axis='y')
            plt.tight_layout()
        st.pyplot(plt)
    else:
        st.warning("Nenhum dado disponível para visualização.")

# Função para plotar gráfico de pizza de distribuição dos horários
def plotar_pizza_periodo_dia(df, tipo_exercicio, data_inicio, data_fim):
    if not df.empty:
        df_filtrado = df[(df['Tipo de Exercício'] == tipo_exercicio) & 
                         (df['Dia'] >= data_inicio) & (df['Dia'] <= data_fim)]
        if df_filtrado.empty:
            st.warning("Nenhum dado disponível para o período selecionado.")
            return

        # Contar os períodos do dia
        periodo_contagem = df_filtrado['Período do Dia'].value_counts()

        # Plotar gráfico de pizza
        plt.figure(figsize=(8, 8))
        plt.pie(periodo_contagem, labels=periodo_contagem.index, autopct='%1.1f%%', startangle=90, colors=['#FFA07A', '#20B2AA', '#9370DB', '#FF6347'])
        plt.title(f"Distribuição dos Períodos do Dia para {tipo_exercicio}")
        plt.tight_layout()
        st.pyplot(plt)
    else:
        st.warning("Nenhum dado disponível para visualização.")

# Função para plotar o top 5 horários mais usados com base na faixa de hora
def plotar_top5_horarios(df, tipo_exercicio, data_inicio, data_fim):
    if not df.empty:
        df_filtrado = df[(df['Tipo de Exercício'] == tipo_exercicio) & 
                         (df['Dia'] >= data_inicio) & (df['Dia'] <= data_fim)]
        if df_filtrado.empty:
            st.warning("Nenhum dado disponível para o período selecionado.")
            return

        # Extrair a faixa de hora e contar as ocorrências
        df_filtrado['Faixa de Hora'] = df_filtrado['Horário'].apply(lambda x: x.hour if pd.notnull(x) else None)
        top5_horarios = df_filtrado['Faixa de Hora'].value_counts().nlargest(5)

        if not top5_horarios.empty:
            # Plotar gráfico de barras
            plt.figure(figsize=(10, 6))
            plt.bar(top5_horarios.index, top5_horarios.values, color='skyblue')
            plt.xlabel('Hora do Dia')
            plt.ylabel('Número de Exercícios')
            plt.title(f'Top 5 Horários Mais Usados para {tipo_exercicio}')
            plt.xticks(top5_horarios.index)
            plt.tight_layout()
            st.pyplot(plt)
        else:
            st.warning("Nenhum dado disponível para o Top 5 horários.")
    else:
        st.warning("Nenhum dado disponível para visualização.")

# Interface do usuário
st.title("Registro de Exercícios Diários e Gamificação")

# Carregar dados
df_exercicios = carregar_dados_exercicios()
df_tarefas = carregar_dados_tarefas()
df_tarefas = aplicar_penalidades(df_tarefas)
df_tarefas = gerar_tarefas_diarias(df_exercicios, df_tarefas)

# Seção de Tarefas Diárias
st.header("Tarefas Diárias")

# Filtrar tarefas do dia atual
data_hoje_str = date.today().strftime('%d/%m/%Y')
tarefas_hoje = df_tarefas[df_tarefas['Data da Tarefa'] == data_hoje_str]

if not tarefas_hoje.empty:
    for index, tarefa in tarefas_hoje.iterrows():
        st.subheader(f"Exercício: {tarefa['Tipo de Exercício']}")
        st.write(f"Objetivo de Repetições: {tarefa['Objetivo Repetições']}")
        st.write(f"Objetivo de Séries: {tarefa['Objetivo Séries']}")
        if tarefa['Penalidade']:
            st.warning(f"Penalidade: {tarefa['Penalidade']}")
        if tarefa['Status da Tarefa'] == 'Concluída':
            st.success("Tarefa concluída!")
        else:
            if st.button(f"Marcar como concluída - {tarefa['Tipo de Exercício']}", key=index):
                df_tarefas.at[index, 'Status da Tarefa'] = 'Concluída'
                df_tarefas.to_csv(arquivo_tarefas, index=False)
                st.success("Tarefa marcada como concluída!")
                st.experimental_rerun()  # Atualiza a interface
else:
    st.write("Nenhuma tarefa para hoje.")

# Seção para adicionar exercícios realizados
st.header("Adicionar Exercício Realizado")

# Layout em colunas para melhor organização
col1, col2 = st.columns(2)

with col1:
    data_exercicio = st.date_input("Escolha a data", datetime.now())

with col2:
    tipo_exercicio = st.selectbox("Escolha o tipo de exercício:", 
                                   ['Flexão', 'Barra Sem Peso', 'Barra Com Peso', 'Agachamento', 'Pular Corda', 'Andar de Bike', 'Prancha'])

repeticoes_totais = st.text_input("Digite o número total de repetições:")
numero_series = st.text_input("Digite o número de séries:")
duracao = st.text_input("Digite a duração total (em minutos): (Se não se aplica, deixe em branco)")
horario = st.text_input("Digite o horário do exercício (HH:MM):")
intervalo_series = st.text_input("Digite o tempo de intervalo entre as séries (em minutos):")

if st.button("Adicionar Exercício"):
    if horario:
        try:
            datetime.strptime(horario, '%H:%M')
        except ValueError:
            st.error("Formato de horário inválido. Use HH:MM.")
        else:
            adicionar_exercicio(data_exercicio, tipo_exercicio, repeticoes_totais, numero_series, duracao, horario, intervalo_series)
    else:
        adicionar_exercicio(data_exercicio, tipo_exercicio, repeticoes_totais, numero_series, duracao, horario, intervalo_series)
    st.experimental_rerun()  # Atualiza a interface

# Atualizar dados após adicionar novo exercício
df_exercicios = carregar_dados_exercicios()

# Seção de Visualização do Progresso
if not df_exercicios.empty:
    st.header("Visualização do Progresso")

    col3, col4 = st.columns(2)

    with col3:
        exercicio_selecionado = st.selectbox("Escolha o tipo de exercício para ver o progresso:", df_exercicios['Tipo de Exercício'].unique())

    with col4:
        periodo_selecionado = st.selectbox("Escolha o período:", ['Diário', 'Semana', 'Mês', 'Semestre'])

    st.subheader("Selecione o intervalo de datas")

    data_min = df_exercicios['Dia'].min().date()
    data_max = df_exercicios['Dia'].max().date()

    data_inicio = st.date_input("Data de Início", data_min, min_value=data_min, max_value=data_max, key='data_inicio')
    data_fim = st.date_input("Data de Fim", data_max, min_value=data_min, max_value=data_max, key='data_fim')

    if st.button("Mostrar Gráficos e Métricas"):
        if data_inicio > data_fim:
            st.error("A data de início deve ser anterior à data de fim.")
        else:
            # Converter para datetime
            data_inicio_dt = pd.to_datetime(data_inicio)
            data_fim_dt = pd.to_datetime(data_fim)

            # Calcular métricas
            total_repeticoes, media_repeticoes, dia_mais_repeticoes, repeticoes_dia_mais = calcular_metricas(df_exercicios, exercicio_selecionado, data_inicio_dt, data_fim_dt)

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
            plotar_progresso(df_exercicios, exercicio_selecionado, periodo_selecionado, data_inicio_dt, data_fim_dt)

            st.subheader("Gráfico de Pizza dos Períodos do Dia")
            plotar_pizza_periodo_dia(df_exercicios, exercicio_selecionado, data_inicio_dt, data_fim_dt)

            st.subheader("Top 5 Horários Mais Usados")
            plotar_top5_horarios(df_exercicios, exercicio_selecionado, data_inicio_dt, data_fim_dt)

    # Seção de Progresso das Tarefas
    st.header("Progresso das Tarefas")

    # Calcular métricas das tarefas
    total_tarefas = len(df_tarefas)
    tarefas_concluidas = len(df_tarefas[df_tarefas['Status da Tarefa'] == 'Concluída'])
    taxa_conclusao = (tarefas_concluidas / total_tarefas) * 100 if total_tarefas > 0 else 0

    st.write(f"**Total de Tarefas:** {total_tarefas}")
    st.write(f"**Tarefas Concluídas:** {tarefas_concluidas}")
    st.write(f"**Taxa de Conclusão:** {taxa_conclusao:.2f}%")

    # Gráfico de barras das tarefas concluídas vs. não concluídas
    status_counts = df_tarefas['Status da Tarefa'].value_counts()
    plt.figure(figsize=(6, 4))
    plt.bar(status_counts.index, status_counts.values, color=['green', 'red'])
    plt.title("Status das Tarefas")
    plt.xlabel("Status")
    plt.ylabel("Quantidade")
    st.pyplot(plt)

else:
    st.warning("Nenhum dado disponível. Adicione exercícios para visualizar os gráficos.")
