import requests
import json
import logging
from typing import Dict, Any, Optional, List
from config.settings import config

logger = logging.getLogger(__name__)

class GeminiService:
    """Serviço para integração com a API do Google Gemini"""
    
    def __init__(self):
        self.api_key = config.GEMINI_API_KEY
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.model = "gemini-2.0-flash-exp"
        
        if not self.api_key:
            logger.warning("GEMINI_API_KEY não configurada. Serviço do Gemini não funcionará.")
    
    def generate_content(self, prompt: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Gera conteúdo usando a API do Gemini
        
        Args:
            prompt: A pergunta ou prompt do usuário
            context: Contexto adicional da conversa (opcional)
            
        Returns:
            Dict contendo a resposta do Gemini ou erro
        """
        if not self.api_key:
            return {
                "success": False,
                "error": "API key do Gemini não configurada",
                "response": "Desculpe, a integração com o Gemini não está configurada corretamente."
            }
        
        try:
            # Prepara o prompt com contexto se fornecido
            full_prompt = prompt
            if context:
                full_prompt = f"Contexto: {context}\n\nPergunta: {prompt}"
            
            # Monta a requisição para a API do Gemini
            url = f"{self.base_url}/models/{self.model}:generateContent"
            headers = {
                "Content-Type": "application/json",
                "x-goog-api-key": self.api_key
            }
            
            payload = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": full_prompt
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.7,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 1024,
                }
            }
            
            logger.info(f"Enviando requisição para Gemini: {prompt[:100]}...")
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            # Extrai o texto da resposta
            if "candidates" in result and len(result["candidates"]) > 0:
                candidate = result["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    text_response = candidate["content"]["parts"][0].get("text", "")
                    
                    logger.info(f"Resposta do Gemini recebida: {text_response[:100]}...")
                    
                    return {
                        "success": True,
                        "response": text_response,
                        "raw_response": result
                    }
            
            # Se não conseguiu extrair o texto
            logger.error(f"Formato de resposta inesperado do Gemini: {result}")
            return {
                "success": False,
                "error": "Formato de resposta inesperado",
                "response": "Desculpe, não consegui processar a resposta do Gemini."
            }
            
        except requests.exceptions.Timeout:
            logger.error("Timeout na requisição para o Gemini")
            return {
                "success": False,
                "error": "Timeout",
                "response": "Desculpe, o Gemini demorou muito para responder. Tente novamente."
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição para o Gemini: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "response": "Desculpe, ocorreu um erro ao comunicar com o Gemini."
            }
            
        except Exception as e:
            logger.error(f"Erro inesperado no serviço do Gemini: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "response": "Desculpe, ocorreu um erro interno no serviço do Gemini."
            }
    
    def generate_with_functions(self, prompt: str, available_functions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Gera conteúdo com capacidade de chamar funções (Function Calling)
        
        Args:
            prompt: A pergunta ou prompt do usuário
            available_functions: Lista de funções disponíveis para o Gemini chamar
            
        Returns:
            Dict contendo a resposta do Gemini e possíveis chamadas de função
        """
        if not self.api_key:
            return {
                "success": False,
                "error": "API key do Gemini não configurada",
                "response": "Desculpe, a integração com o Gemini não está configurada corretamente."
            }
        
        try:
            url = f"{self.base_url}/models/{self.model}:generateContent"
            headers = {
                "Content-Type": "application/json",
                "x-goog-api-key": self.api_key
            }
            
            payload = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": prompt
                            }
                        ]
                    }
                ],
                "tools": [
                    {
                        "function_declarations": available_functions
                    }
                ],
                "generationConfig": {
                    "temperature": 0.7,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 1024,
                }
            }
            
            logger.info(f"Enviando requisição com funções para Gemini: {prompt[:100]}...")
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            # Processa a resposta que pode conter chamadas de função
            if "candidates" in result and len(result["candidates"]) > 0:
                candidate = result["candidates"][0]
                
                response_data = {
                    "success": True,
                    "response": "",
                    "function_calls": [],
                    "raw_response": result
                }
                
                if "content" in candidate and "parts" in candidate["content"]:
                    for part in candidate["content"]["parts"]:
                        if "text" in part:
                            response_data["response"] += part["text"]
                        elif "functionCall" in part:
                            response_data["function_calls"].append(part["functionCall"])
                
                return response_data
            
            logger.error(f"Formato de resposta inesperado do Gemini: {result}")
            return {
                "success": False,
                "error": "Formato de resposta inesperado",
                "response": "Desculpe, não consegui processar a resposta do Gemini."
            }
            
        except Exception as e:
            logger.error(f"Erro no Function Calling do Gemini: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "response": "Desculpe, ocorreu um erro ao processar sua solicitação."
            }
    
    def format_for_speech(self, text: str) -> str:
        """
        Formata o texto do Gemini para ser mais adequado para síntese de fala
        
        Args:
            text: Texto original do Gemini
            
        Returns:
            Texto formatado para fala
        """
        # Remove markdown e formatação
        formatted = text.replace("**", "").replace("*", "")
        formatted = formatted.replace("#", "")
        
        # Substitui quebras de linha por pausas
        formatted = formatted.replace("\n\n", ". ")
        formatted = formatted.replace("\n", " ")
        
        # Limita o tamanho para evitar respostas muito longas
        if len(formatted) > 500:
            # Encontra o último ponto antes do limite
            truncate_point = formatted.rfind(".", 0, 500)
            if truncate_point > 200:  # Garante que não seja muito curto
                formatted = formatted[:truncate_point + 1]
            else:
                formatted = formatted[:500] + "..."
        
        return formatted.strip()

