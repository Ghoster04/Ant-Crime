# Sistema de Upload de Fotos - AntiCrime 04

## 🎯 **Funcionalidade Implementada**

Sistema completo de upload de fotos de residências para o cadastro de usuários, utilizando **multipart/form-data** conforme solicitado.

## 📋 **Endpoints Criados**

### **1. POST /usuarios/upload** 
**Cadastrar usuário COM foto da residência**

**Content-Type:** `multipart/form-data`

**Campos obrigatórios:**
- `nome_completo` (string)
- `numero_identidade` (string) 
- `telefone_principal` (string)
- `provincia` (string)
- `cidade` (string)
- `bairro` (string)
- `latitude_residencia` (float)
- `longitude_residencia` (float)

**Campos opcionais:**
- `telefone_emergencia` (string)
- `email` (string)
- `rua` (string)
- `numero_casa` (string)
- `ponto_referencia` (string)
- `observacoes` (string)
- `ativo` (boolean, default: true)
- `foto_residencia` (file) - Imagem da casa

### **2. POST /usuarios/** 
**Cadastrar usuário SEM foto (JSON tradicional)**

**Content-Type:** `application/json`

Mesmo schema anterior, mas sem suporte a upload de arquivo.

### **3. POST /usuarios/{usuario_id}/foto**
**Upload/atualizar apenas a foto**

**Content-Type:** `multipart/form-data`

**Campo:**
- `foto` (file) - Nova foto da residência

### **4. GET /uploads/{filename}**
**Acessar fotos enviadas**

Serve arquivos estáticos das fotos enviadas.

## 🛡️ **Validações Implementadas**

### **Arquivos:**
- **Extensões permitidas:** `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.webp`
- **Tamanho máximo:** 5MB
- **Validação de tipo MIME**

### **Coordenadas GPS:**
- **Latitude:** -90 a 90
- **Longitude:** -180 a 180

### **Outros:**
- **Número de identidade único**
- **Campos obrigatórios validados**

## 📁 **Estrutura de Arquivos**

```
backend/
├── uploads/                 # Diretório para fotos
│   └── {uuid}.jpg          # Arquivos com nomes únicos
├── main.py                 # Endpoints de upload
├── test_upload.py          # Teste completo
├── test_simple_upload.py   # Teste básico
└── ...
```

## 🔧 **Funcionalidades Técnicas**

### **Geração de Nomes Únicos:**
- Utiliza UUID4 para evitar conflitos
- Preserva extensão original
- Exemplo: `a1b2c3d4-e5f6-7890-abcd-ef1234567890.jpg`

### **Gerenciamento de Arquivos:**
- **Upload:** Salva com nome único
- **Atualização:** Remove arquivo anterior automaticamente
- **Servir:** Acesso via URL `/uploads/{filename}`

### **Segurança:**
- Validação rigorosa de tipos de arquivo
- Limite de tamanho para evitar DoS
- Nomes únicos previnem conflitos

## 🧪 **Como Testar**

### **1. Teste Simples (sem foto):**
```bash
python test_simple_upload.py
```

### **2. Teste Completo (com foto):**
```bash
python test_upload.py
```

### **3. Via cURL:**
```bash
# Login
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@prm.gov.mz", "senha": "admin123"}'

# Upload usuário com foto
curl -X POST "http://localhost:8000/usuarios/upload" \
  -H "Authorization: Bearer {TOKEN}" \
  -F "nome_completo=João Silva" \
  -F "numero_identidade=123456789" \
  -F "telefone_principal=+258841234567" \
  -F "provincia=Maputo" \
  -F "cidade=Maputo" \
  -F "bairro=Sommerschield" \
  -F "latitude_residencia=-25.9692" \
  -F "longitude_residencia=32.5732" \
  -F "foto_residencia=@/caminho/para/foto.jpg"
```

### **4. Via Swagger UI:**
1. Acesse: `http://localhost:8000/docs`
2. Faça login em **POST /auth/login**
3. Use o token em **POST /usuarios/upload**
4. Preencha os campos e anexe uma imagem

## 📱 **Integração com App Móvel**

O app móvel deve:

1. **Capturar foto** da residência
2. **Coletar dados** do usuário
3. **Enviar via POST** para `/usuarios/upload`
4. **Usar multipart/form-data** obrigatoriamente
5. **Incluir token JWT** no header Authorization

## 🌐 **URLs de Exemplo**

- **API Docs:** http://localhost:8000/docs
- **Criar usuário:** http://localhost:8000/usuarios/upload
- **Ver foto:** http://localhost:8000/uploads/a1b2c3d4-e5f6-7890-abcd-ef1234567890.jpg

## ✅ **Status da Implementação**

- ✅ **Multipart/form-data** implementado
- ✅ **Upload de imagens** funcionando
- ✅ **Validações** completas
- ✅ **Nomes únicos** para arquivos
- ✅ **Servir arquivos** estáticos
- ✅ **Testes** automatizados
- ✅ **Documentação** Swagger
- ✅ **Integração** com sistema existente

O sistema está **100% funcional** e pronto para uso em produção! 🚀
