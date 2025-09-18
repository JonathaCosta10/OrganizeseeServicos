# APIs do Sistema de Scheduler

## 📋 Visão Geral

Este documento descreve todas as APIs disponíveis para interagir com o sistema de scheduler. As APIs estão organizadas por funcionalidade.

## 🔍 Estrutura da API

Todas as APIs seguem a estrutura REST e retornam JSON com os seguintes campos comuns:
- `success`: Booleano indicando sucesso ou falha
- `mensagem/error`: Mensagem de sucesso ou erro
- Dados específicos de cada endpoint

## 📊 APIs do Scheduler

### 1. Gerenciamento de Rotinas

#### 1.1 Listar Rotinas Cadastradas
```
GET /api/scheduler/rotinas/
```

**Parâmetros Query (opcionais):**
- `tipo_execucao`: Filtrar por tipo (DIARIO, MENSAL, etc.)
- `ativas`: Filtrar por status (true/false)

**Resposta:**
```json
{
  "success": true,
  "rotinas": [
    {
      "id": 1,
      "nome": "download_b3",
      "nome_exibicao": "Download B3",
      "descricao": "Download de arquivos da B3",
      "tipo_execucao": "DIARIO",
      "tipo_rotina": "DOWNLOAD_ARQUIVO",
      "grupo_dias": 1,
      "grupo_dias_nome": "Dias de Semana (Segunda a Sexta)",
      "ciclico": false,
      "intervalo_horas": 1,
      "executar": true,
      "horario_execucao": "09:00:00",
      "endpoint_url": "/api/download_b3/",
      "metodo_http": "POST",
      "mascara_arquivo": null,
      "pasta_origem": null,
      "permite_recovery": true,
      "max_tentativas_recovery": 3,
      "prioridade": 100,
      "criado_em": "2025-09-15T10:00:00",
      "atualizado_em": "2025-09-15T10:00:00"
    }
  ],
  "total": 1
}
```

#### 1.2 Obter Detalhes de Rotina
```
GET /api/scheduler/rotinas/{id}/
```

**Resposta:**
```json
{
  "success": true,
  "rotina": {
    "id": 1,
    "nome": "download_b3",
    "nome_exibicao": "Download B3",
    ...
  }
}
```

#### 1.3 Ativar/Desativar Rotina
```
PATCH /api/scheduler/rotinas/{id}/
```

**Corpo:**
```json
{
  "executar": true|false
}
```

**Resposta:**
```json
{
  "success": true,
  "message": "Rotina ativada com sucesso",
  "rotina": {
    "id": 1,
    "nome": "download_b3",
    ...
    "executar": true,
    ...
  }
}
```

#### 1.4 Atualizar Rotina
```
PUT /api/scheduler/rotinas/{id}/
```

**Corpo:**
```json
{
  "tipo_execucao": "DIARIO",
  "horario_execucao": "09:30:00",
  "prioridade": 50,
  ...
}
```

**Resposta:**
```json
{
  "success": true,
  "message": "Rotina atualizada com sucesso",
  "rotina": {
    "id": 1,
    "nome": "download_b3",
    ...
  }
}
```

#### 1.5 Executar Rotina Específica
```
POST /api/scheduler/rotinas/{id}/executar/
```

**Resposta:**
```json
{
  "success": true,
  "message": "Rotina \"Download B3\" executada",
  "item_fila": {
    "id": 5,
    "nome_rotina": "Download B3",
    "status": "CONCLUIDA",
    ...
  },
  "resultado_execucao": {
    "total_executadas": 1,
    "sucessos": 1,
    "erros": 0
  }
}
```

### 2. Gerenciamento da Fila de Execução

#### 2.1 Status da Fila
```
GET /api/scheduler/fila/status/
```

**Resposta:**
```json
{
  "data": "16/09/2025",
  "estatisticas": {
    "total": 5,
    "pendentes": 2,
    "executadas": 2,
    "erros": 1,
    "recovery": 0
  },
  "proximas_execucoes": [
    {
      "rotina": "Download B3",
      "horario": "09:00",
      "prioridade": 100
    },
    ...
  ]
}
```

#### 2.2 Cancelar Item da Fila
```
POST /api/scheduler/fila/{id}/cancelar/
```

**Resposta:**
```json
{
  "success": true,
  "message": "Item 5 cancelado com sucesso",
  "item": {
    "id": 5,
    "nome_rotina": "Download B3",
    "status": "CANCELADA",
    ...
  }
}
```

