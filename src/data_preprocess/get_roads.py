import pandas as pd
import math

AVG_PLANE_SPEED_KMH = 800     # km/h en croisière
OVERHEAD_TIME_H    = 1.0      # h total (embarquement + débarquement)


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
