from main import app
from fastapi.testclient import TestClient
from database import get_db
from models import Admin
import jwt
from datetime import datetime, timedelta

# Criar cliente de teste
client = TestClient(app)

def get_test_token():
    """Criar um token válido para teste"""
    # Buscar um admin no banco
    db = next(get_db())
    admin = db.query(Admin).first()
    
    if not admin:
        print("❌ Nenhum admin encontrado no banco")
        return None
    
    # Criar token JWT
    payload = {
        "sub": str(admin.id),
        "exp": datetime.utcnow() + timedelta(hours=1),
        "tipo": "admin"
    }
    
    token = jwt.encode(payload, "sua_chave_secreta_muito_segura_aqui_mude_em_producao", algorithm="HS256")
    db.close()
    
    print(f"✅ Token criado para admin: {admin.nome_completo}")
    return token

def test_pings_api():
    """Testar a API de pings diretamente"""
    token = get_test_token()
    
    if not token:
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = client.get("/dispositivos/pings-roubados", headers=headers)
        print(f"📡 Status da API: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API funcionando! Retornou {len(data)} pings")
            
            for ping in data:
                print(f"  - Ping ID: {ping['id']}")
                print(f"    Dispositivo: {ping['dispositivo']['marca']} {ping['dispositivo']['modelo']}")
                print(f"    Localização: {ping['latitude']}, {ping['longitude']}")
                print(f"    Status: {ping['status_dispositivo']}")
                print()
        else:
            print(f"❌ Erro na API: {response.text}")
    
    except Exception as e:
        print(f"❌ Erro ao testar API: {e}")

if __name__ == "__main__":
    print("🧪 Teste Direto da API de Pings")
    print("=" * 35)
    test_pings_api()