### 3. Execução do Scheduler

#### 3.1 Executar Scheduler Manualmente
```
POST /api/scheduler/executar/
```

**Resposta:**
```json
{
  "sucesso": true,
  "resultado": {
    "total_executadas": 3,
    "sucessos": 3,
    "erros": 0,
    "tempo_execucao_segundos": 5.2
  },
  "timestamp": "2025-09-16T10:30:00"
}
```

#### 3.2 Carregar Rotinas Diárias
```
POST /api/scheduler/carga-diaria/
```

**Resposta:**
```json
{
  "sucesso": true,
  "rotinas_carregadas": 5,
  "data": "16/09/2025",
  "timestamp": "2025-09-16T08:00:00"
}
```

### 4. Monitoramento

#### 4.1 Status do Monitor
```
GET /api/scheduler/monitor/status/
```

**Resposta:**
```json
{
  "monitor": {
    "ativo": true,
    "ultima_execucao_scheduler": "2025-09-16T09:05:00",
    "ultima_renovacao_diaria": "2025-09-16T00:01:00"
  },
  "timestamp": "2025-09-16T10:30:00"
}
```

#### 4.2 Reiniciar Monitor
```
POST /api/scheduler/monitor/reiniciar/
```

**Resposta:**
```json
{
  "success": true,
  "monitor_parado": true,
  "monitor_iniciado": true,
  "timestamp": "2025-09-16T10:35:00"
}
```

### 5. Logs

#### 5.1 Consultar Logs do Scheduler
```
GET /api/scheduler/logs/
```

**Resposta:**
```json
{
  "logs": [
    {
      "id": 1,
      "data": "16/09/2025 09:00:00",
      "rotina": "Download B3",
      "tipo": "INFO",
      "status": "CONCLUIDA",
      "mensagem": "Execução concluída com sucesso",
      "detalhes": null
    },
    ...
  ]
}
```

## 📁 APIs de Downloads e Arquivos

### 1. Download de Arquivos

#### 1.1 Download de Arquivos CVM
```
POST /api/download_cvm/
```

**Resposta:**
```json
{
  "status": "sucesso",
  "mensagem": "Download e processamento de arquivos CVM concluído",
  "pasta_destino": "static/downloadbruto",
  "urls_processadas": 3,
  "arquivos_extraidos": [...]
}
```

#### 1.2 Download de Arquivos B3
```
POST /api/download_b3/
POST /api/download_b3/{dias}/
```

**Resposta:**
```json
{
  "status": "sucesso",
  "mensagem": "Downloads B3 concluídos: 9/9",
  "pasta_destino": "static/downloadbruto",
  "dias_processados": 3,
  "datas": ["2025-09-13", "2025-09-14", "2025-09-15"],
  "downloads_sucesso": 9,
  "total_downloads": 9,
  "arquivos_baixados": [...]
}
```

### 2. Carga de Arquivos

#### 2.1 Carga de Arquivos
```
POST /api/static_arquivos/
```

**Corpo:**
```json
{
  "acao": "Carga",
  "arquivo": "TradeInformationConsolidatedFile_20250910_1.csv"
}
```

**Resposta:**
```json
{
  "status": "sucesso",
  "registros_processados": 1500,
  "tempo_execucao_segundos": 3.2,
  "arquivo": "TradeInformationConsolidatedFile_20250910_1.csv"
}
```

## 📊 Uso das APIs

### Exemplo de Fluxo de Trabalho:

1. **Listar rotinas disponíveis**
   ```
   GET /api/scheduler/rotinas/
   ```

2. **Atualizar horário de uma rotina**
   ```
   PUT /api/scheduler/rotinas/1/
   Corpo: {"horario_execucao": "10:30:00"}
   ```

3. **Ativar uma rotina**
   ```
   PATCH /api/scheduler/rotinas/2/
   Corpo: {"executar": true}
   ```

4. **Carregar rotinas diárias**
   ```
   POST /api/scheduler/carga-diaria/
   ```

5. **Verificar fila de execução**
   ```
   GET /api/scheduler/fila/status/
   ```

6. **Executar rotina manualmente**
   ```
   POST /api/scheduler/rotinas/1/executar/
   ```

7. **Monitorar status da execução**
   ```
   GET /api/scheduler/logs/
   ```
