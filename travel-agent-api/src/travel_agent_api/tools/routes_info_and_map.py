import openai 
import os
import requests
from geopy.geocoders import Nominatim
from dotenv import load_dotenv
from langchain.tools import tool

# Load environment variables
load_dotenv()
print("🔐 ORS_API_KEY from env:", os.getenv("ORS_API_KEY"))  


openai.api_key = os.getenv("OPENAI_API_KEY")
ORS_API_KEY = os.getenv("ORS_API_KEY")

# Initialize geocoder
geolocator = Nominatim(user_agent="AI_Travel_agent_API") 

class RouteController:
    def __init__(self, travel_plan, profile="driving-car"):
        self.travel_plan = travel_plan
        self.coords = []
        self.profile = profile
        print("🧭 RouteController initialized with travel plan:", self.travel_plan)

    def extract_locations(self):
        """Ask ChatGPT to extract key locations from the travel plan"""
        print("🔍 Extracting locations from travel plan...")
        system_msg = (
            "You are a travel assistant. Extract from the travel plan that the user will visit ONLY the towns, cities, or points of interest. If needed, add the country code or town to the point of interest. "
        )
        user_msg = f"Travel plan: {self.travel_plan}\nReturn a comma-separated list of locations only."

        try:
            client = openai.Client()
            response = client.chat.completions.create(
                model="gpt-4o",  
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg}
                ]
            )
            print("🧾 Raw OpenAI response:", response)

            locations_text = response.choices[0].message.content.strip()
            print("📜 Locations extracted from travel plan:", locations_text)

            locations = [loc.strip() for loc in locations_text.split(",") if loc.strip()]
            print("📍 Locations extracted:", locations)
            return locations

        except Exception as e:
            print("❌ Error during location extraction:", str(e))
            return []
    

    def geocode_locations(self, locations):
        """Convert location names to coordinates [lon, lat]"""
        coords = []
        for location in locations:
            loc_obj = geolocator.geocode(location)
            if loc_obj:
                coords.append([loc_obj.longitude, loc_obj.latitude])
                print(f"✅ {location} → {loc_obj.latitude}, {loc_obj.longitude}")
        return coords

    def determine_profile(self):
        """Determine OpenRouteService profile based on travel plan"""
        try:
            response = openai.Client().chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Based on the user travel plan, return the correct OpenRouteService profile: "
                        "one of: car, foot-walking, mountainbike, roadbike, e-bike, bike, wheelchair, heavyvehicle. "
                        "Choose only one. Do not explain."},
                    {"role": "user", "content": f"travel plan: {self.travel_plan}"}
                ]
            )
        
            profile = response.choices[0].message.content.strip().lower()
            print(f"🏷️ Profile determined: {profile}")
            return profile
    
        except Exception as e:
            print("❌ Error determining profile:", str(e))
            return "driving-car"

    def get_route_map(self):
        """Call OpenRouteService API to get the route as GeoJSON"""
        print("iniziamo la richiesta per GeoJSON")
        if len(self.coords) < 2:
            return {"error": "At least two coordinates are required to generate a route."}


        headers = {
            "Authorization": ORS_API_KEY,
            "Content-Type": "application/json"
        }

        body = {"coordinates": self.coords}
        
        print("Sending request to ORS...")
        print("Profile:", self.profile)
        print("Coords:", self.coords)

        url = f"https://api.openrouteservice.org/v2/directions/{self.profile}"

        response = requests.post(url, headers=headers, json=body)

        try:
            data = response.json()
        except Exception as e:
            return {
                "error": "Invalid JSON received from ORS",
                "details": response.text
            }

        if response.status_code == 200:
            data = response.json()

            # Genera link a Google Maps dal primo e ultimo punto
            start = self.coords[0]
            end = self.coords[-1]
            gmaps_url = f"https://www.google.com/maps/dir/{start[1]},{start[0]}/{end[1]},{end[0]}"
            data["google_maps_url"] = gmaps_url

            return data
        else:
            return {
                "error": f"Unable to fetch route data. Status: {response.status_code}",
                "details": response.text
            }


    def generate_route(self):
        """Extracts locations, determines profile, and calls the API"""
        print("🧪 Starting route generation...")

        locations = self.extract_locations()
        coords = self.geocode_locations(locations)

        if len(coords) < 2:
            return {"error": "Not enough locations to generate a route."}

        self.profile = self.determine_profile()
        self.coords = coords

        return self.get_route_map()


@tool
def routes_info_and_map(travel_plan: str) -> dict:
    """
    Generates a route map or location info from a travel plan using OpenRouteService.
    """
    print("⚙️ Tool `routes_info_and_map` called...")

    controller = RouteController(travel_plan)
    return controller.generate_route()

