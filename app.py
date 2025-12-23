import streamlit as st
import os

# Importa os módulos (Garante que a pasta modules tem o __init__.py e home.py)
from modules import data, utils, views, home

# 1. Configuração da Página (Deve ser sempre a primeira linha do Streamlit)
st.set_page_config(page_title="Cartolendários", page_icon="🎩", layout="wide")

# Inicializa o estado da página (Navegação)
if 'pagina_atual' not in st.session_state:
    st.session_state['pagina_atual'] = 'home'

# --- FUNÇÃO PRINCIPAL DO SISTEMA ---
def executar_sistema():
    # --- 🎨 ESTILO CSS (Laranja na Sidebar) ---
    st.markdown("""
        <style>
        /* Altera a cor de fundo da Sidebar */
        [data-testid="stSidebar"] {
            background-color: #FF8C00;
        }
        /* Ajusta a cor do texto na sidebar para branco (opcional, para contraste) */
        [data-testid="stSidebar"] .stMarkdown, 
        [data-testid="stSidebar"] h1, 
        [data-testid="stSidebar"] h2, 
        [data-testid="stSidebar"] h3, 
        [data-testid="stSidebar"] p {
            color: white !important; 
        }
        /* Ajusta cor dos inputs na sidebar se necessário */
        [data-testid="stSidebar"] .stTextInput > label, 
        [data-testid="stSidebar"] .stSelectbox > label,
        [data-testid="stSidebar"] .stSlider > label {
            color: white !important;
        }
        </style>
        """, unsafe_allow_html=True)

    # --- 1. Botão de Voltar (Sempre no topo da Sidebar) ---
    if st.sidebar.button("🏠 Voltar para Início"):
        st.session_state['pagina_atual'] = 'home'
        st.rerun()

    # --- 2. LOGO NA SIDEBAR (Ajustado) ---
    with st.sidebar:
        if os.path.exists("logo.png"):
            # Colunas ajustadas para [1, 4, 1] -> O meio (4) é maior, logo a imagem aumenta
            sb_c1, sb_c2, sb_c3 = st.columns([1, 4, 1]) 
            with sb_c2:
                st.image("logo.png", use_container_width=True)
            st.markdown("---") 
        else:
            st.header("🎩 Cartolendários") 
            st.markdown("---")

    # Título da Página Principal
    st.title("🎩 Área de Competidores")

    # Constantes e Segredos
    ARQUIVO_PADRAO = "dados_campeonato.xlsx"
    ARQUIVO_ESCALACOES = "dados_escalacoes.xlsx"

    try:
        SENHA_ADMIN = st.secrets["SENHA_ADMIN"]
    except FileNotFoundError:
        SENHA_ADMIN = "admin_local"

    # --- 3. Filtros e Uploads ---
    st.sidebar.header("⚙️ Filtros Globais")
    
    with st.sidebar.expander("Área Admin", expanded=False):
        senha = st.text_input("Senha:", type="password")
        up_camp, up_esc = None, None
        if senha == SENHA_ADMIN:
            st.success("Admin Ativado 🔓")
            up_camp = st.file_uploader("Jogos", type=["xlsx", "csv"], key="u1")
            up_esc = st.file_uploader("Escalações", type=["xlsx", "csv"], key="u2")

    # Carga e Padronização
    df_camp = data.carregar_arquivo(up_camp) if up_camp else data.carregar_arquivo(ARQUIVO_PADRAO)
    df_esc = data.carregar_arquivo(up_esc) if up_esc else data.carregar_arquivo(ARQUIVO_ESCALACOES)

    if df_camp is None:
        st.info("Aguardando dados do campeonato.")
        st.stop()

    df_camp = data.padronizar_campeonato(df_camp)
    df_esc = data.padronizar_escalacoes(df_esc)

    # Filtros Globais
    anos = sorted(df_camp['Temporada'].unique(), reverse=True)
    sel_temp = st.sidebar.selectbox("📅 Temporada:", anos)
    df_c_temp = df_camp[df_camp['Temporada'] == sel_temp].copy()

    comps = sorted([c for c in df_c_temp['Competição'].unique()])
    opcoes_comp = ["Todas"] + comps
    sel_comp = st.sidebar.selectbox("🏆 Competição (Abas 1-3):", opcoes_comp)

    df_c_comp = df_c_temp if sel_comp == "Todas" else df_c_temp[df_c_temp['Competição'] == sel_comp].copy()

    # Proteção dados vazios
    if df_c_comp.empty or 'Rodada' not in df_c_comp.columns or df_c_comp['Rodada'].isnull().all():
        st.markdown("### 🔮 Calma, torcedor!")
        st.warning(f"A bola ainda não rolou pela **{sel_comp}** na temporada **{sel_temp}**. Volte mais tarde! ⚽")
        st.stop()

    # Slider Global
    mi, ma = int(df_c_temp['Rodada'].min()), int(df_c_temp['Rodada'].max())
    if mi == ma:
        r_ini, r_fim = mi, ma
        st.sidebar.info(f"Rodada Única: {mi}")
    else:
        r_ini, r_fim = st.sidebar.slider("🔢 Rodadas (Global):", mi, ma, (mi, ma))

    df_c_final = df_c_comp[(df_c_comp['Rodada'] >= r_ini) & (df_c_comp['Rodada'] <= r_fim)].copy()

    # Processamento
    df_res = utils.processar_jogos(df_c_final)

    # Ranking Lendas
    df_lendas_geral, df_lendas_ligas = utils.gerar_ranking_lendas(df_camp, sel_temp, r_ini, r_fim)

    # Visualização (Abas)
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Tabela da Liga", "🔎 Raio-X do Time", "👕 Top Escalações", "🏅 Lendas"])

    with tab1:
        views.exibir_tabela_liga(df_res, sel_comp)

    with tab2:
        views.exibir_raio_x(df_res)
        try:
            t_disp = sorted(df_res['Time'].unique())
            t_padrao = t_disp[0] if t_disp else ""
        except:
            t_padrao = ""

    with tab3:
        if df_esc is None or df_esc.empty:
            st.info("Arquivo de escalações não carregado.")
        else:
            df_esc_temp = df_esc[df_esc['Temporada'] == sel_temp].copy()
            if df_esc_temp.empty:
                st.warning(f"Sem escalações para {sel_temp}.")
            else:
                if 'Rodada' in df_esc_temp.columns:
                    lista_rodadas = sorted(df_esc_temp['Rodada'].unique().astype(int))
                    st.markdown("##### 🕵️ Filtro de Rodada (Aba 3)")
                    c_drop, _ = st.columns([1, 2])
                    with c_drop:
                        rodada_escolhida = st.selectbox("Escolha:", lista_rodadas, index=len(lista_rodadas) - 1)

                    df_esc_final = utils.filtrar_escalacoes(df_esc_temp, sel_temp, rodada_escolhida, rodada_escolhida)
                    views.exibir_top_escalacoes(df_esc_final, t_padrao)
                else:
                    st.warning("Coluna 'Rodada' ausente.")

    with tab4:
        views.exibir_aba_lendas(df_lendas_geral, df_lendas_ligas)


# --- RODAPÉ COM LINK ---
st.sidebar.markdown("")
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


# --- LÓGICA DE ROTEAMENTO (Decide qual página mostrar) ---

if st.session_state['pagina_atual'] == 'home':
    # Mostra a Landing Page
    home.render_page()
else:
    # Mostra o Sistema Completo
    executar_sistema()



















