import asyncio
import websockets
import json
from datetime import datetime

async def test_stolen_device_ping():
    """Testar envio de ping de dispositivo roubado via WebSocket"""
    uri = "ws://localhost:8000/ws"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Conectado ao WebSocket")
            
            # Enviar ping de dispositivo roubado
            ping_data = {
                "type": "stolen_device_ping",
                "imei": "222222222222222",
                "marca": "Acme",
                "modelo": "Android Phone",
                "sistema_operacional": "Android 13",
                "versao_app": "1.0.0",
                "latitude": -25.9692,
                "longitude": 32.5732,
                "bateria": 85,
                "precisao": 10,
                "status": "roubado",
                "timestamp": datetime.now().isoformat()
            }
            
            await websocket.send(json.dumps(ping_data))
            print("📡 Ping enviado:", ping_data)
            
            # Aguardar resposta
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print("📨 Resposta recebida:", response)
            except asyncio.TimeoutError:
                print("⏱️ Timeout - sem resposta em 5 segundos")
            
    except Exception as e:
        print(f"❌ Erro no WebSocket: {e}")

if __name__ == "__main__":
    print("🧪 Teste de Ping via WebSocket")
    print("=" * 35)
    asyncio.run(test_stolen_device_ping())
