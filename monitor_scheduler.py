#!/usr/bin/env python
"""
Script de Monitoramento Automático do Scheduler
Executa o scheduler a cada minuto e monitora os logs
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
    erro = FilaExecucao.objects.filter(status='ERRO').count()
    
    print(f"\n=== STATUS DA FILA [{agora.strftime('%H:%M:%S')}] ===")
    print(f"Total: {total} | Pendentes: {pendentes} | Executando: {executando} | Concluídas: {concluidas} | Erro: {erro}")
    
    if executando > 0 or pendentes > 0:
        print("\nItens ativos:")
        for item in FilaExecucao.objects.filter(status__in=['PENDENTE', 'EM_EXECUCAO']).order_by('data_execucao'):
            nome = item.scheduler_rotina.rotina_definicao.nome if item.scheduler_rotina.rotina_definicao else 'Sem nome'
            horario = item.horario_execucao.strftime('%H:%M:%S')
            print(f"- {nome}: {item.status} (agendado: {horario})")
    
    return pendentes, executando, concluidas, erro

def verificar_logs_recentes():
    """Mostra logs recentes"""
    logs_recentes = LogScheduler.objects.filter(
        criado_em__gte=datetime.now() - timedelta(minutes=5)
    ).order_by('-criado_em')[:5]
    
    if logs_recentes:
        print("\n=== LOGS RECENTES (últimos 5 min) ===")
        for log in logs_recentes:
            tempo = log.criado_em.strftime('%H:%M:%S')
            print(f"[{tempo}] {log.nivel} - {log.componente}: {log.mensagem}")

def main():
    """Função principal de monitoramento"""
    print("🚀 MONITORAMENTO AUTOMÁTICO DO SCHEDULER INICIADO")
    print("⏰ Rotinas agendadas para 09:34:00")
    print("🔄 Verificando a cada 30 segundos...")
    print("❌ Pressione Ctrl+C para parar")
    print("="*60)
    
    try:
        while True:
            tz = pytz.timezone('America/Sao_Paulo')
            agora = datetime.now(tz)
            
            # Verificar fila
            pendentes, executando, concluidas, erro = verificar_fila()
            
            # Executar scheduler se houver pendentes ou executando
            if pendentes > 0 or executando > 0:
                executar_scheduler()
            
            # Verificar logs recentes
            verificar_logs_recentes()
            
            # Se todas concluídas, mostrar resumo final
            if pendentes == 0 and executando == 0 and concluidas > 0:
                print("\n🎉 TODAS AS ROTINAS CONCLUÍDAS!")
                print(f"✅ Concluídas: {concluidas}")
                print(f"❌ Erros: {erro}")
                
                # Mostrar logs finais
                print("\n=== LOG FINAL DAS EXECUÇÕES ===")
                for item in FilaExecucao.objects.all().order_by('data_execucao'):
                    nome = item.scheduler_rotina.rotina_definicao.nome if item.scheduler_rotina.rotina_definicao else 'Sem nome'
                    print(f"- {nome}: {item.status}")
                    if item.saida_stdout:
                        print(f"  Resultado: {item.saida_stdout[:100]}...")
                
                print("\n📊 Verificar logs completos em: static/logs/")
                break
            
            print(f"\n⏱️  Próxima verificação em 30s... (atual: {agora.strftime('%H:%M:%S')})")
            time.sleep(30)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Monitoramento interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro no monitoramento: {e}")

if __name__ == "__main__":
    main()
