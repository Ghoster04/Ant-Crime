#!/usr/bin/env python3
"""
Script de inicialização simples para Railway
"""
import os
import sys
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Inicialização rápida"""
    logger.info("🚀 Iniciando AntiCrime 04 API...")
    
    # Verificar porta
    port = int(os.getenv("PORT", "8000"))
    logger.info(f"🌐 Porta: {port}")
    
    # Verificar se estamos no Railway
    if os.getenv("RAILWAY_ENVIRONMENT"):
        logger.info("✅ Executando no Railway")
    else:
        logger.info("🏠 Executando localmente")
    
    # Iniciar servidor rapidamente
    try:
        import uvicorn
        from main import app
        
        logger.info("🌐 Iniciando servidor...")
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            log_level="info",
            access_log=True,
            timeout_keep_alive=30,
            timeout_graceful_shutdown=30
        )
        
    except Exception as e:
        logger.error(f"💥 Erro ao iniciar servidor: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
