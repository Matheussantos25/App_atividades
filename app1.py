import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, date, timedelta
from PIL import Image
import time as tm

# Configurar estilo do Matplotlib
plt.style.use('ggplot')

# Nome dos arquivos CSV
arquivo_csv = 'exercicios_diarios.csv'
arquivo_tarefas = 'tarefas_diarias.csv'

# Cabeçalhos dos CSVs
cabecalho_exercicios = [
    'Dia',
    'Tipo de Exercício',
    'Repetições Totais',
    'Número de Séries',
    'Duração (min)',
    'Horário',
    'Intervalo entre Séries (min)'
]

cabecalho_tarefas = [
    'Data da Tarefa',
    'Tipo de Exercício',
    'Objetivo Repetições',
    'Objetivo Séries',
    'Intervalo entre Séries (min)',
    'Status da Tarefa',
    'Penalidade'
]

@st.cache_data
def load_data():
    try:
        df_exercicios = pd.read_csv(arquivo_csv, encoding='utf-8')
        df_tarefas = pd.read_csv(arquivo_tarefas, encoding='utf-8')
    except FileNotFoundError:
        df_exercicios = pd.DataFrame(columns=cabecalho_exercicios)
        df_tarefas = pd.DataFrame(columns=cabecalho_tarefas)
        df_exercicios.to_csv(arquivo_csv, index=False)
        df_tarefas.to_csv(arquivo_tarefas, index=False)
    return df_exercicios, df_tarefas

def salvar_dados(df_exercicios, df_tarefas):
    df_exercicios.to_csv(arquivo_csv, index=False)
    df_tarefas.to_csv(arquivo_tarefas, index=False)

# Função para determinar o tipo de exercício do dia
def tipo_exercicio_do_dia():
    dia = date.today().day
    if dia % 2 == 0:
        return 'agachamento'  # Ajustado para singular e minúsculas
    else:
        return 'flexões'  # Ajustado para minúsculas

# Função para gerar desafios diários
def gerar_desafios_diarios(df_exercicios, df_tarefas):
    hoje = date.today()
    tarefa_existente = df_tarefas[df_tarefas['Data da Tarefa'] == hoje.strftime('%Y-%m-%d')]
    if tarefa_existente.empty:
        tipo_exercicio = tipo_exercicio_do_dia()
        if tipo_exercicio == 'flexões':
            desafios = [
                {
                    'Tipo de Exercício': 'flexões',
                    'Objetivo Repetições': 20,
                    'Objetivo Séries': 4,
                    'Intervalo entre Séries (min)': 60,
                    'Penalidade': 3
                }
            ]
        else:  # tipo_exercicio == 'agachamento'
            desafios = [
                {
                    'Tipo de Exercício': 'agachamento',
                    'Objetivo Repetições': 25,
                    'Objetivo Séries': 4,
                    'Intervalo entre Séries (min)': 60,
                    'Penalidade': 4
                }
            ]
        for desafio in desafios:
            nova_tarefa = {
                'Data da Tarefa': hoje.strftime('%Y-%m-%d'),  # Ajustado para '%Y-%m-%d'
                'Tipo de Exercício': desafio['Tipo de Exercício'],
                'Objetivo Repetições': desafio['Objetivo Repetições'],
                'Objetivo Séries': desafio['Objetivo Séries'],
                'Intervalo entre Séries (min)': desafio['Intervalo entre Séries (min)'],
                'Status da Tarefa': 'Pendente',
                'Penalidade': desafio['Penalidade']
            }
            df_tarefas = pd.concat([df_tarefas, pd.DataFrame([nova_tarefa])], ignore_index=True)
        salvar_dados(df_exercicios, df_tarefas)
        st.info("Novo desafio diário adicionado!")
    return df_tarefas

def aplicar_penalidade(valor):
    st.error(f"Você perdeu {valor} pontos por não cumprir o desafio.")

def iniciar_temporizador(segundos):
    temporizador_placeholder = st.empty()
    for i in range(segundos, 0, -1):
        minutos, segundos_restantes = divmod(i, 60)
        temporizador_placeholder.markdown(f"### Tempo restante: {minutos}:{segundos_restantes:02d}")
        tm.sleep(1)
    temporizador_placeholder.markdown("### Tempo esgotado!")
    st.balloons()

# Mapeamento de ranks com imagens
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

# Funções de plotagem
def plotar_progresso(df, exercicio, periodo_selecionado, data_inicio, data_fim):
    df_filtrado = df[(df['Tipo de Exercício'] == exercicio) & (df['Dia'] >= data_inicio) & (df['Dia'] <= data_fim)]
    if df_filtrado.empty:
        st.write("Sem dados para o período selecionado.")
        return
    progresso_diario = df_filtrado.groupby('Dia')['Repetições Totais'].sum().reset_index()
    plt.figure(figsize=(10, 5))
    plt.plot(progresso_diario['Dia'], progresso_diario['Repetições Totais'], marker='o')
    plt.title(f'Progresso de Repetições Totais para {exercicio}')
    plt.xlabel('Data')
    plt.ylabel('Repetições Totais')
    plt.xticks(rotation=45)
    st.pyplot(plt)

