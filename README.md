# Serviços - Rotinas Automáticas

Este é um projeto Django REST Framework para execução de rotinas automáticas de download.

## Configuração do Projeto

### Estrutura
- **Projeto:** servicos
- **Aplicativo:** rotinas_automaticas
- **Banco de dados:** PostgreSQL (configurado)

### Dependências
- Django 5.2.6
- Django REST Framework 3.16.1
- psycopg2-binary (para PostgreSQL)
- python-dotenv
- requests (para downloads HTTP)
- django-cors-headers (para CORS)

### Configurações CORS
- **Origem permitida:** `http://localhost:3000` e `http://127.0.0.1:3000`
- **Métodos permitidos:** GET, POST, PUT, PATCH, DELETE, OPTIONS
- **Headers permitidos:** Todos os headers necessários
- **Credenciais:** Habilitadas

## Endpoints Disponíveis

### 1. Download CVM
- **URL:** `http://127.0.0.1:8000/api/download_cvm/`
- **Métodos:** GET, POST
- **Descrição:** Executa o script de download da CVM, baixa e extrai arquivos ZIP
- **Pasta destino:** `static/downloadbruto/`
- **Arquivos baixados:**
  - **Ações:** `fca_cia_aberta_2025.zip` (extraído automaticamente)
  - **FII Anual:** `inf_anual_fii_2024.zip` (extraído automaticamente)
  - **FII Mensal:** `inf_mensal_fii_2025.zip` (extraído automaticamente)
- **Funcionalidades:**
  - Download automático de 3 arquivos ZIP da CVM
  - Extração automática dos arquivos CSV
  - Remoção dos arquivos ZIP após extração
  - Mantém TODOS os arquivos CSV extraídos (sem exclusões)

### 2. Download B3
- **URL:** `http://127.0.0.1:8000/api/download_b3/`
- **Métodos:** GET, POST
- **Descrição:** Executa o script de download da B3, baixa arquivos de múltiplos dias úteis
- **Pasta destino:** `static/downloadbruto/`
- **Parâmetro:** `dias` (opcional, padrão: 3, máximo: 10)
- **Arquivos baixados por dia:**
  - **Instrumentos:** `InstrumentsConsolidatedFile_YYYYMMDD_1.csv`
  - **Negociações:** `TradeInformationConsolidatedFile_YYYYMMDD_1.csv`
  - **Pós-mercado:** `TradeInformationConsolidatedAfterHoursFile_YYYYMMDD_1.csv`
- **Funcionalidades:**
  - Download automático da API oficial da B3
  - Cálculo inteligente de dias úteis (exclui sábados e domingos)
  - Processo em duas etapas: token + download
  - Suporte a parâmetro de quantidade de dias

**Exemplos de uso:**
- `GET /api/download_b3/` - Baixa 3 dias úteis (padrão)
- `GET /api/download_b3/?dias=5` - Baixa 5 dias úteis
- `POST /api/download_b3/` com `{"dias": 2}` - Baixa 2 dias úteis

## Como Executar

### 1. Ativar o ambiente virtual
```powershell
.\.venv\Scripts\Activate.ps1
```

### 2. Executar o servidor
```powershell
python manage.py runserver 8000
```

### 3. Testar os endpoints
Acesse no navegador ou use um cliente HTTP como Postman:
- `http://127.0.0.1:8000/api/download_cvm/`
- `http://127.0.0.1:8000/api/download_b3/`

## Estrutura de Pastas

```
servicos_organizesee/
├── .venv/                      # Ambiente virtual
├── static/
│   └── downloadbruto/          # Arquivos de download gerados
├── servicos/                   # Configurações do projeto
│   ├── settings.py
│   ├── urls.py
│   └── ...
├── rotinas_automaticas/        # Aplicativo principal
│   ├── views.py
│   ├── urls.py
│   └── ...
├── manage.py
└── README.md
```

## Banco de Dados

O projeto está configurado para usar PostgreSQL com as seguintes configurações:
- **Engine:** postgresql
- **Database:** dagjgmra6bck94
- **Host:** casrkuuedp6an1.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com
- **Port:** 5432
- **User:** u71lo0hl2prk2v

## Funcionalidades

- ✅ Projeto Django REST Framework configurado
- ✅ Aplicativo rotinas_automaticas criado
- ✅ Banco PostgreSQL configurado
- ✅ Endpoints de download CVM e B3 funcionais
- ✅ Geração automática de arquivos na pasta static/downloadbruto
- ✅ Resposta JSON com status da operação

## Resposta dos Endpoints

### Endpoint CVM
Os endpoints retornam uma resposta JSON no formato:

