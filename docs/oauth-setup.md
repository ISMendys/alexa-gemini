# Configuração OAuth para Alexa Skill

## Configuração no Console da Amazon

Para configurar o Account Linking na sua Alexa Skill:

### 1. Acesse o Console da Alexa
- Vá para [Alexa Developer Console](https://developer.amazon.com/alexa/console/ask)
- Selecione sua skill "Gemini Inteligente"

### 2. Configure Account Linking
Na seção "Account Linking", configure:

**Authorization Grant Type:** Authorization Code Grant

**Authorization URI:** 
```
https://accounts.google.com/o/oauth2/auth
```

**Access Token URI:**
```
https://oauth2.googleapis.com/token
```

**Client ID:**
```
[Seu Google Client ID]
```

**Client Secret:**
```
[Seu Google Client Secret]
```

**Client Authentication Scheme:** HTTP Basic (Recommended)

**Scopes:**
```
https://www.googleapis.com/auth/calendar
https://www.googleapis.com/auth/userinfo.email
https://www.googleapis.com/auth/userinfo.profile
```

**Domain List (opcional):**
```
googleapis.com
google.com
```

**Default Access Token Expiration Time:** 3600

**Redirect URLs:**
```
https://seu-dominio.com/auth/callback
https://pitangui.amazon.com/api/skill/link/[SKILL_ID]
https://layla.amazon.com/api/skill/link/[SKILL_ID]
https://alexa.amazon.co.jp/api/skill/link/[SKILL_ID]
```

### 3. Configuração no Google Cloud Console

1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um novo projeto ou selecione um existente
3. Ative as APIs necessárias:
   - Google Calendar API
   - Google+ API (para informações do usuário)

4. Vá em "Credenciais" > "Criar Credenciais" > "ID do cliente OAuth 2.0"
5. Configure:
   - **Tipo de aplicação:** Aplicação da Web
   - **URIs de redirecionamento autorizados:**
     ```
     https://seu-dominio.com/auth/callback
     https://pitangui.amazon.com/api/skill/link/[SKILL_ID]
     https://layla.amazon.com/api/skill/link/[SKILL_ID]
     https://alexa.amazon.co.jp/api/skill/link/[SKILL_ID]
     ```

### 4. Variáveis de Ambiente

Configure as seguintes variáveis no seu arquivo `.env`:

```bash
GOOGLE_CLIENT_ID=seu_google_client_id_aqui
GOOGLE_CLIENT_SECRET=seu_google_client_secret_aqui
GOOGLE_REDIRECT_URI=https://seu-dominio.com/auth/callback
GEMINI_API_KEY=sua_gemini_api_key_aqui
```

### 5. Teste do Account Linking

1. No console da Alexa, vá em "Test" > "Account Linking"
2. Clique em "Link Account" 
3. Você será redirecionado para o Google para autorizar
4. Após autorizar, deve retornar com sucesso

### 6. Fluxo do Usuário

1. Usuário instala a skill "Gemini Inteligente"
2. No aplicativo Alexa, vai em Skills > Suas Skills > Gemini Inteligente
3. Clica em "Configurações" > "Vincular Conta"
4. É redirecionado para o Google para autorizar
5. Após autorizar, pode usar comandos como:
   - "Alexa, peça ao gemini inteligente para consultar minha agenda"
   - "Alexa, peça ao gemini inteligente para marcar reunião amanhã"

### Troubleshooting

**Erro "redirect_uri_mismatch":**
- Verifique se todas as URLs de redirecionamento estão configuradas corretamente
- Certifique-se de que a URL do seu servidor está acessível publicamente

**Erro "invalid_client":**
- Verifique se o Client ID e Client Secret estão corretos
- Confirme se as APIs estão ativadas no Google Cloud Console

**Skill não consegue acessar a agenda:**
- Verifique se os escopos estão corretos
- Confirme se o token está sendo salvo e carregado corretamente

