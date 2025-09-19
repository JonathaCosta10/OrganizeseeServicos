import os
import requests
import zipfile
from datetime import datetime, timedelta
from django.shortcuts import render
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

def job_download_arquivos_CVM(pasta_destino='static/downloadbruto'):
    """Job para download de arquivos da CVM"""
    urls = [
        # Ações
        "https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/FCA/DADOS/fca_cia_aberta_2025.zip",

        # Fundos Imobiliários
        "https://dados.cvm.gov.br/dados/FII/DOC/INF_ANUAL/DADOS/inf_anual_fii_2024.zip",
        "https://dados.cvm.gov.br/dados/FII/DOC/INF_MENSAL/DADOS/inf_mensal_fii_2025.zip"
    ]

    def baixar_e_extrair(url):
        nome_arquivo_zip = os.path.join(pasta_destino, url.split('/')[-1])

        print(f"\n[DOWNLOAD] Baixando: {url}")
        resposta = requests.get(url)
        with open(nome_arquivo_zip, "wb") as f:
            f.write(resposta.content)
        print(f"[OK] Salvo em: {nome_arquivo_zip}")

        print("[EXTRACT] Extraindo arquivos...")
        with zipfile.ZipFile(nome_arquivo_zip, "r") as zip_ref:
            zip_ref.extractall(pasta_destino)
        print(f"[OK] Extraído em: {pasta_destino}")

        if os.path.exists(nome_arquivo_zip):
            os.remove(nome_arquivo_zip)
            print(f"🗑️ Zip removido: {nome_arquivo_zip}")

    # Cria a pasta se necessário
    os.makedirs(pasta_destino, exist_ok=True)

    # Processa todas as URLs
    urls_processadas = 0
    for url in urls:
        try:
            baixar_e_extrair(url)
            urls_processadas += 1
        except Exception as e:
            print(f"[ERROR] Erro ao processar {url}: {e}")

    # Lista os arquivos extraídos
    print("\n[FILE] Arquivos extraídos na pasta:")
    arquivos_extraidos = []
    for arq in os.listdir(pasta_destino):
        print(" -", arq)
        arquivos_extraidos.append(arq)

    # Retornar resultado da execução
    print("\n🎉 Download e processamento de arquivos CVM concluído!")
    return {
        'status': 'sucesso',
        'mensagem': 'Download e processamento de arquivos CVM concluído',
        'pasta_destino': pasta_destino,
        'urls_processadas': urls_processadas,
        'arquivos_extraidos': arquivos_extraidos
    }

def job_baixar_arquivos_b3(n_dias=3):
    """
    Job para fazer download dos arquivos da B3
    """
    print(f"[SEARCH] Iniciando job_baixar_arquivos_b3 para {n_dias} dias úteis")
    
    try:
        # Criar diretório para downloads na pasta static
        DOWNLOAD_DIR = os.path.join(settings.BASE_DIR, 'static', 'downloadbruto')
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        
        # Headers para simular um navegador
        HEADERS = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
        }
        
        # Lista de arquivos disponíveis para download
        ARQUIVOS = [
            "InstrumentsConsolidatedFile",           # Instrumentos (BVBG.028.02)
            "TradeInformationConsolidatedFile",      # Boletim de Negociação (BVBG.086.01)
            "TradeInformationConsolidatedAfterHoursFile"  # Pós-mercado
        ]
        
        # Gerar lista dos últimos n dias úteis
        datas = get_ultimos_dias_uteis(n_dias)
        
        total_downloads = 0
        downloads_sucesso = 0
        arquivos_baixados = []
        
        # Baixar arquivos para cada data
        for data in datas:
            print(f"\n📅 Processando data: {data}")
            for arquivo in ARQUIVOS:
                print(f"⬇️ Baixando {arquivo} para {data}...")
                total_downloads += 1
                
                resultado_download = baixar_arquivo_b3(arquivo, data, DOWNLOAD_DIR, HEADERS)
                if resultado_download['sucesso']:
                    downloads_sucesso += 1
                    arquivos_baixados.append(resultado_download['nome_arquivo'])
        
        resultado = {
            'status': 'sucesso',
            'mensagem': f"Downloads B3 concluídos: {downloads_sucesso}/{total_downloads}",
            'pasta_destino': DOWNLOAD_DIR,
            'dias_processados': len(datas),
            'datas': datas,
            'downloads_sucesso': downloads_sucesso,
            'total_downloads': total_downloads,
            'arquivos_baixados': arquivos_baixados
        }
        
        print(f"[OK] Downloads concluídos: {downloads_sucesso}/{total_downloads} arquivos salvos em {DOWNLOAD_DIR}")
        return resultado
        
    except Exception as e:
        erro = {
            'status': 'erro',
            'mensagem': f"Erro ao processar downloads B3: {str(e)}"
        }
        print(f"[ERROR] {erro['mensagem']}")
        return erro

