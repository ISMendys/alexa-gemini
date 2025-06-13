# Alexa Gemini Plugin - Guia de Deploy

## Deploy na Contabo

### 1. Preparação do Servidor

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Python 3.11
sudo apt install python3.11 python3.11-venv python3.11-dev -y

# Instalar nginx para proxy reverso
sudo apt install nginx -y

# Instalar certbot para SSL
sudo apt install certbot python3-certbot-nginx -y
```

### 2. Configuração do Projeto

```bash
# Clonar ou transferir projeto
scp -r alexa-gemini-plugin/ user@seu-servidor:/home/user/

# No servidor
cd /home/user/alexa-gemini-plugin

# Criar ambiente virtual
python3.11 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
nano .env  # Editar com suas credenciais
```

### 3. Configuração do Nginx

```nginx
# /etc/nginx/sites-available/alexa-gemini
server {
    listen 80;
    server_name seu-dominio.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Ativar site
sudo ln -s /etc/nginx/sites-available/alexa-gemini /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Configurar SSL
sudo certbot --nginx -d seu-dominio.com
```

### 4. Configuração do Systemd

```ini
# /etc/systemd/system/alexa-gemini.service
[Unit]
Description=Alexa Gemini Plugin
After=network.target

[Service]
Type=simple
User=user
WorkingDirectory=/home/user/alexa-gemini-plugin
Environment=PATH=/home/user/alexa-gemini-plugin/venv/bin
ExecStart=/home/user/alexa-gemini-plugin/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Ativar serviço
sudo systemctl daemon-reload
sudo systemctl enable alexa-gemini
sudo systemctl start alexa-gemini
sudo systemctl status alexa-gemini
```

### 5. Verificação

```bash
# Testar endpoints
curl https://seu-dominio.com/
curl https://seu-dominio.com/health

# Verificar logs
sudo journalctl -u alexa-gemini -f
```

## Configuração das APIs

### Google Cloud Platform

1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Crie novo projeto ou selecione existente
3. Ative APIs:
   - Google Calendar API
   - Gemini API
4. Crie credenciais OAuth 2.0:
   - Tipo: Aplicação Web
   - URIs de redirecionamento:
     - `https://seu-dominio.com/auth/callback`
     - `https://pitangui.amazon.com/api/skill/link/[SKILL_ID]`
     - `https://layla.amazon.com/api/skill/link/[SKILL_ID]`
     - `https://alexa.amazon.co.jp/api/skill/link/[SKILL_ID]`

### Alexa Skills Kit

1. Acesse [Alexa Developer Console](https://developer.amazon.com/alexa/console/ask)
2. Crie nova Custom Skill
3. Importe `alexa-skill/interaction-model.json`
4. Configure endpoint: `https://seu-dominio.com/alexa`
5. Configure Account Linking:
   - Authorization URI: `https://accounts.google.com/o/oauth2/auth`
   - Access Token URI: `https://oauth2.googleapis.com/token`
   - Client ID: [Seu Google Client ID]
   - Client Secret: [Seu Google Client Secret]
   - Scopes: `https://www.googleapis.com/auth/calendar https://www.googleapis.com/auth/userinfo.email`

## Monitoramento

### Logs

```bash
# Logs do serviço
sudo journalctl -u alexa-gemini -f

# Logs do nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Health Check

```bash
# Script de monitoramento
#!/bin/bash
# /home/user/health-check.sh

HEALTH_URL="https://seu-dominio.com/health"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_URL)

if [ $RESPONSE -eq 200 ]; then
    echo "$(date): Service is healthy"
else
    echo "$(date): Service is down (HTTP $RESPONSE)"
    sudo systemctl restart alexa-gemini
fi
```

```bash
# Adicionar ao crontab
crontab -e
# */5 * * * * /home/user/health-check.sh >> /var/log/alexa-gemini-health.log
```

## Backup

```bash
#!/bin/bash
# /home/user/backup.sh

BACKUP_DIR="/home/user/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup do projeto
tar -czf $BACKUP_DIR/alexa-gemini-$DATE.tar.gz /home/user/alexa-gemini-plugin

# Backup dos tokens (se existir)
if [ -f /home/user/alexa-gemini-plugin/user_tokens.json ]; then
    cp /home/user/alexa-gemini-plugin/user_tokens.json $BACKUP_DIR/user_tokens_$DATE.json
fi

# Manter apenas últimos 7 backups
find $BACKUP_DIR -name "alexa-gemini-*.tar.gz" -mtime +7 -delete
find $BACKUP_DIR -name "user_tokens_*.json" -mtime +7 -delete
```

## Troubleshooting

### Problemas Comuns

**Erro 502 Bad Gateway:**
- Verificar se o serviço está rodando: `sudo systemctl status alexa-gemini`
- Verificar logs: `sudo journalctl -u alexa-gemini -n 50`

**Erro de OAuth:**
- Verificar URLs de redirecionamento no Google Cloud
- Verificar credenciais no arquivo .env
- Verificar configuração do Account Linking na Alexa

**Skill não responde:**
- Verificar endpoint configurado na skill
- Verificar certificado SSL válido
- Verificar logs do nginx e do serviço

### Comandos Úteis

```bash
# Reiniciar serviço
sudo systemctl restart alexa-gemini

# Ver logs em tempo real
sudo journalctl -u alexa-gemini -f

# Testar configuração nginx
sudo nginx -t

# Renovar certificado SSL
sudo certbot renew --dry-run

# Verificar portas abertas
sudo netstat -tlnp | grep :8000
```

