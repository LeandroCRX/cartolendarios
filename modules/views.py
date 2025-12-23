import streamlit as st
import pandas as pd
import plotly.express as px


def exibir_tabela_liga(df_res, sel_comp):
    st.subheader(f"Classificação: {sel_comp}")
    if df_res.empty:
        st.warning("Sem jogos.")
        return

    df_res['Pts'] = pd.to_numeric(df_res['Pts'], errors='coerce').fillna(0)
    df_res['Placar'] = pd.to_numeric(df_res['Placar'], errors='coerce').fillna(0)

    tb = df_res.groupby('Time').agg(
        Pontos=('Pts', 'sum'), V=('Res', lambda x: (x == 'V').sum()),
        E=('Res', lambda x: (x == 'E').sum()), D=('Res', lambda x: (x == 'D').sum()),
        Pro=('Placar', 'sum'), J=('Rodada', 'count')
    ).reset_index().sort_values(['Pontos', 'V', 'Pro'], ascending=[False, False, False]).reset_index(drop=True)

    tb.index += 1
    tb['Pos'] = tb.index.astype(str) + 'º'
    for c in ['V', 'E', 'D', 'J']: tb[c] = tb[c].astype(str)

    st.dataframe(
        tb[['Pos', 'Time', 'Pontos', 'V', 'E', 'D', 'Pro', 'J']].rename(columns={'Pro': 'Pts Cartola', 'J': 'Jogos'})
        .style.format({'Pts Cartola': '{:.2f}'})
        .background_gradient(subset=['Pontos'], cmap='Greens')
        .set_properties(**{'text-align': 'center'}),
        use_container_width=True, hide_index=True, height=600
    )


def exibir_raio_x(df_res):
    c1, c2 = st.columns([1, 3])
    with c1:
        times = sorted(df_res['Time'].unique())
        t_sel = st.selectbox("Cartoleiro:", times)
    with c2:
        dft = df_res[df_res['Time'] == t_sel].sort_values('Rodada', ascending=False)

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Pontos", dft['Pts'].sum())
        k2.metric("Média", f"{dft['Placar'].mean():.2f}")
        k3.metric("Jogos", len(dft))
        apr = (dft['Pts'].sum() / (len(dft) * 3)) * 100 if len(dft) > 0 else 0
        k4.metric("Aprov.", f"{apr:.1f}%")
        st.divider()

        vitorias = len(dft[dft['Res'] == 'V'])
        empates = len(dft[dft['Res'] == 'E'])
        derrotas = len(dft[dft['Res'] == 'D'])
        j1, j2, j3 = st.columns(3)
        j1.metric("✅ Vitórias", vitorias)
        j2.metric("➖ Empates", empates)
        j3.metric("❌ Derrotas", derrotas)
        st.divider()

        st.markdown("#### 📜 Histórico")
        hist = dft[['Rodada', 'Res', 'Placar', 'Placar_Adv', 'Adv']].copy()
        hist['Icone'] = hist['Res'].map({'V': '✅', 'E': '➖', 'D': '❌'})
        hist['Status'] = hist['Res'].map({'V': 'VITÓRIA', 'E': 'EMPATE', 'D': 'DERROTA'})

        hist['Rodada'] = hist['Rodada'].apply(lambda x: f"{x:.0f}")
        hist['Sua Pont.'] = hist['Placar'].apply(lambda x: f"{x:.2f}")
        hist['Pont. Adv.'] = hist['Placar_Adv'].apply(lambda x: f"{x:.2f}")

        def colorir(
                v): return 'color: green; font-weight: bold;' if v == 'VITÓRIA' else 'color: red; font-weight: bold;' if v == 'DERROTA' else 'color: orange; font-weight: bold;'

        st.dataframe(
            hist[['Rodada', 'Icone', 'Status', 'Sua Pont.', 'Pont. Adv.', 'Adv']].rename(
                columns={'Icone': '', 'Status': 'Resultado', 'Adv': 'Adversário'})
            .style.applymap(colorir, subset=['Resultado'])
            .set_properties(subset=['Rodada', '', 'Resultado', 'Sua Pont.', 'Pont. Adv.'], **{'text-align': 'center'}),
            hide_index=True, use_container_width=True
        )


