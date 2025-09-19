# Instruções para Corrigir o Download no Heroku

## Problema Identificado:

Os downloads no Heroku estão falhando devido a chamadas para URLs fixas com `http://127.0.0.1:8000`. Estas chamadas são rejeitadas no ambiente Heroku, pois 127.0.0.1 refere-se à própria máquina e não ao servidor web.

## Solução Implementada:

1. **Nova variável de configuração `BASE_URL`**
   - Adicionada ao settings.py para uso dinâmico das URLs
   - Em ambiente de desenvolvimento: `http://127.0.0.1:8000` (padrão)
   - Em produção (Heroku): URL completa do seu app, como `https://seu-app.herokuapp.com`

2. **Arquivos modificados:**
   - `settings.py`: Adicionada variável `BASE_URL`
   - `inicializar_scheduler.py`: Substituídas URLs fixas pela variável `BASE_URL`
   - `atualizar_urls_scheduler.py` (novo): Script para atualizar URLs existentes no banco de dados

## Passos para Aplicar no Heroku:

1. **Implante as alterações no Heroku**
   ```
   git push heroku main
   ```

2. **Configure a variável de ambiente `BASE_URL`**
   ```
   heroku config:set BASE_URL=https://seu-app.herokuapp.com -a seu-app
   ```
   (Substitua `seu-app` pelo nome real do seu aplicativo no Heroku)

3. **Execute o comando para atualizar URLs no banco de dados**
   ```
   heroku run python manage.py atualizar_urls_scheduler -a seu-app
   ```

4. **Reinicie a aplicação**
   ```
   heroku restart -a seu-app
   ```

5. **Verifique os logs para confirmar que os downloads estão funcionando**
   ```
   heroku logs --tail -a seu-app
   ```

## Verificação

Após aplicar estas alterações, você deverá ver no log do Heroku que os downloads estão sendo realizados com sucesso, sem erros de "Connection refused".