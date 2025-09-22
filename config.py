"""
Configurações da aplicação AntiCrime 04
"""
import os
from typing import Optional

class Settings:
    """Configurações da aplicação"""
    
    # Configurações do Banco de Dados
    # Para Railway (produção): mysql.railway.internal (só funciona dentro do Railway)
    # Para desenvolvimento local: usar URL externa do Railway ou SQLite
    MYSQL_HOST: str = os.getenv("MYSQL_HOST", "mysql.railway.internal")
    MYSQL_PORT: int = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_DATABASE: str = os.getenv("MYSQL_DATABASE", "railway")
    MYSQL_USER: str = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "qmWIuOIpYLNOJcSdpKumbxNcQJPmalAO")
    
    # URL externa do Railway MySQL (para desenvolvimento local)
    MYSQL_EXTERNAL_HOST: str = os.getenv("MYSQL_EXTERNAL_HOST", "turntable.proxy.rlwy.net")
    MYSQL_EXTERNAL_PORT: int = int(os.getenv("MYSQL_EXTERNAL_PORT", "28897"))
    
    # Configurações da Aplicação
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    USE_LOCAL_DB: bool = os.getenv("USE_LOCAL_DB", "False").lower() == "true"
    
    # Configurações de Segurança
    SECRET_KEY: str = os.getenv("SECRET_KEY", "sua_chave_secreta_muito_segura_aqui_mude_em_producao")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Configurações de Upload
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "5242880"))  # 5MB
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
    ALLOWED_EXTENSIONS: set = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}
    
    # Configurações do Servidor
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    @property
    def database_url(self) -> str:
        """Retorna a URL de conexão com o banco de dados"""
        if self.USE_LOCAL_DB or self.DEBUG:
            # Usar SQLite para desenvolvimento local
            return "sqlite:///./anticrime04.db"
        else:
            # Sempre usar MySQL em produção
            # Detectar se estamos rodando no Railway ou localmente
            if self._is_railway_environment():
                # Dentro do Railway: usar mysql.railway.internal
                mysql_url = f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
            else:
                # Desenvolvimento local: usar URL externa do Railway
                mysql_url = f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_EXTERNAL_HOST}:{self.MYSQL_EXTERNAL_PORT}/{self.MYSQL_DATABASE}"
            
            print(f"🔗 Conectando ao MySQL: {mysql_url}")
            return mysql_url
    
    def _is_railway_environment(self) -> bool:
        """Detecta se estamos rodando no Railway"""
        return (
            os.getenv("RAILWAY_ENVIRONMENT") is not None or
            os.getenv("RAILWAY_PROJECT_ID") is not None or
            "railway" in os.getenv("HOSTNAME", "").lower()
        )
    
    @property
    def connect_args(self) -> dict:
        """Retorna argumentos de conexão específicos do banco"""
        if self.USE_LOCAL_DB or self.DEBUG:
            # Configurações para SQLite
            return {
                "check_same_thread": False,
                "isolation_level": None,
            }
        else:
            # Configurações para MySQL
            return {
                "charset": "utf8mb4",
                "autocommit": False,
            }

# Instância global das configurações
settings = Settings()

# Configurações específicas para diferentes ambientes
class DevelopmentSettings(Settings):
    """Configurações para desenvolvimento"""
    DEBUG: bool = True
    USE_LOCAL_DB: bool = True
    SECRET_KEY: str = "dev_secret_key_not_for_production"

class ProductionSettings(Settings):
    """Configurações para produção"""
    DEBUG: bool = False
    USE_LOCAL_DB: bool = False
    # As credenciais MySQL serão definidas via variáveis de ambiente

# Função para obter configurações baseadas no ambiente
def get_settings() -> Settings:
    """Retorna configurações baseadas no ambiente"""
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    if env == "production":
        return ProductionSettings()
    else:
        return DevelopmentSettings()
