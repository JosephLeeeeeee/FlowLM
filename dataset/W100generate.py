"""
Waxman图生成工具

使用Waxman随机几何图模型生成连通的网络拓扑图。
生成的图包含随机权重边，并保存为gml格式文件。
同时将图描述复制到配置文件中供后续使用。

功能:
- 生成指定节点数的Waxman图
- 确保图的连通性
- 为边分配随机权重(1-5)
- 可视化显示网络拓扑
- 导出GML格式文件
- 自动复制图描述到配置目录
"""

import networkx as nx
import pylab
import datetime
import random
import os

tag = False
node = 20
while not tag:
    # 默认beta=0.4, alpha=0.1，原代码为0.5和0.1
    # 增大beta和alpha都可以增加连通可能性，避免跳不出tag循环
    G = nx.waxman_graph(node, beta=0.8, alpha=0.3)
    for u, v in G.edges():
        G.edges[u, v]['weight'] = random.randint(1, 5)
    tag = nx.is_connected(G)

nx.draw_networkx(G)
pylab.show()
print(nx.is_connected(G))

timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"W{node}N_{timestamp}.gml"
gml_path = f"dataset/generated/{filename}"
nx.write_gml(G, gml_path)
print(f"图已保存为: {filename}")

# 复制gml内容到config/graph_description.txt
config_path = "config/graph_description.txt"
if os.path.exists(config_path):
    choice = input(f"文件 {config_path} 已存在，是否覆盖？(y/n): ")
    if choice.lower() != 'y':
        print("已取消复制到配置文件")
    else:
        with open(gml_path, 'r') as gml_file:
            gml_content = gml_file.read()
        with open(config_path, 'w') as config_file:
            config_file.write(gml_content)
        print(f"图描述已复制到: {config_path}")
else:
    with open(gml_path, 'r') as gml_file:
        gml_content = gml_file.read()
    with open(config_path, 'w') as config_file:
        config_file.write(gml_content)
    print(f"图描述已复制到: {config_path}")
