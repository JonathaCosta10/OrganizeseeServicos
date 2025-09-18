"""
Serviços do Scheduler de Rotinas Automatizadas
=============================================

Este módulo contém todos os serviços relacionados ao scheduler de rotinas:
- Carga diária de rotinas
- Execução da fila
- Recovery de falhas
- Logging estruturado

Autor: Sistema Automatizado
Data: 16/09/2025
"""

import os
import json
import requests
import subprocess
import logging
import pytz
from datetime import datetime, date, time, timedelta
from typing import List, Dict, Any, Optional
from django.db import transaction, connection
from django.utils import timezone
from django.conf import settings
from croniter import croniter

from .models import (
    SchedulerRotina, FilaExecucao, CargaDiariaRotinas, 
    LogScheduler, GrupoDiasExecucao, RegistroExecucao
)

# Configurar timezone Brasil
BRAZIL_TZ = pytz.timezone('America/Sao_Paulo')

# Configurar logging
logger = logging.getLogger(__name__)


class SchedulerLogger:
    """Classe para logging estruturado do scheduler"""
    
    @staticmethod
    def log(nivel: str, componente: str, mensagem: str, 
            fila_execucao=None, carga_diaria=None, dados_extra=None, stack_trace=None):
        """Registra log no banco e no arquivo"""
        try:
            # Salvar no banco
            LogScheduler.objects.create(
                nivel=nivel,
                componente=componente,
                mensagem=mensagem,
                fila_execucao=fila_execucao,
                carga_diaria=carga_diaria,
                dados_extra=dados_extra,
                stack_trace=stack_trace
            )
            
            # Log também no sistema padrão
            log_level = getattr(logging, nivel.upper(), logging.INFO)
            logger.log(log_level, f"[{componente}] {mensagem}")
            
        except Exception as e:
            # Fallback: pelo menos logar no sistema
            logger.error(f"Erro ao salvar log: {e}")
            logger.log(logging.INFO, f"[{componente}] {mensagem}")


