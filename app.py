import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Cartolendários", page_icon="🎩", layout="wide")

st.title("🎩 Cartolendários")

# --- 2. CONFIGURAÇÕES DE ACESSO E DADOS ---

ARQUIVO_PADRAO = "dados_campeonato.xlsx"
try:
    SENHA_ADMIN = st.secrets["SENHA_ADMIN"]
except FileNotFoundError:
    # Caso esteja rodando localmente sem configurar os secrets
    SENHA_ADMIN = "admin_local"

st.sidebar.header("⚙️ Filtros")

# --- LÓGICA DE UPLOAD OCULTO (MODO ADMIN) ---
# Criamos um "expander" para deixar a área de admin discreta
with st.sidebar.expander("Área Restrita (Admin)", expanded=False):
    senha_inserida = st.text_input("Senha de acesso:", type="password")

    arquivo_upload = None
    if senha_inserida == SENHA_ADMIN:
        st.success("Modo Admin Ativado 🔓")
        arquivo_upload = st.file_uploader("Atualizar base (Temporário)", type=["xlsx", "xls", "csv"])
    elif senha_inserida != "":
        st.error("Senha incorreta")


# --- 3. LEITURA DOS DADOS ---
@st.cache_data
def carregar_dados(caminho_ou_arquivo):
    try:
        # Se for string (caminho do arquivo padrão)
        if isinstance(caminho_ou_arquivo, str):
            if not os.path.exists(caminho_ou_arquivo):
                return None
            if caminho_ou_arquivo.endswith('.csv'):
                df = pd.read_csv(caminho_ou_arquivo)
            else:
                df = pd.read_excel(caminho_ou_arquivo)
        # Se for objeto (arquivo do uploader)
        else:
            if caminho_ou_arquivo.name.endswith('.csv'):
                df = pd.read_csv(caminho_ou_arquivo)
            else:
                df = pd.read_excel(caminho_ou_arquivo)

        # --- TRATAMENTO E LIMPEZA ---
        df.columns = df.columns.str.strip()

        # Mapeamentos de nomes
        if 'Competição' not in df.columns and 'Competicao' in df.columns:
            df.rename(columns={'Competicao': 'Competição'}, inplace=True)
        if 'Temporada' not in df.columns and 'Ano' in df.columns:
            df.rename(columns={'Ano': 'Temporada'}, inplace=True)

        # Colunas padrão
        if 'Competição' not in df.columns: df['Competição'] = 'Geral'
        if 'Temporada' not in df.columns: df['Temporada'] = 2025

        df['Temporada'] = df['Temporada'].astype(str).str.replace(r'\.0$', '', regex=True)

        return df
    except Exception as e:
        return None


# DECISÃO: Carregar do Upload ou do Arquivo Padrão?
df_bruto = None

# 1. Prioridade: Se o admin subiu um arquivo agora, usa ele.
if arquivo_upload is not None:
    df_bruto = carregar_dados(arquivo_upload)
    st.toast("Usando arquivo carregado manualmente!", icon="📂")

# 2. Se não tem upload, tenta ler o arquivo padrão da pasta
elif os.path.exists(ARQUIVO_PADRAO):
    df_bruto = carregar_dados(ARQUIVO_PADRAO)

# Se não encontrou nada
if df_bruto is None:
    st.info("👋 Olá! Aguardando o administrador carregar os dados da liga.")
    if senha_inserida != SENHA_ADMIN:
        st.stop()  # Para usuários normais, para aqui.
    else:
        st.warning(f"O arquivo '{ARQUIVO_PADRAO}' não foi encontrado na pasta e nenhum upload foi feito.")
        st.stop()

# --- 4. FILTROS EM CASCATA ---

# A. Filtro de Temporada
lista_temporadas = sorted(df_bruto['Temporada'].unique(), reverse=True)
temporada_selecionada = st.sidebar.selectbox("📅 Temporada:", lista_temporadas)

df_temp = df_bruto[df_bruto['Temporada'] == temporada_selecionada].copy()

# B. Filtro de Competição
lista_competicoes = sorted(df_temp['Competição'].unique().astype(str))
competicao_selecionada = st.sidebar.selectbox("🏆 Competição:", lista_competicoes)

