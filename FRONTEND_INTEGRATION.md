# Integração Frontend com APIs de Scheduler

## 🚀 Visão Geral

Este documento fornece exemplos práticos para integrar o frontend React com as APIs do sistema de scheduler. Todas as APIs necessárias para a interface de controle foram implementadas.

## 📡 APIs Disponíveis

### 1. Gerenciamento de Rotinas

As seguintes APIs foram implementadas para gerenciar rotinas do scheduler:

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/scheduler/rotinas/` | GET | Listar todas as rotinas cadastradas |
| `/api/scheduler/rotinas/{id}/` | GET | Obter detalhes de uma rotina |
| `/api/scheduler/rotinas/{id}/` | PATCH | Ativar/desativar uma rotina |
| `/api/scheduler/rotinas/{id}/` | PUT | Atualizar configuração de uma rotina |
| `/api/scheduler/rotinas/{id}/executar/` | POST | Executar uma rotina específica |

### 2. Gerenciamento da Fila

As seguintes APIs estão disponíveis para gerenciar a fila de execução:

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/scheduler/fila/status/` | GET | Obter status da fila de execução |
| `/api/scheduler/fila/{id}/cancelar/` | POST | Cancelar item da fila |

### 3. Monitoramento e Controle

APIs para monitoramento e controle do sistema:

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/scheduler/executar/` | POST | Executar scheduler manualmente |
| `/api/scheduler/carga-diaria/` | POST | Realizar carga diária |
| `/api/scheduler/logs/` | GET | Consultar logs do scheduler |
| `/api/scheduler/monitor/status/` | GET | Verificar status do monitor |
| `/api/scheduler/monitor/reiniciar/` | POST | Reiniciar monitor |

## 🖥️ Exemplos de Uso (React + Axios)

### 1. Configurando o Cliente API

```javascript
// src/services/api.js
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json'
  }
});

export default api;
```

### 2. Serviço para Gerenciar Rotinas

```javascript
// src/services/schedulerService.js
import api from './api';

export const schedulerService = {
  // Rotinas
  listarRotinas: async (filtros = {}) => {
    const params = new URLSearchParams();
    if (filtros.tipo_execucao) params.append('tipo_execucao', filtros.tipo_execucao);
    if (filtros.ativas !== undefined) params.append('ativas', filtros.ativas);
    
    const response = await api.get(`/api/scheduler/rotinas/?${params}`);
    return response.data;
  },
  
  obterRotina: async (id) => {
    const response = await api.get(`/api/scheduler/rotinas/${id}/`);
    return response.data;
  },
  
  atualizarStatusRotina: async (id, executar) => {
    const response = await api.patch(`/api/scheduler/rotinas/${id}/`, { executar });
    return response.data;
  },
  
  atualizarRotina: async (id, dados) => {
    const response = await api.put(`/api/scheduler/rotinas/${id}/`, dados);
    return response.data;
  },
  
  executarRotina: async (id) => {
    const response = await api.post(`/api/scheduler/rotinas/${id}/executar/`);
    return response.data;
  },
  
  // Fila de Execução
  statusFila: async () => {
    const response = await api.get('/api/scheduler/fila/status/');
    return response.data;
  },
  
  cancelarItemFila: async (id) => {
    const response = await api.post(`/api/scheduler/fila/${id}/cancelar/`);
    return response.data;
  },
  
  // Controle do Scheduler
  executarScheduler: async () => {
    const response = await api.post('/api/scheduler/executar/');
    return response.data;
  },
  
  carregarRotinasDiarias: async () => {
    const response = await api.post('/api/scheduler/carga-diaria/');
    return response.data;
  },
  
  obterLogs: async () => {
    const response = await api.get('/api/scheduler/logs/');
    return response.data;
  },
  
  // Monitor
  statusMonitor: async () => {
    const response = await api.get('/api/scheduler/monitor/status/');
    return response.data;
  },
  
  reiniciarMonitor: async () => {
    const response = await api.post('/api/scheduler/monitor/reiniciar/');
    return response.data;
  }
};
```

### 3. Componentes React

#### 3.1 Dashboard Principal

```jsx
// src/components/scheduler/Dashboard.jsx
import React, { useState, useEffect } from 'react';
import { schedulerService } from '../../services/schedulerService';
import StatusPanel from './StatusPanel';
import ActionsPanel from './ActionsPanel';
import RoutinesTable from './RoutinesTable';
import QueueTable from './QueueTable';

