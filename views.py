import streamlit as st
import pandas as pd
import plotly.express as px

def exibir_tabela_liga(df_res, sel_comp):
    st.subheader(f"Classificação: {sel_comp}")
    if df_res.empty:
        st.warning("Sem jogos.")
        return

    # Garante numérico para evitar erro de soma
    df_res['Pts'] = pd.to_numeric(df_res['Pts'], errors='coerce').fillna(0)
    df_res['Placar'] = pd.to_numeric(df_res['Placar'], errors='coerce').fillna(0)
    
    tb = df_res.groupby('Time').agg(
        Pontos=('Pts', 'sum'), V=('Res', lambda x: (x=='V').sum()), 
        E=('Res', lambda x: (x=='E').sum()), D=('Res', lambda x: (x=='D').sum()),
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
        dft = df_res[df_res['Time'] == t_sel].sort_values('Rodada')
        
        # Cards
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Pontos", dft['Pts'].sum())
        k2.metric("Média", f"{dft['Placar'].mean():.2f}")
        k3.metric("Jogos", len(dft))
        apr = (dft['Pts'].sum()/(len(dft)*3))*100 if len(dft)>0 else 0
        k4.metric("Aprov.", f"{apr:.1f}%")
        st.divider()
        
        # Histórico Visual
        st.markdown("#### 📜 Histórico")
        hist = dft[['Rodada', 'Res', 'Placar', 'Placar_Adv', 'Adv']].copy()
        hist['Icone'] = hist['Res'].map({'V': '✅', 'E': '➖', 'D': '❌'})
        hist['Status'] = hist['Res'].map({'V': 'VITÓRIA', 'E': 'EMPATE', 'D': 'DERROTA'})
        
        # Formatação
        hist['Rodada'] = hist['Rodada'].apply(lambda x: f"{x:.0f}")
        hist['Sua Pont.'] = hist['Placar'].apply(lambda x: f"{x:.2f}")
        hist['Pont. Adv.'] = hist['Placar_Adv'].apply(lambda x: f"{x:.2f}")
        
        def colorir(v): return 'color: green; font-weight: bold;' if v=='VITÓRIA' else 'color: red; font-weight: bold;' if v=='DERROTA' else 'color: orange; font-weight: bold;'
        
        st.dataframe(
            hist[['Rodada', 'Icone', 'Status', 'Sua Pont.', 'Pont. Adv.', 'Adv']].rename(columns={'Icone': '', 'Status': 'Resultado', 'Adv': 'Adversário'})
                .style.applymap(colorir, subset=['Resultado'])
                .set_properties(subset=['Rodada', '', 'Resultado', 'Sua Pont.', 'Pont. Adv.'], **{'text-align': 'center'}),
            hide_index=True, use_container_width=True
        )

def exibir_top_escalacoes(df_esc_ok, t_sel_aba2, sel_comp):
    if df_esc_ok.empty:
        st.info("⚠️ Carregue o arquivo 'dados_escalacoes.xlsx'.")
        return

    st.markdown(f"### 🎨 Painel Visual: {sel_comp}")
    
    # Treemaps (Lógica simplificada para caber aqui)
    df_tree = df_esc_ok.groupby(['Atleta', 'Posição']).size().reset_index(name='Escalações').sort_values('Escalações', ascending=False).head(50)
    
    if not df_tree.empty:
        fig = px.treemap(df_tree, path=['Posição', 'Atleta'], values='Escalações', color='Escalações', color_continuous_scale='Blues')
        st.plotly_chart(fig, use_container_width=True)

    # Tabelas Comparativas (Resumido para o exemplo)
    st.divider()
    st.markdown("### ⚔️ Comparativo")
    
    times_esc = sorted(df_esc_ok['Time'].unique())
    idx_t = times_esc.index(t_sel_aba2) if t_sel_aba2 in times_esc else 0
    time_foco = st.selectbox("Analisar Time:", times_esc, index=idx_t)
    
    # ... (Aqui entraria o loop das posições e capitães que já tens)
    st.caption("Detalhes de Goleiros, Laterais, etc...")
