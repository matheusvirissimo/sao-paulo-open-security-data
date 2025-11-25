# FEITO COM LLM PARA CORRIGIR O NaN DO PYTHON PARA O JS
"""
Script para corrigir arquivos JSON removendo valores NaN inválidos
"""
import json
import re
from pathlib import Path

def fix_json_file(filepath):
    """Remove NaN, Infinity e outros valores inválidos de JSON"""
    print(f"\n🔧 Corrigindo: {filepath.name}")
    
    # Ler arquivo como texto
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Contar problemas
    nan_count = content.count(': NaN')
    inf_count = content.count(': Infinity') + content.count(': -Infinity')
    
    if nan_count == 0 and inf_count == 0:
        print(f"  ✓ Arquivo já está válido!")
        return True
    
    print(f"  ⚠️ Encontrados: {nan_count} NaN, {inf_count} Infinity")
    
    # Substituir valores inválidos
    content = re.sub(r':\s*NaN\s*,', ': null,', content)
    content = re.sub(r':\s*NaN\s*}', ': null}', content)
    content = re.sub(r':\s*Infinity\s*,', ': null,', content)
    content = re.sub(r':\s*Infinity\s*}', ': null}', content)
    content = re.sub(r':\s*-Infinity\s*,', ': null,', content)
    content = re.sub(r':\s*-Infinity\s*}', ': null}', content)
    
    # Validar JSON
    try:
        data = json.loads(content)
        print(f"  ✓ JSON validado com sucesso!")
        
        # Salvar corrigido
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        size = filepath.stat().st_size / (1024 * 1024)
        print(f"  ✓ Arquivo salvo: {size:.2f} MB")
        return True
        
    except json.JSONDecodeError as e:
        print(f"  ❌ Erro ao validar JSON: {e}")
        return False

def main():
    site_dir = Path(__file__).parent
    
    print("="*60)
    print("CORRIGINDO ARQUIVOS JSON")
    print("="*60)
    
    json_files = [
        site_dir / 'dados_criminais.json',
        site_dir / 'dados_criminais_sample.json',
        site_dir / 'estatisticas.json'
    ]
    
    success_count = 0
    for json_file in json_files:
        if json_file.exists():
            if fix_json_file(json_file):
                success_count += 1
        else:
            print(f"\n⚠️ Arquivo não encontrado: {json_file.name}")
    
    print("\n" + "="*60)
    print(f"CONCLUÍDO: {success_count}/{len(json_files)} arquivos corrigidos")
    print("="*60)
    print("\n✅ Atualize o navegador (Ctrl+F5) para ver as mudanças!")

if __name__ == '__main__':
    main()
