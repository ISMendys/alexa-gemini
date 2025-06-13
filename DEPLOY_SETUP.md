# GitHub Actions Secrets Configuration

Para configurar o deploy automático via GitHub Actions, você precisa configurar os seguintes secrets no seu repositório GitHub:

## Como Configurar Secrets

1. Vá para seu repositório no GitHub
2. Clique em **Settings** > **Secrets and variables** > **Actions**
3. Clique em **New repository secret**
4. Adicione cada secret abaixo:

## Secrets Necessários

### Servidor de Deploy
```
HOST=seu-servidor.contabo.com
USERNAME=admin
PORT=22
SSH_PRIVATE_KEY=-----BEGIN OPENSSH PRIVATE KEY-----
[sua chave SSH privada completa]
-----END OPENSSH PRIVATE KEY-----
```

### APIs (Opcionais para testes)
```
GEMINI_API_KEY=sua_gemini_api_key_aqui
GOOGLE_CLIENT_ID=seu_google_client_id_aqui
GOOGLE_CLIENT_SECRET=seu_google_client_secret_aqui
```

## Configuração do Servidor

### 1. Preparar Chave SSH

No seu computador local:
```bash
# Gerar nova chave SSH (se não tiver)
ssh-keygen -t ed25519 -C "github-actions@seu-email.com"

# Copiar chave pública para o servidor
ssh-copy-id -i ~/.ssh/id_ed25519.pub ubuntu@seu-servidor.contabo.com

# Copiar chave privada para usar no GitHub
cat ~/.ssh/id_ed25519
```

### 2. Configurar Servidor

No servidor Contabo:
```bash
# Instalar Docker e Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Clonar repositório
git clone https://github.com/seu-usuario/alexa-gemini-plugin.git
cd alexa-gemini-plugin

# Criar arquivo .env
cp .env.example .env
nano .env  # Configurar suas variáveis
```

### 3. Configurar Nginx (Opcional)

Se quiser usar nginx como proxy:
```bash
# Instalar nginx
sudo apt update
sudo apt install nginx certbot python3-certbot-nginx

# Configurar domínio
sudo nano /etc/nginx/sites-available/alexa-gemini
# Copiar configuração do arquivo nginx/sites-available/alexa-gemini

# Ativar site
sudo ln -s /etc/nginx/sites-available/alexa-gemini /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Configurar SSL
sudo certbot --nginx -d seu-dominio.com
```

## Fluxo de Deploy

### Automático (Recomendado)
1. Faça push para branch `main` ou `master`
2. GitHub Actions executará:
   - Testes automatizados
   - Build da imagem Docker
   - Push para GitHub Container Registry
   - Deploy no servidor via SSH
   - Verificação de saúde

### Manual
```bash
# No servidor
cd /home/ubuntu/alexa-gemini-plugin
git pull origin main
docker-compose down
docker-compose pull
docker-compose up -d
```

## Monitoramento

### Verificar Status
```bash
# Status dos containers
docker-compose ps

# Logs da aplicação
docker-compose logs -f alexa-gemini

# Logs do nginx
docker-compose logs -f nginx

# Health check
curl http://localhost/health
```

### Troubleshooting

**Deploy falha:**
- Verificar secrets configurados
- Verificar conectividade SSH
- Verificar logs do GitHub Actions

**Container não inicia:**
- Verificar variáveis de ambiente
- Verificar logs: `docker-compose logs alexa-gemini`
- Verificar portas disponíveis

**Nginx não funciona:**
- Verificar configuração: `nginx -t`
- Verificar certificado SSL
- Verificar DNS do domínio

## Estrutura de Branches

### Recomendado
```
main/master  -> Produção (deploy automático)
develop      -> Desenvolvimento (apenas testes)
feature/*    -> Features (apenas testes)
hotfix/*     -> Correções urgentes
```

### Configuração de Proteção
1. Vá em **Settings** > **Branches**
2. Adicione regra para `main`:
   - Require pull request reviews
   - Require status checks to pass
   - Require branches to be up to date

## Notificações

### Slack (Opcional)
Adicione webhook do Slack nos secrets:
```
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
```

### Discord (Opcional)
Adicione webhook do Discord nos secrets:
```
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
```

## Rollback

### Automático
```bash
# No servidor, voltar para versão anterior
docker-compose down
docker pull ghcr.io/seu-usuario/alexa-gemini-plugin:previous-tag
docker-compose up -d
```

### Via GitHub
1. Vá em **Actions**
2. Selecione deploy anterior bem-sucedido
3. Clique em **Re-run jobs**