def get_ultimos_dias_uteis(n=3):
    """Gera lista dos últimos n dias úteis (excluindo sábado e domingo), incluindo D0 (hoje) se for dia útil"""
    dias_uteis = []
    hoje = datetime.now()
    
    # Incluir D0 (hoje) se for dia útil
    if hoje.weekday() < 5:  # 0=segunda, 1=terça, 2=quarta, 3=quinta, 4=sexta
        dias_uteis.append(hoje.strftime("%Y-%m-%d"))
    
    delta = 1
    while len(dias_uteis) < n:
        dia = hoje - timedelta(days=delta)
        if dia.weekday() < 5:  # 0=segunda, 1=terça, 2=quarta, 3=quinta, 4=sexta
            dias_uteis.append(dia.strftime("%Y-%m-%d"))
        delta += 1
    return dias_uteis[::-1]  # do mais antigo para o mais recente

def baixar_arquivo_b3(nome_arquivo, data, download_dir, headers):
    """Realiza o download em duas etapas: obter token e depois o arquivo"""
    try:
        # Passo 1: Obter token
        print(f"🔑 Solicitando token para: {nome_arquivo}")
        url_token = f"https://arquivos.b3.com.br/api/download/requestname?fileName={nome_arquivo}&date={data}"
        
        response = requests.get(url_token, headers=headers, timeout=30)
        
        if response.status_code != 200:
            print(f"[ERROR] Erro ao obter token: {response.status_code}")
            return {'sucesso': False, 'erro': f'Erro ao obter token: {response.status_code}'}
        
        dados = response.json()
        token = dados.get("token")
        
        if not token:
            print(f"[ERROR] Token não encontrado na resposta")
            return {'sucesso': False, 'erro': 'Token não encontrado na resposta'}
        
        nome_completo = f"{dados['file']['name']}{dados['file']['extension']}"
        print(f"[OK] Token obtido para: {nome_completo}")
        
        # Passo 2: Download do arquivo
        url_download = f"https://arquivos.b3.com.br/api/download/?token={token}"
        
        arquivo_response = requests.get(url_download, headers=headers, timeout=60)
        
        if arquivo_response.status_code != 200:
            print(f"[ERROR] Erro ao baixar arquivo: {arquivo_response.status_code}")
            return {'sucesso': False, 'erro': f'Erro ao baixar arquivo: {arquivo_response.status_code}'}
        
        # Salvar arquivo
        caminho_arquivo = os.path.join(download_dir, nome_completo)
        with open(caminho_arquivo, "wb") as arquivo:
            arquivo.write(arquivo_response.content)
        
        print(f"[OK] Arquivo salvo: {nome_completo}")
        return {'sucesso': True, 'nome_arquivo': nome_completo}
        
    except Exception as e:
        print(f"[ERROR] Erro no download de {nome_arquivo}: {str(e)}")
        return {'sucesso': False, 'erro': str(e)}

