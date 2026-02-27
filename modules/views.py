import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from modules import utils 

# =============================================================================
# 1. VISUALIZAÇÃO INTELIGENTE
# =============================================================================

def exibir_infos_competicao(df_temporada):
    if df_temporada.empty:
        st.info("🗓️ Aguardando dados para esta temporada.")
        return

    unique_comps = df_temporada['Competição'].unique()
    comps = sorted([str(c) for c in unique_comps if pd.notna(c) and str(c).strip() != ''])
    
    if not comps: 
        st.warning("⚠️ Temporada iniciada, mas nenhuma competição foi registrada ainda.")
        return

    c_filt, _ = st.columns([1, 2])
    with c_filt: 
        sel_comp = st.selectbox("🏆 Selecione a Competição:", comps)

    df_comp = df_temporada[df_temporada['Competição'] == sel_comp].copy()

    valid_rounds = df_comp['Rodada'].dropna()
    if not valid_rounds.empty:
        mi, ma = int(valid_rounds.min()), int(valid_rounds.max())
        if mi == ma:
            st.info(f"Rodada Única: {mi}"); r_ini, r_fim = mi, ma
        else:
            r_ini, r_fim = st.slider("🔢 Intervalo de Rodadas:", mi, ma, (mi, ma))
        df_comp = df_comp[(df_comp['Rodada'] >= r_ini) & (df_comp['Rodada'] <= r_fim)]
    
    df_res = utils.processar_jogos(df_comp)

    st.markdown("---")
    if 'Fase' not in df_res.columns: df_res['Fase'] = '-'
    if 'Grupo' not in df_res.columns: df_res['Grupo'] = '-'

    fases_disponiveis = [f for f in df_res['Fase'].unique() if f != '-' and pd.notna(f) and str(f).strip() != '']

    if len(fases_disponiveis) == 0:
        gerar_tabela_classica(df_res)
        return

    def peso_fase(nome_fase):
        nome = str(nome_fase).lower()
        if 'final' in nome and 'semi' not in nome and 'quartas' not in nome and 'oitavas' not in nome: return 100
        if '3º' in nome or 'terceiro' in nome: return 95
        if 'semi' in nome: return 90
        if 'quartas' in nome: return 80
        if 'oitavas' in nome: return 70
        if '16' in nome: return 60
        if '32' in nome: return 50
        if 'grupo' in nome: return 40
        if 'fase 3' in nome: return 30
        if 'fase 2' in nome: return 20
        if 'fase 1' in nome: return 10
        if 'preliminar' in nome: return 5
        return 0 

    fases_ordenadas = sorted(fases_disponiveis, key=peso_fase, reverse=True)
    abas = st.tabs(fases_ordenadas)

    for aba, fase_atual in zip(abas, fases_ordenadas):
        with aba:
            st.markdown(f"### 📍 {fase_atual}")
            df_fase = df_res[df_res['Fase'] == fase_atual].copy()

            if 'GRUPO' in str(fase_atual).upper():
                st.info("📊 Classificação por Grupos")
                gerar_tabela_com_grupos(df_fase)
            else:
                st.info("⚔️ Confrontos diretos (Ida e Volta Automáticos)")
                exibir_confrontos_mata_mata(df_fase, fase_nome=fase_atual)

def gerar_tabela_com_grupos(df_res):
    grupos = sorted([g for g in df_res['Grupo'].unique() if g != '-' and pd.notna(g) and str(g).strip() != ''])
    if len(grupos) > 0:
        for grupo in grupos:
            st.markdown(f"#### 🟦 Grupo {grupo}")
            df_grupo = df_res[df_res['Grupo'] == grupo].copy()
            gerar_tabela_classica(df_grupo)
            st.divider()
    else:
        gerar_tabela_classica(df_res)

