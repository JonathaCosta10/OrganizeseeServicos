from django.contrib import admin
from .models import (
    # Tabelas B3
    B3InstrumentsConsolidated,
    B3TradeInformation,
    
    # Tabelas CVM - Companhias
    FcaCiaAberta,
    AnualFcaCiaAbertaGeral,
    AnualFcaCiaAbertaValorMobiliario,
    CompanhiaAberta,
    CanalDivulgacaoCompanhia,
    ValorMobiliarioCompanhia,
    
    # Tabelas CVM - FII
    InfAnualFiiGeral,
    InfAnualFiiAtivoValorContabil,
    InfMensalFiiGeral,
    InfMensalFiiAtivoPassivo,
    InfMensalFiiComplemento,
    CvmGeralFii,
    FundoListadoB3,
    
    # Tabelas de Metadados
    EtlMetadata,
    ProcessingMetadata,
    
    # Tabelas Organizesee
    DadosPessoais,
    AtivosPrecos,
    AtivosPessoais,
    AtivosPrecosBruto,
    UserProfile,
    PasswordResetToken,
    
    # Tabelas Orçamento Doméstico
    OrcamentoDomesticoDividas,
    OrcamentoDomesticoEntradas,
    OrcamentoDomesticoGastos,
    OrcamentoDomesticoMetasPersonalizadas,
    OrcamentoDomestico,
    
    # Tabelas Controle de Rotinas
    TipoRotina,
    StatusExecucao,
    RotinaDefinicao,
    ControleRotina,
    HistoricoExecucao,
    MonitorRotina,
    RegistroExecucao,
    
    # Tabelas Scheduler
    GrupoDiasExecucao,
    SchedulerRotina,
    FilaExecucao,
    CargaDiariaRotinas,
    LogScheduler,
)

# ================== ADMIN B3 ==================

@admin.register(B3InstrumentsConsolidated)
class B3InstrumentsConsolidatedAdmin(admin.ModelAdmin):
    list_display = ['codinst', 'nomres', 'datref', 'mercado', 'data_carga']
    list_filter = ['datref', 'mercado', 'segmento', 'fonte']
    search_fields = ['codinst', 'nomres', 'isin']
    readonly_fields = ['data_carga']
    list_per_page = 50

@admin.register(B3TradeInformation)
class B3TradeInformationAdmin(admin.ModelAdmin):
    list_display = ['codinst', 'nomres', 'datref', 'preult', 'voltot', 'data_carga']
    list_filter = ['datref', 'fonte']
    search_fields = ['codinst', 'nomres']
    readonly_fields = ['data_carga']
    list_per_page = 50

# ================== ADMIN CVM - COMPANHIAS ==================

@admin.register(FcaCiaAberta)
class FcaCiaAbertaAdmin(admin.ModelAdmin):
    list_display = ['denom_cia', 'cd_cvm', 'dt_refer', 'categ_doc']
    list_filter = ['dt_refer', 'categ_doc']
    search_fields = ['denom_cia', 'cnpj_cia', 'cd_cvm']
    list_per_page = 50

@admin.register(AnualFcaCiaAbertaGeral)
class AnualFcaCiaAbertaGeralAdmin(admin.ModelAdmin):
    list_display = ['nome_empresarial', 'codigo_cvm', 'data_referencia', 'setor_atividade']
    list_filter = ['data_referencia', 'setor_atividade', 'situacao_registro_cvm']
    search_fields = ['nome_empresarial', 'cnpj_companhia', 'codigo_cvm']
    list_per_page = 50

@admin.register(AnualFcaCiaAbertaValorMobiliario)
class AnualFcaCiaAbertaValorMobiliarioAdmin(admin.ModelAdmin):
    list_display = ['nome_empresarial', 'codigo_negociacao', 'valor_mobiliario', 'mercado']
    list_filter = ['mercado', 'segmento', 'valor_mobiliario']
    search_fields = ['nome_empresarial', 'codigo_negociacao']
    list_per_page = 50

