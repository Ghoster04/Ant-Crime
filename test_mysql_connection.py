#!/usr/bin/env python3
"""
Script para testar a conexão com o banco MySQL do Railway
"""
import sys
import os
from sqlalchemy import create_engine, text
from config import settings

def test_mysql_connection():
    """Testa a conexão com o MySQL"""
    print("🔍 Testando conexão com banco de dados...")
    print(f"Host: {settings.MYSQL_HOST}")
    print(f"Port: {settings.MYSQL_PORT}")
    print(f"Database: {settings.MYSQL_DATABASE}")
    print(f"User: {settings.MYSQL_USER}")
    print(f"URL: {settings.database_url}")
    print(f"Ambiente Railway: {settings._is_railway_environment()}")
    print(f"Usar DB Local: {settings.USE_LOCAL_DB}")
    print(f"Debug: {settings.DEBUG}")
    print("-" * 50)
    
    try:
        # Criar engine de teste
        engine = create_engine(
            settings.database_url,
            echo=True,
            connect_args=settings.connect_args,
            pool_pre_ping=True
        )
        
        # Testar conexão
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1 as test"))
            test_value = result.fetchone()[0]
            
            if test_value == 1:
                print("✅ Conexão com MySQL estabelecida com sucesso!")
                
                # Testar versão do MySQL
                version_result = connection.execute(text("SELECT VERSION() as version"))
                mysql_version = version_result.fetchone()[0]
                print(f"📊 Versão do MySQL: {mysql_version}")
                
                # Testar charset
                charset_result = connection.execute(text("SELECT @@character_set_database as charset"))
                charset = charset_result.fetchone()[0]
                print(f"📝 Charset do banco: {charset}")
                
                return True
            else:
                print("❌ Teste de conexão falhou")
                return False
                
    except Exception as e:
        print(f"❌ Erro ao conectar com MySQL: {e}")
        print(f"Tipo do erro: {type(e).__name__}")
        return False

def test_table_creation():
    """Testa a criação de tabelas"""
    print("\n🏗️ Testando criação de tabelas...")
    
    try:
        from database import engine, init_db
        
        # Tentar criar tabelas
        init_db()
        print("✅ Tabelas criadas com sucesso!")
        
        # Verificar se as tabelas foram criadas
        with engine.connect() as connection:
            tables_result = connection.execute(text("SHOW TABLES"))
            tables = [row[0] for row in tables_result.fetchall()]
            
            print(f"📋 Tabelas encontradas: {tables}")
            
            expected_tables = ['admins', 'usuarios', 'dispositivos', 'emergencias', 'pings_dispositivos', 'logs_sistema', 'configuracoes_sistema']
            
            for table in expected_tables:
                if table in tables:
                    print(f"  ✅ {table}")
                else:
                    print(f"  ❌ {table} - NÃO ENCONTRADA")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 AntiCrime 04 - Teste de Conexão MySQL")
    print("=" * 50)
    
    # Testar conexão
    connection_ok = test_mysql_connection()
    
    if connection_ok:
        # Testar criação de tabelas
        tables_ok = test_table_creation()
        
        if tables_ok:
            print("\n🎉 Todos os testes passaram! MySQL está configurado corretamente.")
            sys.exit(0)
        else:
            print("\n⚠️ Conexão OK, mas houve problemas na criação das tabelas.")
            sys.exit(1)
    else:
        print("\n💥 Falha na conexão com MySQL. Verifique as credenciais.")
        sys.exit(1)

if __name__ == "__main__":
    main()
