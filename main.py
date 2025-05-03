from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import requests
from send_to_claude import send_to_claude
from solver import solve_shortest_path, build_city_graph, get_node
from src.data_preprocess.add_city import add_city
import pandas as pd
import numpy as np
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
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
        raise ValueError(f'No location found for "{city_name}"')
    lat = float(results[0]["lat"])
    lon = float(results[0]["lon"])
    return lat, lon

# --- Your model functions to implement ---
def solve_model(start:str, end:str, preferences, city_path = "data/cities.csv",route_path = "data/routes_clean.csv"):
    cities_df = pd.read_csv(city_path)
    routes_df = pd.read_csv(route_path)
    cities_df, routes_df = add_city(cities_df, routes_df, start, has_airport=False)
    cities_df, routes_df = add_city(cities_df, routes_df, end, has_airport=False)

    # Normalize the costs by dividing by the mean values
    mean_time = routes_df["time"].mean()
    mean_cost = routes_df["price"].mean()
    mean_emissions = routes_df["CO2"].mean()

    routes_df["time"] = routes_df["time"] / mean_time
    routes_df["price"] = routes_df["price"] / mean_cost
    routes_df["CO2"] = routes_df["CO2"] / mean_emissions
    
    # Convert coordinates to lists for JSON serialization
    coords_start = cities_df[cities_df["name"] == start][["lat", "lon"]].values[0].tolist()
    coords_end = cities_df[cities_df["name"] == end][["lat", "lon"]].values[0].tolist()
    
    # Convert DataFrames to dictionaries
    cities_dict = cities_df.to_dict(orient="records")
    routes_dict = routes_df.to_dict(orient="records")
    
    graph = build_city_graph(cities_dict, routes_dict)
    source_node = get_node(start)
    target_node = get_node(end)
    
    alpha = preferences["timeImportance"]
    beta = preferences["costImportance"]
    gamma = preferences["emissionsImportance"]
    path, total_cost, time_cost, cost_cost, emissions_cost = solve_shortest_path(graph, source_node, target_node, alpha, beta, gamma)

    # Now query the cost given extreme preferences
    _, total_cost_time_opt, time_cost_time_opt, cost_cost_time_opt, emissions_cost_time_opt = solve_shortest_path(graph, source_node, target_node, 1.0, 0.0, 0.0)
    _, total_cost_cost_opt, time_cost_cost_opt, cost_cost_cost_opt, emissions_cost_cost_opt = solve_shortest_path(graph, source_node, target_node, 0.0, 1.0, 0.0)
    _, total_cost_emissions_opt, time_cost_emissions_opt, cost_cost_emissions_opt, emissions_cost_emissions_opt = solve_shortest_path(graph, source_node, target_node, 0.0, 0.0, 1.0)
    
    # Create route segments
    route = []
    for i in range(len(path) - 1):
        current_node = path[i]
        next_node = path[i + 1]
        
        # Skip storage nodes
        if "storage" in current_node or "storage" in next_node:
            continue
            
        # Extract city names and transport modes
        current_city = current_node.split("_")[0]
        next_city = next_node.split("_")[0]
        mode = current_node.split("_")[1]
        
        # Get coordinates for the cities and convert to lists
        current_coords = cities_df[cities_df["name"] == current_city][["lat", "lon"]].values[0].tolist()
        next_coords = cities_df[cities_df["name"] == next_city][["lat", "lon"]].values[0].tolist()
        
        # Map mode to the correct format
        mode_map = {
            "road": "road",
            "train": "train",
            "airplane": "airplane",
            "ship": "boat"
        }
        
        route.append({
            "from": current_coords,
            "to": next_coords,
            "mode": mode_map.get(mode, "road")  # Default to road if mode not found
        })
    
    # Convert Gurobi LinExpr objects to regular Python numbers
    def convert_cost(cost):
        if hasattr(cost, 'getValue'):
            return float(cost.getValue())
        return float(cost)
    
    return {
        "coords_start": coords_start,
        "coords_end": coords_end,
        "route": route,
        "costs": {
            "current": {
                "total": convert_cost(total_cost),
                "time": convert_cost(time_cost),
                "cost": convert_cost(cost_cost),
                "emissions": convert_cost(emissions_cost)
            },
            "time_optimized": {
                "total": convert_cost(total_cost_time_opt),
                "time": convert_cost(time_cost_time_opt),
                "cost": convert_cost(cost_cost_time_opt),
                "emissions": convert_cost(emissions_cost_time_opt)
            },
            "cost_optimized": {
                "total": convert_cost(total_cost_cost_opt),
                "time": convert_cost(time_cost_cost_opt),
                "cost": convert_cost(cost_cost_cost_opt),
                "emissions": convert_cost(emissions_cost_cost_opt)
            },
            "emissions_optimized": {
                "total": convert_cost(total_cost_emissions_opt),
                "time": convert_cost(time_cost_emissions_opt),
                "cost": convert_cost(cost_cost_emissions_opt),
                "emissions": convert_cost(emissions_cost_emissions_opt)
            }
        }
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