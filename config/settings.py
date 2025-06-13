import os
from typing import Optional

class Config:
    """Configurações da aplicação"""
    
    # Configurações do servidor
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Configurações do Google OAuth
    GOOGLE_CLIENT_ID: Optional[str] = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: Optional[str] = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_REDIRECT_URI: Optional[str] = os.getenv("GOOGLE_REDIRECT_URI")
    
    # Configurações da API do Gemini
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    
    # Configurações da Alexa
    ALEXA_SKILL_ID: Optional[str] = os.getenv("ALEXA_SKILL_ID")
    
    # Configurações de segurança
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    
    # Escopos do Google OAuth
    GOOGLE_SCOPES = [
        "https://www.googleapis.com/auth/calendar",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile"
    ]
    
    @classmethod
    def validate_config(cls) -> bool:
        """Valida se as configurações essenciais estão definidas"""
        required_configs = [
            cls.GOOGLE_CLIENT_ID,
            cls.GOOGLE_CLIENT_SECRET,
            cls.GEMINI_API_KEY
        ]
        
        missing_configs = [config for config in required_configs if not config]
        
        if missing_configs:
            print(f"Configurações obrigatórias não definidas: {missing_configs}")
            return False
        
        return True

# Instância global da configuração
config = Config()

