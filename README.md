# HEADLM

This project is similar with HEADRL, but using LLM.

## 安装环境

```
conda create -n flowlm python=3.12
conda activate flowlm
pip install -r requirements.txt
```

## 运行用例

### 路由方案生成

#### 使用已有图和数据流需求进行方案生成

运行 `python generate_solution.py` 生成路由方案，生成的方案会保存在results文件夹中，文件名格式为
*模型_generated_日期_时间.txt* 。

将生成的路由方案复制到 `check_availability.py` 中 `results` 部分，运行 `python check_availability.py`，验证结果将显示在终端。

#### 重新生成图和数据流进行方案生成

1. 重新生成图：运行 `python dataset/W100generate.py` 将会生成20个节点组成的无向连通图，其中节点位置、路径长短和路径初始带宽均为随机生成数据。
   若不需要覆盖原有用于测试的graph则选否，选是的话graph_description文件会被新的graph覆盖。
2. 随机指定数据流：在 `config/flow_description.txt` 中修改起始点、终点或待分配带宽。为与拓扑图匹配，起始点和终点应该小于20，待分配带宽小于等于5。
3. 重复使用已有图和数据流需求进行方案生成的步骤。

### 路由方案性能对比

选择上一个测试用例中用于生成路由方案的gml网络拓扑文件，复制到 `baseline.py` 中的 `file_path`，
运行 `python baseline.py`，得到baseline生成的路径和MLU。运行 `python generate_solution.py`，得到LLM生成的路径和MLU。

## 其他

`python read_data.py` 可以指定生成gml文件对应的图，`python k_shortest_paths.py` 可以测试baseline生成效果。