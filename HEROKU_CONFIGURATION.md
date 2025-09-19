# Configuração da Aplicação no Heroku

Este documento contém instruções para a configuração correta da aplicação no ambiente Heroku, incluindo as atualizações relacionadas ao funcionamento das rotinas automáticas.

## Variáveis de Ambiente Necessárias

Para garantir o funcionamento correto da aplicação no ambiente Heroku, as seguintes variáveis de ambiente devem ser configuradas:

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `SECRET_KEY` | Chave secreta Django | (valor longo e aleatório) |
| `DEBUG` | Modo debug (recomendado: False em produção) | False |
| `DATABASE_URL` | URL de conexão com o banco PostgreSQL | (fornecido pelo Heroku) |
| `BASE_URL` | URL base para chamadas internas da API | https://seu-app.herokuapp.com |

## Configuração da Variável BASE_URL

A variável `BASE_URL` é essencial para o funcionamento correto das rotinas automáticas. Esta variável deve conter a URL completa da aplicação implantada no Heroku, sem barra no final.

Para configurar esta variável:

1. Acesse o painel de controle do Heroku para sua aplicação
2. Vá para a seção "Settings" > "Config Vars"
3. Adicione uma nova variável com o nome `BASE_URL` e o valor `https://seu-app.herokuapp.com` (substitua pelo nome real da sua aplicação)

## Atualização das URLs de Rotinas Existentes

Se sua aplicação já estava implantada e tem rotinas configuradas no banco de dados, é necessário atualizar as URLs das rotinas para usar a nova variável BASE_URL. Para isso:

1. Execute o seguinte comando após implantar a nova versão:

```
heroku run python manage.py atualizar_urls_scheduler -a seu-app
```

## Validando a Configuração

Para verificar se a configuração está correta:

1. Verifique os logs da aplicação:
```
heroku logs --tail -a seu-app
```

2. Procure por mensagens relacionadas à execução de rotinas agendadas e verifique se não há erros relacionados a "Connection refused" ou "Max retries exceeded".

## Solução de Problemas Comuns

### Erro "Connection refused" nos Logs

Se você encontrar erros como `HTTPConnectionPool(host='127.0.0.1', port=8000): Max retries exceeded with url: /api/download_b3/ (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x7f87ae735e50>: Failed to establish a new connection: [Errno 111] Connection refused'))`:

1. Verifique se a variável `BASE_URL` está configurada corretamente no Heroku
2. Execute o comando `atualizar_urls_scheduler` para garantir que todas as rotinas estejam usando a URL correta
3. Reinicie a aplicação com `heroku restart -a seu-app`

### Rotinas Não Executam

Se as rotinas não estão sendo executadas conforme esperado:

1. Verifique os logs para identificar possíveis erros
2. Confirme se o scheduler está rodando (`heroku ps -a seu-app`)
3. Verifique se o fuso horário está configurado corretamente (a aplicação usa o fuso horário 'America/Sao_Paulo')

## Histórico de Atualizações

**19/09/2025** - Correção do problema de execução de rotinas no Heroku:
- Adicionada variável `BASE_URL` para substituir URLs fixas com 127.0.0.1
- Atualizado o inicializador de scheduler para usar a variável BASE_URL
- Adicionado comando para atualizar URLs de rotinas existentes no banco de dados