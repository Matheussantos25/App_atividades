import streamlit as st
import csv
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, time, date, timedelta
import seaborn as sns
from PIL import Image

# Configurar estilo do Matplotlib
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
        df_exercicios = pd.read_csv(arquivo_csv, encoding='utf-8')
        df_tarefas = pd.read_csv(arquivo_tarefas, encoding='utf-8')
    except FileNotFoundError:
        df_exercicios = pd.DataFrame(columns=cabecalho_exercicios)
        df_tarefas = pd.DataFrame(columns=cabecalho_tarefas)  # Correção aqui
        df_exercicios.to_csv(arquivo_csv, index=False)
        df_tarefas.to_csv(arquivo_tarefas, index=False)
    return df_exercicios, df_tarefas

def salvar_dados(df_exercicios, df_tarefas):
    df_exercicios.to_csv(arquivo_csv, index=False)
    df_tarefas.to_csv(arquivo_tarefas, index=False)

# Mapeamento de ranks com imagens maiores
ranks = [
    ('Ferro', 0.0, 0.2, 'imagens/ferro.png'),
    ('Bronze', 0.2, 0.4, 'imagens/bronze.png'),
    ('Prata', 0.4, 0.6, 'imagens/prata.png'),
    ('Ouro', 0.6, 0.8, 'imagens/ouro.png'),
    ('Platina', 0.8, 0.9, 'imagens/platina.png'),
    ('Esmeralda', 0.9, 0.95, 'imagens/esmeralda.png'),
    ('Grão Mestre', 0.95, 0.99, 'imagens/grao_mestre.png'),
    ('Challenger', 0.99, 1.0, 'imagens/challenger.png'),
]

def get_rank(progresso):
    for rank, lower, upper, img in ranks:
        if lower <= progresso < upper:
            return rank, img
    return 'Challenger', 'imagens/challenger.png'

# Função para gerar desafios diários com múltiplos exercícios
def gerar_desafios_diarios(df_exercicios, df_tarefas):
    hoje = date.today()
    tarefa_existente = df_tarefas[df_tarefas['Data da Tarefa'] == hoje.strftime('%d/%m/%Y')]
    
    if tarefa_existente.empty:
        # Defina os exercícios disponíveis
        exercicios_disponiveis = ['Corrida', 'Flexões', 'Agachamentos', 'Abdominais']

        # Defina desafios para o dia (exemplo: 2 exercícios por dia)
        desafios = [
            {
                'Tipo de Exercício': 'Corrida',
                'Objetivo Repetições': 20,  # Exemplo de repetições
                'Objetivo Séries': 3,
                'Penalidade': 5
            },
            {
                'Tipo de Exercício': 'Flexões',
                'Objetivo Repetições': 15,
                'Objetivo Séries': 4,
                'Penalidade': 3
            }
        ]

        for desafio in desafios:
            nova_tarefa = {
                'Data da Tarefa': hoje.strftime('%d/%m/%Y'),
                'Tipo de Exercício': desafio['Tipo de Exercício'],
                'Objetivo Repetições': desafio['Objetivo Repetições'],
                'Objetivo Séries': desafio['Objetivo Séries'],
                'Status da Tarefa': 'Pendente',
                'Penalidade': desafio['Penalidade']
            }
            df_tarefas = pd.concat([df_tarefas, pd.DataFrame([nova_tarefa])], ignore_index=True)
        
        salvar_dados(df_exercicios, df_tarefas)
        st.info("Novos desafios diários adicionados!")
    
    return df_tarefas

