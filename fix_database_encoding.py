#!/usr/bin/env python
"""
Script para corrigir problemas de encoding do banco de dados PostgreSQL
"""
import os
import sys
import django
from django.conf import settings
from django.db import connection
from django.core.management import execute_from_command_line

def setup_django():
    """Configura o Django"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'servicos.settings')
    django.setup()

def fix_database_encoding():
    """Corrige problemas de encoding do banco de dados"""
    try:
        print("🔧 Corrigindo configurações de encoding do banco de dados...")
        
        # Fechar conexão existente se houver
        if hasattr(connection, 'close'):
            connection.close()
            print("✅ Conexão anterior fechada")
        
        # Testar nova conexão
        with connection.cursor() as cursor:
            # Verificar encoding atual
            cursor.execute("SHOW client_encoding;")
            encoding = cursor.fetchone()[0]
            print(f"📊 Encoding atual do cliente: {encoding}")
            
            # Definir encoding UTF8 se necessário
            cursor.execute("SET client_encoding TO 'UTF8';")
            print("✅ Encoding do cliente definido para UTF8")
            
            # Verificar timezone
            cursor.execute("SHOW timezone;")
            timezone = cursor.fetchone()[0]
            print(f"🕒 Timezone atual: {timezone}")
            
            # Testar consulta simples
            cursor.execute("SELECT 1;")
            result = cursor.fetchone()[0]
            print(f"✅ Teste de consulta bem-sucedido: {result}")
            
        print("🎉 Configurações de encoding corrigidas com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao corrigir encoding: {str(e)}")
        print(f"💡 Detalhes: {type(e).__name__}")
        return False

def main():
    """Função principal"""
    print("🚀 Iniciando correção de encoding do banco de dados...")
    
    try:
        setup_django()
        print("✅ Django configurado")
        
        if fix_database_encoding():
            print("\n🎊 Correção concluída com sucesso!")
            print("💡 Agora você pode executar: python manage.py runserver")
        else:
            print("\n❌ Falha na correção")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Erro geral: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()