function Dashboard() {
  const [loading, setLoading] = useState(true);
  const [statusData, setStatusData] = useState(null);
  const [monitorData, setMonitorData] = useState(null);
  const [rotinas, setRotinas] = useState([]);
  const [filaItems, setFilaItems] = useState([]);
  
  // Carregar dados iniciais
  useEffect(() => {
    async function loadData() {
      setLoading(true);
      try {
        const [statusFila, statusMonitor, rotinasData] = await Promise.all([
          schedulerService.statusFila(),
          schedulerService.statusMonitor(),
          schedulerService.listarRotinas()
        ]);
        
        setStatusData(statusFila);
        setMonitorData(statusMonitor);
        setRotinas(rotinasData.rotinas || []);
        setFilaItems(statusFila.proximas_execucoes || []);
      } catch (error) {
        console.error("Erro ao carregar dados:", error);
      } finally {
        setLoading(false);
      }
    }
    
    loadData();
    
    // Atualizar a cada 30 segundos
    const interval = setInterval(loadData, 30000);
    return () => clearInterval(interval);
  }, []);
  
  // Manipuladores de eventos
  const handleActivateRotina = async (id, executar) => {
    try {
      await schedulerService.atualizarStatusRotina(id, executar);
      // Atualizar lista de rotinas
      const rotinasData = await schedulerService.listarRotinas();
      setRotinas(rotinasData.rotinas || []);
    } catch (error) {
      console.error("Erro ao ativar/desativar rotina:", error);
    }
  };
  
  const handleExecutarRotina = async (id) => {
    try {
      await schedulerService.executarRotina(id);
      // Atualizar fila
      const statusFila = await schedulerService.statusFila();
      setStatusData(statusFila);
      setFilaItems(statusFila.proximas_execucoes || []);
    } catch (error) {
      console.error("Erro ao executar rotina:", error);
    }
  };
  
  const handleCancelarItem = async (id) => {
    try {
      await schedulerService.cancelarItemFila(id);
      // Atualizar fila
      const statusFila = await schedulerService.statusFila();
      setStatusData(statusFila);
      setFilaItems(statusFila.proximas_execucoes || []);
    } catch (error) {
      console.error("Erro ao cancelar item da fila:", error);
    }
  };
  
  const handleForcarCargaDiaria = async () => {
    try {
      await schedulerService.carregarRotinasDiarias();
      // Atualizar tudo
      const [statusFila, statusMonitor, rotinasData] = await Promise.all([
        schedulerService.statusFila(),
        schedulerService.statusMonitor(),
        schedulerService.listarRotinas()
      ]);
      
      setStatusData(statusFila);
      setMonitorData(statusMonitor);
      setRotinas(rotinasData.rotinas || []);
      setFilaItems(statusFila.proximas_execucoes || []);
    } catch (error) {
      console.error("Erro ao forçar carga diária:", error);
    }
  };
  
  const handleExecutarScheduler = async () => {
    try {
      await schedulerService.executarScheduler();
      // Atualizar fila
      const statusFila = await schedulerService.statusFila();
      setStatusData(statusFila);
      setFilaItems(statusFila.proximas_execucoes || []);
    } catch (error) {
      console.error("Erro ao executar scheduler:", error);
    }
  };
  
  if (loading) {
    return <div>Carregando...</div>;
  }
  
  return (
    <div className="scheduler-dashboard">
      <h1>Painel de Controle - Scheduler</h1>
      
      <div className="dashboard-top">
        <StatusPanel 
          status={statusData} 
          monitor={monitorData} 
        />
        
        <ActionsPanel 
          onForcarCargaDiaria={handleForcarCargaDiaria}
          onExecutarScheduler={handleExecutarScheduler}
          onVerificarMonitor={async () => {
            const statusMonitor = await schedulerService.statusMonitor();
            setMonitorData(statusMonitor);
          }}
          onReiniciarMonitor={async () => {
            await schedulerService.reiniciarMonitor();
            const statusMonitor = await schedulerService.statusMonitor();
            setMonitorData(statusMonitor);
          }}
        />
      </div>
      
      <RoutinesTable 
        rotinas={rotinas} 
        onActivate={handleActivateRotina}
        onExecutar={handleExecutarRotina}
      />
      
      <QueueTable 
        items={filaItems} 
        onCancelar={handleCancelarItem}
      />
    </div>
  );
}

export default Dashboard;
```

#### 3.2 Tabela de Rotinas

```jsx
// src/components/scheduler/RoutinesTable.jsx
import React, { useState } from 'react';
import { Table, Button, Switch, Input, Select } from 'antd';
import { PlayCircleOutlined, EditOutlined, SearchOutlined } from '@ant-design/icons';

