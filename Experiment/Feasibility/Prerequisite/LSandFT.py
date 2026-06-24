import itertools
import math
import random
from collections import Counter, deque
from typing import Deque, Dict, FrozenSet, Iterable, List, Sequence, Set, Tuple


Graph = Dict[str, Set[str]]
SupportWays = Dict[int, List[int]]

# Hard-coded experiment configuration.
K_VALUES = [3, 4, 5, 6, 7, 8, 9, 10]
METHOD = "exact"  # "exact", "monte-carlo", or "auto"
MAX_EXACT_SWITCHES = 16
MONTE_CARLO_TRIALS = 20000
MONTE_CARLO_SEED = 2026

TOPOLOGY_CONFIGS = [
    {
        "topology": "leaf-spine",
        "num_leaf": 8,
        "num_spine": 4,
        "hosts_per_leaf": 20,
    },
    {
        "topology": "fat-tree",
        "fat_tree_k": 6,
        "hosts_per_edge": 20,
    },
]


def add_undirected_edge(graph: Graph, u: str, v: str) -> None:
    graph.setdefault(u, set()).add(v)
    graph.setdefault(v, set()).add(u)


def normalize_edge(u: str, v: str) -> Tuple[str, str]:
    return (u, v) if u <= v else (v, u)


def bfs_shortest_path_parents(graph: Graph, src: str) -> Tuple[Dict[str, int], Dict[str, List[str]]]:
    dist: Dict[str, int] = {src: 0}
    parents: Dict[str, List[str]] = {src: []}
    queue: Deque[str] = deque([src])

    while queue:
        node = queue.popleft()
        next_dist = dist[node] + 1
        for neighbor in sorted(graph.get(node, ())):
            if neighbor not in dist:
                dist[neighbor] = next_dist
                parents[neighbor] = [node]
                queue.append(neighbor)
            elif dist[neighbor] == next_dist:
                parents[neighbor].append(node)

    return dist, parents


def all_shortest_edge_sets(graph: Graph, src: str, dst: str) -> List[FrozenSet[Tuple[str, str]]]:
    if src == dst:
        return []

    dist, parents = bfs_shortest_path_parents(graph, src)
    if dst not in dist:
        return []

    result: Set[FrozenSet[Tuple[str, str]]] = set()

    def backtrack(node: str, reversed_path: List[str]) -> None:
        if node == src:
            path = list(reversed(reversed_path))
            edge_set = frozenset(
                normalize_edge(u, v) for u, v in zip(path[:-1], path[1:])
            )
            result.add(edge_set)
            return

        for parent in parents[node]:
            reversed_path.append(parent)
            backtrack(parent, reversed_path)
            reversed_path.pop()

    backtrack(dst, [dst])
    return list(result)


def triple_success_exists_disjoint_shortest_paths(
    graph: Graph,
    triple: Tuple[str, str, str],
) -> bool:
    a, b, c = triple
    if len({a, b, c}) < 3:
        return False

    edge_sets_ab = all_shortest_edge_sets(graph, a, b)
    edge_sets_bc = all_shortest_edge_sets(graph, b, c)
    edge_sets_ca = all_shortest_edge_sets(graph, c, a)
    if not edge_sets_ab or not edge_sets_bc or not edge_sets_ca:
        return False

    for ab in edge_sets_ab:
        for bc in edge_sets_bc:
            if not ab.isdisjoint(bc):
                continue
            used = ab | bc
            for ca in edge_sets_ca:
                if ca.isdisjoint(used):
                    return True
    return False


def build_leaf_spine(
    num_leaf: int,
    num_spine: int,
    hosts_per_leaf: int,
) -> Tuple[Graph, Dict[str, int]]:
    if num_leaf < 3:
        raise ValueError("leaf-spine requires at least 3 leaf switches")
    if num_spine < 1:
        raise ValueError("leaf-spine requires at least 1 spine switch")
    if hosts_per_leaf < 1:
        raise ValueError("hosts_per_leaf must be >= 1")

    graph: Graph = {}
    attachment_switches: Dict[str, int] = {}
    leaves = [f"leaf{i}" for i in range(num_leaf)]
    spines = [f"spine{i}" for i in range(num_spine)]

    for leaf in leaves:
        graph.setdefault(leaf, set())
        attachment_switches[leaf] = hosts_per_leaf
        for spine in spines:
            add_undirected_edge(graph, leaf, spine)

    return graph, attachment_switches


