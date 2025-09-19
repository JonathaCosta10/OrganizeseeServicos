"""
Comando Django para atualizar as URLs das rotinas do scheduler para usar a variável BASE_URL
=======================================================================================

Usage: python manage.py atualizar_urls_scheduler
"""

from django.core.management.base import BaseCommand
from django.conf import settings
from rotinas_automaticas.models import SchedulerRotina


class Command(BaseCommand):
    help = 'Atualiza as URLs das rotinas do scheduler para usar a variável BASE_URL'

    def handle(self, *args, **options):
        rotinas_atualizadas = 0
        
        # Listar todas as rotinas com URLs que contém localhost ou 127.0.0.1
        rotinas_para_atualizar = SchedulerRotina.objects.filter(
            endpoint_url__contains='127.0.0.1'
        )
        
        self.stdout.write(f"Encontradas {rotinas_para_atualizar.count()} rotinas com URLs fixas para atualizar.")
        
        for rotina in rotinas_para_atualizar:
            # Substituir a parte fixa da URL pela variável BASE_URL
            url_antiga = rotina.endpoint_url
            
            # Extrair o caminho da URL (tudo após o domínio/porta)
            caminho = url_antiga.split('/', 3)[-1]
            nova_url = f"{settings.BASE_URL}/{caminho}"
            
            rotina.endpoint_url = nova_url
            rotina.save()
            
            rotinas_atualizadas += 1
            self.stdout.write(f"Rotina {rotina.rotina_definicao.nome_exibicao} atualizada: {url_antiga} -> {nova_url}")
        
        # Verificar outras possíveis URLs fixas (localhost)
        rotinas_para_atualizar = SchedulerRotina.objects.filter(
            endpoint_url__contains='localhost'
        )
        
        for rotina in rotinas_para_atualizar:
            url_antiga = rotina.endpoint_url
            caminho = url_antiga.split('/', 3)[-1]
            nova_url = f"{settings.BASE_URL}/{caminho}"
            
            rotina.endpoint_url = nova_url
            rotina.save()
            
            rotinas_atualizadas += 1
            self.stdout.write(f"Rotina {rotina.rotina_definicao.nome_exibicao} atualizada: {url_antiga} -> {nova_url}")
        
        self.stdout.write(self.style.SUCCESS(f"Total de {rotinas_atualizadas} rotinas atualizadas com sucesso!"))