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
import argparse


def generate_waxman_graph(
    num_nodes=20,
    beta=0.8,
    alpha=0.3,
    min_weight=1,
    max_weight=5,
    show_visualization=True,
    save_to_file=True,
    output_dir="dataset/generated",
    copy_to_config=True,
    config_path="config/graph_description.txt",
    auto_overwrite=False
):
    """
    生成Waxman拓扑图

    参数:
        num_nodes (int): 节点数量，默认20
        beta (float): Waxman模型beta参数，默认0.8，控制边的密度
        alpha (float): Waxman模型alpha参数，默认0.3，控制距离对边生成的影响
        min_weight (int): 边权重最小值，默认1
        max_weight (int): 边权重最大值，默认5
        show_visualization (bool): 是否显示可视化，默认True
        save_to_file (bool): 是否保存为GML文件，默认True
        output_dir (str): 输出目录，默认"dataset/generated"
        copy_to_config (bool): 是否复制到配置文件，默认True
        config_path (str): 配置文件路径，默认"config/graph_description.txt"
        auto_overwrite (bool): 自动覆盖配置文件（不询问），默认False

    返回:
        tuple: (G, gml_path) - 生成的图对象和保存路径
    """
    # 生成连通的Waxman图
    tag = False
    G = None
    while not tag:
        # 默认beta=0.4, alpha=0.1，原代码为0.5和0.1
        # 增大beta和alpha都可以增加连通可能性，避免跳不出tag循环
        G = nx.waxman_graph(num_nodes, beta=beta, alpha=alpha)
        for u, v in G.edges():
            G.edges[u, v]['weight'] = random.randint(min_weight, max_weight)
        tag = nx.is_connected(G)

    print(f"成功生成连通图，节点数: {num_nodes}, 连通性: {nx.is_connected(G)}")

    # 可视化
    if show_visualization:
        nx.draw_networkx(G)
        pylab.show()

    gml_path = None
    # 保存到文件
    if save_to_file:
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"W{num_nodes}N_{timestamp}.gml"
        gml_path = os.path.join(output_dir, filename)
        nx.write_gml(G, gml_path)
        print(f"图已保存为: {gml_path}")

        # 复制gml内容到config/graph_description.txt
        if copy_to_config:
            should_copy = auto_overwrite
            if not auto_overwrite and os.path.exists(config_path):
                choice = input(f"文件 {config_path} 已存在，是否覆盖？(y/n): ")
                should_copy = choice.lower() == 'y'
            elif not os.path.exists(config_path):
                should_copy = True

            if should_copy:
                # 确保配置目录存在
                os.makedirs(os.path.dirname(config_path), exist_ok=True)

                with open(gml_path, 'r') as gml_file:
                    gml_content = gml_file.read()
                with open(config_path, 'w') as config_file:
                    config_file.write(gml_content)
                print(f"图描述已复制到: {config_path}")
            else:
                print("已取消复制到配置文件")

    return G, gml_path


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='生成Waxman拓扑图',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        allow_abbrev=False  # 禁用自动前缀匹配，避免参数混淆
    )

    parser.add_argument(
        '-n', '--num-nodes',
        type=int,
        default=20,
        help='节点数量'
    )
    parser.add_argument(
        '-b', '--beta',
        type=float,
        default=0.8,
        help='Waxman模型beta参数，控制边的密度'
    )
    parser.add_argument(
        '-a', '--alpha',
        type=float,
        default=0.3,
        help='Waxman模型alpha参数，控制距离对边生成的影响'
    )
    parser.add_argument(
        '--min-weight',
        type=int,
        default=1,
        help='边权重最小值'
    )
    parser.add_argument(
        '--max-weight',
        type=int,
        default=5,
        help='边权重最大值'
    )
    parser.add_argument(
        '--no-viz',
        action='store_true',
        help='不显示可视化'
    )
    parser.add_argument(
        '--no-save',
        action='store_true',
        help='不保存到文件'
    )
    parser.add_argument(
        '-o', '--output-dir',
        type=str,
        default='dataset/generated',
        help='输出目录'
    )
    parser.add_argument(
        '--no-config',
        action='store_true',
        help='不复制到配置文件'
    )
    parser.add_argument(
        '--config-path',
        type=str,
        default='config/graph_description.txt',
        help='配置文件路径'
    )
    parser.add_argument(
        '-y', '--yes',
        action='store_true',
        help='自动覆盖配置文件（不询问）'
    )

    return parser.parse_args()


if __name__ == "__main__":
    # 解析命令行参数
    args = parse_args()

    # 使用命令行参数生成图
    generate_waxman_graph(
        num_nodes=args.num_nodes,
        beta=args.beta,
        alpha=args.alpha,
        min_weight=args.min_weight,
        max_weight=args.max_weight,
        show_visualization=not args.no_viz,
        save_to_file=not args.no_save,
        output_dir=args.output_dir,
        copy_to_config=not args.no_config,
        config_path=args.config_path,
        auto_overwrite=args.yes
    )