def build_fat_tree(
    pod_k: int,
    hosts_per_edge: int,
) -> Tuple[Graph, Dict[str, int]]:
    if pod_k < 4 or pod_k % 2 != 0:
        raise ValueError("fat-tree k must be an even integer >= 4")
    if hosts_per_edge < 1:
        raise ValueError("hosts_per_edge must be >= 1")

    half = pod_k // 2
    graph: Graph = {}
    attachment_switches: Dict[str, int] = {}

    core_switches = [[f"core{group}_{index}" for index in range(half)] for group in range(half)]

    for pod in range(pod_k):
        edge_switches = [f"edge{pod}_{index}" for index in range(half)]
        agg_switches = [f"agg{pod}_{index}" for index in range(half)]

        for edge in edge_switches:
            graph.setdefault(edge, set())
            attachment_switches[edge] = hosts_per_edge
            for agg in agg_switches:
                add_undirected_edge(graph, edge, agg)

        for agg_index, agg in enumerate(agg_switches):
            graph.setdefault(agg, set())
            for group in range(half):
                add_undirected_edge(graph, agg, core_switches[group][agg_index])

    return graph, attachment_switches


def find_successful_attachment_triples(
    switch_graph: Graph,
    attachment_switches: Iterable[str],
) -> List[Tuple[str, str, str]]:
    successful: List[Tuple[str, str, str]] = []
    for triple in itertools.combinations(sorted(attachment_switches), 3):
        if triple_success_exists_disjoint_shortest_paths(switch_graph, triple):
            successful.append(triple)
    return successful


def precompute_uniform_support_ways(
    num_switches: int,
    hosts_per_switch: int,
    max_k: int,
) -> SupportWays:
    choose = [math.comb(hosts_per_switch, taken) for taken in range(hosts_per_switch + 1)]
    ways: SupportWays = {0: [0] * (max_k + 1)}
    ways[0][0] = 1

    for support_size in range(1, num_switches + 1):
        previous = ways[support_size - 1]
        current = [0] * (max_k + 1)
        for used in range(max_k + 1):
            if previous[used] == 0:
                continue
            max_take = min(hosts_per_switch, max_k - used)
            for taken in range(1, max_take + 1):
                current[used + taken] += previous[used] * choose[taken]
        ways[support_size] = current

    return ways


def precompute_general_support_ways(
    hosts_per_switch: Sequence[int],
    max_k: int,
) -> SupportWays:
    ways_by_mask: SupportWays = {0: [0] * (max_k + 1)}
    ways_by_mask[0][0] = 1

    for mask in range(1, 1 << len(hosts_per_switch)):
        lsb = mask & -mask
        bit = lsb.bit_length() - 1
        previous_mask = mask ^ lsb
        previous = ways_by_mask[previous_mask]
        host_count = hosts_per_switch[bit]
        choose = [math.comb(host_count, taken) for taken in range(host_count + 1)]

        current = [0] * (max_k + 1)
        for used in range(max_k + 1):
            if previous[used] == 0:
                continue
            max_take = min(host_count, max_k - used)
            for taken in range(1, max_take + 1):
                current[used + taken] += previous[used] * choose[taken]
        ways_by_mask[mask] = current

    return ways_by_mask


def subset_contains_successful_triple(mask: int, triple_masks: Sequence[int]) -> bool:
    for triple_mask in triple_masks:
        if mask & triple_mask == triple_mask:
            return True
    return False


def analyze_exact_probabilities(
    attachment_host_counts: Dict[str, int],
    successful_triples: Sequence[Tuple[str, str, str]],
    k_values: Sequence[int],
) -> List[Dict[str, object]]:
    switch_names = sorted(attachment_host_counts)
    switch_to_bit = {switch: index for index, switch in enumerate(switch_names)}
    host_counts = [attachment_host_counts[switch] for switch in switch_names]
    total_hosts = sum(host_counts)
    max_k = max(k_values)
    triple_masks = [
        sum(1 << switch_to_bit[switch] for switch in triple)
        for triple in successful_triples
    ]

    uniform = len(set(host_counts)) == 1
    if uniform:
        support_ways = precompute_uniform_support_ways(
            num_switches=len(switch_names),
            hosts_per_switch=host_counts[0],
            max_k=max_k,
        )
    else:
        support_ways = precompute_general_support_ways(host_counts, max_k)

    success_by_k = Counter({k: 0 for k in k_values})
    mask_limit = 1 << len(switch_names)

    for mask in range(1, mask_limit):
        support_size = bin(mask).count("1")
        if support_size < 3:
            continue
        if not subset_contains_successful_triple(mask, triple_masks):
            continue

        ways = support_ways[support_size] if uniform else support_ways[mask]
        for k in k_values:
            success_by_k[k] += ways[k]

    results: List[Dict[str, object]] = []
    for k in k_values:
        total = math.comb(total_hosts, k) if 0 <= k <= total_hosts else 0
        success = success_by_k[k] if total else 0
        rate = (success / total) if total else 0.0
        results.append(
            {
                "k": k,
                "mode": "exact",
                "total": total,
                "success": success,
                "success_rate": rate,
            }
        )
    return results


