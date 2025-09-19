"""
Script direto para corrigir URLs no banco de dados do Heroku
=================================================================
"""

from django.conf import settings
from rotinas_automaticas.models import SchedulerRotina, FilaExecucao
import os

def corrigir_urls():
    """Corrige todas as URLs de rotinas de forma direta e eficiente"""
    print("Iniciando correção de URLs no banco de dados...")
    
    # Verificar BASE_URL configurada
    base_url = settings.BASE_URL
    print(f"BASE_URL configurada: {base_url}")
    
    # Configurar URLs de acordo com ambiente
    is_heroku = os.environ.get('DYNO') is not None
    
    # No Heroku, usar a URL pública
    if is_heroku:
        if not base_url or base_url.startswith('http://127.0.0.1') or base_url.startswith('http://localhost'):
            base_url = "https://service-organizesee-5f72417f9331.herokuapp.com"
            print(f"Ambiente Heroku detectado. Usando URL: {base_url}")
            
            # Também atualizar a configuração
            settings.BASE_URL = base_url
    
    # Reconfigurando completamente todas as rotinas
    print("Reconfigurando todas as rotinas do scheduler...")
    
    # Rotina Download B3
    rotina_b3 = SchedulerRotina.objects.filter(
        rotina_definicao__nome_exibicao__icontains='Download B3'
    ).first()
    
    if rotina_b3:
        rotina_b3.endpoint_url = f"{base_url}/api/download_b3/"
        rotina_b3.save()
        print(f"✓ Corrigido: Download B3 -> {rotina_b3.endpoint_url}")
    
    # Rotina Download CVM
    rotina_cvm = SchedulerRotina.objects.filter(
        rotina_definicao__nome_exibicao__icontains='Download CVM'
    ).first()
    
    if rotina_cvm:
        rotina_cvm.endpoint_url = f"{base_url}/api/download_cvm/"
        rotina_cvm.save()
        print(f"✓ Corrigido: Download CVM -> {rotina_cvm.endpoint_url}")
    
    # Rotina Carregar Preços
    rotina_precos = SchedulerRotina.objects.filter(
        rotina_definicao__nome_exibicao__icontains='Carga Trade'
    ).first()
    
    if rotina_precos:
        rotina_precos.endpoint_url = f"{base_url}/api/static_arquivos/"
        rotina_precos.save()
        print(f"✓ Corrigido: Carga Trade -> {rotina_precos.endpoint_url}")
    
    # Limpar itens da fila com erro
    print("Limpando itens da fila com erro...")
    FilaExecucao.objects.filter(status='ERRO').delete()
    print("✓ Fila de erros limpa")
    
    # Resetar qualquer rotina travada
    FilaExecucao.objects.filter(status='EXECUTANDO').update(status='PENDENTE')
    print("✓ Rotinas travadas resetadas")
    
    # Verificação final
    print("\nVerificando URLs finais:")
    for rotina in SchedulerRotina.objects.filter(endpoint_url__isnull=False).exclude(endpoint_url=''):
        print(f"- {rotina.rotina_definicao.nome_exibicao}: {rotina.endpoint_url}")
        
    print("\nCorreção concluída!")

# Executar a função de correção
corrigir_urls()