from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from pydantic import BaseModel , Field
from typing import Optional
from langchain_core.output_parsers import PydanticOutputParser


class TravelPlanInput(BaseModel):
    start_date: str = Field(description="The start date of the trip (YYYY-MM-DD) e.g. 202412-13.")
    end_date: str = Field(description="The end date of the trip (YYYY-MM-DD) e.g. 2024-1219.")
    destination: str = Field(description="The destination of the trip.")
    adults: Optional[int] = Field(1, description="The number of adults. Defaults to 1.")
    children: Optional[int] = Field(0, description="The number of children. Defaults to 0.")
    travel_style: str = Field(description="The style of travel. e.g. adventure, relax, culture, backpacking, luxury, family-friendly.")
    budget: Optional[int] = Field(description="The total budget for the trip.")
    activities: str = Field(description="The preferred activities. e.g. culture, nature, food, shopping.")
    food_restriction: str = Field(description="Any food restrictions. e.g. vegetarian, gluten-free.")
    
class TravelPlanInputSchema(BaseModel):
    params : TravelPlanInput
    
class TravelDayOutput(BaseModel):
    morning: str = Field(description="The activities for the morning.")
    afternoon: str = Field(description="The activities for the afternoon.")
    evening: str = Field(description="The activities for the evening.")
    
class TravelPlanOutput(BaseModel):
    travel_plan: list[TravelDayOutput]
    
    
@tool(args_schema=TravelPlanInputSchema)

def chain_travel_plan(params:TravelPlanInput) -> TravelPlanOutput:
    """
        Tool that creates a detailed and personalized travel plan.
    """
    model = ChatOpenAI(model_name="gpt-4o", temperature=0.7)
    
    system_prompt = f"""
        You are a top-tier AI travel planner. Create personalized, efficient itineraries adding local tips, not just tourist spots.
        Use the {params: TravelPlanInput} to generate a travel plan.if you don't have enough information, ask the user for more details and do not proceed with the plan until you have the necessary info.

        For each day:
        📅 Date
        🌄 Morning activity 
        🌞 Afternoon activity 
        🌆 Evening activity 
        🍝 give restaurant suggestions (dietary needs) (optional)
        🚇 Transport tips (optional)
        ⏰ Hourly schedule (optional)

        At end:
        🎒 Tailored packing list (optional)
        🛂 Visa info (if needed, with link) (optional)
        🎉 Note relevant events/festivals (optional)
        if necessary, give info on local customs or etiquette (optional)

        Tone: adapt to type of the trip. Include booking links or map links. Adjust style for travel type (luxury, family, adventure, etc.). Only multiple countries if asked. If the destination. You can do a round trip tour within one country.  If the day activity takes the whole day, only give one activity for that day. If the activity contains a difficulty level, include it in the description. 
        give only the information that is gathered and do not invent information, use sources. Keep the arrival and departure time into account. Ask if the user wants a more details.
        """

        
    user_template = """
        Create a travel plan for:
        - Dates: {start_date} to {end_date}
        - Destination: {destination}
        - Adults: {adults}, Children: {children}
        - Style: {travel_style}
        - Budget: {budget}
        - Activities: {activities}
        - Dietary restrictions: {food_restriction}
        - ONLY ON REQUEST: a map or the route and directions, use OpenRouteService API to get the route and directions.

    """

    print(user_template)
    
    model = ChatOpenAI(model_name="gpt-4o")
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", user_template)
    ])

    output_parser = PydanticOutputParser(pydantic_object=TravelPlanOutput)
    chain = prompt | model | output_parser
    result = chain.invoke(input=system_prompt)
    
    print("*" * 80)
    print("chain_travel_plan")
    print("*" * 80)
    return result