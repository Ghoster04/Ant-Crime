#!/usr/bin/env python3
"""
Script de debug para testar conexão MySQL
"""
import sys
import os
from sqlalchemy import create_engine, text

def test_mysql_connection():
    """Testar conexão MySQL com diferentes configurações"""
    print("🔍 Testando conexão MySQL...")
    
    # Configurações MySQL
    mysql_configs = [
        {
            "name": "Railway Interno",
            "url": "mysql+pymysql://root:qmWIuOIpYLNOJcSdpKumbxNcQJPmalAO@mysql.railway.internal:3306/railway"
        },
        {
            "name": "Railway Externo",
            "url": "mysql+pymysql://root:qmWIuOIpYLNOJcSdpKumbxNcQJPmalAO@turntable.proxy.rlwy.net:28897/railway"
        }
    ]
    
    for config in mysql_configs:
        print(f"\n📊 Testando: {config['name']}")
        print(f"URL: {config['url']}")
        
        try:
            # Configurações robustas
            engine = create_engine(
                config['url'],
                connect_args={
                    "charset": "utf8mb4",
                    "autocommit": False,
                    "connect_timeout": 10,
                    "read_timeout": 10,
                    "write_timeout": 10,
                },
                pool_pre_ping=True,
                pool_recycle=300,
                pool_size=2,
                max_overflow=5,
                pool_timeout=30,
                echo=False
            )
            
            # Testar conexão
            with engine.connect() as conn:
                # Teste básico
                result = conn.execute(text("SELECT 1 as test"))
                test_value = result.fetchone()[0]
                
                if test_value == 1:
                    print("✅ Conexão básica OK")
                    
                    # Teste de versão
                    version_result = conn.execute(text("SELECT VERSION() as version"))
                    mysql_version = version_result.fetchone()[0]
                    print(f"📊 Versão MySQL: {mysql_version}")
                    
                    # Teste de charset
                    charset_result = conn.execute(text("SELECT @@character_set_database as charset"))
                    charset = charset_result.fetchone()[0]
                    print(f"📝 Charset: {charset}")
                    
                    print(f"🎉 {config['name']} - SUCESSO!")
                    return config['url']
                else:
                    print(f"❌ {config['name']} - Teste básico falhou")
                    
        except Exception as e:
            print(f"❌ {config['name']} - Erro: {e}")
            print(f"   Tipo: {type(e).__name__}")
    
    print("\n💥 Nenhuma conexão funcionou!")
    return None

def test_with_config():
    """Testar usando configurações do config.py"""
    print("\n🔧 Testando com config.py...")
    
    try:
        from config import settings
        
        print(f"Ambiente Railway: {settings._is_railway_environment()}")
        print(f"URL do banco: {settings.database_url}")
        
        engine = create_engine(
            settings.database_url,
            connect_args={
                "charset": "utf8mb4",
                "autocommit": False,
                "connect_timeout": 10,
                "read_timeout": 10,
                "write_timeout": 10,
            },
            pool_pre_ping=True,
            pool_recycle=300,
            pool_size=2,
            max_overflow=5,
            pool_timeout=30,
            echo=False
        )
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Config.py - Conexão OK!")
            return True
            
    except Exception as e:
        print(f"❌ Config.py - Erro: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 Debug MySQL - AntiCrime 04")
    print("=" * 50)
    
    # Testar configurações diretas
    working_url = test_mysql_connection()
    
    # Testar com config.py
    config_works = test_with_config()
    
    print("\n" + "=" * 50)
    print("📋 Resultado:")
    
    if working_url:
        print(f"✅ Conexão funcionando: {working_url}")
    else:
        print("❌ Nenhuma conexão funcionou")
    
    if config_works:
        print("✅ Config.py funcionando")
    else:
        print("❌ Config.py com problemas")
    
    if working_url and config_works:
        print("\n🎉 MySQL está funcionando corretamente!")
        sys.exit(0)
    else:
        print("\n💥 Há problemas com MySQL")
        sys.exit(1)

if __name__ == "__main__":
    main()
