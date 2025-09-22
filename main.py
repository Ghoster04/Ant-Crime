from fastapi import FastAPI, Depends, HTTPException, status, WebSocket, WebSocketDisconnect, File, UploadFile, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Annotated
from contextlib import asynccontextmanager
import json
import os
import uuid
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext

# Imports locais
from database import get_db, init_db, engine
from models import Admin, Usuario, Dispositivo, Emergencia, LogSistema, PingDispositivo
import schemas

# Importar configurações centralizadas
from config import settings

# Configurações de upload
UPLOAD_DIR = Path(settings.UPLOAD_DIR)
UPLOAD_DIR.mkdir(exist_ok=True)
MAX_FILE_SIZE = settings.MAX_FILE_SIZE
ALLOWED_EXTENSIONS = settings.ALLOWED_EXTENSIONS

# Lifespan event handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerenciar eventos de ciclo de vida da aplicação"""
    # Startup rápido
    print("🚀 AntiCrime 04 API iniciando...")
    
    # Inicializar banco em background (não bloquear)
    try:
        # Não aguardar inicialização do banco
        print("⚠️ Inicializando banco em background...")
    except Exception as e:
        print(f"⚠️ Banco será inicializado sob demanda: {e}")
    
    yield
    
    # Shutdown
    print("🛑 AntiCrime 04 API encerrando...")

# Inicializar FastAPI
app = FastAPI(
    title="AntiCrime 04 API",
    description="Sistema de Vigilância e Controle de Dispositivos - PRM Moçambique",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir arquivos estáticos (uploads)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Configuração de autenticação
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Gerenciador de conexões WebSocket
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Remover conexões quebradas
                self.active_connections.remove(connection)

manager = ConnectionManager()

# Funções auxiliares para upload de arquivos
def validate_file(file: UploadFile) -> bool:
    """Validar arquivo de upload"""
    if not file.filename:
        return False
    
    # Verificar extensão
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        return False
    
    return True

def save_upload_file(file: UploadFile, destination: Path) -> None:
    """Salvar arquivo de upload"""
    try:
        with destination.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    finally:
        file.file.close()

def generate_filename(original_filename: str) -> str:
    """Gerar nome único para arquivo"""
    file_ext = Path(original_filename).suffix.lower()
    unique_id = str(uuid.uuid4())
    return f"{unique_id}{file_ext}"

# Funções auxiliares de autenticação
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        admin_id: int = payload.get("sub")
        if admin_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    admin = db.query(Admin).filter(Admin.id == admin_id).first()
    if admin is None:
        raise credentials_exception
    return admin

# Banco de dados é inicializado no lifespan handler

# ROTAS DE AUTENTICAÇÃO
@app.post("/auth/login", response_model=schemas.Token)
def login(login_data: schemas.Login, db: Session = Depends(get_db)):
    """Login de administrador"""
    admin = db.query(Admin).filter(Admin.email == login_data.email).first()
    
    if not admin or not verify_password(login_data.senha, admin.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not admin.ativo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Conta desativada"
        )
    
    # Atualizar último login
    admin.ultimo_login = datetime.utcnow()
    db.commit()
    
    # Criar token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(admin.id)}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/auth/me", response_model=schemas.AdminResponse)
def read_users_me(current_admin: Admin = Depends(get_current_admin)):
    """Obter dados do admin logado"""
    return current_admin

# ROTAS DE ADMINS
@app.post("/admins/", response_model=schemas.AdminResponse)
def create_admin(
    admin: schemas.AdminCreate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """Criar novo administrador (apenas super_admin)"""
    if current_admin.tipo_admin != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas super administradores podem criar novos admins"
        )
    
    # Verificar se email já existe
    if db.query(Admin).filter(Admin.email == admin.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado"
        )
    
    # Verificar se badge já existe
    if db.query(Admin).filter(Admin.numero_badge == admin.numero_badge).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Número de badge já cadastrado"
        )
    
    # Criar admin
    hashed_password = get_password_hash(admin.senha)
    db_admin = Admin(
        nome_completo=admin.nome_completo,
        email=admin.email,
        senha_hash=hashed_password,
        numero_badge=admin.numero_badge,
        posto_policial=admin.posto_policial,
        tipo_admin=admin.tipo_admin,
        telefone=admin.telefone,
        criado_por=current_admin.id
    )
    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)
    
    return db_admin