def plotar_pizza_periodo_dia(df, exercicio, data_inicio, data_fim):
    df_filtrado = df[(df['Tipo de Exercício'] == exercicio) & (df['Dia'] >= data_inicio) & (df['Dia'] <= data_fim)]
    if df_filtrado.empty:
        st.write("Sem dados para o período selecionado.")
        return
    def classificar_periodo(horario):
        hora = int(horario.split(':')[0])
        if 5 <= hora < 12:
            return 'Manhã'
        elif 12 <= hora < 18:
            return 'Tarde'
        else:
            return 'Noite'
    df_filtrado['Período do Dia'] = df_filtrado['Horário'].apply(classificar_periodo)
    distribuicao = df_filtrado['Período do Dia'].value_counts()
    plt.figure(figsize=(6, 6))
    plt.pie(distribuicao, labels=distribuicao.index, autopct='%1.1f%%', startangle=140)
    plt.axis('equal')
    st.pyplot(plt)

def plotar_top5_horarios(df, exercicio, data_inicio, data_fim):
    df_filtrado = df[(df['Tipo de Exercício'] == exercicio) & (df['Dia'] >= data_inicio) & (df['Dia'] <= data_fim)]
    if df_filtrado.empty:
        st.write("Sem dados para o período selecionado.")
        return
    horarios = df_filtrado['Horário'].value_counts().head(5)
    plt.figure(figsize=(8, 4))
    sns.barplot(x=horarios.index, y=horarios.values)
    plt.title(f'Top 5 Horários Mais Usados para {exercicio}')
    plt.xlabel('Horário')
    plt.ylabel('Frequência')
    st.pyplot(plt)

def calcular_metricas(df, exercicio, data_inicio, data_fim):
    df_filtrado = df[(df['Tipo de Exercício'] == exercicio) & (df['Dia'] >= data_inicio) & (df['Dia'] <= data_fim)]
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
df_exercicios, df_tarefas = load_data()

# Padronizar nomes e datas
df_exercicios['Dia'] = pd.to_datetime(df_exercicios['Dia'], format='%Y-%m-%d', errors='coerce')  # Ajustado o formato da data
df_tarefas['Data da Tarefa'] = pd.to_datetime(df_tarefas['Data da Tarefa'], format='%Y-%m-%d', errors='coerce')  # Ajustado o formato da data
df_exercicios['Tipo de Exercício'] = df_exercicios['Tipo de Exercício'].str.strip().str.lower()
df_tarefas['Tipo de Exercício'] = df_tarefas['Tipo de Exercício'].str.strip().str.lower()

# Remover registros com datas inválidas
df_exercicios = df_exercicios.dropna(subset=['Dia'])
df_tarefas = df_tarefas.dropna(subset=['Data da Tarefa'])

# Gerar desafios diários
df_tarefas = gerar_desafios_diarios(df_exercicios, df_tarefas)

# Função para verificar progresso
def verificar_progresso(df_exercicios, df_tarefas):
    hoje = pd.to_datetime(date.today())
    tarefas_hoje = df_tarefas[df_tarefas['Data da Tarefa'] == hoje]
    if tarefas_hoje.empty:
        st.info("Nenhum desafio para hoje.")
        return
    for index, tarefa in tarefas_hoje.iterrows():
        exercicio = tarefa['Tipo de Exercício']
        objetivo_reps = tarefa['Objetivo Repetições']
        df_exercicios_hoje = df_exercicios[
            (df_exercicios['Dia'] == hoje) &
            (df_exercicios['Tipo de Exercício'] == exercicio)
        ]
        reps_realizadas = df_exercicios_hoje['Repetições Totais'].sum()
        reps_faltantes = max(objetivo_reps - reps_realizadas, 0)
        progresso = min(reps_realizadas / objetivo_reps, 1.0) if objetivo_reps > 0 else 0
        rank, img_path = get_rank(progresso)
        
        st.subheader(f"Progresso do Desafio: {exercicio.capitalize()}")
        col1, col2 = st.columns([3, 1])
        with col1:
            st.progress(progresso)
            st.write(f"{reps_realizadas} de {objetivo_reps} repetições realizadas.")
            st.write(f"Faltam {reps_faltantes} repetições para completar o desafio.")
            if reps_faltantes > 0 and tarefa['Intervalo entre Séries (min)'] > 0:
                st.write("**Iniciar Intervalo entre Séries**")
                if st.button(f"Iniciar intervalo de {tarefa['Intervalo entre Séries (min)']} segundos para {exercicio.capitalize()}", key=f"timer_{index}"):
                    iniciar_temporizador(int(tarefa['Intervalo entre Séries (min)']))
        with col2:
            try:
                rank_image = Image.open(img_path)
                st.image(rank_image, width=150)
                st.write(f"**{rank}**")
            except FileNotFoundError:
                st.write(f"**{rank}**")
            except Exception as e:
                st.write(f"Erro ao carregar a imagem: {e}")
        if progresso >= 1.0:
            st.success(f"Desafio de {exercicio.capitalize()} cumprido! Você alcançou o flow!")
            df_tarefas.at[index, 'Status da Tarefa'] = 'Concluída'
        else:
            st.warning(f"Continue se esforçando para cumprir o desafio de {exercicio.capitalize()}!")
    salvar_dados(df_exercicios, df_tarefas)

