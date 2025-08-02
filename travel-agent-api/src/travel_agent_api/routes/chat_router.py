from fastapi import APIRouter, HTTPException
from pydantic import BaseModel  
from travel_agent_api.services.agent_service import Agent  
from travel_agent_api.tools.routes_info_and_map import RouteController




router = APIRouter()

class ChatComplentionRequest(BaseModel):
    
    messages: list

    model_config = {
        "json_schema_extra": {
            "example": { 
                "messages": [
                    {
                        "role": "user", 
                        "content": "Vorrei organizzare un viaggio a Roma"  
                    }
                ]
            }
        }
    }
    
@router.post("/travel-agent")

def chat_completion(request: ChatComplentionRequest):
    """
    Endpoint per la gestione delle richieste di chat.
    Processa i messaggi ricevuti e restituisce una risposta dall'agente di viaggio.
    
    Args:
        request (ChatComplentionRequest): La richiesta contenente i messaggi della 
        conversazione
        
    Returns:
        dict: La risposta elaborata dall'agente di viaggio
        
    Raises:
        HTTPException: In caso di errori durante l'elaborazione della richiesta
    """
    agent = Agent()
    
    response = agent.run(messages=request.messages)
    
    print("*" * 80)
    print("chat_completion")
    print("*" * 80)
    
    return response


class RouteRequest(BaseModel):
    travel_plan: str
    user_wants_map: bool = True

    model_config = {
        "json_schema_extra": {
            "example": {
                "travel_plan": "Partenza: Genova, Fermata 1: Acquario di Genova, Fermata 2: Porto Antico di Genova",
                "user_wants_map": True
            }
        }
    }

@router.post("/generate-route")
def generate_route(request: RouteRequest):
    """
    Endpoint per generare la rotta e mappa dal travel plan.
    """
    try:
        # Chiamata al tuo tool RouteController
        response = RouteController(travel_plan=request.travel_plan, user_wants_map=request.user_wants_map)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
