#!/usr/bin/env python
"""
Script de Monitoramento Rápido - Teste de Prioridades
"""

import os
import sys
import django
import time
from datetime import datetime, timedelta
import subprocess
import pytz

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'servicos.settings')
django.setup()

from rotinas_automaticas.models import FilaExecucao, LogScheduler

def executar_scheduler():
    """Executa o comando do scheduler"""
    try:
        result = subprocess.run([
            sys.executable, 'manage.py', 'executar_scheduler', '--limite', '10'
        ], capture_output=True, text=True, cwd=os.getcwd())
        
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Scheduler executado:")
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"Erro ao executar scheduler: {e}")
        return False

def verificar_fila():
    """Verifica status da fila"""
    tz = pytz.timezone('America/Sao_Paulo')
    agora = datetime.now(tz)
    
    total = FilaExecucao.objects.count()
    pendentes = FilaExecucao.objects.filter(status='PENDENTE').count()
    executando = FilaExecucao.objects.filter(status='EM_EXECUCAO').count()
    concluidas = FilaExecucao.objects.filter(status='CONCLUIDA').count()
    recovery = FilaExecucao.objects.filter(status='RECOVERY').count()
    
    print(f"\n=== STATUS [{agora.strftime('%H:%M:%S')}] ===")
    print(f"Total: {total} | Pendentes: {pendentes} | Executando: {executando} | Concluídas: {concluidas} | Recovery: {recovery}")
    
    if executando > 0 or pendentes > 0:
        print("\nOrdem de execução (por prioridade):")
        for item in FilaExecucao.objects.filter(status__in=['PENDENTE', 'EM_EXECUCAO']).order_by('-prioridade'):
            nome = item.scheduler_rotina.rotina_definicao.nome if item.scheduler_rotina.rotina_definicao else 'Sem nome'
            print(f"  {item.prioridade:3d} - {nome}: {item.status}")
    
    return pendentes, executando, concluidas

def main():
    """Função principal de monitoramento"""
    print("🎯 TESTE DE PRIORIDADES - SCHEDULER")
    print("⏰ Rotinas agendadas para 09:50:00")
    print("🔧 Downloads (Prioridade 100) → Carga (Prioridade 50)")
    print("="*50)
    
    contador = 0
    try:
        while contador < 20:  # Máximo 10 minutos de monitoramento
            contador += 1
            tz = pytz.timezone('America/Sao_Paulo')
            agora = datetime.now(tz)
            
            # Verificar fila
            pendentes, executando, concluidas = verificar_fila()
            
            # Executar scheduler se houver pendentes ou executando
            if pendentes > 0 or executando > 0:
                executar_scheduler()
            
            # Se todas concluídas, mostrar resumo final
            if pendentes == 0 and executando == 0 and concluidas >= 3:
                print("\n🎉 TESTE CONCLUÍDO!")
                
                # Mostrar ordem final
                print("\n=== RESULTADO FINAL ===")
                items = FilaExecucao.objects.all().order_by('finalizado_em')
                for i, item in enumerate(items, 1):
                    nome = item.scheduler_rotina.rotina_definicao.nome if item.scheduler_rotina.rotina_definicao else 'Sem nome'
                    inicio = item.iniciado_em.strftime('%H:%M:%S') if item.iniciado_em else 'N/A'
                    fim = item.finalizado_em.strftime('%H:%M:%S') if item.finalizado_em else 'N/A'
                    print(f"{i}º - {nome} (Pri: {item.prioridade}) | {inicio} → {fim} | {item.status}")
                
                # Verificar se ordem respeitou prioridades
                downloads_finalizados = []
                carga_finalizada = None
                
                for item in items:
                    nome = item.scheduler_rotina.rotina_definicao.nome if item.scheduler_rotina.rotina_definicao else ''
                    if 'baixar' in nome:
                        downloads_finalizados.append(item.finalizado_em)
                    elif 'carregar' in nome:
                        carga_finalizada = item.finalizado_em
                
                if downloads_finalizados and carga_finalizada:
                    downloads_ok = all(d <= carga_finalizada for d in downloads_finalizados if d)
                    print(f"\n✅ Prioridades respeitadas: {'SIM' if downloads_ok else 'NÃO'}")
                
                break
            
            print(f"⏱️  Aguardando... ({contador}/20)")
            time.sleep(30)
            
    except KeyboardInterrupt:
        print("\n🛑 Teste interrompido")

if __name__ == "__main__":
    main()
