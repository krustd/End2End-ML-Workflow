# 机器学习数据分析与统计系统

这是一个基于机器学习的数据分析与统计系统，提供了完整的数据处理、模型训练和预测功能，以及RESTful API接口供后端调用。

## 功能特点

- **数据处理**: 支持CSV文件上传、数据验证和预处理
- **模型训练**: 支持多种回归模型（线性回归、岭回归、随机森林等）
- **预测服务**: 支持单条和批量预测
- **结果导出**: 支持CSV、Excel和JSON格式的预测结果导出
- **RESTful API**: 提供完整的API接口供后端调用
- **模型比较**: 支持多种模型的性能比较
- **特征分析**: 支持特征重要性计算和异常值检测
- **数据概要**: 自动生成数据概要报告

## 项目结构

```
ml_model/
├── __init__.py              # 主模块初始化
├── main.py                  # 主程序入口
├── run.py                   # 启动脚本
├── pyproject.toml          # 项目依赖配置
├── README.md               # 项目说明
├── data/                   # 数据处理模块
│   ├── __init__.py
│   └── data_processor.py   # 数据处理器
├── models/                 # 模型训练和预测模块
│   ├── __init__.py
│   ├── model_trainer.py    # 模型训练器
│   └── predictor.py        # 预测器
├── api/                    # API接口模块
│   ├── __init__.py
│   └── ml_api.py          # FastAPI应用
├── config/                 # 配置模块
│   ├── __init__.py
│   └── settings.py        # 配置文件
└── utils/                  # 工具函数模块
    ├── __init__.py
    └── helpers.py          # 工具函数
```

## 安装和运行

### 1. 安装依赖

使用uv（推荐）：
```bash
cd ml_model
uv sync
```

或使用pip：
```bash
cd ml_model
pip install -r requirements.txt  # 如果存在
```

### 2. 运行API服务

```bash
# 使用默认配置运行
python ml_model/run.py

# 自定义主机和端口
python ml_model/run.py --host 127.0.0.1 --port 8080

# 启用调试模式
python ml_model/run.py --debug
```

服务启动后，可以通过以下地址访问：
- API服务: http://localhost:8000
- API文档: http://localhost:8000/docs

## API接口说明

### 系统状态

- `GET /system/status` - 获取系统状态
- `GET /` - 获取API基本信息

### 数据管理

- `POST /data/upload` - 上传CSV数据文件
- `GET /data/info` - 获取数据信息
- `GET /data/preview` - 获取数据预览
- `POST /data/process` - 处理数据

### 模型管理

- `GET /model/available` - 获取可用的模型类型
- `GET /model/trained` - 获取已训练的模型
- `POST /model/train` - 训练模型
- `GET /model/metrics/{model_name}` - 获取模型评估指标
- `POST /model/compare` - 比较所有模型的性能
- `GET /model/info` - 获取模型信息

### 预测服务

- `POST /predict` - 单条预测
- `POST /predict/batch` - 批量预测
- `POST /predict/export` - 导出预测结果

## 使用示例

### 1. 上传数据

```python
import requests

# 上传CSV文件
with open('data.csv', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/data/upload',
        files={'file': f}
    )
print(response.json())
```

### 2. 训练模型

```python
# 训练线性回归模型
response = requests.post(
    'http://localhost:8000/model/train',
    json={
        'model_type': 'linear_regression',
        'target_column': 'price',
        'test_size': 0.2,
        'tune_hyperparameters': True
    }
)
print(response.json())
```

### 3. 进行预测

```python
# 单条预测
response = requests.post(
    'http://localhost:8000/predict',
    json={
        'data': {
            'feature1': 100,
            'feature2': 3,
            'feature3': 2
        }
    }
)
print(response.json())

# 批量预测
response = requests.post(
    'http://localhost:8000/predict/batch',
    json=[
        {'feature1': 100, 'feature2': 3, 'feature3': 2},
        {'feature1': 150, 'feature2': 4, 'feature3': 3}
    ]
)
print(response.json())
```

### 4. 模型比较

```python
# 比较所有模型性能
response = requests.post(
    'http://localhost:8000/model/compare',
    params={'test_size': 0.2}
)
print(response.json())
```

## 支持的模型

- 线性回归 (linear_regression)
- 岭回归 (ridge)
- Lasso回归 (lasso)
- 弹性网络 (elastic_net)
- 随机森林 (random_forest)
- 梯度提升 (gradient_boosting)
- 支持向量回归 (svr)
- 决策树 (decision_tree)
- K近邻 (knn)

## 配置说明

配置文件位于 `ml_model/config/settings.py`，包含以下配置项：

- `MODEL_CONFIG`: 模型相关配置
- `DATA_CONFIG`: 数据处理相关配置
- `API_CONFIG`: API服务相关配置
- `PREDICTION_CONFIG`: 预测服务相关配置
- `SYSTEM_CONFIG`: 系统相关配置
- `LOGGING_CONFIG`: 日志相关配置
- `DATABASE_CONFIG`: 数据库相关配置

## 数据处理功能

### 数据预处理

- 缺失值处理：支持删除、均值填充、中位数填充、众数填充
- 分类变量处理：自动进行独热编码
- 数据验证：自动检测数据类型、缺失值和异常值

### 数据分析

- 数据概要生成：自动计算数值列和分类列的统计摘要
- 异常值检测：支持IQR和Z-score方法
- 特征重要性计算：基于模型的特征重要性分析

## 模型训练与评估

### 训练参数

- `model_type`: 模型类型
- `target_column`: 目标列名
- `test_size`: 测试集比例（默认0.2）
- `tune_hyperparameters`: 是否进行超参数调优（默认False）

### 评估指标

- 均方误差 (MSE)
- 均方根误差 (RMSE)
- 平均绝对误差 (MAE)
- 决定系数 (R²)
- 交叉验证分数

## 预测功能

### 单条预测

支持单条数据的预测，输入格式为JSON对象。

### 批量预测

支持批量数据的预测，输入格式为JSON数组，可自定义批处理大小。

### 结果导出

支持将预测结果导出为以下格式：
- CSV
- Excel
- JSON

## 注意事项

1. 上传的文件必须是CSV格式
2. 数据中至少需要包含一个数值列作为目标变量
3. 模型训练可能需要一些时间，请耐心等待
4. 预测时输入的特征必须与训练时的特征一致
5. 预测结果仅供参考，不构成决策建议
6. 大数据集处理可能需要较长时间，建议适当调整批处理大小

## 系统要求

- Python 3.8+
- 推荐使用虚拟环境管理依赖

## 许可证

本项目采用MIT许可证。