class CargaDiariaService:
    """Serviço responsável pela carga diária de rotinas"""
    
    def __init__(self):
        self.logger = SchedulerLogger()
        self.logs_pasta = os.path.join(settings.BASE_DIR, 'static', 'logs')
        os.makedirs(self.logs_pasta, exist_ok=True)
    
    def executar_carga_diaria(self, data_execucao: date = None) -> CargaDiariaRotinas:
        """Executa a carga diária de rotinas"""
        if data_execucao is None:
            data_execucao = timezone.now().astimezone(BRAZIL_TZ).date()
        
        self.logger.log('INFO', 'CargaDiaria', f'Iniciando carga diária para {data_execucao}')
        
        try:
            with transaction.atomic():
                # Verificar se já existe carga para esta data
                carga_existente = CargaDiariaRotinas.objects.select_for_update().filter(data_carga=data_execucao).first()
                
                if carga_existente:
                    # Marcar a carga anterior como substituída
                    self.logger.log('INFO', 'CargaDiaria', f'Substituindo carga existente para {data_execucao}')
                    
                    # Remover itens pendentes da fila associados à carga anterior
                    self._remover_itens_fila_por_data(data_execucao)
                    
                    # Atualizar carga existente ao invés de criar nova
                    carga = carga_existente
                    carga.status = 'INICIADA'
                    carga.iniciado_em = timezone.now()
                    carga.observacoes = f'Reiniciada em {timezone.now()}'
                    carga.save()
                else:
                    # Criar novo registro de carga
                    carga = CargaDiariaRotinas.objects.create(
                        data_carga=data_execucao,
                        status='INICIADA',
                        iniciado_em=timezone.now()
                    )
        except Exception as e:
            self.logger.log('ERROR', 'CargaDiaria', f'Erro ao inicializar carga diária: {e}')
            raise
        
        try:
            with transaction.atomic():
                resultado = self._processar_rotinas_do_dia(data_execucao, carga)
                carga.status = 'CONCLUIDA'
                carga.finalizado_em = timezone.now()
                carga.duracao_segundos = int((carga.finalizado_em - carga.iniciado_em).total_seconds())
                carga.save()
                
                # Gerar log estruturado
                self._gerar_log_estruturado(carga, resultado)
                
                self.logger.log('INFO', 'CargaDiaria', 
                              f'Carga concluída: {resultado["total_adicionadas"]} rotinas adicionadas à fila')
                
                return carga
                
        except Exception as e:
            carga.status = 'ERRO'
            carga.finalizado_em = timezone.now()
            carga.erro_detalhes = str(e)
            carga.save()
            
            self.logger.log('ERROR', 'CargaDiaria', f'Erro na carga diária: {e}', 
                          carga_diaria=carga, stack_trace=str(e))
            raise
    
    def _processar_rotinas_do_dia(self, data_execucao: date, carga: CargaDiariaRotinas) -> Dict[str, Any]:
        """Processa as rotinas que devem ser executadas no dia"""
        resultado = {
            'total_processadas': 0,
            'total_adicionadas': 0,
            'total_ignoradas': 0,
            'rotinas_adicionadas': [],
            'rotinas_ignoradas': []
        }
        
        # Resetar contadores da carga para evitar dados desatualizados
        carga.total_rotinas_processadas = 0
        carga.total_rotinas_adicionadas_fila = 0
        carga.total_rotinas_ignoradas = 0
        carga.save()
        
        # Registrar início do processamento
        self.logger.log('INFO', 'CargaDiaria', f'Iniciando processamento das rotinas para {data_execucao}')
        
        # Buscar rotinas ativas com dados atualizados
        # Não fechamos a conexão para evitar problemas com "connection already closed"
        # Em vez disso, garantimos que a consulta seja atualizada usando .all().select_related()
        rotinas = SchedulerRotina.objects.all().filter(
            rotina_definicao__ativo=True,
            executar=True
        ).select_related('rotina_definicao', 'grupo_dias')
        
        for rotina in rotinas:
            resultado['total_processadas'] += 1
            
            if self._deve_executar_rotina(rotina, data_execucao):
                # Garantir que estamos usando dados atualizados
                rotina_atualizada = SchedulerRotina.objects.get(pk=rotina.pk)
                self.logger.log('INFO', 'CargaDiaria', 
                              f'Adicionando rotina {rotina.rotina_definicao.nome_exibicao} com horário {rotina_atualizada.horario_execucao}')
                
                self._adicionar_na_fila(rotina, data_execucao)
                resultado['total_adicionadas'] += 1
                resultado['rotinas_adicionadas'].append({
                    'nome': rotina.rotina_definicao.nome_exibicao,
                    'horario': rotina_atualizada.horario_execucao.strftime('%H:%M'),
                    'tipo': rotina.get_tipo_execucao_display()
                })
            else:
                resultado['total_ignoradas'] += 1
                resultado['rotinas_ignoradas'].append({
                    'nome': rotina.rotina_definicao.nome_exibicao,
                    'motivo': self._motivo_ignorar_rotina(rotina, data_execucao)
                })
        
        # Atualizar estatísticas da carga
        carga.total_rotinas_processadas = resultado['total_processadas']
        carga.total_rotinas_adicionadas_fila = resultado['total_adicionadas']
        carga.total_rotinas_ignoradas = resultado['total_ignoradas']
        carga.save()
        
        return resultado
    
    def _deve_executar_rotina(self, rotina: SchedulerRotina, data_execucao: date) -> bool:
        """Verifica se a rotina deve ser executada na data especificada"""
        
        # Verificar se rotina está ativa
        if not rotina.rotina_definicao.ativo or not rotina.executar:
            return False
        
        # Verificar tipo de execução
        if rotina.tipo_execucao == 'EVENTUAL':
            # Eventual só executa se explicitamente marcado
            return True
        
        elif rotina.tipo_execucao == 'MENSAL':
            # Mensal executa apenas no primeiro dia do mês
            return data_execucao.day == 1
        
        elif rotina.tipo_execucao == 'CICLICO':
            # Cíclico sempre executa (será controlado pelo executor)
            return True
        
        elif rotina.tipo_execucao == 'DIARIO':
            # Verificar grupo de dias
            if rotina.grupo_dias:
                dia_semana = data_execucao.weekday()  # 0=Segunda, 6=Domingo
                dias_permitidos = rotina.grupo_dias.dias_da_semana_ativados()
                return dia_semana in dias_permitidos
            else:
                # Sem grupo definido = todos os dias
                return True
        
        return False
    
    def _motivo_ignorar_rotina(self, rotina: SchedulerRotina, data_execucao: date) -> str:
        """Retorna o motivo pelo qual a rotina foi ignorada"""
        if not rotina.rotina_definicao.ativo:
            return "Rotina inativa"
        
        if not rotina.executar:
            return "Execução desabilitada"
        
        if rotina.tipo_execucao == 'MENSAL' and data_execucao.day != 1:
            return "Mensal - não é primeiro dia do mês"
        
        if rotina.tipo_execucao == 'DIARIO' and rotina.grupo_dias:
            dia_semana = data_execucao.weekday()
            dias_permitidos = rotina.grupo_dias.dias_da_semana_ativados()
            if dia_semana not in dias_permitidos:
                return f"Grupo de dias não permite execução"
        
        return "Motivo não identificado"
    
    def _adicionar_na_fila(self, rotina: SchedulerRotina, data_execucao: date):
        """Adiciona rotina na fila de execução"""
        
        # Primeiro, garantir que temos os dados mais recentes da rotina
        rotina_atualizada = SchedulerRotina.objects.get(pk=rotina.pk)
        
        # Verificar se já existe na fila para evitar duplicatas
        existe = FilaExecucao.objects.filter(
            scheduler_rotina=rotina,
            data_execucao=data_execucao,
            status='PENDENTE'  # Verificar apenas pendentes
        ).exists()
        
        if not existe:
            FilaExecucao.objects.create(
                scheduler_rotina=rotina,
                data_execucao=data_execucao,
                horario_execucao=rotina_atualizada.horario_execucao,  # Usar horário atualizado
                prioridade=rotina_atualizada.prioridade,  # Usar prioridade atualizada
                max_tentativas=rotina_atualizada.max_tentativas_recovery
            )
            
            self.logger.log('DEBUG', 'CargaDiaria', 
                          f'Rotina adicionada à fila: {rotina.rotina_definicao.nome_exibicao} às {rotina_atualizada.horario_execucao}')
    
    def _remover_itens_fila_por_data(self, data_execucao: date):
        """Remove itens pendentes da fila para uma determinada data"""
        # Remove todos os itens PENDENTES para a data, independente da origem
        with transaction.atomic():
            # Log detalhado antes da remoção para auditoria
            itens_por_rotina = {}
            for item in FilaExecucao.objects.filter(
                data_execucao=data_execucao,
                status='PENDENTE'
            ):
                nome_rotina = item.scheduler_rotina.rotina_definicao.nome_exibicao
                if nome_rotina in itens_por_rotina:
                    itens_por_rotina[nome_rotina] += 1
                else:
                    itens_por_rotina[nome_rotina] = 1
            
            # Efetuar a remoção
            itens_removidos = FilaExecucao.objects.filter(
                data_execucao=data_execucao,
                status='PENDENTE'
            ).delete()
            
            count = itens_removidos[0] if isinstance(itens_removidos, tuple) else 0
            
            if count > 0:
                self.logger.log('INFO', 'CargaDiaria', 
                    f'Removendo {count} itens pendentes da fila para data {data_execucao}')
                
                # Log detalhado por rotina
                for rotina, quantidade in itens_por_rotina.items():
                    self.logger.log('DEBUG', 'CargaDiaria', 
                        f'Removidos {quantidade} item(ns) da rotina: {rotina}')
    
    def _gerar_log_estruturado(self, carga: CargaDiariaRotinas, resultado: Dict[str, Any]):
        """Gera log estruturado da carga diária"""
        data_str = carga.data_carga.strftime('%d%m%Y')
        nome_arquivo = f"ROTINA-DIARIA-{data_str}.txt"
        caminho_log = os.path.join(self.logs_pasta, nome_arquivo)
        
        try:
            with open(caminho_log, 'w', encoding='utf-8') as log_file:
                log_file.write("=" * 80 + "\n")
                log_file.write("LOG DE CARGA DIÁRIA DE ROTINAS\n")
                log_file.write("=" * 80 + "\n\n")
                
                # Informações gerais
                log_file.write("INFORMAÇÕES GERAIS\n")
                log_file.write("-" * 40 + "\n")
                log_file.write(f"Data da carga: {carga.data_carga.strftime('%d/%m/%Y')}\n")
                log_file.write(f"Horário de início: {carga.iniciado_em.astimezone(BRAZIL_TZ).strftime('%d/%m/%Y %H:%M:%S')}\n")
                log_file.write(f"Horário de finalização: {carga.finalizado_em.astimezone(BRAZIL_TZ).strftime('%d/%m/%Y %H:%M:%S')}\n")
                log_file.write(f"Duração: {carga.duracao_segundos} segundos\n")
                log_file.write(f"Status: {carga.get_status_display()}\n\n")
                
                # Estatísticas
                log_file.write("ESTATÍSTICAS DE PROCESSAMENTO\n")
                log_file.write("-" * 40 + "\n")
                log_file.write(f"Total de rotinas processadas: {resultado['total_processadas']}\n")
                log_file.write(f"Total de rotinas adicionadas à fila: {resultado['total_adicionadas']}\n")
                log_file.write(f"Total de rotinas ignoradas: {resultado['total_ignoradas']}\n\n")
                
                # Rotinas adicionadas
                if resultado['rotinas_adicionadas']:
                    log_file.write("ROTINAS ADICIONADAS À FILA\n")
                    log_file.write("-" * 40 + "\n")
                    for rotina in resultado['rotinas_adicionadas']:
                        log_file.write(f"   - {rotina['nome']} ({rotina['tipo']}) - {rotina['horario']}\n")
                    log_file.write("\n")
                
                # Rotinas ignoradas
                if resultado['rotinas_ignoradas']:
                    log_file.write("ROTINAS IGNORADAS\n")
                    log_file.write("-" * 40 + "\n")
                    for rotina in resultado['rotinas_ignoradas']:
                        log_file.write(f"   - {rotina['nome']} - Motivo: {rotina['motivo']}\n")
                    log_file.write("\n")
                
                log_file.write("=" * 80 + "\n")
                log_file.write("FIM DO LOG\n")
                log_file.write("=" * 80 + "\n")
            
            carga.arquivo_log = caminho_log
            carga.save()
            
            self.logger.log('INFO', 'CargaDiaria', f'Log estruturado gerado: {nome_arquivo}')
            
        except Exception as e:
            self.logger.log('ERROR', 'CargaDiaria', f'Erro ao gerar log estruturado: {e}')


