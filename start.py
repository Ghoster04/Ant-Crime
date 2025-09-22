#!/usr/bin/env python3
"""
Script de inicialização para Railway
"""
import os
import sys
import time
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_environment():
    """Verificar variáveis de ambiente"""
    logger.info("🔍 Verificando ambiente...")
    
    # Verificar se estamos no Railway
    railway_env = os.getenv("RAILWAY_ENVIRONMENT")
    railway_project = os.getenv("RAILWAY_PROJECT_ID")
    
    if railway_env:
        logger.info(f"✅ Executando no Railway - Ambiente: {railway_env}")
        logger.info(f"✅ Project ID: {railway_project}")
    else:
        logger.info("🏠 Executando localmente")
    
    # Verificar porta
    port = os.getenv("PORT", "8000")
    logger.info(f"🌐 Porta configurada: {port}")
    
    return True

def check_dependencies():
    """Verificar dependências críticas"""
    logger.info("📦 Verificando dependências...")
    
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        import pymysql
        logger.info("✅ Dependências principais OK")
        return True
    except ImportError as e:
        logger.error(f"❌ Dependência faltando: {e}")
        return False

def check_database_connection():
    """Verificar conexão com banco de dados"""
    logger.info("🗄️ Verificando conexão com banco...")
    
    try:
        from config import settings
        logger.info(f"📊 URL do banco: {settings.database_url}")
        
        # Tentar conectar
        from database import engine
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            logger.info("✅ Conexão com banco OK")
            return True
            
    except Exception as e:
        logger.error(f"❌ Erro na conexão com banco: {e}")
        logger.info("⚠️ Continuando sem banco...")
        return False

def create_upload_directory():
    """Criar diretório de uploads"""
    logger.info("📁 Verificando diretório de uploads...")
    
    try:
        upload_dir = Path("uploads")
        upload_dir.mkdir(exist_ok=True)
        logger.info(f"✅ Diretório de uploads: {upload_dir.absolute()}")
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao criar diretório de uploads: {e}")
        return False

def main():
    """Função principal"""
    logger.info("🚀 Iniciando AntiCrime 04 API...")
    logger.info("=" * 60)
    
    # Verificações
    checks = [
        ("Ambiente", check_environment),
        ("Dependências", check_dependencies),
        ("Banco de dados", check_database_connection),
        ("Diretório uploads", create_upload_directory)
    ]
    
    for name, check_func in checks:
        try:
            if not check_func():
                logger.warning(f"⚠️ Verificação {name} falhou, mas continuando...")
        except Exception as e:
            logger.error(f"❌ Erro na verificação {name}: {e}")
    
    logger.info("=" * 60)
    logger.info("🎉 Inicialização concluída!")
    
    # Iniciar servidor
    try:
        import uvicorn
        from main import app
        
        port = int(os.getenv("PORT", "8000"))
        host = "0.0.0.0"
        
        logger.info(f"🌐 Iniciando servidor em {host}:{port}")
        
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="info",
            access_log=True
        )
        
    except Exception as e:
        logger.error(f"💥 Erro ao iniciar servidor: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
