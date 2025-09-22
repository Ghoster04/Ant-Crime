from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum

# Enums
class StatusEmergenciaSchema(str, Enum):
    ATIVO = "ativo"
    RESPONDIDO = "respondido"
    FINALIZADO = "finalizado"
    FALSO_ALARME = "falso_alarme"

class TipoAdminSchema(str, Enum):
    SUPER_ADMIN = "super_admin"
    OPERADOR = "operador"
    SUPERVISOR = "supervisor"

class StatusDispositivoSchema(str, Enum):
    ATIVO = "ativo"
    INATIVO = "inativo"
    ROUBADO = "roubado"
    RECUPERADO = "recuperado"
    BLOQUEADO = "bloqueado"

# Schemas para Admin
class AdminBase(BaseModel):
    nome_completo: str
    email: EmailStr
    numero_badge: str
    posto_policial: str
    tipo_admin: TipoAdminSchema = TipoAdminSchema.OPERADOR
    telefone: Optional[str] = None
    ativo: bool = True

class AdminCreate(AdminBase):
    senha: str
    
    @field_validator('senha')
    @classmethod
    def validate_senha(cls, v):
        if len(v) < 6:
            raise ValueError('Senha deve ter pelo menos 6 caracteres')
        return v

class AdminUpdate(BaseModel):
    nome_completo: Optional[str] = None
    email: Optional[EmailStr] = None
    numero_badge: Optional[str] = None
    posto_policial: Optional[str] = None
    tipo_admin: Optional[TipoAdminSchema] = None
    telefone: Optional[str] = None
    ativo: Optional[bool] = None

class AdminResponse(AdminBase):
    id: int
    data_criacao: datetime
    ultimo_login: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

# Schemas para Usuario
class UsuarioBase(BaseModel):
    nome_completo: str
    numero_identidade: str
    telefone_principal: str
    telefone_emergencia: Optional[str] = None
    email: Optional[EmailStr] = None
    provincia: str
    cidade: str
    bairro: str
    rua: Optional[str] = None
    numero_casa: Optional[str] = None
    ponto_referencia: Optional[str] = None
    latitude_residencia: float
    longitude_residencia: float
    foto_residencia: Optional[str] = None
    observacoes: Optional[str] = None
    ativo: bool = True

class UsuarioCreate(UsuarioBase):
    @field_validator('latitude_residencia')
    @classmethod
    def validate_latitude(cls, v):
        if not -90 <= v <= 90:
            raise ValueError('Latitude deve estar entre -90 e 90')
        return v
    
    @field_validator('longitude_residencia')
    @classmethod
    def validate_longitude(cls, v):
        if not -180 <= v <= 180:
            raise ValueError('Longitude deve estar entre -180 e 180')
        return v

class UsuarioUpdate(BaseModel):
    nome_completo: Optional[str] = None
    telefone_principal: Optional[str] = None
    telefone_emergencia: Optional[str] = None
    email: Optional[EmailStr] = None
    provincia: Optional[str] = None
    cidade: Optional[str] = None
    bairro: Optional[str] = None
    rua: Optional[str] = None
    numero_casa: Optional[str] = None
    ponto_referencia: Optional[str] = None
    latitude_residencia: Optional[float] = None
    longitude_residencia: Optional[float] = None
    foto_residencia: Optional[str] = None
    observacoes: Optional[str] = None
    ativo: Optional[bool] = None

class UsuarioResponse(UsuarioBase):
    id: int
    data_cadastro: datetime
    admin_cadastrador_id: int
    
    model_config = ConfigDict(from_attributes=True)

# Schemas para Dispositivo
class DispositivoBase(BaseModel):
    imei: str
    modelo: Optional[str] = None
    marca: Optional[str] = None
    sistema_operacional: Optional[str] = None
    versao_app: Optional[str] = None
    status: StatusDispositivoSchema = StatusDispositivoSchema.ATIVO

class DispositivoCreate(DispositivoBase):
    usuario_id: int
    
    @field_validator('imei')
    @classmethod
    def validate_imei(cls, v):
        if len(v) != 15:
            raise ValueError('IMEI deve ter exatamente 15 dígitos')
        if not v.isdigit():
            raise ValueError('IMEI deve conter apenas números')
        return v

class DispositivoUpdate(BaseModel):
    modelo: Optional[str] = None
    marca: Optional[str] = None
    sistema_operacional: Optional[str] = None
    versao_app: Optional[str] = None
    status: Optional[StatusDispositivoSchema] = None
    ultima_localizacao_lat: Optional[float] = None
    ultima_localizacao_lng: Optional[float] = None

class DispositivoResponse(DispositivoBase):
    id: int
    usuario_id: int
    data_primeiro_registro: datetime
    data_cadastro: datetime
    ultima_localizacao_lat: Optional[float] = None
    ultima_localizacao_lng: Optional[float] = None
    ultimo_ping: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

# Schemas para Emergencia
class EmergenciaBase(BaseModel):
    latitude: float
    longitude: float
    nivel_bateria: Optional[int] = None
    precisao_gps: Optional[float] = None

class EmergenciaCreate(EmergenciaBase):
    dispositivo_id: int
    
    @field_validator('latitude')
    @classmethod
    def validate_latitude(cls, v):
        if not -90 <= v <= 90:
            raise ValueError('Latitude deve estar entre -90 e 90')
        return v
    
    @field_validator('longitude')
    @classmethod
    def validate_longitude(cls, v):
        if not -180 <= v <= 180:
            raise ValueError('Longitude deve estar entre -180 e 180')
        return v

class EmergenciaUpdate(BaseModel):
    status: Optional[StatusEmergenciaSchema] = None
    admin_responsavel_id: Optional[int] = None
    observacoes_admin: Optional[str] = None

class EmergenciaResponse(EmergenciaBase):
    id: int
    usuario_id: int
    dispositivo_id: int
    timestamp_acionamento: datetime
    status: StatusEmergenciaSchema
    admin_responsavel_id: Optional[int] = None
    tempo_resposta: Optional[int] = None
    timestamp_resposta: Optional[datetime] = None
    timestamp_finalizacao: Optional[datetime] = None
    observacoes_admin: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

# Schemas para autenticação
class Login(BaseModel):
    email: EmailStr
    senha: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    admin_id: Optional[int] = None

# Schema para estatísticas
class EstatisticasResponse(BaseModel):
    total_usuarios: int
    total_dispositivos: int
    total_emergencias: int
    emergencias_ativas: int
    dispositivos_roubados: int
    usuarios_ativos: int
