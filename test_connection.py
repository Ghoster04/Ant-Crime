#!/usr/bin/env python3
"""
Teste rápido de conexão com MySQL
"""
from config import settings

def main():
    print("🔍 Configuração atual:")
    print(f"URL do banco: {settings.database_url}")
    print(f"Ambiente Railway: {settings._is_railway_environment()}")
    print(f"Usar DB Local: {settings.USE_LOCAL_DB}")
    print(f"Debug: {settings.DEBUG}")
    
    print("\n🚀 Para testar a conexão, execute:")
    print("python test_mysql_connection.py")

if __name__ == "__main__":
    main()
