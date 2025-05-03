import networkx as nx
import gurobipy as gp
from gurobipy import GRB
import pandas as pd

import requests

## TIME, COST, EMISSIONS

# Cost and emission factors per ton-kilometer for each transport mode
COST_PER_TKM = {
    'road': 0.04,      # $ per t·km
    'train': 0.02,
    'ship': 0.01,
    'airplane': 1.0
}
EMISSION_PER_TKM = {
    'road': 100,       # g CO₂ per t·km
    'train': 30,
    'ship': 10,
    'airplane': 600
}

TRANSITION_TIME_HR = 0.5
TRANSITION_COST = 0

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


import math

# Paramètres à ajuster
AVG_PLANE_SPEED_KMH = 800     # km/h en croisière
OVERHEAD_TIME_H    = 1.0      # h total (embarquement + débarquement)

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


cities = pd.read_csv("data/cities.csv").to_dict(orient="records")
routes = pd.read_csv("data/routes.csv").to_dict(orient="records")


def build_city_graph(cities,routes):
    G = nx.DiGraph()
    city_nodes = {}

    for city in cities:
        city_name = city["name"]
        nodes = {}
        
        nodes["road"] = f"{city_name}_road"
        nodes["train"] = f"{city_name}_train"
        G.add_node(nodes["road"], city=city_name, type="road")
        G.add_node(nodes["train"], city=city_name, type="train")
        if city.get("has_airport"):
            nodes["airplane"] = f"{city_name}_airplane"
            G.add_node(nodes["airplane"], city=city_name, type="airplane")
        if city.get("has_port"):
            nodes["ship"] = f"{city_name}_ship"
            G.add_node(nodes["ship"], city=city_name, type="ship")
        city_nodes[city_name] = nodes

        # Add edges between all nodes of this city (clique)
        node_list = list(nodes.values())
        for i in range(len(node_list)):
            for j in range(i + 1, len(node_list)):
                G.add_edge(node_list[i], node_list[j], cost=(TRANSITION_TIME_HR, TRANSITION_COST, 0))
                G.add_edge(node_list[j], node_list[i], cost=(TRANSITION_TIME_HR,TRANSITION_COST, 0))
        nodes["storage"] = f"{city_name}_storage"
        G.add_node(nodes["storage"], city=city_name, type="storage")
        # Add edges between storage and other nodes in the city
        for node in node_list:
            G.add_edge(nodes["storage"], node, cost=(0, 0, 0))
            G.add_edge(node, nodes["storage"], cost=(0, 0, 0))

    # Add edges between nodes of the same type in different cities (except storage)7
    for edge in routes:
        type = edge["type"]
        origin = edge["origin"]
        destination = edge["destination"]
        from_node = city_nodes[origin][type]
        to_node = city_nodes[destination][type]
        G.add_edge(from_node, to_node, cost=(edge["time"], edge["price"], edge["CO2"]))

    return G

# def build_edge_database(cities):
#     city_nodes = {}

#     # Création des nœuds par ville
#     for city in cities:
#         city_name = city["name"]
#         nodes = {}
#         nodes["storage"] = f"{city_name}_storage"
#         nodes["road"] = f"{city_name}_road"
#         nodes["train"] = f"{city_name}_train"
#         if city.get("has_airport"):
#             nodes["airplane"] = f"{city_name}_airplane"
#         if city.get("has_port"):
#             nodes["ship"] = f"{city_name}_ship"
#         city_nodes[city_name] = nodes

#     edge_db = []

#     # Arêtes internes à la ville (clique)
#     for nodes in city_nodes.values():
#         node_list = list(nodes.values())
#         for i in range(len(node_list)):
#             for j in range(i + 1, len(node_list)):
#                 edge_db.append({
#                     "from_node": node_list[i],
#                     "to_node": node_list[j],
#                     "cost": (0, 0, 0)
#                 })

#     # Arêtes entre villes de même type (hors storage)
#     types = ["road", "train", "airplane", "ship"]
#     for t in types:
#         nodes_of_type = [nodes[t] for nodes in city_nodes.values() if t in nodes]
#         for i in range(len(nodes_of_type)):
#             for j in range(i + 1, len(nodes_of_type)):
#                 edge_db.append({
#                     "from_node": nodes_of_type[i],
#                     "to_node": nodes_of_type[j],
#                     "cost": (0, 0, 0)
#                 })

