from database import get_db
from models import Dispositivo, PingDispositivo, Usuario
from datetime import datetime

def create_test_ping():
    """Criar um ping de teste para verificar se a API funciona"""
    db = next(get_db())
    
    # Buscar dispositivo de teste
    dispositivo = db.query(Dispositivo).filter(Dispositivo.imei == '222222222222222').first()
    
    if not dispositivo:
        print("❌ Dispositivo de teste não encontrado")
        return
    
    # Criar ping de teste
    ping = PingDispositivo(
        dispositivo_id=dispositivo.id,
        latitude=-25.9692,
        longitude=32.5732,
        precisao_gps=10.0,
        nivel_bateria=75,
        status_dispositivo='roubado',
        tipo_ping='stolen_device_ping',
        timestamp=datetime.utcnow()
    )
    
    db.add(ping)
    db.commit()
    
    print(f"✅ Ping de teste criado para dispositivo {dispositivo.marca} {dispositivo.modelo}")
    print(f"   Localização: {ping.latitude}, {ping.longitude}")
    print(f"   Bateria: {ping.nivel_bateria}%")
    
    # Verificar quantos pings existem agora
    total_pings = db.query(PingDispositivo).count()
    print(f"📊 Total de pings no banco: {total_pings}")
    
    db.close()

def show_all_pings():
    """Mostrar todos os pings do banco"""
    db = next(get_db())
    
    pings = db.query(PingDispositivo).join(Dispositivo).all()
    
    print(f"\n📍 Todos os pings ({len(pings)}):")
    for ping in pings:
        print(f"  ID: {ping.id} | Dispositivo: {ping.dispositivo.marca} {ping.dispositivo.modelo}")
        print(f"      Localização: {ping.latitude}, {ping.longitude}")
        print(f"      Bateria: {ping.nivel_bateria}% | Status: {ping.status_dispositivo}")
        print(f"      Timestamp: {ping.timestamp}")
        print()
    
    db.close()

if __name__ == "__main__":
    print("🧪 Teste da API de Pings")
    print("=" * 30)
    
    create_test_ping()
    show_all_pings()
