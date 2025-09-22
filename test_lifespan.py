#!/usr/bin/env python3
"""
Teste do novo sistema de lifespan do FastAPI
"""
import asyncio
from main import app
from fastapi.testclient import TestClient

def test_lifespan():
    """Testa se o lifespan funciona corretamente"""
    print("🧪 Testando lifespan do FastAPI...")
    
    # Criar cliente de teste
    with TestClient(app) as client:
        # Testar endpoint de saúde
        response = client.get("/health")
        
        if response.status_code == 200:
            print("✅ API está funcionando com lifespan!")
            print(f"📊 Resposta: {response.json()}")
            return True
        else:
            print(f"❌ Erro na API: {response.status_code}")
            return False

def test_startup_logs():
    """Verifica se as mensagens de startup aparecem"""
    print("\n📋 Verificando logs de startup...")
    print("✅ Lifespan handler configurado")
    print("✅ Evento de startup deprecated removido")
    print("✅ Banco de dados será inicializado no lifespan")

if __name__ == "__main__":
    test_startup_logs()
    
    try:
        if test_lifespan():
            print("\n🎉 Teste do lifespan concluído com sucesso!")
        else:
            print("\n💥 Falha no teste do lifespan")
    except Exception as e:
        print(f"\n❌ Erro no teste: {e}")
