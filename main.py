from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel
import json
import logging
from typing import Dict, Any, Optional
from models.alexa_handler import AlexaRequestHandler
from services.oauth_service import oauth_service

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Alexa Gemini Plugin", version="1.0.0")

# Configuração CORS para permitir requisições da Alexa
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instância do handler da Alexa
alexa_handler = AlexaRequestHandler()

# Carrega tokens salvos na inicialização
oauth_service.load_tokens_from_file()

# Modelos Pydantic para as requisições da Alexa
class AlexaRequest(BaseModel):
    version: str
    session: Dict[str, Any]
    context: Dict[str, Any]
    request: Dict[str, Any]

class AlexaResponse(BaseModel):
    version: str = "1.0"
    response: Dict[str, Any]
    sessionAttributes: Optional[Dict[str, Any]] = None

@app.get("/")
async def root():
    """Endpoint de teste para verificar se o serviço está funcionando"""
    return {"message": "Alexa Gemini Plugin está funcionando!"}

@app.post("/alexa")
async def alexa_webhook(request: Request):
    """Endpoint principal para receber requisições da Alexa"""
    try:
        # Recebe o JSON da requisição
        body = await request.json()
        logger.info(f"Requisição recebida da Alexa: {json.dumps(body, indent=2)}")
        
        # Processa a requisição usando o handler
        response = alexa_handler.process_request(body)
        
        logger.info(f"Resposta enviada para Alexa: {json.dumps(response, indent=2)}")
        return response
    
    except Exception as e:
        logger.error(f"Erro ao processar requisição da Alexa: {str(e)}")
        # Resposta de erro formatada para Alexa
        error_response = {
            "version": "1.0",
            "response": {
                "outputSpeech": {
                    "type": "PlainText",
                    "text": "Desculpe, ocorreu um erro interno. Tente novamente."
                },
                "shouldEndSession": True
            }
        }
        return error_response

@app.get("/auth/login")
async def oauth_login(user_id: str = Query(..., description="ID único do usuário")):
    """Inicia o processo de autenticação OAuth"""
    try:
        result = oauth_service.create_authorization_url(user_id)
        
        if result["success"]:
            return RedirectResponse(url=result["authorization_url"])
        else:
            raise HTTPException(status_code=500, detail=result["error"])
    
    except Exception as e:
        logger.error(f"Erro no login OAuth: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno no processo de autenticação")

@app.get("/auth/callback")
async def oauth_callback(
    code: str = Query(..., description="Código de autorização"),
    state: str = Query(..., description="Estado OAuth")
):
    """Processa o callback OAuth do Google"""
    try:
        result = oauth_service.handle_oauth_callback(code, state)
        
        if result["success"]:
            # Salva tokens atualizados
            oauth_service.save_tokens_to_file()
            
            # Retorna página de sucesso
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Autenticação Concluída</title>
                <meta charset="utf-8">
                <style>
                    body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                    .success {{ color: green; }}
                    .container {{ max-width: 500px; margin: 0 auto; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1 class="success">✅ Autenticação Concluída!</h1>
                    <p>Sua conta Google foi vinculada com sucesso ao Gemini Inteligente.</p>
                    <p>Agora você pode usar comandos como:</p>
                    <ul style="text-align: left;">
                        <li>"Alexa, peça ao gemini inteligente para consultar minha agenda"</li>
                        <li>"Alexa, peça ao gemini inteligente para marcar reunião amanhã"</li>
                        <li>"Alexa, peça ao gemini inteligente para conversar comigo"</li>
                    </ul>
                    <p>Você pode fechar esta janela e voltar ao aplicativo Alexa.</p>
                </div>
            </body>
            </html>
            """
            return HTMLResponse(content=html_content)
        else:
            raise HTTPException(status_code=400, detail=result["error"])
    
    except Exception as e:
        logger.error(f"Erro no callback OAuth: {str(e)}")
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Erro na Autenticação</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                .error {{ color: red; }}
                .container {{ max-width: 500px; margin: 0 auto; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1 class="error">❌ Erro na Autenticação</h1>
                <p>Ocorreu um erro ao vincular sua conta Google.</p>
                <p>Erro: {str(e)}</p>
                <p>Tente novamente através do aplicativo Alexa.</p>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content, status_code=400)

@app.get("/auth/status/{user_id}")
async def check_auth_status(user_id: str):
    """Verifica o status de autenticação de um usuário"""
    is_authenticated = oauth_service.is_user_authenticated(user_id)
    return {
        "user_id": user_id,
        "authenticated": is_authenticated
    }

@app.delete("/auth/revoke/{user_id}")
async def revoke_access(user_id: str):
    """Revoga acesso de um usuário"""
    success = oauth_service.revoke_user_access(user_id)
    if success:
        oauth_service.save_tokens_to_file()
        return {"message": "Acesso revogado com sucesso"}
    else:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

@app.get("/health")
async def health_check():
    """Endpoint de verificação de saúde do serviço"""
    return {"status": "healthy", "service": "alexa-gemini-plugin"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

