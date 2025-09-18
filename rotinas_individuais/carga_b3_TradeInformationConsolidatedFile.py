#!/usr/bin/env python
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
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation

# Configuração do Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'servicos.settings')

import django
django.setup()

from django.db import connection, transaction
from rotinas_automaticas.models import FundoListadoB3, AnualFcaCiaAbertaValorMobiliario


class CargaB3TradeInformation:
    """Classe para processar arquivos TradeInformationConsolidatedFile da B3"""
    
    def __init__(self):
        self.pasta_origem = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'downloadbruto')
        self.pasta_destino = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'processados')
        self.lista_tickers_fii = set()
        self.lista_tickers_acao = set()
        self.arquivos_processados = []
        self.total_linhas_processadas = 0
        self.total_linhas_inseridas = 0
        self.total_linhas_rejeitadas = 0
        
    def carregar_listas_referencia(self):
        """Carrega listas de tickers FII e Ações das tabelas de referência"""
        print("Carregando listas de referência...")
        
        # Lista de FII
        try:
            fiis = FundoListadoB3.objects.values_list('codigo', flat=True).distinct()
            self.lista_tickers_fii = {fii.strip().upper() for fii in fiis if fii and fii.strip()}
            print(f"FII: {len(self.lista_tickers_fii)} códigos carregados")
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
            print(f"Ações: {len(self.lista_tickers_acao)} códigos carregados")
        except Exception as e:
            print(f"Erro ao carregar lista Ações: {e}")
            self.lista_tickers_acao = set()
        
        print(f"Total de tickers de referência: {len(self.lista_tickers_fii) + len(self.lista_tickers_acao)}")
    
    def encontrar_arquivos_trade_information(self):
        """Encontra arquivos TradeInformationConsolidatedFile na pasta de origem"""
        arquivos = []
        
        if not os.path.exists(self.pasta_origem):
            print(f"Pasta de origem não encontrada: {self.pasta_origem}")
            return arquivos
        
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
            # Formato esperado: TradeInformationConsolidatedFile_2025-09-10.txt
            for parte in nome_arquivo.split('_'):
                if '-' in parte and len(parte) >= 10:
                    data_str = parte[:10]  # YYYY-MM-DD
                    return datetime.strptime(data_str, '%Y-%m-%d').date()
            
            # Se não encontrar data no nome, usar data atual
            return datetime.now().date()
        except:
            return datetime.now().date()
    
    def classificar_ticker(self, ticker):
        """Classifica ticker como FII, Ação ou Desconhecido"""
        ticker_clean = ticker.strip().upper()
        
        if ticker_clean in self.lista_tickers_fii:
            return 'FII'
        elif ticker_clean in self.lista_tickers_acao:
            return 'Ação'
        else:
            return None  # Desconhecido - será rejeitado
    
    def processar_linha_csv(self, linha, data_referencia):
        """Processa uma linha do CSV e retorna dados formatados para inserção"""
        try:
            # Estrutura do arquivo:
            # RptDt;TckrSymb;ISIN;SgmtNm;MinPric;MaxPric;TradAvrgPric;LastPric;OscnPctg;AdjstdQt;AdjstdQtTax;RefPric;TradQty;FinInstrmQty;NtlFinVol
            # Índices: 0=RptDt, 1=TckrSymb, 2=ISIN, 3=SgmtNm, 4=MinPric, 5=MaxPric, 6=TradAvrgPric, 7=LastPric, 13=FinInstrmQty, 14=NtlFinVol
            
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
                'data': data_referencia,
                'fonte': 'B3'
            }
            
        except Exception as e:
            print(f"❌ Erro ao processar linha: {e}")
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
            print(f"❌ Erro na inserção em lote: {e}")
            return 0
    
    def processar_arquivo(self, info_arquivo):
        """Processa um arquivo TradeInformationConsolidatedFile"""
        nome_arquivo = info_arquivo['nome']
        caminho_arquivo = info_arquivo['caminho']
        
        print(f"\n📄 Processando: {nome_arquivo}")
        print(f"   Tamanho: {info_arquivo['tamanho_mb']:.1f} MB")
        
        # Extrair data do arquivo
        data_referencia = self.extrair_data_arquivo(nome_arquivo)
        print(f"   Data de referência: {data_referencia}")
        
        linhas_processadas = 0
        linhas_inseridas = 0
        linhas_rejeitadas = 0
        batch_size = 1000  # Processar em lotes de 1000
        dados_batch = []
        
        try:
            with open(caminho_arquivo, 'r', encoding='utf-8', errors='ignore') as arquivo:
                # Usar csv.reader para melhor performance
                reader = csv.reader(arquivo, delimiter=';')
                
                # Pular cabeçalho se existir
                try:
                    primeira_linha = next(reader)
                    if not self.eh_linha_dados(primeira_linha):
                        print("   📋 Cabeçalho detectado e ignorado")
                    else:
                        # Se primeira linha é dados, processar ela
                        dados = self.processar_linha_csv(primeira_linha, data_referencia)
                        if dados:
                            dados_batch.append(dados)
                        linhas_processadas += 1
                except StopIteration:
                    print("   ❌ Arquivo vazio")
                    return
                
                # Processar linhas restantes
                for linha in reader:
                    linhas_processadas += 1
                    
                    if linhas_processadas % 10000 == 0:
                        print(f"   📊 Processadas: {linhas_processadas:,} linhas")
                    
                    dados = self.processar_linha_csv(linha, data_referencia)
                    
                    if dados:
                        dados_batch.append(dados)
                        
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
            print(f"❌ Erro ao processar arquivo {nome_arquivo}: {e}")
            return
        
        # Estatísticas do arquivo
        print(f"   ✅ Processamento concluído:")
        print(f"   📊 Linhas processadas: {linhas_processadas:,}")
        print(f"   ✅ Linhas inseridas: {linhas_inseridas:,}")
        print(f"   ❌ Linhas rejeitadas: {linhas_rejeitadas:,}")
        print(f"   📈 Taxa de aproveitamento: {(linhas_inseridas/linhas_processadas*100):.1f}%")
        
        # Atualizar totais
        self.total_linhas_processadas += linhas_processadas
        self.total_linhas_inseridas += linhas_inseridas
        self.total_linhas_rejeitadas += linhas_rejeitadas
        
        # Mover arquivo para pasta processados
        self.mover_arquivo_processado(info_arquivo, data_referencia)
    
    def eh_linha_dados(self, linha):
        """Verifica se a linha contém dados (não é cabeçalho)"""
        if not linha or len(linha) < 2:
            return False
        
        # Se o segundo campo (TckrSymb) contém apenas letras/números, provavelmente é dados
        ticker = linha[1].strip() if len(linha) > 1 else ''
        return bool(ticker and ticker.replace('-', '').replace('.', '').isalnum())
    
    def mover_arquivo_processado(self, info_arquivo, data_referencia):
        """Move arquivo processado para pasta processados com novo nome"""
        try:
            nome_original = info_arquivo['nome']
            caminho_original = info_arquivo['caminho']
            
            # Criar nome do arquivo processado
            data_str = data_referencia.strftime('%d%m%Y')
            nome_processado = f"TradeInformationConsolidatedFile-{data_str}.carregado"
            caminho_processado = os.path.join(self.pasta_destino, nome_processado)
            
            # Garantir que pasta destino existe
            os.makedirs(self.pasta_destino, exist_ok=True)
            
            # Mover arquivo
            shutil.move(caminho_original, caminho_processado)
            
            print(f"   📦 Arquivo movido para: {nome_processado}")
            self.arquivos_processados.append(nome_processado)
            
        except Exception as e:
            print(f"❌ Erro ao mover arquivo {info_arquivo['nome']}: {e}")
    
    def executar_carga(self):
        """Executa o processo completo de carga"""
        print("🚀 Iniciando Carga B3 TradeInformationConsolidatedFile")
        print("=" * 60)
        
        inicio = datetime.now()
        
        # 1. Carregar listas de referência
        self.carregar_listas_referencia()
        
        if not self.lista_tickers_fii and not self.lista_tickers_acao:
            print("❌ Nenhuma lista de referência carregada. Abortando processo.")
            return
        
        # 2. Encontrar arquivos para processar
        arquivos = self.encontrar_arquivos_trade_information()
        
        if not arquivos:
            print("❌ Nenhum arquivo TradeInformationConsolidatedFile encontrado.")
            return
        
        # 3. Processar cada arquivo
        print(f"\n🔄 Processando {len(arquivos)} arquivo(s)...")
        
        for info_arquivo in arquivos:
            self.processar_arquivo(info_arquivo)
        
        # 4. Estatísticas finais
        fim = datetime.now()
        duracao = fim - inicio
        
        print("\n" + "=" * 60)
        print("📊 RESUMO DA CARGA")
        print("=" * 60)
        print(f"⏱️  Tempo de execução: {duracao}")
        print(f"📁 Arquivos processados: {len(self.arquivos_processados)}")
        print(f"📊 Total de linhas processadas: {self.total_linhas_processadas:,}")
        print(f"✅ Total de linhas inseridas: {self.total_linhas_inseridas:,}")
        print(f"❌ Total de linhas rejeitadas: {self.total_linhas_rejeitadas:,}")
        
        if self.total_linhas_processadas > 0:
            taxa_aproveitamento = (self.total_linhas_inseridas / self.total_linhas_processadas) * 100
            print(f"📈 Taxa de aproveitamento geral: {taxa_aproveitamento:.1f}%")
        
        print(f"🎯 Tickers FII conhecidos: {len(self.lista_tickers_fii)}")
        print(f"🎯 Tickers Ação conhecidos: {len(self.lista_tickers_acao)}")
        
        if self.arquivos_processados:
            print("\n📦 Arquivos movidos para pasta processados:")
            for arquivo in self.arquivos_processados:
                print(f"   - {arquivo}")
        
        print("\n✅ Carga concluída com sucesso!")


def main():
    """Função principal"""
    try:
        carga = CargaB3TradeInformation()
        carga.executar_carga()
    except KeyboardInterrupt:
        print("\n⚠️  Processo interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