def gerar_tabela_classica(df_res):
    if df_res.empty: st.warning("Sem jogos para exibir."); return
    
    # Remove jogos futuros (onde Resultado é '-')
    df_res = df_res[df_res['Res'] != '-'].copy()

    if df_res.empty:
        st.info("Nenhum jogo realizado nesta seleção.")
        return
    
    df_res['Pts'] = pd.to_numeric(df_res['Pts'], errors='coerce').fillna(0)
    df_res['Placar'] = pd.to_numeric(df_res['Placar'], errors='coerce').fillna(0)

    tb = df_res.groupby('Time').agg(
        Pontos=('Pts', 'sum'), 
        V=('Res', lambda x: (x=='V').sum()),
        E=('Res', lambda x: (x=='E').sum()),
        D=('Res', lambda x: (x=='D').sum()),
        Pro=('Placar', 'sum'), 
        J=('Rodada', 'count')
    ).reset_index().sort_values(['Pontos', 'V', 'Pro'], ascending=[False, False, False]).reset_index(drop=True)

    tb.index += 1; tb['Pos'] = tb.index.astype(str) + 'º'
    for c in ['V', 'E', 'D', 'J']: tb[c] = tb[c].astype(str)

    st.dataframe(
        tb[['Pos', 'Time', 'Pontos', 'V', 'E', 'D', 'Pro', 'J']]
        .rename(columns={'Pro': 'Pts Cartola', 'J': 'Jogos'})
        .style.format({'Pts Cartola': '{:.2f}'})
        .background_gradient(subset=['Pontos'], cmap='Greens')
        .set_properties(**{'text-align': 'center'}),
        use_container_width=True, hide_index=True
    )

