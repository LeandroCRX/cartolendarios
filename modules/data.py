import pandas as pd
import streamlit as st
from datetime import datetime

def carregar_arquivo(uploaded_file):
    """Carrega o arquivo Excel ou CSV e retorna um DataFrame."""
    if uploaded_file is None:
        return None
    
    try:
        # Verifica se é um arquivo enviado pelo usuário ou um caminho local (string)
        if isinstance(uploaded_file, str):
            nome_arquivo = uploaded_file
        else:
            nome_arquivo = uploaded_file.name

        # Carrega baseado na extensão
        if nome_arquivo.endswith('.xlsx'):
            return pd.read_excel(uploaded_file)
        else:
            return pd.read_csv(uploaded_file, sep=';', encoding='utf-8')
    except Exception as e:
        st.error(f"Erro ao carregar arquivo: {e}")
        return None

# ==============================================================================
# FUNÇÕES CACHEADAS — Evitam releitura dos arquivos a cada interação do usuário
# ==============================================================================

@st.cache_data(ttl=600, show_spinner="⏳ Baixando dados do Google Sheets...")
def carregar_dados_google_sheets(url: str):
    """Baixa o arquivo Excel completo do Google sheets."""
    try:
        return pd.read_excel(url, sheet_name=None)
    except Exception as e:
        st.error(f"Erro ao acessar Google Sheets: {e}")
        return None

@st.cache_data(ttl=600, show_spinner="⏳ Carregando dados dos campeonatos...")
def carregar_campeonato_cache(caminho: str):
    """Carrega e padroniza o arquivo de campeonato com cache (10 minutos)."""
    df = carregar_arquivo(caminho)
    if df is None:
        return None
    return padronizar_campeonato(df)

@st.cache_data(ttl=600, show_spinner="⏳ Carregando escalações...")
def carregar_escalacoes_cache(caminho: str):
    """Carrega e padroniza o arquivo de escalações com cache (10 minutos)."""
    df = carregar_arquivo(caminho)
    if df is None:
        return None
    return padronizar_escalacoes(df)

def padronizar_campeonato(df):
    """Ajusta nomes de colunas do campeonato."""
    if df is None or df.empty: return None
    df = df.copy()
    
    df.columns = df.columns.str.strip()

    mapa_colunas = {
        'Competicao': 'Competição', 'Competição': 'Competição',
        'Ano': 'Temporada', 'Rod': 'Rodada',
        'Time Mandante': 'Mandante', 'Time Visitante': 'Visitante',
        'Pontuacao_Man': 'Pontuacao_Mandante', 'Pontuação_Man': 'Pontuacao_Mandante',
        'Pontuacao Mandante': 'Pontuacao_Mandante', 'Pontuação Mandante': 'Pontuacao_Mandante',
        'Pont_Man': 'Pontuacao_Mandante', 'Pont_Mandante': 'Pontuacao_Mandante',
        'Pontuacao_Visi': 'Pontuacao_Visitante', 'Pontuação_Visi': 'Pontuacao_Visitante',
        'Pontuacao Visitante': 'Pontuacao_Visitante', 'Pontuação Visitante': 'Pontuacao_Visitante',
        'Pont_Visi': 'Pontuacao_Visitante', 'Pont_Visitante': 'Pontuacao_Visitante',
        'Fase': 'Fase', 'Etapa': 'Fase', 'Rodada Fase': 'Fase', 'N': 'Fase',
        'Chave': 'Grupo'
    }
    
    df.rename(columns=mapa_colunas, inplace=True)

    if 'Competição' not in df.columns: df['Competição'] = 'Geral'
    if 'Temporada' not in df.columns: df['Temporada'] = str(datetime.now().year)
    if 'Fase' not in df.columns: df['Fase'] = '-'
    if 'Grupo' not in df.columns: df['Grupo'] = '-'

    df = df.dropna(subset=['Temporada'])
    df['Temporada'] = df['Temporada'].astype(str).str.replace(r'\.0$', '', regex=True)
    df = df[df['Temporada'].str.lower() != 'nan']

    colunas_finais = [
        'Mandante', 'Visitante', 'Pontuacao_Mandante', 'Pontuacao_Visitante', 
        'Rodada', 'Competição', 'Temporada', 'Fase', 'Grupo'
    ]
    cols_existentes = [c for c in colunas_finais if c in df.columns]
    
    return df[cols_existentes]

def padronizar_escalacoes(df):
    """Padroniza o arquivo de escalações."""
    if df is None or df.empty: return df
    df = df.copy()
    df.columns = df.columns.str.strip()
    
    mapa = {
        'Nome': 'Atleta', 'Atleta': 'Atleta', 'Apelido': 'Atleta', 'Jogador': 'Atleta',
        'Posicao': 'Posição', 'Posição': 'Posição',
        'Time Cartola': 'Time', 'Clube': 'Time', 'Time': 'Time', 'Equipe': 'Time',
        'Rodada': 'Rodada', 'Temporada': 'Temporada', 'Ano': 'Temporada',
        'Pontos': 'Pontos', 'Pontuacao': 'Pontos', 'Pontuação': 'Pontos',
        'Capitao': 'Capitao', 'Capitão': 'Capitao'
    }
    
    df.rename(columns=mapa, inplace=True)

    if 'Atleta' not in df.columns:
        colunas_texto = df.select_dtypes(include=['object']).columns
        if len(colunas_texto) > 0: df['Atleta'] = df[colunas_texto[0]]
        else: df['Atleta'] = 'Desconhecido'

    if 'Temporada' not in df.columns:
        df['Temporada'] = str(datetime.now().year)
    
    df = df.dropna(subset=['Temporada'])
    df['Temporada'] = df['Temporada'].astype(str).str.replace(r'\.0$', '', regex=True)
    
    # Remove linhas onde Atleta + Time + Rodada + Temporada são idênticos.
    if {'Atleta', 'Time', 'Rodada', 'Temporada'}.issubset(df.columns):
        df.drop_duplicates(subset=['Atleta', 'Time', 'Rodada', 'Temporada'], inplace=True)
    
    return df
