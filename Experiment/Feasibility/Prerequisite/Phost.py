import itertools
import math
import os
from typing import Any, Dict, FrozenSet, List, Sequence, Set, Tuple

import networkx as nx


successful_triples: Set[Tuple[Any, Any, Any]] = set()

# Hard-coded experiment configuration.
TOPO_DIR = r"./topo"
HOSTS_PER_NODE = 20
K_VALUES = [3, 4, 5, 6]
PRINT_NODE_STATS = False


def extract_edges_from_file(file_path: str) -> List[Tuple[int, int]]:
    edges: List[Tuple[int, int]] = []
    is_edge_section = False

    try:
        with open(file_path, "r", encoding="utf-8") as handle:
            for raw_line in handle:
                line = raw_line.strip()
                if not line:
                    continue

                if line.startswith("EDGES"):
                    is_edge_section = True
                    continue

                if not is_edge_section or line.startswith("label"):
                    continue

                parts = line.split()
                if len(parts) != 6:
                    continue

                _, src, dest, weight, bw, delay = parts
                try:
                    src_int = int(src)
                    dest_int = int(dest)
                    int(weight)
                    int(bw)
                    int(delay)
                except ValueError:
                    continue

                edges.append((src_int, dest_int))
    except FileNotFoundError:
        return []
    except OSError:
        return []

    return edges


def get_all_file_paths(folder_path: str) -> List[str]:
    if not os.path.isdir(folder_path):
        return []

    file_full_paths: List[str] = []
    for file_name in sorted(os.listdir(folder_path)):
        full_path = os.path.join(folder_path, file_name)
        if os.path.isfile(full_path) and full_path.endswith(".graph"):
            file_full_paths.append(os.path.abspath(full_path))
    return file_full_paths


def _edge_set_of_path(G: nx.Graph, path: Sequence[Any]) -> FrozenSet[Tuple[Any, Any]]:
    edges = []
    for u, v in zip(path[:-1], path[1:]):
        if G.is_directed():
            edges.append((u, v))
        else:
            edges.append((u, v) if u <= v else (v, u))
    return frozenset(edges)


def _all_shortest_edge_sets(
    G: nx.Graph,
    u: Any,
    v: Any,
    weight=None,
) -> List[FrozenSet[Tuple[Any, Any]]]:
    try:
        paths = nx.all_shortest_paths(G, u, v, weight=weight)
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return []
    return [_edge_set_of_path(G, path) for path in paths]


def triple_success_exists_disjoint_shortest_paths(
    G: nx.Graph,
    triple: Tuple[Any, Any, Any],
    weight=None,
) -> bool:
    a, b, c = triple
    edge_sets_ab = _all_shortest_edge_sets(G, a, b, weight=weight)
    edge_sets_bc = _all_shortest_edge_sets(G, b, c, weight=weight)
    edge_sets_ca = _all_shortest_edge_sets(G, c, a, weight=weight)

    if not edge_sets_ab or not edge_sets_bc or not edge_sets_ca:
        return False

    for edges_ab in edge_sets_ab:
        for edges_bc in edge_sets_bc:
            if not edges_ab.isdisjoint(edges_bc):
                continue
            used_edges = edges_ab | edges_bc
            for edges_ca in edge_sets_ca:
                if edges_ca.isdisjoint(used_edges):
                    return True

    return False


def k_subset_contains_successful_triple(
    G: nx.Graph,
    nodes_k: Tuple[Any, ...],
    weight=None,
) -> bool:
    if len(nodes_k) == 3:
        triple = tuple(sorted(nodes_k))
        if triple_success_exists_disjoint_shortest_paths(G, triple, weight=weight):
            successful_triples.add(triple)
            return True
        return False

    for triple in itertools.combinations(nodes_k, 3):
        if tuple(sorted(triple)) in successful_triples:
            return True
    return False


def node_success_stats_over_all_k_combinations(
    G: nx.Graph,
    k: int,
    weight=None,
) -> Dict[str, Any]:
    nodes = list(G.nodes())
    node_count = len(nodes)
    if k < 3:
        raise ValueError("k must be >= 3")
    if node_count < k:
        return {"k": k, "total": 0, "success": 0, "success_rate": 0.0}

    total = 0
    success = 0
    for nodes_k in itertools.combinations(nodes, k):
        total += 1
        if k_subset_contains_successful_triple(G, nodes_k, weight=weight):
            success += 1

    return {"k": k, "total": total, "success": success, "success_rate": success / total}


def precompute_uniform_support_ways(
    max_support_size: int,
    hosts_per_node: int,
    max_k: int,
) -> Dict[int, List[int]]:
    choose = [math.comb(hosts_per_node, taken) for taken in range(hosts_per_node + 1)]
    ways: Dict[int, List[int]] = {0: [0] * (max_k + 1)}
    ways[0][0] = 1

    for support_size in range(1, max_support_size + 1):
        previous = ways[support_size - 1]
        current = [0] * (max_k + 1)
        for used in range(max_k + 1):
            if previous[used] == 0:
                continue
            max_take = min(hosts_per_node, max_k - used)
            for taken in range(1, max_take + 1):
                current[used + taken] += previous[used] * choose[taken]
        ways[support_size] = current

    return ways


def host_success_stats_from_node_success_counts(
    node_count: int,
    hosts_per_node: int,
    node_success_counts: Dict[int, int],
    support_ways: Dict[int, List[int]],
    k: int,
) -> Dict[str, Any]:
    total_hosts = node_count * hosts_per_node
    if k > total_hosts:
        return {"k": k, "total": 0, "success": 0, "success_rate": 0.0}

    total = math.comb(total_hosts, k)
    success = 0
    max_support_size = min(k, node_count)
    for support_size in range(3, max_support_size + 1):
        success += node_success_counts.get(support_size, 0) * support_ways[support_size][k]

    return {"k": k, "total": total, "success": success, "success_rate": success / total}


def main() -> None:
    k_values = sorted(set(K_VALUES))
    if not k_values:
        raise ValueError("at least one k value is required")
    if any(k < 3 for k in k_values):
        raise ValueError("all k values must be >= 3")
    if HOSTS_PER_NODE < 1:
        raise ValueError("hosts_per_node must be >= 1")

    paths = get_all_file_paths(TOPO_DIR)
    print(paths)
    max_k = max(k_values)

    for path in paths:
        successful_triples.clear()
        edges = extract_edges_from_file(path)
        graph = nx.Graph()
        graph.add_edges_from(edges)

        node_count = graph.number_of_nodes()
        max_support_size = min(max_k, node_count)
        node_success_counts: Dict[int, int] = {}

        for support_size in range(3, max_support_size + 1):
            node_result = node_success_stats_over_all_k_combinations(graph, k=support_size)
            node_success_counts[support_size] = node_result["success"]
            if PRINT_NODE_STATS:
                print(path)
                print({"mode": "node", **node_result})

        support_ways = precompute_uniform_support_ways(
            max_support_size=max_support_size,
            hosts_per_node=HOSTS_PER_NODE,
            max_k=max_k,
        )

        print(path)
        print(
            f"assumption: each topology node attaches {HOSTS_PER_NODE} hosts; "
            "k now counts hosts instead of topology nodes"
        )
        for k in k_values:
            result = host_success_stats_from_node_success_counts(
                node_count=node_count,
                hosts_per_node=HOSTS_PER_NODE,
                node_success_counts=node_success_counts,
                support_ways=support_ways,
                k=k,
            )
            print(result)


if __name__ == "__main__":
    main()
