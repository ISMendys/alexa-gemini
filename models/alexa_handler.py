from typing import Dict, Any, Optional
from pydantic import BaseModel
import logging
from services.gemini_service import GeminiService
from services.calendar_service import CalendarService
from services.oauth_service import oauth_service
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class AlexaRequestHandler:
    """Classe para processar diferentes tipos de requisições da Alexa"""
    
    def __init__(self):
        self.intent_handlers = {
            "ConversarComGemini": self.handle_conversar_gemini,
            "ConsultarAgenda": self.handle_consultar_agenda,
            "CriarEvento": self.handle_criar_evento,
            "AMAZON.HelpIntent": self.handle_help,
            "AMAZON.CancelIntent": self.handle_cancel,
            "AMAZON.StopIntent": self.handle_stop
        }
        
        # Inicializa os serviços
        self.gemini_service = GeminiService()
        self.calendar_service = CalendarService()
    
    def process_request(self, alexa_request: Dict[str, Any]) -> Dict[str, Any]:
        """Processa uma requisição da Alexa e retorna a resposta apropriada"""
        try:
            request_type = alexa_request.get("request", {}).get("type")
            
            if request_type == "LaunchRequest":
                return self.handle_launch()
            elif request_type == "IntentRequest":
                return self.handle_intent(alexa_request)
            elif request_type == "SessionEndedRequest":
                return self.handle_session_ended()
            else:
                return self.create_response("Desculpe, não consegui processar sua solicitação.")
        
        except Exception as e:
            logger.error(f"Erro ao processar requisição da Alexa: {str(e)}")
            return self.create_response("Desculpe, ocorreu um erro interno. Tente novamente.")
    
    def handle_launch(self) -> Dict[str, Any]:
        """Manipula o LaunchRequest (quando o usuário abre a skill)"""
        speech_text = (
            "Olá! Eu sou sua assistente inteligente conectada ao Gemini. "
            "Você pode me pedir para conversar sobre qualquer assunto ou consultar sua agenda. "
            "Por exemplo, diga: 'Converse comigo sobre tecnologia' ou 'Consulte minha agenda de hoje'. "
            "Como posso ajudá-lo?"
        )
        return self.create_response(speech_text, should_end_session=False)
    
    def handle_intent(self, alexa_request: Dict[str, Any]) -> Dict[str, Any]:
        """Manipula IntentRequest baseado no intent específico"""
        intent = alexa_request.get("request", {}).get("intent", {})
        intent_name = intent.get("name")
        
        handler = self.intent_handlers.get(intent_name)
        if handler:
            return handler(intent, alexa_request)
        else:
            return self.create_response(
                "Desculpe, não entendi o que você quer. "
                "Tente dizer 'ajuda' para ver o que posso fazer."
            )
    
    def handle_conversar_gemini(self, intent: Dict[str, Any], alexa_request: Dict[str, Any]) -> Dict[str, Any]:
        """Manipula o intent ConversarComGemini"""
        slots = intent.get("slots", {})
        pergunta_slot = slots.get("pergunta", {})
        pergunta = pergunta_slot.get("value", "")
        
        if not pergunta:
            speech_text = "Sobre o que você gostaria de conversar? Faça uma pergunta e eu responderei usando o Gemini."
            return self.create_response(speech_text, should_end_session=False)
        
        # Chama o serviço do Gemini
        logger.info(f"Processando pergunta para o Gemini: {pergunta}")
        gemini_response = self.gemini_service.generate_content(pergunta)
        
        if gemini_response["success"]:
            # Formata a resposta para fala
            speech_text = self.gemini_service.format_for_speech(gemini_response["response"])
        else:
            speech_text = gemini_response["response"]
        
        return self.create_response(speech_text)
    
    def handle_consultar_agenda(self, intent: Dict[str, Any], alexa_request: Dict[str, Any]) -> Dict[str, Any]:
        """Manipula o intent ConsultarAgenda"""
        # Extrai o user ID da requisição da Alexa
        user_id = alexa_request.get("session", {}).get("user", {}).get("userId", "")
        
        # Verifica se o usuário está autenticado
        if not oauth_service.is_user_authenticated(user_id):
            speech_text = (
                "Para consultar sua agenda, você precisa primeiro vincular "
                "sua conta Google no aplicativo Alexa. Vá em Configurações da Skill e "
                "configure o Account Linking. Depois disso, poderei acessar sua agenda do Google."
            )
            return self.create_response(speech_text)
        
        # Obtém token de acesso
        access_token = oauth_service.get_user_access_token(user_id)
        if not access_token:
            speech_text = (
                "Houve um problema com sua autenticação. "
                "Tente vincular sua conta Google novamente nas configurações da skill."
            )
            return self.create_response(speech_text)
        
        # Inicializa o serviço do Calendar
        if not self.calendar_service.initialize_service(access_token):
            speech_text = "Desculpe, não consegui acessar sua agenda no momento. Tente novamente."
            return self.create_response(speech_text)
        
        slots = intent.get("slots", {})
        data_slot = slots.get("data", {})
        periodo_slot = slots.get("periodo", {})
        
        data = data_slot.get("value", "")
        periodo = periodo_slot.get("value", "")
        
        # Determina o período para consulta
        if data:
            target_date = self.calendar_service.parse_date_from_speech(data)
            if target_date:
                time_min = target_date
                time_max = target_date + timedelta(days=1)
                period_text = f"para {data}"
            else:
                period_text = "para hoje"
                time_min = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                time_max = time_min + timedelta(days=1)
        elif periodo:
            if periodo.lower() in ['hoje', 'today']:
                time_min = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                time_max = time_min + timedelta(days=1)
                period_text = "para hoje"
            elif periodo.lower() in ['amanhã', 'tomorrow']:
                time_min = (datetime.now() + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
                time_max = time_min + timedelta(days=1)
                period_text = "para amanhã"
            else:
                time_min = datetime.now()
                time_max = time_min + timedelta(days=7)
                period_text = f"para {periodo}"
        else:
            time_min = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            time_max = time_min + timedelta(days=1)
            period_text = "para hoje"
        
        # Busca eventos
        result = self.calendar_service.get_events(time_min=time_min, time_max=time_max)
        
        if result["success"]:
            events = result["events"]
            speech_text = self.calendar_service.format_events_for_speech(events)
        else:
            speech_text = f"Desculpe, não consegui consultar sua agenda {period_text}. Tente novamente."
        
        return self.create_response(speech_text)
    
    def handle_criar_evento(self, intent: Dict[str, Any], alexa_request: Dict[str, Any]) -> Dict[str, Any]:
        """Manipula o intent CriarEvento"""
        slots = intent.get("slots", {})
        titulo_slot = slots.get("titulo", {})
        data_slot = slots.get("data", {})
        hora_slot = slots.get("hora", {})
        
        titulo = titulo_slot.get("value", "")
        data = data_slot.get("value", "")
        hora = hora_slot.get("value", "")
        
        if not titulo:
            speech_text = "Qual é o título do evento que você quer criar?"
            return self.create_response(speech_text, should_end_session=False)
        
        # Por enquanto, retorna mensagem sobre configuração necessária
        speech_text = f"Para criar o evento '{titulo}'"
        if data:
            speech_text += f" para {data}"
        if hora:
            speech_text += f" às {hora}"
        speech_text += (
            ", você precisa primeiro vincular sua conta Google no aplicativo Alexa. "
            "Vá em Configurações da Skill e configure o Account Linking. "
            "Depois disso, poderei criar eventos na sua agenda do Google."
        )
        
        return self.create_response(speech_text)
    
    def handle_help(self, intent: Dict[str, Any], alexa_request: Dict[str, Any]) -> Dict[str, Any]:
        """Manipula o intent de ajuda"""
        speech_text = (
            "Eu posso ajudá-lo de várias formas! "
            "Você pode me pedir para conversar sobre qualquer assunto, por exemplo: "
            "'Converse comigo sobre inteligência artificial'. "
            "Também posso consultar sua agenda dizendo: 'Consulte minha agenda de hoje'. "
            "Ou criar eventos: 'Marque reunião amanhã às 14 horas'. "
            "Para usar as funções da agenda, você precisa vincular sua conta Google "
            "nas configurações da skill no aplicativo Alexa. "
            "O que você gostaria de fazer?"
        )
        return self.create_response(speech_text, should_end_session=False)
    
    def handle_cancel(self, intent: Dict[str, Any], alexa_request: Dict[str, Any]) -> Dict[str, Any]:
        """Manipula o intent de cancelamento"""
        speech_text = "Operação cancelada. Posso ajudá-lo com algo mais?"
        return self.create_response(speech_text, should_end_session=False)
    
    def handle_stop(self, intent: Dict[str, Any], alexa_request: Dict[str, Any]) -> Dict[str, Any]:
        """Manipula o intent de parada"""
        speech_text = "Até logo! Foi um prazer ajudá-lo."
        return self.create_response(speech_text, should_end_session=True)
    
    def handle_session_ended(self) -> Dict[str, Any]:
        """Manipula o SessionEndedRequest"""
        # Não precisa retornar resposta para SessionEndedRequest
        return {}
    
    def create_response(self, speech_text: str, should_end_session: bool = False, 
                       reprompt_text: Optional[str] = None) -> Dict[str, Any]:
        """Cria uma resposta formatada para a Alexa"""
        response = {
            "version": "1.0",
            "response": {
                "outputSpeech": {
                    "type": "PlainText",
                    "text": speech_text
                },
                "shouldEndSession": should_end_session
            }
        }
        
        if reprompt_text and not should_end_session:
            response["response"]["reprompt"] = {
                "outputSpeech": {
                    "type": "PlainText",
                    "text": reprompt_text
                }
            }
        
        return response

