from django.urls import path
from . import views
from . import heroku_views

urlpatterns = [
    path('api/download_cvm/', views.download_cvm, name='download_cvm'),
    path('api/download_b3/', views.download_b3, name='download_b3'),
    path('api/download_b3/<int:dias>/', views.download_b3, name='download_b3_dias'),
    path('api/static_arquivos/', views.static_arquivos, name='static_arquivos'),
    path('api/grafico_tabela_precos/', views.grafico_tabela_precos, name='grafico_tabela_precos'),
    
    # APIs do Scheduler - Fila de Execução
    path('api/scheduler/carga-diaria/', views.executar_carga_diaria, name='scheduler_carga_diaria'),
    path('api/scheduler/executar/', views.executar_scheduler, name='scheduler_executar'),
    path('api/scheduler/fila/status/', views.status_fila_execucao, name='scheduler_fila_status'),
    path('api/scheduler/logs/', views.logs_scheduler, name='scheduler_logs'),
    path('api/scheduler/fila/<int:item_id>/cancelar/', views.cancelar_item_fila, name='scheduler_cancelar_item'),
    
    # APIs do Monitor
    path('api/scheduler/monitor/status/', views.status_monitor, name='scheduler_monitor_status'),
    path('api/scheduler/monitor/reiniciar/', views.reiniciar_monitor, name='scheduler_monitor_reiniciar'),
    path('api/scheduler/monitor/health-check/', views.verificar_saude_monitor, name='scheduler_monitor_health_check'),
    
    # Novas APIs para gerenciamento de Rotinas
    path('api/scheduler/rotinas/', views.listar_rotinas, name='scheduler_listar_rotinas'),
    path('api/scheduler/rotinas/<int:rotina_id>/', views.gerenciar_rotina, name='scheduler_gerenciar_rotina'),
    path('api/scheduler/rotinas/<int:rotina_id>/executar/', views.executar_rotina_especifica, name='scheduler_executar_rotina'),
    
    # Status específico do Heroku
    path('api/scheduler/heroku/status/', heroku_views.status_scheduler_heroku, name='scheduler_status_heroku'),
]
