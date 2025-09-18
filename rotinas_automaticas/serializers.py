"""
Serializadores para as APIs de rotinas automáticas
"""
from rest_framework import serializers
from .models import SchedulerRotina, RotinaDefinicao, GrupoDiasExecucao, FilaExecucao


class GrupoDiasExecucaoSerializer(serializers.ModelSerializer):
    """Serializador para grupos de dias de execução"""
    
    class Meta:
        model = GrupoDiasExecucao
        fields = ['id', 'nome', 'descricao', 'segunda', 'terca', 'quarta', 
                  'quinta', 'sexta', 'sabado', 'domingo']


class RotinaDefinicaoSerializer(serializers.ModelSerializer):
    """Serializador para definição de rotinas"""
    
    class Meta:
        model = RotinaDefinicao
        fields = ['id', 'nome', 'nome_exibicao', 'descricao', 'comando_management',
                  'argumentos_padrao', 'periodo_cron', 'fuso_horario', 'ativo']


class SchedulerRotinaSerializer(serializers.ModelSerializer):
    """Serializador para rotinas do scheduler"""
    
    nome = serializers.SerializerMethodField()
    nome_exibicao = serializers.SerializerMethodField()
    descricao = serializers.SerializerMethodField()
    grupo_dias_nome = serializers.SerializerMethodField()
    
    class Meta:
        model = SchedulerRotina
        fields = [
            'id', 'nome', 'nome_exibicao', 'descricao', 'tipo_execucao', 
            'tipo_rotina', 'grupo_dias', 'grupo_dias_nome', 'ciclico', 
            'intervalo_horas', 'executar', 'horario_execucao', 'endpoint_url',
            'metodo_http', 'mascara_arquivo', 'pasta_origem', 'permite_recovery',
            'max_tentativas_recovery', 'prioridade', 'criado_em', 'atualizado_em'
        ]
    
    def get_nome(self, obj):
        """Retorna o nome da rotina definição"""
        if obj.rotina_definicao:
            return obj.rotina_definicao.nome
        return None
    
    def get_nome_exibicao(self, obj):
        """Retorna o nome de exibição da rotina definição"""
        if obj.rotina_definicao:
            return obj.rotina_definicao.nome_exibicao
        return None
    
    def get_descricao(self, obj):
        """Retorna a descrição da rotina definição"""
        if obj.rotina_definicao:
            return obj.rotina_definicao.descricao
        return None
    
    def get_grupo_dias_nome(self, obj):
        """Retorna o nome do grupo de dias"""
        if obj.grupo_dias:
            return obj.grupo_dias.get_nome_display()
        return None


class FilaExecucaoSerializer(serializers.ModelSerializer):
    """Serializador para a fila de execução"""
    
    nome_rotina = serializers.SerializerMethodField()
    tipo_rotina = serializers.SerializerMethodField()
    
    class Meta:
        model = FilaExecucao
        fields = [
            'id', 'scheduler_rotina', 'nome_rotina', 'tipo_rotina',
            'data_execucao', 'horario_execucao', 'status',
            'prioridade', 'iniciado_em', 'finalizado_em',
            'duracao_segundos', 'tentativa_atual', 'max_tentativas',
            'codigo_retorno', 'erro_detalhes'
        ]
    
    def get_nome_rotina(self, obj):
        """Retorna o nome da rotina"""
        if obj.scheduler_rotina and obj.scheduler_rotina.rotina_definicao:
            return obj.scheduler_rotina.rotina_definicao.nome_exibicao
        return "Rotina Sem Nome"
    
    def get_tipo_rotina(self, obj):
        """Retorna o tipo da rotina"""
        if obj.scheduler_rotina:
            return obj.scheduler_rotina.get_tipo_rotina_display()
        return None
