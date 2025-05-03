from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import requests
from send_to_claude import send_to_claude
from solver import solve_shortest_path, build_city_graph, get_node
from src.data_preprocess.add_city import add_city
import pandas as pd

app = FastAPI()

# Allow requests from your frontend (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development only! Use your real domain in production.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def geocode_city(city_name: str) -> tuple[float, float]:
    """
    Look up a place name via Nominatim and return (lat, lon).
    Raises ValueError if no match is found.
    """
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": city_name,
        "format": "json",
        "limit": 1
    }
    # Nominatim requires a valid User-Agent
    headers = {
        "User-Agent": "demo-app/1.0 (youremail@example.com)"
    }
    resp = requests.get(url, params=params, headers=headers)
    resp.raise_for_status()
    results = resp.json()
    if not results:
        raise ValueError(f"No location found for “{city_name}”")
    lat = float(results[0]["lat"])
    lon = float(results[0]["lon"])
    return lat, lon

# --- Your model functions to implement ---
def solve_model(start:str, end:str, preferences, city_path = "data/cities.csv",route_path = "data/routes.csv"):
    cities_df = pd.read_csv(city_path)
    routes_df = pd.read_csv(route_path)
    cities_df, routes_df = add_city(cities_df, routes_df, start, has_airport=True)
    cities_df, routes_df = add_city(cities_df, routes_df, end, has_airport=True)
    coords_start = cities_df[cities_df["name"] == start][["lat", "lon"]].values[0]
    coords_end = cities_df[cities_df["name"] == end][["lat", "lon"]].values[0]
    graph = build_city_graph(cities_df, routes_df)
    source_node = get_node(start)
    target_node = get_node(end)
    path, cost = solve_shortest_path(graph, source_node, target_node, preferences)



    

    
    # TODO: Implement your logic here
    
    return {
        "coords_start": coords_start,
        "coords_end": coords_end,
        "route": route
    }

def query_model(comment):
    send_to_claude(comment)
    return {"status": "success", "echo": comment}

# --- API Endpoints ---

@app.post("/api/solve")
async def solve(request: Request):
    data = await request.json()
    start = data.get("start")
    end = data.get("end")
    preferences = data.get("preferences")
    result = solve_model(start, end, preferences)
    return result

@app.post("/api/comment")
async def comment(request: Request):
    data = await request.json()
    comment = data.get("comment")
    result = query_model(comment)
    return result