function RoutinesTable({ rotinas, onActivate, onExecutar, onEdit }) {
  const [searchText, setSearchText] = useState('');
  const [filterType, setFilterType] = useState(null);
  
  // Filtrar rotinas
  const filteredRotinas = rotinas.filter(rotina => {
    const matchesSearch = searchText === '' || 
      rotina.nome.toLowerCase().includes(searchText.toLowerCase()) ||
      rotina.nome_exibicao.toLowerCase().includes(searchText.toLowerCase());
      
    const matchesType = !filterType || rotina.tipo_execucao === filterType;
    
    return matchesSearch && matchesType;
  });

  const columns = [
    {
      title: 'Ativo',
      dataIndex: 'executar',
      key: 'executar',
      render: (executar, record) => (
        <Switch 
          checked={executar} 
          onChange={(checked) => onActivate(record.id, checked)}
        />
      ),
      width: '80px'
    },
    {
      title: 'Nome',
      dataIndex: 'nome_exibicao',
      key: 'nome_exibicao',
      sorter: (a, b) => a.nome_exibicao.localeCompare(b.nome_exibicao)
    },
    {
      title: 'Tipo',
      dataIndex: 'tipo_rotina',
      key: 'tipo_rotina',
      filters: [
        { text: 'Download Arquivo', value: 'DOWNLOAD_ARQUIVO' },
        { text: 'Carga Arquivo', value: 'CARGA_ARQUIVO' },
        { text: 'Chamada API', value: 'CHAMADA_API' },
        { text: 'Execução Script', value: 'EXECUCAO_SCRIPT' }
      ],
      onFilter: (value, record) => record.tipo_rotina === value
    },
    {
      title: 'Arquivo/Endpoint',
      key: 'arquivo_endpoint',
      render: (_, record) => {
        if (record.mascara_arquivo) {
          return record.mascara_arquivo;
        } else if (record.endpoint_url) {
          return record.endpoint_url;
        }
        return '-';
      }
    },
    {
      title: 'Horário',
      dataIndex: 'horario_execucao',
      key: 'horario_execucao',
      sorter: (a, b) => a.horario_execucao.localeCompare(b.horario_execucao)
    },
    {
      title: 'Prioridade',
      dataIndex: 'prioridade',
      key: 'prioridade',
      sorter: (a, b) => a.prioridade - b.prioridade
    },
    {
      title: 'Ações',
      key: 'acoes',
      render: (_, record) => (
        <>
          <Button 
            icon={<PlayCircleOutlined />} 
            onClick={() => onExecutar(record.id)}
            title="Executar agora"
            disabled={!record.executar}
          />
          <Button 
            icon={<EditOutlined />}
            onClick={() => onEdit && onEdit(record)}
            title="Editar rotina"
            style={{ marginLeft: '8px' }}
          />
        </>
      )
    }
  ];

  return (
    <div className="routines-table">
      <h2>Rotinas Cadastradas</h2>
      
      <div className="table-filters">
        <Input
          placeholder="Buscar rotina..."
          prefix={<SearchOutlined />}
          value={searchText}
          onChange={e => setSearchText(e.target.value)}
          style={{ width: 200, marginRight: 16 }}
        />
        
        <Select
          placeholder="Filtrar por tipo"
          allowClear
          style={{ width: 200 }}
          onChange={value => setFilterType(value)}
          options={[
            { value: 'DIARIO', label: 'Diário' },
            { value: 'MENSAL', label: 'Mensal' },
            { value: 'EVENTUAL', label: 'Eventual' },
            { value: 'CICLICO', label: 'Cíclico' }
          ]}
        />
      </div>
      
      <Table 
        dataSource={filteredRotinas}
        columns={columns}
        rowKey="id"
        pagination={{ pageSize: 10 }}
      />
    </div>
  );
}

export default RoutinesTable;
```

#### 3.3 Tabela de Fila

```jsx
// src/components/scheduler/QueueTable.jsx
import React, { useState } from 'react';
import { Table, Tag, Button, Select } from 'antd';
import { PlayCircleOutlined, StopOutlined, InfoCircleOutlined } from '@ant-design/icons';

