import streamlit as st
import os
import base64


def get_base64_of_bin_file(bin_file):
    """Função auxiliar para ler a imagem e transformar em texto para o HTML."""
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        return None


def render_page():
    # Inicializa o estado
    if 'exibir_infos' not in st.session_state:
        st.session_state['exibir_infos'] = False

    # --- CABEÇALHO (HERO SECTION COM FUNDO LARANJA) ---
    st.markdown("<div style='padding-top: 1rem;'></div>", unsafe_allow_html=True)

    # 1. Prepara a imagem (Logo ou Cartola)
    img_html = ""
    if os.path.exists("logo.png"):
        img_b64 = get_base64_of_bin_file("logo.png")
        if img_b64:
            # Ajuste 'width: 250px' se quiser a logo maior ou menor
            img_html = f'<img src="data:image/png;base64,{img_b64}" style="width: 250px; display: block; margin: 0 auto;">'

    # Se não tiver logo, usa o emoji
    if not img_html:
        img_html = "<h1 style='text-align: center; font-size: 5rem; margin: 0;'>🎩</h1>"

    # 2. Cria o Banner HTML Laranja
    # Cor usada: #FF7F00 (Laranja Cartola) | Texto: Branco para destaque
    st.markdown(f"""
    <div style="
        background-color: #FF7F00; 
        padding: 40px 20px; 
        border-radius: 15px; 
        margin-bottom: 30px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
    ">
        {img_html}
        <h3 style='color: white; font-family: sans-serif; font-size: 3.5rem; margin-top: 10px; margin-bottom: 0; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);'>
            ___________________________
        </h3>
        <h3 style='color: #fff5e6; font-family: sans-serif; font-weight: lighter; margin-top: 5px;'>
                A Elite do Cartola FC reunida
        </h3>
    </div>
    """, unsafe_allow_html=True)

    # --- ÁREA DE DECISÃO (BOTÕES) ---
    col_spacer_e, col_btn, col_spacer_d = st.columns([1, 2, 1])

    with col_btn:
        st.markdown("##### 🚀 Para Competidores")
        if st.button("⚽ JÁ SOU MEMBRO: ACESSAR ESTATÍSTICAS", type="primary", use_container_width=True):
            st.session_state['pagina_atual'] = 'sistema'
            st.rerun()

        st.write("")

        st.markdown("##### 👋 Para Visitantes")
        if st.button("🔍 NÃO SOU MEMBRO: QUERO CONHECER A LIGA", use_container_width=True):
            st.session_state['exibir_infos'] = True
            st.rerun()

    # --- CONTEÚDO INFORMATIVO ---
    if st.session_state['exibir_infos']:
        st.markdown("---")

        st.markdown("### 🏛️ Nossa História")
        st.markdown("""
        O **Cartolendários** nasceu da paixão pelo futebol e pela competitividade. 
        O que começou com uma brincadeira entre amigos transformou-se numa das ligas mais organizadas e disputadas no Espírito Santo.

        Nosso objetivo é proporcionar entretenimento, resenha de qualidade e, claro, premiar os melhores estrategistas da rodada.
        """)

        st.markdown("---")

        # --- NOVA DIRETORIA ---
        st.markdown("### 🤝 A Diretoria")

        # FOTO DA DIRETORIA
        c_img_e, c_img_c, c_img_d = st.columns([1, 4, 1])
        with c_img_c:
            if os.path.exists("diretoria.jpg"):
                st.image("diretoria.jpg", caption="A Elite Reunida: Diretoria Cartolendários 2026",
                         use_container_width=True)
            elif os.path.exists("diretoria.png"):
                st.image("diretoria.png", caption="A Elite Reunida: Diretoria Cartolendários 2026",
                         use_container_width=True)

        st.write("")

        # Os 5 Cards
        col_d1, col_d2, col_d3, col_d4, col_d5 = st.columns(5)

        with col_d1:
            st.info("**Presidente**\n\nLeo Favato\n\n*O Visionário*")
        with col_d2:
            st.info("**Diretor Técnico**\n\nGil\n\n*O Colecionador de Troféus*")
        with col_d3:
            st.info("**Diretor Técnico**\n\nWellington\n\n*Especialista enigmático*")
        with col_d4:
            st.info("**Diretor Técnico**\n\nLeandro Rocha\n\n*O Mago dos Dados*")
        with col_d5:
            st.info("**Diretor Técnico**\n\nElielton\n\n*O Estagiário, Maravilha na voz*")

        st.markdown("---")

        # Seção Campeonatos
        st.markdown("### 🏆 Nossos Campeonatos")
        tab_a, tab_b, tab_c = st.tabs(["Liga Clássica", "Mata-Mata", "Ligas Tiro Curto"])

        with tab_a:
            st.write(
                "A tradicional disputa por pontos corridos. Premiação para os melhores de cada turno e o grande campeão geral.")
            st.metric("Premiação Estimada", "R$ 1.500,00")
        with tab_b:
            st.write("Emoção pura! Confrontos diretos onde quem perde dá adeus. Apenas um sobreviverá.")
            st.metric("Premiação Estimada", "R$ 800,00")
        with tab_c:
            st.write("Ligas rápidas de 5 ou 10 rodadas para quem busca recuperação imediata e dinheiro no bolso.")
            st.metric("Premiação Estimada", "R$ 200,00 / Rodada")

        st.markdown("---")

        # Seção Final
        st.success("""
        ### 💰 Quer participar da Temporada 2026?

        Ainda dá tempo de garantir a tua vaga na elite!

        * **Valor da Inscrição:** R$ XX,00
        * **Chave Pix:** email@exemplo.com

        📲 **Entre em contato com a Diretoria:** (XX) 99999-9999
        """)

        if st.button("⬆️ Recolher Informações"):
            st.session_state['exibir_infos'] = False
            st.rerun()

    st.markdown("---")
    st.markdown("Desenvolvido por [**Leandro Costa Rocha**](https://www.linkedin.com/in/leandro-costa-rocha-b40189b0/")
    st.caption("© 2026 Cartolendários - Todos os direitos reservados.")
