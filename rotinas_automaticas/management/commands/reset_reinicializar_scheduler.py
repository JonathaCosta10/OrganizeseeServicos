"""
Management command para redefinir e recriar todas as rotinas do scheduler
========================================================================

Este comando exclui todas as rotinas existentes e recria com as configurações
atualizadas usando o valor correto de BASE_URL.

Uso: python manage.py reset_reinicializar_scheduler
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.conf import settings
from rotinas_automaticas.models import SchedulerRotina, RotinaDefinicao, FilaExecucao
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Redefine e reinicializa todas as rotinas do scheduler'

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                # 1. Backup das rotinas existentes para referência
                self.stdout.write("Fazendo backup das rotinas existentes...")
                rotinas_backup = []
                for rotina in SchedulerRotina.objects.select_related('rotina_definicao').all():
                    rotinas_backup.append({
                        'nome': rotina.rotina_definicao.nome,
                        'tipo_execucao': rotina.tipo_execucao,
                        'tipo_rotina': rotina.tipo_rotina,
                        'horario_execucao': rotina.horario_execucao,
                        'executar': rotina.executar,
                    })
                
                # 2. Remover itens da fila pendentes
                self.stdout.write("Removendo itens pendentes da fila...")
                count_fila = FilaExecucao.objects.filter(status='PENDENTE').delete()[0]
                self.stdout.write(f"  {count_fila} itens removidos da fila")
                
                # 3. Excluir todas as rotinas (scheduler e definições)
                self.stdout.write("Excluindo rotinas existentes...")
                count_scheduler = SchedulerRotina.objects.all().delete()[0]
                count_definicao = RotinaDefinicao.objects.all().delete()[0]
                self.stdout.write(f"  {count_scheduler} rotinas do scheduler excluídas")
                self.stdout.write(f"  {count_definicao} definições de rotinas excluídas")
                
                # 4. Reinicializar o scheduler
                self.stdout.write("Reinicializando scheduler com novas configurações...")
                
                # Verificar BASE_URL configurada
                base_url = settings.BASE_URL
                self.stdout.write(f"BASE_URL configurada: {base_url}")
                
                # Executar comando de inicialização
                from django.core.management import call_command
                call_command('inicializar_scheduler', verbosity=2)
                
                # 5. Verificar novas URLs
                self.stdout.write("\nVerificando novas URLs das rotinas:")
                for rotina in SchedulerRotina.objects.select_related('rotina_definicao').all():
                    nome_rotina = rotina.rotina_definicao.nome_exibicao
                    url_atual = rotina.endpoint_url or "N/A"
                    self.stdout.write(f"- {nome_rotina}: {url_atual}")
                
                self.stdout.write(self.style.SUCCESS("Redefinição e reinicialização concluídas com sucesso!"))
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Erro durante o processo: {str(e)}"))
            raise