function QueueTable({ items, onExecutar, onCancelar, onDetalhes }) {
  const [statusFilter, setStatusFilter] = useState('PENDENTE');
  
  // Mapear status para cores
  const getStatusTag = (status) => {
    const statusMap = {
      'PENDENTE': { color: 'gold', icon: '⏳' },
      'EXECUTANDO': { color: 'blue', icon: '⚡' },
      'CONCLUIDA': { color: 'green', icon: '✅' },
      'ERRO': { color: 'red', icon: '❌' },
      'CANCELADA': { color: 'gray', icon: '❌' },
      'RECOVERY': { color: 'purple', icon: '🔄' }
    };
    
    const { color, icon } = statusMap[status] || { color: 'default', icon: '?' };
    return (
      <Tag color={color}>
        {icon} {status}
      </Tag>
    );
  };

  const columns = [
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: status => getStatusTag(status),
      filters: [
        { text: 'Pendente', value: 'PENDENTE' },
        { text: 'Executando', value: 'EXECUTANDO' },
        { text: 'Concluída', value: 'CONCLUIDA' },
        { text: 'Erro', value: 'ERRO' },
        { text: 'Cancelada', value: 'CANCELADA' },
        { text: 'Recovery', value: 'RECOVERY' }
      ],
      onFilter: (value, record) => record.status === value
    },
    {
      title: 'Rotina',
      dataIndex: 'nome_rotina',
      key: 'nome_rotina'
    },
    {
      title: 'Horário',
      dataIndex: 'horario_execucao',
      key: 'horario_execucao',
      render: (horario) => horario.substring(0, 5),
      sorter: (a, b) => a.horario_execucao.localeCompare(b.horario_execucao)
    },
    {
      title: 'Prioridade',
      dataIndex: 'prioridade',
      key: 'prioridade',
      sorter: (a, b) => a.prioridade - b.prioridade
    },
    {
      title: 'Ações',
      key: 'acoes',
      render: (_, record) => {
        if (record.status === 'PENDENTE') {
          return (
            <>
              <Button 
                icon={<PlayCircleOutlined />} 
                onClick={() => onExecutar && onExecutar(record.id)}
                title="Executar agora"
              />
              <Button 
                icon={<StopOutlined />} 
                onClick={() => onCancelar && onCancelar(record.id)}
                title="Cancelar item"
                style={{ marginLeft: '8px' }}
                danger
              />
              <Button 
                icon={<InfoCircleOutlined />} 
                onClick={() => onDetalhes && onDetalhes(record)}
                title="Detalhes"
                style={{ marginLeft: '8px' }}
              />
            </>
          );
        }
        
        // Para outros status
        const actions = [];
        
        // Repetir para CONCLUIDA ou ERRO
        if (['CONCLUIDA', 'ERRO', 'CANCELADA'].includes(record.status)) {
          actions.push(
            <Button 
              key="repetir"
              onClick={() => onExecutar && onExecutar(record.scheduler_rotina)}
              title="Repetir execução"
              icon={<PlayCircleOutlined />}
            />
          );
        }
        
        // Detalhes para todos
        actions.push(
          <Button 
            key="detalhes"
            icon={<InfoCircleOutlined />} 
            onClick={() => onDetalhes && onDetalhes(record)}
            title="Detalhes"
            style={{ marginLeft: '8px' }}
          />
        );
        
        return actions;
      }
    }
  ];

  return (
    <div className="queue-table">
      <div className="table-header">
        <h2>Fila de Execução</h2>
        
        <Select
          value={statusFilter}
          onChange={setStatusFilter}
          options={[
            { value: 'PENDENTE', label: 'Pendentes' },
            { value: 'CONCLUIDA', label: 'Concluídas' },
            { value: 'ERRO', label: 'Erros' },
            { value: 'TODOS', label: 'Todos' }
          ]}
          style={{ width: 150 }}
        />
      </div>
      
      <Table 
        dataSource={statusFilter === 'TODOS' 
          ? items 
          : items.filter(item => item.status === statusFilter)
        }
        columns={columns}
        rowKey="id"
        pagination={{ pageSize: 10 }}
      />
    </div>
  );
}

export default QueueTable;
```

#### 3.4 Painel de Status

```jsx
// src/components/scheduler/StatusPanel.jsx
import React from 'react';
import { Card, Statistic, Row, Col, Badge } from 'antd';
import { ClockCircleOutlined, FileOutlined, CheckCircleOutlined, ExclamationCircleOutlined } from '@ant-design/icons';

