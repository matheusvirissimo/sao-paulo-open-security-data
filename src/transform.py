import pandas as pd
import numpy as np
from typing import List
import logging

logger = logging.getLogger(__name__) ## logger já foi carregado antes 

def clean_column_names(df: pd.DataFrame):
    """
    Padronizar nomes de colunas (minúsculas, sem acentos, underscores)
    Adaptado para estrutura do portal SSP-SP

    Params:
        df: DataFrame contendo o dado a ser transformado 
    -------
    Returns: 
        df: retorna o DataFrame normalizado
    """
    df = df.copy()
    
    # Limpar nomes de colunas
    df.columns = (df.columns
                  .astype(str)  # Garantir que são strings
                  .str.strip()  # Remover espaços
                  .str.lower() # tudo minusculo 
                  .str.normalize('NFKD') # normalização unicode no formato NNFD
                  .str.encode('ascii', errors='ignore') # botar em asc tudo
                  .str.decode('utf-8') # talvez colocar em latin. Usar para não ficar tudo em byte
                  .str.replace(' ', '_')
                  .str.replace('-', '_')
                  .str.replace(r'[^\w]', '', regex=True))
    
    # Mapeamento de colunas específicas do SSP-SP
    column_mapping = {
        'natureza': 'tipo_crime',
        'jan': 'janeiro',
        'fev': 'fevereiro', 
        'mar': 'marco',
        'abr': 'abril',
        'mai': 'maio',
        'jun': 'junho',
        'jul': 'julho',
        'ago': 'agosto',
        'set': 'setembro',
        'out': 'outubro',
        'nov': 'novembro',
        'dez': 'dezembro',
        'n_de_vitimas': 'vitimas',
        'n_vitimas': 'vitimas'
    }
    
    df.rename(columns=column_mapping, inplace=True)
    
    return df

def remove_duplicates(df: pd.DataFrame, subset: List[str] = None):
    """
    Remover registros duplicados para facilitar
    
    Params:
        df: DataFrame
        subset: Colunas para verificar duplicidade
    ------
    Returns: 
        df: DataFrame normalizado
    """
    initial_count = len(df)
    df = df.drop_duplicates(subset=subset)
    removed = initial_count - len(df)
    
    if removed > 0:
        logger.info(f"Removidas {removed} linhas duplicadas")
    
    return df

def handle_missing_values(df: pd.DataFrame, strategy: str = 'drop'):
    """
    Tratamento de valores ausentes
    
    Params:
        df: DataFrame
        strategy: 'drop', 'fill_zero', 'fill_mean', 'fill_median'
    --------
    Returns:
        df: Dataframe sem valores ausentes (ou tratados)
    """
    df = df.copy()
    
    if strategy == 'drop':
        df = df.dropna()
    elif strategy == 'fill_zero':
        df = df.fillna(0)
    elif strategy == 'fill_mean':
        df = df.fillna(df.mean(numeric_only=True))
    elif strategy == 'fill_median':
        df = df.fillna(df.median(numeric_only=True))
    
    return df

def normalize_dates(df: pd.DataFrame, date_columns: List[str]):
    """
    Normalização de datas

    Params: 
        df: DataFrame
        date_columns: lista com as datas
    """
    df = df.copy()
    
    for col in date_columns:
        if col in df.columns: ## Ver esse if com mais carinho
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    return df

def categorize_crimes(df: pd.DataFrame, crime_column: str = 'tipo_crime'):
    """
    Categorizar tipos de crime em grupos (violentos, patrimoniais e outros)
    Adaptado para nomenclatura do portal SSP-SP
    """
    df = df.copy()
    
    # Categorias baseadas nos dados reais do SSP-SP
    crime_categories = {
        'Crimes Violentos': [
            'homicidio', 'latrocinio', 'lesao_corporal', 'estupro',
            'tentativa_de_homicidio', 'homicidio_doloso', 'homicidio_culposo',
            'lesao_corporal_dolosa', 'lesao_corporal_seguida_de_morte'
        ],
        'Crimes Patrimoniais': [
            'roubo', 'furto', 'extorsao', 'roubo_de_veiculo', 'furto_de_veiculo',
            'roubo_de_carga', 'roubo_a_banco', 'total_de_roubo'
        ],
        'Crimes de Trânsito': [
            'acidente', 'transito', 'culposo_por_acidente',
            'homicidio_culposo_por_acidente_de_transito',
            'lesao_corporal_culposa_por_acidente_de_transito'
        ],
    }
    
    def categorize(crime):
        if pd.isna(crime):
            return 'Outros'
        
        crime_lower = str(crime).lower()
        
        for category, keywords in crime_categories.items():
            if any(keyword in crime_lower for keyword in keywords):
                return category
        return 'Outros'
    
    df['categoria_crime'] = df[crime_column].apply(categorize)
    return df

def aggregate_by_region(df: pd.DataFrame, region_col: str = 'municipio'):
    """
    Unir estatísticas por região
    """
    return df.groupby(region_col).agg({
        'ocorrencias': 'sum',
        'vitimas': 'sum',
        # pensar em mais agregações para se realizar
    }).reset_index()

def calculate_crime_rate(df: pd.DataFrame, population_data: pd.DataFrame):
    """
    Calcula da taxa de criminalidade por 100 mil habitantes 
    """
    df = df.merge(population_data, on='municipio', how='left')
    # Fazer uma possível validação para que os valores das colunas sejam de um tipo numérico
    df['taxa_criminalidade'] = (df['ocorrencias'] / df['populacao']) * 100000
    return df

def validate_data(df: pd.DataFrame):
    """
    Valida integridade dos dados transformados
    # não sei se esse tá funcionando corretamente

    Returns:
        Dicionário com estatísticas de validação
    """
    validation = {
        'total_registros': len(df),
        'valores_nulos': df.isnull().sum().to_dict(),
        'duplicatas': df.duplicated().sum(),
        'colunas': list(df.columns)
    }
    
    logger.info(f"Validação: {validation}")
    return validation