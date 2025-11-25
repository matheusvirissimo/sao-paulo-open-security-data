import requests ## lib para requisição web
import pandas as pd
from pathlib import Path
from typing import Optional
import logging ## lib para fazer o registro das ações

## Carregar log
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_local_file(file_path: str, **kwargs):
    """
    Extrair dados de arquivo local CSV/Excel
    
    Args:
        file_path: Caminho do arquivo
        **kwargs: Argumentos adicionais para pd.read_csv ou pd.read_excel
    
    Returns:
        DataFrame com os dados
    """
    try:
        if file_path.endswith('.csv'): # caminho terminou com csv
            return pd.read_csv(file_path, **kwargs) 
        elif file_path.endswith(('.xlsx', '.xls')):
            return pd.read_excel(file_path, **kwargs) # caminho terminou em planilha
        else:
            logger.error(f"Formato não suportado: {file_path}")
            return None
    except Exception as e:
        logger.error(f"Erro ao ler arquivo {file_path}: {e}")
        return None
    