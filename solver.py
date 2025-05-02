import networkx as nx
import gurobipy as gp
from gurobipy import GRB
import pandas as pd

import requests

# Cost and emission factors per ton-kilometer for each transport mode
COST_PER_TKM = {
    'road': 0.04,      # $ per t·km
    'train': 0.02,
    'boat': 0.01,
    'airplane': 1.0
}
EMISSION_PER_TKM = {
    'road': 100,       # g CO₂ per t·km
    'train': 30,
    'boat': 10,
    'airplane': 600
}

def get_road_distance_and_time(coords1, coords2):
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


cities = pd.read_csv("data/cities.csv").to_dict(orient="records")


def build_city_graph(cities):
    G = nx.DiGraph()
    city_nodes = {}

    for city in cities:
        city_name = city["name"]
        nodes = {}
        nodes["storage"] = f"{city_name}_storage"
        nodes["road"] = f"{city_name}_road"
        nodes["train"] = f"{city_name}_train"
        G.add_node(nodes["storage"], city=city_name, type="storage")
        G.add_node(nodes["road"], city=city_name, type="road")
        G.add_node(nodes["train"], city=city_name, type="train")
        if city.get("has_airport"):
            nodes["airplane"] = f"{city_name}_airplane"
            G.add_node(nodes["airplane"], city=city_name, type="airplane")
        if city.get("has_port"):
            nodes["boat"] = f"{city_name}_boat"
            G.add_node(nodes["boat"], city=city_name, type="boat")
        city_nodes[city_name] = nodes

        # Add edges between all nodes of this city (clique)
        node_list = list(nodes.values())
        for i in range(len(node_list)):
            for j in range(i + 1, len(node_list)):
                G.add_edge(node_list[i], node_list[j], cost=(0, 0, 0))
                G.add_edge(node_list[j], node_list[i], cost=(0, 0, 0))

    # Add edges between nodes of the same type in different cities (except storage)
    types = ["road", "train", "airplane", "boat"]
    for t in types:
        nodes_of_type = [nodes[t] for nodes in city_nodes.values() if t in nodes]
        for i in range(len(nodes_of_type)):
            for j in range(i + 1, len(nodes_of_type)):
                G.add_edge(nodes_of_type[i], nodes_of_type[j], cost=(0, 0, 0))
                G.add_edge(nodes_of_type[j], nodes_of_type[i], cost=(0, 0, 0))

    return G

def build_edge_database(cities):
    city_nodes = {}

    # Création des nœuds par ville
    for city in cities:
        city_name = city["name"]
        nodes = {}
        nodes["storage"] = f"{city_name}_storage"
        nodes["road"] = f"{city_name}_road"
        nodes["train"] = f"{city_name}_train"
        if city.get("has_airport"):
            nodes["airplane"] = f"{city_name}_airplane"
        if city.get("has_port"):
            nodes["boat"] = f"{city_name}_boat"
        city_nodes[city_name] = nodes

    edge_db = []

    # Arêtes internes à la ville (clique)
    for nodes in city_nodes.values():
        node_list = list(nodes.values())
        for i in range(len(node_list)):
            for j in range(i + 1, len(node_list)):
                edge_db.append({
                    "from_node": node_list[i],
                    "to_node": node_list[j],
                    "cost": (0, 0, 0)
                })

    # Arêtes entre villes de même type (hors storage)
    types = ["road", "train", "airplane", "boat"]
    for t in types:
        nodes_of_type = [nodes[t] for nodes in city_nodes.values() if t in nodes]
        for i in range(len(nodes_of_type)):
            for j in range(i + 1, len(nodes_of_type)):
                edge_db.append({
                    "from_node": nodes_of_type[i],
                    "to_node": nodes_of_type[j],
                    "cost": (0, 0, 0)
                })

    return edge_db


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
    city_graph = build_city_graph(cities)
    source_node = list(city_graph.nodes())[0]
    target_node = list(city_graph.nodes())[-1]
    path, cost = solve_shortest_path(city_graph, source_node, target_node, alpha=0.5, beta=0.3, gamma=0.2)
    print(f"Optimal path from {source_node} to {target_node}: {path}")
    print(f"Weighted cost: {cost}")

    print(f"Total nodes: {city_graph.number_of_nodes()}")
    print("Sample nodes:", list(city_graph.nodes)[:10])

    # Exemple d'utilisation
    edge_database = build_edge_database(cities)
    print(f"Nombre d'arêtes: {len(edge_database)}")
    print("Exemple d'arêtes:", edge_database[:5])