class ExecutorRotinas:
    """Serviço responsável pela execução das rotinas na fila"""
    
    def __init__(self):
        self.logger = SchedulerLogger()
        
    def verificar_rotinas_travadas(self, limite_horas: int = 1) -> Dict[str, Any]:
        """Verifica se há rotinas travadas e as marca como erro"""
        from django.utils import timezone
        from datetime import timedelta
        
        # Considerar como travadas rotinas que estão executando há mais tempo que o limite
        hora_limite = timezone.now() - timedelta(hours=limite_horas)
        
        # Buscar rotinas potencialmente travadas
        travadas = FilaExecucao.objects.filter(
            status='EXECUTANDO',
            iniciado_em__lt=hora_limite
        )
        
        resultado = {
            'total_rotinas_travadas': 0,
            'rotinas_corrigidas': []
        }
        
        for item in travadas:
            try:
                nome_rotina = item.scheduler_rotina.rotina_definicao.nome_exibicao
                duracao = timezone.now() - item.iniciado_em
                duracao_minutos = duracao.total_seconds() / 60
                
                self.logger.log('WARNING', 'Executor', 
                              f'Rotina travada detectada: {nome_rotina} - Executando há {duracao_minutos:.1f} minutos')
                
                # Marcar como erro
                item.status = 'ERRO'
                item.finalizado_em = timezone.now()
                item.duracao_segundos = int(duracao.total_seconds())
                item.codigo_retorno = -1
                item.saida_stderr = f"Rotina interrompida automaticamente após {duracao_minutos:.1f} minutos"
                item.erro_detalhes = f"Execução excedeu o tempo máximo de {limite_horas} hora(s)"
                item.save()
                
                resultado['total_rotinas_travadas'] += 1
                resultado['rotinas_corrigidas'].append({
                    'id': item.id,
                    'nome': nome_rotina,
                    'duracao_minutos': duracao_minutos
                })
                
                # Verificar se deve tentar recovery
                if item.tentativa_atual < item.max_tentativas and item.scheduler_rotina.permite_recovery:
                    self._agendar_recovery(item)
            
            except Exception as e:
                self.logger.log('ERROR', 'Executor', f'Erro ao corrigir rotina travada: {e}')
                
        return resultado
    
    def executar_fila(self, limite_execucoes: int = None) -> Dict[str, Any]:
        """Executa rotinas pendentes na fila"""
        agora = timezone.now().astimezone(BRAZIL_TZ)
        data_atual = agora.date()
        hora_atual = agora.time()
        
        # Buscar rotinas pendentes que devem ser executadas
        fila_query = FilaExecucao.objects.filter(
            status='PENDENTE',
            data_execucao__lte=data_atual
        ).filter(
            horario_execucao__lte=hora_atual
        ).order_by('data_execucao', 'horario_execucao', '-prioridade')  # Prioridade decrescente
        
        if limite_execucoes:
            fila_query = fila_query[:limite_execucoes]
        
        resultado = {
            'total_executadas': 0,
            'total_sucesso': 0,
            'total_erro': 0,
            'execucoes': []
        }
        
        for item_fila in fila_query:
            resultado_execucao = self._executar_rotina(item_fila)
            resultado['execucoes'].append(resultado_execucao)
            resultado['total_executadas'] += 1
            
            if resultado_execucao['sucesso']:
                resultado['total_sucesso'] += 1
            else:
                resultado['total_erro'] += 1
        
        return resultado
    
    def _executar_rotina(self, item_fila: FilaExecucao) -> Dict[str, Any]:
        """Executa uma rotina específica"""
        rotina = item_fila.scheduler_rotina
        
        # Log detalhado com horário atual e horário programado
        agora = timezone.now().astimezone(BRAZIL_TZ)
        self.logger.log('INFO', 'Executor', 
                       f'Iniciando execução: {rotina.rotina_definicao.nome_exibicao} - '
                       f'Horário atual: {agora.strftime("%H:%M:%S")}, '
                       f'Horário programado: {item_fila.horario_execucao}', 
                       fila_execucao=item_fila)
        
        # Marcar como executando
        item_fila.status = 'EXECUTANDO'
        item_fila.iniciado_em = timezone.now()
        item_fila.save()
        
        try:
            with transaction.atomic():
                if rotina.tipo_rotina == 'CARGA_ARQUIVO':
                    resultado = self._executar_carga_arquivo(item_fila)
                elif rotina.tipo_rotina == 'DOWNLOAD_ARQUIVO':
                    resultado = self._executar_download_arquivo(item_fila)
                elif rotina.tipo_rotina == 'CHAMADA_API':
                    resultado = self._executar_chamada_api(item_fila)
                elif rotina.tipo_rotina == 'EXECUCAO_SCRIPT':
                    resultado = self._executar_script(item_fila)
                else:
                    raise ValueError(f"Tipo de rotina não suportado: {rotina.tipo_rotina}")
                
                # Marcar como concluída
                item_fila.status = 'CONCLUIDA'
                item_fila.finalizado_em = timezone.now()
                item_fila.duracao_segundos = int((item_fila.finalizado_em - item_fila.iniciado_em).total_seconds())
                item_fila.codigo_retorno = 0
                item_fila.saida_stdout = resultado.get('stdout', '')
                item_fila.save()
                
                self.logger.log('INFO', 'Executor', 
                              f'Execução concluída com sucesso: {rotina.rotina_definicao.nome_exibicao}', 
                              fila_execucao=item_fila)
                
                return {'sucesso': True, 'item_fila': item_fila, 'resultado': resultado}
                
        except Exception as e:
            # Marcar como erro
            item_fila.status = 'ERRO'
            item_fila.finalizado_em = timezone.now()
            item_fila.duracao_segundos = int((item_fila.finalizado_em - item_fila.iniciado_em).total_seconds())
            item_fila.codigo_retorno = -1
            item_fila.saida_stderr = str(e)
            item_fila.erro_detalhes = str(e)
            item_fila.save()
            
            self.logger.log('ERROR', 'Executor', 
                          f'Erro na execução: {rotina.rotina_definicao.nome_exibicao} - {e}', 
                          fila_execucao=item_fila, stack_trace=str(e))
            
            # Verificar se deve tentar recovery
            if item_fila.tentativa_atual < item_fila.max_tentativas and rotina.permite_recovery:
                self._agendar_recovery(item_fila)
            
            return {'sucesso': False, 'item_fila': item_fila, 'erro': str(e)}
    
    def _executar_carga_arquivo(self, item_fila: FilaExecucao) -> Dict[str, Any]:
        """Executa carga de arquivo"""
        rotina = item_fila.scheduler_rotina
        
        # Encontrar TODOS os arquivos baseados na máscara para os últimos 3 dias
        if rotina.mascara_arquivo:
            arquivos_encontrados = self._encontrar_arquivos_ultimos_dias(rotina.mascara_arquivo, rotina.pasta_origem, dias=3)
            
            # Se não encontrou NENHUM arquivo, isso é um erro
            if not arquivos_encontrados:
                # Tenta buscar apenas o mais recente (compatibilidade)
                arquivo_fallback = self._encontrar_arquivo_por_mascara(rotina.mascara_arquivo, rotina.pasta_origem)
                if arquivo_fallback:
                    arquivos_encontrados = [arquivo_fallback]
                else:
                    self.logger.log('WARNING', 'Executor', f"Nenhum arquivo encontrado para máscara: {rotina.mascara_arquivo}")
                    return {
                        'status': 'warning', 
                        'message': f'Nenhum arquivo encontrado para máscara: {rotina.mascara_arquivo}',
                        'arquivos_processados': 0
                    }
            
            # Processar todos os arquivos encontrados
            resultados = []
            sucessos = 0
            erros = 0
            
            self.logger.log('INFO', 'Executor', f"Iniciando carga de {len(arquivos_encontrados)} arquivo(s)")
            
            for i, arquivo in enumerate(arquivos_encontrados, 1):
                nome_arquivo = os.path.basename(arquivo)
                
                try:
                    self.logger.log('DEBUG', 'Executor', f"Processando arquivo {i}/{len(arquivos_encontrados)}: {nome_arquivo}")
                    
                    item_fila.arquivo_processado = arquivo
                    item_fila.save()
                    
                    # Chamar endpoint API se configurado
                    if rotina.endpoint_url:
                        resultado = self._chamar_endpoint_carga(rotina, arquivo)
                        resultados.append({
                            'arquivo': nome_arquivo,
                            'status': 'sucesso',
                            'resultado': resultado
                        })
                        sucessos += 1
                        self.logger.log('INFO', 'Executor', f"Carga concluída com sucesso: {nome_arquivo}")
                    
                except Exception as e:
                    erros += 1
                    erro_msg = str(e)
                    self.logger.log('ERROR', 'Executor', f"Erro na carga do arquivo {nome_arquivo}: {erro_msg}")
                    resultados.append({
                        'arquivo': nome_arquivo,
                        'status': 'erro',
                        'erro': erro_msg
                    })
                    # Continua processando outros arquivos mesmo se um falhar
            
            # Retornar resultado consolidado
            status_final = 'success' if sucessos > 0 else ('warning' if erros == 0 else 'partial_success')
            
            self.logger.log('INFO', 'Executor', f"Carga finalizada: {sucessos} sucessos, {erros} erros, {len(arquivos_encontrados)} total")
            
            return {
                'status': status_final,
                'arquivos_processados': len(arquivos_encontrados),
                'sucessos': sucessos,
                'erros': erros,
                'detalhes': resultados,
                'stdout': f"Processados {len(arquivos_encontrados)} arquivos: {sucessos} sucessos, {erros} erros"
            }
        
        return {'status': 'error', 'message': 'Máscara de arquivo não configurada'}
    
    def _executar_download_arquivo(self, item_fila: FilaExecucao) -> Dict[str, Any]:
        """Executa download de arquivo"""
        rotina = item_fila.scheduler_rotina
        
        # Se tem endpoint configurado, chamar via API
        if rotina.endpoint_url:
            return self._executar_chamada_api(item_fila)
        
        # Senão, executar como script
        return self._executar_script(item_fila)
    
    def _executar_chamada_api(self, item_fila: FilaExecucao) -> Dict[str, Any]:
        """Executa chamada API"""
        rotina = item_fila.scheduler_rotina
        
        headers = {}
        if rotina.headers_json:
            headers = json.loads(rotina.headers_json)
        
        payload = {}
        if rotina.payload_json:
            payload = json.loads(rotina.payload_json)
        
        response = requests.request(
            method=rotina.metodo_http,
            url=rotina.endpoint_url,
            json=payload,
            headers=headers,
            timeout=rotina.rotina_definicao.timeout_segundos
        )
        
        response.raise_for_status()
        
        return {
            'status_code': response.status_code,
            'response': response.text,
            'stdout': f"API call successful: {response.status_code}"
        }
    
    def _executar_script(self, item_fila: FilaExecucao) -> Dict[str, Any]:
        """Executa script do sistema"""
        rotina = item_fila.scheduler_rotina
        
        comando = rotina.rotina_definicao.comando_management
        argumentos = rotina.rotina_definicao.argumentos_padrao.split() if rotina.rotina_definicao.argumentos_padrao else []
        
        resultado = subprocess.run(
            [comando] + argumentos,
            capture_output=True,
            text=True,
            timeout=rotina.rotina_definicao.timeout_segundos
        )
        
        if resultado.returncode != 0:
            raise subprocess.CalledProcessError(resultado.returncode, comando, resultado.stderr)
        
        return {
            'stdout': resultado.stdout,
            'stderr': resultado.stderr,
            'returncode': resultado.returncode
        }
    
    def _encontrar_arquivo_por_mascara(self, mascara: str, pasta: str = None) -> Optional[str]:
        """Encontra arquivo baseado na máscara"""
        import glob
        
        if pasta is None:
            pasta = os.path.join(settings.BASE_DIR, 'static', 'downloadbruto')
        
        # Substituir data atual na máscara se necessário
        hoje = timezone.now().astimezone(BRAZIL_TZ).date()
        mascara_processada = mascara.replace('*YYYYMMDD*', hoje.strftime('%Y%m%d'))
        mascara_processada = mascara_processada.replace('*DDMMYYYY*', hoje.strftime('%d%m%Y'))
        
        caminho_busca = os.path.join(pasta, mascara_processada)
        arquivos = glob.glob(caminho_busca)
        
        if arquivos:
            # Retornar o mais recente
            return max(arquivos, key=os.path.getctime)
        
        return None
    
    def _encontrar_arquivos_ultimos_dias(self, mascara: str, pasta: str = None, dias: int = 3) -> List[str]:
        """Encontra todos os arquivos baseados na máscara para os últimos N dias úteis"""
        import glob
        from datetime import timedelta
        
        if pasta is None:
            pasta = os.path.join(settings.BASE_DIR, 'static', 'downloadbruto')
        
        arquivos_encontrados = []
        hoje = timezone.now().astimezone(BRAZIL_TZ).date()
        
        self.logger.log('DEBUG', 'Executor', f"Buscando arquivos para {dias} dias úteis com máscara: {mascara}")
        
        # Verificar se a máscara tem placeholders de data
        tem_placeholder_data = ('*YYYYMMDD*' in mascara or '*DDMMYYYY*' in mascara)
        
        if tem_placeholder_data:
            # Buscar arquivos para os últimos N dias úteis específicos
            dias_verificados = 0
            delta = 0
            
            while dias_verificados < dias and delta <= 15:  # Máximo 15 dias para trás
                data_busca = hoje - timedelta(days=delta)
                
                # Verificar se é dia útil (segunda a sexta)
                if data_busca.weekday() < 5:  # 0=segunda, 4=sexta
                    # Substituir datas na máscara
                    mascara_processada = mascara.replace('*YYYYMMDD*', data_busca.strftime('%Y%m%d'))
                    mascara_processada = mascara_processada.replace('*DDMMYYYY*', data_busca.strftime('%d%m%Y'))
                    
                    caminho_busca = os.path.join(pasta, mascara_processada)
                    arquivos_data = glob.glob(caminho_busca)
                    
                    if arquivos_data:
                        self.logger.log('DEBUG', 'Executor', f"Encontrados {len(arquivos_data)} arquivo(s) para {data_busca}: {[os.path.basename(a) for a in arquivos_data]}")
                        arquivos_encontrados.extend(arquivos_data)
                    else:
                        self.logger.log('DEBUG', 'Executor', f"Nenhum arquivo encontrado para {data_busca} (normal, nem todos os dias têm dados)")
                    
                    dias_verificados += 1
                
                delta += 1
        else:
            # Para máscaras simples (como TradeInformationConsolidatedFile*.csv),
            # buscar todos os arquivos e filtrar pelos últimos N dias úteis
            caminho_busca = os.path.join(pasta, mascara)
            todos_arquivos = glob.glob(caminho_busca)
            
            if todos_arquivos:
                # Filtrar arquivos pelos últimos N dias úteis baseado na data do arquivo
                arquivos_com_data = []
                
                for arquivo in todos_arquivos:
                    # Tentar extrair data do nome do arquivo (formato: YYYYMMDD)
                    nome = os.path.basename(arquivo)
                    import re
                    match = re.search(r'(\d{8})', nome)  # Buscar 8 dígitos consecutivos
                    
                    if match:
                        try:
                            data_str = match.group(1)
                            data_arquivo = datetime.strptime(data_str, '%Y%m%d').date()
                            arquivos_com_data.append((arquivo, data_arquivo))
                            self.logger.log('DEBUG', 'Executor', f"Arquivo {nome} data extraída: {data_arquivo}")
                        except ValueError:
                            self.logger.log('DEBUG', 'Executor', f"Não foi possível extrair data válida de: {nome}")
                    else:
                        self.logger.log('DEBUG', 'Executor', f"Padrão de data não encontrado em: {nome}")
                
                # Filtrar pelos últimos N dias úteis
                if arquivos_com_data:
                    dias_verificados = 0
                    delta = 0
                    
                    while dias_verificados < dias and delta <= 15:
                        data_busca = hoje - timedelta(days=delta)
                        
                        if data_busca.weekday() < 5:  # Dia útil
                            arquivos_desta_data = [arq for arq, data in arquivos_com_data if data == data_busca]
                            if arquivos_desta_data:
                                arquivos_encontrados.extend(arquivos_desta_data)
                                self.logger.log('DEBUG', 'Executor', f"Encontrados {len(arquivos_desta_data)} arquivo(s) para {data_busca}")
                            
                            dias_verificados += 1
                        
                        delta += 1
        
        # Retornar arquivos ordenados por data (mais antigos primeiro)
        arquivos_ordenados = sorted(set(arquivos_encontrados))  # Remove duplicatas
        self.logger.log('INFO', 'Executor', f"Total de arquivos encontrados: {len(arquivos_ordenados)} para {dias} dias úteis")
        
        return arquivos_ordenados
    
    def _chamar_endpoint_carga(self, rotina: SchedulerRotina, arquivo: str) -> Dict[str, Any]:
        """Chama endpoint para carga de arquivo"""
        
        payload = {
            'acao': 'carga',  # Minúsculo conforme esperado pela API
            'arquivo': os.path.basename(arquivo)
        }
        
        response = requests.post(
            rotina.endpoint_url,
            json=payload,
            timeout=rotina.rotina_definicao.timeout_segundos
        )
        
        response.raise_for_status()
        
        return {
            'status_code': response.status_code,
            'response': response.text,
            'stdout': f"Carga de arquivo successful: {response.status_code}",
            'arquivo': arquivo
        }
    
    def _agendar_recovery(self, item_fila: FilaExecucao):
        """Agenda tentativa de recovery"""
        rotina = item_fila.scheduler_rotina
        
        item_fila.status = 'RECOVERY'
        item_fila.tentativa_atual += 1
        item_fila.ultima_tentativa_em = timezone.now()
        
        # Agendar para daqui X minutos
        delay_minutos = rotina.delay_recovery_minutos * item_fila.tentativa_atual
        novo_horario = timezone.now() + timedelta(minutes=delay_minutos)
        
        item_fila.horario_execucao = novo_horario.time()
        item_fila.save()
        
        self.logger.log('INFO', 'Executor', 
                       f'Recovery agendado para {novo_horario}: {rotina.rotina_definicao.nome_exibicao}', 
                       fila_execucao=item_fila)


