# Configuração MySQL - AntiCrime 04

## 🎯 Visão Geral

O backend do AntiCrime 04 foi configurado para usar o banco de dados MySQL do Railway em produção, mantendo SQLite para desenvolvimento local.

## 🔧 Configurações Implementadas

### Credenciais MySQL (Railway)

#### Para Produção (dentro do Railway):
- **Host**: `mysql.railway.internal`
- **Port**: `3306`
- **Database**: `railway`
- **User**: `root`
- **Password**: `qmWIuOIpYLNOJcSdpKumbxNcQJPmalAO`

#### Para Desenvolvimento Local:
- **Host**: `turntable.proxy.rlwy.net`
- **Port**: `28897`
- **Database**: `railway`
- **User**: `root`
- **Password**: `qmWIuOIpYLNOJcSdpKumbxNcQJPmalAO`

### Arquivos Modificados

1. **`database.py`** - Configuração centralizada do banco
2. **`requirements.txt`** - Dependências MySQL adicionadas
3. **`config.py`** - Configurações centralizadas (NOVO)
4. **`main.py`** - Atualizado para usar configurações centralizadas
5. **`models.py`** - Compatibilidade com MySQL garantida

## 🚀 Como Usar

### Para Produção (MySQL)
O sistema automaticamente usa MySQL quando:
- `USE_LOCAL_DB=False` (padrão)
- `DEBUG=False` (padrão)

### Para Desenvolvimento Local:

#### Opção 1: Usar MySQL Railway (Externo) - RECOMENDADO
```bash
# Não precisa configurar nada, já está configurado
python test_mysql_connection.py
```

#### Opção 2: Usar SQLite Local
Para usar SQLite localmente, defina as variáveis de ambiente:
```bash
export USE_LOCAL_DB=True
export DEBUG=True
```

Ou edite o arquivo `config.py`:
```python
USE_LOCAL_DB: bool = True
DEBUG: bool = True
```

## 📦 Dependências Adicionadas

```txt
pymysql==1.1.0          # Driver MySQL para Python
cryptography==41.0.7    # Criptografia necessária para conexões seguras
```

## 🧪 Testando a Conexão

Execute o script de teste:
```bash
python test_mysql_connection.py
```

Este script irá:
- ✅ Testar conexão com MySQL
- ✅ Verificar versão do banco
- ✅ Testar criação de tabelas
- ✅ Listar tabelas criadas

## 🔄 Migração de Dados

### Se você tem dados em SQLite e quer migrar para MySQL:

1. **Exportar dados do SQLite**:
```bash
python -c "
import sqlite3
import json
conn = sqlite3.connect('anticrime04.db')
# Exportar dados...
"
```

2. **Importar para MySQL**:
```bash
# Usar o script de migração ou importar manualmente
```

## 🏗️ Estrutura das Tabelas

O MySQL criará as seguintes tabelas:
- `admins` - Administradores do sistema
- `usuarios` - Cidadãos cadastrados
- `dispositivos` - Smartphones com o app
- `emergencias` - Acionamentos SOS
- `pings_dispositivos` - Histórico de localização
- `logs_sistema` - Logs do sistema
- `configuracoes_sistema` - Configurações

## ⚙️ Configurações de Pool de Conexões

```python
pool_recycle=300,  # Reciclar conexões a cada 5 minutos
pool_size=10,      # Pool de conexões
max_overflow=20    # Conexões extras permitidas
```

## 🔒 Segurança

- ✅ Conexões criptografadas com `cryptography`
- ✅ Charset UTF-8 para suporte completo a caracteres
- ✅ Pool de conexões para performance
- ✅ Credenciais centralizadas em `config.py`

## 🐛 Troubleshooting

### Erro de Conexão
```bash
# Verificar se as credenciais estão corretas
python test_mysql_connection.py
```

### Erro de Charset
```sql
-- Verificar charset do banco
SELECT @@character_set_database;
-- Deve retornar: utf8mb4
```

### Erro de Tabelas
```bash
# Recriar tabelas
python -c "from database import init_db; init_db()"
```

## 📊 Monitoramento

### Verificar Conexões Ativas
```sql
SHOW PROCESSLIST;
```

### Verificar Status do MySQL
```sql
SHOW STATUS LIKE 'Connections';
```

## 🚀 Deploy

Para fazer deploy com MySQL:

1. **Instalar dependências**:
```bash
pip install -r requirements.txt
```

2. **Testar conexão**:
```bash
python test_mysql_connection.py
```

3. **Inicializar banco**:
```bash
python -c "from database import init_db, create_superuser; init_db(); create_superuser()"
```

4. **Executar aplicação**:
```bash
python main.py
```

## 📝 Logs

O sistema registrará logs de:
- Conexões com banco
- Criação de tabelas
- Erros de conexão
- Performance de queries

## ✅ Checklist de Verificação

- [ ] Credenciais MySQL corretas
- [ ] Dependências instaladas (`pymysql`, `cryptography`)
- [ ] Teste de conexão passou
- [ ] Tabelas criadas corretamente
- [ ] Super admin criado
- [ ] API respondendo
- [ ] Frontend conectando

## 🆘 Suporte

Se encontrar problemas:

1. Verifique os logs da aplicação
2. Execute o script de teste
3. Verifique as credenciais MySQL
4. Confirme que o banco está acessível
5. Teste a conectividade de rede

---

**Status**: ✅ Configurado e pronto para uso em produção!
