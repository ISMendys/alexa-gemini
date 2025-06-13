# Configuração da Alexa Skill

Este diretório contém os arquivos de configuração necessários para criar a Alexa Skill no console da Amazon.

## Arquivos

### interaction-model.json
Define o modelo de interação da skill, incluindo:
- **Invocation Name**: "gemini inteligente" - nome usado para ativar a skill
- **Intents**: As intenções que a skill pode reconhecer
  - `ConversarComGemini`: Para fazer perguntas ao Gemini
  - `ConsultarAgenda`: Para consultar eventos do Google Agenda
  - `CriarEvento`: Para criar novos eventos na agenda
- **Slots**: Parâmetros extraídos da fala do usuário
- **Sample Utterances**: Exemplos de frases que ativam cada intent

### skill.json
Manifesto da skill contendo:
- Informações de publicação (nome, descrição, categoria)
- Configuração do endpoint (URL do webhook)
- Permissões necessárias
- Configurações de privacidade e compliance

## Como usar

1. Acesse o [Alexa Developer Console](https://developer.amazon.com/alexa/console/ask)
2. Crie uma nova Custom Skill
3. Importe o `interaction-model.json` na seção "Interaction Model"
4. Configure o endpoint apontando para seu servidor (ex: `https://seu-dominio.com/alexa`)
5. Importe as configurações do `skill.json` se necessário
6. Configure o Account Linking para autenticação OAuth com Google
7. Teste a skill no simulador

## Exemplos de uso

- "Alexa, abra gemini inteligente"
- "Alexa, peça ao gemini inteligente para explicar inteligência artificial"
- "Alexa, peça ao gemini inteligente para consultar minha agenda de hoje"
- "Alexa, peça ao gemini inteligente para marcar reunião amanhã às 14h"

## Configuração do Account Linking

Para conectar com o Google OAuth:
1. No console da Alexa, vá em "Account Linking"
2. Configure:
   - Authorization URI: `https://accounts.google.com/o/oauth2/auth`
   - Access Token URI: `https://oauth2.googleapis.com/token`
   - Client ID: Seu Google Client ID
   - Client Secret: Seu Google Client Secret
   - Scopes: `https://www.googleapis.com/auth/calendar https://www.googleapis.com/auth/userinfo.email`

