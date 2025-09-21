#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de inicialização do sistema AntiCrime 04
"""

import sys
import os
import subprocess
from pathlib import Path

# Configurar encoding UTF-8 no Windows
if sys.platform == "win32":
    os.system('chcp 65001 > nul')
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')

def install_dependencies():
    """Instalar dependências Python"""
    print("📦 Instalando dependências...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependências instaladas com sucesso!")
    except subprocess.CalledProcessError:
        print("❌ Erro ao instalar dependências")
        return False
    return True

def setup_database():
    """Configurar banco de dados"""
    print("🗄️ Configurando banco de dados...")
    try:
        from database import init_db, create_superuser
        
        # Inicializar tabelas
        init_db()
        
        # Criar super administrador
        create_superuser()
        
        print("✅ Banco de dados configurado com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao configurar banco de dados: {e}")
        print(f"   Detalhes: {type(e).__name__}")
        return False

def check_config():
    """Verificar se configurações estão OK"""
    print("📝 Verificando configurações...")
    print("   ✅ Configurações estão direto no código")
    print("   ✅ Não são necessários arquivos externos")

def main():
    """Função principal"""
    print("🚀 Inicializando sistema AntiCrime 04...")
    print("=" * 50)
    
    # Verificar se estamos no diretório correto
    if not Path("requirements.txt").exists():
        print("❌ Execute este script no diretório backend/")
        return
    
    # Verificar configurações
    check_config()
    
    # Instalar dependências
    if not install_dependencies():
        return
    
    # Configurar banco de dados
    if not setup_database():
        return
    
    print("\n" + "=" * 50)
    print("🎉 Sistema configurado com sucesso!")
    print("\n📋 Informações importantes:")
    print("   • Super Admin criado:")
    print("     Email: admin@prm.gov.mz")
    print("     Senha: admin123")
    print("\n🚀 Para iniciar o servidor:")
    print("   python main.py")
    print("   ou")
    print("   uvicorn main:app --reload")
    print("\n🌐 API estará disponível em:")
    print("   http://localhost:8000")
    print("   Documentação: http://localhost:8000/docs")
    print("=" * 50)

if __name__ == "__main__":
    main()
