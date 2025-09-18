from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db import close_old_connections, connection
from django.utils import timezone
import pytz
import os

@api_view(['GET'])
def status_scheduler_heroku(request):
    """Retorna status do scheduler no Heroku"""
    try:
        # Fechar conexões antigas
        close_old_connections()
        
        # Verificar se estamos no Heroku
        is_heroku = os.environ.get('DYNO') is not None
        
        # Configurar timezone
        BRAZIL_TZ = pytz.timezone('America/Sao_Paulo')
        agora = timezone.now().astimezone(BRAZIL_TZ)
        
        # Buscar informações do scheduler
        from rotinas_automaticas.models import FilaExecucao, CargaDiariaRotinas, LogScheduler
        
        # Status da fila
        total_fila = FilaExecucao.objects.count()
        pendentes = FilaExecucao.objects.filter(status='PENDENTE').count()
        executando = FilaExecucao.objects.filter(status='EXECUTANDO').count()
        concluidas = FilaExecucao.objects.filter(status='CONCLUIDA').count()
        erro = FilaExecucao.objects.filter(status='ERRO').count()
        
        # Carga diária de hoje
        carga_hoje = CargaDiariaRotinas.objects.filter(
            data_carga=agora.date()
        ).first()
        
        # Últimos logs
        ultimos_logs = LogScheduler.objects.order_by('-criado_em')[:10]
        logs = []
        for log in ultimos_logs:
            logs.append({
                'nivel': log.nivel,
                'componente': log.componente,
                'mensagem': log.mensagem,
                'horario': log.criado_em.astimezone(BRAZIL_TZ).strftime('%H:%M:%S'),
                'data': log.criado_em.astimezone(BRAZIL_TZ).strftime('%d/%m/%Y'),
            })
        
        # Próximas rotinas a serem executadas
        proximas_rotinas = []
        for item in FilaExecucao.objects.filter(status='PENDENTE').order_by('horario_execucao', 'prioridade')[:5]:
            proximas_rotinas.append({
                'nome': item.scheduler_rotina.rotina_definicao.nome_exibicao,
                'horario': item.horario_execucao.strftime('%H:%M:%S'),
                'data': item.data_execucao.strftime('%d/%m/%Y'),
                'prioridade': item.prioridade,
            })
        
        # Status da conexão
        conexao_ok = connection.is_usable()
        
        # Preparar resposta
        resposta = {
            'ambiente': 'Heroku' if is_heroku else 'Local',
            'timestamp': agora.strftime('%d/%m/%Y %H:%M:%S'),
            'fila': {
                'total': total_fila,
                'pendentes': pendentes,
                'executando': executando,
                'concluidas': concluidas,
                'erro': erro,
            },
            'carga_diaria': {
                'existe': carga_hoje is not None,
                'status': carga_hoje.status if carga_hoje else None,
                'horario': carga_hoje.iniciado_em.astimezone(BRAZIL_TZ).strftime('%H:%M:%S') if carga_hoje else None,
                'rotinas_adicionadas': carga_hoje.total_rotinas_adicionadas_fila if carga_hoje else 0,
            },
            'logs': logs,
            'proximas_rotinas': proximas_rotinas,
            'conexao_banco': {
                'status': 'OK' if conexao_ok else 'ERRO',
            }
        }
        
        return Response(resposta)
        
    except Exception as e:
        return Response({
            'status': 'erro',
            'mensagem': str(e),
            'tipo_erro': type(e).__name__,
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)