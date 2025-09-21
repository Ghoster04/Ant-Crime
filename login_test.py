#!/usr/bin/env python3
"""
Script simples para fazer login e testar o admin inicial
"""

import requests
import json

# Configurações
BASE_URL = "http://localhost:8000"
ADMIN_EMAIL = "admin@prm.gov.mz"
ADMIN_PASSWORD = "admin123"

def test_admin_login():
    """Testar login do admin inicial"""
    print("🔐 Testando login do admin inicial...")
    print("=" * 50)
    
    # Dados de login
    login_data = {
        "email": ADMIN_EMAIL,
        "senha": ADMIN_PASSWORD
    }
    
    try:
        # Fazer login
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        
        if response.status_code == 200:
            data = response.json()
            token = data["access_token"]
            
            print("✅ Login realizado com sucesso!")
            print(f"📧 Email: {ADMIN_EMAIL}")
            print(f"🔑 Token: {token[:50]}...")
            
            # Testar token obtendo dados do admin
            headers = {"Authorization": f"Bearer {token}"}
            me_response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
            
            if me_response.status_code == 200:
                admin_data = me_response.json()
                print("\n👤 Dados do Admin:")
                print(f"   Nome: {admin_data['nome_completo']}")
                print(f"   Email: {admin_data['email']}")
                print(f"   Badge: {admin_data['numero_badge']}")
                print(f"   Posto: {admin_data['posto_policial']}")
                print(f"   Tipo: {admin_data['tipo_admin']}")
                
                return token
            else:
                print("❌ Erro ao obter dados do admin")
                return None
        else:
            print(f"❌ Erro no login: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ Não foi possível conectar ao servidor")
        print("   Certifique-se de que o servidor está rodando:")
        print("   python main.py")
        return None

def test_admin_functions(token):
    """Testar algumas funções do admin"""
    if not token:
        return
    
    print("\n🧪 Testando funções do admin...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Listar usuários
    try:
        response = requests.get(f"{BASE_URL}/usuarios/", headers=headers)
        if response.status_code == 200:
            usuarios = response.json()
            print(f"✅ Total de usuários: {len(usuarios)}")
        else:
            print(f"❌ Erro ao listar usuários: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # Obter estatísticas
    try:
        response = requests.get(f"{BASE_URL}/dashboard/stats", headers=headers)
        if response.status_code == 200:
            stats = response.json()
            print("📊 Estatísticas do Sistema:")
            for key, value in stats.items():
                print(f"   {key}: {value}")
        else:
            print(f"❌ Erro ao obter estatísticas: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    print("🚀 Teste de Login - AntiCrime 04")
    print("=" * 50)
    
    # Fazer login
    token = test_admin_login()
    
    # Testar funções
    test_admin_functions(token)
    
    print("\n" + "=" * 50)
    print("🌐 Acesse a documentação interativa em:")
    print("   http://localhost:8000/docs")
    print("\n💡 Use as credenciais:")
    print(f"   Email: {ADMIN_EMAIL}")
    print(f"   Senha: {ADMIN_PASSWORD}")
