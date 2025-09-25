import networkx as nx
import k_shortest_paths as ks
from generate_solution import APIClient
import re

file_path = "dataset/generated/W20N_20250924_170313.gml"

client = APIClient()
flow = client.flow_description
print("数据流需求:", flow)

# 提取初始点、终点和带宽
start_node = re.search(r'初始点：(\d+)', flow).group(1)
end_node = re.search(r'终点：(\d+)', flow).group(1)
bandwidth = re.search(r'数据流待分配带宽：(\d+)', flow).group(1)

graph = nx.read_gml(file_path)
shortest_path = ks.k_shortest_paths(graph, start_node, end_node, 1)
path = shortest_path[1][0]  # 获取路径节点列表

print(f"由贪心算法得到的路径为: {path}")
print(f"带宽需求: {bandwidth}")

# 修改路径上每条边的权重，加上带宽
bandwidth_value = int(bandwidth)
for i in range(len(path) - 1):
    u = path[i]
    v = path[i + 1]

    # 获取当前边的权重
    current_weight = graph.edges[u, v]['weight']
    new_weight = current_weight + bandwidth_value
    graph.edges[u, v]['weight'] = new_weight
    print(f"边 ({u}, {v}): {current_weight} -> {new_weight}")

# 计算MLU并显示所有边权重
max_capacity = 0
print("\n所有边权重:")
for u, v, data in graph.edges(data=True):
    weight = data['weight']
    print(f"边 ({u}, {v}): {weight}")
    max_capacity = max(max_capacity, weight)

MLU = max_capacity / 10
print(f"\n最大边权重: {max_capacity}")
print(f"分配带宽: {bandwidth}")
print(f"MLU: {MLU:.3f}")
