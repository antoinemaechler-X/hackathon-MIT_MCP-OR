import pandas as pd
import itertools
from geopy.geocoders import Nominatim
import requests

# Load the file





def has_osm_port(city_name):
    geolocator = Nominatim(user_agent="port-checker")
    location = geolocator.geocode(city_name)
    if not location:
        return False

    lat, lon = location.latitude, location.longitude

    overpass_url = "http://overpass-api.de/api/interpreter"
    query = f"""
    [out:json];
    (
      node["harbour"](around:50000,{lat},{lon});
      way["harbour"](around:50000,{lat},{lon});
      relation["harbour"](around:50000,{lat},{lon});
    );
    out body;
    """
    response = requests.post(overpass_url, data={"data": query})
    data = response.json()
    return len(data.get("elements", [])) > 0



# Filter cities with ports

def get_routes(df):
    """
    Generate routes between cities with ports.
    :param df: DataFrame containing city names and coordinates
    :return: DataFrame with route information
    """
    # Filter cities with ports
    ports_df = df[df['has_port'] == True]

    # Generate all pairs of port cities
    pairs = list(itertools.combinations(ports_df.itertuples(index=False), 2))

    # Build route data
    routes = []
    for origin, destination in pairs:
        route = {
            "route_name": f"{origin.name}-{destination.name}",
            "olon": origin.lon,
            "olat": origin.lat,
            "dlon": destination.lon,
            "dlat": destination.lat
        }
        routes.append(route)

    return pd.DataFrame(routes)

if __name__ == "__main__":
    # Load your CSV
    df = pd.read_csv("data/cities.csv")
    df['has_port'] = df['name'].apply(has_osm_port)
    df.to_csv("data/cities.csv", index=False)

    df = df[df['has_port'] == True]

    # Get routes
    routes_df = get_routes(df)

    # Save result (optional)
    routes_df.to_csv("data/port_routes.csv", index=False)