def exibir_confrontos_mata_mata(df_res, fase_nome=""):
    if df_res.empty: st.warning("Nenhum confronto."); return
    rodadas = sorted(df_res['Rodada'].unique(), reverse=True)
    
    st.markdown("""<style>
        .placar-box { background-color: #f0f2f6; padding: 8px 15px; border-radius: 8px; text-align: center; font-weight: bold; border: 1px solid #ddd; font-size: 1.1em; } 
        .placar-mini { font-size: 0.85em; color: #555; text-align: center; margin-bottom: 2px; }
        .time-nome { font-weight: 600; font-size: 1rem; padding-top: 5px; } 
        .campeao-box { background: linear-gradient(to right, #FFD700, #FDB931); color: black; padding: 10px; border-radius: 10px; text-align: center; font-size: 1.2rem; font-weight: bold; margin-top: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border: 2px solid #fff; } 
        .classificado-box { background-color: #d4edda; color: #155724; padding: 8px; border-radius: 8px; text-align: center; font-weight: bold; margin-top: 8px; border: 1px solid #c3e6cb; }
        .empate-box { background-color: #e2e3e5; color: #383d41; padding: 8px; border-radius: 8px; text-align: center; font-style: italic; margin-top: 8px; border: 1px solid #d6d8db; }
        .agregado-label { background-color: #333; color: #fff; padding: 2px 6px; border-radius: 4px; font-size: 0.7em; text-transform: uppercase; }
    </style>""", unsafe_allow_html=True)
    
    fase_upper = str(fase_nome).upper()
    eh_final = 'FINAL' in fase_upper and 'SEMI' not in fase_upper and 'QUAR' not in fase_upper and 'OITAV' not in fase_upper
    
    comp_nome = df_res['Competição'].iloc[0] if not df_res.empty else ""
    eh_liga = 'LIGA' in str(comp_nome).upper()
    margem_empate = 3.0 if eh_liga else 0.0

    df_unicos = df_res[df_res['Mando'] == 'C'].copy()
    confrontos = {}
    
    for _, row in df_unicos.iterrows():
        t1 = row['Time']
        t2 = row.get('Adv', row.get('Adversário', row.get('Adversario', 'Op.')))
        chave = tuple(sorted([str(t1), str(t2)]))
        if chave not in confrontos: confrontos[chave] = []
        confrontos[chave].append(row)

    def limpar_desc(valor, padrao):
        s = str(valor).strip()
        if s == '-' or s.lower() == 'nan' or s == '': return padrao
        return s

    for chave, jogos in confrontos.items():
        if len(jogos) == 1:
            row = jogos[0]
            t1, t2 = row['Time'], row.get('Adv', row.get('Adversário', 'Op.'))
            p1, p2 = row['Placar'], row['Placar_Adv']
            desc = limpar_desc(row['Grupo'], f"Rodada {int(row['Rodada'])}")
            
            st.caption(f"📅 {desc}")
            c1, c2, c3 = st.columns([4, 2, 4])
            with c1: st.markdown(f"<div style='text-align: right;' class='time-nome'>{t1}</div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='placar-box'>{p1:.2f} x {p2:.2f}</div>", unsafe_allow_html=True)
            with c3: st.markdown(f"<div style='text-align: left;' class='time-nome'>{t2}</div>", unsafe_allow_html=True)

            encerrado = row.get('Res', '-') != '-'
            if encerrado:
                if abs(p1 - p2) <= margem_empate:
                     st.markdown(f"<div class='empate-box'>⚖️ EMPATE APÓS A IDA</div>", unsafe_allow_html=True)
                else:
                    vencedor = t1 if p1 > p2 else t2
                    st.markdown(f"<div class='classificado-box'>🏁 VANTAGEM NO JOGO DE IDA: {vencedor}</div>", unsafe_allow_html=True)

        elif len(jogos) >= 2:
            jogos = sorted(jogos, key=lambda x: x['Rodada'])
            j1, j2 = jogos[0], jogos[1]
            time_A, time_B = j1['Time'], j1.get('Adv', j1.get('Adversário', 'Op.'))
            p1_ida, p2_ida = j1['Placar'], j1['Placar_Adv']
            desc1 = limpar_desc(j1['Grupo'], "Ida")

            if j2['Time'] == time_A:
                p1_volta, p2_volta = j2['Placar'], j2['Placar_Adv']
                desc2 = limpar_desc(j2['Grupo'], "Volta")
            else:
                p1_volta, p2_volta = j2['Placar_Adv'], j2['Placar']
                desc2 = limpar_desc(j2['Grupo'], "Volta")

            total_A, total_B = p1_ida + p1_volta, p2_ida + p2_volta
            
            j1_encerrado = j1.get('Res', '-') != '-'
            j2_encerrado = j2.get('Res', '-') != '-'

            st.markdown(f"<div style='text-align:center'><span class='agregado-label'>PLACAR AGREGADO</span></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='placar-mini'>{desc1}: {time_A} <b>{p1_ida:.2f} x {p2_ida:.2f}</b> {time_B} | {desc2}: {time_B} <b>{p2_volta:.2f} x {p1_volta:.2f}</b> {time_A}</div>", unsafe_allow_html=True)

            c1, c2, c3 = st.columns([4, 2, 4])
            with c1: st.markdown(f"<div style='text-align: right;' class='time-nome'>{time_A}</div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='placar-box' style='background-color:#e6f3ff; border:1px solid #0066cc'>{total_A:.2f} x {total_B:.2f}</div>", unsafe_allow_html=True)
            with c3: st.markdown(f"<div style='text-align: left;' class='time-nome'>{time_B}</div>", unsafe_allow_html=True)

            if j1_encerrado or j2_encerrado:
                if not j2_encerrado:
                    # Somente o jogo de ida aconteceu e o de volta ainda não
                    if abs(total_A - total_B) <= margem_empate:
                         st.markdown(f"<div class='empate-box'>⚖️ EMPATE APÓS A IDA</div>", unsafe_allow_html=True)
                    else:
                        vencedor_agg = time_A if total_A > total_B else time_B
                        st.markdown(f"<div class='classificado-box'>🏁 VANTAGEM APÓS A IDA: {vencedor_agg}</div>", unsafe_allow_html=True)
                else:
                    # Ambas as partidas encerradas
                    if abs(total_A - total_B) <= margem_empate:
                         st.markdown(f"<div class='empate-box'>⚖️ AGREGADO EMPATADO (Dif: {abs(total_A - total_B):.2f})</div>", unsafe_allow_html=True)
                    else:
                        vencedor_agg = time_A if total_A > total_B else time_B
                        if eh_final: st.markdown(f"<div class='campeao-box'>🏆 CAMPEÃO: {vencedor_agg} 🏆</div>", unsafe_allow_html=True); st.balloons()
                        else: st.markdown(f"<div class='classificado-box'>✅ CLASSIFICADO: {vencedor_agg}</div>", unsafe_allow_html=True)
        st.divider()

