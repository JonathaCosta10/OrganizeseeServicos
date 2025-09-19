"""
Sistema de Monitoramento e Renovação Diária do Scheduler
=======================================================
Background para:
- Monitorar execução das rotinas
- Renovar carga diária às 00:01
- Executar scheduler automaticamente
- Garantir continuidade do sistema

Autor: Sistema Automatizado
Data: 17/09/2025
"""

import os
import sys
import time
import threading
import schedule
from datetime import datetime, timedelta
import pytz
import logging
from django.core.management import call_command
from django.conf import settings
from django.db import close_old_connections
from django.db.utils import InterfaceError, OperationalError

# Configurar timezone
BRAZIL_TZ = pytz.timezone('America/Sao_Paulo')

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('scheduler_monitor')

# Aumentar nível de log para DEBUG durante desenvolvimento
logger.setLevel(logging.DEBUG)

class SchedulerMonitor:
    """Monitor do sistema de scheduler"""
    
    def __init__(self):
        self.running = False
        self.thread = None
        self.ultima_execucao_scheduler = None
        self.ultima_renovacao_diaria = None
        self.inicio_monitor = None
        self.ultima_verificacao_bem_sucedida = None
        
    def start(self):
        """Inicia o monitor"""
        if self.running:
            return
            
        self.running = True
        self.inicio_monitor = datetime.now(BRAZIL_TZ)
        self.thread = threading.Thread(target=self._run_monitor, daemon=True)
        self.thread.start()
        
        # Agendar tarefas
        self._agendar_tarefas()
        
        logger.info("🔄 Monitor do scheduler iniciado")
        
    def stop(self):
        """Para o monitor"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("🛑 Monitor do scheduler parado")
        
    def verificar_saude_externa(self):
        """Método para verificar a saúde do monitor a partir de uma chamada externa (view, cron, etc)"""
        agora = datetime.now(BRAZIL_TZ)
        
        # Se o monitor não estiver rodando ou sem verificação recente, reiniciar
        if not self.running or self.thread is None or not self.thread.is_alive():
            logger.critical("🚨 Monitor não está rodando! Reiniciando...")
            try:
                self.stop()
                time.sleep(2)
                self.start()
                return {"status": "reiniciado", "mensagem": "Monitor não estava rodando e foi reiniciado"}
            except Exception as e:
                logger.critical(f"❌ Falha ao reiniciar o monitor: {e}", exc_info=True)
                return {"status": "erro", "mensagem": f"Falha ao reiniciar o monitor: {str(e)}"}
        
        # Verificar se houve atualização recente
        if self.ultima_verificacao_bem_sucedida:
            tempo_sem_atualizacao = (agora - self.ultima_verificacao_bem_sucedida).total_seconds() / 60
            
            # Se não houver atualização há mais de 10 minutos, reiniciar
            if tempo_sem_atualizacao > 10:
                logger.warning(f"⚠️ Monitor sem atualização há {tempo_sem_atualizacao:.1f} minutos! Reiniciando...")
                try:
                    self.stop()
                    time.sleep(2)
                    self.start()
                    return {"status": "reiniciado", "mensagem": f"Monitor estava travado há {tempo_sem_atualizacao:.1f} minutos e foi reiniciado"}
                except Exception as e:
                    logger.critical(f"❌ Falha ao reiniciar o monitor após inatividade: {e}", exc_info=True)
                    return {"status": "erro", "mensagem": f"Falha ao reiniciar o monitor: {str(e)}"}
            else:
                return {"status": "ok", "mensagem": f"Monitor saudável, última atualização há {tempo_sem_atualizacao:.1f} minutos"}
        else:
            # Se nunca houve verificação bem-sucedida desde o início, verificar tempo desde início
            tempo_desde_inicio = (agora - self.inicio_monitor).total_seconds() / 60 if self.inicio_monitor else float('inf')
            
            if tempo_desde_inicio > 5:  # Mais de 5 minutos sem verificação bem-sucedida
                logger.warning(f"⚠️ Monitor sem verificação bem-sucedida há {tempo_desde_inicio:.1f} minutos desde o início! Reiniciando...")
                try:
                    self.stop()
                    time.sleep(2)
                    self.start()
                    return {"status": "reiniciado", "mensagem": f"Monitor sem verificação bem-sucedida desde o início há {tempo_desde_inicio:.1f} minutos e foi reiniciado"}
                except Exception as e:
                    logger.critical(f"❌ Falha ao reiniciar o monitor após inatividade desde o início: {e}", exc_info=True)
                    return {"status": "erro", "mensagem": f"Falha ao reiniciar o monitor: {str(e)}"}
            else:
                return {"status": "iniciando", "mensagem": f"Monitor iniciado há {tempo_desde_inicio:.1f} minutos, aguardando primeira verificação"}
        
    def _close_old_connections(self):
        """Fecha conexões antigas com o banco de dados para evitar problemas"""
        try:
            from django.db import close_old_connections
            close_old_connections()
        except Exception as e:
            logger.warning(f"Erro ao fechar conexões antigas: {e}")
        
    def _agendar_tarefas(self):
        """Agenda tarefas recorrentes"""
        
        # Renovação diária às 00:01
        schedule.every().day.at("00:01").do(self._renovar_carga_diaria)
        
        # Execução do scheduler a cada minuto para garantir execuções precisas
        schedule.every(1).minutes.do(self._executar_scheduler_se_necessario)
        
        # Verificação de saúde a cada hora
        schedule.every().hour.do(self._verificar_saude_sistema)
        
        # Verificação de rotinas travadas a cada 30 minutos
        schedule.every(30).minutes.do(self._verificar_rotinas_travadas)
        
        logger.info("📅 Tarefas agendadas:")
        logger.info("   - Renovação diária: 00:01")
        logger.info("   - Scheduler: a cada 1 minuto")
        logger.info("   - Verificação saúde: a cada hora")
        logger.info("   - Verificação rotinas travadas: a cada 30 minutos")
        
    def _run_monitor(self):
        """Loop principal do monitor"""
        ultima_verificacao = datetime.now(BRAZIL_TZ)
        falhas_consecutivas = 0
        
        while self.running:
            try:
                # Fechar conexões antigas para evitar problemas - com tratamento de erro
                try:
                    # Tentar usar o método da classe primeiro
                    if hasattr(self, '_close_old_connections'):
                        self._close_old_connections()
                    else:
                        # Caso não exista, usar o módulo diretamente
                        from django.db import close_old_connections
                        close_old_connections()
                except Exception as e:
                    logger.warning(f"Erro ao fechar conexões antigas no monitor principal: {e}, mas continuando execução...")
                
                # Executar tarefas agendadas
                schedule.run_pending()
                
                # Verificar se há rotinas que deveriam ser executadas neste minuto exato
                # para evitar perder execuções devido ao ciclo de sleep
                self._verificar_execucoes_imediatas()
                
                # Registrar tempo de verificação para métricas de desempenho
                agora = datetime.now(BRAZIL_TZ)
                delta = (agora - ultima_verificacao).total_seconds()
                if delta > 15:  # Se passou mais de 15 segundos entre verificações
                    logger.warning(f"⚠️ Atraso de {delta:.1f}s entre verificações do monitor")
                ultima_verificacao = agora
                
                # Resetar contador de falhas quando bem-sucedido
                if falhas_consecutivas > 0:
                    logger.info(f"✅ Monitor recuperado após {falhas_consecutivas} falhas consecutivas")
                    falhas_consecutivas = 0
                
                # Registrar última verificação bem-sucedida para health check
                self.ultima_verificacao_bem_sucedida = datetime.now(BRAZIL_TZ)
                
                # Sleep mais curto para garantir execução próxima ao horário exato
                time.sleep(5)  # Verificar a cada 5 segundos para maior precisão
                
            except (ConnectionError, InterfaceError, OperationalError) as e:
                falhas_consecutivas += 1
                logger.error(f"Erro de conexão no monitor: {e} (Falha #{falhas_consecutivas})", exc_info=True)
                
                # Aumentar tempo de espera com backoff exponencial limitado
                wait_time = min(15 * (2 ** (falhas_consecutivas - 1)), 300)  # Máximo 5 minutos
                logger.info(f"Aguardando {wait_time}s antes de tentar novamente...")
                time.sleep(wait_time)
            
            except Exception as e:
                # Capturar qualquer outra exceção para garantir que o monitor continue rodando
                falhas_consecutivas += 1
                logger.error(f"Erro inesperado no monitor: {e} (Falha #{falhas_consecutivas})", exc_info=True)
                time.sleep(10)  # Aguardar um tempo padrão
                
                # Se houver muitas falhas consecutivas, tentar reiniciar o monitor
                if falhas_consecutivas >= 10:
                    logger.critical(f"⚠️ ALERTA: {falhas_consecutivas} falhas consecutivas. Tentando reiniciar o monitor...")
                    try:
                        # Tentar reiniciar o thread do monitor
                        self.stop()
                        time.sleep(5)
                        self.start()
                        logger.info("✅ Monitor reiniciado com sucesso após falhas consecutivas")
                        falhas_consecutivas = 0
                    except Exception as restart_error:
                        logger.critical(f"❌ Falha ao tentar reiniciar o monitor: {restart_error}", exc_info=True)
                
    def _renovar_carga_diaria(self):
        """Executa renovação diária às 00:01"""
        try:
            # Fechar conexões antigas antes de iniciar novas consultas - com tratamento de erro
            try:
                # Tentar usar o método da classe primeiro
                if hasattr(self, '_close_old_connections'):
                    self._close_old_connections()
                else:
                    # Caso não exista, usar o módulo diretamente
                    from django.db import close_old_connections
                    close_old_connections()
            except Exception as e:
                logger.warning(f"Erro ao fechar conexões antigas: {e}, mas continuando execução...")
            
            agora = datetime.now(BRAZIL_TZ)
            logger.info(f"🌅 Iniciando renovação diária - {agora.strftime('%d/%m/%Y %H:%M:%S')}")
            
            # Importar aqui para evitar problemas de inicialização
            from rotinas_automaticas.startup_scheduler import carregar_rotinas_diarias_startup
            from django.db.utils import InterfaceError, OperationalError
            
            try:
                # Executar carga diária
                sucesso = carregar_rotinas_diarias_startup()
                
                if sucesso:
                    self.ultima_renovacao_diaria = agora
                    logger.info("✅ Renovação diária concluída com sucesso")
                else:
                    logger.error("❌ Falha na renovação diária")
                    
            except (InterfaceError, OperationalError) as e:
                logger.warning(f"Problemas de conexão com banco de dados durante renovação diária: {e}")
                # Não faz nada mais, vai tentar novamente no próximo ciclo
                
        except Exception as e:
            logger.error(f"Erro na renovação diária: {e}", exc_info=True)
            
    def _executar_scheduler_se_necessario(self):
        """Executa scheduler se houver rotinas pendentes"""
        try:
            # Fechar conexões antigas antes de iniciar novas consultas - com tratamento de erro
            try:
                # Tentar usar o método da classe primeiro
                if hasattr(self, '_close_old_connections'):
                    self._close_old_connections()
                else:
                    # Caso não exista, usar o módulo diretamente
                    from django.db import close_old_connections
                    close_old_connections()
            except Exception as e:
                logger.warning(f"Erro ao fechar conexões antigas na execução do scheduler: {e}, mas continuando execução...")
            
            inicio_verificacao = datetime.now(BRAZIL_TZ)
            
            # Permitir execução 24 horas por dia para garantir que todas as rotinas sejam executadas
            agora = inicio_verificacao
            
            # Importar modelos
            from rotinas_automaticas.models import FilaExecucao
            from django.db.utils import InterfaceError, OperationalError
            
            # Log do horário atual para depuração
            hora_atual_str = agora.strftime('%H:%M:%S')
            logger.debug(f"Monitor verificando rotinas pendentes às {hora_atual_str}")
            
            try:
                # Verificar se há rotinas pendentes para executar
                pendentes_query = FilaExecucao.objects.filter(
                    status='PENDENTE',
                    data_execucao__lte=agora.date(),
                    horario_execucao__lte=agora.time()
                )
                
                # Obter os IDs das rotinas pendentes para evitar problemas de conexão fechada
                pendentes_ids = list(pendentes_query.values_list('id', flat=True))
                pendentes_count = len(pendentes_ids)
                
                # Verificar também rotinas que estão próximas de executar
                proxima_execucao = None
                try:
                    proximas_rotinas = FilaExecucao.objects.filter(
                        status='PENDENTE',
                        data_execucao=agora.date(),
                    ).order_by('horario_execucao').first()
                    
                    if proximas_rotinas:
                        proxima_execucao = f"{proximas_rotinas.scheduler_rotina.rotina_definicao.nome_exibicao} às {proximas_rotinas.horario_execucao}"
                except (InterfaceError, OperationalError):
                    logger.warning("Problema de conexão ao verificar próximas rotinas")
                
                if pendentes_count > 0:
                    # Usar nova query para evitar problemas de conexão fechada
                    rotinas_pendentes = []
                    pendentes_detalhadas = FilaExecucao.objects.filter(id__in=pendentes_ids).select_related('scheduler_rotina__rotina_definicao')
                    
                    for item in pendentes_detalhadas:
                        rotina_nome = item.scheduler_rotina.rotina_definicao.nome_exibicao
                        rotinas_pendentes.append(
                            f"{rotina_nome} ({item.data_execucao} {item.horario_execucao})"
                        )
                    
                    logger.info(f"🚀 Executando scheduler - {pendentes_count} rotina(s) pendente(s): {', '.join(rotinas_pendentes)}")
                    
                    # Executar scheduler
                    from rotinas_automaticas.scheduler_services import SchedulerService
                    
                    inicio_execucao = datetime.now(BRAZIL_TZ)
                    scheduler = SchedulerService()
                    resultado = scheduler.executor.executar_fila(limite_execucoes=pendentes_count)
                    fim_execucao = datetime.now(BRAZIL_TZ)
                    
                    self.ultima_execucao_scheduler = agora
                    
                    # Calcular tempo de execução
                    tempo_execucao = (fim_execucao - inicio_execucao).total_seconds()
                    
                    logger.info(f"✅ Scheduler executado - {resultado['total_executadas']} rotinas processadas em {tempo_execucao:.2f}s")
                    
                    # Log das próximas execuções se houver
                    if proxima_execucao:
                        logger.debug(f"Próxima rotina agendada: {proxima_execucao}")
                else:
                    # Log discreto quando não há rotinas pendentes
                    if proxima_execucao:
                        logger.debug(f"Nenhuma rotina pendente. Próxima rotina agendada: {proxima_execucao}")
            
            except (InterfaceError, OperationalError) as e:
                logger.warning(f"Problemas de conexão com banco de dados: {e}")
                # Reconectar no próximo ciclo
                
        except Exception as e:
            logger.error(f"Erro na execução do scheduler: {e}", exc_info=True)
            
    def _verificar_execucoes_imediatas(self):
        """Verifica e executa rotinas do minuto atual para maior precisão"""
        try:
            # Fechar conexões antigas antes de iniciar novas consultas - com tratamento de erro
            try:
                # Tentar usar o método da classe primeiro
                if hasattr(self, '_close_old_connections'):
                    self._close_old_connections()
                else:
                    # Caso não exista, usar o módulo diretamente
                    from django.db import close_old_connections
                    close_old_connections()
            except Exception as e:
                logger.warning(f"Erro ao fechar conexões antigas na verificação de execuções imediatas: {e}, mas continuando execução...")
            
            # Importar modelos
            from rotinas_automaticas.models import FilaExecucao
            from django.db.utils import InterfaceError, OperationalError
            
            # Obter hora atual com precisão de minuto
            agora = datetime.now(BRAZIL_TZ)
            hora_atual_str = agora.strftime('%H:%M')
            hora_atual_time = datetime.strptime(hora_atual_str, '%H:%M').time()
            
            try:
                # Verificar rotinas do minuto atual com precisão
                rotinas_do_minuto_query = FilaExecucao.objects.filter(
                    status='PENDENTE',
                    data_execucao=agora.date(),
                    horario_execucao__hour=agora.hour,
                    horario_execucao__minute=agora.minute
                )
                
                # Usar list() em vez de exists() para forçar a avaliação agora
                rotinas_do_minuto = list(rotinas_do_minuto_query)
                
                if rotinas_do_minuto:
                    logger.info(f"⏰ Execução imediata - Encontradas {len(rotinas_do_minuto)} rotina(s) para {hora_atual_str}")
                    
                    # Listar as rotinas para depuração
                    for item in rotinas_do_minuto:
                        logger.info(f"⏰ Executando imediatamente: {item.scheduler_rotina.rotina_definicao.nome_exibicao} ({item.horario_execucao})")
                    
                    # Executar diretamente sem aguardar o scheduler normal
                    from rotinas_automaticas.scheduler_services import ExecutorRotinas
                    executor = ExecutorRotinas()
                    
                    # Executar cada rotina individualmente para garantir execução
                    for item in rotinas_do_minuto:
                        try:
                            resultado = executor._executar_rotina(item)
                            status = "✅ Sucesso" if resultado["sucesso"] else "❌ Erro"
                            logger.info(f"{status} na execução imediata: {item.scheduler_rotina.rotina_definicao.nome_exibicao}")
                        except Exception as e:
                            logger.error(f"Erro na execução imediata: {e}", exc_info=True)
            except (InterfaceError, OperationalError) as e:
                logger.warning(f"Problemas de conexão com banco de dados: {e}")
                # Reconectar no próximo ciclo
        except Exception as e:
            logger.error(f"Erro na verificação de execuções imediatas: {e}", exc_info=True)
    
    def _verificar_saude_sistema(self):
        """Verifica saúde geral do sistema"""
        try:
            # Fechar conexões antigas antes de iniciar novas consultas - com tratamento de erro
            try:
                # Tentar usar o método da classe primeiro
                if hasattr(self, '_close_old_connections'):
                    self._close_old_connections()
                else:
                    # Caso não exista, usar o módulo diretamente
                    from django.db import close_old_connections
                    close_old_connections()
            except Exception as e:
                logger.warning(f"Erro ao fechar conexões antigas na verificação de saúde: {e}, mas continuando execução...")
            
            agora = datetime.now(BRAZIL_TZ)
            
            # Verificar há quanto tempo o sistema está rodando
            tempo_execucao = (agora - self.inicio_monitor).total_seconds() / 60 / 60  # em horas
            
            # Forçar reinício a cada 24 horas para garantir limpeza de recursos
            if tempo_execucao > 24:
                logger.warning(f"🔄 Monitor executando há {tempo_execucao:.1f} horas. Realizando reinicialização preventiva...")
                try:
                    self.stop()
                    time.sleep(5)
                    self.start()
                    logger.info("✅ Monitor reiniciado preventivamente com sucesso")
                    return
                except Exception as restart_error:
                    logger.error(f"❌ Falha ao tentar reinício preventivo do monitor: {restart_error}", exc_info=True)
            
            from rotinas_automaticas.models import FilaExecucao, CargaDiariaRotinas, SchedulerRotina
            from django.db import connection
            from django.db.utils import InterfaceError, OperationalError
            from django.utils import timezone
            from datetime import timedelta
            
            try:
                # Estatísticas gerais
                total_fila = FilaExecucao.objects.count()
                pendentes = FilaExecucao.objects.filter(status='PENDENTE').count()
                erros = FilaExecucao.objects.filter(status='ERRO').count()
                recovery = FilaExecucao.objects.filter(status='RECOVERY').count()
                executando = FilaExecucao.objects.filter(status='EXECUTANDO').count()
                
                # Verificar execuções travadas (executando há mais de 1 hora)
                hora_atras = timezone.now() - timedelta(hours=1)
                executando_travadas = FilaExecucao.objects.filter(
                    status='EXECUTANDO',
                    iniciado_em__lt=hora_atras
                ).count()
                
                # Verificar carga diária de hoje
                carga_hoje = CargaDiariaRotinas.objects.filter(
                    data_carga=agora.date()
                ).first()
                
                # Rotinas ativas
                rotinas_ativas = SchedulerRotina.objects.filter(executar=True).count()
                
                # Verificar conexões do banco
                conexoes_abertas = len(connection.connection.notices) if hasattr(connection, 'connection') and hasattr(connection.connection, 'notices') else 0
                
                logger.info(f"💊 Verificação de saúde - {agora.strftime('%d/%m/%Y %H:%M')}")
                logger.info(f"   Fila: {total_fila} total, {pendentes} pendentes, {executando} executando, {erros} erros, {recovery} recovery")
                logger.info(f"   Carga hoje: {'✅' if carga_hoje else '❌'}")
                logger.info(f"   Rotinas ativas: {rotinas_ativas}")
                logger.info(f"   Monitor ativo há: {(agora - self.ultima_renovacao_diaria).total_seconds() / 3600:.1f} horas" if self.ultima_renovacao_diaria else "   Monitor iniciado recentemente")
                
                # Alertas
                if not carga_hoje:
                    logger.warning("⚠️  ALERTA: Carga diária não encontrada para hoje")
                    
                if erros > 5:
                    logger.warning(f"⚠️  ALERTA: {erros} rotinas com erro")
                    
                if recovery > 3:
                    logger.warning(f"⚠️  ALERTA: {recovery} rotinas em recovery")
                    
                if executando_travadas > 0:
                    logger.warning(f"⚠️  ALERTA: {executando_travadas} rotinas parecem estar travadas (executando há mais de 1 hora)")
                    
                if pendentes > 20:
                    logger.warning(f"⚠️  ALERTA: Acúmulo de {pendentes} rotinas pendentes")
                
            except (InterfaceError, OperationalError) as e:
                logger.warning(f"Problemas de conexão com banco de dados durante verificação de saúde: {e}")
                # Não faz nada mais, vai tentar novamente no próximo ciclo
                
        except Exception as e:
            logger.error(f"Erro na verificação de saúde: {e}", exc_info=True)
            
    def _verificar_rotinas_travadas(self):
        """Verifica e corrige rotinas que ficaram travadas em execução"""
        try:
            # Fechar conexões antigas antes de iniciar novas consultas - com tratamento de erro
            try:
                # Tentar usar o método da classe primeiro
                if hasattr(self, '_close_old_connections'):
                    self._close_old_connections()
                else:
                    # Caso não exista, usar o módulo diretamente
                    from django.db import close_old_connections
                    close_old_connections()
            except Exception as e:
                logger.warning(f"Erro ao fechar conexões antigas na verificação de rotinas travadas: {e}, mas continuando execução...")
            
            from rotinas_automaticas.scheduler_services import ExecutorRotinas
            from django.db.utils import InterfaceError, OperationalError
            
            try:
                # Verificar rotinas travadas há mais de 1 hora
                executor = ExecutorRotinas()
                resultado = executor.verificar_rotinas_travadas(limite_horas=1)
                
                if resultado['total_rotinas_travadas'] > 0:
                    rotinas = [f"{r['nome']} ({r['duracao_minutos']:.1f} min)" for r in resultado['rotinas_corrigidas']]
                    logger.warning(f"🔄 Corrigidas {resultado['total_rotinas_travadas']} rotinas travadas: {', '.join(rotinas)}")
            
            except (InterfaceError, OperationalError) as e:
                logger.warning(f"Problemas de conexão com banco de dados durante verificação de rotinas travadas: {e}")
                # Não faz nada mais, vai tentar novamente no próximo ciclo
                
        except Exception as e:
            logger.error(f"Erro na verificação de rotinas travadas: {e}", exc_info=True)

# Instância global do monitor
monitor_global = None

def iniciar_monitor():
    """Inicia o monitor global"""
    global monitor_global
    
    from django.db import close_old_connections
    # Garantir que todas as conexões antigas estão fechadas antes de iniciar o monitor
    close_old_connections()
    
    if monitor_global is None:
        monitor_global = SchedulerMonitor()
        
    if not monitor_global.running:
        monitor_global.start()
        logger.info("🚀 Monitor de rotinas iniciado com sucesso")
        return True
    logger.info("ℹ️ Monitor de rotinas já está em execução")
    return False

def parar_monitor():
    """Para o monitor global"""
    global monitor_global
    
    if monitor_global and monitor_global.running:
        monitor_global.stop()
        logger.info("🛑 Monitor de rotinas parado com sucesso")
        return True
    logger.info("ℹ️ Monitor de rotinas não está em execução")
    return False
    
    
def verificar_saude_monitor():
    """Verifica saúde do monitor e reinicia automaticamente se necessário"""
    global monitor_global
    
    # Se o monitor não existe, inicializá-lo
    if monitor_global is None:
        logger.warning("⚠️ Monitor não existe! Inicializando...")
        iniciar_monitor()
        return {
            "status": "iniciado",
            "mensagem": "Monitor não existia e foi inicializado"
        }
    
    # Se o monitor existe, verificar sua saúde
    try:
        return monitor_global.verificar_saude_externa()
    except Exception as e:
        logger.error(f"❌ Erro ao verificar saúde do monitor: {e}", exc_info=True)
        
        # Tentar reinicializar o monitor em caso de erro
        try:
            parar_monitor()
            time.sleep(2)
            iniciar_monitor()
            return {
                "status": "reiniciado_erro",
                "mensagem": f"Monitor reiniciado após erro: {str(e)}"
            }
        except Exception as restart_error:
            return {
                "status": "erro",
                "mensagem": f"Falha ao reiniciar monitor: {str(restart_error)}"
            }

def status_monitor():
    """Retorna status do monitor"""
    global monitor_global
    
    if monitor_global and monitor_global.running:
        agora = datetime.now(BRAZIL_TZ)
        tempo_desde_ultima_exec = None
        tempo_desde_renovacao = None
        
        if monitor_global.ultima_execucao_scheduler:
            tempo_desde_ultima_exec = (agora - monitor_global.ultima_execucao_scheduler).total_seconds() / 60.0
        
        if monitor_global.ultima_renovacao_diaria:
            tempo_desde_renovacao = (agora - monitor_global.ultima_renovacao_diaria).total_seconds() / 3600.0
        
        # Calcular tempo desde última verificação bem-sucedida
        tempo_desde_ultima_verificacao = None
        if monitor_global.ultima_verificacao_bem_sucedida:
            tempo_desde_ultima_verificacao = (agora - monitor_global.ultima_verificacao_bem_sucedida).total_seconds() / 60.0
            
        return {
            'ativo': True,
            'ultima_execucao_scheduler': monitor_global.ultima_execucao_scheduler,
            'tempo_desde_ultima_exec_min': tempo_desde_ultima_exec,
            'ultima_renovacao_diaria': monitor_global.ultima_renovacao_diaria,
            'tempo_desde_renovacao_horas': tempo_desde_renovacao,
            'inicio_monitor': monitor_global.inicio_monitor,
            'ultima_verificacao_bem_sucedida': monitor_global.ultima_verificacao_bem_sucedida,
            'tempo_desde_ultima_verificacao_min': tempo_desde_ultima_verificacao
        }
    return {'ativo': False}
