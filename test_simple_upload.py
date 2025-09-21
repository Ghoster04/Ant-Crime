#!/usr/bin/env python3
"""
Teste simples de upload
"""

import requests

# Configurações
BASE_URL = "http://localhost:8000"
ADMIN_EMAIL = "admin@prm.gov.mz"
ADMIN_PASSWORD = "admin123"

def login():
    """Fazer login"""
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": ADMIN_EMAIL,
        "senha": ADMIN_PASSWORD
    })
    return response.json()["access_token"] if response.status_code == 200 else None

def test_create_usuario_without_photo(token):
    """Testar criação de usuário SEM foto"""
    print("👤 Testando criação de usuário SEM foto...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    form_data = {
        "nome_completo": "João Teste",
        "numero_identidade": "123TEST",
        "telefone_principal": "+258841111111",
        "provincia": "Maputo",
        "cidade": "Maputo", 
        "bairro": "Teste",
        "latitude_residencia": -25.9658,
        "longitude_residencia": 32.5892,
    }
    
    response = requests.post(f"{BASE_URL}/usuarios/upload", data=form_data, headers=headers)
    
    if response.status_code == 200:
        usuario = response.json()
        print("✅ Usuário criado com sucesso!")
        print(f"   Nome: {usuario['nome_completo']}")
        return usuario
    else:
        print(f"❌ Erro: {response.status_code}")
        print(f"   Detalhes: {response.text}")
        return None

def main():
    """Função principal"""
    print("🧪 Teste Simples de Upload")
    print("=" * 40)
    
    # Login
    token = login()
    if not token:
        print("❌ Falha no login")
        return
    
    print("✅ Login OK\n")
    
    # Testar sem foto primeiro
    test_create_usuario_without_photo(token)

if __name__ == "__main__":
    main()