@app.get("/admins/", response_model=List[schemas.AdminResponse])
def read_admins(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """Listar administradores"""
    admins = db.query(Admin).offset(skip).limit(limit).all()
    return admins

# ROTAS DE USUÁRIOS (JSON)
@app.post("/usuarios/", response_model=schemas.UsuarioResponse)
def create_usuario_json(
    usuario: schemas.UsuarioCreate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """Cadastrar novo usuário via JSON (sem foto)"""
    # Verificar se número de identidade já existe
    if db.query(Usuario).filter(Usuario.numero_identidade == usuario.numero_identidade).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Número de identidade já cadastrado"
        )
    
    # Criar usuário
    db_usuario = Usuario(
        **usuario.dict(),
        admin_cadastrador_id=current_admin.id
    )
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    
    return db_usuario

# ROTAS DE USUÁRIOS (MULTIPART/FORM-DATA)
@app.post("/usuarios/upload", response_model=schemas.UsuarioResponse)
async def create_usuario(
    # Dados do usuário via form
    nome_completo: Annotated[str, Form()],
    numero_identidade: Annotated[str, Form()],
    telefone_principal: Annotated[str, Form()],
    provincia: Annotated[str, Form()],
    cidade: Annotated[str, Form()],
    bairro: Annotated[str, Form()],
    latitude_residencia: Annotated[float, Form()],
    longitude_residencia: Annotated[float, Form()],
    
    # Campos opcionais
    telefone_emergencia: Annotated[str, Form()] = None,
    email: Annotated[str, Form()] = None,
    rua: Annotated[str, Form()] = None,
    numero_casa: Annotated[str, Form()] = None,
    ponto_referencia: Annotated[str, Form()] = None,
    observacoes: Annotated[str, Form()] = None,
    ativo: Annotated[bool, Form()] = True,
    
    # Arquivo de foto
    foto_residencia: UploadFile = File(None),
    
    # Dependências
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """Cadastrar novo usuário com foto da residência"""
    
    # Verificar se número de identidade já existe
    if db.query(Usuario).filter(Usuario.numero_identidade == numero_identidade).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Número de identidade já cadastrado"
        )
    
    # Validar coordenadas
    if not (-90 <= latitude_residencia <= 90):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Latitude deve estar entre -90 e 90"
        )
    
    if not (-180 <= longitude_residencia <= 180):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Longitude deve estar entre -180 e 180"
        )
    
    # Processar upload da foto
    foto_url = None
    if foto_residencia and foto_residencia.filename:
        # Validar arquivo
        if not validate_file(foto_residencia):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Arquivo inválido. Use apenas imagens: JPG, PNG, GIF, BMP, WEBP"
            )
        
        # Verificar tamanho do arquivo
        file_content = await foto_residencia.read()
        if len(file_content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Arquivo muito grande. Máximo {MAX_FILE_SIZE // (1024*1024)}MB"
            )
        
        # Gerar nome único e salvar arquivo
        filename = generate_filename(foto_residencia.filename)
        file_path = UPLOAD_DIR / filename
        
        # Salvar o conteúdo do arquivo
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        # URL para acessar a foto
        foto_url = f"/uploads/{filename}"
    
    # Criar usuário
    db_usuario = Usuario(
        nome_completo=nome_completo,
        numero_identidade=numero_identidade,
        telefone_principal=telefone_principal,
        telefone_emergencia=telefone_emergencia,
        email=email,
        provincia=provincia,
        cidade=cidade,
        bairro=bairro,
        rua=rua,
        numero_casa=numero_casa,
        ponto_referencia=ponto_referencia,
        latitude_residencia=latitude_residencia,
        longitude_residencia=longitude_residencia,
        foto_residencia=foto_url,
        observacoes=observacoes,
        ativo=ativo,
        admin_cadastrador_id=current_admin.id
    )
    
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    
    return db_usuario

@app.get("/usuarios/", response_model=List[schemas.UsuarioResponse])
def read_usuarios(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """Listar usuários com busca opcional"""
    query = db.query(Usuario)
    
    if search:
        query = query.filter(
            or_(
                Usuario.nome_completo.contains(search),
                Usuario.numero_identidade.contains(search),
                Usuario.telefone_principal.contains(search)
            )
        )
    
    usuarios = query.offset(skip).limit(limit).all()
    return usuarios

@app.get("/usuarios/{usuario_id}", response_model=schemas.UsuarioResponse)
def read_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """Obter usuário por ID"""
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario

@app.put("/usuarios/{usuario_id}", response_model=schemas.UsuarioResponse)
def update_usuario(
    usuario_id: int,
    usuario_update: schemas.UsuarioUpdate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """Atualizar usuário"""
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Atualizar campos
    update_data = usuario_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(usuario, field, value)
    
    db.commit()
    db.refresh(usuario)
    return usuario

@app.post("/usuarios/{usuario_id}/foto")
async def upload_foto_residencia(
    usuario_id: int,
    foto: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """Upload/atualizar foto da residência do usuário"""
    
    # Verificar se usuário existe
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Validar arquivo
    if not validate_file(foto):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Arquivo inválido. Use apenas imagens: JPG, PNG, GIF, BMP, WEBP"
        )
    
    # Verificar tamanho do arquivo
    file_content = await foto.read()
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Arquivo muito grande. Máximo {MAX_FILE_SIZE // (1024*1024)}MB"
        )
    
    # Remover foto anterior se existir
    if usuario.foto_residencia:
        old_filename = usuario.foto_residencia.split("/")[-1]
        old_file_path = UPLOAD_DIR / old_filename
        if old_file_path.exists():
            old_file_path.unlink()
    
    # Gerar nome único e salvar arquivo
    filename = generate_filename(foto.filename)
    file_path = UPLOAD_DIR / filename
    
    # Salvar o conteúdo do arquivo
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    # Atualizar URL da foto no usuário
    usuario.foto_residencia = f"/uploads/{filename}"
    db.commit()
    
    return {
        "message": "Foto atualizada com sucesso",
        "foto_url": usuario.foto_residencia
    }

# ROTAS DE DISPOSITIVOS
@app.post("/dispositivos/ping")
async def dispositivo_ping(
    ping_data: dict,
    db: Session = Depends(get_db)
):
    """Endpoint HTTP para dispositivos enviarem pings de localização"""
    # Validar dados obrigatórios
    required_fields = ["imei", "latitude", "longitude"]
    for field in required_fields:
        if field not in ping_data:
            raise HTTPException(status_code=400, detail=f"Campo {field} é obrigatório")
    
    imei = ping_data["imei"]
    lat = ping_data["latitude"]
    lng = ping_data["longitude"]
    bateria = ping_data.get("bateria", 0)
    precisao = ping_data.get("precisao", 0)
    device_status = ping_data.get("status", "ativo")
    tipo_ping = ping_data.get("tipo_ping", "device_ping")
    
    # Verificar se dispositivo existe
    dispositivo = db.query(Dispositivo).filter(Dispositivo.imei == imei).first()
    if not dispositivo:
        raise HTTPException(status_code=404, detail="Dispositivo não registrado no sistema")
    
    # Atualizar localização e último ping
    dispositivo.ultima_localizacao_lat = lat
    dispositivo.ultima_localizacao_lng = lng
    dispositivo.ultimo_ping = datetime.utcnow()
    
    # Atualizar status baseado no tipo de ping
    if tipo_ping == "stolen_device_ping" or device_status == "roubado":
        dispositivo.status = "roubado"
    elif dispositivo.status == "inativo":
        dispositivo.status = "ativo"
    
    # Registrar ping no histórico
    ping_record = PingDispositivo(
        dispositivo_id=dispositivo.id,
        latitude=lat,
        longitude=lng,
        precisao_gps=precisao,
        nivel_bateria=bateria,
        status_dispositivo=dispositivo.status,
        tipo_ping=tipo_ping,
        timestamp=datetime.utcnow()
    )
    db.add(ping_record)
    db.commit()
    
    # Buscar dados do usuário
    usuario = db.query(Usuario).filter(Usuario.id == dispositivo.usuario_id).first()
    
    # Notificar admins via WebSocket se conectados
    notification = {
        "type": "device_ping",
        "device_id": dispositivo.id,
        "imei": dispositivo.imei,
        "device_marca": dispositivo.marca,
        "device_modelo": dispositivo.modelo,
        "device_status": dispositivo.status,
        "usuario_id": dispositivo.usuario_id,
        "usuario_nome": usuario.nome_completo if usuario else "N/A",
        "latitude": lat,
        "longitude": lng,
        "bateria": bateria,
        "precisao_gps": precisao,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Se é dispositivo roubado, enviar alerta especial
    if dispositivo.status == "roubado":
        await manager.broadcast(json.dumps({
            "type": "stolen_device_located",
            "message": f"🚨 DISPOSITIVO ROUBADO LOCALIZADO!",
            "device_id": dispositivo.id,
            "imei": imei,
            "device_info": f"{dispositivo.marca} {dispositivo.modelo}",
            "user_name": usuario.nome_completo if usuario else "N/A",
            "latitude": lat,
            "longitude": lng,
            "bateria": bateria,
            "timestamp": datetime.utcnow().isoformat()
        }))
    else:
        # Ping normal
        await manager.broadcast(json.dumps(notification))
    
    return {
        "status": "success",
        "message": "Ping registrado com sucesso",
        "device_id": dispositivo.id,
        "device_status": dispositivo.status,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/dispositivos/register")
def register_dispositivo(
    dispositivo_data: dict,
    db: Session = Depends(get_db)
):
    """Registrar dispositivo pelo IMEI (usado pelo app móvel)"""
    imei = dispositivo_data.get("imei")
    if not imei:
        raise HTTPException(status_code=400, detail="IMEI é obrigatório")
    
    # Verificar se existe usuário cadastrado para este dispositivo
    dispositivo = db.query(Dispositivo).filter(Dispositivo.imei == imei).first()
    
    if not dispositivo:
        raise HTTPException(
            status_code=404, 
            detail="Dispositivo não cadastrado no sistema"
        )
    
    # Atualizar informações do dispositivo
    dispositivo.modelo = dispositivo_data.get("modelo", dispositivo.modelo)
    dispositivo.marca = dispositivo_data.get("marca", dispositivo.marca)
    dispositivo.sistema_operacional = dispositivo_data.get("sistema_operacional", dispositivo.sistema_operacional)
    dispositivo.versao_app = dispositivo_data.get("versao_app", dispositivo.versao_app)
    dispositivo.ultimo_ping = datetime.utcnow()
    
    db.commit()
    
    return {
        "status": "success",
        "message": "Dispositivo registrado com sucesso",
        "usuario_id": dispositivo.usuario_id,
        "dispositivo_id": dispositivo.id
    }

@app.post("/dispositivos/", response_model=schemas.DispositivoResponse)
def create_dispositivo(
    dispositivo: schemas.DispositivoCreate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """Cadastrar novo dispositivo para usuário"""
    # Verificar se IMEI já existe
    if db.query(Dispositivo).filter(Dispositivo.imei == dispositivo.imei).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="IMEI já cadastrado"
        )
    
    # Verificar se usuário existe
    usuario = db.query(Usuario).filter(Usuario.id == dispositivo.usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Criar dispositivo
    db_dispositivo = Dispositivo(**dispositivo.dict())
    db.add(db_dispositivo)
    db.commit()
    db.refresh(db_dispositivo)
    
    return db_dispositivo

@app.get("/dispositivos/", response_model=List[schemas.DispositivoResponse])
def read_dispositivos(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """Listar dispositivos com filtro de status opcional"""
    query = db.query(Dispositivo)
    
    if status_filter:
        query = query.filter(Dispositivo.status == status_filter)
    
    dispositivos = query.offset(skip).limit(limit).all()
    return dispositivos

@app.put("/dispositivos/{dispositivo_id}/status")
def update_dispositivo_status(
    dispositivo_id: int,
    status_data: dict,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """Atualizar status do dispositivo"""
    dispositivo = db.query(Dispositivo).filter(Dispositivo.id == dispositivo_id).first()
    if not dispositivo:
        raise HTTPException(status_code=404, detail="Dispositivo não encontrado")
    
    novo_status = status_data.get("status")
    if novo_status not in ["ativo", "inativo", "roubado", "recuperado", "bloqueado"]:
        raise HTTPException(status_code=400, detail="Status inválido")
    
    dispositivo.status = novo_status
    db.commit()
    
    return {"message": f"Status do dispositivo atualizado para {novo_status}"}

@app.put("/dispositivos/{dispositivo_id}/marcar-roubado")
async def marcar_dispositivo_roubado(
    dispositivo_id: int,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """Marcar dispositivo como roubado"""
    dispositivo = db.query(Dispositivo).filter(Dispositivo.id == dispositivo_id).first()
    
    if not dispositivo:
        raise HTTPException(status_code=404, detail="Dispositivo não encontrado")
    
    dispositivo.status = "roubado"
    db.commit()
    
    # Notificar admins
    await manager.broadcast(json.dumps({
        "type": "device_status_changed",
        "device_id": dispositivo_id,
        "new_status": "roubado",
        "message": f"Dispositivo {dispositivo.marca} {dispositivo.modelo} marcado como ROUBADO",
        "imei": dispositivo.imei
    }))
    
    return {"message": "Dispositivo marcado como roubado", "device_id": dispositivo_id}

@app.put("/dispositivos/{dispositivo_id}/marcar-recuperado")  
async def marcar_dispositivo_recuperado(
    dispositivo_id: int,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """Marcar dispositivo como recuperado"""
    dispositivo = db.query(Dispositivo).filter(Dispositivo.id == dispositivo_id).first()
    
    if not dispositivo:
        raise HTTPException(status_code=404, detail="Dispositivo não encontrado")
    
    dispositivo.status = "recuperado"
    db.commit()
    
    # Notificar admins
    await manager.broadcast(json.dumps({
        "type": "device_status_changed", 
        "device_id": dispositivo_id,
        "new_status": "recuperado",
        "message": f"✅ Dispositivo {dispositivo.marca} {dispositivo.modelo} foi RECUPERADO!",
        "imei": dispositivo.imei
    }))
    
    return {"message": "Dispositivo marcado como recuperado", "device_id": dispositivo_id}

@app.get("/dispositivos/pings-roubados")
def get_pings_dispositivos_roubados(
    skip: int = 0,
    limit: int = 100,
    dispositivo_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """Buscar histórico de pings de dispositivos roubados"""
    query = db.query(PingDispositivo).join(Dispositivo)
    
    # Filtrar apenas dispositivos com status roubado ou que já foram roubados
    if dispositivo_id:
        query = query.filter(PingDispositivo.dispositivo_id == dispositivo_id)
    else:
        query = query.filter(or_(
            Dispositivo.status == "roubado",
            PingDispositivo.status_dispositivo == "roubado"
        ))
    
    # Ordenar por timestamp mais recente primeiro
    query = query.order_by(PingDispositivo.timestamp.desc())
    
    # Paginação
    pings = query.offset(skip).limit(limit).all()
    
    # Formatar resposta com informações do dispositivo
    result = []
    for ping in pings:
        dispositivo = ping.dispositivo
        usuario = dispositivo.usuario if dispositivo else None
        
        result.append({
            "id": ping.id,
            "timestamp": ping.timestamp.isoformat(),
            "latitude": ping.latitude,
            "longitude": ping.longitude,
            "precisao_gps": ping.precisao_gps,
            "nivel_bateria": ping.nivel_bateria,
            "status_dispositivo": ping.status_dispositivo,
            "tipo_ping": ping.tipo_ping,
            "dispositivo": {
                "id": dispositivo.id,
                "imei": dispositivo.imei,
                "marca": dispositivo.marca,
                "modelo": dispositivo.modelo,
                "status": dispositivo.status
            },
            "usuario": {
                "id": usuario.id,
                "nome": usuario.nome_completo,
                "telefone": usuario.telefone_principal
            } if usuario else None
        })
    
    return result

# ROTAS DE EMERGÊNCIAS
@app.post("/emergencias/sos")
async def create_emergencia(
    emergencia_data: dict,
    db: Session = Depends(get_db)
):
    """Acionar emergência (SOS) - usado pelo app móvel"""
    # Validar dados obrigatórios
    required_fields = ["dispositivo_id", "latitude", "longitude"]
    for field in required_fields:
        if field not in emergencia_data:
            raise HTTPException(status_code=400, detail=f"Campo {field} é obrigatório")
    
    # Verificar se dispositivo existe
    dispositivo = db.query(Dispositivo).filter(
        Dispositivo.id == emergencia_data["dispositivo_id"]
    ).first()
    
    if not dispositivo:
        raise HTTPException(status_code=404, detail="Dispositivo não encontrado")
    
    # Criar emergência
    emergencia = Emergencia(
        usuario_id=dispositivo.usuario_id,
        dispositivo_id=emergencia_data["dispositivo_id"],
        latitude=emergencia_data["latitude"],
        longitude=emergencia_data["longitude"],
        nivel_bateria=emergencia_data.get("nivel_bateria"),
        precisao_gps=emergencia_data.get("precisao_gps")
    )
    
    db.add(emergencia)
    db.commit()
    db.refresh(emergencia)
    
    # Atualizar localização do dispositivo
    dispositivo.ultima_localizacao_lat = emergencia_data["latitude"]
    dispositivo.ultima_localizacao_lng = emergencia_data["longitude"]
    dispositivo.ultimo_ping = datetime.utcnow()
    db.commit()
    
    # Enviar notificação via WebSocket para todos os admins conectados
    usuario = db.query(Usuario).filter(Usuario.id == dispositivo.usuario_id).first()
    
    notification = {
        "type": "emergency_created",
        "emergency_id": emergencia.id,
        "device_id": dispositivo.id,
        "device_marca": dispositivo.marca,
        "device_modelo": dispositivo.modelo,
        "device_imei": dispositivo.imei,
        "user_id": usuario.id,
        "user_name": usuario.nome_completo,
        "user_phone": usuario.telefone_principal,
        "user_address": f"{usuario.rua}, {usuario.bairro}, {usuario.cidade}",
        "latitude": emergencia.latitude,
        "longitude": emergencia.longitude,
        "timestamp": emergencia.timestamp_acionamento.isoformat(),
        "battery_level": emergencia.nivel_bateria,
        "gps_accuracy": emergencia.precisao_gps
    }
    
    await manager.broadcast(json.dumps(notification))
    
    return {
        "status": "success",
        "message": "Emergência registrada com sucesso",
        "emergency_id": emergencia.id
    }

@app.get("/emergencias/", response_model=List[schemas.EmergenciaResponse])
def read_emergencias(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """Listar emergências com filtro de status"""
    query = db.query(Emergencia)
    
    if status_filter:
        query = query.filter(Emergencia.status == status_filter)
    
    emergencias = query.order_by(Emergencia.timestamp_acionamento.desc()).offset(skip).limit(limit).all()
    return emergencias

@app.get("/emergencias/ativas", response_model=List[schemas.EmergenciaResponse])
def read_emergencias_ativas(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """Listar apenas emergências ativas"""
    emergencias = db.query(Emergencia).filter(
        Emergencia.status == "ativo"
    ).order_by(Emergencia.timestamp_acionamento.desc()).all()
    return emergencias

@app.put("/emergencias/{emergencia_id}/responder")
async def responder_emergencia(
    emergencia_id: int,
    resposta_data: dict,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """Responder a uma emergência"""
    emergencia = db.query(Emergencia).filter(Emergencia.id == emergencia_id).first()
    if not emergencia:
        raise HTTPException(status_code=404, detail="Emergência não encontrada")
    
    # Atualizar emergência
    emergencia.status = "respondido"
    emergencia.admin_responsavel_id = current_admin.id
    emergencia.timestamp_resposta = datetime.utcnow()
    
    # Calcular tempo de resposta em minutos
    tempo_resposta = (emergencia.timestamp_resposta - emergencia.timestamp_acionamento).total_seconds() / 60
    emergencia.tempo_resposta = int(tempo_resposta)
    
    if "observacoes" in resposta_data:
        emergencia.observacoes_admin = resposta_data["observacoes"]
    
    db.commit()
    
    # Notificar via WebSocket
    notification = {
        "type": "emergency_response",
        "emergency_id": emergencia.id,
        "admin_name": current_admin.nome_completo,
        "response_time": emergencia.tempo_resposta,
        "timestamp": emergencia.timestamp_resposta.isoformat()
    }
    
    await manager.broadcast(json.dumps(notification))
    
    return {"message": "Emergência respondida com sucesso"}

@app.put("/emergencias/{emergencia_id}/finalizar")
def finalizar_emergencia(
    emergencia_id: int,
    finalizacao_data: dict,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """Finalizar uma emergência"""
    emergencia = db.query(Emergencia).filter(Emergencia.id == emergencia_id).first()
    if not emergencia:
        raise HTTPException(status_code=404, detail="Emergência não encontrada")
    
    emergencia.status = "finalizado"
    emergencia.timestamp_finalizacao = datetime.utcnow()
    
    if "observacoes" in finalizacao_data:
        emergencia.observacoes_admin = finalizacao_data["observacoes"]
    
    db.commit()
    
    return {"message": "Emergência finalizada com sucesso"}

# ROTAS DE ESTATÍSTICAS
@app.get("/dashboard/stats", response_model=schemas.EstatisticasResponse)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """Obter estatísticas para o dashboard"""
    stats = {
        "total_usuarios": db.query(Usuario).count(),
        "total_dispositivos": db.query(Dispositivo).count(),
        "total_emergencias": db.query(Emergencia).count(),
        "emergencias_ativas": db.query(Emergencia).filter(Emergencia.status == "ativo").count(),
        "dispositivos_roubados": db.query(Dispositivo).filter(Dispositivo.status == "roubado").count(),
        "usuarios_ativos": db.query(Usuario).filter(Usuario.ativo == True).count()
    }
    return stats

# WEBSOCKET PARA COMUNICAÇÃO EM TEMPO REAL
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket para comunicação em tempo real com admins"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Tentar interpretar mensagens JSON vindas de dispositivos (emulador)
            try:
                payload = json.loads(data)
            except Exception:
                # Echo para compatibilidade antiga
                await manager.send_personal_message(f"Echo: {data}", websocket)
                continue

            msg_type = payload.get("type")
            if msg_type == "device_ping" or msg_type == "stolen_device_ping":
                # Esperado: { type, imei, latitude, longitude, bateria?, precisao?, status? }
                imei = payload.get("imei")
                lat = payload.get("latitude")
                lng = payload.get("longitude")
                bateria = payload.get("bateria", 0)
                precisao = payload.get("precisao", 0)
                device_status = payload.get("status")
                
                # Atualizar no banco e retransmitir
                db_gen = get_db()
                db = next(db_gen)
                try:
                    dispositivo = db.query(Dispositivo).filter(Dispositivo.imei == imei).first()
                    if dispositivo:
                        # Atualizar localização e último ping
                        dispositivo.ultima_localizacao_lat = lat
                        dispositivo.ultima_localizacao_lng = lng
                        dispositivo.ultimo_ping = datetime.utcnow()
                        
                        # Atualizar status baseado no tipo de ping
                        if msg_type == "stolen_device_ping" or device_status == "roubado":
                            dispositivo.status = "roubado"
                        elif dispositivo.status == "inativo":
                            dispositivo.status = "ativo"
                        
                        # Registrar ping no histórico
                        ping_record = PingDispositivo(
                            dispositivo_id=dispositivo.id,
                            latitude=lat,
                            longitude=lng,
                            precisao_gps=precisao,
                            nivel_bateria=bateria,
                            status_dispositivo=dispositivo.status,
                            tipo_ping=msg_type,
                            timestamp=datetime.utcnow()
                        )
                        db.add(ping_record)
                        db.commit()

                        usuario = db.query(Usuario).filter(Usuario.id == dispositivo.usuario_id).first()
                        
                        # Broadcast para todos admins conectados
                        notification = {
                            "type": "device_ping",
                            "device_id": dispositivo.id,
                            "imei": dispositivo.imei,
                            "device_marca": dispositivo.marca,
                            "device_modelo": dispositivo.modelo,
                            "device_status": dispositivo.status,
                            "usuario_id": dispositivo.usuario_id,
                            "usuario_nome": usuario.nome_completo if usuario else "N/A",
                            "latitude": lat,
                            "longitude": lng,
                            "bateria": bateria,
                            "precisao_gps": precisao,
                            "timestamp": datetime.utcnow().isoformat()
                        }
                        
                        await manager.broadcast(json.dumps(notification))
                        
                        # Se é dispositivo roubado, enviar alerta especial
                        if dispositivo.status == "roubado":
                            await manager.broadcast(json.dumps({
                                "type": "stolen_device_located",
                                "message": f"🚨 DISPOSITIVO ROUBADO LOCALIZADO!",
                                "device_id": dispositivo.id,
                                "imei": imei,
                                "device_info": f"{dispositivo.marca} {dispositivo.modelo}",
                                "user_name": usuario.nome_completo if usuario else "N/A",
                                "latitude": lat,
                                "longitude": lng,
                                "bateria": bateria,
                                "timestamp": datetime.utcnow().isoformat()
                            }))
                    else:
                        # Dispositivo desconhecido; apenas ecoar erro ao remetente
                        await manager.send_personal_message(json.dumps({
                            "type": "error",
                            "message": "Dispositivo não registrado no sistema",
                            "imei": imei
                        }), websocket)
                finally:
                    try:
                        next(db_gen)
                    except StopIteration:
                        pass
            elif msg_type == "device_sos":
                # Criar emergência no banco a partir do IMEI recebido e coordenadas
                imei = payload.get("imei")
                lat = payload.get("latitude")
                lng = payload.get("longitude")
                nivel_bateria = payload.get("bateria")
                precisao_gps = payload.get("precisao")

                db_gen = get_db()
                db = next(db_gen)
                try:
                    dispositivo = db.query(Dispositivo).filter(Dispositivo.imei == imei).first()
                    if not dispositivo:
                        await manager.send_personal_message(json.dumps({
                            "type": "error",
                            "message": "Dispositivo não registrado",
                            "imei": imei
                        }), websocket)
                    else:
                        emergencia = Emergencia(
                            usuario_id=dispositivo.usuario_id,
                            dispositivo_id=dispositivo.id,
                            latitude=lat,
                            longitude=lng,
                            status="ativo",
                            nivel_bateria=nivel_bateria,
                            precisao_gps=precisao_gps
                        )
                        db.add(emergencia)
                        # Atualizar "ultimo ping" e localização do device
                        dispositivo.ultima_localizacao_lat = lat
                        dispositivo.ultima_localizacao_lng = lng
                        dispositivo.ultimo_ping = datetime.utcnow()
                        db.commit()
                        db.refresh(emergencia)

                        # Buscar dados do usuário
                        usuario = db.query(Usuario).filter(Usuario.id == dispositivo.usuario_id).first()
                        
                        await manager.broadcast(json.dumps({
                            "type": "emergency_created",
                            "emergency_id": emergencia.id,
                            "device_id": dispositivo.id,
                            "device_marca": dispositivo.marca,
                            "device_modelo": dispositivo.modelo,
                            "device_imei": dispositivo.imei,
                            "user_id": dispositivo.usuario_id,
                            "user_name": usuario.nome_completo if usuario else "N/A",
                            "user_phone": usuario.telefone_principal if usuario else "N/A",
                            "user_address": f"{usuario.rua}, {usuario.bairro}, {usuario.cidade}" if usuario else "N/A",
                            "latitude": lat,
                            "longitude": lng,
                            "timestamp": emergencia.timestamp_acionamento.isoformat(),
                            "battery_level": nivel_bateria,
                            "gps_accuracy": precisao_gps
                        }))
                finally:
                    try:
                        next(db_gen)
                    except StopIteration:
                        pass
            else:
                # Mensagem não reconhecida, ecoar
                await manager.send_personal_message(json.dumps({"type": "echo", "data": payload}), websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# ROTA DE SAÚDE
@app.get("/health")
def health_check():
    """Verificar saúde da API"""
    db_status = "unknown"
    try:
        if engine is not None:
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            db_status = "connected"
        else:
            db_status = "not_configured"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "database": db_status
    }

# ROTA DE TESTE DE BANCO
@app.get("/test-db")
def test_database():
    """Testar conexão com banco de dados"""
    try:
        if engine is None:
            return {
                "status": "error",
                "message": "Engine do banco não configurado",
                "details": "Verifique as configurações de conexão"
            }
        
        with engine.connect() as conn:
            result = conn.execute("SELECT VERSION() as version")
            mysql_version = result.fetchone()[0]
            
            return {
                "status": "success",
                "message": "Conexão com MySQL estabelecida",
                "mysql_version": mysql_version,
                "database_url": settings.database_url
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erro ao conectar com banco: {str(e)}",
            "database_url": settings.database_url,
            "error_type": type(e).__name__
        }
@app.get("/health")
def health():
    return {"status": "ok"}
# ROTA PARA INICIALIZAR BANCO
@app.post("/init-db")
def initialize_database():
    """Inicializar banco de dados sob demanda"""
    try:
        if init_db():
            return {
                "status": "success",
                "message": "Banco de dados inicializado com sucesso"
            }
        else:
            return {
                "status": "warning",
                "message": "Banco de dados não pôde ser inicializado"
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erro ao inicializar banco: {str(e)}"
        }
import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # usa a PORT do Railway
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=False)
