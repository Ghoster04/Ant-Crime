# Modelo de Banco de Dados - AntiCrime 04

## 📊 Visão Geral da Arquitetura

O sistema AntiCrime 04 utiliza um modelo de banco de dados relacional otimizado para gerenciar:
- **Administradores** (Policiais da PRM)
- **Usuários** (Cidadãos cadastrados)
- **Dispositivos** (Smartphones com o app)
- **Emergências** (Acionamentos SOS)
- **Logs e Configurações** do sistema

## 🗂️ Entidades Principais

### 1. **Admin** (Administradores/Policiais)
```sql
Tabela: admins
```
**Responsabilidade**: Gerenciar o sistema, cadastrar usuários e responder emergências

**Campos principais**:
- `id`: Identificador único
- `nome_completo`: Nome do policial
- `email`: Email institucional (@prm.gov.mz)
- `senha_hash`: Senha criptografada
- `numero_badge`: Número de identificação policial
- `posto_policial`: Unidade onde trabalha
- `tipo_admin`: SUPER_ADMIN | OPERADOR | SUPERVISOR

**Funcionalidades**:
- ✅ Cadastrar novos usuários no sistema
- ✅ Responder a emergências ativas
- ✅ Gerenciar dispositivos roubados
- ✅ Gerar relatórios e estatísticas

### 2. **Usuario** (Cidadãos Cadastrados)
```sql
Tabela: usuarios
```
**Responsabilidade**: Pessoas que recebem o app e podem acionar emergências

**Campos principais**:
- `id`: Identificador único
- `nome_completo`: Nome completo do cidadão
- `numero_identidade`: BI ou Passaporte
- `telefone_principal`: Contato principal
- `telefone_emergencia`: Contato alternativo
- `provincia`, `cidade`, `bairro`: Localização
- `latitude_residencia`, `longitude_residencia`: Coordenadas exatas
- `foto_residencia`: Foto da casa para identificação
- `admin_cadastrador_id`: Policial que fez o cadastro

**Fluxo de Cadastro**:
1. **Policial** vai à residência/delegacia
2. **Coleta** informações completas do cidadão
3. **Registra** coordenadas GPS da residência
4. **Tira foto** da casa para identificação
5. **Usuário recebe** o app pré-configurado

### 3. **Dispositivo** (Smartphones)
```sql
Tabela: dispositivos
```
**Responsabilidade**: Controlar e rastrear dispositivos móveis

**Campos principais**:
- `id`: Identificador único
- `imei`: Número IMEI único (15 dígitos)
- `modelo`, `marca`: Informações do aparelho
- `sistema_operacional`: Android/iOS
- `status`: ATIVO | INATIVO | ROUBADO | RECUPERADO | BLOQUEADO
- `usuario_id`: Proprietário do dispositivo
- `ultima_localizacao_lat/lng`: Última posição conhecida
- `ultimo_ping`: Último sinal recebido

**Funcionalidades**:
- 🔍 **Rastreamento por IMEI**: Funciona mesmo após formatação
- 📍 **Localização contínua**: GPS em tempo real
- 🔒 **Controle remoto**: Bloqueio/desbloqueio pela PRM
- 📊 **Monitoramento**: Status e atividade do dispositivo

### 4. **Emergencia** (Acionamentos SOS)
```sql
Tabela: emergencias
```
**Responsabilidade**: Registrar e gerenciar situações de emergência

**Campos principais**:
- `id`: Identificador único da ocorrência
- `latitude`, `longitude`: Localização exata da emergência
- `timestamp_acionamento`: Momento do acionamento
- `status`: ATIVO | RESPONDIDO | FINALIZADO | FALSO_ALARME
- `usuario_id`: Quem acionou
- `dispositivo_id`: Dispositivo usado
- `admin_responsavel_id`: Policial que atendeu
- `tempo_resposta`: Tempo até primeira resposta
- `nivel_bateria`: Bateria no momento do acionamento
- `precisao_gps`: Precisão da localização (metros)

