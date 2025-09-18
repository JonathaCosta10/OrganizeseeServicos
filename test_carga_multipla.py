#!/usr/bin/env python
"""
Monitoramento de Teste - Carga Múltipla de Arquivos
Testa se a carga processa TODOS os arquivos dos últimos 3 dias
"""

import os
import sys
import django
import time
from datetime import datetime
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
    
    return pendentes, executando, concluidas, recovery

def verificar_arquivos_baixados():
    """Verifica arquivos TradeInformationConsolidatedFile baixados"""
    import glob
    pasta = "C:/Desenvolvendo/servicos_organizesee/static/downloadbruto"
    arquivos = glob.glob(f"{pasta}/TradeInformationConsolidatedFile*.csv")
    
    print(f"\n=== ARQUIVOS DISPONÍVEIS PARA CARGA ===")
    print(f"Arquivos TradeInformationConsolidatedFile encontrados: {len(arquivos)}")
    for arquivo in sorted(arquivos):
        nome = os.path.basename(arquivo)
        tamanho = os.path.getsize(arquivo) / (1024*1024)  # MB
        print(f"  - {nome} ({tamanho:.1f} MB)")

def main():
    """Função principal de monitoramento"""
    print("🧪 TESTE DE CARGA MÚLTIPLA - SCHEDULER")
    print("⏰ Rotinas agendadas para 10:05:00")
    print("🔄 Testando processamento de múltiplos arquivos")
    print("="*60)
    
    # Verificar arquivos disponíveis
    verificar_arquivos_baixados()
    
    try:
        contador = 0
        while contador < 20:  # Máximo 20 verificações
            contador += 1
            tz = pytz.timezone('America/Sao_Paulo')
            agora = datetime.now(tz)
            
            # Verificar fila
            pendentes, executando, concluidas, recovery = verificar_fila()
            
            # Executar scheduler se houver pendentes ou executando
            if pendentes > 0 or executando > 0:
                executar_scheduler()
            
            # Se todas concluídas, mostrar resumo final
            if pendentes == 0 and executando == 0 and concluidas > 0:
                print("\n🎉 TESTE CONCLUÍDO!")
                
                print(f"\n=== RESULTADO FINAL ===")
                for item in FilaExecucao.objects.all().order_by('-prioridade', 'finalizado_em'):
                    nome = item.scheduler_rotina.rotina_definicao.nome if item.scheduler_rotina.rotina_definicao else 'Sem nome'
                    inicio = item.iniciado_em.strftime('%H:%M:%S') if item.iniciado_em else 'N/A'
                    fim = item.finalizado_em.strftime('%H:%M:%S') if item.finalizado_em else 'N/A'
                    print(f"- {nome} (Pri: {item.prioridade}) | {inicio} → {fim} | {item.status}")
                    
                    # Mostrar detalhes especiais para carga
                    if 'carregar_precos' in nome and item.saida_stdout:
                        print(f"  Resultado: {item.saida_stdout[:200]}...")
                
                # Verificar logs específicos de carga múltipla
                print(f"\n=== LOGS DE CARGA MÚLTIPLA ===")
                logs_carga = LogScheduler.objects.filter(
                    componente='Executor',
                    mensagem__icontains='arquivos_processados'
                ).order_by('-criado_em')[:3]
                
                for log in logs_carga:
                    tempo = log.criado_em.strftime('%H:%M:%S')
                    print(f"[{tempo}] {log.mensagem}")
                
                break
            
            print(f"\n⏱️  Aguardando... ({contador}/20)")
            time.sleep(30)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Monitoramento interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro no monitoramento: {e}")

if __name__ == "__main__":
    main()
