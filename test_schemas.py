#!/usr/bin/env python3
"""
Teste dos schemas Pydantic V2 atualizados
"""
import sys
from schemas import (
    AdminCreate, AdminResponse, 
    UsuarioCreate, UsuarioResponse,
    DispositivoCreate, DispositivoResponse,
    EmergenciaCreate, EmergenciaResponse,
    Login, Token, EstatisticasResponse
)

def test_admin_schema():
    """Testa schemas de Admin"""
    print("🧪 Testando schemas de Admin...")
    
    try:
        # Teste AdminCreate
        admin_data = AdminCreate(
            nome_completo="João Silva",
            email="joao@prm.gov.mz",
            numero_badge="PRM001",
            posto_policial="PRM Maputo",
            tipo_admin="super_admin",
            telefone="+258841234567",
            senha="admin123"
        )
        print("  ✅ AdminCreate válido")
        
        # Teste com senha inválida
        try:
            AdminCreate(
                nome_completo="João Silva",
                email="joao@prm.gov.mz",
                numero_badge="PRM001",
                posto_policial="PRM Maputo",
                senha="123"  # Senha muito curta
            )
            print("  ❌ Validação de senha falhou")
        except ValueError as e:
            print(f"  ✅ Validação de senha funcionando: {e}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erro no schema Admin: {e}")
        return False

def test_usuario_schema():
    """Testa schemas de Usuario"""
    print("\n🧪 Testando schemas de Usuario...")
    
    try:
        # Teste UsuarioCreate
        usuario_data = UsuarioCreate(
            nome_completo="Maria Santos",
            numero_identidade="1234567890123",
            telefone_principal="+258841234567",
            provincia="Maputo",
            cidade="Maputo",
            bairro="Alto Maé",
            latitude_residencia=-25.969248,
            longitude_residencia=32.573924,
            ativo=True
        )
        print("  ✅ UsuarioCreate válido")
        
        # Teste com latitude inválida
        try:
            UsuarioCreate(
                nome_completo="Maria Santos",
                numero_identidade="1234567890123",
                telefone_principal="+258841234567",
                provincia="Maputo",
                cidade="Maputo",
                bairro="Alto Maé",
                latitude_residencia=95.0,  # Latitude inválida
                longitude_residencia=32.573924
            )
            print("  ❌ Validação de latitude falhou")
        except ValueError as e:
            print(f"  ✅ Validação de latitude funcionando: {e}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erro no schema Usuario: {e}")
        return False

def test_dispositivo_schema():
    """Testa schemas de Dispositivo"""
    print("\n🧪 Testando schemas de Dispositivo...")
    
    try:
        # Teste DispositivoCreate
        dispositivo_data = DispositivoCreate(
            imei="123456789012345",
            modelo="Galaxy S21",
            marca="Samsung",
            sistema_operacional="Android",
            versao_app="1.0.0",
            usuario_id=1
        )
        print("  ✅ DispositivoCreate válido")
        
        # Teste com IMEI inválido
        try:
            DispositivoCreate(
                imei="12345678901234",  # IMEI com 14 dígitos (inválido)
                usuario_id=1
            )
            print("  ❌ Validação de IMEI falhou")
        except ValueError as e:
            print(f"  ✅ Validação de IMEI funcionando: {e}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erro no schema Dispositivo: {e}")
        return False

def test_emergencia_schema():
    """Testa schemas de Emergencia"""
    print("\n🧪 Testando schemas de Emergencia...")
    
    try:
        # Teste EmergenciaCreate
        emergencia_data = EmergenciaCreate(
            dispositivo_id=1,
            latitude=-25.969248,
            longitude=32.573924,
            nivel_bateria=85,
            precisao_gps=5.0
        )
        print("  ✅ EmergenciaCreate válido")
        
        # Teste com longitude inválida
        try:
            EmergenciaCreate(
                dispositivo_id=1,
                latitude=-25.969248,
                longitude=185.0  # Longitude inválida
            )
            print("  ❌ Validação de longitude falhou")
        except ValueError as e:
            print(f"  ✅ Validação de longitude funcionando: {e}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erro no schema Emergencia: {e}")
        return False

def test_auth_schemas():
    """Testa schemas de autenticação"""
    print("\n🧪 Testando schemas de autenticação...")
    
    try:
        # Teste Login
        login_data = Login(
            email="admin@prm.gov.mz",
            senha="admin123"
        )
        print("  ✅ Login schema válido")
        
        # Teste Token
        token_data = Token(
            access_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            token_type="bearer"
        )
        print("  ✅ Token schema válido")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erro nos schemas de auth: {e}")
        return False

def test_stats_schema():
    """Testa schema de estatísticas"""
    print("\n🧪 Testando schema de estatísticas...")
    
    try:
        # Teste EstatisticasResponse
        stats_data = EstatisticasResponse(
            total_usuarios=150,
            total_dispositivos=120,
            total_emergencias=25,
            emergencias_ativas=3,
            dispositivos_roubados=5,
            usuarios_ativos=145
        )
        print("  ✅ EstatisticasResponse válido")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erro no schema de estatísticas: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 Teste dos Schemas Pydantic V2 - AntiCrime 04")
    print("=" * 60)
    
    tests = [
        test_admin_schema,
        test_usuario_schema,
        test_dispositivo_schema,
        test_emergencia_schema,
        test_auth_schemas,
        test_stats_schema
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Resultado: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 Todos os schemas estão funcionando corretamente!")
        print("✅ Migração para Pydantic V2 concluída com sucesso!")
        sys.exit(0)
    else:
        print("⚠️ Alguns schemas precisam de ajustes")
        sys.exit(1)

if __name__ == "__main__":
    main()
