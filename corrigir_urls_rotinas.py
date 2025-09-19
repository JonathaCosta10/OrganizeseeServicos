"""
Script para corrigir URLs de rotinas diretamente no banco de dados
=================================================================

Este script corrige as URLs fixas para URLs dinâmicas no banco de dados.
Execução: python corrigir_urls_rotinas.py
"""

import os
import django
import sys

# Configurar ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'servicos.settings')
django.setup()

# Importar após configurar o ambiente
from rotinas_automaticas.models import SchedulerRotina
from django.conf import settings

def corrigir_urls_rotinas():
    """Corrige todas as URLs de rotinas para usar a variável BASE_URL"""
    print(f"BASE_URL atual: {settings.BASE_URL}")
    
    # Buscar todas as rotinas com endpoint
    rotinas = SchedulerRotina.objects.filter(endpoint_url__isnull=False).exclude(endpoint_url='')
    
    print(f"Total de rotinas com endpoint: {rotinas.count()}")
    
    # Iterar sobre rotinas e corrigir URLs
    count_atualizadas = 0
    for rotina in rotinas:
        nome_rotina = rotina.rotina_definicao.nome_exibicao
        url_antiga = rotina.endpoint_url
        
        # Verificar se a URL precisa ser atualizada
        if '127.0.0.1' in url_antiga or 'localhost' in url_antiga:
            # Extrair o caminho da URL (após o domínio e porta)
            try:
                caminho = url_antiga.split('/', 3)[3]  # http://127.0.0.1:8000/api/download_b3/ -> api/download_b3/
                nova_url = f"{settings.BASE_URL}/{caminho}"
                
                print(f"Atualizando rotina: {nome_rotina}")
                print(f"  URL Antiga: {url_antiga}")
                print(f"  URL Nova: {nova_url}")
                
                rotina.endpoint_url = nova_url
                rotina.save()
                
                count_atualizadas += 1
            except Exception as e:
                print(f"Erro ao processar URL {url_antiga}: {str(e)}")
        else:
            print(f"Rotina já está correta: {nome_rotina} - {url_antiga}")
    
    print(f"\nResultado: {count_atualizadas} rotinas atualizadas de {rotinas.count()} total")
    
    # Verificar valores atualizados
    print("\nVerificando URLs das rotinas:")
    for rotina in SchedulerRotina.objects.filter(endpoint_url__isnull=False).exclude(endpoint_url=''):
        nome_rotina = rotina.rotina_definicao.nome_exibicao
        url_atual = rotina.endpoint_url
        print(f"- {nome_rotina}: {url_atual}")

if __name__ == "__main__":
    print("Iniciando correção de URLs de rotinas...")
    corrigir_urls_rotinas()
    print("Concluído!")