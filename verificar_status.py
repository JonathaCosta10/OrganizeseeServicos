import os
import sys
import django

# Adicione o diretório do projeto ao path do sistema
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configurar o ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'servicos.settings')
django.setup()

# Importar após configuração do Django
from rotinas_automaticas.models import FilaExecucao, CargaDiariaRotinas, SchedulerRotina
from datetime import datetime
import pytz

BRAZIL_TZ = pytz.timezone('America/Sao_Paulo')

def mostrar_status_sistema():
    """Mostra o status geral do sistema"""
    print("\n" + "="*60)
    print("📊 STATUS DO SISTEMA DE ROTINAS - {}".format(datetime.now(BRAZIL_TZ).strftime('%d/%m/%Y %H:%M:%S')))
    print("="*60)
    
    # Estatísticas gerais
    total_fila = FilaExecucao.objects.count()
    pendentes = FilaExecucao.objects.filter(status='PENDENTE').count()
    erros = FilaExecucao.objects.filter(status='ERRO').count()
    recovery = FilaExecucao.objects.filter(status='RECOVERY').count()
    executando = FilaExecucao.objects.filter(status='EXECUTANDO').count()
    
    # Carga diária
    hoje = datetime.now(BRAZIL_TZ).date()
    carga_hoje = CargaDiariaRotinas.objects.filter(data_carga=hoje).first()
    carga_status = carga_hoje.status if carga_hoje else "NÃO ENCONTRADA"
    
    # Rotinas ativas
    rotinas_ativas = SchedulerRotina.objects.filter(executar=True).all()
    
    print("\n📋 FILA DE EXECUÇÃO:")
    print(f"   Total de itens: {total_fila}")
    print(f"   Pendentes: {pendentes}")
    print(f"   Em execução: {executando}")
    print(f"   Erros: {erros}")
    print(f"   Recovery: {recovery}")
    
    print("\n📅 CARGA DIÁRIA:")
    if carga_hoje:
        print(f"   Data: {carga_hoje.data_carga}")
        print(f"   Status: {carga_hoje.status}")
        print(f"   Criada em: {carga_hoje.criado_em}")
        print(f"   Atualizada em: {carga_hoje.atualizado_em}")
    else:
        print("   ❌ Carga diária não encontrada para hoje")
    
    print("\n⚙️ ROTINAS ATIVAS:")
    if rotinas_ativas:
        for rotina in rotinas_ativas:
            print(f"   - {rotina.nome} ({rotina.tipo})")
            print(f"     Horário: {rotina.horario_execucao}")
            print(f"     Dias da semana: {rotina.dias_semana_texto()}")
    else:
        print("   ❌ Nenhuma rotina ativa configurada")
    
    print("\n🕓 ITENS PENDENTES NA FILA:")
    itens_pendentes = FilaExecucao.objects.filter(status='PENDENTE').order_by('horario_execucao')[:5]
    if itens_pendentes:
        for item in itens_pendentes:
            print(f"   - {item.scheduler_rotina.nome} ({item.data_execucao} {item.horario_execucao})")
    else:
        print("   ✅ Nenhum item pendente na fila")
    
    print("\n📊 ÚLTIMAS EXECUÇÕES:")
    ultimas_execucoes = FilaExecucao.objects.order_by('-atualizado_em')[:5]
    if ultimas_execucoes:
        for exec in ultimas_execucoes:
            status_emoji = "✅" if exec.status == 'CONCLUIDO' else "❌" if exec.status == 'ERRO' else "⏳" if exec.status == 'EXECUTANDO' else "⏱️"
            print(f"   {status_emoji} {exec.scheduler_rotina.nome} - {exec.status} - {exec.atualizado_em}")
    else:
        print("   ❌ Nenhuma execução registrada")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    mostrar_status_sistema()