# produtos/management/commands/populate_ncm.py
import json
from django.core.management.base import BaseCommand
from produtos.models import NCM
import os

class Command(BaseCommand):
    help = 'Popula a tabela NCM com dados de um arquivo JSON.'

    def handle(self, *args, **kwargs):
        # Ajuste o caminho conforme onde você colocou o arquivo JSON
        json_file_path = os.path.join(os.path.dirname(__file__), '../../data', 'ncm_data.json')

        # Certifique-se de que o arquivo existe
        if not os.path.exists(json_file_path):
            self.stderr.write(self.style.ERROR(f"Arquivo JSON não encontrado em: {json_file_path}"))
            return

        self.stdout.write(self.style.SUCCESS('Iniciando a importação de NCMs...'))

        # Opcional: Limpar a tabela existente antes de popular
        # Descomente a linha abaixo se você quiser remover todos os NCMs existentes antes de importar os novos.
        # CUIDADO: Isso apagará todos os NCMs atuais no seu banco de dados.
        # NCM.objects.all().delete()
        # self.stdout.write(self.style.WARNING('Tabela NCM limpa.'))

        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

            ncm_list = []
            # Acessa a lista de nomenclaturas dentro da chave 'Nomenclaturas'
            for item in data.get('Nomenclaturas', []):
                codigo = item.get('Codigo')
                descricao = item.get('Descricao')

                if codigo and descricao: # Garante que Código e Descrição existam
                    ncm_list.append(
                        NCM(
                            codigo=codigo,
                            descricao=descricao
                        )
                    )

            # Inserção em massa para eficiência.
            # 'ignore_conflicts=True' é útil se você rodar o comando mais de uma vez e não quiser duplicatas,
            # assumindo que 'codigo' é único no seu modelo NCM.
            NCM.objects.bulk_create(ncm_list, ignore_conflicts=True)

        self.stdout.write(self.style.SUCCESS(f'Importação de {len(ncm_list)} NCMs concluída com sucesso!'))