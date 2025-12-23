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
                    'Pts': rm[0], 'Res': rm[1], 'Placar': pm, 'Placar_Adv': pv}
            
            lst.append(base)
            lst.append({**base, 'Time': r['Visitante'], 'Adv': r['Mandante'], 
                        'Pts': rv[0], 'Res': rv[1], 'Placar': pv, 'Placar_Adv': pm})
        except: continue
        
    return pd.DataFrame(lst)

def filtrar_escalacoes(df_esc, temporada, r_ini, r_fim):
    """Filtra as escalações por temporada e rodada."""
    if df_esc is None or df_esc.empty: return pd.DataFrame()
    
    try:
        df = df_esc.copy()
        # Filtra Temporada
        df = df[df['Temporada'] == temporada]
        # Filtra Rodadas
        if 'Rodada' in df.columns:
            df = df[(df['Rodada'] >= r_ini) & (df['Rodada'] <= r_fim)]
            
        return df
    except:
        return pd.DataFrame()
