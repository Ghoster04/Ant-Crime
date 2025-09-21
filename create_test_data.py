from database import get_db
from models import Dispositivo, PingDispositivo
from datetime import datetime, timedelta
import random

def create_test_pings():
    """Criar vários pings de teste para o dispositivo 222222222222222"""
    db = next(get_db())
    
    dispositivo = db.query(Dispositivo).filter(Dispositivo.imei == '222222222222222').first()
    
    if not dispositivo:
        print("❌ Dispositivo de teste não encontrado")
        return
    
    print(f"📱 Criando pings para: {dispositivo.marca} {dispositivo.modelo}")
    
    # Localização base (Maputo)
    base_lat = -25.9692
    base_lng = 32.5732
    
    # Criar 10 pings com localizações diferentes
    for i in range(10):
        # Variar localização em ~1km
        lat = base_lat + (random.random() - 0.5) * 0.01
        lng = base_lng + (random.random() - 0.5) * 0.01
        battery = max(10, 100 - i * 8)  # Bateria diminuindo
        
        ping = PingDispositivo(
            dispositivo_id=dispositivo.id,
            latitude=lat,
            longitude=lng,
            precisao_gps=random.randint(5, 25),
            nivel_bateria=battery,
            status_dispositivo='roubado',
            tipo_ping='stolen_device_ping',
            timestamp=datetime.now() - timedelta(minutes=i*10)
        )
        
        db.add(ping)
        print(f"  📍 Ping {i+1}: {lat:.4f}, {lng:.4f} - {battery}%")
    
    db.commit()
    
    total_pings = db.query(PingDispositivo).count()
    print(f"\n✅ Pings criados! Total no banco: {total_pings}")
    
    db.close()

if __name__ == "__main__":
    create_test_pings()