#     return edge_db


# -------------------- Gurobi Shortest Path Solver --------------------
def solve_shortest_path(graph, source, target, alpha=1.0, beta=1.0, gamma=1.0):
    """
    Solve the shortest path problem with multi-dimensional edge costs using Gurobi.
    :param graph: networkx Graph with edge attribute 'cost' as a tuple (t, c, co2)
    :param source: source node name
    :param target: target node name
    :param alpha: weight for time cost
    :param beta: weight for monetary cost
    :param gamma: weight for carbon cost
    :return: (path list of nodes, objective value)
    """

    # Scaling the costs so that the three components are on the same order of magnitude
    # We use the means computed on the routes dataset
    mean_time = 18
    mean_cost = 148
    mean_emissions = 234

    alpha = alpha / mean_time
    beta = beta / mean_cost
    gamma = gamma / mean_emissions

    # Initialize model
    model = gp.Model("multi_objective_shortest_path")
    model.setParam('OutputFlag', 0)

    # Decision variables: x_e = 1 if edge e=(u,v) is in the path
    x = {}
    for u, v, data in graph.edges(data=True):
        x[(u, v)] = model.addVar(vtype=GRB.BINARY, name=f"x_{u}_{v}")

    # Flow conservation constraints
    for node in graph.nodes():
        inflow = gp.quicksum(x[(u, v)] for u, v in graph.in_edges(node) if (u, v) in x)
        outflow = gp.quicksum(x[(u, v)] for u, v in graph.out_edges(node) if (u, v) in x)
        if node == source:
            model.addConstr(outflow - inflow == 1, name=f"flow_{node}")
        elif node == target:
            model.addConstr(outflow - inflow == -1, name=f"flow_{node}")
        else:
            model.addConstr(outflow - inflow == 0, name=f"flow_{node}")
    # No storage node unless it is the source or target
    for node in graph.nodes():
        if graph.nodes[node].get("type") == "storage" and node not in [source, target]:
            model.addConstr(gp.quicksum(x[(u, v)] for u, v in graph.out_edges(node) if (u, v) in x) == 0, name=f"no_storage_{node}")

    # Objective: weighted sum of the three cost components
    objective = gp.quicksum(
        (alpha * data['cost'][0] + beta * data['cost'][1] + gamma * data['cost'][2]) * x[(u, v)]
        for u, v, data in graph.edges(data=True)
    )
    model.setObjective(objective, GRB.MINIMIZE)

    # Optimize
    model.optimize()

    # Extract selected edges and reconstruct path
    selected = [(u, v) for (u, v), var in x.items() if var.X > 0.5]
    subgraph = nx.DiGraph()
    subgraph.add_edges_from(selected)
    try:
        path = nx.shortest_path(subgraph, source=source, target=target)
    except nx.NetworkXNoPath:
        path = selected
    return path, model.ObjVal

def get_node(city_name):
    """
    Get the node name for a city.
    :param city_name: Name of the city
    :return: Node name
    """
    return f"{city_name}_storage"  # Assuming we want the road node


def test_road_distance():
    # New York coordinates (approximate)
    ny_coords = (40.7128, -74.0060)
    # Boston coordinates (approximate)
    boston_coords = (42.3601, -71.0589)
    
    distance, time = get_road_distance_and_time(ny_coords, boston_coords)
    print(f"Road distance between New York and Boston: {distance:.2f} km")
    print(f"Estimated travel time: {time:.2f} hours")


if __name__ == "__main__":
    test_road_distance()
    city_graph = build_city_graph(cities, routes)
    source_node = get_node("New York")  # Example source node
    target_node = get_node("Boston")  # Example target node
    path, cost = solve_shortest_path(city_graph, source_node, target_node, alpha=10, beta=0.3, gamma=0.2)
    print(f"Optimal path from {source_node} to {target_node}: {path}")
    print(f"Weighted cost: {cost}")

    print(f"Total nodes: {city_graph.number_of_nodes()}")
    print("Sample nodes:", list(city_graph.nodes)[:10])

    # Exemple d'utilisation
    # # edge_database = build_edge_database(cities)
    # print(f"Nombre d'arêtes: {len(edge_database)}")
    # print("Exemple d'arêtes:", edge_database[:5])
    # print(build_city_graph(cities,routes).nodes(data=True))
