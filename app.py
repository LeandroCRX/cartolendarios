import streamlit as st
import os
from modules import data, utils, views

# 1. Configuração
st.set_page_config(page_title="Cartolendários", page_icon="🎩", layout="wide")
st.title("🎩 Cartolendários")

ARQUIVO_PADRAO = "dados_campeonato.xlsx"
ARQUIVO_ESCALACOES = "dados_escalacoes.xlsx"

try:
    SENHA_ADMIN = st.secrets["SENHA_ADMIN"]
except FileNotFoundError:
    SENHA_ADMIN = "admin_local"

# 2. Sidebar
st.sidebar.header("⚙️ Filtros Globais")
with st.sidebar.expander("Área Admin", expanded=False):
    senha = st.text_input("Senha:", type="password")
    up_camp, up_esc = None, None
    if senha == SENHA_ADMIN:
        st.success("Admin Ativado 🔓")
        up_camp = st.file_uploader("Jogos", type=["xlsx", "csv"], key="u1")
        up_esc = st.file_uploader("Escalações", type=["xlsx", "csv"], key="u2")

# 3. Carga e Padronização
df_camp = data.carregar_arquivo(up_camp) if up_camp else data.carregar_arquivo(ARQUIVO_PADRAO)
df_esc = data.carregar_arquivo(up_esc) if up_esc else data.carregar_arquivo(ARQUIVO_ESCALACOES)

if df_camp is None:
    st.info("Aguardando dados do campeonato.")
    st.stop()

df_camp = data.padronizar_campeonato(df_camp)
df_esc = data.padronizar_escalacoes(df_esc) # Padroniza aqui para facilitar o uso na Aba 3

# 4. Filtros Globais (Barra Lateral)
anos = sorted(df_camp['Temporada'].unique(), reverse=True)
sel_temp = st.sidebar.selectbox("📅 Temporada:", anos)
df_c_temp = df_camp[df_camp['Temporada'] == sel_temp].copy()

comps = sorted([c for c in df_c_temp['Competição'].unique()])
opcoes_comp = ["Todas"] + comps
sel_comp = st.sidebar.selectbox("🏆 Competição:", opcoes_comp)

df_c_comp = df_c_temp if sel_comp == "Todas" else df_c_temp[df_c_temp['Competição'] == sel_comp].copy()

# Proteção dados vazios
if df_c_comp.empty or 'Rodada' not in df_c_comp.columns or df_c_comp['Rodada'].isnull().all():
    st.markdown("### 🔮 Calma, torcedor!")
    st.warning(f"A bola ainda não rolou pela **{sel_comp}** na temporada **{sel_temp}**. Volte mais tarde! ⚽")
    st.stop()

# Slider Global (Aba 1 e 2)
mi, ma = int(df_c_comp['Rodada'].min()), int(df_c_comp['Rodada'].max())
if mi == ma:
    r_ini, r_fim = mi, ma
    st.sidebar.info(f"Rodada Única: {mi}")
else:
    r_ini, r_fim = st.sidebar.slider("🔢 Rodadas (Abas 1 e 2):", mi, ma, (mi, ma))

df_c_final = df_c_comp[(df_c_comp['Rodada'] >= r_ini) & (df_c_comp['Rodada'] <= r_fim)].copy()

# 5. Processamento Principal
df_res = utils.processar_jogos(df_c_final)

# 6. Visualização
tab1, tab2, tab3 = st.tabs(["📊 Tabela da Liga", "🔎 Raio-X do Time", "👕 Top Escalações"])

with tab1:
    views.exibir_tabela_liga(df_res, sel_comp)

with tab2:
    views.exibir_raio_x(df_res)
    # Pega time padrão para aba 3
    try:
        times_disponiveis = sorted(df_res['Time'].unique())
        t_padrao = times_disponiveis[0] if times_disponiveis else ""
    except: t_padrao = ""

with tab3:
    # --- LÓGICA EXCLUSIVA DA ABA 3 ---
    if df_esc is None or df_esc.empty:
        st.info("Arquivo de escalações não carregado.")
    else:
        # 1. Filtra apenas pela TEMPORADA
        df_esc_temp = df_esc[df_esc['Temporada'] == sel_temp].copy()
        
        if df_esc_temp.empty:
            st.warning(f"Sem escalações para {sel_temp}.")
        else:
            # 2. Descobre rodadas disponíveis (Lista Única e Ordenada)
            if 'Rodada' in df_esc_temp.columns:
                # Pega as rodadas únicas e converte para inteiros para ficar bonito (sem 1.0)
                lista_rodadas = sorted(df_esc_temp['Rodada'].unique().astype(int))
                
                # 3. Dropdown (Selectbox)
                st.markdown("##### 🕵️ Filtro de Rodada")
                
                c_drop, _ = st.columns([1, 2]) # Coluna mais estreita para o dropdown
                with c_drop:
                    # O index=len()-1 faz com que a última rodada (mais recente) venha selecionada por padrão
                    rodada_escolhida = st.selectbox(
                        "Escolha a Rodada:", 
                        lista_rodadas, 
                        index=len(lista_rodadas)-1
                    )
                
                # 4. Filtra e Exibe
                # O TRUQUE: Passamos a mesma rodada como início e fim para a função filtrar_escalacoes
                # Assim ela retorna apenas os dados daquela rodada específica.
                df_esc_final = utils.filtrar_escalacoes(df_esc_temp, sel_temp, rodada_escolhida, rodada_escolhida)
                
                views.exibir_top_escalacoes(df_esc_final, t_padrao)
            else:
                st.warning("Coluna 'Rodada' não encontrada nas escalações.")


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













