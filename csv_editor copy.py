#!/usr/bin/env python
"""
MCP server minimal qui édite contacts.csv via deux outils :
  - list_columns()   – retourne les colonnes
  - update_cell()    – modifie une cellule
  - name_cities()     – retourne les lignes
  - answer_user() – pour répondre à la question de l'utilisateur

"""
from pathlib import Path
import pandas as pd
import sys, traceback
from mcp.server.fastmcp import FastMCP


# ----- Chemins -----
BASE_DIR = Path(__file__).parent            # dossier du script
CSV_FILE = BASE_DIR / "data" / "contacts.csv"
CSV_CITIES = BASE_DIR / "data" / "cities.csv"
CSV_ROUTES = BASE_DIR / "data" / "routes.csv"

# ----- Définition du serveur -----
mcp = FastMCP(
    "CSV Editor",
    description="Éditeur CSV local très simple",
    dependencies=["pandas"],               # pour le packaging ultérieur
)

# ----- Outils exposés -----
# @mcp.tool()
# def list_columns() -> list[str]:
#     """Return the columns of the CSV."""
#     return pd.read_csv(CSV_FILE).columns.tolist()

@mcp.tool()
def name_cities() -> list[str]:
    """Return the cities of the CSV."""
    return pd.read_csv(CSV_CITIES)["name"].tolist()

@mcp.tool()
def update_cell(row: int, column: str, value: str) -> str:
    """
    Met à jour la valeur de la cellule (row, column).
    - row : index 0-based
    - column : nom de la colonne
    - value : nouvelle valeur
    """
    df = pd.read_csv(CSV_FILE)
    if column not in df.columns:
        raise ValueError(f"Colonne inconnue : {column}")
    if row < 0 or row >= len(df):
        raise ValueError(f"Ligne {row} hors limites")
    df.at[row, column] = value
    df.to_csv(CSV_FILE, index=False)
    return f"OK – ({row}, {column}) ← {value}"

@mcp.tool()
def get_neighbors(city: str) -> list[str]:
    """
    Returns a list of all unique neighboring cities directly connected to the given city
    via any type of transport (airplane, road, ship).
    - city: the name of the city to search from
    - Neighbors are either origins or destinations directly linked to the given city
    - No duplicates are included
    """
    df = pd.read_csv(CSV_ROUTES)
    neighbors = set()

    direct_from = df[df["origin"] == city]["destination"].tolist()
    direct_to = df[df["destination"] == city]["origin"].tolist()

    for neighbor in direct_from + direct_to:
        if neighbor != city:
            neighbors.add(neighbor)

    return sorted(neighbors)


@mcp.tool()
def co2_per_km(origin: str, destination: str, transport_type: str) -> float | None:
    """
    Computes the CO2 emissions per kilometer for a specific route in routes.csv.
    - origin / destination: city names
    - transport_type: one of the values in the 'type' column (e.g., 'airplane', 'road', 'ship')
    - Returns the CO2 per km as a float, or None if data is missing or route not found.
    - Formula: co2_per_km = CO2 / distance
    """
    df = pd.read_csv(CSV_ROUTES)
    route = df[
        (df["origin"] == origin)
        & (df["destination"] == destination)
        & (df["type"] == transport_type)
    ]
    if route.empty:
        return None
    row = route.iloc[0]
    if pd.isna(row["CO2"]) or row["distance"] == 0:
        return None
    return row["CO2"] / row["distance"]

@mcp.tool()
def price_per_km(origin: str, destination: str, transport_type: str) -> float | None:
    """
    Computes the price per kilometer for a specific route in routes.csv.
    - origin / destination: city names
    - transport_type: one of the values in the 'type' column (e.g., 'airplane', 'road', 'ship')
    - Returns the price per km as a float, or None if data is missing or route not found.
    - Formula: price_per_km = price / distance
    """
    df = pd.read_csv(CSV_ROUTES)
    route = df[
        (df["origin"] == origin)
        & (df["destination"] == destination)
        & (df["type"] == transport_type)
    ]
    if route.empty:
        return None
    row = route.iloc[0]
    if pd.isna(row["price"]) or row["distance"] == 0:
        return None
    return row["price"] / row["distance"]