def analyze_monte_carlo_probabilities(
    attachment_host_counts: Dict[str, int],
    successful_triples: Sequence[Tuple[str, str, str]],
    k_values: Sequence[int],
    trials: int,
    seed: int,
) -> List[Dict[str, object]]:
    switch_names = sorted(attachment_host_counts)
    switch_to_bit = {switch: index for index, switch in enumerate(switch_names)}
    triple_masks = [
        sum(1 << switch_to_bit[switch] for switch in triple)
        for triple in successful_triples
    ]

    host_pool: List[int] = []
    for switch in switch_names:
        bit = 1 << switch_to_bit[switch]
        host_pool.extend([bit] * attachment_host_counts[switch])

    rng = random.Random(seed)
    cached_success: Dict[int, bool] = {}
    results: List[Dict[str, object]] = []

    for k in k_values:
        if k > len(host_pool):
            results.append(
                {
                    "k": k,
                    "mode": f"monte-carlo({trials})",
                    "total": 0,
                    "success": 0,
                    "success_rate": 0.0,
                }
            )
            continue

        success = 0
        for _ in range(trials):
            chosen = rng.sample(range(len(host_pool)), k)
            mask = 0
            for index in chosen:
                mask |= host_pool[index]

            known = cached_success.get(mask)
            if known is None:
                known = subset_contains_successful_triple(mask, triple_masks)
                cached_success[mask] = known
            if known:
                success += 1

        results.append(
            {
                "k": k,
                "mode": f"monte-carlo({trials})",
                "total": trials,
                "success": success,
                "success_rate": success / trials if trials else 0.0,
            }
        )
    return results


def build_topology(config: Dict[str, int]) -> Tuple[str, Graph, Dict[str, int]]:
    topology_type = config["topology"]
    if topology_type == "leaf-spine":
        graph, attachment_switches = build_leaf_spine(
            num_leaf=config["num_leaf"],
            num_spine=config["num_spine"],
            hosts_per_leaf=config["hosts_per_leaf"],
        )
        description = (
            f"leaf-spine: leaves={config['num_leaf']}, spines={config['num_spine']}, "
            f"hosts_per_leaf={config['hosts_per_leaf']}"
        )
        return description, graph, attachment_switches

    graph, attachment_switches = build_fat_tree(
        pod_k=config["fat_tree_k"],
        hosts_per_edge=config["hosts_per_edge"],
    )
    description = f"fat-tree: k={config['fat_tree_k']}, hosts_per_edge={config['hosts_per_edge']}"
    return description, graph, attachment_switches


def print_report(
    description: str,
    switch_graph: Graph,
    attachment_host_counts: Dict[str, int],
    successful_triples: Sequence[Tuple[str, str, str]],
    results: Sequence[Dict[str, object]],
) -> None:
    total_hosts = sum(attachment_host_counts.values())
    print(description)
    print(f"switches={len(switch_graph)}, attachment_switches={len(attachment_host_counts)}, hosts={total_hosts}")
    print(
        "assumption=randomly selected hosts are mapped to their attachment switches; "
        "a k-host set succeeds if it contains at least one successful triple of attachment switches"
    )
    print(f"successful_attachment_triples={len(successful_triples)}")
    print("k\tmode\ttotal\tsuccess\tsuccess_rate")
    for item in results:
        print(
            f"{item['k']}\t{item['mode']}\t{item['total']}\t"
            f"{item['success']}\t{item['success_rate']:.8f}"
        )


def main() -> None:
    k_values = sorted(set(K_VALUES))
    if any(k < 3 for k in k_values):
        raise ValueError("all k values must be >= 3")

    if METHOD not in {"auto", "exact", "monte-carlo"}:
        raise ValueError("METHOD must be one of: auto, exact, monte-carlo")

    for config in TOPOLOGY_CONFIGS:
        description, switch_graph, attachment_host_counts = build_topology(config)
        successful_triples = find_successful_attachment_triples(
            switch_graph,
            attachment_host_counts.keys(),
        )

        if METHOD == "exact":
            results = analyze_exact_probabilities(attachment_host_counts, successful_triples, k_values)
        elif METHOD == "monte-carlo":
            results = analyze_monte_carlo_probabilities(
                attachment_host_counts,
                successful_triples,
                k_values,
                trials=MONTE_CARLO_TRIALS,
                seed=MONTE_CARLO_SEED,
            )
        else:
            if len(attachment_host_counts) <= MAX_EXACT_SWITCHES:
                results = analyze_exact_probabilities(attachment_host_counts, successful_triples, k_values)
            else:
                results = analyze_monte_carlo_probabilities(
                    attachment_host_counts,
                    successful_triples,
                    k_values,
                    trials=MONTE_CARLO_TRIALS,
                    seed=MONTE_CARLO_SEED,
                )

        print_report(
            description=description,
            switch_graph=switch_graph,
            attachment_host_counts=attachment_host_counts,
            successful_triples=successful_triples,
            results=results,
        )
        print()


if __name__ == "__main__":
    main()
