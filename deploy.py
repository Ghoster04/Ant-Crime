#!/usr/bin/env python3
"""
Script de Deploy - AntiCrime 04
Configura e inicializa o sistema para produção
"""
import sys
import os
from pathlib import Path

def check_dependencies():
    """Verifica se todas as dependências estão instaladas"""
    print("🔍 Verificando dependências...")
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'sqlalchemy',
        'pymysql',
        'cryptography',
        'pydantic',
        'pyjwt',
        'passlib',
        'python-multipart'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️ Pacotes faltando: {', '.join(missing_packages)}")
        print("Execute: pip install -r requirements.txt")
        return False
    
    print("✅ Todas as dependências estão instaladas!")
    return True

def test_database_connection():
    """Testa a conexão com o banco de dados"""
    print("\n🗄️ Testando conexão com banco de dados...")
    
    try:
        from test_mysql_connection import test_mysql_connection, test_table_creation
        
        if test_mysql_connection():
            if test_table_creation():
                print("✅ Banco de dados configurado corretamente!")
                return True
            else:
                print("❌ Problema na criação das tabelas")
                return False
        else:
            print("❌ Falha na conexão com banco de dados")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar banco: {e}")
        return False

def create_super_admin():
    """Cria o super administrador inicial"""
    print("\n👤 Criando super administrador...")
    
    try:
        from database import create_superuser
        create_superuser()
        print("✅ Super administrador criado!")
        print("📧 Email: admin@prm.gov.mz")
        print("🔑 Senha: admin123")
        print("⚠️ ALTERE A SENHA EM PRODUÇÃO!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar super admin: {e}")
        return False

def check_uploads_directory():
    """Verifica/cria diretório de uploads"""
    print("\n📁 Verificando diretório de uploads...")
    
    try:
        from config import settings
        upload_dir = Path(settings.UPLOAD_DIR)
        
        if not upload_dir.exists():
            upload_dir.mkdir(exist_ok=True)
            print(f"✅ Diretório criado: {upload_dir}")
        else:
            print(f"✅ Diretório existe: {upload_dir}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar uploads: {e}")
        return False

def test_api_health():
    """Testa se a API está funcionando"""
    print("\n🏥 Testando saúde da API...")
    
    try:
        import requests
        import time
        import subprocess
        import threading
        
        # Iniciar servidor em thread separada
        def start_server():
            os.system("python main.py")
        
        server_thread = threading.Thread(target=start_server, daemon=True)
        server_thread.start()
        
        # Aguardar servidor iniciar
        time.sleep(5)
        
        # Testar endpoint de saúde
        response = requests.get("http://localhost:8000/health", timeout=10)
        
        if response.status_code == 200:
            print("✅ API está funcionando!")
            return True
        else:
            print(f"❌ API retornou status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar API: {e}")
        return False

def main():
    """Função principal de deploy"""
    print("🚀 AntiCrime 04 - Deploy de Produção")
    print("=" * 50)
    
    # Verificar dependências
    if not check_dependencies():
        sys.exit(1)
    
    # Testar banco de dados
    if not test_database_connection():
        print("\n💥 Falha na configuração do banco de dados")
        sys.exit(1)
    
    # Criar super admin
    if not create_super_admin():
        print("\n💥 Falha na criação do super administrador")
        sys.exit(1)
    
    # Verificar diretório de uploads
    if not check_uploads_directory():
        print("\n💥 Falha na configuração de uploads")
        sys.exit(1)
    
    print("\n🎉 Deploy concluído com sucesso!")
    print("\n📋 Próximos passos:")
    print("1. Execute: python main.py")
    print("2. Acesse: http://localhost:8000/docs")
    print("3. Teste o login com admin@prm.gov.mz / admin123")
    print("4. Altere a senha padrão em produção!")
    
    print("\n🔗 URLs importantes:")
    print("- API Docs: http://localhost:8000/docs")
    print("- Health Check: http://localhost:8000/health")
    print("- Frontend: Configure para usar http://localhost:8000")

if __name__ == "__main__":
    main()
