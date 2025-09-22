#!/usr/bin/env python3
"""
Script simples para criar usuário admin usando SQLite
"""
import sqlite3
import hashlib
from datetime import datetime

def hash_password(password):
    """Hash simples da senha"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_admin():
    """Criar usuário admin no SQLite"""
    try:
        # Conectar ao banco SQLite
        conn = sqlite3.connect('anticrime04.db')
        cursor = conn.cursor()
        
        # Criar tabela de admins se não existir
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_completo TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                senha_hash TEXT NOT NULL,
                numero_badge TEXT UNIQUE NOT NULL,
                posto_policial TEXT NOT NULL,
                tipo_admin TEXT DEFAULT 'operador',
                telefone TEXT,
                ativo BOOLEAN DEFAULT 1,
                data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                ultimo_login DATETIME,
                criado_por INTEGER
            )
        ''')
        
        # Verificar se já existe admin
        cursor.execute("SELECT COUNT(*) FROM admins WHERE tipo_admin = 'super_admin'")
        count = cursor.fetchone()[0]
        
        if count > 0:
            print("⚠️ Super administrador já existe!")
            cursor.execute("SELECT email, tipo_admin FROM admins WHERE tipo_admin = 'super_admin'")
            admin = cursor.fetchone()
            print(f"   Email: {admin[0]}")
            print(f"   Tipo: {admin[1]}")
        else:
            # Criar super admin
            admin_data = (
                "Administrador Sistema",
                "admin@prm.gov.mz", 
                hash_password("admin123"),
                "ADMIN001",
                "PRM Central",
                "super_admin"
            )
            
            cursor.execute('''
                INSERT INTO admins 
                (nome_completo, email, senha_hash, numero_badge, posto_policial, tipo_admin)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', admin_data)
            
            conn.commit()
            print("✅ Super administrador criado com sucesso!")
            print("📋 Credenciais:")
            print("   Email: admin@prm.gov.mz")
            print("   Senha: admin123")
            print("   Tipo: super_admin")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar administrador: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("🔧 CRIADOR DE USUÁRIO ADMINISTRADOR (SQLite)")
    print("=" * 50)
    
    if create_admin():
        print("\n🎉 Processo concluído com sucesso!")
    else:
        print("\n💥 Falha ao criar administrador")
