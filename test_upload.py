#!/usr/bin/env python3
"""
Script para testar upload de fotos de residências
"""

import requests
import io
from PIL import Image
import json

# Configurações
BASE_URL = "http://localhost:8000"
ADMIN_EMAIL = "admin@prm.gov.mz"
ADMIN_PASSWORD = "admin123"

def login():
    """Fazer login e obter token"""
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": ADMIN_EMAIL,
        "senha": ADMIN_PASSWORD
    })
    
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Erro no login: {response.text}")
        return None

def create_test_image():
    """Criar imagem de teste"""
    # Criar uma imagem simples para teste
    img = Image.new('RGB', (400, 300), color='lightblue')
    
    # Salvar em buffer
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='JPEG')
    img_buffer.seek(0)
    
    return img_buffer

def test_create_usuario_with_photo(token):
    """Testar criação de usuário com foto"""
    print("🏠 Testando criação de usuário com foto...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Criar imagem de teste
    test_image = create_test_image()
    
    # Dados do usuário
    form_data = {
        "nome_completo": "Maria Silva Santos",
        "numero_identidade": "987654321B",
        "telefone_principal": "+258847654321",
        "telefone_emergencia": "+258841234567",
        "email": "maria.silva@email.com",
        "provincia": "Maputo",
        "cidade": "Maputo",
        "bairro": "Polana",
        "rua": "Rua da Liberdade",
        "numero_casa": "456",
        "ponto_referencia": "Próximo ao banco",
        "latitude_residencia": -25.9658,
        "longitude_residencia": 32.5892,
        "observacoes": "Casa com jardim na frente",
        "ativo": True
    }
    
    # Arquivos
    files = {
        "foto_residencia": ("casa_teste.jpg", test_image, "image/jpeg")
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/usuarios/upload",
            data=form_data,
            files=files,
            headers=headers
        )
        
        if response.status_code == 200:
            usuario = response.json()
            print("✅ Usuário criado com sucesso!")
            print(f"   Nome: {usuario['nome_completo']}")
            print(f"   ID: {usuario['id']}")
            if usuario['foto_residencia']:
                print(f"   Foto: {BASE_URL}{usuario['foto_residencia']}")
            return usuario
        else:
            print(f"❌ Erro: {response.status_code}")
            print(f"   Detalhes: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return None

def test_upload_photo_only(token, usuario_id):
    """Testar upload apenas da foto"""
    print(f"📷 Testando upload de foto para usuário {usuario_id}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Criar nova imagem de teste
    test_image = create_test_image()
    
    files = {
        "foto": ("nova_casa.jpg", test_image, "image/jpeg")
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/usuarios/{usuario_id}/foto",
            files=files,
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Foto atualizada com sucesso!")
            print(f"   Nova foto: {BASE_URL}{result['foto_url']}")
            return True
        else:
            print(f"❌ Erro: {response.status_code}")
            print(f"   Detalhes: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False

def test_invalid_file(token):
    """Testar upload de arquivo inválido"""
    print("🚫 Testando upload de arquivo inválido...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Criar arquivo de texto (inválido)
    text_content = io.StringIO("Este é um arquivo de texto inválido")
    
    form_data = {
        "nome_completo": "Teste Arquivo Inválido",
        "numero_identidade": "111111111C",
        "telefone_principal": "+258841111111",
        "provincia": "Maputo",
        "cidade": "Maputo",
        "bairro": "Teste",
        "latitude_residencia": -25.9658,
        "longitude_residencia": 32.5892,
    }
    
    files = {
        "foto_residencia": ("arquivo.txt", text_content, "text/plain")
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/usuarios/upload",
            data=form_data,
            files=files,
            headers=headers
        )
        
        if response.status_code == 400:
            print("✅ Arquivo inválido rejeitado corretamente!")
            print(f"   Mensagem: {response.json()['detail']}")
            return True
        else:
            print(f"❌ Arquivo inválido foi aceito (erro!): {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False

def main():
    """Função principal"""
    print("🧪 Teste de Upload de Fotos - AntiCrime 04")
    print("=" * 50)
    
    # Fazer login
    print("🔐 Fazendo login...")
    token = login()
    if not token:
        return
    
    print("✅ Login realizado com sucesso!\n")
    
    # Teste 1: Criar usuário com foto
    usuario = test_create_usuario_with_photo(token)
    if not usuario:
        return
    
    print()
    
    # Teste 2: Upload apenas da foto
    if usuario:
        test_upload_photo_only(token, usuario['id'])
    
    print()
    
    # Teste 3: Arquivo inválido
    test_invalid_file(token)
    
    print("\n" + "=" * 50)
    print("✅ Testes de upload concluídos!")
    print("\n🌐 Verifique as fotos em:")
    print("   http://localhost:8000/uploads/")
    print("\n📋 Documentação da API:")
    print("   http://localhost:8000/docs")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Teste interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
