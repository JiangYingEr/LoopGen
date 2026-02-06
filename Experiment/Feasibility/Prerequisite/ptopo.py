import itertools
from typing import Any, Dict, Iterable, List, Tuple
import networkx as nx
import os
import random

success_triple = set()

def extract_edges_from_file(file_path):

    edges_core = []  
    edges_full = []  
    is_edge_section = False  

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()  
                if not line:  
                    continue

                if line.startswith('EDGES'):
                    is_edge_section = True
                    continue

                if is_edge_section:
                    if line.startswith('label'):
                        continue
                    parts = line.split()
                    if len(parts) != 6:
                        continue
                    label, src, dest, weight, bw, delay = parts[0], parts[1], parts[2], parts[3], parts[4], parts[5]
                    try:
                        src_int = int(src)
                        dest_int = int(dest)
                        weight_int = int(weight)
                        bw_int = int(bw)
                        delay_int = int(delay)
                    except ValueError:
                        continue
                    edges_core.append((src_int, dest_int))
                    edges_full.append({
                        'label': label,
                        'src': src_int,
                        'dest': dest_int,
                        'weight': weight_int,
                        'bw': bw_int,
                        'delay': delay_int
                    })
        return edges_core

    except FileNotFoundError:
        return [], []
    except Exception as e:
        return [], []

def get_all_file_paths(folder_path):

    file_full_paths = []
    if not os.path.exists(folder_path):
        return file_full_paths
    if not os.path.isdir(folder_path):
        return file_full_paths
    
    for file_name in os.listdir(folder_path):
        full_path = os.path.join(folder_path, file_name)
        if os.path.isfile(full_path):
            abs_full_path = os.path.abspath(full_path)
            if "graph" in abs_full_path:
                file_full_paths.append(abs_full_path)
    return file_full_paths

def read_edges(file_path):
    edges = []
    with open(file_path, 'r') as file:
        s = 0
        number = 0
        for line in file.readlines()[1:]:  
            parts = line.strip().split()
            #print(parts)
            edge_label = parts[0]
            src = parts[1]
            dest = parts[2]
            weight = int(parts[3])
            bw = int(parts[4])
            delay = int(parts[5])
            number += 1
            s += delay/1000
            edges.append((src, dest)) 
    #print(s/number)
    return edges


def _edge_set_of_path(G: nx.Graph, path: List[Any]) -> frozenset:

    edges = []
    for u, v in zip(path[:-1], path[1:]):
        if G.is_directed():
            edges.append((u, v))
        else:
            edges.append((u, v) if u <= v else (v, u))
    return frozenset(edges)


def _all_shortest_edge_sets(G: nx.Graph, u: Any, v: Any, weight=None) -> List[frozenset]:
    try:
        paths = nx.all_shortest_paths(G, u, v, weight=weight)
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return []
    return [_edge_set_of_path(G, p) for p in paths]


def triple_success_exists_disjoint_shortest_paths(
    G: nx.Graph,
    triple: Tuple[Any, Any, Any],
    weight=None,
) -> bool:

    a, b, c = triple
    Eab = _all_shortest_edge_sets(G, a, b, weight=weight)
    if not Eab:
        return False
    Ebc = _all_shortest_edge_sets(G, b, c, weight=weight)
    if not Ebc:
        return False
    Eca = _all_shortest_edge_sets(G, c, a, weight=weight)
    if not Eca:
        return False


    for eab in Eab:
        # Candidate BC edgesets that don't overlap with AB
        bc_candidates = [ebc for ebc in Ebc if ebc.isdisjoint(eab)]
        if not bc_candidates:
            continue

        for ebc in bc_candidates:
            used = eab | ebc
            # Need a CA edgeset disjoint with both
            for eca in Eca:
                if eca.isdisjoint(used):
                    return True

    return False

def k_subset_contains_successful_triple(
    G: nx.Graph,
    nodes_k: Tuple[Any, ...],
    weight=None,
) -> bool:

    k = len(nodes_k)
    if k == 3:
        for triple in list(itertools.combinations(nodes_k, 3)):
            if triple_success_exists_disjoint_shortest_paths(G, triple, weight=weight):
                success_triple.add(triple)
                return True
        return False
    else:
        for triple in list(itertools.combinations(nodes_k, 3)):
            if triple in success_triple:
                return True
        return False


def success_rate_over_all_k_combinations(
    G: nx.Graph,
    k: int,
    weight=None,
) -> Dict[str, Any]:

    nodes = list(G.nodes())
    n = len(nodes)
    if k < 3:
        raise ValueError("k must be >= 3")
    if n < k:
        return {"k": k, "total": 0, "success": 0, "success_rate": 0.0}

    total = 0
    success = 0
    for nodes_k in list(itertools.combinations(nodes, k)):
        #print(nodes_k)
        total += 1
        if k_subset_contains_successful_triple(G, nodes_k, weight=weight):
            success += 1

    return {"k": k, "total": total, "success": success, "success_rate": success / total}


if __name__ == "__main__":
    paths = get_all_file_paths('topo')
    
    for path in paths:
        if True:
            success_triple.clear()
            edges = extract_edges_from_file(path)
            G = nx.Graph()
            G.add_edges_from(edges)
            
            res = success_rate_over_all_k_combinations(G,k=3)
            print(path)
            print(res)
            res = success_rate_over_all_k_combinations(G,k=4)
            print(res)
            res = success_rate_over_all_k_combinations(G,k=5)
            print(res)
            res = success_rate_over_all_k_combinations(G,k=6)
            print(res)
