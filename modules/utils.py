import pandas as pd


def processar_jogos(df):
    """Aplica a regra dos 3 pontos e gera tabela de resultados."""
    lst = []
    for _, r in df.iterrows():
        try:
            cm = 'Pontuação' if 'Pontuação' in r else 'Pontuacao_Mandante'
            cv = 'Pontuação.1' if 'Pontuação.1' in r else 'Pontuacao_Visitante'
            if cm not in r: cm = 'Pontuacao_Mandante'
            if cv not in r: cv = 'Pontuacao_Visitante'

            pm = float(r[cm]) if pd.notnull(r[cm]) else 0.0
            pv = float(r[cv]) if pd.notnull(r[cv]) else 0.0

            diff = abs(pm - pv)

            if diff <= 3:
                rm, rv = (1, 'E'), (1, 'E')
            elif pm > pv:
                rm, rv = (3, 'V'), (0, 'D')
            else:
                rm, rv = (0, 'D'), (3, 'V')

            base = {'Rodada': r['Rodada'], 'Time': r['Mandante'], 'Adv': r['Visitante'],
                    'Pts': rm[0], 'Res': rm[1], 'Placar': pm, 'Placar_Adv': pv,
                    'Competição': r.get('Competição', 'Geral')}

            lst.append(base)
            lst.append({**base, 'Time': r['Visitante'], 'Adv': r['Mandante'],
                        'Pts': rv[0], 'Res': rv[1], 'Placar': pv, 'Placar_Adv': pm})
        except:
            continue

    return pd.DataFrame(lst)


def filtrar_escalacoes(df_esc, temporada, r_ini, r_fim):
    """Filtra as escalações por temporada e rodada."""
    if df_esc is None or df_esc.empty: return pd.DataFrame()

    try:
        df = df_esc.copy()
        df = df[df['Temporada'] == temporada]
        if 'Rodada' in df.columns:
            df = df[(df['Rodada'] >= r_ini) & (df['Rodada'] <= r_fim)]
        return df
    except:
        return pd.DataFrame()


def gerar_ranking_lendas(df_camp, temporada, r_ini, r_fim):
    """
    Gera dois dataframes de 'Maiores Pontuadores da Rodada' (Mitadas).
    """
    if df_camp is None or df_camp.empty:
        return pd.DataFrame(), pd.DataFrame()

    # 1. Filtro Inicial
    df = df_camp.copy()
    df = df[df['Temporada'] == temporada]
    if 'Rodada' in df.columns:
        df = df[(df['Rodada'] >= r_ini) & (df['Rodada'] <= r_fim)]

    # 2. Transforma em Lista Vertical
    lista_atuacoes = []
    for _, r in df.iterrows():
        try:
            # Garante float
            cm = 'Pontuação' if 'Pontuação' in r else 'Pontuacao_Mandante'
            cv = 'Pontuação.1' if 'Pontuação.1' in r else 'Pontuacao_Visitante'
            if cm not in r: cm = 'Pontuacao_Mandante'
            if cv not in r: cv = 'Pontuacao_Visitante'

            pm = float(r[cm]) if pd.notnull(r[cm]) else 0.0
            pv = float(r[cv]) if pd.notnull(r[cv]) else 0.0

            comp = r.get('Competição', 'Geral')
            rod = r['Rodada']

            lista_atuacoes.append({'Time': r['Mandante'], 'Pontuação': pm, 'Rodada': rod, 'Adversário': r['Visitante'],
                                   'Competição': comp})
            lista_atuacoes.append({'Time': r['Visitante'], 'Pontuação': pv, 'Rodada': rod, 'Adversário': r['Mandante'],
                                   'Competição': comp})
        except:
            continue

    df_atuacoes = pd.DataFrame(lista_atuacoes)
    if df_atuacoes.empty:
        return pd.DataFrame(), pd.DataFrame()

    # 3. DataFrame GERAL (Removemos duplicatas aqui pois é um Hall da Fama único)
    df_geral = df_atuacoes.sort_values('Pontuação', ascending=False).drop_duplicates(subset=['Time', 'Rodada'])

    # 4. DataFrame LIGAS (Mantemos duplicatas de times em ligas diferentes para permitir o filtro)
    df_ligas = df_atuacoes[df_atuacoes['Competição'].str.contains('Liga', case=False, na=False)]
    df_ligas = df_ligas.sort_values('Pontuação', ascending=False)
    # Nota: NÃO fazemos drop_duplicates aqui ainda, faremos na visualização se necessário.

    return df_geral, df_ligas