@admin.register(CompanhiaAberta)
class CompanhiaAbertaAdmin(admin.ModelAdmin):
    list_display = ['denominacao_social', 'cnpj', 'setor_atividade', 'situacao', 'data_referencia']
    list_filter = ['setor_atividade', 'situacao', 'data_referencia']
    search_fields = ['denominacao_social', 'cnpj', 'denominacao_comercial']
    readonly_fields = ['criado_em', 'atualizado_em']
    list_per_page = 50

@admin.register(CanalDivulgacaoCompanhia)
class CanalDivulgacaoCompanhiaAdmin(admin.ModelAdmin):
    list_display = ['denominacao_social', 'tipo_canal', 'endereco_canal', 'data_referencia']
    list_filter = ['tipo_canal', 'data_referencia']
    search_fields = ['denominacao_social', 'cnpj_companhia']
    readonly_fields = ['criado_em', 'atualizado_em']
    list_per_page = 50

@admin.register(ValorMobiliarioCompanhia)
class ValorMobiliarioCompanhiaAdmin(admin.ModelAdmin):
    list_display = ['denominacao_social', 'tipo_valor_mobiliario', 'mercado', 'segmento']
    list_filter = ['tipo_valor_mobiliario', 'mercado', 'segmento']
    search_fields = ['denominacao_social', 'cnpj_companhia', 'cod_cvm']
    readonly_fields = ['criado_em', 'atualizado_em']
    list_per_page = 50

# ================== ADMIN CVM - FII ==================

@admin.register(InfAnualFiiGeral)
class InfAnualFiiGeralAdmin(admin.ModelAdmin):
    list_display = ['nome_fundo_classe', 'cnpj_fundo_classe', 'data_referencia', 'segmento_atuacao']
    list_filter = ['data_referencia', 'segmento_atuacao', 'tipo_gestao']
    search_fields = ['nome_fundo_classe', 'cnpj_fundo_classe']
    list_per_page = 50

@admin.register(InfAnualFiiAtivoValorContabil)
class InfAnualFiiAtivoValorContabilAdmin(admin.ModelAdmin):
    list_display = ['cnpj_fundo_classe', 'nome_ativo', 'valor', 'data_referencia']
    list_filter = ['data_referencia']
    search_fields = ['cnpj_fundo_classe', 'nome_ativo']
    list_per_page = 50

@admin.register(InfMensalFiiGeral)
class InfMensalFiiGeralAdmin(admin.ModelAdmin):
    list_display = ['nome_fundo_classe', 'cnpj_fundo_classe', 'data_referencia', 'segmento_atuacao']
    list_filter = ['data_referencia', 'segmento_atuacao']
    search_fields = ['nome_fundo_classe', 'cnpj_fundo_classe']
    list_per_page = 50

@admin.register(InfMensalFiiAtivoPassivo)
class InfMensalFiiAtivoPassivoAdmin(admin.ModelAdmin):
    list_display = ['cnpj_fundo_classe', 'data_referencia', 'total_investido', 'total_passivo']
    list_filter = ['data_referencia']
    search_fields = ['cnpj_fundo_classe']
    list_per_page = 50

@admin.register(InfMensalFiiComplemento)
class InfMensalFiiComplementoAdmin(admin.ModelAdmin):
    list_display = ['cnpj_fundo_classe', 'data_referencia', 'total_numero_cotistas', 'valor_patrimonial_cotas']
    list_filter = ['data_referencia']
    search_fields = ['cnpj_fundo_classe']
    list_per_page = 50

@admin.register(CvmGeralFii)
class CvmGeralFiiAdmin(admin.ModelAdmin):
    list_display = ['denominacao_social', 'cnpj_fundo', 'tipo_fundo', 'situacao']
    list_filter = ['tipo_fundo', 'situacao', 'segmento_atuacao']
    search_fields = ['denominacao_social', 'cnpj_fundo']
    readonly_fields = ['criado_em', 'atualizado_em']
    list_per_page = 50

@admin.register(FundoListadoB3)
class FundoListadoB3Admin(admin.ModelAdmin):
    list_display = ['codigo', 'razao_social', 'cnpj', 'criado_em']
    search_fields = ['codigo', 'razao_social', 'cnpj']
    readonly_fields = ['criado_em', 'atualizado_em']
    list_per_page = 50

