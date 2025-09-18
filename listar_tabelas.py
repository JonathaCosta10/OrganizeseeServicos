import psycopg2
import sys

def listar_tabelas_e_colunas():
    """Conecta ao banco PostgreSQL e lista todas as tabelas e suas colunas"""
    
    # Configurações do banco
    config = {
        'host': 'casrkuuedp6an1.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com',
        'port': '5432',
        'database': 'dagjgmra6bck94',
        'user': 'u71lo0hl2prk2v',
        'password': 'p7c0b8d9f79594dac5c5b95f2fc38a3208eb662cb439a00ff133de32c68f55801'
    }
    
    try:
        # Conectar ao banco
        print("🔗 Conectando ao banco PostgreSQL...")
        conn = psycopg2.connect(**config)
        cursor = conn.cursor()
        
        # Listar todas as tabelas (exceto tabelas do sistema)
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """)
        
        tabelas = cursor.fetchall()
        
        if not tabelas:
            print("❌ Nenhuma tabela encontrada no schema 'public'")
            return
        
        print(f"📊 Encontradas {len(tabelas)} tabelas:\n")
        
        # Para cada tabela, listar as colunas
        for (nome_tabela,) in tabelas:
            print(f"🔍 TABELA: {nome_tabela}")
            print("=" * (len(nome_tabela) + 10))
            
            cursor.execute("""
                SELECT 
                    column_name,
                    data_type,
                    is_nullable,
                    column_default,
                    character_maximum_length
                FROM information_schema.columns 
                WHERE table_name = %s
                ORDER BY ordinal_position;
            """, (nome_tabela,))
            
            colunas = cursor.fetchall()
            
            for coluna in colunas:
                nome_col, tipo_dados, permite_null, default, max_length = coluna
                
                # Formatear informações da coluna
                info_coluna = f"  📝 {nome_col} ({tipo_dados}"
                
                if max_length:
                    info_coluna += f"({max_length})"
                
                info_coluna += ")"
                
                if permite_null == 'NO':
                    info_coluna += " [NOT NULL]"
                
                if default:
                    info_coluna += f" [DEFAULT: {default}]"
                
                print(info_coluna)
            
            print()  # Linha em branco entre tabelas
        
        cursor.close()
        conn.close()
        print("✅ Conexão encerrada com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco: {str(e)}")
        return

if __name__ == "__main__":
    listar_tabelas_e_colunas()
