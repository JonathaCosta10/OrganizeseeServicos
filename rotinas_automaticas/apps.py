from django.apps import AppConfig
import os


class RotinasAutomaticasConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "rotinas_automaticas"
    
    def ready(self):
        """Executado quando a aplicação está pronta"""
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