# ================== ADMIN METADADOS ==================

@admin.register(EtlMetadata)
class EtlMetadataAdmin(admin.ModelAdmin):
    list_display = ['arquivo', 'tipo_processamento', 'status', 'registros_processados', 'data_processamento']
    list_filter = ['status', 'tipo_processamento', 'data_processamento']
    search_fields = ['arquivo']
    readonly_fields = ['data_processamento']
    list_per_page = 50

@admin.register(ProcessingMetadata)
class ProcessingMetadataAdmin(admin.ModelAdmin):
    list_display = ['arquivo_origem', 'tabela_destino', 'status_processamento', 'total_linhas', 'data_processamento']
    list_filter = ['status_processamento', 'data_processamento']
    search_fields = ['arquivo_origem', 'tabela_destino']
    readonly_fields = ['data_processamento']
    list_per_page = 50

# ================== ADMIN ORGANIZESEE ==================

@admin.register(DadosPessoais)
class DadosPessoaisAdmin(admin.ModelAdmin):
    list_display = ['nome_completo', 'cpf', 'email', 'cidade', 'estado', 'data_criacao']
    list_filter = ['estado', 'genero', 'data_criacao']
    search_fields = ['nome_completo', 'cpf', 'email']
    readonly_fields = ['data_criacao', 'data_atualizacao']
    list_per_page = 50

@admin.register(AtivosPrecos)
class AtivosPrecosAdmin(admin.ModelAdmin):
    list_display = ['ticker', 'tipo', 'data', 'close', 'volume', 'fonte']
    list_filter = ['tipo', 'data', 'fonte']
    search_fields = ['ticker']
    list_per_page = 50

@admin.register(AtivosPessoais)
class AtivosPessoaisAdmin(admin.ModelAdmin):
    list_display = ['user', 'ticker', 'tipo', 'quantidade', 'preco_medio', 'data_compra']
    list_filter = ['tipo', 'data_compra', 'data_criacao']
    search_fields = ['ticker', 'user__username']
    readonly_fields = ['data_criacao', 'data_atualizacao']
    list_per_page = 50

@admin.register(AtivosPrecosBruto)
class AtivosPrecosBrutoAdmin(admin.ModelAdmin):
    list_display = ['codigo_ativo', 'data_referencia', 'preco_ultimo', 'volume_total', 'fonte']
    list_filter = ['data_referencia', 'fonte']
    search_fields = ['codigo_ativo']
    readonly_fields = ['data_carga']
    list_per_page = 50

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_paid_user', 'is_google_account', 'created_at']
    list_filter = ['is_paid_user', 'is_google_account', 'created_at']
    search_fields = ['user__username', 'google_email', 'google_name']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 50

@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ['email', 'code', 'is_used', 'attempts', 'created_at']
    list_filter = ['is_used', 'created_at']
    search_fields = ['email', 'code']
    readonly_fields = ['created_at']
    list_per_page = 50

# ================== ADMIN ORÇAMENTO DOMÉSTICO ==================

@admin.register(OrcamentoDomesticoDividas)
class OrcamentoDomesticoDividasAdmin(admin.ModelAdmin):
    list_display = ['user', 'categoria', 'descricao', 'valor_mensal', 'quantidade_parcelas']
    list_filter = ['categoria', 'mes', 'ano', 'flag']
    search_fields = ['user__username', 'descricao']
    list_per_page = 50

@admin.register(OrcamentoDomesticoEntradas)
class OrcamentoDomesticoEntradasAdmin(admin.ModelAdmin):
    list_display = ['user', 'categoria', 'descricao', 'valor_mensal', 'mes', 'ano']
    list_filter = ['categoria', 'mes', 'ano', 'flag']
    search_fields = ['user__username', 'descricao']
    list_per_page = 50

@admin.register(OrcamentoDomesticoGastos)
class OrcamentoDomesticoGastosAdmin(admin.ModelAdmin):
    list_display = ['user', 'categoria', 'descricao', 'valor_mensal', 'mes', 'ano']
    list_filter = ['categoria', 'mes', 'ano', 'flag']
    search_fields = ['user__username', 'descricao']
    list_per_page = 50

