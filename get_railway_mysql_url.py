#!/usr/bin/env python3
"""
Script para obter a URL externa do MySQL do Railway
"""
import requests
import json

def get_railway_mysql_url():
    """
    Tenta obter a URL externa do MySQL do Railway
    Você precisa configurar manualmente no painel do Railway
    """
    print("🔍 Configuração do MySQL Railway")
    print("=" * 50)
    
    print("📋 Para usar MySQL em desenvolvimento local, você precisa:")
    print("1. Acessar o painel do Railway (https://railway.app)")
    print("2. Ir para o seu projeto")
    print("3. Selecionar o serviço MySQL")
    print("4. Na aba 'Connect', copiar a URL externa")
    print("5. Configurar as variáveis de ambiente")
    
    print("\n🔧 Configuração manual:")
    print("export MYSQL_EXTERNAL_HOST=containers-us-west-xxx.railway.app")
    print("export MYSQL_EXTERNAL_PORT=3306")
    
    print("\n💡 Ou edite o arquivo config.py:")
    print("MYSQL_EXTERNAL_HOST = 'sua-url-aqui.railway.app'")
    
    print("\n🚀 Alternativa: Usar SQLite para desenvolvimento")
    print("export USE_LOCAL_DB=True")
    print("export DEBUG=True")
    
    print("\n📝 Exemplo de configuração completa:")
    print("""
# Para desenvolvimento local com SQLite
USE_LOCAL_DB=True
DEBUG=True

# Para desenvolvimento local com MySQL externo
MYSQL_EXTERNAL_HOST=containers-us-west-xxx.railway.app
MYSQL_EXTERNAL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=qmWIuOIpYLNOJcSdpKumbxNcQJPmalAO
MYSQL_DATABASE=railway
""")

if __name__ == "__main__":
    get_railway_mysql_url()
