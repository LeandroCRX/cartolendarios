# 🎩 Como Rodar o Cartolendários Localmente

Este guia explica como configurar seu ambiente Windows para rodar e testar a aplicação.

## 1. Pré-requisitos
* **Python 3.9 ou superior**: Caso não tenha, baixe em [python.org](https://www.python.org/downloads/). 
  * *Importante:* Marque a opção **"Add Python to PATH"** durante a instalação.

## 2. Configurando o Ambiente (Recomendado)
É boa prática usar um ambiente virtual para não conflitar com outras bibliotecas do seu PC.

No terminal (PowerShell ou CMD), dentro da pasta do projeto, execute:
```powershell
# Cria o ambiente virtual
python -m venv venv

# Ativa o ambiente
# No PowerShell:
.\venv\Scripts\Activate.ps1
# No CMD:
.\venv\Scripts\activate.bat
```

## 3. Instalando as Dependências
Com o ambiente ativado, instale as bibliotecas necessárias:
```powershell
pip install -r requirements.txt
```

## 4. Rodando a Aplicação
Para iniciar o servidor local do Streamlit:
```powershell
streamlit run app.py
```
A aplicação abrirá automaticamente no seu navegador padrão (geralmente em `http://localhost:8501`).

## 5. Área de Admin (Dica)
A aplicação possui uma área restrita para upload de arquivos. 
* A senha padrão para execução local é: `admin_local`

## 6. Como Testar
1. Verifique se a página inicial ("Home") carrega o logo e as informações.
2. Navegue pelas abas ("Informações da Competição", "Raio-X", etc).
3. Verifique se os dados dos arquivos `.xlsx` estão sendo exibidos corretamente nas tabelas e gráficos.
4. Tente trocar a "Temporada" no menu lateral para ver se os filtros funcionam.

---
*Em caso de erro de "módulo não encontrado", verifique se o comando `pip install` foi concluído com sucesso.*
