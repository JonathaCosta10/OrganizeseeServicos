"""
Comando Django para inicializar dados básicos do scheduler
========================================================

Usage: python manage.py inicializar_scheduler
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from rotinas_automaticas.models import (
    GrupoDiasExecucao, TipoRotina, StatusExecucao, 
    RotinaDefinicao, SchedulerRotina
)


class Command(BaseCommand):
    help = 'Inicializa dados básicos do scheduler'
    
    def handle(self, *args, **options):
        self.stdout.write('Inicializando dados básicos do scheduler...')
        
        # 1. Criar grupos de dias
        self._criar_grupos_dias()
        
        # 2. Criar tipos de rotina
        self._criar_tipos_rotina()
        
        # 3. Criar status de execução
        self._criar_status_execucao()
        
        # 4. Criar rotinas básicas
        self._criar_rotinas_basicas()
        
        self.stdout.write(
            self.style.SUCCESS('Dados básicos inicializados com sucesso!')
        )
    
    def _criar_grupos_dias(self):
        """Cria grupos de dias de execução"""
        grupos = [
            {
                'nome': 'DIARIO',
                'descricao': 'Todos os dias da semana',
                'segunda': True, 'terca': True, 'quarta': True,
                'quinta': True, 'sexta': True, 'sabado': True, 'domingo': True
            },
            {
                'nome': 'DIAS_SEMANA',
                'descricao': 'Apenas dias de semana (Segunda a Sexta)',
                'segunda': True, 'terca': True, 'quarta': True,
                'quinta': True, 'sexta': True, 'sabado': False, 'domingo': False
            },
            {
                'nome': 'FINAL_SEMANA',
                'descricao': 'Apenas final de semana (Sábado e Domingo)',
                'segunda': False, 'terca': False, 'quarta': False,
                'quinta': False, 'sexta': False, 'sabado': True, 'domingo': True
            },
            {
                'nome': 'D_MAIS_1',
                'descricao': 'D+1: Terça a Sábado',
                'segunda': False, 'terca': True, 'quarta': True,
                'quinta': True, 'sexta': True, 'sabado': True, 'domingo': False
            }
        ]
        
        for grupo_data in grupos:
            grupo, created = GrupoDiasExecucao.objects.get_or_create(
                nome=grupo_data['nome'],
                defaults=grupo_data
            )
            if created:
                self.stdout.write(f'  Grupo criado: {grupo.get_nome_display()}')
    
    def _criar_tipos_rotina(self):
        """Cria tipos de rotina se não existirem"""
        tipos = [
            {'nome': 'Carga de Arquivo', 'descricao': 'Rotinas de carga de arquivos', 'icone': 'upload', 'cor': '#007bff'},
            {'nome': 'Download', 'descricao': 'Rotinas de download de arquivos', 'icone': 'download', 'cor': '#28a745'},
            {'nome': 'Script', 'descricao': 'Execução de scripts', 'icone': 'code', 'cor': '#ffc107'},
            {'nome': 'API', 'descricao': 'Chamadas de API', 'icone': 'link', 'cor': '#17a2b8'},
        ]
        
        for tipo_data in tipos:
            tipo, created = TipoRotina.objects.get_or_create(
                nome=tipo_data['nome'],
                defaults=tipo_data
            )
            if created:
                self.stdout.write(f'  Tipo criado: {tipo.nome}')
    
    def _criar_status_execucao(self):
        """Cria status de execução se não existirem"""
        status_list = [
            {'nome': 'PENDENTE', 'descricao': 'Aguardando execução', 'icone': '⏳', 'cor': '#6c757d'},
            {'nome': 'EXECUTANDO', 'descricao': 'Em execução', 'icone': '▶️', 'cor': '#007bff'},
            {'nome': 'CONCLUIDA', 'descricao': 'Concluída com sucesso', 'icone': '✅', 'cor': '#28a745'},
            {'nome': 'ERRO', 'descricao': 'Erro na execução', 'icone': '❌', 'cor': '#dc3545'},
            {'nome': 'CANCELADA', 'descricao': 'Cancelada', 'icone': '⏹️', 'cor': '#6c757d'},
        ]
        
        for status_data in status_list:
            status_obj, created = StatusExecucao.objects.get_or_create(
                nome=status_data['nome'],
                defaults=status_data
            )
            if created:
                self.stdout.write(f'  Status criado: {status_obj.nome}')
    
    def _criar_rotinas_basicas(self):
        """Cria rotinas básicas do sistema"""
        
        # Buscar tipo padrão
        tipo_carga = TipoRotina.objects.filter(nome__icontains='Carga').first()
        if not tipo_carga:
            tipo_carga = TipoRotina.objects.first()
        
        # Buscar grupo diário
        grupo_diario = GrupoDiasExecucao.objects.filter(nome='DIARIO').first()
        
        rotinas_basicas = [
            {
                'nome': 'baixar_cvm',
                'nome_exibicao': 'Download CVM',
                'descricao': 'Download de arquivos da CVM',
                'comando_management': 'python',
                'argumentos_padrao': 'manage.py download_cvm',
                'periodo_cron': '0 8 * * *',  # 08:00 todos os dias
                'tipo_execucao': 'DIARIO',
                'tipo_rotina': 'DOWNLOAD_ARQUIVO',
                'horario_execucao': '08:00:00',
                'endpoint_url': f"{settings.BASE_URL}/api/download_cvm/",
                'metodo_http': 'POST'
            },
            {
                'nome': 'baixar_b3',
                'nome_exibicao': 'Download B3',
                'descricao': 'Download de arquivos da B3',
                'comando_management': 'python',
                'argumentos_padrao': 'manage.py download_b3',
                'periodo_cron': '0 9 * * *',  # 09:00 todos os dias
                'tipo_execucao': 'DIARIO',
                'tipo_rotina': 'DOWNLOAD_ARQUIVO',
                'horario_execucao': '09:00:00',
                'endpoint_url': f"{settings.BASE_URL}/api/download_b3/",
                'metodo_http': 'POST'
            },
            {
                'nome': 'job_carregar_precos_trade_consolidado_file',
                'nome_exibicao': 'Carga Trade Consolidated File',
                'descricao': 'Carrega dados do arquivo TradeInformationConsolidatedFile da B3',
                'comando_management': 'python',
                'argumentos_padrao': 'rotinas_individuais/carga_b3_TradeInformationConsolidatedFile_sem_emoji.py',
                'periodo_cron': '0 10 * * *',  # 10:00 todos os dias
                'tipo_execucao': 'DIARIO',
                'tipo_rotina': 'CARGA_ARQUIVO',
                'horario_execucao': '10:00:00',
                'endpoint_url': f"{settings.BASE_URL}/api/static_arquivos/",
                'metodo_http': 'POST',
                'payload_json': '{"acao": "Carga", "arquivo": "TradeInformationConsolidatedFile*.csv"}',
                'mascara_arquivo': 'TradeInformationConsolidatedFile*.csv'
            }
        ]
        
        for rotina_data in rotinas_basicas:
            # Verificar se rotina_definicao já existe
            rotina_def, def_created = RotinaDefinicao.objects.get_or_create(
                nome=rotina_data['nome'],
                defaults={
                    'nome_exibicao': rotina_data['nome_exibicao'],
                    'descricao': rotina_data['descricao'],
                    'comando_management': rotina_data['comando_management'],
                    'argumentos_padrao': rotina_data['argumentos_padrao'],
                    'periodo_cron': rotina_data['periodo_cron'],
                    'fuso_horario': 'America/Sao_Paulo',
                    'ativo': True,
                    'timeout_segundos': 3600,
                    'tipo_rotina': tipo_carga
                }
            )
            
            if def_created:
                self.stdout.write(f'  Definição de rotina criada: {rotina_def.nome_exibicao}')
            
            # Criar scheduler para a rotina
            scheduler, sch_created = SchedulerRotina.objects.get_or_create(
                rotina_definicao=rotina_def,
                defaults={
                    'tipo_execucao': rotina_data['tipo_execucao'],
                    'tipo_rotina': rotina_data['tipo_rotina'],
                    'grupo_dias': grupo_diario,
                    'executar': True,
                    'horario_execucao': rotina_data['horario_execucao'],
                    'endpoint_url': rotina_data.get('endpoint_url'),
                    'metodo_http': rotina_data.get('metodo_http', 'POST'),
                    'payload_json': rotina_data.get('payload_json'),
                    'mascara_arquivo': rotina_data.get('mascara_arquivo'),
                    'prioridade': 50
                }
            )
            
            if sch_created:
                self.stdout.write(f'  Scheduler criado: {scheduler.rotina_definicao.nome_exibicao}')
