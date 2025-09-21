#!/usr/bin/env python3
"""
Script para migração do banco de dados
"""

from database import engine, get_db
from models import Base, PingDispositivo, Dispositivo, Usuario, Admin, Emergencia, LogSistema
from sqlalchemy import text
import sys

def create_new_tables():
    """Criar apenas novas tabelas sem afetar as existentes"""
    try:
        print("🔄 Criando novas tabelas...")
        Base.metadata.create_all(bind=engine)
        print("✅ Novas tabelas criadas com sucesso!")
        
        # Verificar se a tabela pings_dispositivos foi criada
        db = next(get_db())
        result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='pings_dispositivos'")).fetchone()
        if result:
            print("✅ Tabela 'pings_dispositivos' confirmada no banco!")
        else:
            print("❌ Tabela 'pings_dispositivos' não foi encontrada!")
        db.close()
        
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        sys.exit(1)

def recreate_all_tables():
    """CUIDADO: Apaga TODOS os dados e recria todas as tabelas"""
    confirm = input("⚠️  ATENÇÃO: Isso vai APAGAR TODOS os dados! Digite 'CONFIRMAR' para continuar: ")
    if confirm != "CONFIRMAR":
        print("❌ Operação cancelada.")
        return
    
    try:
        print("🔄 Apagando todas as tabelas...")
        Base.metadata.drop_all(bind=engine)
        print("🔄 Recriando todas as tabelas...")
        Base.metadata.create_all(bind=engine)
        print("✅ Banco de dados recriado com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao recriar banco: {e}")
        sys.exit(1)

def show_tables():
    """Mostrar todas as tabelas do banco"""
    try:
        db = next(get_db())
        tables = db.execute(text("SELECT name FROM sqlite_master WHERE type='table'")).fetchall()
        print("\n📋 Tabelas no banco de dados:")
        for table in tables:
            print(f"  - {table[0]}")
        db.close()
        
    except Exception as e:
        print(f"❌ Erro ao listar tabelas: {e}")

if __name__ == "__main__":
    print("🗄️  Migração do Banco de Dados - AntiCrime 04")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "create":
            create_new_tables()
        elif command == "recreate":
            recreate_all_tables()
        elif command == "show":
            show_tables()
        else:
            print("❌ Comando inválido!")
            print("Uso: python migrate_db.py [create|recreate|show]")
    else:
        print("Comandos disponíveis:")
        print("  create   - Criar novas tabelas (seguro)")
        print("  recreate - Recriar TODAS as tabelas (apaga dados!)")
        print("  show     - Mostrar tabelas existentes")
        print("\nExemplo: python migrate_db.py create")
