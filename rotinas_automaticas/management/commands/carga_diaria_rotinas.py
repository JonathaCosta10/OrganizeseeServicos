"""
Comando Django para executar carga diária de rotinas
===================================================

Usage: python manage.py carga_diaria_rotinas [--data YYYY-MM-DD]
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, date
from rotinas_automaticas.scheduler_services import CargaDiariaService


class Command(BaseCommand):
    help = 'Executa a carga diária de rotinas para o scheduler'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--data',
            type=str,
            help='Data para carga (formato YYYY-MM-DD). Se não informado, usa data atual.',
        )
        
        parser.add_argument(
            '--force',
            action='store_true',
            help='Força execução mesmo se já existir carga para a data',
        )
    
    def handle(self, *args, **options):
        service = CargaDiariaService()
        
        # Determinar data
        if options['data']:
            try:
                data_execucao = datetime.strptime(options['data'], '%Y-%m-%d').date()
            except ValueError:
                self.stdout.write(
                    self.style.ERROR('Formato de data inválido. Use YYYY-MM-DD')
                )
                return
        else:
            data_execucao = timezone.now().date()
        
        self.stdout.write(f'Iniciando carga diária para {data_execucao}...')
        
        try:
            carga = service.executar_carga_diaria(data_execucao)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Carga concluída com sucesso!\n'
                    f'Rotinas processadas: {carga.total_rotinas_processadas}\n'
                    f'Rotinas adicionadas à fila: {carga.total_rotinas_adicionadas_fila}\n'
                    f'Rotinas ignoradas: {carga.total_rotinas_ignoradas}\n'
                    f'Log gerado: {carga.arquivo_log}'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erro na carga diária: {e}')
            )
            raise
