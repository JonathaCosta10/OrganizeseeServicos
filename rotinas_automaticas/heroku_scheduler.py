"""
Inicialização do Scheduler para Ambientes Heroku
===============================================

Este módulo é usado no ambiente Heroku para garantir que o scheduler
seja inicializado corretamente.

Autor: Sistema Automatizado
Data: 18/09/2025
"""

import os
import sys
import logging
import time
from django.core.management import call_command

logger = logging.getLogger('heroku_scheduler')

def iniciar_scheduler_heroku():
    """Inicializa o scheduler no ambiente Heroku"""
    try:
        # Verificar se estamos no Heroku
        is_heroku = os.environ.get('DYNO') is not None
        
        if not is_heroku:
            return False
        
        logger.info("🚀 Inicializando scheduler no ambiente Heroku...")
        
        # Dar um tempo para o servidor inicializar completamente
        time.sleep(5)
        
        # Fechar conexões antigas que possam estar abertas
        from django.db import close_old_connections
        close_old_connections()
        
        # Verificar duplicatas e limpar fila
        from rotinas_automaticas.scheduler_services import SchedulerService
        scheduler = SchedulerService()
        
        try:
            # Verificar e corrigir itens com horários desatualizados
            corrigidos = scheduler.corrigir_horarios_desatualizados_fila()
            if corrigidos > 0:
                logger.info(f"⚠️ Encontrados {corrigidos} item(ns) com horários desatualizados")
            
            # Verificar e limpar itens duplicados na fila
            duplicatas = scheduler.verificar_duplicatas_fila()
            if duplicatas > 0:
                logger.info(f"🧹 Limpeza: {duplicatas} item(ns) duplicado(s) removido(s)")
                
        except Exception as e:
            logger.error(f"Erro ao verificar fila: {e}")
        
        # Executar carga diária
        try:
            from rotinas_automaticas.scheduler_services import CargaDiariaService
            from django.utils import timezone
            import pytz
            
            BRAZIL_TZ = pytz.timezone('America/Sao_Paulo')
            agora = timezone.now().astimezone(BRAZIL_TZ)
            data_hoje = agora.date()
            
            servico = CargaDiariaService()
            resultado = servico.executar_carga_diaria(data_hoje)
            
            logger.info(f"✅ Carga diária executada com sucesso!")
            logger.info(f"   Rotinas adicionadas: {resultado.total_rotinas_adicionadas_fila}")
            
            # Verificar status da fila
            from rotinas_automaticas.models import FilaExecucao
            close_old_connections()
            
            pendentes = FilaExecucao.objects.filter(status='PENDENTE').count()
            logger.info(f"📊 Itens pendentes na fila: {pendentes}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao executar carga diária: {e}")
            return False
    
    except Exception as e:
        logger.error(f"❌ Erro geral na inicialização do scheduler Heroku: {e}")
        return False

# Inicializar monitor de scheduler
def iniciar_monitor_heroku():
    """Inicia o monitor no ambiente Heroku"""
    try:
        from rotinas_automaticas.monitor_scheduler import iniciar_monitor
        
        # Iniciar monitor em background
        monitor_iniciado = iniciar_monitor()
        
        if monitor_iniciado:
            logger.info("🔄 Monitor de scheduler iniciado com sucesso")
            return True
        else:
            logger.warning("⚠️ Monitor já estava ativo ou falhou ao iniciar")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar monitor: {e}")
        return False