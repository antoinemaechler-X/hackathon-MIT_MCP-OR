import pandas as pd
import geopandas as gpd
from shapely.geometry import LineString, Point

# Charger les données des routes ferroviaires


# Générer toutes les paires de villes
from itertools import combinations


# Liste pour stocker les routes valides
valid_routes = []


def get_routes_from_cities(routes, cities, type: str = "train"):
    city_pairs = list(combinations(cities['name'], 2))
    for city1, city2 in city_pairs:
        point1 = cities_gdf[cities_gdf['name'] == city1].geometry.values[0]
        point2 = cities_gdf[cities_gdf['name'] == city2].geometry.values[0]
        line = LineString([point1, point2])
        
        # Vérifier si une route ferroviaire correspond à cette ligne
        for route in routes.geometry:
            if route.contains(line):
                # Vérifier s'il y a une troisième ville sur la route
                intermediate_cities = cities_gdf[
                    (cities_gdf['name'] != city1) & 
                    (cities_gdf['name'] != city2) & 
                    (cities_gdf.geometry.within(route))
                ]
                if intermediate_cities.empty:
                    valid_routes.append((city1, city2))
                break
    return valid_routes

if __name__ == "__main__":
    # Charger les données des villes et des routes
    routes = gpd.read_file('data/NTAD_Amtrak_Routes_-6198991300221713211.csv')  # Remplacez par le chemin vers vos données

# Charger la liste des villes
    cities = pd.read_csv('data/cities.csv')  # Votre fichier CSV contenant les villes
    cities_gdf = gpd.GeoDataFrame(cities, geometry=gpd.points_from_xy(cities.lon, cities.lat))
    valid_routes = get_routes_from_cities(routes, cities_gdf, type="train")
