import requests
import json
import uuid

class EventStore:
    def __init__(self, host="http://eventstore:2113", stream="events"):
        self.host = host
        self.stream = stream

    def append_event(self, event_type: str, event_data: dict):
        """Armazena um evento no EventStoreDB"""
        url = f"{self.host}/streams/{self.stream}"
        headers = {
            "Content-Type": "application/vnd.eventstore.events+json"
        }

        # Criar um payload no formato correto
        event_payload = [{
            "eventId": str(uuid.uuid4()),  # UUID obrigatório
            "eventType": event_type,
            "data": event_data 
        }]

        # Print para debugging
        #print("Payload enviado:", json.dumps(event_payload, indent=2))
        
        response = requests.post(url, headers=headers, data=json.dumps(event_payload))

        if response.status_code not in [201, 204]:
            print(f"Erro ao armazenar evento {event_type}: {response.text}")
        else:
            print(f"Evento {event_type} armazenado com sucesso!")

    def get_events(self):
        """Recupera eventos do EventStoreDB"""
        url = f"{self.host}/streams/{self.stream}/head/backward/10"
        headers = {"Accept": "application/json"}
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Erro ao recuperar eventos: {response.text}")
            return []