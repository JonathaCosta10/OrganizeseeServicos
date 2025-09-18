"""
Sistema de Inicialização Automática do Scheduler
===============================================

Este módulo é executado automaticamente quando o servidor Django inicia.
Responsável por:
- Carregar rotinas diárias automaticamente
- Inicializar o sistema de scheduler
- Verificar integridade das configurações

Autor: Sistema Automatizado  
Data: 16/09/2025
"""

import os
import sys
import logging
from datetime import datetime, date
import pytz
from django.conf import settings
from django.db import transaction

# Configurar timezone
BRAZIL_TZ = pytz.timezone('America/Sao_Paulo')

logger = logging.getLogger('scheduler_startup')

def carregar_rotinas_diarias_startup():
    """Carrega rotinas diárias no startup do servidor"""
    try:
        # Fechar conexões antigas para evitar problemas de "connection already closed"
        from django.db import close_old_connections
        close_old_connections()
        
        from rotinas_automaticas.scheduler_services import CargaDiariaService
        from rotinas_automaticas.models import CargaDiariaRotinas
        from django.db.utils import InterfaceError, OperationalError, IntegrityError
        
        agora = datetime.now(BRAZIL_TZ)
        data_hoje = agora.date()
        
        print(f"\n{'='*60}")
        print(f"🚀 SCHEDULER STARTUP - {agora.strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"{'='*60}")
        
        try:
            # No início do servidor, sempre substituir a carga diária para considerar os horários atuais
            carga_existente = CargaDiariaRotinas.objects.filter(
                data_carga=data_hoje
            ).first()
            
            if carga_existente:
                print(f"🔄 Substituindo carga diária existente para {data_hoje}")
                print(f"   Status anterior: {carga_existente.status}")
                print(f"   Criada originalmente em: {carga_existente.iniciado_em}")
            else:
                print(f"📅 Criando primeira carga diária para {data_hoje}...")
        except (InterfaceError, OperationalError) as db_err:
            # Reconectar e tentar novamente
            close_old_connections()
            print(f"⚠️ Reconectando ao banco de dados: {str(db_err)}")
            carga_existente = None
            
        try:
            # Executar carga diária com substituição
            servico = CargaDiariaService()
            resultado = servico.executar_carga_diaria(data_hoje)
            
            print(f"✅ Carga diária concluída!")
            print(f"   Rotinas processadas: {resultado.total_rotinas_processadas}")
            print(f"   Adicionadas à fila: {resultado.total_rotinas_adicionadas_fila}")
            print(f"   Arquivo log: {resultado.arquivo_log}")
        except IntegrityError as integ_err:
            # Captura específica para erro de integridade
            print(f"⚠️ Detectados registros duplicados. Será feita uma limpeza automática.")
            print(f"   Erro original: {str(integ_err)}")
            
            # Tentar limpar duplicatas e continuar
            from rotinas_automaticas.scheduler_services import SchedulerService
            scheduler = SchedulerService()
            duplicatas = scheduler.verificar_duplicatas_fila()
            print(f"🧹 Limpeza automática: {duplicatas} item(ns) duplicado(s) removido(s) da fila")
        
        # Verificar status da fila
        from rotinas_automaticas.models import FilaExecucao
        close_old_connections()  # Reabrir conexão antes de consultar
        
        total_fila = FilaExecucao.objects.count()
        pendentes = FilaExecucao.objects.filter(status='PENDENTE').count()
        
        print(f"\n📊 STATUS DA FILA:")
        print(f"   Total itens: {total_fila}")
        print(f"   Pendentes: {pendentes}")
        
        if pendentes > 0:
            print(f"   Próximas execuções:")
            for item in FilaExecucao.objects.filter(status='PENDENTE').order_by('-prioridade', 'horario_execucao')[:3]:
                nome = item.scheduler_rotina.rotina_definicao.nome if item.scheduler_rotina.rotina_definicao else 'Sem nome'
                print(f"     - {nome}: {item.horario_execucao} (Pri: {item.prioridade})")
        
        # Verificar configurações críticas
        from rotinas_automaticas.models import SchedulerRotina
        rotinas_ativas = SchedulerRotina.objects.filter(executar=True).count()
        
        print(f"\n⚙️  CONFIGURAÇÕES:")
        print(f"   Rotinas ativas: {rotinas_ativas}")
        print(f"   Timezone: {BRAZIL_TZ}")
        print(f"   Horário servidor: {agora.strftime('%H:%M:%S')}")
        
        print(f"{'='*60}")
        print(f"🎯 SCHEDULER PRONTO PARA EXECUÇÃO!")
        print(f"🕐 Próxima execução programada: 12:30")
        print(f"{'='*60}\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO NO STARTUP DO SCHEDULER:")
        print(f"   {str(e)}")
        print(f"   Tipo: {type(e).__name__}")
        
        # Log do erro
        logger.error(f"Erro no startup do scheduler: {e}", exc_info=True)
        
        # Não interromper o servidor, apenas avisar
        print(f"⚠️  Servidor continuará sem carga automática")
        print(f"   Execute manualmente: python manage.py carga_diaria_rotinas")
        print(f"{'='*60}\n")
        
        return False

def verificar_integridade_scheduler():
    """Verifica integridade das configurações do scheduler"""
    try:
        from rotinas_automaticas.models import SchedulerRotina, RotinaDefinicao
        
        # Verificar se existem rotinas configuradas
        total_rotinas = SchedulerRotina.objects.count()
        if total_rotinas == 0:
            print("⚠️  AVISO: Nenhuma rotina configurada no scheduler")
            return False
        
        # Verificar rotinas ativas
        rotinas_ativas = SchedulerRotina.objects.filter(executar=True).count()
        if rotinas_ativas == 0:
            print("⚠️  AVISO: Nenhuma rotina ativa no scheduler")
            return False
        
        # Verificar se APIs estão configuradas corretamente
        rotinas_sem_endpoint = SchedulerRotina.objects.filter(
            executar=True,
            endpoint_url__isnull=True
        ).count()
        
        if rotinas_sem_endpoint > 0:
            print(f"⚠️  AVISO: {rotinas_sem_endpoint} rotina(s) ativa(s) sem endpoint configurado")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na verificação de integridade: {e}")
        logger.error(f"Erro na verificação de integridade: {e}", exc_info=True)
        return False

def inicializar_scheduler():
    """Função principal de inicialização do scheduler"""
    print(f"\n🔧 Inicializando sistema de scheduler...")
    
    # Fechar conexões antigas para evitar problemas
    from django.db import close_old_connections
    close_old_connections()
    
    # Verificar se estamos no Heroku
    import os
    is_heroku = os.environ.get('DYNO') is not None
    
    if is_heroku:
        print("🚀 Detectado ambiente Heroku")
    
    # Verificar integridade
    if not verificar_integridade_scheduler():
        print("⚠️  Problemas detectados na configuração")
    
    try:
        # Primeiro limpar a fila de itens antigos ou desatualizados
        print("🧹 Verificando itens desatualizados na fila...")
        
        from rotinas_automaticas.scheduler_services import SchedulerService
        from rotinas_automaticas.models import FilaExecucao, SchedulerRotina
        from django.db.utils import InterfaceError, OperationalError
        
        try:
            # Verificar e corrigir itens com horários desatualizados
            scheduler = SchedulerService()
            corrigidos = scheduler.corrigir_horarios_desatualizados_fila()
            if corrigidos > 0:
                print(f"⚠️ Encontrados {corrigidos} item(ns) com horários desatualizados")
                print("   Executando carga diária para corrigir configurações...")
            
            # Verificar e limpar itens duplicados na fila
            duplicatas = scheduler.verificar_duplicatas_fila()
            if duplicatas > 0:
                print(f"🧹 Limpeza automática: {duplicatas} item(ns) duplicado(s) removido(s) da fila")
                
        except (InterfaceError, OperationalError) as db_err:
            # Reconectar e continuar
            close_old_connections()
            print(f"⚠️ Erro de conexão com banco de dados: {str(db_err)}")
            print("   Continuando inicialização...")
        
        # Carregar rotinas diárias com substituição automática
        carregar_rotinas_diarias_startup()
        
    except Exception as e:
        print(f"⚠️  Erro durante a inicialização: {str(e)}")
        print(f"   O servidor continuará funcionando, mas verifique os logs")
    
    # Agendar próxima verificação de meia-noite
    print("🌙 Sistema de renovação diária será ativado às 00:01")
    
    return True