# Função para verificar progresso por exercício
def verificar_progresso(df_exercicios, df_tarefas):
    hoje = date.today().strftime('%d/%m/%Y')
    tarefas_hoje = df_tarefas[df_tarefas['Data da Tarefa'] == hoje]
    
    for index, tarefa in tarefas_hoje.iterrows():
        exercicio = tarefa['Tipo de Exercício']
        objetivo_reps = tarefa['Objetivo Repetições']
        reps_realizadas = df_exercicios[
            (df_exercicios['Dia'] == hoje) & 
            (df_exercicios['Tipo de Exercício'] == exercicio)
        ]['Repetições Totais'].sum()
        reps_faltantes = max(objetivo_reps - reps_realizadas, 0)
        progresso = min(reps_realizadas / objetivo_reps, 1.0)

        rank, img_path = get_rank(progresso)

        st.subheader(f"Progresso do Desafio: {exercicio}")
        col1, col2 = st.columns([3, 1])
        with col1:
            progress_bar = st.progress(progresso)
            st.write(f"{reps_realizadas} de {objetivo_reps} repetições realizadas.")
            st.write(f"Faltam {reps_faltantes} repetições para completar o desafio.")
        with col2:
            try:
                rank_image = Image.open(img_path)
                st.image(rank_image, width=300)  # Aumentado significativamente o tamanho aqui
                st.write(f"**{rank}**")
            except FileNotFoundError:
                st.write(f"**{rank}**")
            except Exception as e:
                st.write(f"Erro ao carregar a imagem: {e}")
        
        if progresso >= 1.0:
            st.success("Desafio cumprido! Você alcançou o flow!")
            df_tarefas.at[index, 'Status da Tarefa'] = 'Concluída'
        else:
            st.warning("Desafio não cumprido. Penalidade aplicada.")
            penalidade = tarefa['Penalidade']
            aplicar_penalidade(penalidade)
            df_tarefas.at[index, 'Status da Tarefa'] = 'Falhou'
    
    salvar_dados(df_exercicios, df_tarefas)

def aplicar_penalidade(valor):
    st.error(f"Você perdeu {valor} pontos por não cumprir o desafio.")

# Integração no app1.py
df_exercicios, df_tarefas = load_data()

# Gerar desafios diários
df_tarefas = gerar_desafios_diarios(df_exercicios, df_tarefas)

# Verificar progresso após adicionar exercício
if st.button("Verificar Progresso do Dia"):
    verificar_progresso(df_exercicios, df_tarefas)

# Mostrar desafios com barra de progresso e ranks
hoje = date.today().strftime('%d/%m/%Y')
tarefas_hoje = df_tarefas[df_tarefas['Data da Tarefa'] == hoje]

if not tarefas_hoje.empty:
    for index, tarefa in tarefas_hoje.iterrows():
        exercicio = tarefa['Tipo de Exercício']
        objetivo_reps = tarefa['Objetivo Repetições']
        reps_realizadas = df_exercicios[
            (df_exercicios['Dia'] == hoje) & 
            (df_exercicios['Tipo de Exercício'] == exercicio)
        ]['Repetições Totais'].sum()
        reps_faltantes = max(objetivo_reps - reps_realizadas, 0)
        progresso = min(reps_realizadas / objetivo_reps, 1.0)

        rank, img_path = get_rank(progresso)

        st.subheader(f"Progresso do Desafio: {exercicio}")
        col1, col2 = st.columns([3, 1])
        with col1:
            progress_bar = st.progress(progresso)
            st.write(f"{reps_realizadas} de {objetivo_reps} repetições realizadas.")
            st.write(f"Faltam {reps_faltantes} repetições para completar o desafio.")
        with col2:
            try:
                rank_image = Image.open(img_path)
                st.image(rank_image, width=300)  # Aumentado significativamente o tamanho aqui
                st.write(f"**{rank}**")
            except FileNotFoundError:
                st.write(f"**{rank}**")
            except Exception as e:
                st.write(f"Erro ao carregar a imagem: {e}")
        
        if progresso >= 1.0:
            st.success("Desafio cumprido! Você alcançou o flow!")
        else:
            st.warning("Continue se esforçando para cumprir o desafio!")
else:
    st.info("Nenhum desafio para hoje.")