# =============================================================================
# 2. RAIO-X DO TIME
# =============================================================================

def calcular_historico_posicoes(df_competicao, time_nome):
    """
    Calcula a posição do time a cada rodada na classificação acumulada.
    Retorna DataFrame com colunas: Rodada, Posição
    """
    # Processar jogos da competição
    df_proc = utils.processar_jogos(df_competicao)
    
    # Filtrar apenas jogos realizados
    df_proc = df_proc[df_proc['Res'] != '-'].copy()
    
    if df_proc.empty:
        return pd.DataFrame()
    
    # Obter rodadas únicas ordenadas
    rodadas = sorted(df_proc['Rodada'].unique())
    
    historico = []
    
    for rodada in rodadas:
        # Filtrar dados até a rodada atual (acumulado)
        df_ate_rodada = df_proc[df_proc['Rodada'] <= rodada].copy()
        
        # Calcular tabela de classificação
        tabela = df_ate_rodada.groupby('Time').agg(
            Pontos=('Pts', 'sum'),
            V=('Res', lambda x: (x=='V').sum()),
            Pro=('Placar', 'sum')
        ).reset_index()
        
        # Ordenar por Pontos, Vitórias e Pontos Pro (critérios de desempate)
        tabela = tabela.sort_values(
            ['Pontos', 'V', 'Pro'], 
            ascending=[False, False, False]
        ).reset_index(drop=True)
        
        # Adicionar coluna de posição
        tabela['Posição'] = range(1, len(tabela) + 1)
        
        # Buscar posição do time selecionado
        time_row = tabela[tabela['Time'] == time_nome]
        
        if not time_row.empty:
            posicao = time_row.iloc[0]['Posição']
            historico.append({'Rodada': int(rodada), 'Posição': int(posicao)})
    
    return pd.DataFrame(historico)