@admin.register(OrcamentoDomesticoMetasPersonalizadas)
class OrcamentoDomesticoMetasPersonalizadasAdmin(admin.ModelAdmin):
    list_display = ['user', 'titulo_da_meta', 'valor_hoje', 'valor_alvo', 'data_limite']
    list_filter = ['categoria', 'data_limite', 'data_cadastro']
    search_fields = ['user__username', 'titulo_da_meta']
    list_per_page = 50

@admin.register(OrcamentoDomestico)
class OrcamentoDomesticoAdmin(admin.ModelAdmin):
    list_display = ['user', 'custos_fixos', 'prazer', 'conforto', 'metas', 'data']
    list_filter = ['data']
    search_fields = ['user__username']
    list_per_page = 50

# ================== ADMIN CONTROLE DE ROTINAS ==================

@admin.register(TipoRotina)
class TipoRotinaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'descricao', 'ativo', 'cor', 'icone']
    list_filter = ['ativo']
    search_fields = ['nome', 'descricao']
    list_per_page = 50

@admin.register(StatusExecucao)
class StatusExecucaoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'descricao', 'cor', 'icone']
    search_fields = ['nome', 'descricao']
    list_per_page = 50

@admin.register(RotinaDefinicao)
class RotinaDefinicaoAdmin(admin.ModelAdmin):
    list_display = ['nome_exibicao', 'nome', 'ativo', 'tipo_rotina', 'criado_em']
    list_filter = ['ativo', 'tipo_rotina', 'criado_em']
    search_fields = ['nome', 'nome_exibicao', 'comando_management']
    readonly_fields = ['criado_em', 'atualizado_em']
    list_per_page = 50

@admin.register(ControleRotina)
class ControleRotinaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'ativo', 'periodo', 'hora_execucao', 'ultima_execucao']
    list_filter = ['ativo', 'periodo', 'executar_inicio']
    search_fields = ['nome', 'descricao']
    readonly_fields = ['criado_em', 'atualizado_em']
    list_per_page = 50

@admin.register(HistoricoExecucao)
class HistoricoExecucaoAdmin(admin.ModelAdmin):
    list_display = ['rotina', 'status', 'iniciado_em', 'finalizado_em', 'duracao_segundos']
    list_filter = ['status', 'iniciado_em', 'ambiente']
    search_fields = ['rotina__nome', 'argumentos_executados']
    list_per_page = 50

@admin.register(MonitorRotina)
class MonitorRotinaAdmin(admin.ModelAdmin):
    list_display = ['rotina', 'status_atual', 'ultima_execucao', 'total_execucoes', 'execucoes_sucesso']
    list_filter = ['status_atual', 'alertas_ativo']
    search_fields = ['rotina__nome']
    readonly_fields = ['atualizado_em']
    list_per_page = 50

@admin.register(RegistroExecucao)
class RegistroExecucaoAdmin(admin.ModelAdmin):
    list_display = [
        'job_arquivo_processo',
        'tabela_destino', 
        'status_execucao',
        'sistema',
        'grupo',
        'dia_horario_execucao',
        'registros_totais_novos',
        'registros_totais_rejeitados'
    ]
    list_filter = [
        'status_execucao',
        'sistema',
        'grupo',
        'dia_horario_execucao'
    ]
    search_fields = [
        'job_arquivo_processo',
        'tabela_destino',
        'observacoes'
    ]
    readonly_fields = [
        'dia_horario_execucao',
        'dia_horario_finalizacao',
        'criado_em',
        'atualizado_em',
        'duracao_execucao'
    ]
    fieldsets = [
        ('Informações Básicas', {
            'fields': ['job_arquivo_processo', 'tabela_destino', 'sistema', 'grupo']
        }),
        ('Status e Execução', {
            'fields': ['status_execucao', 'dia_horario_execucao', 'dia_horario_finalizacao', 'proxima_execucao']
        }),
        ('Estatísticas de Processamento', {
            'fields': [
                'quantidade_linhas_arquivo',
                'registros_totais_arquivo', 
                'registros_totais_novos',
                'registros_totais_atualizados',
                'registros_totais_ignorados'
            ]
        }),
        ('Logs e Observações', {
            'fields': ['arquivo_log', 'observacoes', 'erro_detalhes']
        }),
        ('Auditoria', {
            'fields': ['criado_em', 'atualizado_em', 'duracao_execucao'],
            'classes': ['collapse']
        })
    ]
    list_per_page = 50
    
    def registros_totais_rejeitados(self, obj):
        """Campo calculado para mostrar total de rejeitados na lista"""
        return obj.registros_totais_ignorados
    registros_totais_rejeitados.short_description = 'Rejeitados'
    
    def save_model(self, request, obj, form, change):
        """Personalizar save se necessário"""
        super().save_model(request, obj, form, change)


