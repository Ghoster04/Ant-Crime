# Backend AntiCrime 04

## 🚀 Configuração Rápida

### Setup Automático (Recomendado)
```bash
cd backend/
python setup.py
```

### Setup Manual (se necessário)

#### 1. Instalar Dependências
```bash
pip install -r requirements.txt
```

#### 2. Inicializar Banco de Dados
```bash
python database.py
```

**Nota:** Todas as configurações estão diretamente no código, não são necessários arquivos externos (.env, config.py, etc.)

### 4. Executar Sistema
```bash
# Desenvolvimento
python main.py

# ou
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Produção
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 5. Testar API
```bash
python test_api.py
```

## 📁 Estrutura do Projeto

```
backend/
├── models.py           # Modelos SQLAlchemy (Tabelas)
├── schemas.py          # Schemas Pydantic (Validação)
├── database.py         # Configuração do banco
├── requirements.txt    # Dependências Python
├── config_example.env  # Exemplo de configuração
├── DATABASE_DESIGN.md  # Documentação do banco
└── README.md          # Este arquivo
```

## 🗄️ Modelos de Dados

### Admin (Policiais PRM)
- Gerenciam o sistema
- Cadastram usuários
- Respondem emergências

### Usuario (Cidadãos)
- Cadastrados pelos policiais
- Recebem app pré-configurado
- Podem acionar SOS

### Dispositivo (Smartphones)
- Identificados por IMEI
- Rastreáveis mesmo formatados
- Controlados remotamente

### Emergencia (Acionamentos)
- SOS em tempo real
- Localização GPS precisa
- WebSocket para resposta rápida

## 🔐 Segurança

- **Autenticação JWT** para admins
- **Senhas criptografadas** com bcrypt
- **Validação rigorosa** de dados
- **Logs completos** de auditoria

## 🛠️ Tecnologias

- **FastAPI**: Framework web moderno
- **SQLAlchemy**: ORM para banco de dados
- **Pydantic**: Validação de dados
- **WebSocket**: Comunicação tempo real
- **PostgreSQL/SQLite**: Banco de dados

## 📊 Uso do Sistema

### Fluxo Principal:
1. **Policial** acessa sistema web
2. **Cadastra** usuário com dados completos
3. **Usuário** recebe app no celular
4. **App** se registra automaticamente via IMEI
5. **Em emergência**, botão SOS envia localização
6. **Central PRM** recebe alerta instantâneo
7. **Policial** responde e atualiza status

### 🔗 Principais Endpoints:

#### Autenticação
- `POST /auth/login` - Login de administrador
- `GET /auth/me` - Dados do admin logado

#### Administradores
- `POST /admins/` - Criar novo admin (super_admin only)
- `GET /admins/` - Listar administradores

#### Usuários (Cidadãos)
- `POST /usuarios/` - Cadastrar usuário
- `GET /usuarios/` - Listar usuários (com busca)
- `GET /usuarios/{id}` - Obter usuário específico
- `PUT /usuarios/{id}` - Atualizar usuário

#### Dispositivos
- `POST /dispositivos/register` - Registrar dispositivo (app móvel)
- `POST /dispositivos/` - Cadastrar dispositivo (admin)
- `GET /dispositivos/` - Listar dispositivos
- `PUT /dispositivos/{id}/status` - Atualizar status

#### Emergências
- `POST /emergencias/sos` - Acionar SOS (app móvel)
- `GET /emergencias/` - Listar emergências
- `GET /emergencias/ativas` - Emergências ativas
- `PUT /emergencias/{id}/responder` - Responder emergência
- `PUT /emergencias/{id}/finalizar` - Finalizar emergência

#### Dashboard
- `GET /dashboard/stats` - Estatísticas do sistema
- `GET /health` - Status da API
- `WebSocket /ws` - Comunicação tempo real

## 🔧 Comandos Úteis

```bash
# Inicializar banco
python database.py

# Criar super admin
python -c "from database import create_superuser; create_superuser()"

# Executar testes
pytest

# Executar em produção
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## 📱 Integração Mobile

O app móvel se comunica com este backend através de:
- **REST API** para operações padrão
- **WebSocket** para emergências tempo real
- **IMEI** para identificação automática
- **GPS** para localização precisa
