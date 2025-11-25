import pandas as pd
from pathlib import Path
from typing import Optional
import json
import logging
from sqlalchemy import create_engine # lib para facilitar interação com bancos relacionais

logger = logging.getLogger(__name__)

def save_to_csv(df: pd.DataFrame, output_path: str, **kwargs):
    """
    Salvar DataFrame em arquivo CSV
    
    Params:
        df: DataFrame a ser salvo
        output_path: Caminho do arquivo de saída
        **kwargs: Argumentos adicionais para 'to_csv'
    """
    try:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False, encoding='utf-8-sig', **kwargs)
        logger.info(f"Dados salvos em: {output_path}")
        return True
    except Exception as e:
        logger.error(f"Erro ao salvar CSV: {e}")
        return False

def save_to_parquet(df: pd.DataFrame, output_path: str, **kwargs):
    """
    Salvar DataFrame em formato Parquet (bem mais eficiente)
    """
    try:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(output_path, index=False, **kwargs)
        logger.info(f"Dados salvos em: {output_path}")
        return True
    except Exception as e:
        logger.error(f"Erro ao salvar Parquet: {e}")
        return False

## Se for usar parquet, bom usar o duckdb para manipular depois os dados

def save_to_excel(df: pd.DataFrame, output_path: str, sheet_name: str = 'Dados'):
    """
    Salvar DataFrame em arquivo Excel (bônus)
    """
    try:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        df.to_excel(output_path, sheet_name=sheet_name, index=False)
        logger.info(f"Dados salvos em: {output_path}")
        return True
    except Exception as e:
        logger.error(f"Erro ao salvar Excel: {e}")
        return False
    
def save_to_database(df: pd.DataFrame, table_name: str, connection_string: str, if_exists: str = 'replace'):
    """
    Salva DataFrame em banco de dados SQL
    
    Params:
        df: DataFrame
        table_name: Nome da tabela
        connection_string: String de conexão SQLAlchemy
        if_exists: 'fail', 'replace', 'append'
    """
    try:
        engine = create_engine(connection_string)
        df.to_sql(table_name, engine, if_exists=if_exists, index=False)
        logger.info(f"Dados carregados na tabela: {table_name}")
        return True
    except Exception as e:
        logger.error(f"Erro ao salvar no banco: {e}")
        return False

def save_metadata(metadata: dict, output_path: str) -> bool:
    """
    Salvar metadados do processamento

    Params
        metadata: dicionário contendo informações sobre o processamento dos dados
        output_path: diretório que será colocado
    """
    try:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        logger.info(f"Metadados salvos em: {output_path}")
        return True
    except Exception as e:
        logger.error(f"Erro ao salvar metadados: {e}")
        return False
    
def create_summary_report(df: pd.DataFrame, output_dir: str):
    """
    Criar relatório resumidos dos dados processados
    """
    try:
        summary = {
            'total_registros': len(df),
            'periodo': {
                'inicio': str(df['data'].min()) if 'data' in df.columns else 'N/A',
                'fim': str(df['data'].max()) if 'data' in df.columns else 'N/A'
            },
            'estatisticas': df.describe().to_dict(),
            'colunas': list(df.columns)
        }
        
        summary_path = f"{output_dir}/summary_report.json"
        return save_metadata(summary, summary_path)
    except Exception as e:
        logger.error(f"Erro ao criar relatório: {e}")
        return False