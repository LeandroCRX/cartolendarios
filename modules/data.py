import pandas as pd
import streamlit as st
import os
from datetime import datetime

@st.cache_data
def carregar_arquivo(file_or_path):
    """Lê Excel ou CSV e faz limpeza básica."""
    try:
        if isinstance(file_or_path, str):
            if not os.path.exists(file_or_path): return None
            df = pd.read_excel(file_or_path) if not file_or_path.endswith('.csv') else pd.read_csv(file_or_path)
        else:
            df = pd.read_excel(file_or_path) if not file_or_path.name.endswith('.csv') else pd.read_csv(file_or_path)
        
        df.columns = df.columns.str.strip()
        return df
    except Exception:
        return None

def padronizar_campeonato(df):
    """Ajusta nomes de colunas do campeonato."""
    if df is None: return None
    df = df.copy()
    col_map = {'Competicao': 'Competição', 'Ano': 'Temporada'}
    df.rename(columns=col_map, inplace=True)
    
    if 'Competição' not in df.columns: df['Competição'] = 'Geral'
    if 'Temporada' not in df.columns: df['Temporada'] = str(datetime.now().year)

    df = df.dropna(subset=['Temporada'])
    df['Temporada'] = df['Temporada'].astype(str).str.replace(r'\.0$', '', regex=True)
    df = df[df['Temporada'].str.lower() != 'nan']
    return df

def padronizar_escalacoes(df):
    """Ajusta nomes de colunas das escalações e limpa dados."""
    if df is None: return None
    df = df.copy()
    
    # 1. Renomear (Normalização)
    mapa = {
        'Nome': 'Atleta', 'Posicao': 'Posição', 'Posição': 'Posição',
        'Time Cartola': 'Time', 'ime Cartola': 'Time', 'Cartoleiro': 'Cartoleiro',
        'Capitão': 'Capitao', 'Capitao': 'Capitao', 'Ano': 'Temporada'
    }
    df.rename(columns=mapa, inplace=True)
    
    # 2. Tratamento da Temporada (Crucial para o filtro funcionar)
    if 'Temporada' in df.columns:
        df = df.dropna(subset=['Temporada'])
        # Converte para texto, remove .0 (de 2025.0), e remove espaços extras
        df['Temporada'] = df['Temporada'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
    
    # 3. Tratamento da Rodada (Garante que é número)
    if 'Rodada' in df.columns:
        # Força conversão para numérico, transformando erros em NaN
        df['Rodada'] = pd.to_numeric(df['Rodada'], errors='coerce')
        df = df.dropna(subset=['Rodada']) # Remove linhas onde a rodada ficou inválida
        df['Rodada'] = df['Rodada'].astype(int)

    return df