function StatusPanel({ status, monitor }) {
  if (!status || !monitor) {
    return <div>Carregando informações...</div>;
  }
  
  return (
    <Card title="Status do Sistema">
      <Row gutter={16}>
        <Col span={12}>
          <Statistic
            title="Monitor"
            value={monitor.monitor.ativo ? "ATIVO" : "INATIVO"}
            valueStyle={{ color: monitor.monitor.ativo ? '#52c41a' : '#cf1322' }}
            prefix={
              <Badge 
                status={monitor.monitor.ativo ? "success" : "error"} 
                style={{ marginRight: 8 }}
              />
            }
          />
        </Col>
        <Col span={12}>
          <Statistic
            title="Última Carga"
            value={monitor.monitor.ultima_renovacao_diaria 
              ? new Date(monitor.monitor.ultima_renovacao_diaria).toLocaleTimeString('pt-BR', { 
                  hour: '2-digit', 
                  minute: '2-digit',
                  day: '2-digit',
                  month: '2-digit'
                })
              : "Nunca"
            }
            prefix={<ClockCircleOutlined />}
          />
        </Col>
      </Row>
      <Row gutter={16} style={{ marginTop: 16 }}>
        <Col span={8}>
          <Statistic
            title="Total na Fila"
            value={status.estatisticas.total}
            prefix={<FileOutlined />}
          />
        </Col>
        <Col span={8}>
          <Statistic
            title="Pendentes"
            value={status.estatisticas.pendentes}
            prefix={<ClockCircleOutlined />}
          />
        </Col>
        <Col span={8}>
          <Statistic
            title="Erros"
            value={status.estatisticas.erros}
            valueStyle={{ color: status.estatisticas.erros > 0 ? '#cf1322' : '#52c41a' }}
            prefix={<ExclamationCircleOutlined />}
          />
        </Col>
      </Row>
      {status.proximas_execucoes && status.proximas_execucoes.length > 0 && (
        <div className="next-execution" style={{ marginTop: 16 }}>
          <h4>Próxima Execução:</h4>
          <p>
            {status.proximas_execucoes[0].rotina} - {status.proximas_execucoes[0].horario}
          </p>
        </div>
      )}
    </Card>
  );
}

export default StatusPanel;
```

#### 3.5 Painel de Ações

```jsx
// src/components/scheduler/ActionsPanel.jsx
import React from 'react';
import { Card, Button, Space } from 'antd';
import { 
  PlayCircleOutlined, 
  ReloadOutlined, 
  SearchOutlined, 
  FileSearchOutlined 
} from '@ant-design/icons';

function ActionsPanel({ 
  onForcarCargaDiaria, 
  onExecutarScheduler, 
  onVerificarMonitor,
  onVisualizarLogs
}) {
  return (
    <Card title="Ações Rápidas">
      <Space direction="vertical" style={{ width: '100%' }}>
        <Button 
          type="primary" 
          icon={<ReloadOutlined />} 
          onClick={onForcarCargaDiaria}
          block
        >
          Forçar Carga de Rotinas
        </Button>
        
        <Button 
          icon={<PlayCircleOutlined />} 
          onClick={onExecutarScheduler}
          block
        >
          Executar Scheduler
        </Button>
        
        <Button 
          icon={<SearchOutlined />} 
          onClick={onVerificarMonitor}
          block
        >
          Verificar Monitor
        </Button>
        
        <Button 
          icon={<FileSearchOutlined />} 
          onClick={onVisualizarLogs}
          block
        >
          Visualizar Logs
        </Button>
      </Space>
    </Card>
  );
}

export default ActionsPanel;
```

## 🎨 Estrutura da Aplicação React

```
src/
  components/
    scheduler/
      Dashboard.jsx         # Página principal do scheduler
      StatusPanel.jsx       # Status do sistema
      ActionsPanel.jsx      # Ações rápidas
      RoutinesTable.jsx     # Tabela de rotinas
      QueueTable.jsx        # Tabela de fila
      EditRoutineModal.jsx  # Modal para editar rotina
      LogsModal.jsx         # Modal para visualizar logs
  services/
    api.js                 # Cliente Axios
    schedulerService.js    # Serviço para APIs do scheduler
  App.js                   # Componente principal
  index.js                 # Ponto de entrada
```

## 🔌 Considerações Finais

Os componentes acima ilustram como integrar o frontend React com as APIs de scheduler. Todos os endpoints necessários foram implementados no backend e estão prontos para uso. A estrutura proposta é modular e pode ser facilmente adaptada para sua aplicação existente.

Para melhorar a experiência do usuário, recomenda-se:

1. Implementar feedback visual para ações (toasts ou notificações)
2. Adicionar confirmações antes de ações críticas
3. Implementar tratamento de erros robusto
4. Adicionar paginação nos logs e nas tabelas grandes
5. Implementar polling inteligente para atualizações automáticas

Todas as APIs necessárias estão disponíveis e funcionando corretamente, como testado no ambiente local.
