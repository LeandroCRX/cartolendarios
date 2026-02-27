import pandas as pd
import numpy as np

def processar_jogos(df):
    """
    Aplica a regra dos 3 pontos e gera tabela de resultados.
    Jogos 0x0 são considerados 'Agendados' (Res = '-').
    """
    lst = []
    
    # Garante que as colunas de pontuação sejam float
    cols_pontuacao = ['Pontuacao_Mandante', 'Pontuação', 'Pontuacao_Visitante', 'Pontuação.1']
    for col in cols_pontuacao:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)

    for _, r in df.iterrows():
        try:
            # Identifica colunas corretas
            cm = 'Pontuação' if 'Pontuação' in r else 'Pontuacao_Mandante'
            cv = 'Pontuação.1' if 'Pontuação.1' in r else 'Pontuacao_Visitante'
            
            if cm not in r: cm = 'Pontuacao_Mandante'
            if cv not in r: cv = 'Pontuacao_Visitante'

            pm = float(r[cm])
            pv = float(r[cv])

            comp = r.get('Competição', 'Geral')
            eh_liga = 'LIGA' in str(comp).upper()
            margem = 3.0 if eh_liga else 0.0

            # Lógica de Resultado
            if pm == 0 and pv == 0: 
                # Jogo Futuro / Não realizado
                rm, rv = (0, '-'), (0, '-')
            else:              
                diff = abs(pm - pv)
                
                # Regra de Empate (Liga: <= 3pts | Copas: 0pts)
                if diff <= margem:
                    rm, rv = (1, 'E'), (1, 'E')
                elif pm > pv:
                    rm, rv = (3, 'V'), (0, 'D')
                else:
                    rm, rv = (0, 'D'), (3, 'V')
            
            # --- CRIAÇÃO DOS DADOS ---
            
            # Lado Mandante
            base_m = {
                'Rodada': r['Rodada'], 
                'Time': r['Mandante'], 
                'Adv': r['Visitante'],
                'Pts': rm[0], 
                'Res': rm[1], 
                'Placar': pm, 
                'Placar_Adv': pv,
                'Mando': 'C',
                'Competição': comp,
                'Fase': r.get('Fase', '-'),
                'Grupo': r.get('Grupo', '-')
            }
            lst.append(base_m)
            
            # Lado Visitante
            base_v = {
                'Rodada': r['Rodada'], 
                'Time': r['Visitante'], 
                'Adv': r['Mandante'],
                'Pts': rv[0], 
                'Res': rv[1], 
                'Placar': pv, 
                'Placar_Adv': pm,
                'Mando': 'F',
                'Competição': comp,
                'Fase': r.get('Fase', '-'),
                'Grupo': r.get('Grupo', '-')
            }
            lst.append(base_v)

        except Exception:
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
    """Gera rankings ignorando jogos 0x0."""
    if df_camp is None or df_camp.empty:
        return pd.DataFrame(), pd.DataFrame()

    df = df_camp.copy()
    df = df[df['Temporada'] == temporada]
    if 'Rodada' in df.columns:
        df = df[(df['Rodada'] >= r_ini) & (df['Rodada'] <= r_fim)]

    lista_atuacoes = []
    cols_pontuacao = ['Pontuacao_Mandante', 'Pontuação', 'Pontuacao_Visitante', 'Pontuação.1']
    for col in cols_pontuacao:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)

    for _, r in df.iterrows():
        try:
            cm = 'Pontuação' if 'Pontuação' in r else 'Pontuacao_Mandante'
            cv = 'Pontuação.1' if 'Pontuação.1' in r else 'Pontuacao_Visitante'
            if cm not in r: cm = 'Pontuacao_Mandante'
            if cv not in r: cv = 'Pontuacao_Visitante'

            pm = float(r[cm])
            pv = float(r[cv])

            if pm == 0 and pv == 0: continue

            comp = r.get('Competição', 'Geral')
            rod = r['Rodada']

            lista_atuacoes.append({'Time': r['Mandante'], 'Pontuação': pm, 'Rodada': rod, 'Adversário': r['Visitante'], 'Competição': comp})
            lista_atuacoes.append({'Time': r['Visitante'], 'Pontuação': pv, 'Rodada': rod, 'Adversário': r['Mandante'], 'Competição': comp})
        except:
            continue

    df_atuacoes = pd.DataFrame(lista_atuacoes)
    if df_atuacoes.empty:
        return pd.DataFrame(), pd.DataFrame()

    df_geral = df_atuacoes.sort_values('Pontuação', ascending=False).drop_duplicates(subset=['Time', 'Rodada'])
    df_ligas = df_atuacoes[df_atuacoes['Competição'].str.contains('Liga', case=False, na=False)]
    df_ligas = df_ligas.sort_values('Pontuação', ascending=False)

    return df_geral, df_ligas
