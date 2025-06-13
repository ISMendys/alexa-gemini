# 🎯 Alexa Gemini Plugin

> **Conecte sua Alexa ao poder do Google Gemini**

Um plugin inovador que integra dispositivos Amazon Alexa com o Google Gemini, oferecendo conversas inteligentes e gerenciamento de agenda por voz.

## ✨ Funcionalidades

- 🗣️ **Conversação Inteligente**: Faça perguntas complexas ao Gemini através da Alexa
- 📅 **Gerenciamento de Agenda**: Consulte e crie eventos no Google Calendar por voz
- 🔐 **Autenticação Segura**: OAuth 2.0 para proteção de dados
- 🚀 **Arquitetura Moderna**: FastAPI + Python para alta performance

## 🎮 Como Usar

### Comandos de Voz

```
"Alexa, abra gemini inteligente"
"Alexa, peça ao gemini inteligente para explicar inteligência artificial"
"Alexa, peça ao gemini inteligente para consultar minha agenda de hoje"
"Alexa, peça ao gemini inteligente para marcar reunião amanhã às 14 horas"
```

## 🚀 Instalação Rápida

### 1. Clone o Projeto
```bash
git clone <repository-url>
cd alexa-gemini-plugin
```

### 2. Configure o Ambiente
```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure Variáveis
```bash
cp .env.example .env
# Edite .env com suas credenciais
```

### 4. Execute
```bash
python main.py
```

## 📋 Pré-requisitos

- Python 3.11+
- Conta Amazon Developer (para Alexa Skill)
- Conta Google Cloud Platform
- Chave API do Google Gemini
- Servidor com HTTPS (para produção)

## 🔧 Configuração Completa

### APIs Necessárias

1. **Google Gemini API**
   - Obtenha em: [Google AI Studio](https://ai.google.dev/)
   - Configure: `GEMINI_API_KEY`

2. **Google Calendar API**
   - Ative no [Google Cloud Console](https://console.cloud.google.com/)
   - Configure OAuth 2.0

3. **Alexa Skills Kit**
   - Crie skill em: [Alexa Developer Console](https://developer.amazon.com/alexa/console/ask)
   - Configure Account Linking

### Variáveis de Ambiente

```bash
GEMINI_API_KEY=sua_gemini_api_key_aqui
GOOGLE_CLIENT_ID=seu_google_client_id_aqui
GOOGLE_CLIENT_SECRET=seu_google_client_secret_aqui
GOOGLE_REDIRECT_URI=https://seu-dominio.com/auth/callback
```

## 📁 Estrutura do Projeto

```
alexa-gemini-plugin/
├── 📄 main.py                 # Aplicação FastAPI principal
├── 📄 requirements.txt        # Dependências Python
├── 📁 config/
│   └── settings.py           # Configurações centralizadas
├── 📁 services/
│   ├── gemini_service.py     # Integração com Gemini
│   ├── calendar_service.py   # Integração com Google Calendar
│   └── oauth_service.py      # Autenticação OAuth
├── 📁 models/
│   └── alexa_handler.py      # Processamento de requisições Alexa
├── 📁 alexa-skill/
│   ├── interaction-model.json # Modelo de interação da skill
│   ├── skill.json            # Manifesto da skill
│   └── README.md             # Documentação da skill
├── 📁 docs/
│   └── oauth-setup.md        # Guia de configuração OAuth
└── 📁 test_requests/
    ├── launch_request.json   # Testes de requisições
    └── gemini_intent.json
```

## 🧪 Testes

### Teste Local
```bash
# Iniciar servidor
python main.py

# Testar endpoints
curl http://localhost:8000/
curl http://localhost:8000/health

# Testar requisição Alexa
curl -X POST http://localhost:8000/alexa \
  -H "Content-Type: application/json" \
  -d @test_requests/launch_request.json
```

### Resultados dos Testes
- ✅ Servidor FastAPI funcionando
- ✅ Endpoints respondendo corretamente
- ✅ Processamento de requisições Alexa
- ✅ Integração com serviços Google (estrutura)
- ✅ Autenticação OAuth (estrutura)

## 🌐 Deploy em Produção

### Deploy na Contabo

Consulte o arquivo [`DEPLOY.md`](DEPLOY.md) para instruções completas de deploy, incluindo:

- Configuração do servidor
- Nginx como proxy reverso
- SSL com Let's Encrypt
- Systemd para gerenciamento do serviço
- Monitoramento e backup

### Configuração da Alexa Skill

1. Importe `alexa-skill/interaction-model.json`
2. Configure endpoint: `https://seu-dominio.com/alexa`
3. Configure Account Linking com credenciais Google
4. Teste a skill no simulador

## 📚 Documentação

- 📖 [Documentação Completa](documentation.pdf) - Guia técnico detalhado
- 🔧 [Configuração OAuth](docs/oauth-setup.md) - Setup do Account Linking
- 🚀 [Guia de Deploy](DEPLOY.md) - Deploy em produção
- 🧪 [Resultados de Testes](test_results.md) - Relatório de validação

## 🔒 Segurança

- 🛡️ OAuth 2.0 para autenticação segura
- 🔐 HTTPS obrigatório para comunicações
- 🔑 Tokens com escopo limitado
- 📝 Logs de auditoria
- 🚫 Princípio do menor privilégio

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🆘 Suporte

### Problemas Comuns

**Skill não responde:**
- Verifique se o endpoint está configurado corretamente
- Confirme que o certificado SSL é válido
- Verifique os logs do servidor

**Erro de OAuth:**
- Confirme as URLs de redirecionamento
- Verifique as credenciais no arquivo .env
- Teste o fluxo OAuth manualmente

**Gemini não responde:**
- Verifique se a API key está configurada
- Confirme que a API está ativada no Google Cloud
- Verifique os logs para erros específicos

### Contato

- 📧 Email: suporte@exemplo.com
- 💬 Discord: [Link do servidor]
- 📱 Telegram: [@suporte]

---

**Desenvolvido com ❤️ por Manus AI**

> Transformando a interação por voz com inteligência artificial avançada

