from django.core.management.base import BaseCommand
from django.utils import timezone
import pytz
import logging

logger = logging.getLogger('iniciar_heroku_scheduler')

class Command(BaseCommand):
    help = 'Inicia o scheduler no ambiente Heroku'

    def handle(self, *args, **options):
        self.stdout.write('🚀 Iniciando o scheduler no ambiente Heroku...')
        
        try:
            # Fechar conexões antigas
            from django.db import close_old_connections
            close_old_connections()
            
            # Verificar se estamos no Heroku
            import os
            is_heroku = os.environ.get('DYNO') is not None
            
            self.stdout.write(f'Ambiente: {"Heroku" if is_heroku else "Local"}')
            
            # Importar serviços do scheduler
            from rotinas_automaticas.heroku_scheduler import iniciar_scheduler_heroku, iniciar_monitor_heroku
            
            # Iniciar scheduler
            resultado_scheduler = iniciar_scheduler_heroku()
            if resultado_scheduler:
                self.stdout.write(self.style.SUCCESS('✅ Scheduler iniciado com sucesso!'))
            else:
                self.stdout.write(self.style.WARNING('⚠️ Problemas ao iniciar o scheduler'))
            
            # Iniciar monitor
            resultado_monitor = iniciar_monitor_heroku()
            if resultado_monitor:
                self.stdout.write(self.style.SUCCESS('✅ Monitor iniciado com sucesso!'))
            else:
                self.stdout.write(self.style.WARNING('⚠️ Problemas ao iniciar o monitor'))
            
            # Verificar status da fila
            from rotinas_automaticas.models import FilaExecucao, CargaDiariaRotinas
            
            # Configurar timezone
            BRAZIL_TZ = pytz.timezone('America/Sao_Paulo')
            agora = timezone.now().astimezone(BRAZIL_TZ)
            
            # Status da fila
            total_fila = FilaExecucao.objects.count()
            pendentes = FilaExecucao.objects.filter(status='PENDENTE').count()
            
            self.stdout.write(f'📊 Status da fila:')
            self.stdout.write(f'   Total: {total_fila}')
            self.stdout.write(f'   Pendentes: {pendentes}')
            
            # Carga diária de hoje
            carga_hoje = CargaDiariaRotinas.objects.filter(
                data_carga=agora.date()
            ).first()
            
            if carga_hoje:
                self.stdout.write(f'📅 Carga diária de hoje:')
                self.stdout.write(f'   Status: {carga_hoje.status}')
                self.stdout.write(f'   Rotinas adicionadas: {carga_hoje.total_rotinas_adicionadas_fila}')
            else:
                self.stdout.write(self.style.WARNING('⚠️ Não há carga diária para hoje'))
            
            self.stdout.write(self.style.SUCCESS('✅ Inicialização concluída!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro ao iniciar scheduler: {e}'))
            logger.error(f'Erro ao iniciar scheduler: {e}', exc_info=True)