# ================== ADMIN SCHEDULER ==================

@admin.register(GrupoDiasExecucao)
class GrupoDiasExecucaoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'descricao', 'get_dias_ativados', 'ativo']
    list_filter = ['ativo', 'nome']
    search_fields = ['descricao']
    readonly_fields = ['criado_em']
    
    fieldsets = [
        ('Informações Básicas', {
            'fields': ['nome', 'descricao', 'ativo']
        }),
        ('Dias da Semana', {
            'fields': ['segunda', 'terca', 'quarta', 'quinta', 'sexta', 'sabado', 'domingo']
        }),
        ('Auditoria', {
            'fields': ['criado_em'],
            'classes': ['collapse']
        })
    ]
    
    def get_dias_ativados(self, obj):
        dias = []
        if obj.segunda: dias.append('Seg')
        if obj.terca: dias.append('Ter')
        if obj.quarta: dias.append('Qua')
        if obj.quinta: dias.append('Qui')
        if obj.sexta: dias.append('Sex')
        if obj.sabado: dias.append('Sab')
        if obj.domingo: dias.append('Dom')
        return ', '.join(dias) if dias else 'Nenhum'
    get_dias_ativados.short_description = 'Dias Ativados'


@admin.register(SchedulerRotina)
class SchedulerRotinaAdmin(admin.ModelAdmin):
    list_display = [
        'rotina_definicao', 
        'tipo_execucao', 
        'tipo_rotina',
        'horario_execucao',
        'executar',
        'prioridade'
    ]
    list_filter = [
        'tipo_execucao', 
        'tipo_rotina', 
        'executar', 
        'ciclico',
        'grupo_dias'
    ]
    search_fields = [
        'rotina_definicao__nome', 
        'rotina_definicao__nome_exibicao'
    ]
    readonly_fields = ['criado_em', 'atualizado_em']
    
    fieldsets = [
        ('Rotina', {
            'fields': ['rotina_definicao']
        }),
        ('Configurações de Execução', {
            'fields': [
                'tipo_execucao', 
                'tipo_rotina', 
                'grupo_dias',
                'executar', 
                'horario_execucao', 
                'prioridade'
            ]
        }),
        ('Configurações Cíclicas', {
            'fields': ['ciclico', 'intervalo_horas']
        }),
        ('Configurações de API/Endpoint', {
            'fields': [
                'endpoint_url', 
                'metodo_http', 
                'payload_json', 
                'headers_json'
            ],
            'classes': ['collapse']
        }),
        ('Configurações de Arquivo', {
            'fields': ['mascara_arquivo', 'pasta_origem'],
            'classes': ['collapse']
        }),
        ('Recovery e Resilência', {
            'fields': [
                'permite_recovery', 
                'max_tentativas_recovery', 
                'delay_recovery_minutos'
            ],
            'classes': ['collapse']
        }),
        ('Auditoria', {
            'fields': ['criado_em', 'atualizado_em', 'criado_por'],
            'classes': ['collapse']
        })
    ]


