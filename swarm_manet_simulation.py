
import networkx as nx
import matplotlib.pyplot as plt
import random

# Parameters
num_nodes = 10
failure_threshold = 20
rounds = 5

def find_best_path(graph, start, end):
    try:
        paths = list(nx.all_simple_paths(graph, start, end, cutoff=4))
    except nx.NetworkXNoPath:
        return None, float('inf')
    if not paths:
        return None, float('inf')
    best_path, best_score = None, float('inf')
    for path in paths:
        total_weight = sum(graph[path[i]][path[i+1]]['weight'] for i in range(len(path)-1))
        min_energy = min(graph.nodes[n]['energy'] for n in path)
        score = total_weight / min_energy
        if score < best_score:
            best_path, best_score = path, score
    return best_path, best_score

def decay_energy(graph, path, energy_cost_per_unit=1):
    if not path: return
    for i in range(len(path)-1):
        u, v = path[i], path[i+1]
        distance = graph[u][v]['weight']
        cost = distance * energy_cost_per_unit
        graph.nodes[u]['energy'] = max(0, graph.nodes[u]['energy'] - cost)
        graph.nodes[v]['energy'] = max(0, graph.nodes[v]['energy'] - cost)

def prune_dead_nodes(graph, threshold):
    dead = [n for n, attr in graph.nodes(data=True) if attr['energy'] < threshold]
    graph.remove_nodes_from(dead)
    return dead

def simulate_mobility(graph, conn_prob=0.5, max_dist=10):
    graph.clear_edges()
    nodes = list(graph.nodes)
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            if random.random() < conn_prob:
                dist = random.randint(1, max_dist)
                graph.add_edge(nodes[i], nodes[j], weight=dist)

# Initialize
G = nx.Graph()
for i in range(num_nodes):
    G.add_node(i, energy=random.randint(50, 100))

history = []

for r in range(1, rounds + 1):
    simulate_mobility(G)
    dead_nodes = prune_dead_nodes(G, failure_threshold)
    if 0 not in G.nodes or 9 not in G.nodes:
        history.append((r, dead_nodes, None, None, None, None, "Source or destination removed"))
        break
    path, score = find_best_path(G, 0, 9)
    if not path:
        history.append((r, dead_nodes, None, None, None, None, "No path found"))
        continue
    total_dist = sum(G[path[i]][path[i+1]]['weight'] for i in range(len(path)-1))
    min_energy = min(G.nodes[n]['energy'] for n in path)
    history.append((r, dead_nodes, path, total_dist, min_energy, score, "Path found"))
    decay_energy(G, path)

# Output results
for h in history:
    print(f"Round {h[0]} | Dead: {h[1]} | Path: {h[2]} | Dist: {h[3]} | MinE: {h[4]} | Score: {h[5]:.3f} | Status: {h[6]}")
