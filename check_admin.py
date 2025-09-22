#!/usr/bin/env python3
"""
Script para verificar se existe admin no SQLite
"""
import sqlite3

def check_admin():
    """Verificar se existe admin"""
    try:
        conn = sqlite3.connect('anticrime04.db')
        cursor = conn.cursor()
        
        # Verificar se tabela existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='admins'")
        if not cursor.fetchone():
            print("❌ Tabela 'admins' não existe")
            return False
        
        # Buscar admins
        cursor.execute("SELECT id, email, tipo_admin, ativo FROM admins")
        admins = cursor.fetchall()
        
        if not admins:
            print("❌ Nenhum admin encontrado")
            return False
        
        print(f"✅ Encontrados {len(admins)} admin(s):")
        for admin in admins:
            print(f"   ID: {admin[0]}, Email: {admin[1]}, Tipo: {admin[2]}, Ativo: {admin[3]}")
        
        # Verificar se existe admin padrão
        cursor.execute("SELECT * FROM admins WHERE email = 'admin@prm.gov.mz'")
        default_admin = cursor.fetchone()
        
        if default_admin:
            print("\n✅ Admin padrão encontrado!")
            print(f"   Email: {default_admin[2]}")
            print(f"   Tipo: {default_admin[6]}")
            print(f"   Ativo: {default_admin[8]}")
        else:
            print("\n⚠️ Admin padrão (admin@prm.gov.mz) não encontrado")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("🔍 VERIFICANDO ADMINS NO SQLITE")
    print("=" * 50)
    check_admin()
