import os
from django.core.management.base import BaseCommand
from produtos.models import CFOP # Importe o seu modelo CFOP aqui

class Command(BaseCommand):
    help = 'Carrega dados de CFOP de um arquivo de texto.'

    def add_arguments(self, parser):
        # Esta linha é essencial para que o comando aceite o caminho do arquivo como argumento.
        parser.add_argument('cfop_file', type=str, help='O caminho para o arquivo de texto CFOP.')

    def handle(self, *args, **options):
        # O caminho do arquivo é acessado através de options['cfop_file']
        file_path = options['cfop_file']

        # Verifica se o arquivo existe antes de tentar abri-lo
        if not os.path.exists(file_path):
            self.stderr.write(self.style.ERROR(f"Erro: Arquivo '{file_path}' não encontrado. Por favor, verifique o caminho."))
            return

        self.stdout.write(self.style.SUCCESS(f"Iniciando carregamento de CFOPs do arquivo: {file_path}"))
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Opcional: Limpa a tabela CFOP existente antes de carregar novos dados
            # Isso é útil se você estiver recarregando os dados e quiser garantir que não haja duplicatas ou dados antigos.
            CFOP.objects.all().delete()
            self.stdout.write(self.style.WARNING("Tabela CFOP existente limpa (todos os registros anteriores foram removidos)."))

            cfops_to_create = []
            for line in lines:
                line = line.strip() # Remove espaços em branco e quebras de linha

                # Ignora linhas vazias, comentários (linhas que começam com #) ou linhas que não contêm " - "
                if not line or line.startswith('#') or ' - ' not in line:
                    continue

                try:
                    # Divide a linha no primeiro " - " para separar código e descrição
                    codigo, descricao = line.split(' - ', 1)
                    cfops_to_create.append(CFOP(codigo=codigo.strip(), descricao=descricao.strip()))
                except ValueError:
                    # Captura erros de linhas mal formatadas e as ignora
                    self.stderr.write(self.style.WARNING(f"Ignorando linha mal formatada (formato 'CODIGO - DESCRICAO' esperado): '{line}'"))
                    continue

            # Cria os objetos CFOP em massa para otimizar a inserção no banco de dados
            # `ignore_conflicts=True` evita erros se por algum motivo um código duplicado tentar ser inserido
            CFOP.objects.bulk_create(cfops_to_create, ignore_conflicts=True)
            self.stdout.write(self.style.SUCCESS(f"Total de {len(cfops_to_create)} CFOPs carregados com sucesso!"))

        except Exception as e:
            # Captura qualquer outra exceção que possa ocorrer durante o processo
            self.stderr.write(self.style.ERROR(f"Ocorreu um erro inesperado ao carregar os dados: {e}"))