**Fluxo de Emergência**:
1. **Usuário** pressiona botão SOS
2. **Sistema** captura localização GPS
3. **WebSocket** envia dados instantaneamente
4. **Central PRM** recebe alerta em tempo real
5. **Policial** responde e atualiza status

## 🔗 Relacionamentos

### Hierarquia de Controle:
```
Admin (PRM) 
    ├── Cadastra → Usuario (Cidadão)
    │   └── Possui → Dispositivo (IMEI)
    │       └── Gera → Emergencia (SOS)
    └── Responde → Emergencia
```

### Relacionamentos Específicos:
- **Admin 1:N Usuario**: Um policial cadastra vários usuários
- **Usuario 1:N Dispositivo**: Um usuário pode ter vários dispositivos
- **Dispositivo 1:N Emergencia**: Um dispositivo pode gerar várias emergências
- **Admin 1:N Emergencia**: Um policial pode atender várias emergências

## 🛡️ Segurança e Controle

### Níveis de Acesso:
1. **SUPER_ADMIN**: Controle total do sistema
2. **SUPERVISOR**: Gerencia operadores e relatórios
3. **OPERADOR**: Atende emergências e cadastra usuários

### Auditoria Completa:
- **LogSistema**: Registra todas as ações
- **Timestamps**: Data/hora de todas as operações
- **Rastreabilidade**: Quem fez o quê e quando

### Validações:
- **IMEI**: Exatamente 15 dígitos numéricos
- **Coordenadas**: Latitude (-90 a 90), Longitude (-180 a 180)
- **Senhas**: Mínimo 6 caracteres, hash bcrypt
- **Emails**: Validação de formato

## 📱 Integração com App Móvel

### Fluxo de Funcionamento:
1. **App instalado** → Envia IMEI para servidor
2. **Servidor verifica** → IMEI está cadastrado?
3. **Se SIM** → App ativado automaticamente
4. **Se NÃO** → App permanece inativo

### Comunicação:
- **WebSocket**: Emergências em tempo real
- **REST API**: Operações CRUD
- **GPS**: Localização contínua
- **Push Notifications**: Alertas e notificações

## 🚀 Configuração e Deploy

### Variáveis de Ambiente:
```env
DATABASE_URL=postgresql://user:pass@localhost/anticrime04
SECRET_KEY=sua_chave_secreta_aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Comandos de Inicialização:
```bash
# Instalar dependências
pip install -r requirements.txt

# Inicializar banco de dados
python database.py

# Criar migrações (Alembic)
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## 📊 Queries Importantes

### Emergências Ativas:
```sql
SELECT e.*, u.nome_completo, u.telefone_principal 
FROM emergencias e 
JOIN usuarios u ON e.usuario_id = u.id 
WHERE e.status = 'ativo';
```

### Dispositivos Roubados:
```sql
SELECT d.*, u.nome_completo, u.telefone_principal
FROM dispositivos d
JOIN usuarios u ON d.usuario_id = u.id
WHERE d.status = 'roubado';
```

### Estatísticas Diárias:
```sql
SELECT 
    COUNT(*) as total_emergencias,
    COUNT(CASE WHEN status = 'ativo' THEN 1 END) as ativas,
    AVG(tempo_resposta) as tempo_medio_resposta
FROM emergencias 
WHERE DATE(timestamp_acionamento) = CURRENT_DATE;
```

## 🔄 Futuras Expansões

### Funcionalidades Planejadas:
- **Reconhecimento facial** nas fotos das residências
- **Integração com câmeras** de segurança públicas
- **Machine Learning** para detectar padrões criminais
- **API para outros órgãos** de segurança
- **App para familiares** acompanharem status

### Otimizações:
- **Índices** em campos de busca frequente
- **Particionamento** de tabelas por data
- **Cache Redis** para consultas frequentes
- **Réplicas de leitura** para relatórios