def exibir_raio_x(df_temporada):
    if df_temporada.empty:
        st.info("Aguardando início da temporada para gerar estatísticas.")
        return

    unique_comps = df_temporada['Competição'].unique()
    comps = sorted([str(c) for c in unique_comps if pd.notna(c) and str(c).strip() != ''])
    
    if not comps:
        st.warning("⚠️ Nenhuma competição válida encontrada para gerar o Raio-X.")
        return

    opcoes_comp = ["Todas"] + comps
    
    c1, c2 = st.columns([1, 1])
    with c1: 
        sel_comp = st.selectbox("🏆 Competição (Raio-X):", opcoes_comp)
    
    if sel_comp == "Todas": df_foco = df_temporada.copy()
    else: df_foco = df_temporada[df_temporada['Competição'] == sel_comp].copy()
    
    df_res = utils.processar_jogos(df_foco) 
    if df_res.empty: st.warning("Sem dados."); return
    
    times_unicos = df_res['Time'].unique()
    times = sorted([str(t) for t in times_unicos if pd.notna(t) and str(t).strip() != ''])
    
    if not times: st.warning("Sem times encontrados."); return

    with c2: 
        t_sel = st.selectbox("🕵️ Cartoleiro:", times)
    
    st.markdown("---")
    
    dft = df_res[df_res['Time'] == t_sel].copy()

    jogos_jogados = dft[dft['Res'] != '-'].sort_values('Rodada', ascending=False)
    jogos_futuros = dft[dft['Res'] == '-'].sort_values('Rodada', ascending=True)

    # --- 1. ESTATÍSTICAS ---
    if not jogos_jogados.empty:
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Pontos Totais", f"{jogos_jogados['Pts'].sum():.0f}")
        k2.metric("Média Pontos", f"{jogos_jogados['Placar'].mean():.2f}")
        k3.metric("Jogos Disputados", len(jogos_jogados))
        
        total_pts = len(jogos_jogados) * 3
        apr = (jogos_jogados['Pts'].sum() / total_pts) * 100 if total_pts > 0 else 0
        k4.metric("Aprov.", f"{apr:.1f}%")
        
        st.divider()
        
        v = len(jogos_jogados[jogos_jogados['Res'] == 'V'])
        e = len(jogos_jogados[jogos_jogados['Res'] == 'E'])
        d = len(jogos_jogados[jogos_jogados['Res'] == 'D'])
        j1, j2, j3 = st.columns(3)
        j1.metric("✅ Vitórias", v)
        j2.metric("➖ Empates", e)
        j3.metric("❌ Derrotas", d)
    else:
        st.info("Nenhum jogo realizado ainda nesta competição.")

    st.divider()
    
    # --- 2. HISTÓRICO ---
    st.markdown(f"#### 📜 Histórico - {sel_comp}")
    if not jogos_jogados.empty:
        cols = ['Rodada', 'Res', 'Placar', 'Placar_Adv', 'Competição']
        c_adv = 'Adv' if 'Adv' in jogos_jogados.columns else 'Adversário' 
        cols.append(c_adv)
        
        hist = jogos_jogados[cols].copy()
        hist['Icone'] = hist['Res'].map({'V':'✅','E':'➖','D':'❌'})
        hist['Status'] = hist['Res'].map({'V':'VITÓRIA','E':'EMPATE','D':'DERROTA'})
        hist['Rodada'] = hist['Rodada'].apply(lambda x: f"{x:.0f}")
        hist['Sua Pont.'] = hist['Placar'].apply(lambda x: f"{x:.2f}")
        hist['Pont. Adv.'] = hist['Placar_Adv'].apply(lambda x: f"{x:.2f}")
        
        def colorir(v): 
            return 'color: green; font-weight: bold;' if v=='VITÓRIA' else 'color: red; font-weight: bold;' if v=='DERROTA' else 'color: orange; font-weight: bold;'
        
        hist = hist.rename(columns={c_adv:'Adversário', 'Icone':'', 'Status':'Resultado'})
        c_fin = ['Rodada', 'Competição', '', 'Resultado', 'Sua Pont.', 'Pont. Adv.', 'Adversário']
        if 'Fase' in hist.columns: c_fin.insert(2, 'Fase')
        
        st.dataframe(hist[c_fin].style.applymap(colorir, subset=['Resultado']).set_properties(**{'text-align': 'center'}), hide_index=True, use_container_width=True)
    else:
        st.caption("Sem histórico de partidas concluídas.")

    # Gráfico de Evolução de Posição
    # Usa df_res que contém TODOS os jogos da competição (não apenas do time selecionado)
    df_geral_comp = df_res[df_res['Res'] != '-'].copy()
    
    # Busca TODAS as rodadas agendadas (incluindo futuras com 0x0) para mostrar no eixo X
    df_todas_rodadas = df_res.copy()
    
    if not df_geral_comp.empty and sel_comp != "Todas":
        st.divider()
        st.markdown("### 📈 Evolução de Posição")
        
        rodadas_jogadas = sorted(df_geral_comp['Rodada'].unique())
        todas_rodadas = sorted(df_todas_rodadas['Rodada'].unique())
        evolucao = []

        # Calcula a posição rodada a rodada (apenas para rodadas jogadas)
        for r in rodadas_jogadas:
            df_ate_r = df_geral_comp[df_geral_comp['Rodada'] <= r]
            
            # Recalcula tabela acumulada até a rodada R
            tabela_r = df_ate_r.groupby('Time').agg(
                Pts=('Pts', 'sum'),
                V=('Res', lambda x: (x=='V').sum()),
                Pro=('Placar', 'sum')
            ).reset_index().sort_values(['Pts', 'V', 'Pro'], ascending=[False, False, False])
            
            tabela_r.reset_index(drop=True, inplace=True)
            
            # Pega a posição do time selecionado
            idx = tabela_r.index[tabela_r['Time'] == t_sel].tolist()
            if idx:
                evolucao.append({'Rodada': int(r), 'Posição': idx[0] + 1})

        if evolucao:
            df_ev = pd.DataFrame(evolucao)
            
            # Configuração do Gráfico usando Graph Objects para maior controle
            fig = go.Figure()
            
            # Adiciona a linha apenas para rodadas jogadas
            fig.add_trace(go.Scatter(
                x=df_ev['Rodada'],
                y=df_ev['Posição'],
                mode='lines+markers+text',
                name='Posição',
                line=dict(color='#FF8C00', width=3),
                marker=dict(size=10, symbol='circle'),
                text=df_ev['Posição'],
                textposition='top center'
            ))
            
            # Define o range do eixo X para incluir TODAS as rodadas (jogadas + futuras)
            fig.update_xaxes(
                title="Rodada",
                range=[min(todas_rodadas) - 0.5, max(todas_rodadas) + 0.5],
                dtick=1
            )
            
            # Inverte eixo Y (1º lugar em cima) e ajusta layout
            fig.update_yaxes(autorange="reversed", title="Colocação", dtick=1)
            fig.update_layout(
                height=350, 
                margin=dict(l=20, r=20, t=30, b=20),
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            st.caption(f"📊 Mostrando {len(rodadas_jogadas)} de {len(todas_rodadas)} rodadas disputadas. A linha representa apenas rodadas com resultados reais.")
        else:
            st.caption("Dados insuficientes para gerar gráfico de evolução.")

    # --- 4. PRÓXIMAS PARTIDAS ---
    if not jogos_futuros.empty:
        st.divider()
        st.markdown("### 📅 Próximas Partidas")
        st.caption("Jogos agendados (placar atual 0x0)")
        
        colunas_futuro = ['Rodada', 'Competição', 'Adv', 'Mando']
        if 'Fase' in jogos_futuros.columns: colunas_futuro.append('Fase')
        
        fut = jogos_futuros[colunas_futuro].copy()
        
        fut['Rodada'] = fut['Rodada'].apply(lambda x: f"{int(x)}")
        fut['Mando'] = fut['Mando'].map({'C': 'Casa 🏠', 'F': 'Fora ✈️'})
        fut = fut.rename(columns={'Adv': 'Adversário'})
        
        st.dataframe(
            fut.style.set_properties(**{'text-align': 'center'}), 
            hide_index=True, 
            use_container_width=True
        )

# =============================================================================
# 3. TOP ESCALAÇÕES
# =============================================================================
def exibir_top_escalacoes(df_esc_season, temporada_label):
    if df_esc_season is None or df_esc_season.empty:
         st.info(f"Sem dados de escalação para {temporada_label}.")
         return

    if 'Rodada' in df_esc_season.columns:
        valid_rounds = df_esc_season['Rodada'].dropna().unique()
        if len(valid_rounds) == 0:
            st.info(f"Ainda não há rodadas processadas para {temporada_label}.")
            return

        lista_rodadas = sorted(valid_rounds.astype(int))
        opcoes_rodadas = ["Todas"] + lista_rodadas
        
        c_filter, _ = st.columns([1, 3])
        with c_filter: 
            rodada_escolhida = st.selectbox("Escolha a rodada:", opcoes_rodadas, index=len(opcoes_rodadas)-1)
            
        if rodada_escolhida == "Todas": df_final = df_esc_season.copy(); st.info(f"Visualizando dados acumulados de todas as rodadas de {temporada_label}.")
        else: df_final = utils.filtrar_escalacoes(df_esc_season, temporada_label, rodada_escolhida, rodada_escolhida)
        renderizar_escalacoes(df_final)
    else: st.warning("Coluna 'Rodada' não encontrada no arquivo de escalações.")

def renderizar_escalacoes(df_esc_ok):
    if df_esc_ok.empty: st.info("Sem dados para exibir."); return
    
    st.markdown(f"### 🎨 Painel Visual")
    df_tree = df_esc_ok.groupby(['Atleta', 'Posição']).size().reset_index(name='Escalações').sort_values('Escalações', ascending=False).head(50)
    df_cap = df_esc_ok[df_esc_ok['Capitao'].astype(str).str.contains('CAP', case=False, na=False)]['Atleta'].value_counts().reset_index(); df_cap.columns = ['Atleta', 'Vezes']
    
    col_graphs = st.columns(2)
    with col_graphs[0]:
        st.subheader("🔥 Os Queridinhos"); 
        if not df_tree.empty: fig = px.treemap(df_tree, path=['Posição', 'Atleta'], values='Escalações', color='Escalações', color_continuous_scale='Blues'); st.plotly_chart(fig, use_container_width=True)
    with col_graphs[1]:
        st.subheader("©️ Top Capitães")
        if not df_cap.empty: figc = px.treemap(df_cap.head(30), path=['Atleta'], values='Vezes', color='Vezes', color_continuous_scale='Oranges'); st.plotly_chart(figc, use_container_width=True)
    
    st.divider()
    
    st.markdown("### ⚔️ Comparativo Detalhado")
    
    times_unicos = df_esc_ok['Time'].unique()
    times = sorted([str(t) for t in times_unicos if pd.notna(t) and str(t).strip() != ''])
    
    if times:
        idx_t = 0
        tf = st.selectbox("Analisar Time:", times, index=idx_t)
        st.caption(f"Mostrando destaques do **{tf}** vs **Geral**")
        st.divider()

        def get_top5(df_input, posicao):
            df_pos = df_input[df_input['Posição'] == posicao]
            top = df_pos['Atleta'].value_counts().reset_index()
            top.columns = ['Atleta', 'Qtd']
            top = top.head(5)
            top['Qtd'] = top['Qtd'].astype(str)
            return top

        posicoes = ['Goleiro', 'Lateral', 'Zagueiro', 'Meia', 'Atacante', 'Técnico']
        df_time_foco = df_esc_ok[df_esc_ok['Time'] == tf]
        df_geral = df_esc_ok.copy()

        for pos in posicoes:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"**{pos}s - {tf}**")
                df_show = get_top5(df_time_foco, pos)
                if not df_show.empty: st.dataframe(df_show.style.set_properties(**{'text-align': 'center'}), use_container_width=True, hide_index=True)
                else: st.caption("Nenhum escalado nesta posição.")
            with c2:
                st.markdown(f"**{pos}s - Geral**")
                df_show_g = get_top5(df_geral, pos)
                if not df_show_g.empty: st.dataframe(df_show_g.style.set_properties(**{'text-align': 'center'}), use_container_width=True, hide_index=True)
            st.divider()

