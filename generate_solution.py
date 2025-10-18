"""
生成路由方案并保存到results文件夹
"""
import yaml
import requests
import os
import networkx as nx
import re
from datetime import datetime
from typing import Dict, Any


# from baseline import file_path

def load_api_config(config_file: str = "config/API.yaml") -> Dict[str, str]:
    """从YAML文件加载API配置"""
    try:
        with open(config_file, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
        if "problem_description_file" in config:
            problem_file = config['problem_description_file']
            with open(problem_file, 'r', encoding='utf-8') as pd:
                config['problem_description'] = pd.read()
        elif "problem_description_file" not in config:
            print("没有找到问题描述文件，请检查配置文件")

        if "graph_description_file" in config:
            graph_description_file = config['graph_description_file']
            with open(graph_description_file, 'r', encoding='utf-8') as gd:
                config['graph_description'] = gd.read()
        elif "graph_description_file" not in config:
            print("没有找到网络拓扑描述文件，请检查配置文件")

        if "flow_description_file" in config:
            flow_description_file = config['flow_description_file']
            with open(flow_description_file, 'r', encoding='utf-8') as fd:
                config['flow_description'] = fd.read()
        elif "flow_description_file" not in config:
            print("没有找到数据流描述文件，请检查配置文件")

        return config
    except FileNotFoundError:
        raise FileNotFoundError(f"配置文件 {config_file} 不存在")
    except yaml.YAMLError as e:
        raise ValueError(f"YAML文件格式错误: {e}")


class APIClient:
    """API客户端类"""

    def __init__(self, config_file: str = "./config/API.yaml"):
        self.config = load_api_config(config_file)
        self.base_url = self.config.get('base_url')
        self.api_key = self.config.get('api_key')
        self.problem_description = self.config.get('problem_description')
        self.graph_description = self.config.get('graph_description')
        self.flow_description = self.config.get('flow_description')

        if not self.base_url or not self.api_key:
            raise ValueError("API配置中缺少必要的base_url或api_key")

    def get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

    def chat_completion(self, messages: list, model: str = "gpt-3.5-turbo",
                        temperature: float = 0.7, max_tokens: int = 100000) -> Dict[str, Any]:
        """
        完成API调用
        注意：max_tokens对于不同模型不一样，如gpt3.5-turbo就不能用100000
        """
        url = f"{self.base_url}/chat/completions"

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        try:
            response = requests.post(
                url,
                json=payload,
                headers=self.get_headers(),
                timeout=300
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"API请求失败: {e}")

    def simple_chat(self, message: str, model: str = "gpt-3.5-turbo") -> str:
        """简单调用接口"""
        messages = [{"role": "user", "content": message}]
        response = self.chat_completion(messages, model)

        if 'choices' in response and len(response['choices']) > 0:
            return response['choices'][0]['message']['content']
        else:
            raise Exception("API响应格式异常")


def save_result_to_file(content: str, model_name: str) -> str:
    """保存结果到results文件夹，文件名为model_generated_时间戳"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{model_name}_generated_{timestamp}.txt"
    filepath = os.path.join("results", filename)

    # 确保results目录存在
    os.makedirs("results", exist_ok=True)

    # 保存结果
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"模型: {model_name}\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 50 + "\n\n")
        f.write(content)

    return filepath


# 使用示例
if __name__ == "__main__":
    # 创建API客户端
    client = APIClient()
    model = "gpt-5"
    # 打印配置信息
    print(f"Base URL: {client.base_url}")
    print(f"API Key: {client.api_key[:10]}...")
    print("model name:", model, "\n")

    from optimal_solution import OptimalSolver

    file_path = "dataset/generated/W20N_20250924_144247.gml"
    graph = nx.read_gml(file_path)
    flow = client.flow_description
    optimal_solution = OptimalSolver(graph)
    start_node = re.search(r'初始点：(\d+)', flow).group(1)
    end_node = re.search(r'终点：(\d+)', flow).group(1)
    bandwidth = int(re.search(r'数据流待分配带宽：(\d+)', flow).group(1))
    print(f"\033[33m开始搜索最优路径...\033[0m")
    optimal_path, optimal_mlu, all_paths_info = optimal_solution.find_optimal_path(
        start_node,
        end_node,
        bandwidth,
        max_path_length=10  # Limit max path length to avoid long search time
    )
    if optimal_path is None:
        print("No feasible path found!")
    print("\nOptimal path (minimizing MLU):")
    print(f"Path: {' -> '.join(map(str, optimal_path))}")
    print(f"Path length: {len(optimal_path) - 1} hops")
    print(f"MLU: {optimal_mlu:.1f}")

    print("\n前5条最优路径:")
    for i, (path, mlu) in enumerate(all_paths_info[:5], 1):
        path_str = ' -> '.join(map(str, path))
        print(f"{i}. MLU={mlu:.3f}, 路径: {path_str}")

    # 生成方案
    try:
        prompt = client.problem_description + client.graph_description + "4. 下面是需要分配的数据流 \n" + client.flow_description
        response = client.simple_chat(prompt, model)
        print(f"\n\033[33mAI生成路由方案:\033[0m {response}")
        promt_cal_diff = response + "请计算该方案与最优解的MLU值差异，最优解的MLU值为：" + str(
            optimal_mlu) + "，并只返回数值差异部分。"
        diff = client.simple_chat(promt_cal_diff, model)
        print("\n 和最优解的MLU值相差为：", diff)

        # 保存结果
        saved_filepath = save_result_to_file(response, model)
        print(f"\n结果已保存到: {saved_filepath}")

    except Exception as e:
        print(f"错误: {e}")