def exibir_top_escalacoes(df_esc_ok, t_sel_aba2):
    if df_esc_ok.empty:
        st.info("⚠️ Sem dados de escalações para o período selecionado.")
        return

    st.markdown(f"### 🎨 Painel Visual")

    df_tree = df_esc_ok.groupby(['Atleta', 'Posição']).size().reset_index(name='Escalações').sort_values('Escalações',
                                                                                                         ascending=False).head(
        50)

    df_cap_tree = df_esc_ok[df_esc_ok['Capitao'].astype(str).str.contains('CAP', case=False, na=False)]
    df_cap_tree = df_cap_tree['Atleta'].value_counts().reset_index()
    df_cap_tree.columns = ['Atleta', 'Vezes']
    df_cap_tree = df_cap_tree.head(30)

    st.subheader("🔥 Os Queridinhos")
    if not df_tree.empty:
        fig = px.treemap(
            df_tree, path=['Posição', 'Atleta'], values='Escalações',
            color='Escalações', color_continuous_scale='Blues'
        )
        fig.update_traces(textinfo="label+value")
        fig.update_layout(margin=dict(t=10, l=0, r=0, b=0))
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("©️ Top Capitães")
    if not df_cap_tree.empty:
        fig_caps = px.treemap(
            df_cap_tree, path=['Atleta'], values='Vezes',
            color='Vezes', color_continuous_scale='Oranges'
        )
        fig_caps.update_traces(textinfo="label+value")
        fig_caps.update_layout(margin=dict(t=10, l=0, r=0, b=0))
        st.plotly_chart(fig_caps, use_container_width=True)

    st.divider()
    st.markdown("### ⚔️ Comparativo Detalhado")

    times_esc = sorted(df_esc_ok['Time'].unique())
    idx_t = times_esc.index(t_sel_aba2) if t_sel_aba2 in times_esc else 0
    time_foco = st.selectbox("Analisar Time:", times_esc, index=idx_t)

    st.divider()

    def get_top5(df_input, posicao):
        df_pos = df_input[df_input['Posição'] == posicao]
        top = df_pos['Atleta'].value_counts().reset_index()
        top.columns = ['Atleta', 'Qtd']
        top = top.head(5)
        top['Qtd'] = top['Qtd'].astype(str)
        return top

    posicoes = ['Goleiro', 'Lateral', 'Zagueiro', 'Meia', 'Atacante', 'Técnico']
    df_time_foco = df_esc_ok[df_esc_ok['Time'] == time_foco]
    df_geral = df_esc_ok.copy()

    for pos in posicoes:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"**{pos}s - {time_foco}**")
            df_show = get_top5(df_time_foco, pos)
            if not df_show.empty:
                st.dataframe(df_show.style.set_properties(**{'text-align': 'center'}), use_container_width=True,
                             hide_index=True)
            else:
                st.caption("Nenhum escalado.")
        with c2:
            st.markdown(f"**{pos}s - Geral (Temporada)**")
            df_show_g = get_top5(df_geral, pos)
            if not df_show_g.empty:
                st.dataframe(df_show_g.style.set_properties(**{'text-align': 'center'}), use_container_width=True,
                             hide_index=True)
        st.divider()


