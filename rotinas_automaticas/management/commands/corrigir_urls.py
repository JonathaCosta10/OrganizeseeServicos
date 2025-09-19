"""
Script para executar o script de correção diretamente como um comando Django
===========================================================================

Uso: python manage.py corrigir_urls
"""

from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Corrige as URLs das rotinas para usar a URL correta no Heroku'

    def handle(self, *args, **options):
        self.stdout.write("Iniciando correção de URLs...")
        
        try:
            # Importar e executar o script de correção
            from corrigir_direto import corrigir_urls
            corrigir_urls()
            
            self.stdout.write(self.style.SUCCESS("Correção de URLs concluída com sucesso!"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Erro durante a correção: {str(e)}"))
            raise