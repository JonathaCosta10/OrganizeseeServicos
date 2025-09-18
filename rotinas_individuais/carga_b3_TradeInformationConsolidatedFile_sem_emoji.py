#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Rotina de Carga: B3 TradeInformationConsolidatedFile
=====================================================

Este script processa arquivos TradeInformationConsolidatedFile da B3 e carrega os dados
na tabela 'organizesee_ativosprecos', filtrando apenas dados relevantes (FII e Ações).

Requisitos:
- Filtrar linhas com MaxPrice (coluna F) não nulo
- Classificar ticker como FII ou Ação baseado em tabelas de referência
- Carregar apenas tickers conhecidos (FII ou Ação)
- Mover arquivos processados para pasta 'processados'

Autor: Sistema Automatizado
Data: 10/09/2025
"""

import os
import sys
import csv
import shutil
import random
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation

# Configuração do Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'servicos.settings')

import django
django.setup()

from django.db import connection, transaction
from rotinas_automaticas.models import FundoListadoB3, AnualFcaCiaAbertaValorMobiliario, RegistroExecucao


class CargaB3TradeInformation:
    """Classe para processar arquivos TradeInformationConsolidatedFile da B3"""
    
    def __init__(self, arquivo_especifico=None):
        self.pasta_origem = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'downloadbruto')
        self.pasta_destino = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'processados')
        self.pasta_logs = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'logs')
        self.arquivo_especifico = arquivo_especifico  # Novo parâmetro para arquivo específico
        self.lista_tickers_fii = set()
        self.lista_tickers_acao = set()
        self.arquivos_processados = []
        self.total_linhas_processadas = 0
        self.total_linhas_inseridas = 0
        self.total_linhas_rejeitadas = 0
        self.total_linhas_atualizadas = 0
        self.total_linhas_ignoradas = 0
        self.tickers_nao_carregados = set()
        self.amostras_arquivo = []
        self.cabecalho_arquivo = None
        self.registro_execucao = None
        
        # Criar pasta de logs se não existir
        os.makedirs(self.pasta_logs, exist_ok=True)
    
    def criar_registro_execucao(self, nome_arquivo):
        """Cria registro de execução na tabela"""
        try:
            self.registro_execucao = RegistroExecucao.objects.create(
                job_arquivo_processo=f"carga_b3_TradeInformationConsolidatedFile - {nome_arquivo}",
                tabela_destino="organizesee_ativosprecos",
                status_execucao='EXECUTANDO',
                sistema='B3',
                grupo='DIARIO'
            )
            print(f"   Registro de execução criado - ID: {self.registro_execucao.id}")
        except Exception as e:
            print(f"   ERRO ao criar registro de execução: {e}")
            self.registro_execucao = None
    
    def atualizar_registro_execucao(self, status, **kwargs):
        """Atualiza registro de execução"""
        if not self.registro_execucao:
            return
            
        try:
            self.registro_execucao.status_execucao = status
            
            # Atualizar campos específicos
            for campo, valor in kwargs.items():
                if hasattr(self.registro_execucao, campo):
                    setattr(self.registro_execucao, campo, valor)
            
            # Se for finalização, marcar data/hora
            if status in ['CONCLUIDA', 'ERRO', 'CANCELADO']:
                self.registro_execucao.dia_horario_finalizacao = datetime.now()
            
            self.registro_execucao.save()
            
        except Exception as e:
            print(f"   ERRO ao atualizar registro de execução: {e}")
    
    def gerar_log_estruturado(self, nome_arquivo):
        """Gera log estruturado do processamento"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo_base = os.path.splitext(nome_arquivo)[0]
            nome_log = f"log_{nome_arquivo_base}_{timestamp}.txt"
            caminho_log = os.path.join(self.pasta_logs, nome_log)
            
            with open(caminho_log, 'w', encoding='utf-8') as log_file:
                log_file.write("=" * 80 + "\n")
                log_file.write("LOG DE PROCESSAMENTO - B3 TRADE INFORMATION CONSOLIDATED FILE\n")
                log_file.write("=" * 80 + "\n\n")
                
                # Informações gerais
                log_file.write("INFORMAÇÕES GERAIS\n")
                log_file.write("-" * 40 + "\n")
                log_file.write(f"Arquivo processado: {nome_arquivo}\n")
                log_file.write(f"Data de processamento: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                log_file.write(f"Tabela destino: organizesee_ativosprecos\n")
                log_file.write(f"Sistema: B3\n")
                log_file.write(f"Grupo: Diário\n\n")
                
                # Cabeçalho do arquivo
                if self.cabecalho_arquivo:
                    log_file.write("CABEÇALHO DO ARQUIVO\n")
                    log_file.write("-" * 40 + "\n")
                    for i, campo in enumerate(self.cabecalho_arquivo):
                        log_file.write(f"Coluna {i+1:2d}: {campo}\n")
                    log_file.write("\n")
                
                # Amostras do arquivo (15 linhas randômicas)
                if self.amostras_arquivo:
                    log_file.write("AMOSTRAS DO ARQUIVO (15 LINHAS RANDÔMICAS)\n")
                    log_file.write("-" * 40 + "\n")
                    for i, amostra in enumerate(self.amostras_arquivo[:15], 1):
                        log_file.write(f"Linha {i:2d}: {amostra}\n")
                    log_file.write("\n")
                
                # Estatísticas de processamento
                log_file.write("ESTATÍSTICAS DE PROCESSAMENTO\n")
                log_file.write("-" * 40 + "\n")
                log_file.write(f"Total de linhas do arquivo: {self.total_linhas_processadas:,}\n")
                log_file.write(f"Registros novos inseridos: {self.total_linhas_inseridas:,}\n")
                log_file.write(f"Registros atualizados: {self.total_linhas_atualizadas:,}\n")
                log_file.write(f"Registros rejeitados: {self.total_linhas_rejeitadas:,}\n")
                log_file.write(f"Registros ignorados: {self.total_linhas_ignoradas:,}\n")
                
                if self.total_linhas_processadas > 0:
                    taxa = (self.total_linhas_inseridas / self.total_linhas_processadas) * 100
                    log_file.write(f"Taxa de aproveitamento: {taxa:.1f}%\n")
                log_file.write("\n")
                
                # Tickers não carregados (filtrados por regra final 3, 4 ou 11)
                if self.tickers_nao_carregados:
                    log_file.write("TICKERS NÃO CARREGADOS (REGRA FINAL 3, 4 OU 11)\n")
                    log_file.write("-" * 40 + "\n")
                    log_file.write("Tickers que apareceram no arquivo mas não foram carregados\n")
                    log_file.write("por não estarem nas listas de referência (FII ou Ações):\n\n")
                    
                    # Filtrar apenas tickers que terminam com 3, 4 ou 11
                    tickers_filtrados = [ticker for ticker in self.tickers_nao_carregados 
                                       if ticker.endswith(('3', '4', '11'))]
                    
                    if tickers_filtrados:
                        for ticker in sorted(tickers_filtrados):
                            log_file.write(f"   - {ticker}\n")
                    else:
                        log_file.write("   Nenhum ticker encontrado com terminação 3, 4 ou 11\n")
                    
                    log_file.write(f"\nTotal de tickers não carregados (filtrados): {len(tickers_filtrados)}\n")
                    log_file.write(f"Total de tickers não carregados (geral): {len(self.tickers_nao_carregados)}\n\n")
                
                # Listas de referência
                log_file.write("LISTAS DE REFERÊNCIA\n")
                log_file.write("-" * 40 + "\n")
                log_file.write(f"Tickers FII conhecidos: {len(self.lista_tickers_fii)}\n")
                log_file.write(f"Tickers Ação conhecidos: {len(self.lista_tickers_acao)}\n\n")
                
                log_file.write("=" * 80 + "\n")
                log_file.write("FIM DO LOG\n")
                log_file.write("=" * 80 + "\n")
            
            # Atualizar registro de execução com caminho do log
            if self.registro_execucao:
                self.registro_execucao.arquivo_log = caminho_log
                self.registro_execucao.save()
            
            print(f"   Log estruturado gerado: {nome_log}")
            return caminho_log
            
        except Exception as e:
            print(f"   ERRO ao gerar log estruturado: {e}")
            return None
        
    def carregar_listas_referencia(self):
        """Carrega listas de tickers FII e Ações das tabelas de referência"""
        print("Carregando listas de referencia...")
        
        # Lista de FII
        try:
            fiis = FundoListadoB3.objects.values_list('codigo', flat=True).distinct()
            self.lista_tickers_fii = {fii.strip().upper() for fii in fiis if fii and fii.strip()}
            print(f"FII: {len(self.lista_tickers_fii)} codigos carregados")
        except Exception as e:
            print(f"Erro ao carregar lista FII: {e}")
            self.lista_tickers_fii = set()
        
        # Lista de Ações
        try:
            # Usar SQL direta devido ao mapeamento de campo com maiúscula
            with connection.cursor() as cursor:
                cursor.execute('SELECT DISTINCT "Codigo_Negociacao" FROM rotinas_automaticas_anual_fca_cia_aberta_valor_mobiliario WHERE "Codigo_Negociacao" IS NOT NULL')
                acoes = [row[0] for row in cursor.fetchall()]
            self.lista_tickers_acao = {acao.strip().upper() for acao in acoes if acao and acao.strip()}
            print(f"Acoes: {len(self.lista_tickers_acao)} codigos carregados")
        except Exception as e:
            print(f"Erro ao carregar lista Acoes: {e}")
            self.lista_tickers_acao = set()
        
        print(f"Total de tickers de referencia: {len(self.lista_tickers_fii) + len(self.lista_tickers_acao)}")
    
    def encontrar_arquivos_trade_information(self):
        """Encontra arquivos TradeInformationConsolidatedFile na pasta de origem"""
        arquivos = []
        
        if not os.path.exists(self.pasta_origem):
            print(f"Pasta de origem nao encontrada: {self.pasta_origem}")
            return arquivos
        
        # Se um arquivo específico foi solicitado, processar apenas ele
        if self.arquivo_especifico:
            caminho_especifico = os.path.join(self.pasta_origem, self.arquivo_especifico)
            if os.path.exists(caminho_especifico):
                arquivos.append({
                    'nome': self.arquivo_especifico,
                    'caminho': caminho_especifico,
                    'tamanho_mb': os.path.getsize(caminho_especifico) / (1024 * 1024)
                })
                print(f"Arquivo especifico encontrado: {self.arquivo_especifico}")
            else:
                print(f"Arquivo especifico nao encontrado: {self.arquivo_especifico}")
            return arquivos
        
        # Caso contrário, encontrar todos os arquivos TradeInformationConsolidatedFile
        for arquivo in os.listdir(self.pasta_origem):
            if 'TradeInformationConsolidatedFile' in arquivo and (arquivo.endswith('.txt') or arquivo.endswith('.csv')):
                caminho_completo = os.path.join(self.pasta_origem, arquivo)
                arquivos.append({
                    'nome': arquivo,
                    'caminho': caminho_completo,
                    'tamanho_mb': os.path.getsize(caminho_completo) / (1024 * 1024)
                })
        
        # Ordenar por nome (que geralmente contém a data)
        arquivos.sort(key=lambda x: x['nome'])
        
        print(f"Encontrados {len(arquivos)} arquivos TradeInformationConsolidatedFile:")
        for arq in arquivos:
            print(f"   - {arq['nome']} ({arq['tamanho_mb']:.1f} MB)")
        
        return arquivos
    
    def extrair_data_arquivo(self, nome_arquivo):
        """Extrai data do nome do arquivo"""
        try:
            # Formato esperado: TradeInformationConsolidatedFile_20250908_1.csv
            partes = nome_arquivo.split('_')
            for parte in partes:
                # Procurar por uma parte que tenha 8 dígitos (YYYYMMDD)
                if parte.isdigit() and len(parte) == 8:
                    # Converter YYYYMMDD para YYYY-MM-DD
                    ano = parte[:4]
                    mes = parte[4:6]
                    dia = parte[6:8]
                    data_str = f"{ano}-{mes}-{dia}"
                    return datetime.strptime(data_str, '%Y-%m-%d').date()
            
            # Se não encontrar data no nome, usar data atual
            print(f"   AVISO: Nao foi possivel extrair data do arquivo {nome_arquivo}, usando data atual")
            return datetime.now().date()
        except Exception as e:
            print(f"   ERRO ao extrair data do arquivo {nome_arquivo}: {e}, usando data atual")
            return datetime.now().date()
    
    def classificar_ticker(self, ticker):
        """Classifica ticker como FII, Ação ou Desconhecido"""
        ticker_clean = ticker.strip().upper()
        
        if ticker_clean in self.lista_tickers_fii:
            return 'FII'
        elif ticker_clean in self.lista_tickers_acao:
            return 'Acao'
        else:
            return None  # Desconhecido - será rejeitado
    
    def processar_linha_csv(self, linha):
        """Processa uma linha do CSV e retorna dados formatados para inserção"""
        try:
            # Estrutura do arquivo:
            # RptDt;TckrSymb;ISIN;SgmtNm;MinPric;MaxPric;TradAvrgPric;LastPric;OscnPctg;AdjstdQt;AdjstdQtTax;RefPric;TradQty;FinInstrmQty;NtlFinVol
            # Índices: 0=RptDt, 1=TckrSymb, 2=ISIN, 3=SgmtNm, 4=MinPric, 5=MaxPric, 6=TradAvrgPric, 7=LastPric, 13=FinInstrmQty, 14=NtlFinVol
            
            # Adicionar amostra aleatória (com chance de 0.1%) para o log
            if random.random() < 0.001 and len(self.amostras_arquivo) < 50:
                self.amostras_arquivo.append("|".join(linha))
            
            # Verificar se temos colunas suficientes
            if len(linha) < 6:
                return None
            
            # Extrair e validar data do campo RptDt (coluna 0)
            rpt_dt = linha[0].strip() if len(linha) > 0 else ''
            if not rpt_dt:
                return None
            
            # Converter data do formato YYYY-MM-DD para objeto date
            try:
                data_referencia = datetime.strptime(rpt_dt, '%Y-%m-%d').date()
            except ValueError:
                # Tentar outros formatos possíveis
                try:
                    data_referencia = datetime.strptime(rpt_dt, '%d/%m/%Y').date()
                except ValueError:
                    try:
                        data_referencia = datetime.strptime(rpt_dt, '%Y%m%d').date()
                    except ValueError:
                        print(f"   Formato de data nao reconhecido: {rpt_dt}")
                        return None
            
            # Verificar se MaxPrice (coluna 5) não está vazio
            if len(linha) < 6 or not linha[5].strip():
                return None
            
            # Extrair campos principais
            ticker = linha[1].strip() if len(linha) > 1 else ''  # TckrSymb
            max_price = linha[5].strip() if len(linha) > 5 else ''  # MaxPric
            
            if not ticker or not max_price:
                return None
            
            # Classificar ticker
            tipo = self.classificar_ticker(ticker)
            if not tipo:
                # Adicionar ticker não carregado à lista para o log
                self.tickers_nao_carregados.add(ticker)
                return None  # Rejeitar tickers desconhecidos
            
            # Extrair preços (ajustar baseado na estrutura real do arquivo)
            try:
                # Converter vírgulas em pontos para decimais
                min_price_str = linha[4].strip().replace(',', '.') if len(linha) > 4 and linha[4].strip() else None
                max_price_str = linha[5].strip().replace(',', '.') if len(linha) > 5 and linha[5].strip() else None
                avg_price_str = linha[6].strip().replace(',', '.') if len(linha) > 6 and linha[6].strip() else None
                last_price_str = linha[7].strip().replace(',', '.') if len(linha) > 7 and linha[7].strip() else None
                volume_str = linha[14].strip().replace(',', '.') if len(linha) > 14 and linha[14].strip() else None
                
                # Converter para Decimal
                low_price = Decimal(min_price_str) if min_price_str else None
                high_price = Decimal(max_price_str) if max_price_str else None
                close_price = Decimal(last_price_str) if last_price_str else None  # LastPric como close
                open_price = close_price  # Usar close como open (arquivo não tem open específico)
                volume = Decimal(volume_str) if volume_str else None
                
            except (InvalidOperation, ValueError, IndexError):
                return None
            
            return {
                'tipo': tipo,
                'ticker': ticker.upper(),
                'open': open_price,
                'high': high_price,
                'low': low_price,
                'close': close_price,
                'volume': volume,
                'data': data_referencia,  # Usar data extraída do RptDt
                'fonte': 'B3'
            }
            
        except Exception as e:
            print(f"Erro ao processar linha: {e}")
            return None
    
    def inserir_dados_bulk(self, dados_batch):
        """Insere dados em lote na tabela organizesee_ativosprecos"""
        if not dados_batch:
            return 0
        
        try:
            with connection.cursor() as cursor:
                # SQL de inserção
                sql = """
                INSERT INTO organizesee_ativosprecos 
                (tipo, ticker, "open", high, low, "close", volume, data, fonte)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                # Preparar dados para inserção
                valores = []
                for item in dados_batch:
                    valores.append((
                        item['tipo'],
                        item['ticker'],
                        item['open'],
                        item['high'],
                        item['low'],
                        item['close'],
                        item['volume'],
                        item['data'],
                        item['fonte']
                    ))
                
                # Executar inserção em lote
                cursor.executemany(sql, valores)
                return len(valores)
                
        except Exception as e:
            print(f"Erro na insercao em lote: {e}")
            return 0
    
    def processar_arquivo(self, info_arquivo):
        """Processa um arquivo TradeInformationConsolidatedFile"""
        nome_arquivo = info_arquivo['nome']
        caminho_arquivo = info_arquivo['caminho']
        
        print(f"\nProcessando: {nome_arquivo}")
        print(f"   Tamanho: {info_arquivo['tamanho_mb']:.1f} MB")
        print(f"   Data sera extraida do campo RptDt de cada linha")
        
        # Criar registro de execução
        self.criar_registro_execucao(nome_arquivo)
        
        # Resetar contadores para este arquivo
        self.tickers_nao_carregados.clear()
        self.amostras_arquivo.clear()
        self.cabecalho_arquivo = None
        
        linhas_processadas = 0
        linhas_inseridas = 0
        linhas_rejeitadas = 0
        batch_size = 1000  # Processar em lotes de 1000
        dados_batch = []
        data_dos_dados = None  # Para capturar a data real dos dados
        
        try:
            with open(caminho_arquivo, 'r', encoding='utf-8', errors='ignore') as arquivo:
                # Usar csv.reader para melhor performance
                reader = csv.reader(arquivo, delimiter=';')
                
                # Pular cabeçalho se existir
                try:
                    primeira_linha = next(reader)
                    
                    # Capturar cabeçalho para o log
                    if not self.eh_linha_dados(primeira_linha):
                        print("   Cabecalho detectado e capturado para log")
                        self.cabecalho_arquivo = primeira_linha
                    else:
                        # Se primeira linha é dados, processar ela
                        dados = self.processar_linha_csv(primeira_linha)
                        if dados:
                            dados_batch.append(dados)
                            if data_dos_dados is None:
                                data_dos_dados = dados['data']  # Capturar primeira data válida
                        linhas_processadas += 1
                except StopIteration:
                    print("   Arquivo vazio")
                    self.atualizar_registro_execucao('ERRO', erro_detalhes="Arquivo vazio")
                    return
                
                # Processar linhas restantes
                for linha in reader:
                    linhas_processadas += 1
                    
                    if linhas_processadas % 10000 == 0:
                        print(f"   Processadas: {linhas_processadas:,} linhas")
                    
                    dados = self.processar_linha_csv(linha)
                    
                    if dados:
                        dados_batch.append(dados)
                        if data_dos_dados is None:
                            data_dos_dados = dados['data']  # Capturar primeira data válida
                        
                        # Inserir em lote quando atingir batch_size
                        if len(dados_batch) >= batch_size:
                            with transaction.atomic():
                                inseridos = self.inserir_dados_bulk(dados_batch)
                                linhas_inseridas += inseridos
                            dados_batch = []
                    else:
                        linhas_rejeitadas += 1
                
                # Inserir último lote
                if dados_batch:
                    with transaction.atomic():
                        inseridos = self.inserir_dados_bulk(dados_batch)
                        linhas_inseridas += inseridos
        
        except Exception as e:
            print(f"Erro ao processar arquivo {nome_arquivo}: {e}")
            self.atualizar_registro_execucao('ERRO', erro_detalhes=str(e))
            return
        
        # Estatísticas do arquivo
        print(f"   Processamento concluido:")
        print(f"   Linhas processadas: {linhas_processadas:,}")
        print(f"   Linhas inseridas: {linhas_inseridas:,}")
        print(f"   Linhas rejeitadas: {linhas_rejeitadas:,}")
        print(f"   Taxa de aproveitamento: {(linhas_inseridas/linhas_processadas*100):.1f}%")
        if data_dos_dados:
            print(f"   Data dos dados: {data_dos_dados}")
        
        # Atualizar totais da classe
        self.total_linhas_processadas += linhas_processadas
        self.total_linhas_inseridas += linhas_inseridas
        self.total_linhas_rejeitadas += linhas_rejeitadas
        
        # Gerar log estruturado
        caminho_log = self.gerar_log_estruturado(nome_arquivo)
        
        # Atualizar registro de execução com dados finais
        self.atualizar_registro_execucao(
            'CONCLUIDA',
            registros_totais_novos=linhas_inseridas,
            quantidade_linhas_arquivo=linhas_processadas,
            registros_totais_arquivo=linhas_processadas,
            registros_totais_atualizados=0,  # Este processo só insere
            registros_totais_ignorados=linhas_rejeitadas,
            observacoes=f"Taxa de aproveitamento: {(linhas_inseridas/linhas_processadas*100):.1f}%. "
                       f"Tickers não carregados: {len(self.tickers_nao_carregados)}"
        )
        
        # Mover arquivo para pasta processados usando a data real dos dados
        self.mover_arquivo_processado(info_arquivo, data_dos_dados)
    
    def eh_linha_dados(self, linha):
        """Verifica se a linha contém dados (não é cabeçalho)"""
        if not linha or len(linha) < 2:
            return False
        
        # Se o segundo campo (TckrSymb) contém apenas letras/números, provavelmente é dados
        ticker = linha[1].strip() if len(linha) > 1 else ''
        return bool(ticker and ticker.replace('-', '').replace('.', '').isalnum())
    
    def mover_arquivo_processado(self, info_arquivo, data_dos_dados=None):
        """Move arquivo processado para pasta processados com novo nome"""
        try:
            nome_original = info_arquivo['nome']
            caminho_original = info_arquivo['caminho']
            
            # Usar data dos dados se disponível, senão usar data/hora atual
            if data_dos_dados:
                data_str = data_dos_dados.strftime('%d%m%Y')
                nome_processado = f"TradeInformationConsolidatedFile-{data_str}.carregado"
            else:
                # Fallback para data/hora atual se não conseguir extrair data dos dados
                data_atual = datetime.now()
                timestamp = data_atual.strftime('%d%m%Y_%H%M%S')
                nome_processado = f"TradeInformationConsolidatedFile-{timestamp}.carregado"
            
            caminho_processado = os.path.join(self.pasta_destino, nome_processado)
            
            # Garantir que pasta destino existe
            os.makedirs(self.pasta_destino, exist_ok=True)
            
            # Mover arquivo
            shutil.move(caminho_original, caminho_processado)
            
            print(f"   Arquivo movido para: {nome_processado}")
            self.arquivos_processados.append(nome_processado)
            
        except Exception as e:
            print(f"Erro ao mover arquivo {info_arquivo['nome']}: {e}")
    
    def executar_carga(self):
        """Executa o processo completo de carga"""
        print("Iniciando Carga B3 TradeInformationConsolidatedFile")
        print("=" * 60)
        
        inicio = datetime.now()
        
        # 1. Carregar listas de referência
        self.carregar_listas_referencia()
        
        if not self.lista_tickers_fii and not self.lista_tickers_acao:
            print("Nenhuma lista de referencia carregada. Abortando processo.")
            return
        
        # 2. Encontrar arquivos para processar
        arquivos = self.encontrar_arquivos_trade_information()
        
        if not arquivos:
            print("Nenhum arquivo TradeInformationConsolidatedFile encontrado.")
            return
        
        # 3. Processar cada arquivo
        print(f"\nProcessando {len(arquivos)} arquivo(s)...")
        
        for info_arquivo in arquivos:
            self.processar_arquivo(info_arquivo)
        
        # 4. Estatísticas finais
        fim = datetime.now()
        duracao = fim - inicio
        
        print("\n" + "=" * 60)
        print("RESUMO DA CARGA")
        print("=" * 60)
        print(f"Tempo de execucao: {duracao}")
        print(f"Arquivos processados: {len(self.arquivos_processados)}")
        print(f"Total de linhas processadas: {self.total_linhas_processadas:,}")
        print(f"Total de linhas inseridas: {self.total_linhas_inseridas:,}")
        print(f"Total de linhas rejeitadas: {self.total_linhas_rejeitadas:,}")
        
        if self.total_linhas_processadas > 0:
            taxa_aproveitamento = (self.total_linhas_inseridas / self.total_linhas_processadas) * 100
            print(f"Taxa de aproveitamento geral: {taxa_aproveitamento:.1f}%")
        
        print(f"Tickers FII conhecidos: {len(self.lista_tickers_fii)}")
        print(f"Tickers Acao conhecidos: {len(self.lista_tickers_acao)}")
        print(f"Tickers nao carregados (total): {len(self.tickers_nao_carregados)}")
        
        # Contar tickers não carregados filtrados (terminados em 3, 4 ou 11)
        tickers_filtrados = [t for t in self.tickers_nao_carregados if t.endswith(('3', '4', '11'))]
        print(f"Tickers nao carregados (filtrados 3,4,11): {len(tickers_filtrados)}")
        
        if self.arquivos_processados:
            print("\nArquivos movidos para pasta processados:")
            for arquivo in self.arquivos_processados:
                print(f"   - {arquivo}")
        
        print(f"\nLogs estruturados gerados na pasta: {self.pasta_logs}")
        print(f"Registros de execucao salvos na tabela: rotinas_automaticas_registro_execucao")
        print("\nCarga concluida com sucesso!")


def main():
    """Função principal"""
    try:
        # Verificar se foi passado um arquivo específico como argumento
        arquivo_especifico = None
        if len(sys.argv) > 1:
            arquivo_especifico = sys.argv[1]
            print(f"Processando arquivo especifico: {arquivo_especifico}")
        
        carga = CargaB3TradeInformation(arquivo_especifico)
        carga.executar_carga()
    except KeyboardInterrupt:
        print("\nProcesso interrompido pelo usuario")
    except Exception as e:
        print(f"\nErro fatal: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
