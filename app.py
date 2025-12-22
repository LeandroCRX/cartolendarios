import streamlit as st
import os

# Importa os nossos novos módulos
from modules import data, utils, views

# 1. Configuração
st.set_page_config(page_title="Cartolendários", page_icon="🎩", layout="wide")
st.title("🎩 Cartolendários")

# Constantes e Segredos
ARQUIVO_PADRAO = "dados_campeonato.xlsx"
ARQUIVO_ESCALACOES = "dados_escalacoes.xlsx"
try:
    SENHA_ADMIN = st.secrets["SENHA_ADMIN"]
except FileNotFoundError:
    SENHA_ADMIN = "admin_local"

# 2. Sidebar e Upload
st.sidebar.header("⚙️ Filtros")
with st.sidebar.expander("Área Restrita (Admin)", expanded=False):
    senha = st.text_input("Senha:", type="password")
    up_camp, up_esc = None, None
    if senha == SENHA_ADMIN:
        st.success("Admin Ativado 🔓")
        up_camp = st.file_uploader("Jogos", type=["xlsx", "csv"], key="u1")
        up_esc = st.file_uploader("Escalações", type=["xlsx", "csv"], key="u2")

# 3. Carga de Dados (Usando o módulo data.py)
df_camp = data.carregar_arquivo(up_camp) if up_camp else data.carregar_arquivo(ARQUIVO_PADRAO)
df_esc = data.carregar_arquivo(up_esc) if up_esc else data.carregar_arquivo(ARQUIVO_ESCALACOES)

if df_camp is None:
    st.info("Aguardando dados do campeonato.")
    st.stop()

df_camp = data.padronizar_campeonato(df_camp)

# 4. Filtros (Lógica de Controle fica no app.py)
anos = sorted(df_camp['Temporada'].unique(), reverse=True)
sel_temp = st.sidebar.selectbox("📅 Temporada:", anos)
df_c_temp = df_camp[df_camp['Temporada'] == sel_temp].copy()

comps = sorted([c for c in df_c_temp['Competição'].unique()])
opcoes_comp = ["Todas"] + comps
sel_comp = st.sidebar.selectbox("🏆 Competição:", opcoes_comp)

df_c_comp = df_c_temp if sel_comp == "Todas" else df_c_temp[df_c_temp['Competição'] == sel_comp].copy()

if 'Rodada' in df_c_comp.columns:
    mi, ma = int(df_c_comp['Rodada'].min()), int(df_c_comp['Rodada'].max())
    r_ini, r_fim = st.sidebar.slider("🔢 Rodadas:", mi, ma, (mi, ma))
    df_c_final = df_c_comp[(df_c_comp['Rodada'] >= r_ini) & (df_c_comp['Rodada'] <= r_fim)].copy()
else:
    r_ini, r_fim = 1, 38
    df_c_final = df_c_comp.copy()

# 5. Processamento (Usando o módulo utils.py)
df_res = utils.processar_jogos(df_c_final)

times_validos = df_res['Time'].unique() if sel_comp != "Todas" else None
df_esc_ok = utils.processar_escalacoes(df_esc, sel_temp, r_ini, r_fim, times_validos)

# 6. Visualização (Usando o módulo views.py)
tab1, tab2, tab3 = st.tabs(["📊 Tabela da Liga", "🔎 Raio-X do Time", "👕 Top Escalações"])

with tab1:
    views.exibir_tabela_liga(df_res, sel_comp)

with tab2:
    views.exibir_raio_x(df_res)
    # Hackzinho para passar o time selecionado para a aba 3
    # (Em uma versão avançada, usaríamos st.session_state)
    time_selecionado_aba2 = df_res['Time'].iloc[0] # Padrão
    # Nota: A seleção real acontece dentro da função exibir_raio_x visualmente

with tab3:
    # Passamos um time padrão ou implementamos session_state para ligar as abas
    views.exibir_top_escalacoes(df_esc_ok, "Time Padrão", sel_comp)

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






