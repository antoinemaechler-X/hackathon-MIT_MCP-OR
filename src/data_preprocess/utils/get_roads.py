####
#This code is long

###


import pandas as pd
import math
import requests

AVG_PLANE_SPEED_KMH = 800     # km/h en croisière
OVERHEAD_TIME_H    = 1.0      # h total (embarquement + débarquement)
AVG_BOAT_SPEED_KMH = 30        # km/h en croisière



def get_road_distance_and_time(coords1, coords2):## duplicated in src/data_preprocess/get_roads.py
    """
    Compute road distance (km) and travel time (hours) using OSRM between two coordinate pairs.
    :param coords1: (lat, lon) tuple for origin
    :param coords2: (lat, lon) tuple for destination
    :return: (distance_km, duration_h)
    """
    lat1, lon1 = coords1
    lat2, lon2 = coords2
    url = f"http://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}?overview=false"
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()
    route = data['routes'][0]
    distance_km = route['distance'] / 1000.0
    duration_h = route['duration'] / 3600.0
    return distance_km, duration_h



import math

# Paramètres à ajuster
AVG_PLANE_SPEED_KMH = 800     # km/h en croisière
OVERHEAD_TIME_H    = 1.0      # h total (embarquement + débarquement)



def haversine_distance(coords1, coords2):## duplicated in src/data_preprocess/get_roads.py
    """
    Calcule la distance grand-cercle (km) entre deux points (lat, lon).
    """
    lat1, lon1 = coords1
    lat2, lon2 = coords2
    R = 6371.0  # rayon de la Terre en km
    φ1, φ2 = math.radians(lat1), math.radians(lat2)
    Δφ = math.radians(lat2 - lat1)
    Δλ = math.radians(lon2 - lon1)
    a = math.sin(Δφ/2)**2 + math.cos(φ1)*math.cos(φ2)*math.sin(Δλ/2)**2
    return 2 * R * math.asin(math.sqrt(a))

def get_airplane_distance_and_time_proxy(coords1, coords2,
                                         speed_kmh=AVG_PLANE_SPEED_KMH,
                                         overhead_h=OVERHEAD_TIME_H):## duplicated in src/data_preprocess/get_roads.py
    """
    Retourne :
      - distance_km : distance grand‐cercle entre coords1 et coords2
      - time_h       : temps total estimé = overhead + distance/speed
    """
    dist_km = haversine_distance(coords1, coords2)
    flight_time_h = dist_km / speed_kmh
    total_time_h = flight_time_h + overhead_h
    return dist_km, total_time_h

def get_boat_time_proxy(distance_km):
    """
    Retourne le temps de trajet en bateau (en heures) pour une distance donnée (en km).
    :param distance_km: distance en km
    :return: temps de trajet en heures
    """
    return distance_km / AVG_BOAT_SPEED_KMH



def get_rp_routes(df,city:pd.Series,type:str="road"):
    """
    Generate routes between the old cities and the new one.
    :param df: DataFrame containing city names and coordinates
    :param city: row
    :return: DataFrame with route information
    """
    routes = []
    for index, row in df.iterrows():
        if row['name'] != city['name']:
            coord1s = (row['lat'], row['lon'])
            coord2s = (city['lat'], city['lon'])
            if type == "airplane":
                distance, time = get_airplane_distance_and_time_proxy(coord1s, coord2s)
            elif type == "road":
                distance, time = get_road_distance_and_time(coord1s, coord2s)
            route = {
                "type": type,
                "route_name": f"{row['name']}-{city['name']}",
                "origin": row['name'],
                "destination": city['name'],
                "distance": distance,
                "time": time,
                "olon": row['lon'],
                "olat": row['lat'],
                "dlon": city['lon'],
                "dlat": city['lat']
            }
            routes.append(route)
            # symetric route
            route = {
                "type": type,
                "route_name": f"{city['name']}-{row['name']}",
                "origin": city['name'],
                "destination": row['name'],
                "distance": distance,
                "time": time,
                "olon": city['lon'],
                "olat": city['lat'],
                "dlon": row['lon'],
                "dlat": row['lat']
            }
            routes.append(route)
    road_df = pd.DataFrame(routes)
    road_df = road_df[["type", "route_name", "origin", "destination",
                        "time", "distance", "olat", "olon", "dlat", "dlon"]]
    return road_df


# Paramètres à ajuster


def haversine_distance(coords1, coords2): ## duplicated in src/data_preprocess/get_roads.py
    """
    Calcule la distance grand-cercle (km) entre deux points (lat, lon).
    """
    lat1, lon1 = coords1
    lat2, lon2 = coords2
    R = 6371.0  # rayon de la Terre en km
    φ1, φ2 = math.radians(lat1), math.radians(lat2)
    Δφ = math.radians(lat2 - lat1)
    Δλ = math.radians(lon2 - lon1)
    a = math.sin(Δφ/2)**2 + math.cos(φ1)*math.cos(φ2)*math.sin(Δλ/2)**2
    return 2 * R * math.asin(math.sqrt(a))

def get_airplane_distance_and_time_proxy(coords1, coords2,
                                         speed_kmh=AVG_PLANE_SPEED_KMH,
                                         overhead_h=OVERHEAD_TIME_H):## duplicated in src/data_preprocess/get_roads.py
    """
    Retourne :
      - distance_km : distance grand‐cercle entre coords1 et coords2
      - time_h       : temps total estimé = overhead + distance/speed
    """
    dist_km = haversine_distance(coords1, coords2)
    flight_time_h = dist_km / speed_kmh
    total_time_h = flight_time_h + overhead_h
    return dist_km, total_time_h


def generate_all_routes(cities_path):
    cities_df = pd.read_csv(cities_path)
    plane_dfs = []
    airplane_city_df = cities_df[cities_df["has_airport"] == True]
    for i, row in airplane_city_df.iterrows():
        for j, row2 in airplane_city_df.iterrows():
            if i <j:
                plane_route_df = get_rp_routes(airplane_city_df, row, type="airplane")
                plane_dfs.append(plane_route_df)
    airplane_df = pd.concat(plane_dfs, ignore_index=True)

    road_dfs = []
    road_city_df = cities_df[cities_df["has_airport"] == False]
    for i, row in road_city_df.iterrows():
        for j, row2 in road_city_df.iterrows():
            if i < j:
                road_route_df = get_rp_routes(road_city_df, row, type="road")
                road_dfs.append(road_route_df)
    road_df = pd.concat(road_dfs, ignore_index=True)
    road_df = road_df[[
        "type", "route_name", "origin", "destination",
        "time", "distance", "olat", "olon", "dlat", "dlon"
    ]]
    airplane_df = airplane_df[["type", "route_name", "origin", "destination",
                                 "time", "distance", "olat", "olon", "dlat", "dlon"]]
    airplane_df.to_csv("data/airplane_routes.csv", index=False)
    road_df.to_csv("data/road_routes.csv", index=False)


if __name__ == "__main__":
    generate_all_routes("data/cities.csv")

