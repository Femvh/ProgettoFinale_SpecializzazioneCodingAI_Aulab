from datetime import datetime
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
# Tools
from travel_agent_api.tools.flights_finder import flights_finder
from travel_agent_api.tools.hotels_finder import hotels_finder
from travel_agent_api.tools.chain_historical_expert import chain_historical_expert
from travel_agent_api.tools.chain_travel_plan import chain_travel_plan
from travel_agent_api.tools.routes_info_and_map import routes_info_and_map

FLIGHTS_OUTPUT = """
        format: markdown, SENZA FOTO
            ## Miglior Opzione 
            
            ### Andata:
            - Compagnia aerea: Ryanair
            - Data di partenza: 2024-12-13
            - Ora di partenza: 10:00
            - Durata del volo: 1h 30m
            
            ### Ritorno:
            - Compagnia aerea: Ryanair
            - Data di ritorno: 2024-12-19
            - Ora di ritorno: 14:30
            - Durata del volo: 1h 30m
            
            Inserisci il link di Google per la prenotazione se possibile.
            
            #### Altri opzioni disponibili:
            
            - Compagnia aerea: Ryanair
            - Data di partenza: 2024-12-13
            - Ora di partenza: 10:00
            - Durata del volo: 1h 30m
            
            - Compagnia aerea: Ryanair
            - Data di ritorno: 2024-12-19
            - Ora di ritorno: 14:30
            - Durata del volo: 1h 30m
            ...
        """
        
HOTELS_OUTPUT ="""
        
    format: markdown 
    Ripeti queste istruzioni per creare un output dettagliato per ogni hotel. Crea un output per minimo 2 hotel.
    
    #### Hotel 1
    Inserisci la foto/le foto dell'hotel se disponibile.
    
    *Descrizione:* Camere e suite eleganti, a volte con vista sulla città, in hotel esclusivo con piscina panoramica e spa.
    *Prezzo per notte:* €296 (prima delle tasse e spese: €260)
    *Prezzo totale:* €2,660 (prima delle tasse e spese: €2,336)
    *Check-in:* 15:00, Check-out: 12:00
    *Valutazione complessiva:* 4.5 su 5
    *Servizi Inclusi:* Spa, Piscina, Parcheggio gratuito
    ...
    
"""

TRAVEL_PLAN_OUTPUT ="""
    format: markdown
    Ripeti queste istruzioni per creare un piano di viaggio dettagliato per ogni giorno del viaggio.

    ### Itinerario:
    
    ### Giorno 1 - 2024-12-13:
    
    *Mattina:* Descrizione dell'attivita' da svolgere la mattina.
    Aggiungi eventuali link per la prenotazione/info.
    
    *Pomeriggio:* Descrizione dell'attivita' da svolgere il pomeriggio
    Aggiungi eventuali link per la prenotazione/info

    *Sera:* Descrizione dell'attivita' da svolgere la sera
    Aggiungi eventuali link per la prenotazione/info
    
    ...

"""
ROUTES_INFO_AND_MAP_OUTPUT = f"""
    format: markdown
    USA QUESTO TOOL SOLO SU RICHIESTA DELL'UTENTE, NON AUTOMATICAMENTE. SOLO SE RICHIEDE UNA MAPPA O INFORMAZIONI DETTAGLIATI SULLE INDICAZIONI STRADALI DEL PERCORSO.    
    ### Mappa del percorso: 
    inserisci il link della mappa se disponibile o l'immagine generata dal tool {routes_info_and_map}.

    ### le Informazioni sul percorso:
    - **Partenza:** Roma
    - **Arrivo:** Milano
    - **Distanza:** 570 km
    - **Durata:** 6 ore
    - **mezzo:** Auto
"""

class Agent:
    def __init__(self):
        self.current_datetime = datetime.now()
        self.model = ChatOpenAI(model_name="gpt-4o")
        self.tools = [
            chain_historical_expert,
            flights_finder,
            hotels_finder,
            chain_travel_plan,
            routes_info_and_map
        ]
        self.agent_executor = create_react_agent(self.model , self.tools)
        pass
    def run(self, messages : list):
        SYSTEM_PROMPT = f"""
            Sei un travel planner. Il tuo compito e' organizzare il viaggio per l'utente. 
            In base al tipo di viaggio, adegui il tono.
            La data di oggi e' {self.current_datetime}
            Usa le seguenti istruzioni per creare un output ( ATTENZIONE: esempio di output mappa e informazioni SOLO SU RICHIESTA DELL'UTENTE, NON AUTOMATICAMENTE. SOLO SE RICHIEDE UNA MAPPA O INFORMAZIONI DETTAGLIATI SULLE INDICAZIONI STRADALI DEL PERCORSO.):
            Esempio Ouput Voli: 
            {FLIGHTS_OUTPUT}
            Esempio Output Hotel:
            {HOTELS_OUTPUT}
            Esempio di Output Viaggio:
            {TRAVEL_PLAN_OUTPUT}
            Esempio di Output Mappa e Informazioni:
            {ROUTES_INFO_AND_MAP_OUTPUT}
        """
        convesation_history = [{"role" : "system" , "content" :   SYSTEM_PROMPT}] + messages
        response = self.agent_executor.invoke({"messages" : convesation_history})
        return response["messages"][1:]
    

    