# =============================================================================
# 4. ABA DE LENDAS
# =============================================================================
def exibir_aba_lendas(df_temporada):
    if df_temporada.empty or 'Rodada' not in df_temporada.columns:
        st.info("Aguardando dados da temporada para exibir Lendas.")
        return

    valid_rounds = df_temporada['Rodada'].dropna()
    
    if valid_rounds.empty:
        st.info("Aguardando o início dos jogos para gerar o Hall da Fama.")
        return

    mi, ma = int(valid_rounds.min()), int(valid_rounds.max())
    r_ini, r_fim = st.slider("🔢 Período de Análise (Lendas):", mi, ma, (mi, ma))
    
    df_filt = df_temporada[(df_temporada['Rodada'] >= r_ini) & (df_temporada['Rodada'] <= r_fim)].copy()
    df_proc = utils.processar_jogos(df_filt)
    
    if df_proc.empty: 
        st.warning("Sem dados processados."); 
        return
        
    df_proc['Pontuação'] = pd.to_numeric(df_proc['Placar'], errors='coerce').fillna(0)
    df_geral = df_proc.sort_values('Pontuação', ascending=False); df_ligas = df_proc.copy()
    
    st.markdown("### 🏅 Hall da Fama & Campeões")
    t1, t2, t3 = st.tabs(["🌍 Ranking Geral", "🏆 Campeões da Rodada", "👑 Rei da Rodada"])
    
    with t1:
        d = df_geral.head(50).copy(); d.reset_index(drop=True, inplace=True); d.index+=1; d['Pos']=d.index.astype(str)+'º'
        if len(d)>=1: d.loc[1,'Pos']='🥇 1º'; 
        if len(d)>=2: d.loc[2,'Pos']='🥈 2º'; 
        if len(d)>=3: d.loc[3,'Pos']='🥉 3º'
        d['Rodada']=d['Rodada'].astype(int).astype(str)
        if 'Adversário' not in d.columns: d['Adversário'] = d['Adv'] if 'Adv' in d.columns else '-'
        st.dataframe(d[['Pos','Time','Pontuação','Rodada','Competição','Adversário']].style.format({'Pontuação':'{:.2f}'}).background_gradient(subset=['Pontuação'], cmap='Greens').set_properties(**{'text-align':'center'}), use_container_width=True, hide_index=True)
    with t2:
        unique_ls = df_ligas['Competição'].unique()
        ls = sorted([str(c) for c in unique_ls if pd.notna(c) and str(c).strip() != ''])
        
        if ls:
            l = st.selectbox("Filtrar Liga:", ls); dl = df_ligas[df_ligas['Competição']==l].copy()
            if not dl.empty:
                dl['Rodada'] = pd.to_numeric(dl['Rodada'], errors='coerce')
                mx = dl.groupby('Rodada')['Pontuação'].transform('max'); dc = dl[dl['Pontuação']==mx].sort_values('Rodada')
                dc['Rodada']=dc['Rodada'].astype(int).astype(str); dc['🥇']='🏆'
                if 'Adversário' not in dc.columns: dc['Adversário'] = dc['Adv'] if 'Adv' in dc.columns else '-'
                st.dataframe(dc[['Rodada','🥇','Time','Pontuação','Adversário']].style.format({'Pontuação':'{:.2f}'}).background_gradient(subset=['Pontuação'], cmap='Oranges').set_properties(**{'text-align':'center'}), use_container_width=True, hide_index=True)
        else:
            st.info("Sem dados de ligas.")
            
    with t3:
        dr = df_ligas[df_ligas['Competição'].str.contains('Liga', case=False, na=False)].copy()
        if not dr.empty:
            dr['Rodada'] = pd.to_numeric(dr['Rodada'], errors='coerce')
            mx = dr.groupby('Rodada')['Pontuação'].transform('max'); drf = dr[dr['Pontuação']==mx].sort_values('Rodada')
            drf['Rodada']=drf['Rodada'].astype(int).astype(str); drf['👑']='👑'
            if 'Adversário' not in drf.columns: drf['Adversário'] = drf['Adv'] if 'Adv' in drf.columns else '-'
            st.dataframe(drf[['Rodada','👑','Time','Pontuação','Competição','Adversário']].style.format({'Pontuação':'{:.2f}'}).background_gradient(subset=['Pontuação'], cmap='Reds').set_properties(**{'text-align':'center'}), use_container_width=True, hide_index=True)