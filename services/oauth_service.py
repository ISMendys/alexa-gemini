from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import json
import logging
from typing import Dict, Any, Optional
from config.settings import config
import secrets
import os

logger = logging.getLogger(__name__)

class OAuthService:
    """Serviço para gerenciar autenticação OAuth com Google"""
    
    def __init__(self):
        self.client_id = config.GOOGLE_CLIENT_ID
        self.client_secret = config.GOOGLE_CLIENT_SECRET
        self.redirect_uri = config.GOOGLE_REDIRECT_URI
        self.scopes = config.GOOGLE_SCOPES
        
        # Armazenamento temporário de estados OAuth (em produção, usar Redis ou banco de dados)
        self.oauth_states = {}
        self.user_tokens = {}
        
        if not all([self.client_id, self.client_secret, self.redirect_uri]):
            logger.warning("Configurações OAuth não completas. Serviço OAuth não funcionará.")
    
    def create_authorization_url(self, user_id: str) -> Dict[str, Any]:
        """
        Cria URL de autorização OAuth para o usuário
        
        Args:
            user_id: ID único do usuário (ex: Alexa user ID)
            
        Returns:
            Dict contendo URL de autorização e estado
        """
        if not all([self.client_id, self.client_secret, self.redirect_uri]):
            return {
                "success": False,
                "error": "Configurações OAuth não completas"
            }
        
        try:
            # Cria configuração do cliente OAuth
            client_config = {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.redirect_uri]
                }
            }
            
            # Cria o flow OAuth
            flow = Flow.from_client_config(
                client_config,
                scopes=self.scopes
            )
            flow.redirect_uri = self.redirect_uri
            
            # Gera estado único para segurança
            state = secrets.token_urlsafe(32)
            
            # Gera URL de autorização
            authorization_url, _ = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                state=state
            )
            
            # Armazena o estado e flow para validação posterior
            self.oauth_states[state] = {
                "user_id": user_id,
                "flow": flow
            }
            
            logger.info(f"URL de autorização criada para usuário {user_id}")
            
            return {
                "success": True,
                "authorization_url": authorization_url,
                "state": state
            }
            
        except Exception as e:
            logger.error(f"Erro ao criar URL de autorização: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def handle_oauth_callback(self, authorization_code: str, state: str) -> Dict[str, Any]:
        """
        Processa o callback OAuth e obtém tokens de acesso
        
        Args:
            authorization_code: Código de autorização retornado pelo Google
            state: Estado OAuth para validação
            
        Returns:
            Dict contendo informações do usuário e tokens
        """
        if state not in self.oauth_states:
            return {
                "success": False,
                "error": "Estado OAuth inválido"
            }
        
        try:
            oauth_data = self.oauth_states[state]
            flow = oauth_data["flow"]
            user_id = oauth_data["user_id"]
            
            # Troca o código de autorização por tokens
            flow.fetch_token(code=authorization_code)
            
            # Obtém as credenciais
            credentials = flow.credentials
            
            # Armazena os tokens do usuário
            self.user_tokens[user_id] = {
                "access_token": credentials.token,
                "refresh_token": credentials.refresh_token,
                "token_uri": credentials.token_uri,
                "client_id": credentials.client_id,
                "client_secret": credentials.client_secret,
                "scopes": credentials.scopes
            }
            
            # Remove o estado usado
            del self.oauth_states[state]
            
            logger.info(f"OAuth concluído com sucesso para usuário {user_id}")
            
            return {
                "success": True,
                "user_id": user_id,
                "access_token": credentials.token,
                "refresh_token": credentials.refresh_token
            }
            
        except Exception as e:
            logger.error(f"Erro no callback OAuth: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_user_access_token(self, user_id: str) -> Optional[str]:
        """
        Obtém token de acesso válido para o usuário
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Token de acesso válido ou None
        """
        if user_id not in self.user_tokens:
            return None
        
        try:
            token_data = self.user_tokens[user_id]
            
            # Cria credenciais a partir dos dados armazenados
            credentials = Credentials(
                token=token_data["access_token"],
                refresh_token=token_data["refresh_token"],
                token_uri=token_data["token_uri"],
                client_id=token_data["client_id"],
                client_secret=token_data["client_secret"],
                scopes=token_data["scopes"]
            )
            
            # Verifica se o token precisa ser atualizado
            if credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
                
                # Atualiza os tokens armazenados
                self.user_tokens[user_id]["access_token"] = credentials.token
                
                logger.info(f"Token atualizado para usuário {user_id}")
            
            return credentials.token
            
        except Exception as e:
            logger.error(f"Erro ao obter token de acesso para usuário {user_id}: {str(e)}")
            return None
    
    def revoke_user_access(self, user_id: str) -> bool:
        """
        Revoga acesso do usuário (remove tokens armazenados)
        
        Args:
            user_id: ID do usuário
            
        Returns:
            True se revogado com sucesso
        """
        try:
            if user_id in self.user_tokens:
                del self.user_tokens[user_id]
                logger.info(f"Acesso revogado para usuário {user_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Erro ao revogar acesso para usuário {user_id}: {str(e)}")
            return False
    
    def is_user_authenticated(self, user_id: str) -> bool:
        """
        Verifica se o usuário está autenticado
        
        Args:
            user_id: ID do usuário
            
        Returns:
            True se autenticado
        """
        return user_id in self.user_tokens and self.get_user_access_token(user_id) is not None
    
    def save_tokens_to_file(self, filepath: str = "user_tokens.json"):
        """
        Salva tokens em arquivo (para persistência)
        
        Args:
            filepath: Caminho do arquivo para salvar
        """
        try:
            with open(filepath, 'w') as f:
                json.dump(self.user_tokens, f, indent=2)
            logger.info(f"Tokens salvos em {filepath}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar tokens: {str(e)}")
    
    def load_tokens_from_file(self, filepath: str = "user_tokens.json"):
        """
        Carrega tokens de arquivo
        
        Args:
            filepath: Caminho do arquivo para carregar
        """
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    self.user_tokens = json.load(f)
                logger.info(f"Tokens carregados de {filepath}")
            
        except Exception as e:
            logger.error(f"Erro ao carregar tokens: {str(e)}")

# Instância global do serviço OAuth
oauth_service = OAuthService()