def exibir_aba_lendas(df_geral, df_ligas):
    """Exibe Hall da Fama e Campeões por Rodada."""

    st.markdown("### 🏅 Hall da Fama & Campeões")

    tab_l1, tab_l2 = st.tabs(["🌍 Ranking Geral (Top Mitadas)", "👑 Campeões da Rodada (Por Liga)"])

    # --- ABA 1: Ranking Geral (Hall da Fama) ---
    with tab_l1:
        st.caption("As maiores pontuações registradas na temporada, independente da liga.")
        if df_geral.empty:
            st.info("Nenhum registro encontrado.")
        else:
            # Formatação Hall da Fama
            df_show = df_geral.head(50).copy()
            df_show.reset_index(drop=True, inplace=True)
            df_show.index += 1
            df_show['Pos'] = df_show.index.astype(str) + 'º'

            df_show.loc[1, 'Pos'] = '🥇 1º' if len(df_show) >= 1 else '1º'
            df_show.loc[2, 'Pos'] = '🥈 2º' if len(df_show) >= 2 else '2º'
            df_show.loc[3, 'Pos'] = '🥉 3º' if len(df_show) >= 3 else '3º'

            df_show['Rodada'] = df_show['Rodada'].astype(int).astype(str)

            st.dataframe(
                df_show[['Pos', 'Time', 'Pontuação', 'Rodada', 'Competição', 'Adversário']]
                .style.format({'Pontuação': '{:.2f}'})
                .background_gradient(subset=['Pontuação'], cmap='Greens')
                .set_properties(**{'text-align': 'center'}),
                use_container_width=True, hide_index=True
            )

    # --- ABA 2: Campeões da Rodada (Por Liga) ---
    with tab_l2:
        st.caption("Veja quem foi o maior pontuador de cada rodada na liga selecionada.")

        if df_ligas.empty:
            st.info("Nenhuma competição do tipo 'Liga' encontrada.")
        else:
            # Dropdown de Ligas
            ligas_disponiveis = sorted(df_ligas['Competição'].unique())
            liga_sel = st.selectbox("Selecione a Liga para visualizar:", ligas_disponiveis)

            # Filtra dados da liga selecionada
            df_liga_atual = df_ligas[df_ligas['Competição'] == liga_sel].copy()

            if df_liga_atual.empty:
                st.warning("Sem dados para esta liga.")
            else:
                # LÓGICA DO CAMPEÃO DA RODADA
                # 1. Garante que Rodada é número para ordenar corretamente
                df_liga_atual['Rodada'] = pd.to_numeric(df_liga_atual['Rodada'], errors='coerce')

                # 2. Encontra a pontuação máxima de cada rodada
                # Usamos transform('max') para lidar com empates (mostra os dois se empatarem)
                max_pts_por_rodada = df_liga_atual.groupby('Rodada')['Pontuação'].transform('max')
                df_campeoes = df_liga_atual[df_liga_atual['Pontuação'] == max_pts_por_rodada]

                # 3. Ordena cronologicamente (Rodada 1, 2, 3...)
                df_campeoes = df_campeoes.sort_values('Rodada')

                # 4. Formatação para Exibição
                df_campeoes['Rodada'] = df_campeoes['Rodada'].astype(int).astype(str)
                df_campeoes['👑'] = '🏆'  # Adiciona um ícone visual

                st.dataframe(
                    df_campeoes[['Rodada', '👑', 'Time', 'Pontuação', 'Adversário']]
                    .style.format({'Pontuação': '{:.2f}'})
                    .background_gradient(subset=['Pontuação'], cmap='Oranges')
                    .set_properties(**{'text-align': 'center'}),
                    use_container_width=True, hide_index=True
                )


    
    # --- ABA 3: Rei da Rodada (O Maior entre TODAS as Ligas) ---
    with tab_l3:
        st.caption("Quem foi o MELHOR de todos na rodada? Compara todas as ligas e mostra o maior pontuador absoluto.")
        
        if df_ligas.empty:
            st.info("Sem dados de ligas para comparar.")
        else:
            # 1. Filtra para garantir que só temos "Ligas" (Caso tenha passado sujeira)
            # O filtro é case-insensitive (pega 'Liga', 'liga', 'LIGA')
            df_reis = df_ligas[df_ligas['Competição'].str.contains('Liga', case=False, na=False)].copy()
            
            if df_reis.empty:
                 st.warning("Nenhuma competição com nome 'Liga' encontrada.")
            else:
                # 2. Garante que Rodada é número
                df_reis['Rodada'] = pd.to_numeric(df_reis['Rodada'], errors='coerce')

                # 3. Mágica: Agrupa por Rodada e descobre o MAX global (entre todas as ligas)
                max_pts_global = df_reis.groupby('Rodada')['Pontuação'].transform('max')
                
                # 4. Mantém apenas as linhas que igualam esse máximo
                df_reis_final = df_reis[df_reis['Pontuação'] == max_pts_global].copy()

                # 5. Ordenação e Formatação
                df_reis_final = df_reis_final.sort_values('Rodada')
                df_reis_final['Rodada'] = df_reis_final['Rodada'].astype(int).astype(str)
                df_reis_final['👑'] = '👑' # Ícone de Rei

                # Mostramos também a coluna "Competição" para saber de qual Liga o Rei veio
                st.dataframe(
                    df_reis_final[['Rodada', '👑', 'Time', 'Pontuação', 'Competição', 'Adversário']]
                    .style.format({'Pontuação': '{:.2f}'})
                    .background_gradient(subset=['Pontuação'], cmap='Reds') # Vermelho real para destaque
                    .set_properties(**{'text-align': 'center'}),
                    use_container_width=True, hide_index=True
                )
