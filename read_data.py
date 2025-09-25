"""Network topology visualization and analysis module.

This module provides functionality for reading GML graph files, 
visualizing network topologies, and performing basic graph analysis.

Functions:
    read_gml_files: Read and load GML files from a directory
    visualize_topology: Generate network topology visualizations
    analyze_topology: Perform basic topology analysis
    main: Main execution function
"""

import networkx as nx
import matplotlib.pyplot as plt
import os
import glob


def read_gml_files(dataset_path="dataset", gml_file="*.gml"):
    """
    Read all GML files from the dataset directory
    
    Args:
        dataset_path (str): Path to the dataset directory
        
    Returns:
        dict: Dictionary with filename as key and NetworkX graph as value
    """
    graphs = {}
    gml_files = glob.glob(os.path.join(dataset_path, gml_file))

    for file_path in gml_files:
        filename = os.path.basename(file_path)
        try:
            graph = nx.read_gml(file_path)
            graphs[filename] = graph
            print(f"Successfully loaded {filename}: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges")
        except Exception as e:
            print(f"\033[91mError loading \033[0m{filename}: {e}")
    return graphs


def visualize_topology(graph, title="Network Topology", figsize=(12, 8)):
    """
    Generate and display topology graph
    
    Args:
        graph: NetworkX graph object
        title (str): Title for the plot
        figsize (tuple): Figure size
    """
    plt.figure(figsize=figsize)

    # Use spring layout for better visualization
    pos = nx.spring_layout(graph, k=1, iterations=50)

    # Draw the network
    nx.draw_networkx_nodes(graph, pos, node_color='lightblue',
                           node_size=300, alpha=0.7)
    nx.draw_networkx_edges(graph, pos, alpha=0.5, width=1)
    nx.draw_networkx_labels(graph, pos, font_size=8)

    plt.title(title)
    plt.axis('off')
    plt.tight_layout()
    plt.show()


def analyze_topology(graph, name):
    """
    Print basic topology analysis
    
    Args:
        graph: NetworkX graph object
        name (str): Graph name
    """
    print(f"\n=== Topology Analysis for {name} ===")
    print(f"Nodes: {graph.number_of_nodes()}")
    print(f"Edges: {graph.number_of_edges()}")
    print(f"Connected: {nx.is_connected(graph)}")

    if nx.is_connected(graph):
        print(f"Diameter: {nx.diameter(graph)}")
        print(f"Average shortest path length: {nx.average_shortest_path_length(graph):.2f}")

    print(f"Average degree: {sum(dict(graph.degree()).values()) / graph.number_of_nodes():.2f}")


def main():
    # Read all GML files
    gml_file_path = "dataset/generated"
    gml_file_name = "W5N_20250922_170214.gml"
    graphs = read_gml_files(gml_file_path, gml_file_name)

    if not graphs:
        print("No GML files found in dataset directory")
        return

    # Process each graph
    for filename, graph in graphs.items():
        name = filename.replace('.gml', '')

        # Analyze topology
        analyze_topology(graph, name)

        # Visualize topology
        visualize_topology(graph, f"{name} Network Topology")


if __name__ == "__main__":
    main()
