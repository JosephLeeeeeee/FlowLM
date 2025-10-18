# -*- coding: utf-8 -*-
"""
Brute-force algorithm to find the optimal path that minimizes MLU

MLU (Maximum Link Utilization) = max(utilization of all edges)
Edge utilization = (initial weight + allocated bandwidth) / total capacity (10)

Algorithm:
1. Use DFS to enumerate all simple paths from source to target
2. For each path, calculate the MLU after allocating bandwidth
3. Return the path with minimum MLU
"""

import networkx as nx
import re
from generate_solution import APIClient


class OptimalSolver:
    def __init__(self, graph, total_capacity=10):
        """
        Initialize the optimal solver

        Args:
            graph: NetworkX graph object
            total_capacity: Total capacity of each edge, default is 10
        """
        self.graph = graph
        self.total_capacity = total_capacity

    def find_all_simple_paths_dfs(self, source, target, max_path_length=None):
        """
        Use DFS to enumerate all simple paths from source to target

        Args:
            source: Source node
            target: Target node
            max_path_length: Maximum path length limit, None means no limit

        Returns:
            List of all simple paths
        """
        all_paths = []

        def dfs(current, target, visited, path):
            if current == target:
                all_paths.append(path.copy())
                return

            # If max path length is set, check if exceeded
            if max_path_length and len(path) >= max_path_length:
                return

            visited.add(current)

            for neighbor in self.graph.neighbors(current):
                if neighbor not in visited:
                    path.append(neighbor)
                    dfs(neighbor, target, visited, path)
                    path.pop()

            visited.remove(current)

        visited = set()
        dfs(source, target, visited, [source])

        return all_paths

    def calculate_mlu_for_path(self, path, bandwidth):
        """
        Calculate MLU for a given path after allocating bandwidth

        Args:
            path: Node path list
            bandwidth: Bandwidth to allocate

        Returns:
            MLU value
        """
        max_utilization = 0

        # Iterate through all edges in the graph to calculate utilization
        for u, v, data in self.graph.edges(data=True):
            current_weight = data.get('weight', 0)

            # Check if this edge is on the path
            edge_on_path = False
            for i in range(len(path) - 1):
                # For undirected graph, check both directions
                if (path[i] == u and path[i + 1] == v) or (path[i] == v and path[i + 1] == u):
                    edge_on_path = True
                    break

            # If edge is on path, add bandwidth
            if edge_on_path:
                new_weight = current_weight + bandwidth
            else:
                new_weight = current_weight

            # Calculate utilization
            utilization = new_weight / self.total_capacity
            max_utilization = max(max_utilization, utilization)

        return max_utilization

    def find_optimal_path(self, source, target, bandwidth, max_path_length=None):
        """
        Brute-force search for the path that minimizes MLU

        Args:
            source: Source node
            target: Target node
            bandwidth: Bandwidth to allocate
            max_path_length: Maximum path length limit, None means no limit

        Returns:
            (optimal path, corresponding MLU, detailed info of all paths)
        """
        # Enumerate all simple paths
        all_paths = self.find_all_simple_paths_dfs(source, target, max_path_length)

        if not all_paths:
            return None, float('inf'), []

        print(f"Found {len(all_paths)} simple paths from node {source} to node {target}")

        # Calculate MLU for each path
        path_mlu_list = []
        for path in all_paths:
            mlu = self.calculate_mlu_for_path(path, bandwidth)
            path_mlu_list.append((path, mlu))

        # Sort by MLU
        path_mlu_list.sort(key=lambda x: x[1])

        # Return optimal path
        optimal_path, optimal_mlu = path_mlu_list[0]

        return optimal_path, optimal_mlu, path_mlu_list


def main():
    """
    Main function: Read flow requirements and graph from config, solve for optimal path
    """
    # Read configuration
    client = APIClient()
    flow = client.flow_description
    print("=" * 60)
    print("Flow requirement:", flow)

    # Extract source, target, and bandwidth
    start_node = re.search(r'初始点：(\d+)', flow).group(1)
    end_node = re.search(r'终点：(\d+)', flow).group(1)
    bandwidth = int(re.search(r'数据流待分配带宽：(\d+)', flow).group(1))

    print(f"Source: {start_node}, Target: {end_node}, Bandwidth: {bandwidth}")
    print("=" * 60)

    # Read graph
    file_path = "dataset/generated/W20N_20250924_144247.gml"
    graph = nx.read_gml(file_path)

    # Create solver
    solver = OptimalSolver(graph)

    # Solve for optimal path
    # Note: For large graphs, set max_path_length to limit search space
    # Example: max_path_length=10 means only search paths with length <= 10
    print("\nStarting brute-force search for optimal path...")
    optimal_path, optimal_mlu, all_paths_info = solver.find_optimal_path(
        start_node,
        end_node,
        bandwidth,
        max_path_length=10  # Limit max path length to avoid long search time
    )

    if optimal_path is None:
        print("No feasible path found!")
        return

    print("\n" + "=" * 60)
    print("Optimal path (minimizing MLU):")
    print(f"Path: {' -> '.join(map(str, optimal_path))}")
    print(f"Path length: {len(optimal_path) - 1} hops")
    print(f"MLU: {optimal_mlu:.3f}")
    print("=" * 60)

    # Display top 10 optimal paths
    print("\nTop 10 optimal paths:")
    for i, (path, mlu) in enumerate(all_paths_info[:10], 1):
        path_str = ' -> '.join(map(str, path))
        print(f"{i}. MLU={mlu:.3f}, Path: {path_str}")

    # Display detailed edge information for optimal path
    print("\n" + "=" * 60)
    print("Edge usage on optimal path:")
    for i in range(len(optimal_path) - 1):
        u = optimal_path[i]
        v = optimal_path[i + 1]
        current_weight = graph.edges[u, v]['weight']
        new_weight = current_weight + bandwidth
        utilization = new_weight / 10
        print(f"Edge ({u}, {v}): {current_weight} -> {new_weight}, Utilization: {utilization:.3f}")

    # Find edges that determine the MLU (bottleneck edges)
    print("\nBottleneck edges (determining MLU):")
    for u, v, data in graph.edges(data=True):
        current_weight = data.get('weight', 0)
        edge_on_path = False
        for i in range(len(optimal_path) - 1):
            if (optimal_path[i] == u and optimal_path[i + 1] == v) or \
                    (optimal_path[i] == v and optimal_path[i + 1] == u):
                edge_on_path = True
                break

        if edge_on_path:
            new_weight = current_weight + bandwidth
        else:
            new_weight = current_weight

        utilization = new_weight / 10
        if abs(utilization - optimal_mlu) < 0.001:  # Floating point comparison
            print(f"Edge ({u}, {v}): Weight={new_weight}, Utilization={utilization:.3f}")


if __name__ == "__main__":
    main()