@api_view(['GET', 'POST'])
def download_cvm(request):
    """Endpoint para download CVM"""
    try:
        # Executa o job de download
        resultado = job_download_arquivos_CVM()
        
        return Response({
            'message': 'Download CVM executado com sucesso',
            'resultado': resultado
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({
            'error': f'Erro ao executar download CVM: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET', 'POST'])
def download_b3(request, dias=None):
    """Endpoint para download B3 com parâmetro de dias úteis"""
    try:
        # Obter parâmetro de dias úteis
        if dias is not None:
            # Parâmetro veio da URL
            dias_param = dias
        elif request.method == 'POST':
            # Parâmetro no body da requisição POST
            dias_param = request.data.get('dias', 3)  # Padrão 3 dias (D0, D-1, D-2)
        else:
            # Parâmetro como query parameter no GET
            dias_param = request.GET.get('dias', 3)  # Padrão 3 dias
        
        # Validar parâmetro
        try:
            dias_param = int(dias_param)
            if dias_param < 1 or dias_param > 10:  # Limitar entre 1 e 10 dias
                dias_param = 3 if dias is None else dias  # Padrão 3 dias
        except (ValueError, TypeError):
            dias_param = 3  # Padrão 3 dias
        
        # Executar o job de download
        resultado = job_baixar_arquivos_b3(dias_param)
        
        return Response({
            'message': f'Download B3 executado para {dias_param} dias úteis',
            'dias_solicitados': dias_param,
            'resultado': resultado
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({
            'error': f'Erro ao executar download B3: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def listar_arquivos_static():
    """Função para listar arquivos na pasta static"""
    try:
        # Caminho da pasta static
        STATIC_DIR = os.path.join(settings.BASE_DIR, 'static')
        
        if not os.path.exists(STATIC_DIR):
            return {
                'status': 'erro',
                'mensagem': 'Pasta static não encontrada',
                'pasta_static': STATIC_DIR,
                'pastas': [],
                'arquivos': []
            }
        
        resultado = {
            'status': 'sucesso',
            'mensagem': 'Listagem de arquivos da pasta static',
            'pasta_static': STATIC_DIR,
            'pastas': [],
            'arquivos': []
        }
        
        # Listar conteúdo da pasta static
        for item in os.listdir(STATIC_DIR):
            item_path = os.path.join(STATIC_DIR, item)
            
            if os.path.isdir(item_path):
                # É uma pasta
                pasta_info = {
                    'nome': item,
                    'tipo': 'pasta',
                    'caminho': item_path,
                    'arquivos': []
                }
                
                # Listar arquivos dentro da pasta
                try:
                    for arquivo in os.listdir(item_path):
                        arquivo_path = os.path.join(item_path, arquivo)
                        if os.path.isfile(arquivo_path):
                            # Obter informações do arquivo
                            stat_info = os.stat(arquivo_path)
                            data_modificacao = datetime.fromtimestamp(stat_info.st_mtime)
                            tamanho_mb = stat_info.st_size / (1024 * 1024)  # Converter para MB
                            
                            arquivo_info = {
                                'nome': arquivo,
                                'tamanho_mb': round(tamanho_mb, 2),
                                'data_modificacao': data_modificacao.strftime('%Y-%m-%d %H:%M:%S'),
                                'caminho_completo': arquivo_path
                            }
                            pasta_info['arquivos'].append(arquivo_info)
                except Exception as e:
                    pasta_info['erro'] = f"Erro ao listar arquivos da pasta {item}: {str(e)}"
                
                resultado['pastas'].append(pasta_info)
            
            elif os.path.isfile(item_path):
                # É um arquivo na raiz da pasta static
                stat_info = os.stat(item_path)
                data_modificacao = datetime.fromtimestamp(stat_info.st_mtime)
                tamanho_mb = stat_info.st_size / (1024 * 1024)
                
                arquivo_info = {
                    'nome': item,
                    'tamanho_mb': round(tamanho_mb, 2),
                    'data_modificacao': data_modificacao.strftime('%Y-%m-%d %H:%M:%S'),
                    'caminho_completo': item_path
                }
                resultado['arquivos'].append(arquivo_info)
        
        # Estatísticas gerais
        total_pastas = len(resultado['pastas'])
        total_arquivos_raiz = len(resultado['arquivos'])
        total_arquivos_subpastas = sum(len(pasta['arquivos']) for pasta in resultado['pastas'])
        
        resultado['estatisticas'] = {
            'total_pastas': total_pastas,
            'total_arquivos_raiz': total_arquivos_raiz,
            'total_arquivos_subpastas': total_arquivos_subpastas,
            'total_arquivos_geral': total_arquivos_raiz + total_arquivos_subpastas
        }
        
        print(f"[OK] Listagem concluída: {total_pastas} pastas, {total_arquivos_raiz + total_arquivos_subpastas} arquivos")
        return resultado
        
    except Exception as e:
        erro = {
            'status': 'erro',
            'mensagem': f'Erro ao listar arquivos da pasta static: {str(e)}'
        }
        print(f"[ERROR] {erro['mensagem']}")
        return erro


def deletar_todos_arquivos_static():
    """Função para deletar todos os arquivos da pasta static"""
    try:
        # Caminho da pasta static
        STATIC_DIR = os.path.join(settings.BASE_DIR, 'static')
        
        if not os.path.exists(STATIC_DIR):
            return {
                'status': 'erro',
                'mensagem': 'Pasta static não encontrada',
                'pasta_static': STATIC_DIR,
                'arquivos_deletados': 0,
                'pastas_processadas': 0
            }
        
        resultado = {
            'status': 'sucesso',
            'mensagem': 'Deleção de arquivos da pasta static executada',
            'pasta_static': STATIC_DIR,
            'arquivos_deletados': 0,
            'pastas_processadas': 0,
            'detalhes': []
        }
        
        # Processar conteúdo da pasta static
        for item in os.listdir(STATIC_DIR):
            item_path = os.path.join(STATIC_DIR, item)
            
            if os.path.isdir(item_path):
                # É uma pasta - deletar todos os arquivos dentro dela
                pasta_info = {
                    'nome_pasta': item,
                    'arquivos_deletados': 0,
                    'arquivos_erro': []
                }
                
                try:
                    for arquivo in os.listdir(item_path):
                        arquivo_path = os.path.join(item_path, arquivo)
                        if os.path.isfile(arquivo_path):
                            try:
                                os.remove(arquivo_path)
                                pasta_info['arquivos_deletados'] += 1
                                resultado['arquivos_deletados'] += 1
                                print(f"[DELETE] Arquivo deletado: {arquivo_path}")
                            except Exception as e:
                                erro_msg = f"Erro ao deletar {arquivo}: {str(e)}"
                                pasta_info['arquivos_erro'].append(erro_msg)
                                print(f"[ERROR] {erro_msg}")
                    
                    resultado['pastas_processadas'] += 1
                    resultado['detalhes'].append(pasta_info)
                    
                except Exception as e:
                    pasta_info['erro_pasta'] = f"Erro ao acessar pasta {item}: {str(e)}"
                    resultado['detalhes'].append(pasta_info)
                    print(f"[ERROR] Erro ao processar pasta {item}: {str(e)}")
            
            elif os.path.isfile(item_path):
                # É um arquivo na raiz da pasta static
                try:
                    os.remove(item_path)
                    resultado['arquivos_deletados'] += 1
                    print(f"[DELETE] Arquivo deletado (raiz): {item_path}")
                except Exception as e:
                    erro_msg = f"Erro ao deletar arquivo da raiz {item}: {str(e)}"
                    resultado['detalhes'].append({'arquivo_raiz': item, 'erro': erro_msg})
                    print(f"[ERROR] {erro_msg}")
        
        print(f"[OK] Deleção concluída: {resultado['arquivos_deletados']} arquivos deletados de {resultado['pastas_processadas']} pastas")
        return resultado
        
    except Exception as e:
        erro = {
            'status': 'erro',
            'mensagem': f'Erro ao deletar arquivos da pasta static: {str(e)}'
        }
        print(f"[ERROR] {erro['mensagem']}")
        return erro


def executar_carga_arquivo(nome_arquivo):
    """Executa carga de arquivo específico baseado no tipo"""
    try:
        import subprocess
        import sys
        
        # Caminho da pasta static
        STATIC_DIR = os.path.join(settings.BASE_DIR, 'static', 'downloadbruto')
        caminho_arquivo = os.path.join(STATIC_DIR, nome_arquivo)
        
        if not os.path.exists(caminho_arquivo):
            return {
                'status': 'erro',
                'mensagem': f'Arquivo não encontrado: {nome_arquivo}',
                'arquivo_solicitado': nome_arquivo,
                'pasta_buscada': STATIC_DIR
            }
        
        # Determinar qual script de carga usar baseado no nome do arquivo
        script_carga = None
        
        if 'TradeInformationConsolidatedFile' in nome_arquivo:
            script_carga = 'carga_b3_TradeInformationConsolidatedFile_sem_emoji.py'
        elif 'InstrumentsConsolidatedFile' in nome_arquivo:
            # Usar o mesmo script para InstrumentsConsolidatedFile por enquanto
            script_carga = 'carga_b3_TradeInformationConsolidatedFile_sem_emoji.py'
        else:
            return {
                'status': 'erro',
                'mensagem': f'Tipo de arquivo não suportado para carga: {nome_arquivo}',
                'arquivo_solicitado': nome_arquivo,
                'tipos_suportados': ['TradeInformationConsolidatedFile', 'InstrumentsConsolidatedFile']
            }
        
        # Caminho para o script de carga
        pasta_rotinas = os.path.join(settings.BASE_DIR, 'rotinas_individuais')
        script_path = os.path.join(pasta_rotinas, script_carga)
        
        if not os.path.exists(script_path):
            return {
                'status': 'erro',
                'mensagem': f'Script de carga não encontrado: {script_carga}',
                'script_esperado': script_path
            }
        
        print(f"[CARGA] Executando carga para arquivo: {nome_arquivo}")
        print(f"[CARGA] Script: {script_path}")
        
        # Executar script de carga passando o nome do arquivo como argumento
        resultado_processo = subprocess.run(
            [sys.executable, script_path, nome_arquivo],  # Passar nome do arquivo como argumento
            cwd=pasta_rotinas,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minutos de timeout
            encoding='utf-8',
            errors='ignore'  # Ignorar caracteres não UTF-8
        )
        
        # Analisar resultado
        if resultado_processo.returncode == 0:
            # Sucesso
            return {
                'status': 'sucesso',
                'mensagem': f'Carga do arquivo {nome_arquivo} executada com sucesso',
                'arquivo_processado': nome_arquivo,
                'script_utilizado': script_carga,
                'codigo_retorno': resultado_processo.returncode,
                'saida_stdout': resultado_processo.stdout,
                'saida_stderr': resultado_processo.stderr if resultado_processo.stderr else None
            }
        else:
            # Erro na execução
            return {
                'status': 'erro',
                'mensagem': f'Erro na execução da carga para arquivo {nome_arquivo}',
                'arquivo_processado': nome_arquivo,
                'script_utilizado': script_carga,
                'codigo_retorno': resultado_processo.returncode,
                'saida_stdout': resultado_processo.stdout,
                'saida_stderr': resultado_processo.stderr
            }
            
    except subprocess.TimeoutExpired:
        return {
            'status': 'erro',
            'mensagem': f'Timeout na execução da carga para arquivo {nome_arquivo} (5 minutos)',
            'arquivo_processado': nome_arquivo
        }
    except Exception as e:
        return {
            'status': 'erro',
            'mensagem': f'Erro inesperado na carga do arquivo {nome_arquivo}: {str(e)}',
            'arquivo_processado': nome_arquivo
        }


@api_view(['GET', 'POST'])
def static_arquivos(request):
    """Endpoint para listar ou gerenciar arquivos da pasta static"""
    try:
        if request.method == 'GET':
            # Executar a listagem
            resultado = listar_arquivos_static()
            
            return Response({
                'message': 'Listagem de arquivos static executada com sucesso',
                'resultado': resultado
            }, status=status.HTTP_200_OK)
        
        elif request.method == 'POST':
            # Verificar a ação solicitada
            acao = request.data.get('acao', '').lower()
            
            if acao == 'deletar_todos':
                # Executar deleção de todos os arquivos
                resultado = deletar_todos_arquivos_static()
                
                if resultado['status'] == 'sucesso':
                    return Response({
                        'message': f'Deleção executada com sucesso: {resultado["arquivos_deletados"]} arquivos deletados',
                        'resultado': resultado
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({
                        'error': resultado['mensagem'],
                        'resultado': resultado
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            elif acao == 'carga':
                # Executar carga de arquivo específico
                arquivo = request.data.get('arquivo')
                
                # Log detalhado para debug
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f"[DEBUG] Recebido request para carga: acao={acao}, arquivo={arquivo}")
                logger.info(f"[DEBUG] Request data completo: {request.data}")
                
                if not arquivo:
                    return Response({
                        'error': 'Parâmetro "arquivo" é obrigatório para ação "carga"',
                        'request_data_recebido': request.data,
                        'exemplo': {
                            'acao': 'carga',
                            'arquivo': 'TradeInformationConsolidatedFile_20250910_1.csv'
                        }
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                resultado = executar_carga_arquivo(arquivo)
                
                if resultado['status'] == 'sucesso':
                    return Response({
                        'message': f'Carga do arquivo {arquivo} executada com sucesso',
                        'resultado': resultado
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({
                        'error': resultado['mensagem'],
                        'resultado': resultado
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            elif acao == 'listar':
                # Executar listagem via POST
                resultado = listar_arquivos_static()
                
                return Response({
                    'message': 'Listagem de arquivos static executada com sucesso',
                    'resultado': resultado
                }, status=status.HTTP_200_OK)
            
            else:
                return Response({
                    'error': f'Ação "{acao}" não reconhecida. Ações disponíveis: "deletar_todos", "carga", "listar"',
                    'acoes_disponiveis': ['deletar_todos', 'carga', 'listar'],
                    'exemplos': {
                        'deletar_todos': {'acao': 'deletar_todos'},
                        'carga': {'acao': 'carga', 'arquivo': 'TradeInformationConsolidatedFile_20250910_1.csv'},
                        'listar': {'acao': 'listar'}
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        return Response({
            'error': f'Erro ao processar requisição: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def grafico_tabela_precos(request):
    """
    Endpoint para consultar estatísticas da tabela organizesee_ativosprecos
    Retorna contagem por tipo (Ação, FII, Índices) para as últimas 20 datas
    """
    try:
        from django.db import connection
        
        with connection.cursor() as cursor:
            # 1. Buscar as últimas 20 datas distintas
            cursor.execute("""
                SELECT DISTINCT data 
                FROM organizesee_ativosprecos 
                ORDER BY data DESC 
                LIMIT 20
            """)
            
            datas_resultado = cursor.fetchall()
            datas_lista = [row[0] for row in datas_resultado]
            
            if not datas_lista:
                return Response({
                    'message': 'Nenhum dado encontrado na tabela organizesee_ativosprecos',
                    'datas': [],
                    'estatisticas': []
                })
            
            # 2. Para cada data, contar por tipo (com normalização)
            estatisticas_por_data = []
            
            for data in datas_lista:
                cursor.execute("""
                    SELECT 
                        CASE 
                            WHEN UPPER(tipo) IN ('ACAO', 'ACOES') THEN 'Acao'
                            WHEN UPPER(tipo) IN ('FII', 'FUNDOS IMOBILIÁRIOS', 'FUNDOS IMOBILIÃ¡RIOS') THEN 'FII'
                            WHEN UPPER(tipo) IN ('INDICE', 'INDICES', 'ÍNDICE', 'ÍNDICES') THEN 'Indice'
                            WHEN UPPER(tipo) = 'ETF' THEN 'ETF'
                            ELSE tipo
                        END as tipo_normalizado,
                        COUNT(*) as quantidade
                    FROM organizesee_ativosprecos 
                    WHERE data = %s
                    GROUP BY tipo_normalizado
                    ORDER BY tipo_normalizado
                """, [data])
                
                contagem_tipos = cursor.fetchall()
                
                # Organizar os dados por tipo
                estatistica_data = {
                    'data': data.strftime('%Y-%m-%d'),
                    'tipos': {
                        'Acao': 0,
                        'FII': 0,
                        'Indice': 0,
                        'ETF': 0
                    },
                    'total': 0
                }
                
                for tipo_normalizado, quantidade in contagem_tipos:
                    if tipo_normalizado in estatistica_data['tipos']:
                        estatistica_data['tipos'][tipo_normalizado] = quantidade
                    else:
                        # Para tipos não esperados, adicionar dinamicamente
                        estatistica_data['tipos'][tipo_normalizado] = quantidade
                    
                    estatistica_data['total'] += quantidade
                
                estatisticas_por_data.append(estatistica_data)
            
            # 3. Calcular estatísticas gerais
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_registros,
                    COUNT(DISTINCT ticker) as total_tickers,
                    COUNT(DISTINCT data) as total_datas,
                    MIN(data) as data_minima,
                    MAX(data) as data_maxima
                FROM organizesee_ativosprecos
            """)
            
            estatisticas_gerais = cursor.fetchone()
            
            # 4. Contagem geral por tipo (normalizado)
            cursor.execute("""
                SELECT 
                    CASE 
                        WHEN UPPER(tipo) IN ('ACAO', 'ACOES') THEN 'Acao'
                        WHEN UPPER(tipo) IN ('FII', 'FUNDOS IMOBILIÁRIOS', 'FUNDOS IMOBILIÃ¡RIOS') THEN 'FII'
                        WHEN UPPER(tipo) IN ('INDICE', 'INDICES', 'ÍNDICE', 'ÍNDICES') THEN 'Indice'
                        WHEN UPPER(tipo) = 'ETF' THEN 'ETF'
                        ELSE tipo
                    END as tipo_normalizado,
                    COUNT(*) as total_registros,
                    COUNT(DISTINCT ticker) as tickers_unicos
                FROM organizesee_ativosprecos 
                GROUP BY tipo_normalizado
                ORDER BY total_registros DESC
            """)
            
            resumo_tipos = []
            for tipo_normalizado, total_reg, tickers_unicos in cursor.fetchall():
                resumo_tipos.append({
                    'tipo': tipo_normalizado,
                    'total_registros': total_reg,
                    'tickers_unicos': tickers_unicos
                })
            
            # 5. Dados para gráfico - série temporal das últimas 20 datas
            series_grafico = {
                'Acao': [],
                'FII': [],
                'Indice': [],
                'ETF': []
            }
            
            for estat in estatisticas_por_data:
                for tipo in series_grafico.keys():
                    series_grafico[tipo].append({
                        'data': estat['data'],
                        'quantidade': estat['tipos'].get(tipo, 0)
                    })
        
        # Resposta da API
        response_data = {
            'success': True,
            'datas_analisadas': [data.strftime('%Y-%m-%d') for data in datas_lista],
            'total_datas': len(datas_lista),
            'estatisticas_por_data': estatisticas_por_data,
            'series_grafico': series_grafico,
            'estatisticas_gerais': {
                'total_registros': estatisticas_gerais[0] if estatisticas_gerais[0] else 0,
                'total_tickers': estatisticas_gerais[1] if estatisticas_gerais[1] else 0,
                'total_datas': estatisticas_gerais[2] if estatisticas_gerais[2] else 0,
                'data_minima': estatisticas_gerais[3].strftime('%Y-%m-%d') if estatisticas_gerais[3] else None,
                'data_maxima': estatisticas_gerais[4].strftime('%Y-%m-%d') if estatisticas_gerais[4] else None
            },
            'resumo_por_tipo': resumo_tipos,
            'observacoes': [
                'Tipos foram normalizados: ACAO/Acoes -> Acao, FII/Fundos Imobiliários -> FII, INDICE -> Indice',
                'Dados ordenados por data decrescente (mais recente primeiro)',
                'Series_grafico contém dados formatados para gráficos temporais'
            ]
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': f'Erro ao consultar dados: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==================== APIS DO SCHEDULER ====================

@api_view(['POST'])
def executar_carga_diaria(request):
    """API para executar carga diária de rotinas manualmente"""
    try:
        from .scheduler_services import CargaDiariaService
        from django.utils import timezone
        from datetime import datetime
        
        service = CargaDiariaService()
        
        # Obter data do request ou usar atual
        data_str = request.data.get('data')
        if data_str:
            try:
                data_execucao = datetime.strptime(data_str, '%Y-%m-%d').date()
            except ValueError:
                return Response({
                    'success': False,
                    'error': 'Formato de data inválido. Use YYYY-MM-DD'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            data_execucao = timezone.now().date()
        
        # Primeiro, verificar se há itens com horários desatualizados
        from .scheduler_services import SchedulerService
        scheduler = SchedulerService()
        
        # Verificar e corrigir horários desatualizados antes da carga
        scheduler.corrigir_horarios_desatualizados_fila()
        
        # Executar carga com substituição
        carga = service.executar_carga_diaria(data_execucao)
        
        # Verificar duplicatas após a carga
        scheduler.verificar_duplicatas_fila()
        
        return Response({
            'success': True,
            'data': {
                'data_carga': carga.data_carga.strftime('%Y-%m-%d'),
                'status': carga.get_status_display(),
                'total_rotinas_processadas': carga.total_rotinas_processadas,
                'total_rotinas_adicionadas_fila': carga.total_rotinas_adicionadas_fila,
                'total_rotinas_ignoradas': carga.total_rotinas_ignoradas,
                'duracao_segundos': carga.duracao_segundos,
                'arquivo_log': os.path.basename(carga.arquivo_log) if carga.arquivo_log else None
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        # Log detalhado do erro
        import logging
        logger = logging.getLogger('rotinas_automaticas.views')
        logger.error(f'Erro ao executar carga diária: {str(e)}', exc_info=True)
        
        # Tratamento especial para erros de conexão
        if "connection already closed" in str(e):
            # Tentar reconexão e nova execução
            from django import db
            db.connections.close_all()
            
            try:
                # Reconectar e tentar novamente
                service = CargaDiariaService()
                carga = service.executar_carga_diaria(data_execucao)
                
                return Response({
                    'success': True,
                    'data': {
                        'data_carga': carga.data_carga.strftime('%Y-%m-%d'),
                        'status': carga.get_status_display(),
                        'observacao': 'Reconexão automática realizada',
                        'total_rotinas_processadas': carga.total_rotinas_processadas,
                        'total_rotinas_adicionadas_fila': carga.total_rotinas_adicionadas_fila,
                        'total_rotinas_ignoradas': carga.total_rotinas_ignoradas,
                    }
                })
            except Exception as e2:
                # Se ainda houver erro, desistir
                logger.error(f'Erro na tentativa de reconexão: {str(e2)}', exc_info=True)
        
        # Resposta padrão de erro
        return Response({
            'success': False,
            'error': f'Erro ao executar carga diária: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def executar_scheduler(request):
    """API para executar scheduler manualmente"""
    try:
        from .scheduler_services import ExecutorRotinas
        
        executor = ExecutorRotinas()
        limite = request.data.get('limite', 10)
        
        resultado = executor.executar_fila(limite_execucoes=limite)
        
        return Response({
            'success': True,
            'data': {
                'total_executadas': resultado['total_executadas'],
                'total_sucesso': resultado['total_sucesso'],
                'total_erro': resultado['total_erro'],
                'execucoes': [
                    {
                        'rotina': exec['item_fila'].scheduler_rotina.rotina_definicao.nome_exibicao,
                        'status': exec['item_fila'].get_status_display(),
                        'sucesso': exec['sucesso'],
                        'duracao_segundos': exec['item_fila'].duracao_segundos,
                        'erro': exec.get('erro') if not exec['sucesso'] else None
                    }
                    for exec in resultado['execucoes']
                ]
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': f'Erro ao executar scheduler: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def status_fila_execucao(request):
    """API para consultar status da fila de execução"""
    try:
        from .models import FilaExecucao
        from django.utils import timezone
        
        # Buscar itens da fila
        fila_items = FilaExecucao.objects.filter(
            data_execucao__gte=timezone.now().date()
        ).select_related('scheduler_rotina', 'scheduler_rotina__rotina_definicao').order_by(
            'data_execucao', 'horario_execucao', 'prioridade'
        )
        
        # Estatísticas
        total_pendentes = fila_items.filter(status='PENDENTE').count()
        total_executando = fila_items.filter(status='EXECUTANDO').count()
        total_concluidas = fila_items.filter(status='CONCLUIDA').count()
        total_erro = fila_items.filter(status='ERRO').count()
        
        # Detalhes dos itens
        items_data = []
        for item in fila_items[:50]:  # Limitar a 50 itens
            items_data.append({
                'id': item.id,
                'rotina_nome': item.scheduler_rotina.rotina_definicao.nome_exibicao,
                'tipo_execucao': item.scheduler_rotina.get_tipo_execucao_display(),
                'data_execucao': item.data_execucao.strftime('%Y-%m-%d'),
                'horario_execucao': item.horario_execucao.strftime('%H:%M'),
                'status': item.get_status_display(),
                'prioridade': item.prioridade,
                'tentativa_atual': item.tentativa_atual,
                'max_tentativas': item.max_tentativas,
                'duracao_segundos': item.duracao_segundos,
                'arquivo_processado': item.arquivo_processado
            })
        
        return Response({
            'success': True,
            'data': {
                'estatisticas': {
                    'total_pendentes': total_pendentes,
                    'total_executando': total_executando,
                    'total_concluidas': total_concluidas,
                    'total_erro': total_erro,
                    'total_geral': fila_items.count()
                },
                'items': items_data
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': f'Erro ao consultar fila: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def logs_scheduler(request):
    """API para consultar logs do scheduler"""
    try:
        from .models import LogScheduler
        
        # Parâmetros de filtro
        nivel = request.GET.get('nivel')
        componente = request.GET.get('componente')
        limite = int(request.GET.get('limite', 100))
        
        logs_query = LogScheduler.objects.all()
        
        if nivel:
            logs_query = logs_query.filter(nivel=nivel.upper())
        
        if componente:
            logs_query = logs_query.filter(componente__icontains=componente)
        
        logs = logs_query.order_by('-criado_em')[:limite]
        
        logs_data = []
        for log in logs:
            logs_data.append({
                'id': log.id,
                'nivel': log.get_nivel_display(),
                'componente': log.componente,
                'mensagem': log.mensagem,
                'criado_em': log.criado_em.strftime('%Y-%m-%d %H:%M:%S'),
                'dados_extra': log.dados_extra,
                'fila_execucao_id': log.fila_execucao_id if log.fila_execucao else None
            })
        
        return Response({
            'success': True,
            'data': {
                'total_logs': logs_query.count(),
                'logs': logs_data
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': f'Erro ao consultar logs: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def cancelar_item_fila(request, item_id):
    """API para cancelar item específico da fila"""
    try:
        from .models import FilaExecucao
        from django.utils import timezone
        from .serializers import FilaExecucaoSerializer
        
        item = FilaExecucao.objects.get(id=item_id)
        
        if item.status in ['CONCLUIDA', 'CANCELADA']:
            return Response({
                'success': False,
                'error': f'Item já está {item.get_status_display()}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        item.status = 'CANCELADA'
        item.finalizado_em = timezone.now()
        item.save()
        
        # Serializar o item para retornar detalhes atualizados
        serializer = FilaExecucaoSerializer(item)
        
        return Response({
            'success': True,
            'message': f'Item {item_id} cancelado com sucesso',
            'item': serializer.data
        }, status=status.HTTP_200_OK)
        
    except FilaExecucao.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Item não encontrado'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'error': f'Erro ao cancelar item: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def status_monitor(request):
    """Verificar status do monitor em background"""
    try:
        from .monitor_scheduler import status_monitor
        
        status_info = status_monitor()
        
        return Response({
            'monitor': status_info,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
@api_view(['GET'])
def verificar_saude_monitor(request):
    """Verifica saúde do monitor e o reinicia automaticamente se necessário"""
    try:
        from .monitor_scheduler import verificar_saude_monitor
        
        resultado = verificar_saude_monitor()
        
        return Response({
            'resultado': resultado,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# --- Novas APIs para gerenciamento de rotinas ---

@api_view(['GET'])
def listar_rotinas(request):
    """Listar todas as rotinas cadastradas no scheduler"""
    try:
        from .models import SchedulerRotina
        from .serializers import SchedulerRotinaSerializer
        
        # Buscar todas as rotinas
        rotinas = SchedulerRotina.objects.select_related('rotina_definicao', 'grupo_dias').all()
        
        # Aplicar filtros se fornecidos
        tipo_execucao = request.query_params.get('tipo_execucao')
        if tipo_execucao:
            rotinas = rotinas.filter(tipo_execucao=tipo_execucao)
            
        ativas = request.query_params.get('ativas')
        if ativas:
            rotinas = rotinas.filter(executar=True if ativas.lower() == 'true' else False)
        
        serializer = SchedulerRotinaSerializer(rotinas, many=True)
        
        return Response({
            'success': True,
            'rotinas': serializer.data,
            'total': rotinas.count()
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': f'Erro ao listar rotinas: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'PATCH', 'PUT'])
def gerenciar_rotina(request, rotina_id):
    """Gerencia uma rotina específica (visualizar, atualizar status, editar)"""
    try:
        from .models import SchedulerRotina
        from .serializers import SchedulerRotinaSerializer
        
        # Buscar a rotina
        try:
            rotina = SchedulerRotina.objects.select_related('rotina_definicao', 'grupo_dias').get(pk=rotina_id)
        except SchedulerRotina.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Rotina não encontrada'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # GET - Retorna detalhes da rotina
        if request.method == 'GET':
            serializer = SchedulerRotinaSerializer(rotina)
            return Response({
                'success': True,
                'rotina': serializer.data
            })
        
        # PATCH - Atualiza apenas status da rotina (ativar/desativar)
        elif request.method == 'PATCH':
            # Verificar se o campo executar foi fornecido
            if 'executar' in request.data:
                rotina.executar = request.data['executar']
                rotina.save()
                
                serializer = SchedulerRotinaSerializer(rotina)
                return Response({
                    'success': True,
                    'message': f'Rotina {"ativada" if rotina.executar else "desativada"} com sucesso',
                    'rotina': serializer.data
                })
            else:
                return Response({
                    'success': False,
                    'error': 'Campo "executar" não fornecido'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # PUT - Atualiza vários campos da rotina
        elif request.method == 'PUT':
            # Campos permitidos para atualização
            campos_permitidos = [
                'tipo_execucao', 'tipo_rotina', 'grupo_dias', 'ciclico',
                'intervalo_horas', 'executar', 'horario_execucao', 'endpoint_url',
                'metodo_http', 'mascara_arquivo', 'pasta_origem', 'permite_recovery',
                'max_tentativas_recovery', 'prioridade'
            ]
            
            # Atualizar apenas os campos permitidos
            for campo in campos_permitidos:
                if campo in request.data:
                    setattr(rotina, campo, request.data[campo])
            
            rotina.save()
            
            serializer = SchedulerRotinaSerializer(rotina)
            return Response({
                'success': True,
                'message': 'Rotina atualizada com sucesso',
                'rotina': serializer.data
            })
    
    except Exception as e:
        return Response({
            'success': False,
            'error': f'Erro ao gerenciar rotina: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def executar_rotina_especifica(request, rotina_id):
    """Executa uma rotina específica imediatamente"""
    try:
        from .models import SchedulerRotina, FilaExecucao
        from django.utils import timezone
        import pytz
        
        # Buscar a rotina
        try:
            rotina = SchedulerRotina.objects.select_related('rotina_definicao').get(pk=rotina_id)
        except SchedulerRotina.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Rotina não encontrada'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Verificar se a rotina está ativa
        if not rotina.executar:
            return Response({
                'success': False,
                'error': 'Não é possível executar uma rotina inativa'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Criar item na fila com execução imediata
        agora = timezone.now()
        
        # Verificar se já existe execução pendente para esta rotina
        existente = FilaExecucao.objects.filter(
            scheduler_rotina=rotina,
            status='PENDENTE'
        ).first()
        
        if existente:
            return Response({
                'success': False,
                'error': 'Já existe uma execução pendente para esta rotina',
                'item_fila_id': existente.id
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Criar novo item na fila para execução imediata
        item_fila = FilaExecucao(
            scheduler_rotina=rotina,
            data_execucao=agora.date(),
            horario_execucao=agora.time(),
            status='PENDENTE',
            prioridade=rotina.prioridade,
            max_tentativas=rotina.max_tentativas_recovery if rotina.permite_recovery else 1
        )
        item_fila.save()
        
        # Executar o scheduler para processar o item
        from .scheduler_services import SchedulerService
        service = SchedulerService()
        
        # Executar apenas este item
        resultado = service.executar_rotinas(id_fila=item_fila.id)
        
        # Se disponível, usar o serializador para o item da fila
        from .serializers import FilaExecucaoSerializer
        item_atualizado = FilaExecucao.objects.get(pk=item_fila.id)
        serializer = FilaExecucaoSerializer(item_atualizado)
        
        return Response({
            'success': True,
            'message': f'Rotina "{rotina.rotina_definicao.nome}" executada',
            'item_fila': serializer.data,
            'resultado_execucao': resultado
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': f'Erro ao executar rotina: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def reiniciar_monitor(request):
    """Reiniciar monitor em background"""
    try:
        from .monitor_scheduler import parar_monitor, iniciar_monitor
        
        # Parar monitor existente
        parou = parar_monitor()
        
        # Aguardar um pouco
        import time
        time.sleep(2)
        
        # Iniciar novamente
        iniciou = iniciar_monitor()
        
        return Response({
            'success': True,
            'monitor_parado': parou,
            'monitor_iniciado': iniciou,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
