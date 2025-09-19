"""
Script direto para corrigir URLs no banco de dados do Heroku
=================================================================
"""

from django.conf import settings
from rotinas_automaticas.models import SchedulerRotina, FilaExecucao

def corrigir_urls():
    """Corrige todas as URLs de rotinas de forma direta e eficiente"""
    print("Iniciando correção de URLs no banco de dados...")
    
    # Verificar BASE_URL configurada
    base_url = settings.BASE_URL
    print(f"BASE_URL configurada: {base_url}")
    
    # Atualizar todas as rotinas com URLs fixas
    rotinas_atualizadas = 0
    
    for rotina in SchedulerRotina.objects.filter(endpoint_url__isnull=False).exclude(endpoint_url=''):
        url_antiga = rotina.endpoint_url
        nome_rotina = rotina.rotina_definicao.nome_exibicao
        
        # Para Download B3
        if 'download_b3' in url_antiga:
            rotina.endpoint_url = f"{base_url}/api/download_b3/"
            rotina.save()
            rotinas_atualizadas += 1
            print(f"✓ Corrigido: {nome_rotina} -> {rotina.endpoint_url}")
            
        # Para Download CVM
        elif 'download_cvm' in url_antiga:
            rotina.endpoint_url = f"{base_url}/api/download_cvm/"
            rotina.save()
            rotinas_atualizadas += 1
            print(f"✓ Corrigido: {nome_rotina} -> {rotina.endpoint_url}")
            
        # Para arquivos estáticos
        elif 'static_arquivos' in url_antiga:
            rotina.endpoint_url = f"{base_url}/api/static_arquivos/"
            rotina.save()
            rotinas_atualizadas += 1
            print(f"✓ Corrigido: {nome_rotina} -> {rotina.endpoint_url}")
    
    # Limpar itens da fila com erro
    itens_erro = FilaExecucao.objects.filter(status='ERRO')
    if itens_erro.exists():
        count_erros = itens_erro.count()
        itens_erro.delete()
        print(f"✓ Removidos {count_erros} itens com erro da fila")
    
    # Verificação final
    print("\nVerificando URLs finais:")
    for rotina in SchedulerRotina.objects.filter(endpoint_url__isnull=False).exclude(endpoint_url=''):
        print(f"- {rotina.rotina_definicao.nome_exibicao}: {rotina.endpoint_url}")
        
    print(f"\nTotal de {rotinas_atualizadas} rotinas atualizadas")
    print("Correção concluída!")

# Executar a função de correção
corrigir_urls()