# Função para adicionar um novo registro de exercício
def adicionar_exercicio(data_exercicio, tipo_exercicio, repeticoes_totais, numero_series, duracao, horario, intervalo_series):
    dia_formatado = data_exercicio.strftime('%d/%m/%Y')

    # Adicionar os dados no arquivo CSV
    with open(arquivo_csv, 'a', newline='', encoding='utf-8') as arquivo:
        escritor_csv = csv.writer(arquivo)
        if arquivo.tell() == 0:
            escritor_csv.writerow(cabecalho_exercicios)
        escritor_csv.writerow([dia_formatado, tipo_exercicio, repeticoes_totais, numero_series, duracao, horario, intervalo_series])

    st.success("Registro adicionado com sucesso!")

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

# Função para carregar e processar dados
def carregar_dados():
    try:
        df = pd.read_csv(arquivo_csv, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(arquivo_csv, encoding='ISO-8859-1')
    
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
            x = df_agrupado['Dia'].dt.strftime('Mês %m')
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
            df_agrupado = df_filtrado.resample('6M', on='Dia')[colunas_numericas].sum().reset_index()
            x = df_agrupado['Dia']
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
st.title("Registro de Exercícios Diários")

# Layout em colunas para melhor organização
col1, col2 = st.columns(2)

with col1:
    data_exercicio = st.date_input("Escolha a data", datetime.now())

with col2:
    tipo_exercicio = st.selectbox("Escolha o tipo de exercício:", 
                                   ['Flexão', 'Barra Sem Peso', 'Barra Com Peso', 'Agachamento', 'Pular Corda', 'Andar de Bike', 'Prancha'])

repeticoes_totais = st.text_input("Digite o número total de repetições:")
numero_series = st.text_input("Digite o número de séries:")
duracao = st.text_input("Digite a duração de cada série (em minutos): (Se não se aplica, deixe em branco)")
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

# Carregar dados
df = carregar_dados()

# Selecionar o tipo de exercício e o período para visualização
if not df.empty:
    st.header("Visualização do Progresso")
    
    col3, col4 = st.columns(2)

    with col3:
        exercicio_selecionado = st.selectbox("Escolha o tipo de exercício para ver o progresso:", df['Tipo de Exercício'].unique())

    with col4:
        periodo_selecionado = st.selectbox("Escolha o período:", ['Diário', 'Semana', 'Mês', 'Semestre'])

    st.subheader("Selecione o intervalo de datas")

    data_min = df['Dia'].min().date()
    data_max = df['Dia'].max().date()

    data_inicio = st.date_input("Data de Início", data_min, min_value=data_min, max_value=data_max)
    data_fim = st.date_input("Data de Fim", data_max, min_value=data_min, max_value=data_max)

    if st.button("Mostrar Gráficos e Métricas"):
        if data_inicio > data_fim:
            st.error("A data de início deve ser anterior à data de fim.")
        else:
            # Converter para datetime
            data_inicio_dt = pd.to_datetime(data_inicio)
            data_fim_dt = pd.to_datetime(data_fim)

            # Calcular métricas
            total_repeticoes, media_repeticoes, dia_mais_repeticoes, repeticoes_dia_mais = calcular_metricas(df, exercicio_selecionado, data_inicio_dt, data_fim_dt)

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
            plotar_progresso(df, exercicio_selecionado, periodo_selecionado, data_inicio_dt, data_fim_dt)

            st.subheader("Gráfico de Pizza dos Períodos do Dia")
            plotar_pizza_periodo_dia(df, exercicio_selecionado, data_inicio_dt, data_fim_dt)

            st.subheader("Top 5 Horários Mais Usados")
            plotar_top5_horarios(df, exercicio_selecionado, data_inicio_dt, data_fim_dt)

else:
    st.warning("Nenhum dado disponível. Adicione exercícios para visualizar os gráficos.")