@mcp.tool()
def remove_city(city_name: str) -> str:
    """
    Removes a city from both cities.csv and all matching entries in routes.csv.
    - city_name: exact name of the city to remove
    - Also removes any route where this city is either the origin or destination
    """
    cities = pd.read_csv(CSV_CITIES)
    routes = pd.read_csv(CSV_ROUTES)
    if city_name not in cities["name"].values:
        return f"City {city_name} not found"
    cities = cities[cities["name"] != city_name]
    routes = routes[(routes["origin"] != city_name) & (routes["destination"] != city_name)]
    cities.to_csv(CSV_CITIES, index=False)
    routes.to_csv(CSV_ROUTES, index=False)
    return f"{city_name} removed from cities.csv and routes.csv"

@mcp.tool()
def add_city(name: str, has_port: bool, has_airport: bool, lat: float, lon: float) -> str:
    """
    Adds a new city to cities.csv (routes.csv remains unchanged).
    - name: name of the city
    - has_port / has_airport: booleans indicating transport facilities
    - lat / lon: geographic coordinates of the city
    """
    df = pd.read_csv(CSV_CITIES)
    if name in df["name"].values:
        return f"{name} already exists"
    df.loc[len(df)] = [name, has_port, has_airport, lat, lon]
    df.to_csv(CSV_CITIES, index=False)
    return f"{name} added to cities.csv"

@mcp.tool()
def get_item(origin: str, destination: str, column: str) -> str:
    """
    Returns a specific value from a route in routes.csv.
    - origin / destination: city names
    - column: one of type, time, distance, CO2, price, olon, olat, dlon, dlat
    - Returns the value as a string
    You can use this function to help you for something else if needed.
    """
    df = pd.read_csv(CSV_ROUTES)
    if column not in df.columns:
        return f"Invalid column: {column}"
    route = df[(df["origin"] == origin) & (df["destination"] == destination)]
    if route.empty:
        return f"Route {origin} → {destination} not found"
    return str(route.iloc[0][column])

@mcp.tool()
def update_weight_percent(origin: str, destination: str, column: str, percent: float) -> str:
    """
    Updates a numeric field in routes.csv for a specific route by a given percentage.
    - origin / destination: city names
    - column: numeric column to modify
    - percent: percentage change (e.g. 10.0 increases by 10%, -5.0 decreases by 5%)
    - Returns confirmation with old and new values
    Do not forget to use this function multiple times to update all the routes if necessary.
    """
    df = pd.read_csv(CSV_ROUTES)
    if column not in df.columns or not pd.api.types.is_numeric_dtype(df[column]):
        return f"Invalid or non-numeric column: {column}"
    mask = (df["origin"] == origin) & (df["destination"] == destination)
    if not mask.any():
        return f"Route {origin} → {destination} not found"
    original = df.loc[mask, column].iloc[0]
    df.loc[mask, column] = original * (1 + percent / 100)
    df.to_csv(CSV_ROUTES, index=False)
    return f"{column} for {origin} → {destination} updated by {percent}%: {original} → {df.loc[mask, column].iloc[0]}"


@mcp.prompt()
def answer_user() -> str:
    """Generates a appropriate answer to the user query."""
    return (f"We built an optimization algorithm to determine the best path to send packages depending on parameters. You are an AI agent capable of 1) modifying one or multiple of those parameters based on the user input and 2) providing informations, both of those actions only by using the functions provided in Test tool MCP. Here is a little context of the CSV file you are working with: cities.csv with columns name,has_port,has_airport,lat,lon and routes.csv with columns type,route_name,origin,destination,time,distance,CO2,price,olon,olat,dlon,dlat. You cannot use outside information, only what you get through the functions, do not try to add outside context. Please respond to user input in a very concise way, not saying who you are or what you do, but only answering the query using the appropriate function(s). No follow-up question, no introduction, just the answer the user need or the confirmation you did the action the user need.")


# ----- Boucle MCP -----
if __name__ == "__main__":
    try:
        # transport="stdio" => dialogue JSON-RPC sur stdin/stdout (requis par Claude & Inspector)
        mcp.run(transport="stdio")
    except Exception:
        # Toute exception survient => trace dans stderr (visible dans les logs Claude)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)