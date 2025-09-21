#!/usr/bin/env python3
"""
Script de teste para a API AntiCrime 04
"""

import requests
import json
from datetime import datetime

# Configuração
BASE_URL = "http://localhost:8000"
ADMIN_EMAIL = "admin@prm.gov.mz"
ADMIN_PASSWORD = "admin123"

class AntiCrimeAPI:
    def __init__(self, base_url):
        self.base_url = base_url
        self.token = None
        self.headers = {}
    
    def login(self, email, password):
        """Fazer login e obter token"""
        response = requests.post(
            f"{self.base_url}/auth/login",
            json={"email": email, "senha": password}
        )
        
        if response.status_code == 200:
            data = response.json()
            self.token = data["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
            print("✅ Login realizado com sucesso!")
            return True
        else:
            print(f"❌ Erro no login: {response.text}")
            return False
    
    def create_usuario(self, usuario_data):
        """Criar novo usuário"""
        response = requests.post(
            f"{self.base_url}/usuarios/",
            json=usuario_data,
            headers=self.headers
        )
        
        if response.status_code == 200:
            user = response.json()
            print(f"✅ Usuário criado: {user['nome_completo']} (ID: {user['id']})")
            return user
        else:
            print(f"❌ Erro ao criar usuário: {response.text}")
            return None
    
    def create_dispositivo(self, dispositivo_data):
        """Criar novo dispositivo"""
        response = requests.post(
            f"{self.base_url}/dispositivos/",
            json=dispositivo_data,
            headers=self.headers
        )
        
        if response.status_code == 200:
            device = response.json()
            print(f"✅ Dispositivo criado: IMEI {device['imei']} (ID: {device['id']})")
            return device
        else:
            print(f"❌ Erro ao criar dispositivo: {response.text}")
            return None
    
    def register_dispositivo(self, imei, device_info):
        """Registrar dispositivo (simulando app móvel)"""
        data = {"imei": imei, **device_info}
        response = requests.post(f"{self.base_url}/dispositivos/register", json=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Dispositivo registrado pelo app: {result['message']}")
            return result
        else:
            print(f"❌ Erro no registro do dispositivo: {response.text}")
            return None
    
    def create_emergencia(self, dispositivo_id, lat, lng):
        """Criar emergência (simulando SOS)"""
        data = {
            "dispositivo_id": dispositivo_id,
            "latitude": lat,
            "longitude": lng,
            "nivel_bateria": 45,
            "precisao_gps": 5.2
        }
        
        response = requests.post(f"{self.base_url}/emergencias/sos", json=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"🚨 EMERGÊNCIA CRIADA! ID: {result['emergency_id']}")
            return result
        else:
            print(f"❌ Erro ao criar emergência: {response.text}")
            return None
    
    def get_emergencias_ativas(self):
        """Listar emergências ativas"""
        response = requests.get(
            f"{self.base_url}/emergencias/ativas",
            headers=self.headers
        )
        
        if response.status_code == 200:
            emergencias = response.json()
            print(f"🚨 {len(emergencias)} emergência(s) ativa(s)")
            for em in emergencias:
                print(f"   - ID {em['id']}: Lat {em['latitude']}, Lng {em['longitude']}")
            return emergencias
        else:
            print(f"❌ Erro ao listar emergências: {response.text}")
            return []
    
    def get_stats(self):
        """Obter estatísticas"""
        response = requests.get(
            f"{self.base_url}/dashboard/stats",
            headers=self.headers
        )
        
        if response.status_code == 200:
            stats = response.json()
            print("📊 Estatísticas do Sistema:")
            for key, value in stats.items():
                print(f"   {key}: {value}")
            return stats
        else:
            print(f"❌ Erro ao obter estatísticas: {response.text}")
            return None

def test_complete_flow():
    """Testar fluxo completo do sistema"""
    print("🧪 Iniciando teste completo da API...")
    print("=" * 50)
    
    # Inicializar API
    api = AntiCrimeAPI(BASE_URL)
    
    # 1. Fazer login
    print("\n1️⃣ Fazendo login...")
    if not api.login(ADMIN_EMAIL, ADMIN_PASSWORD):
        return
    
    # 2. Criar usuário
    print("\n2️⃣ Criando usuário...")
    usuario_data = {
        "nome_completo": "João Silva Santos",
        "numero_identidade": "123456789A",
        "telefone_principal": "+258841234567",
        "telefone_emergencia": "+258847654321",
        "email": "joao.silva@email.com",
        "provincia": "Maputo",
        "cidade": "Maputo",
        "bairro": "Sommerschield",
        "rua": "Rua da Paz",
        "numero_casa": "123",
        "ponto_referencia": "Próximo ao mercado central",
        "latitude_residencia": -25.9692,
        "longitude_residencia": 32.5732,
        "foto_residencia": "https://exemplo.com/foto_casa.jpg",
        "observacoes": "Casa com portão azul"
    }
    
    usuario = api.create_usuario(usuario_data)
    if not usuario:
        return
    
    # 3. Criar dispositivo
    print("\n3️⃣ Criando dispositivo...")
    dispositivo_data = {
        "imei": "123456789012345",
        "modelo": "Galaxy S21",
        "marca": "Samsung",
        "sistema_operacional": "Android",
        "versao_app": "1.0.0",
        "usuario_id": usuario["id"]
    }
    
    dispositivo = api.create_dispositivo(dispositivo_data)
    if not dispositivo:
        return
    
    # 4. Simular registro do app móvel
    print("\n4️⃣ Simulando registro do app móvel...")
    device_info = {
        "modelo": "Galaxy S21 Ultra",
        "marca": "Samsung",
        "sistema_operacional": "Android 13",
        "versao_app": "1.0.1"
    }
    
    register_result = api.register_dispositivo("123456789012345", device_info)
    
    # 5. Simular emergência (SOS)
    print("\n5️⃣ Simulando emergência SOS...")
    # Coordenadas de Maputo (exemplo)
    emergencia = api.create_emergencia(
        dispositivo["id"], 
        -25.9658, 
        32.5892
    )
    
    # 6. Listar emergências ativas
    print("\n6️⃣ Listando emergências ativas...")
    api.get_emergencias_ativas()
    
    # 7. Obter estatísticas
    print("\n7️⃣ Obtendo estatísticas...")
    api.get_stats()
    
    print("\n" + "=" * 50)
    print("✅ Teste completo finalizado!")
    print("\n🌐 Acesse a documentação interativa em:")
    print("   http://localhost:8000/docs")

def check_api_health():
    """Verificar se a API está funcionando"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API está funcionando: {data['status']}")
            return True
        else:
            print(f"❌ API retornou status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Não foi possível conectar à API")
        print("   Certifique-se de que o servidor está rodando:")
        print("   python main.py")
        return False

if __name__ == "__main__":
    print("🧪 Teste da API AntiCrime 04")
    print("=" * 50)
    
    # Verificar se API está rodando
    if check_api_health():
        test_complete_flow()
    else:
        print("\n💡 Para iniciar o servidor:")
        print("   cd backend/")
        print("   python main.py")
