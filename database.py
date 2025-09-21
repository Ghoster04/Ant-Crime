from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Configurações diretas no código
DATABASE_URL = "sqlite:///./anticrime04.db"
DEBUG = False

# Configurações específicas para SQLite
sqlite_connect_args = {
    "check_same_thread": False,
    "isolation_level": None,
}

# Criar engine
engine = create_engine(
    DATABASE_URL,
    echo=DEBUG,
    connect_args=sqlite_connect_args,
    pool_pre_ping=True
)

# Criar sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para os modelos
Base = declarative_base()

def get_db():
    """
    Dependency para obter sessão do banco de dados
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    Inicializar banco de dados - criar todas as tabelas
    """
    from models import Base
    Base.metadata.create_all(bind=engine)
    print("Banco de dados inicializado com sucesso!")

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
