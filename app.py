import streamlit as st
import os

# Importa os nossos módulos (certifica-te que a pasta modules existe)
from modules import data, utils, views

# 1. Configuração da Página
st.set_page_config(page_title="Cartolendários", page_icon="🎩", layout="wide")
st.title("🎩 Cartolendários")

# Constantes e Segredos
ARQUIVO_PADRAO = "dados_campeonato.xlsx"
ARQUIVO_ESCALACOES = "dados_escalacoes.xlsx"

try:
    SENHA_ADMIN = st.secrets["SENHA_ADMIN"]
except FileNotFoundError:
    SENHA_ADMIN = "admin_local"

# 2. Barra Lateral e Upload (Admin)
st.sidebar.header("⚙️ Filtros")
with st.sidebar.expander("Área Restrita (Admin)", expanded=False):
    senha = st.text_input("Senha:", type="password")
    up_camp, up_esc = None, None
    if senha == SENHA_ADMIN:
        st.success("Admin Ativado 🔓")
        up_camp = st.file_uploader("Jogos", type=["xlsx", "csv"], key="u1")
        up_esc = st.file_uploader("Escalações", type=["xlsx", "csv"], key="u2")

# 3. Carga de Dados (Usando modules/data.py)
df_camp = data.carregar_arquivo(up_camp) if up_camp else data.carregar_arquivo(ARQUIVO_PADRAO)
df_esc = data.carregar_arquivo(up_esc) if up_esc else data.carregar_arquivo(ARQUIVO_ESCALACOES)

if df_camp is None:
    st.info("👋 Olá! Aguardando o carregamento dos dados do campeonato.")
    st.stop()

# Padronização inicial
df_camp = data.padronizar_campeonato(df_camp)

# 4. Filtros Globais
# A. Temporada
anos = sorted(df_camp['Temporada'].unique(), reverse=True)
sel_temp = st.sidebar.selectbox("📅 Temporada:", anos)
df_c_temp = df_camp[df_camp['Temporada'] == sel_temp].copy()

# B. Competição
comps = sorted([c for c in df_c_temp['Competição'].unique()])
opcoes_comp = ["Todas"] + comps
sel_comp = st.sidebar.selectbox("🏆 Competição:", opcoes_comp)

df_c_comp = df_c_temp if sel_comp == "Todas" else df_c_temp[df_c_temp['Competição'] == sel_comp].copy()

# --- BLOCO DE SEGURANÇA (A Correção Importante) ---
# Se não houver dados para o ano/competição selecionados, para aqui.
if df_c_comp.empty or 'Rodada' not in df_c_comp.columns or df_c_comp['Rodada'].isnull().all():
    st.markdown("### 🔮 Calma, torcedor!")
    st.warning(f"A bola ainda não rolou pela **{sel_comp}** na temporada **{sel_temp}**. Volte mais tarde! ⚽")
    st.stop()
# --------------------------------------------------

# C. Rodadas
mi, ma = int(df_c_comp['Rodada'].min()), int(df_c_comp['Rodada'].max())

if mi == ma:
    r_ini, r_fim = mi, ma
    st.sidebar.info(f"Rodada Única disponível: {mi}")
else:
    r_ini, r_fim = st.sidebar.slider("🔢 Intervalo de Rodadas:", mi, ma, (mi, ma))

df_c_final = df_c_comp[(df_c_comp['Rodada'] >= r_ini) & (df_c_comp['Rodada'] <= r_fim)].copy()

# 5. Processamento (Usando modules/utils.py)
# Gera tabela de resultados (vitórias, pontos, etc.)
df_res = utils.processar_jogos(df_c_final)

# Gera tabela de escalações filtrada
times_validos = df_res['Time'].unique() if sel_comp != "Todas" else None
df_esc_ok = utils.processar_escalacoes(df_esc, sel_temp, r_ini, r_fim, times_validos)

# 6. Visualização (Usando modules/views.py)
tab1, tab2, tab3 = st.tabs(["📊 Tabela da Liga", "🔎 Raio-X do Time", "👕 Top Escalações"])

with tab1:
    views.exibir_tabela_liga(df_res, sel_comp)

with tab2:
    views.exibir_raio_x(df_res)
    # Lógica auxiliar para passar um time padrão para a aba 3
    try:
        times_disponiveis = sorted(df_res['Time'].unique())
        t_padrao = times_disponiveis[0] if times_disponiveis else ""
    except: t_padrao = ""

with tab3:
    # Chama a visualização que inclui os Treemaps (Gráficos) e Comparativos
    views.exibir_top_escalacoes(df_esc_ok, t_padrao, sel_comp)


# --- RODAPÉ COM LINK ---
st.sidebar.markdown("")
st.sidebar.markdown("")
st.sidebar.markdown("")
st.sidebar.markdown("")
st.sidebar.markdown("")
st.sidebar.markdown("")
st.sidebar.markdown("---")
st.sidebar.caption("Mantido pela Diretoria: Elielton, Gil, Leandro, Léo e Welington 🛠️")
st.sidebar.markdown(
    "Desenvolvido por [**Leandro Costa Rocha**](https://www.linkedin.com/in/leandro-costa-rocha-b40189b0/)",
    unsafe_allow_html=True
)
st.sidebar.caption("v1.0 - Cartolendários")








