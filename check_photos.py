#!/usr/bin/env python3
"""
Verificar fotos de residências no banco de dados
"""

from database import get_db
from models import Usuario
import requests

def check_photos():
    """Verificar usuários com fotos"""
    db = next(get_db())
    
    print("🔍 Verificando usuários com fotos...")
    
    usuarios_com_foto = db.query(Usuario).filter(Usuario.foto_residencia.isnot(None)).all()
    
    print(f"📊 Total de usuários com foto: {len(usuarios_com_foto)}")
    
    for usuario in usuarios_com_foto:
        print(f"\n👤 Usuário: {usuario.nome_completo}")
        print(f"   📷 Foto: {usuario.foto_residencia}")
        print(f"   🆔 ID: {usuario.id}")
        
        # Testar acesso à foto
        if usuario.foto_residencia:
            foto_url = f"http://localhost:8000{usuario.foto_residencia}"
            print(f"   🌐 URL: {foto_url}")
            
            try:
                response = requests.get(foto_url, timeout=5)
                if response.status_code == 200:
                    print(f"   ✅ Foto acessível ({response.headers.get('content-type', 'unknown')})")
                else:
                    print(f"   ❌ Erro HTTP {response.status_code}")
            except Exception as e:
                print(f"   ❌ Erro de acesso: {e}")
    
    db.close()

if __name__ == "__main__":
    check_photos()
