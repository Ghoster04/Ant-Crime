#!/usr/bin/env python3
"""
Demonstração da ligação entre Dispositivo e Usuário
"""

import requests
import json

BASE_URL = "http://localhost:8000"
ADMIN_EMAIL = "admin@prm.gov.mz"
ADMIN_PASSWORD = "admin123"

def login():
    """Fazer login como admin"""
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": ADMIN_EMAIL,
        "senha": ADMIN_PASSWORD
    })
    return response.json()["access_token"] if response.status_code == 200 else None

def create_usuario(token):
    """1. Admin cadastra usuário"""
    print("1️⃣ ADMIN: Cadastrando usuário...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Usando endpoint JSON (sem foto)
    usuario_data = {
        "nome_completo": "Maria Santos",
        "numero_identidade": "987654321B",
        "telefone_principal": "+258847654321",
        "telefone_emergencia": "+258841234567",
        "email": "maria.santos@email.com",
        "provincia": "Maputo",
        "cidade": "Maputo",
        "bairro": "Polana",
        "rua": "Rua da Paz",
        "numero_casa": "123",
        "ponto_referencia": "Próximo ao mercado",
        "latitude_residencia": -25.9658,
        "longitude_residencia": 32.5892,
        "observacoes": "Casa com portão azul"
    }
    
    response = requests.post(f"{BASE_URL}/usuarios/", json=usuario_data, headers=headers)
    
    if response.status_code == 200:
        usuario = response.json()
        print(f"   ✅ Usuário criado: {usuario['nome_completo']} (ID: {usuario['id']})")
        return usuario
    else:
        print(f"   ❌ Erro: {response.text}")
        return None

def create_dispositivo(token, usuario_id):
    """2. Admin vincula dispositivo ao usuário"""
    print(f"2️⃣ ADMIN: Vinculando dispositivo ao usuário {usuario_id}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    dispositivo_data = {
        "imei": "123456789012345",
        "modelo": "iPhone 13",
        "marca": "Apple",
        "sistema_operacional": "iOS",
        "versao_app": "1.0.0",
        "usuario_id": usuario_id  # ← LIGAÇÃO AQUI!
    }
    
    response = requests.post(f"{BASE_URL}/dispositivos/", json=dispositivo_data, headers=headers)
    
    if response.status_code == 200:
        dispositivo = response.json()
        print(f"   ✅ Dispositivo vinculado: IMEI {dispositivo['imei']} → Usuário {dispositivo['usuario_id']}")
        return dispositivo
    else:
        print(f"   ❌ Erro: {response.text}")
        return None

def simulate_app_registration():
    """3. App móvel se registra automaticamente"""
    print("3️⃣ APP MÓVEL: Registrando-se automaticamente...")
    
    # App envia apenas IMEI e dados do dispositivo
    app_data = {
        "imei": "123456789012345",  # Mesmo IMEI cadastrado pelo admin
        "modelo": "iPhone 13 Pro",  # App pode enviar modelo mais específico
        "marca": "Apple",
        "sistema_operacional": "iOS 17",
        "versao_app": "1.0.1"
    }
    
    response = requests.post(f"{BASE_URL}/dispositivos/register", json=app_data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ App ativado! Usuário: {result['usuario_id']}, Dispositivo: {result['dispositivo_id']}")
        return result
    else:
        print(f"   ❌ Erro: {response.text}")
        return None

def test_emergency_with_link(dispositivo_id):
    """4. Testar emergência com ligação"""
    print(f"4️⃣ EMERGÊNCIA: Testando SOS do dispositivo {dispositivo_id}...")
    
    emergency_data = {
        "dispositivo_id": dispositivo_id,
        "latitude": -25.9658,
        "longitude": 32.5892,
        "nivel_bateria": 45,
        "precisao_gps": 3.2
    }
    
    response = requests.post(f"{BASE_URL}/emergencias/sos", json=emergency_data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"   🚨 EMERGÊNCIA CRIADA! ID: {result['emergency_id']}")
        return result
    else:
        print(f"   ❌ Erro: {response.text}")
        return None

def show_relationships(token):
    """5. Mostrar relacionamentos"""
    print("5️⃣ RELACIONAMENTOS: Verificando ligações...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Listar usuários
    users_response = requests.get(f"{BASE_URL}/usuarios/", headers=headers)
    if users_response.status_code == 200:
        usuarios = users_response.json()
        print(f"   👥 Total de usuários: {len(usuarios)}")
        for user in usuarios:
            print(f"      - {user['nome_completo']} (ID: {user['id']})")
    
    # Listar dispositivos
    devices_response = requests.get(f"{BASE_URL}/dispositivos/", headers=headers)
    if devices_response.status_code == 200:
        dispositivos = devices_response.json()
        print(f"   📱 Total de dispositivos: {len(dispositivos)}")
        for device in dispositivos:
            print(f"      - IMEI: {device['imei']} → Usuário ID: {device['usuario_id']}")
    
    # Listar emergências
    emergency_response = requests.get(f"{BASE_URL}/emergencias/", headers=headers)
    if emergency_response.status_code == 200:
        emergencias = emergency_response.json()
        print(f"   🚨 Total de emergências: {len(emergencias)}")
        for emergency in emergencias:
            print(f"      - ID: {emergency['id']} → Usuário: {emergency['usuario_id']}, Dispositivo: {emergency['dispositivo_id']}")

def main():
    """Demonstração completa"""
    print("🔗 Demonstração: Ligação Dispositivo ↔ Usuário")
    print("=" * 60)
    
    # Login
    token = login()
    if not token:
        print("❌ Falha no login")
        return
    
    print("✅ Login realizado com sucesso!\n")
    
    # 1. Criar usuário
    usuario = create_usuario(token)
    if not usuario:
        return
    
    print()
    
    # 2. Vincular dispositivo
    dispositivo = create_dispositivo(token, usuario['id'])
    if not dispositivo:
        return
    
    print()
    
    # 3. App se registra
    app_result = simulate_app_registration()
    if not app_result:
        return
    
    print()
    
    # 4. Testar emergência
    test_emergency_with_link(app_result['dispositivo_id'])
    
    print()
    
    # 5. Mostrar relacionamentos
    show_relationships(token)
    
    print("\n" + "=" * 60)
    print("✅ Demonstração completa!")
    print("\n📋 RESUMO DO FLUXO:")
    print("   1. Admin cadastra usuário na PRM")
    print("   2. Admin registra IMEI do celular do usuário")
    print("   3. Usuário recebe app que se ativa automaticamente")
    print("   4. Em emergência, app envia SOS com localização")
    print("   5. PRM recebe alerta com dados completos do usuário")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Demonstração interrompida")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