```json
{
    "message": "Download CVM executado com sucesso",
    "resultado": {
        "status": "sucesso",
        "mensagem": "Download e processamento de arquivos CVM concluído",
        "pasta_destino": "static/downloadbruto",
        "urls_processadas": 3,
        "arquivos_extraidos": ["fca_cia_aberta_2025.csv", "inf_anual_fii_geral_2024.csv", ...]
    }
}
```

### Endpoint B3
```json
{
    "message": "Download B3 executado para 2 dias úteis",
    "dias_solicitados": 2,
    "resultado": {
        "status": "sucesso",
        "mensagem": "Downloads B3 concluídos: 6/6",
        "pasta_destino": "static/downloadbruto",
        "dias_processados": 2,
        "datas": ["2025-09-09", "2025-09-10"],
        "downloads_sucesso": 6,
        "total_downloads": 6,
        "arquivos_baixados": [
            "InstrumentsConsolidatedFile_20250909_1.csv",
            "TradeInformationConsolidatedFile_20250909_1.csv",
            "TradeInformationConsolidatedAfterHoursFile_20250909_1.csv",
            "InstrumentsConsolidatedFile_20250910_1.csv",
            "TradeInformationConsolidatedFile_20250910_1.csv",
            "TradeInformationConsolidatedAfterHoursFile_20250910_1.csv"
        ]
    }
}
```

## Arquivos Baixados da CVM

### Dados de Ações (FCA)
- `fca_cia_aberta_2025.csv` - Dados principais das companhias
- `fca_cia_aberta_geral_2025.csv` - Informações gerais
- `fca_cia_aberta_valor_mobiliario_2025.csv` - Valores mobiliários
- `fca_cia_aberta_auditor_2025.csv` - Dados dos auditores
- `fca_cia_aberta_canal_divulgacao_2025.csv` - Canais de divulgação
- `fca_cia_aberta_departamento_acionistas_2025.csv` - Departamento de acionistas
- `fca_cia_aberta_dri_2025.csv` - Diretor de relações com investidores
- `fca_cia_aberta_endereco_2025.csv` - Endereços das companhias
- `fca_cia_aberta_escriturador_2025.csv` - Escrituradores
- `fca_cia_aberta_pais_estrangeiro_negociacao_2025.csv` - Negociação no exterior

### Dados de Fundos Imobiliários (FII)
**Informações Anuais 2024:**
- `inf_anual_fii_geral_2024.csv` - Dados gerais dos FII
- `inf_anual_fii_ativo_valor_contabil_2024.csv` - Ativos e valores contábeis
- `inf_anual_fii_complemento_2024.csv` - Informações complementares
- `inf_anual_fii_diretor_responsavel_2024.csv` - Diretores responsáveis
- `inf_anual_fii_distribuicao_cotistas_2024.csv` - Distribuição de cotistas
- `inf_anual_fii_experiencia_profissional_2024.csv` - Experiência profissional
- `inf_anual_fii_ativo_adquirido_2024.csv` - Ativos adquiridos
- `inf_anual_fii_ativo_transacao_2024.csv` - Transações de ativos
- `inf_anual_fii_prestador_servico_2024.csv` - Prestadores de serviço
- `inf_anual_fii_processo_2024.csv` - Processos
- `inf_anual_fii_processo_semelhante_2024.csv` - Processos semelhantes
- `inf_anual_fii_representante_cotista_2024.csv` - Representantes de cotistas

**Informações Mensais 2025:**
- `inf_mensal_fii_geral_2025.csv` - Dados gerais mensais
- `inf_mensal_fii_ativo_passivo_2025.csv` - Ativo e passivo
- `inf_mensal_fii_complemento_2025.csv` - Informações complementares mensais

## Arquivos Baixados da B3

### Dados Diários de Mercado
**Por dia útil solicitado:**

**Instrumentos:**
- `InstrumentsConsolidatedFile_YYYYMMDD_1.csv` - Lista de todos os instrumentos negociáveis

**Negociações (Pregão Regular):**
- `TradeInformationConsolidatedFile_YYYYMMDD_1.csv` - Dados consolidados de negociação do pregão regular

**Negociações (Pós-mercado):**
- `TradeInformationConsolidatedAfterHoursFile_YYYYMMDD_1.csv` - Dados consolidados de negociação after-hours

### Lógica de Dias Úteis
- **Inclui:** Segunda a sexta-feira
- **Exclui:** Sábados e domingos
- **Exemplo:** Se hoje for segunda e solicitar 3 dias, buscará: sexta anterior, hoje (segunda) e amanhã (terça)
- **Limite:** Máximo 10 dias úteis por requisição

## Desenvolvimento

Para adicionar novos scripts de download:
1. Crie uma nova view em `rotinas_automaticas/views.py`
2. Adicione a URL correspondente em `rotinas_automaticas/urls.py`
3. Implemente a lógica de download e geração de arquivo
#   P r o d S e r v i c e  
 