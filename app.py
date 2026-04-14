import streamlit as st
import os

# Importa os módulos
from modules import data, utils, views, home

# 1. Configuração da Página
st.set_page_config(page_title="Cartolendários", page_icon="🎩", layout="wide")

# Inicializa o estado da página
if 'pagina_atual' not in st.session_state:
    st.session_state['pagina_atual'] = 'home'


# --- FUNÇÃO PRINCIPAL DO SISTEMA ---
def executar_sistema():
    # --- ESTILO CSS ---
    st.markdown("""
        <style>
        [data-testid="stSidebar"] { background-color: #FF8C00; }
        [data-testid="stSidebar"] * { color: black !important; }
        div.stButton > button { width: 100%; }
        /* Ajuste para inputs dentro das abas não ficarem brancos demais se o tema for dark */
        div[data-baseweb="select"] > div { background-color: #f0f2f6; color: black; }
        </style>
        """, unsafe_allow_html=True)

    # ==========================================
    # 1. SIDEBAR (Logo + Temporada)
    # ==========================================
    with st.sidebar:
        if os.path.exists("logo.png"):
            sb_c1, sb_c2, sb_c3 = st.columns([1, 4, 1])
            with sb_c2:
                st.image("logo.png", use_container_width=True)
        else:
            st.header("🎩 Cartolendários")

        st.write("")
        if st.button("🏠 Voltar para Início"):
            st.session_state['pagina_atual'] = 'home'
            st.rerun()
        st.markdown("---")

        # --- FILTRO APENAS DE TEMPORADA ---
        st.header("📅 Temporada")

        # Carregamento de Admin/Arquivos (Mantido para garantir funcionamento)
        with st.expander("Área Admin", expanded=False):
            try:
                SENHA_ADMIN = st.secrets["SENHA_ADMIN"]
            except:
                SENHA_ADMIN = "admin_local"
            senha = st.text_input("Senha:", type="password")
            up_camp, up_esc = None, None
            if senha == SENHA_ADMIN:
                st.success("Admin Ativado 🔓")
                st.info("💡 Dica: O sistema carrega os parâmetros da Planilha (Google Sheets) automaticamente. O upload serve como sobreposição manual temporária.")
                up_camp = st.file_uploader("Jogos (Sobrescrita)", type=["xlsx", "csv"], key="u1")
                up_esc = st.file_uploader("Escalações (Sobrescrita)", type=["xlsx", "csv"], key="u2")

    # Carga de Dados (Google Sheets e Upload do Admin)
    URL_PLANILHA = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRe3TueEzfUATx9dp4ucEqu9c0gYJBWhIwh98VTUYca3itxkMO9Aw0wmZfCzQG_PotBrCx1YlBB0Nfy/pub?output=xlsx"

    planilha_gs = None
    if not up_camp or not up_esc:
        planilha_gs = data.carregar_dados_google_sheets(URL_PLANILHA)

    # Jogos
    if up_camp:
        df_camp_raw = data.carregar_arquivo(up_camp)
        df_camp = data.padronizar_campeonato(df_camp_raw) if df_camp_raw is not None else None
    else:
        df_camp_raw = planilha_gs.get('Jogos') if planilha_gs else None
        df_camp = data.padronizar_campeonato(df_camp_raw)

    # Escalações
    if up_esc:
        df_esc_raw = data.carregar_arquivo(up_esc)
        df_esc = data.padronizar_escalacoes(df_esc_raw) if df_esc_raw is not None else None
    else:
        df_esc_raw = planilha_gs.get('Escalações') if planilha_gs else None
        df_esc = data.padronizar_escalacoes(df_esc_raw)

    if df_camp is None or df_camp.empty:
        st.sidebar.warning("⚠️ Dados de campeonato não encontrados.")
        st.sidebar.info("Verifique se a aba 'Jogos' existe na planilha do Google Sheets linkada no sistema e se há internet disponível.")
        st.title("🎩 Área de Competidores")
        st.warning("Dados não carregados. O sistema foi interrompido.")
        st.stop()

    # Filtro de Temporada (Sidebar)
    anos = sorted(df_camp['Temporada'].unique(), reverse=True)
    sel_temp = st.sidebar.selectbox("Escolha o Ano:", anos)

    # Filtra os DataFrames Pela Temporada selecionada
    # Passaremos estes dataframes "brutos" da temporada para as views processarem
    df_camp_season = df_camp[df_camp['Temporada'] == sel_temp].copy()

    if df_esc is not None and not df_esc.empty:
        df_esc_season = df_esc[df_esc['Temporada'] == sel_temp].copy()
    else:
        df_esc_season = None

    # Rodapé Sidebar
    st.sidebar.markdown("---")
    st.sidebar.caption("Mantido pela Diretoria: Elielton, Gil, Leandro, Léo e Welington 🛠️")
    st.sidebar.caption("v1.1 - Cartolendários")

    # ==========================================
    # 2. ÁREA PRINCIPAL (Abas)
    # ==========================================
    st.title("🎩 Área de Competidores")

    if df_camp_season.empty:
        st.warning(f"Sem dados para a temporada {sel_temp}.")
        st.stop()

    # Criação das Abas
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📊 Informações da Competição", "🔎 Raio-X do Time", "👕 Top Escalações", "🏅 Lendas"])

    # --- ABA 1: TABELA E MATA-MATA ---
    with tab1:
        # Passamos o dataframe bruto da temporada. A view vai criar o dropdown de competição.
        views.exibir_infos_competicao(df_camp_season)

    # --- ABA 2: RAIO-X ---
    with tab2:
        # Passamos o dataframe bruto. A view vai criar dropdown de competição e time.
        views.exibir_raio_x(df_camp_season)

    # --- ABA 3: ESCALAÇÕES ---
    with tab3:
        if df_esc_season is None or df_esc_season.empty:
            st.info(f"Sem escalações para {sel_temp}.")
        else:
            views.exibir_top_escalacoes(df_esc_season, sel_temp)

    # --- ABA 4: LENDAS ---
    with tab4:
        # A lógica de lendas precisa processar tudo. Vamos deixar a view cuidar disso.
        views.exibir_aba_lendas(df_camp_season)


# --- ROTEAMENTO ---
if st.session_state['pagina_atual'] == 'home':
    home.render_page()
else:
    executar_sistema()


