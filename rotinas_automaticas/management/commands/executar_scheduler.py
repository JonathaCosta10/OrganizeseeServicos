"""
Comando Django para executar o scheduler de rotinas
==================================================

Usage: python manage.py executar_scheduler [--loop] [--intervalo 60]
"""

import time
from django.core.management.base import BaseCommand
from rotinas_automaticas.scheduler_services import SchedulerService


class Command(BaseCommand):
    help = 'Executa o scheduler de rotinas'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--loop',
            action='store_true',
            help='Executa em loop contínuo',
        )
        
        parser.add_argument(
            '--intervalo',
            type=int,
            default=60,
            help='Intervalo em segundos entre execuções (default: 60)',
        )
        
        parser.add_argument(
            '--limite',
            type=int,
            help='Limite de rotinas a executar por ciclo',
        )
    
    def handle(self, *args, **options):
        service = SchedulerService()
        
        self.stdout.write('Iniciando scheduler de rotinas...')
        
        if options['loop']:
            self.stdout.write(f'Modo loop ativado - intervalo: {options["intervalo"]} segundos')
            
            try:
                while True:
                    resultado = service.executor.executar_fila(limite_execucoes=options.get('limite'))
                    
                    if resultado['total_executadas'] > 0:
                        self.stdout.write(
                            f'Ciclo executado - {resultado["total_sucesso"]} sucessos, '
                            f'{resultado["total_erro"]} erros'
                        )
                    
                    time.sleep(options['intervalo'])
                    
            except KeyboardInterrupt:
                self.stdout.write('\nScheduler interrompido pelo usuário')
                
        else:
            # Execução única
            resultado = service.executor.executar_fila(limite_execucoes=options.get('limite'))
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Scheduler executado!\n'
                    f'Total executadas: {resultado["total_executadas"]}\n'
                    f'Sucessos: {resultado["total_sucesso"]}\n'
                    f'Erros: {resultado["total_erro"]}'
                )
            )
            
            # Mostrar detalhes das execuções
            for execucao in resultado['execucoes']:
                item = execucao['item_fila']
                status = 'SUCESSO' if execucao['sucesso'] else 'ERRO'
                self.stdout.write(
                    f'  - {item.scheduler_rotina.rotina_definicao.nome_exibicao}: {status}'
                )
