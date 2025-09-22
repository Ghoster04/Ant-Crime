from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import DeclarativeBase
from fastapi import HTTPException
from config import settings

# Criar engine usando SQLite (mais simples e confiável)
def create_database_engine():
    """Criar engine do banco SQLite"""
    try:
        # Usar SQLite em vez de MySQL
        sqlite_url = "sqlite:///./anticrime04.db"
        
        engine = create_engine(
            sqlite_url,
            echo=settings.DEBUG,
            connect_args={"check_same_thread": False},  # Para SQLite
        )
        return engine
    except Exception as e:
        print(f"⚠️ Erro ao criar engine do banco: {e}")
        return None

# Tentar criar engine, mas não falhar se não conseguir
engine = create_database_engine()

# Criar sessionmaker apenas se engine estiver disponível
if engine is not None:
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
else:
    SessionLocal = None

# Base para os modelos
class Base(DeclarativeBase):
    pass

def get_db():
    """
    Dependency para obter sessão do banco de dados
    """
    if engine is None or SessionLocal is None:
        raise HTTPException(
            status_code=503, 
            detail="Banco de dados não disponível"
        )
    
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=503,
            detail=f"Erro de conexão com banco: {str(e)}"
        )
    finally:
        db.close()

def init_db():
    """
    Inicializar banco de dados - criar todas as tabelas
    """
    if engine is None:
        print("⚠️ Engine do banco não disponível, pulando inicialização...")
        return False
    
    try:
        from models import Base
        Base.metadata.create_all(bind=engine)
        print("✅ Banco de dados inicializado com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao inicializar banco de dados: {e}")
        print("⚠️ Continuando sem inicialização do banco...")
        return False

def create_superuser():
    """
    Criar primeiro super admin do sistema
    """
    from models import Admin
    from passlib.context import CryptContext
    
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    db = SessionLocal()
    try:
        # Verificar se já existe um super admin
        existing_admin = db.query(Admin).filter(
            Admin.tipo_admin == "super_admin"
        ).first()
        
        if not existing_admin:
            super_admin = Admin(
                nome_completo="Administrador Sistema",
                email="admin@prm.gov.mz",
                senha_hash=pwd_context.hash("admin123"),  # Mudar em produção
                numero_badge="ADMIN001",
                posto_policial="PRM Central",
                tipo_admin="super_admin"
            )
            db.add(super_admin)
            db.commit()
            print("Super administrador criado com sucesso!")
            print("Email: admin@prm.gov.mz")
            print("Senha: admin123")
        else:
            print("Super administrador já existe!")
    except Exception as e:
        print(f"Erro ao criar super administrador: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Inicializando banco de dados...")
    init_db()
    create_superuser()