@admin.register(FilaExecucao)
class FilaExecucaoAdmin(admin.ModelAdmin):
    list_display = [
        'scheduler_rotina',
        'data_execucao',
        'horario_execucao', 
        'status',
        'prioridade',
        'tentativa_atual',
        'duracao_formatada'
    ]
    list_filter = [
        'status', 
        'data_execucao', 
        'scheduler_rotina__tipo_execucao'
    ]
    search_fields = [
        'scheduler_rotina__rotina_definicao__nome_exibicao',
        'arquivo_processado'
    ]
    readonly_fields = [
        'criado_em', 
        'atualizado_em', 
        'duracao_formatada'
    ]
    date_hierarchy = 'data_execucao'
    
    fieldsets = [
        ('Execução', {
            'fields': [
                'scheduler_rotina', 
                'data_execucao', 
                'horario_execucao',
                'status', 
                'prioridade'
            ]
        }),
        ('Timing', {
            'fields': [
                'iniciado_em', 
                'finalizado_em', 
                'duracao_segundos',
                'duracao_formatada'
            ]
        }),
        ('Recovery', {
            'fields': [
                'tentativa_atual', 
                'max_tentativas', 
                'ultima_tentativa_em'
            ]
        }),
        ('Resultado', {
            'fields': [
                'codigo_retorno', 
                'arquivo_processado',
                'registros_processados',
                'saida_stdout', 
                'saida_stderr', 
                'erro_detalhes'
            ],
            'classes': ['collapse']
        }),
        ('Auditoria', {
            'fields': ['criado_em', 'atualizado_em'],
            'classes': ['collapse']
        })
    ]
    
    actions = ['cancelar_execucoes']
    
    def cancelar_execucoes(self, request, queryset):
        """Action para cancelar execuções selecionadas"""
        from django.utils import timezone
        
        count = 0
        for item in queryset.filter(status__in=['PENDENTE', 'EXECUTANDO']):
            item.status = 'CANCELADA'
            item.finalizado_em = timezone.now()
            item.save()
            count += 1
        
        self.message_user(request, f'{count} execuções canceladas.')
    cancelar_execucoes.short_description = 'Cancelar execuções selecionadas'


@admin.register(CargaDiariaRotinas)
class CargaDiariaRotinasAdmin(admin.ModelAdmin):
    list_display = [
        'data_carga',
        'status', 
        'total_rotinas_processadas',
        'total_rotinas_adicionadas_fila',
        'duracao_segundos'
    ]
    list_filter = ['status', 'data_carga']
    readonly_fields = [
        'iniciado_em', 
        'finalizado_em', 
        'duracao_segundos',
        'arquivo_log'
    ]
    date_hierarchy = 'data_carga'
    
    fieldsets = [
        ('Carga', {
            'fields': ['data_carga', 'status']
        }),
        ('Estatísticas', {
            'fields': [
                'total_rotinas_processadas',
                'total_rotinas_adicionadas_fila', 
                'total_rotinas_ignoradas'
            ]
        }),
        ('Timing', {
            'fields': ['iniciado_em', 'finalizado_em', 'duracao_segundos']
        }),
        ('Log e Observações', {
            'fields': ['arquivo_log', 'observacoes', 'erro_detalhes'],
            'classes': ['collapse']
        })
    ]


@admin.register(LogScheduler)
class LogSchedulerAdmin(admin.ModelAdmin):
    list_display = [
        'criado_em',
        'nivel', 
        'componente', 
        'mensagem_resumida',
        'fila_execucao',
        'carga_diaria'
    ]
    list_filter = ['nivel', 'componente', 'criado_em']
    search_fields = ['mensagem', 'componente']
    readonly_fields = ['criado_em']
    date_hierarchy = 'criado_em'
    
    fieldsets = [
        ('Log', {
            'fields': [
                'nivel', 
                'componente', 
                'mensagem',
                'criado_em'
            ]
        }),
        ('Relacionamentos', {
            'fields': ['fila_execucao', 'carga_diaria']
        }),
        ('Dados Técnicos', {
            'fields': ['dados_extra', 'stack_trace'],
            'classes': ['collapse']
        })
    ]
    
    def mensagem_resumida(self, obj):
        return obj.mensagem[:100] + '...' if len(obj.mensagem) > 100 else obj.mensagem
    mensagem_resumida.short_description = 'Mensagem'
