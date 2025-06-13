from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class CalendarService:
    """Serviço para integração com a API do Google Calendar"""
    
    def __init__(self):
        self.service = None
        self.scopes = ['https://www.googleapis.com/auth/calendar']
    
    def initialize_service(self, access_token: str) -> bool:
        """
        Inicializa o serviço do Google Calendar com o token de acesso do usuário
        
        Args:
            access_token: Token de acesso OAuth do usuário
            
        Returns:
            True se inicializado com sucesso, False caso contrário
        """
        try:
            # Cria credenciais a partir do token de acesso
            credentials = Credentials(token=access_token)
            
            # Constrói o serviço da API do Calendar
            self.service = build('calendar', 'v3', credentials=credentials)
            
            logger.info("Serviço do Google Calendar inicializado com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao inicializar serviço do Google Calendar: {str(e)}")
            self.service = None
            return False
    
    def get_events(self, calendar_id: str = 'primary', max_results: int = 10, 
                   time_min: Optional[datetime] = None, time_max: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Obtém eventos do calendário
        
        Args:
            calendar_id: ID do calendário (padrão: 'primary')
            max_results: Número máximo de eventos a retornar
            time_min: Data/hora mínima para buscar eventos
            time_max: Data/hora máxima para buscar eventos
            
        Returns:
            Dict contendo os eventos ou erro
        """
        if not self.service:
            return {
                "success": False,
                "error": "Serviço não inicializado",
                "events": []
            }
        
        try:
            # Define período padrão se não especificado
            if not time_min:
                time_min = datetime.utcnow()
            if not time_max:
                time_max = time_min + timedelta(days=7)
            
            # Converte para formato ISO
            time_min_iso = time_min.isoformat() + 'Z'
            time_max_iso = time_max.isoformat() + 'Z'
            
            logger.info(f"Buscando eventos de {time_min_iso} até {time_max_iso}")
            
            # Chama a API do Google Calendar
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=time_min_iso,
                timeMax=time_max_iso,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # Formata os eventos para resposta
            formatted_events = []
            for event in events:
                formatted_event = {
                    'id': event.get('id'),
                    'summary': event.get('summary', 'Sem título'),
                    'description': event.get('description', ''),
                    'start': event.get('start', {}),
                    'end': event.get('end', {}),
                    'location': event.get('location', ''),
                    'attendees': event.get('attendees', [])
                }
                formatted_events.append(formatted_event)
            
            logger.info(f"Encontrados {len(formatted_events)} eventos")
            
            return {
                "success": True,
                "events": formatted_events,
                "count": len(formatted_events)
            }
            
        except Exception as e:
            logger.error(f"Erro ao buscar eventos: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "events": []
            }
    
    def create_event(self, summary: str, start_time: datetime, end_time: datetime,
                     description: str = "", location: str = "", calendar_id: str = 'primary') -> Dict[str, Any]:
        """
        Cria um novo evento no calendário
        
        Args:
            summary: Título do evento
            start_time: Data/hora de início
            end_time: Data/hora de fim
            description: Descrição do evento
            location: Local do evento
            calendar_id: ID do calendário
            
        Returns:
            Dict contendo informações do evento criado ou erro
        """
        if not self.service:
            return {
                "success": False,
                "error": "Serviço não inicializado"
            }
        
        try:
            # Monta o evento
            event = {
                'summary': summary,
                'description': description,
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'America/Sao_Paulo',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'America/Sao_Paulo',
                },
            }
            
            if location:
                event['location'] = location
            
            logger.info(f"Criando evento: {summary} em {start_time}")
            
            # Cria o evento
            created_event = self.service.events().insert(
                calendarId=calendar_id,
                body=event
            ).execute()
            
            logger.info(f"Evento criado com ID: {created_event.get('id')}")
            
            return {
                "success": True,
                "event": {
                    'id': created_event.get('id'),
                    'summary': created_event.get('summary'),
                    'start': created_event.get('start'),
                    'end': created_event.get('end'),
                    'htmlLink': created_event.get('htmlLink')
                }
            }
            
        except Exception as e:
            logger.error(f"Erro ao criar evento: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def format_events_for_speech(self, events: List[Dict[str, Any]]) -> str:
        """
        Formata uma lista de eventos para síntese de fala
        
        Args:
            events: Lista de eventos
            
        Returns:
            Texto formatado para fala
        """
        if not events:
            return "Você não tem eventos marcados para este período."
        
        if len(events) == 1:
            event = events[0]
            start = event.get('start', {})
            summary = event.get('summary', 'Evento sem título')
            
            # Extrai informações de data/hora
            start_time = ""
            if 'dateTime' in start:
                dt = datetime.fromisoformat(start['dateTime'].replace('Z', '+00:00'))
                start_time = f"às {dt.strftime('%H:%M')}"
            elif 'date' in start:
                start_time = "dia todo"
            
            return f"Você tem um evento: {summary} {start_time}."
        
        # Múltiplos eventos
        speech = f"Você tem {len(events)} eventos marcados: "
        for i, event in enumerate(events[:5]):  # Limita a 5 eventos para não ficar muito longo
            summary = event.get('summary', 'Evento sem título')
            if i == len(events) - 1:
                speech += f"e {summary}."
            else:
                speech += f"{summary}, "
        
        if len(events) > 5:
            speech += f" E mais {len(events) - 5} outros eventos."
        
        return speech
    
    def parse_date_from_speech(self, date_text: str) -> Optional[datetime]:
        """
        Converte texto de data falado para datetime
        
        Args:
            date_text: Texto da data (ex: "hoje", "amanhã", "2024-01-15")
            
        Returns:
            Objeto datetime ou None se não conseguir converter
        """
        try:
            now = datetime.now()
            
            if date_text.lower() in ['hoje', 'today']:
                return now.replace(hour=0, minute=0, second=0, microsecond=0)
            elif date_text.lower() in ['amanhã', 'tomorrow']:
                return (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            elif date_text.lower() in ['ontem', 'yesterday']:
                return (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            else:
                # Tenta converter formato ISO
                return datetime.fromisoformat(date_text)
                
        except Exception as e:
            logger.error(f"Erro ao converter data '{date_text}': {str(e)}")
            return None