# Interface do aplicativo
st.title("Relatório Físico")

# Seção para adicionar exercícios
st.header("Adicionar Exercício")
col1, col2 = st.columns(2)
with col1:
    data_exercicio = st.date_input("Escolha a data", datetime.now(), key="data_exercicio_add")
with col2:
    tipo_exercicio = st.selectbox("Escolha o tipo de exercício:", [
        'flexões', 'agachamento', 'corrida', 'pular corda', 'andar de bike', 'prancha', 'barra sem peso', 'barra com peso'
    ], key="tipo_exercicio_add")
repeticoes_totais = st.number_input("Digite o número total de repetições:", min_value=0, step=1, key="repeticoes_totais_add")
numero_series = st.number_input("Digite o número de séries:", min_value=1, step=1, key="numero_series_add")
duracao = st.text_input("Digite a duração de cada série (em minutos): (Se não se aplica, deixe em branco)", key="duracao_add")
horario = st.text_input("Digite o horário do exercício (HH:MM):", key="horario_add")
intervalo_series = st.number_input("Digite o tempo de intervalo entre as séries (em segundos):", min_value=0, step=10, key="intervalo_series_add")

if st.button("Adicionar Exercício", key="adicionar_exercicio_btn"):
    if horario:
        try:
            datetime.strptime(horario, '%H:%M')
            nova_entrada = {
                'Dia': data_exercicio.strftime('%Y-%m-%d'),  # Ajustado para '%Y-%m-%d'
                'Tipo de Exercício': tipo_exercicio.strip().lower(),
                'Repetições Totais': repeticoes_totais,
                'Número de Séries': numero_series,
                'Duração (min)': duracao if duracao else None,
                'Horário': horario,
                'Intervalo entre Séries (min)': intervalo_series
            }
            df_exercicios = pd.concat([df_exercicios, pd.DataFrame([nova_entrada])], ignore_index=True)
            salvar_dados(df_exercicios, df_tarefas)
            st.success("Exercício adicionado com sucesso!")
            # Após adicionar um exercício, verifique o progresso
            verificar_progresso(df_exercicios, df_tarefas)
        except ValueError:
            st.error("Formato de horário inválido. Use HH:MM.")
    else:
        st.error("Por favor, insira o horário do exercício.")

# Verificar progresso automaticamente ao carregar a página
verificar_progresso(df_exercicios, df_tarefas)

# Seção para visualizar estatísticas
st.header("Estatísticas")
df = df_exercicios.copy()
if not df.empty:
    df['Dia'] = pd.to_datetime(df['Dia'])
    df = df.sort_values('Dia')
    exercicios_disponiveis = df['Tipo de Exercício'].unique()
    exercicio_selecionado = st.selectbox("Selecione o exercício:", exercicios_disponiveis)
    periodo_opcoes = ['7 dias', '14 dias', '30 dias', 'Personalizado']
    periodo_selecionado = st.selectbox("Selecione o período:", periodo_opcoes)
    if periodo_selecionado == 'Personalizado':
        col1, col2 = st.columns(2)
        with col1:
            data_inicio = st.date_input("Data de início", df['Dia'].min().date(), key="data_inicio_personalizado")
        with col2:
            data_fim = st.date_input("Data de fim", df['Dia'].max().date(), key="data_fim_personalizado")
    else:
        dias = int(periodo_selecionado.split()[0])
        data_fim = df['Dia'].max().date()
        data_inicio = data_fim - timedelta(days=dias)
    data_inicio_dt = pd.to_datetime(data_inicio)
    data_fim_dt = pd.to_datetime(data_fim)
    df_filtrado = df[(df['Tipo de Exercício'] == exercicio_selecionado) & (df['Dia'] >= data_inicio_dt) & (df['Dia'] <= data_fim_dt)]
    if not df_filtrado.empty:
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
        st.warning("Nenhum dado disponível para o período selecionado.")
else:
    st.warning("Nenhum dado disponível. Adicione exercícios para visualizar os gráficos.")

# Seção do temporizador de contagem regressiva
st.header("Temporizador de Contagem Regressiva")

# Entrada para o usuário selecionar a duração do temporizador
duracao_temporizador = st.number_input("Escolha a duração do temporizador em segundos:", min_value=1, step=1, value=30)

# Botão para iniciar o temporizador
if st.button("Iniciar Temporizador"):
    # Placeholder para exibir o temporizador
    temporizador_placeholder = st.empty()
    # Loop de contagem regressiva
    for segundos_restantes in range(int(duracao_temporizador), 0, -1):
        minutos, segundos = divmod(segundos_restantes, 60)
        temporizador_placeholder.markdown(f"## Tempo restante: {minutos}:{segundos:02d}")
        tm.sleep(1)
    # Quando o temporizador termina
    temporizador_placeholder.markdown("## O tempo acabou!")
    st.balloons()