class SchedulerService:
    """Serviço principal do scheduler"""
    
    def __init__(self):
        self.carga_diaria = CargaDiariaService()
        self.executor = ExecutorRotinas()
        self.logger = SchedulerLogger()
    
    def executar_scheduler_completo(self):
        """Executa o scheduler completo: carga diária + execução da fila"""
        try:
            # 1. Executar carga diária (se necessário)
            agora = timezone.now().astimezone(BRAZIL_TZ)
            if agora.hour == 8 and agora.minute == 0:  # 08:00
                self.carga_diaria.executar_carga_diaria()
            
            # 2. Executar fila de rotinas
            resultado = self.executor.executar_fila(limite_execucoes=10)
            
            if resultado['total_executadas'] > 0:
                self.logger.log('INFO', 'Scheduler', 
                              f"Scheduler executado: {resultado['total_sucesso']} sucessos, {resultado['total_erro']} erros")
            
            return resultado
            
        except Exception as e:
            self.logger.log('ERROR', 'Scheduler', f'Erro no scheduler principal: {e}', stack_trace=str(e))
            raise
    
    def corrigir_horarios_desatualizados_fila(self) -> int:
        """Verifica e corrige itens na fila com horários desatualizados
        
        Retorna o número de itens desatualizados encontrados
        """
        try:
            with transaction.atomic():
                itens_desatualizados = []
                itens_pendentes = FilaExecucao.objects.filter(status='PENDENTE')
                
                for item in itens_pendentes:
                    # Comparar horário do item na fila com horário atual da rotina
                    rotina_atual = SchedulerRotina.objects.get(pk=item.scheduler_rotina.pk)
                    
                    # Verificar se o horário está desatualizado
                    if item.horario_execucao != rotina_atual.horario_execucao:
                        itens_desatualizados.append({
                            'item_id': item.pk,
                            'rotina': rotina_atual.rotina_definicao.nome_exibicao,
                            'horario_antigo': item.horario_execucao,
                            'horario_atual': rotina_atual.horario_execucao
                        })
                        
                        self.logger.log('WARNING', 'Scheduler', 
                                     f'Horário desatualizado para {rotina_atual.rotina_definicao.nome_exibicao}: '
                                     f'{item.horario_execucao} -> {rotina_atual.horario_execucao}')
                
                # Se encontrou itens desatualizados, remove todos os pendentes
                # para serem substituídos por novos na carga diária
                if itens_desatualizados:
                    # Registrar detalhes antes de remover
                    for item in itens_desatualizados:
                        self.logger.log('INFO', 'Scheduler', 
                                     f'Removendo item desatualizado: {item["rotina"]}, '
                                     f'horário antigo: {item["horario_antigo"]}, horário atual: {item["horario_atual"]}')
                    
                    # Remover todos os itens pendentes para garantir que serão recriados com horários corretos
                    hoje = timezone.now().astimezone(BRAZIL_TZ).date()
                    FilaExecucao.objects.filter(data_execucao=hoje, status='PENDENTE').delete()
                
                return len(itens_desatualizados)
                
        except Exception as e:
            self.logger.log('ERROR', 'Scheduler', f'Erro ao verificar horários desatualizados: {e}')
            return 0
    
    def verificar_duplicatas_fila(self) -> int:
        """Verifica e remove duplicatas na fila de execução
        
        Retorna o número de itens duplicados removidos
        """
        try:
            with transaction.atomic():
                # Identificar duplicatas - itens com mesma rotina, data e horário em status PENDENTE
                from django.db.models import Count
                duplicatas = FilaExecucao.objects.filter(
                    status='PENDENTE'
                ).values('scheduler_rotina', 'data_execucao', 'horario_execucao'
                ).annotate(
                    total=Count('*')
                ).filter(total__gt=1)
                
                total_removidos = 0
                
                for duplicata in duplicatas:
                    # Para cada grupo de duplicatas, manter apenas o item mais recente
                    itens = FilaExecucao.objects.filter(
                        scheduler_rotina=duplicata['scheduler_rotina'],
                        data_execucao=duplicata['data_execucao'],
                        horario_execucao=duplicata['horario_execucao'],
                        status='PENDENTE'
                    ).order_by('-criado_em')
                    
                    # Manter o primeiro (mais recente) e excluir os demais
                    if itens.count() > 1:
                        primeiro = itens.first()
                        removidos = itens.exclude(pk=primeiro.pk).delete()
                        total_removidos += removidos[0]
                        
                        # Registrar no log
                        rotina = SchedulerRotina.objects.get(pk=duplicata['scheduler_rotina'])
                        self.logger.log('INFO', 'Scheduler', 
                                      f'Removidas {removidos[0]} duplicata(s) para {rotina.rotina_definicao.nome_exibicao}')
                
                return total_removidos
                
        except Exception as e:
            self.logger.log('ERROR', 'Scheduler', f'Erro ao verificar duplicatas: {e}')
            return 0
            