df_comp = df_temp[df_temp['Competição'] == competicao_selecionada].copy()

# --- C. Filtro de Rodadas (Nível 3) ---

# 1. Verificação de Segurança: Existe algum dado para esta competição/ano?
# Se o dataframe estiver vazio OU se a coluna Rodada só tiver valores vazios (NaN)
if df_comp.empty or 'Rodada' not in df_comp.columns or df_comp['Rodada'].isnull().all():
    st.markdown("### 🔮 Calma, torcedor!")
    st.warning(f"A bola ainda não rolou pela **{competicao_selecionada}** na temporada **{temporada_selecionada}**. Volte mais tarde! ⚽")
    st.stop() # Para a execução aqui, evitando o erro lá embaixo

# 2. Se passou da verificação acima, é porque tem dados. Vamos criar o slider.
if 'Rodada' in df_comp.columns:
    # Converte para inteiros garantindo que ignora erros
    min_rodada = int(df_comp['Rodada'].min())
    max_rodada = int(df_comp['Rodada'].max())
    
    # Se só houver 1 rodada, ajusta para não dar erro no slider
    if min_rodada == max_rodada:
        rodada_inicio, rodada_fim = min_rodada, max_rodada
        st.sidebar.info(f"Rodada Única disponível: {min_rodada}")
    else:
        rodada_inicio, rodada_fim = st.sidebar.slider(
            "🔢 Intervalo de Rodadas:",
            min_value=min_rodada,
            max_value=max_rodada,
            value=(min_rodada, max_rodada)
        )
    
    # Filtra pelas rodadas
    df_filtrado = df_comp[(df_comp['Rodada'] >= rodada_inicio) & (df_comp['Rodada'] <= rodada_fim)].copy()
else:
    # Caso raro onde tem dados mas não tem a coluna Rodada
    df_filtrado = df_comp.copy()

# --- 5. PROCESSAMENTO DOS DADOS ---
def processar_jogos(df):
    lista_processada = []

    for _, row in df.iterrows():
        try:
            # Identificação das colunas
            col_pts_m = 'Pontuação' if 'Pontuação' in row else 'Pontuacao_Mandante'
            col_pts_v = 'Pontuação.1' if 'Pontuação.1' in row else 'Pontuacao_Visitante'

            if col_pts_m not in row: col_pts_m = 'Pontuacao_Mandante'
            if col_pts_v not in row: col_pts_v = 'Pontuacao_Visitante'

            m_pts = float(row[col_pts_m])
            v_pts = float(row[col_pts_v])

            mandante = row['Mandante']
            visitante = row['Visitante']
            rodada = row['Rodada']

            diff = abs(m_pts - v_pts)

            if diff <= 3:
                res_m, res_v = (1, 'E'), (1, 'E')
            elif m_pts > v_pts:
                res_m, res_v = (3, 'V'), (0, 'D')
            else:
                res_m, res_v = (0, 'D'), (3, 'V')

            lista_processada.append({
                'Time': mandante, 'Pontos_Camp': res_m[0], 'Resultado': res_m[1],
                'Pontuacao_Feita': m_pts, 'Rodada': rodada, 'Adversario': visitante, 'Pontuacao_Adv': v_pts
            })
            lista_processada.append({
                'Time': visitante, 'Pontos_Camp': res_v[0], 'Resultado': res_v[1],
                'Pontuacao_Feita': v_pts, 'Rodada': rodada, 'Adversario': mandante, 'Pontuacao_Adv': m_pts
            })

        except Exception:
            continue

    return pd.DataFrame(lista_processada)


df_final = processar_jogos(df_filtrado)

if df_final.empty:
    st.warning("Nenhum dado encontrado para os filtros atuais.")
    st.stop()

# --- 6. VISUALIZAÇÃO ---
tab1, tab2 = st.tabs(["📊 Tabela da Liga", "🔎 Raio-X do Time"])

