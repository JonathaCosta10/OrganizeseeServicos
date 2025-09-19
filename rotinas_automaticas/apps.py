from django.apps import AppConfig
import os


class RotinasAutomaticasConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "rotinas_automaticas"
    
    def ready(self):
        """Executado quando a aplicação está pronta"""
        # Verificar se estamos no Heroku
        is_heroku = os.environ.get('DYNO') is not None
        
        if is_heroku:
            self._inicializar_heroku()
        else:
            self._inicializar_local()
    
    def _inicializar_heroku(self):
        """Inicialização específica para ambiente Heroku"""
        try:
            # Iniciar em um thread separado para não bloquear o servidor
            import threading
            
            def iniciar_heroku_async():
                # Dar tempo para o servidor Gunicorn inicializar completamente
                import time
                time.sleep(10)
                
                # Primeiro, corrigir URLs das rotinas
                self._corrigir_urls_heroku()
                
                from .heroku_scheduler import iniciar_scheduler_heroku, iniciar_monitor_heroku
                
                # Inicializar scheduler
                iniciar_scheduler_heroku()
                
                # Iniciar monitor
                iniciar_monitor_heroku()
            
            # Iniciar thread
            thread = threading.Thread(target=iniciar_heroku_async)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            print(f"❌ Erro na inicialização do Heroku: {e}")
    
    def _corrigir_urls_heroku(self):
        """Corrige automaticamente as URLs das rotinas no ambiente Heroku"""
        try:
            import logging
            from django.conf import settings
            
            logger = logging.getLogger('heroku_scheduler')
            logger.info("🔧 Iniciando correção automática de URLs no Heroku...")
            
            # Importar models apenas quando necessário para evitar problemas de inicialização
            from .models import SchedulerRotina, FilaExecucao
            
            # Obter BASE_URL das configurações
            base_url = settings.BASE_URL
            if not base_url or '127.0.0.1' in base_url or 'localhost' in base_url:
                base_url = "https://service-organizesee-5f72417f9331.herokuapp.com"
                logger.info(f"🌐 Usando URL padrão do Heroku: {base_url}")
            else:
                logger.info(f"🌐 Usando BASE_URL configurada: {base_url}")
            
            # Remover barra final se existir
            if base_url.endswith('/'):
                base_url = base_url[:-1]
            
            # Corrigir URLs das rotinas
            rotinas_corrigidas = 0
            
            for rotina in SchedulerRotina.objects.filter(endpoint_url__isnull=False).exclude(endpoint_url=''):
                url_antiga = rotina.endpoint_url
                nome_rotina = rotina.rotina_definicao.nome_exibicao
                
                # Verificar se precisa correção
                if '127.0.0.1' in url_antiga or 'localhost' in url_antiga:
                    # Extrair o caminho da URL
                    try:
                        if '/api/' in url_antiga:
                            # Extrair a partir de '/api/'
                            caminho = '/api/' + url_antiga.split('/api/', 1)[1]
                        else:
                            # Método alternativo
                            from urllib.parse import urlparse
                            parsed = urlparse(url_antiga)
                            caminho = parsed.path
                        
                        nova_url = f"{base_url}{caminho}"
                        
                        rotina.endpoint_url = nova_url
                        rotina.save()
                        
                        rotinas_corrigidas += 1
                        logger.info(f"✅ {nome_rotina}: {url_antiga} -> {nova_url}")
                        
                    except Exception as e:
                        logger.error(f"❌ Erro ao corrigir URL da rotina {nome_rotina}: {e}")
                else:
                    logger.debug(f"✓ {nome_rotina}: URL já está correta")
            
            # Limpar itens da fila com erro de conexão
            itens_erro = FilaExecucao.objects.filter(
                status='ERRO',
                erro_detalhes__contains='127.0.0.1'
            )
            if itens_erro.exists():
                count_erros = itens_erro.count()
                itens_erro.delete()
                logger.info(f"🧹 Removidos {count_erros} itens da fila com erros de conexão")
            
            # Resetar rotinas travadas
            FilaExecucao.objects.filter(status='EXECUTANDO').update(status='PENDENTE')
            
            logger.info(f"🚀 Correção concluída: {rotinas_corrigidas} rotinas atualizadas")
            
        except Exception as e:
            print(f"❌ Erro na correção automática de URLs: {e}")
            import traceback
            traceback.print_exc()
    
    def _inicializar_local(self):
        """Inicialização específica para ambiente local"""
        # Só executar no processo principal do runserver (evitar duplicação)
        if os.environ.get('RUN_MAIN') or 'runserver' not in os.sys.argv:
            return
            
        try:
            # Aguardar um pouco para garantir que o banco está pronto
            import time
            time.sleep(2)
            
            # Inicializar sistema de scheduler
            from .startup_scheduler import inicializar_scheduler
            from .monitor_scheduler import iniciar_monitor
            
            print("\n🚀 Inicializando sistema de scheduler integrado...")
            
            # Carregar rotinas diárias e verificar integridade
            inicializar_scheduler()
            
            # Iniciar monitor em background
            monitor_iniciado = iniciar_monitor()
            
            if monitor_iniciado:
                print("🔄 Monitor de background ativado")
            else:
                print("⚠️  Monitor já estava ativo")
                
            print("✅ Sistema de scheduler totalmente integrado ao Django!")
            
        except Exception as e:
            print(f"❌ Erro na inicialização do scheduler: {e}")
            print("   O servidor continuará funcionando, mas o scheduler pode não estar ativo")
            # Não impedir o Django de iniciar
