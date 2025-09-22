from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship, DeclarativeBase
from datetime import datetime
import enum

# Importar Base do database.py para evitar conflitos
from database import Base

class StatusEmergencia(enum.Enum):
    ATIVO = "ativo"
    RESPONDIDO = "respondido"
    FINALIZADO = "finalizado"
    FALSO_ALARME = "falso_alarme"

class TipoAdmin(enum.Enum):
    SUPER_ADMIN = "super_admin"
    OPERADOR = "operador"
    SUPERVISOR = "supervisor"

class StatusDispositivo(enum.Enum):
    ATIVO = "ativo"
    INATIVO = "inativo"
    ROUBADO = "roubado"
    RECUPERADO = "recuperado"
    BLOQUEADO = "bloqueado"

class Admin(Base):
    __tablename__ = 'admins'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome_completo = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)
    numero_badge = Column(String(50), unique=True, nullable=False)  # Número de identificação policial
    posto_policial = Column(String(100), nullable=False)  # Ex: "PRM Maputo Central"
    tipo_admin = Column(String(20), default="operador")
    telefone = Column(String(20))
    ativo = Column(Boolean, default=True)
    data_criacao = Column(DateTime, default=datetime.utcnow)
    ultimo_login = Column(DateTime)
    criado_por = Column(Integer, ForeignKey('admins.id'))  # Admin que criou este usuário
    
    # Relacionamentos
    usuarios_cadastrados = relationship("Usuario", back_populates="admin_cadastrador")
    emergencias_atendidas = relationship("Emergencia", back_populates="admin_responsavel")

class Usuario(Base):
    __tablename__ = 'usuarios'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome_completo = Column(String(255), nullable=False)
    numero_identidade = Column(String(50), unique=True, nullable=False)  # BI ou Passaporte
    telefone_principal = Column(String(20), nullable=False)
    telefone_emergencia = Column(String(20))  # Contato de emergência
    email = Column(String(255))
    
    # Endereço detalhado
    provincia = Column(String(100), nullable=False)
    cidade = Column(String(100), nullable=False)
    bairro = Column(String(100), nullable=False)
    rua = Column(String(255))
    numero_casa = Column(String(20))
    ponto_referencia = Column(Text)
    
    # Coordenadas da residência
    latitude_residencia = Column(Float, nullable=False)
    longitude_residencia = Column(Float, nullable=False)
    
    # Informações adicionais
    foto_residencia = Column(String(500))  # URL/caminho da foto
    observacoes = Column(Text)
    ativo = Column(Boolean, default=True)
    
    # Metadados
    data_cadastro = Column(DateTime, default=datetime.utcnow)
    admin_cadastrador_id = Column(Integer, ForeignKey('admins.id'), nullable=False)
    
    # Relacionamentos
    admin_cadastrador = relationship("Admin", back_populates="usuarios_cadastrados")
    dispositivos = relationship("Dispositivo", back_populates="usuario")
    emergencias = relationship("Emergencia", back_populates="usuario")

class Dispositivo(Base):
    __tablename__ = 'dispositivos'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    imei = Column(String(20), unique=True, nullable=False)  # Identificador único
    modelo = Column(String(100))
    marca = Column(String(50))
    sistema_operacional = Column(String(50))  # Android/iOS
    versao_app = Column(String(20))
    
    # Status e controle
    status = Column(String(20), default="ativo")
    data_primeiro_registro = Column(DateTime, default=datetime.utcnow)
    ultima_localizacao_lat = Column(Float)
    ultima_localizacao_lng = Column(Float)
    ultimo_ping = Column(DateTime)  # Última vez que o app enviou sinal
    
    # Relacionamento com usuário
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    
    # Metadados
    data_cadastro = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    usuario = relationship("Usuario", back_populates="dispositivos")
    emergencias = relationship("Emergencia", back_populates="dispositivo")
    pings = relationship("PingDispositivo", back_populates="dispositivo")

class Emergencia(Base):
    __tablename__ = 'emergencias'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Informações da emergência
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    timestamp_acionamento = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default="ativo")
    
    # Relacionamentos
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    dispositivo_id = Column(Integer, ForeignKey('dispositivos.id'), nullable=False)
    admin_responsavel_id = Column(Integer, ForeignKey('admins.id'))
    
    # Informações de resposta
    tempo_resposta = Column(Integer)  # Em minutos
    timestamp_resposta = Column(DateTime)
    timestamp_finalizacao = Column(DateTime)
    observacoes_admin = Column(Text)
    
    # Dados adicionais do contexto
    nivel_bateria = Column(Integer)  # Nível da bateria quando acionado
    precisao_gps = Column(Float)  # Precisão do GPS em metros
    
    # Relacionamentos
    usuario = relationship("Usuario", back_populates="emergencias")
    dispositivo = relationship("Dispositivo", back_populates="emergencias")
    admin_responsavel = relationship("Admin", back_populates="emergencias_atendidas")

class PingDispositivo(Base):
    __tablename__ = 'pings_dispositivos'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    dispositivo_id = Column(Integer, ForeignKey('dispositivos.id'), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    precisao_gps = Column(Float)
    nivel_bateria = Column(Integer)
    status_dispositivo = Column(String(20))  # online, offline, roubado
    tipo_ping = Column(String(30))  # device_ping, stolen_device_ping
    
    # Relacionamento
    dispositivo = relationship("Dispositivo", back_populates="pings")

class LogSistema(Base):
    __tablename__ = 'logs_sistema'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    nivel = Column(String(20))  # INFO, WARNING, ERROR, CRITICAL
    modulo = Column(String(100))  # Módulo do sistema que gerou o log
    mensagem = Column(Text, nullable=False)
    detalhes = Column(Text)  # JSON com detalhes adicionais
    
    # Relacionamentos opcionais
    admin_id = Column(Integer, ForeignKey('admins.id'))
    usuario_id = Column(Integer, ForeignKey('usuarios.id'))
    dispositivo_id = Column(Integer, ForeignKey('dispositivos.id'))

class ConfiguracaoSistema(Base):
    __tablename__ = 'configuracoes_sistema'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    chave = Column(String(100), unique=True, nullable=False)
    valor = Column(Text, nullable=False)
    descricao = Column(Text)
    data_modificacao = Column(DateTime, default=datetime.utcnow)
    modificado_por = Column(Integer, ForeignKey('admins.id'))
