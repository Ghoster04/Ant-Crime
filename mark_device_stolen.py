from database import get_db
from models import Dispositivo

def mark_device_stolen(imei):
    db = next(get_db())
    dispositivo = db.query(Dispositivo).filter(Dispositivo.imei == imei).first()
    
    if dispositivo:
        print(f"📱 Dispositivo encontrado: {dispositivo.marca} {dispositivo.modelo}")
        print(f"   Status atual: {dispositivo.status}")
        dispositivo.status = 'roubado'
        db.commit()
        print("✅ Dispositivo marcado como ROUBADO!")
    else:
        print(f"❌ Dispositivo com IMEI {imei} não encontrado")
    
    db.close()

if __name__ == "__main__":
    mark_device_stolen('222222222222222')
