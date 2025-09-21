#!/usr/bin/env python3
"""
Teste simples para o endpoint HTTP de ping
"""

import requests
import json
from datetime import datetime

def test_http_ping():
    """Testar endpoint HTTP de ping"""
    
    # Dados do ping
    ping_data = {
        "imei": "222222222222222",  # IMEI do dispositivo de teste
        "latitude": -25.9692,
        "longitude": 32.5732,
        "bateria": 85,
        "precisao": 10,
        "status": "roubado",
        "tipo_ping": "stolen_device_ping"
    }
    
    print("🧪 Testando endpoint HTTP de ping...")
    print(f"📡 URL: http://localhost:8000/dispositivos/ping")
    print(f"📦 Dados: {json.dumps(ping_data, indent=2)}")
    
    try:
        response = requests.post(
            "http://localhost:8000/dispositivos/ping",
            json=ping_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"\n📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Ping enviado com sucesso!")
            print(f"   Status: {result.get('status')}")
            print(f"   Device ID: {result.get('device_id')}")
            print(f"   Device Status: {result.get('device_status')}")
            print(f"   Timestamp: {result.get('timestamp')}")
            return True
        else:
            print(f"❌ Erro: {response.status_code}")
            try:
                error = response.json()
                print(f"   Detalhes: {error}")
            except:
                print(f"   Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return False

if __name__ == "__main__":
    print("🔧 AntiCrime04 - Teste HTTP Ping")
    print("=" * 50)
    
    # Verificar se servidor está rodando
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Servidor está rodando!")
        else:
            print("⚠️ Servidor respondeu com status diferente de 200")
    except Exception as e:
        print(f"❌ Servidor não está rodando: {e}")
        print("💡 Execute o servidor com: python main.py")
        exit(1)
    
    print()
    
    # Testar ping
    success = test_http_ping()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Teste passou! Endpoint HTTP funcionando.")
        print("💡 Agora os pings HTTP devem aparecer no WebSocket!")
    else:
        print("⚠️ Teste falhou. Verifique o servidor e dados.")
