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
TRANSITION_COST = 0.2

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

    # Add edges between nodes of the same type in different cities (except storage)
    for edge in routes:
        type = edge["type"]
        origin = edge["origin"]
        destination = edge["destination"]
        
        # Skip if either city doesn't have the required transport mode
        if type not in city_nodes[origin] or type not in city_nodes[destination]:
            continue
            
        from_node = city_nodes[origin][type]
        to_node = city_nodes[destination][type]
        G.add_edge(from_node, to_node, cost=(edge["time"], edge["price"], edge["CO2"]))

    return G


# -------------------- Gurobi Shortest Path Solver --------------------
def solve_shortest_path(graph, source, target, alpha, beta, gamma):
    """
    Solve the shortest path problem with multi-dimensional edge costs using Gurobi.
    :param graph: networkx Graph with edge attribute 'cost' as a tuple (t, c, co2)
    :param source: source node name
    :param target: target node name
    :param alpha: weight for time cost
    :param beta: weight for monetary cost
    :param gamma: weight for carbon cost
    :return: (path list of nodes, total_cost, time_cost, cost_cost, emissions_cost)
    """

    # Initialize model
    model = gp.Model("multi_objective_shortest_path")
    model.setParam('OutputFlag', 0)

    # Renormalize the costs
    sum_preferences = alpha + beta + gamma
    alpha = alpha / sum_preferences
    beta = beta / sum_preferences
    gamma = gamma / sum_preferences

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

    # Objective: minimize weighted sum of costs
    time_cost = gp.quicksum(x[(u, v)] * data['cost'][0] for u, v, data in graph.edges(data=True) if (u, v) in x)
    cost_cost = gp.quicksum(x[(u, v)] * data['cost'][1] for u, v, data in graph.edges(data=True) if (u, v) in x)
    emissions_cost = gp.quicksum(x[(u, v)] * data['cost'][2] for u, v, data in graph.edges(data=True) if (u, v) in x)
    
    total_cost = alpha * time_cost + beta * cost_cost + gamma * emissions_cost
    model.setObjective(total_cost, GRB.MINIMIZE)

    # Solve the model
    model.optimize()

    if model.status == GRB.OPTIMAL:
        # Extract the path using networkx
        selected_edges = [(u, v) for (u, v), var in x.items() if var.X > 0.5]
        subgraph = nx.DiGraph()
        subgraph.add_edges_from(selected_edges)
        
        try:
            path = nx.shortest_path(subgraph, source=source, target=target)
        except nx.NetworkXNoPath:
            raise Exception("No path found between source and target")

        # Get the actual values of the costs
        time_value = time_cost.getValue()
        cost_value = cost_cost.getValue()
        emissions_value = emissions_cost.getValue()
        total_value = total_cost.getValue()

        return path, total_value, time_value, cost_value, emissions_value
    else:
        raise Exception(f"No optimal solution found. Model status: {model.status}")

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
    cities_df = pd.read_csv("data/cities.csv")
    routes_df = pd.read_csv("data/routes_clean.csv")
    start = "Vancouver"
    end = "Boston"
    from src.data_preprocess.add_city import add_city
    cities_df, routes_df = add_city(cities_df, routes_df, start, has_airport=False)
    cities_df, routes_df = add_city(cities_df, routes_df, end, has_airport=False)

    graph = build_city_graph(cities_df.to_dict(orient="records"), routes_df.to_dict(orient="records"))
    source_node = get_node(start)
    target_node = get_node(end)
    

    alpha = 1
    beta = 1
    gamma = 1
    path, total_cost, time_cost, cost_cost, emissions_cost = solve_shortest_path(graph, source_node, target_node, alpha, beta, gamma)
    print(f"Path: {path}")

