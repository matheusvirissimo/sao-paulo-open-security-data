# Extração de Dados do Portal SSP-SP

## Sobre

Este projeto realiza ETL (Extração, Transformação e Carga) de dados de criminalidade do Portal da Secretaria de Segurança Pública de São Paulo.

**URL do Portal:** https://www.ssp.sp.gov.br/estatistica/dados-mensais


Estes scripts irão:
1. Extrair dados de São Paulo Capital
2. Limpar e transformar os dados
3. Salvar em CSV e Parquet

## Funções Principais

### extract.py

- `extract_local_file(file_path)` - Lê arquivo local CSV/Excel

### transform.py

- `clean_column_names(df)` - Normaliza nomes de colunas
- `unpivot_monthly_data(df)` - Converte formato wide → long
- `categorize_crimes(df)` - Categoriza tipos de crimes
- `remove_duplicates(df)` - Remove duplicatas
- `handle_missing_values(df, strategy)` - Trata valores nulos
- `calculate_crime_rate(df, population_data)` - Calcula taxa por 100k habitantes

### load.py

- `save_to_csv(df, output_path)` - Salva em CSV
- `save_to_parquet(df, output_path)` - Salva em Parquet (recomendado)
- `save_to_excel(df, output_path)` - Salva em Excel
- `save_to_database(df, table_name, connection_string)` - Salva em banco SQL (apesar de que iremos usar duckdb)
- `create_summary_report(df, output_dir)` - Gera relatório JSON