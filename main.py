from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import requests

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
def solve_model(start, end, preferences):
    # Get coordinates using the existing geocode_city function
    coords_start = geocode_city(start)
    coords_end = geocode_city(end)
    
    # TODO: Implement your logic here
    
    return {
        "message": f"Solving model for {start} to {end}",
        "coords_start": coords_start,
        "coords_end": coords_end,
        "preferences": preferences
    }

def query_model(comment):
    # TODO: Implement your logic here
    # Example return:
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