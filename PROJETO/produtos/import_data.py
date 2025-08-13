# produtos/import_data.py
import os
import django
import json

# Configura o ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'viveiro_lagni.settings') # Certifique-se de que 'viveiro_lagni' é o nome correto da sua pasta de settings
django.setup()

from produtos.models import NCM, CFOP # Importe seus modelos

def import_ncms(filepath='ncm_data.json'):
    print(f"Importando NCMs de {filepath}...")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            ncm_list = data.get('Nomenclaturas', []) # Acessa a lista de nomenclaturas

            for item in ncm_list:
                codigo = item.get('Codigo')
                descricao = item.get('Descricao')

                if codigo and descricao:
                    ncm, created = NCM.objects.get_or_create(
                        codigo=codigo,
                        defaults={'descricao': descricao}
                    )
                    if created:
                        print(f"Adicionado NCM: {codigo} - {descricao}")
                    # else:
                        # print(f"NCM já existe: {codigo}")
                else:
                    print(f"Item NCM ignorado (formato incorreto ou campos ausentes): {item}")
        print("Importação de NCMs concluída.")
    except FileNotFoundError:
        print(f"Erro: Arquivo '{filepath}' não encontrado. Certifique-se de que ele está na pasta correta.")
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar JSON em '{filepath}': {e}. Verifique se o arquivo JSON está bem formatado.")
    except Exception as e:
        print(f"Ocorreu um erro durante a importação de NCMs: {e}")

def import_cfops(filepath='cfops.txt'):
    print(f"Importando CFOPs de {filepath}...")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split(' - ', 1)
                if len(parts) == 2:
                    codigo = parts[0].strip()
                    descricao = parts[1].strip()
                    if codigo and descricao:
                        cfop, created = CFOP.objects.get_or_create(
                            codigo=codigo,
                            defaults={'descricao': descricao}
                        )
                        if created:
                            print(f"Adicionado CFOP: {codigo} - {descricao}")
                        # else:
                            # print(f"CFOP já existe: {codigo}")
                else:
                    print(f"Linha ignorada (formato incorreto): {line}")
        print("Importação de CFOPs concluída.")
    except FileNotFoundError:
        print(f"Erro: Arquivo '{filepath}' não encontrado. Certifique-se de que ele está na pasta correta.")
    except Exception as e:
        print(f"Ocorreu um erro durante a importação de CFOPs: {e}")


if __name__ == '__main__':
    # Certifique-se de que ncm_data.json e cfops.txt estão no mesmo diretório do script,
    # ou forneça o caminho completo para eles.
    # Por exemplo, se eles estiverem na pasta 'produtos/data/'
    # import_ncms(filepath='data/ncm_data.json')
    # import_cfops(filepath='data/cfops.txt')

    # Assumindo que ncm_data.json e cfops.txt estão no mesmo nível do seu arquivo import_data.py
    # (ou seja, dentro da pasta 'produtos/')
    import_ncms(filepath='ncm_data.json')
    import_cfops(filepath='cfops.txt')