# ABA 1: TABELA GERAL
with tab1:
    st.subheader(f"Classificação: {competicao_selecionada}")

    tabela_detalhada = df_final.groupby('Time').agg(
        Pontos=('Pontos_Camp', 'sum'),
        Vitorias=('Resultado', lambda x: (x == 'V').sum()),
        Empates=('Resultado', lambda x: (x == 'E').sum()),
        Derrotas=('Resultado', lambda x: (x == 'D').sum()),
        Pontuacao_Total=('Pontuacao_Feita', 'sum'),
        Jogos=('Rodada', 'count')
    ).reset_index()

    tabela_detalhada = tabela_detalhada.sort_values(
        by=['Pontos', 'Vitorias', 'Pontuacao_Total'],
        ascending=[False, False, False]
    ).reset_index(drop=True)

    tabela_detalhada.index = tabela_detalhada.index + 1
    tabela_detalhada.index.name = 'Pos'
    tabela_detalhada = tabela_detalhada.reset_index()
    tabela_detalhada['Pos'] = tabela_detalhada['Pos'].astype(str) + 'º'

    colunas_finais = ['Pos', 'Time', 'Pontos', 'Vitorias', 'Empates', 'Derrotas', 'Pontuacao_Total', 'Jogos']
    tabela_show = tabela_detalhada[colunas_finais].rename(columns={
        'Pontuacao_Total': 'Pts Cartola',
        'Vitorias': 'V', 'Empates': 'E', 'Derrotas': 'D'
    })

    st.dataframe(
        tabela_show.style.format({'Pts Cartola': '{:.2f}'})
        .background_gradient(subset=['Pontos'], cmap='Greens'),
        use_container_width=True,
        hide_index=True,
        height=600
    )

# ABA 2: RAIO-X DO TIME
with tab2:
    col_input, col_info = st.columns([1, 3])

    with col_input:
        st.markdown("### Seleção")
        lista_times = sorted(df_final['Time'].unique())
        time_selecionado = st.selectbox("Escolha o Cartoleiro:", lista_times)

    with col_info:
        df_time = df_final[df_final['Time'] == time_selecionado].sort_values('Rodada')

        total_pts = df_time['Pontos_Camp'].sum()
        total_jogos = len(df_time)
        media_cartola = df_time['Pontuacao_Feita'].mean()
        vitorias = len(df_time[df_time['Resultado'] == 'V'])
        empates = len(df_time[df_time['Resultado'] == 'E'])
        derrotas = len(df_time[df_time['Resultado'] == 'D'])
        aproveitamento = (total_pts / (total_jogos * 3)) * 100 if total_jogos > 0 else 0

        st.subheader(f"Estatísticas: {time_selecionado}")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Pontos na Liga", total_pts)
        c2.metric("Média Cartola", f"{media_cartola:.2f}")
        c3.metric("Jogos", total_jogos)
        c4.metric("Aproveitamento", f"{aproveitamento:.1f}%")

        st.divider()

        k1, k2, k3 = st.columns(3)
        k1.metric("✅ Vitórias", vitorias)
        k2.metric("➖ Empates", empates)
        k3.metric("❌ Derrotas", derrotas)

        st.divider()

        st.markdown("#### 📜 Histórico de Confrontos")

        df_historico = df_time[['Rodada', 'Pontuacao_Feita', 'Adversario', 'Pontuacao_Adv', 'Resultado']].copy()
        df_historico['Status'] = df_historico['Resultado'].map({'V': 'VITÓRIA', 'E': 'EMPATE', 'D': 'DERROTA'})
        df_historico['Icone'] = df_historico['Resultado'].map({'V': '✅', 'E': '➖', 'D': '❌'})

        df_historico = df_historico[['Rodada', 'Icone', 'Status', 'Pontuacao_Feita', 'Pontuacao_Adv', 'Adversario']]
        df_historico.columns = ['Rodada', '', 'Resultado', 'Sua Pont.', 'Pont. Adv.', 'Adversário']


        def cor_resultado(val):
            if val == 'VITÓRIA': return 'color: green; font-weight: bold;'
            if val == 'DERROTA': return 'color: red; font-weight: bold;'
            return 'color: orange; font-weight: bold;'


        st.dataframe(
            df_historico.style.format({'Sua Pont.': '{:.2f}', 'Pont. Adv.': '{:.2f}'})
            .applymap(cor_resultado, subset=['Resultado']),
            hide_index=True,
            use_container_width=True

        )

