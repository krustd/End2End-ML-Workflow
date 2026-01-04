# 机器学习数据分析与统计系统

<p align="center">
  <img src="../Icon.png" alt="Icon" width="150" height="150">
</p>

这是一个基于机器学习的数据分析与统计系统，提供了完整的数据处理、模型训练和预测功能，以及RESTful API接口供后端调用。系统支持多Worker模式，使用Redis进行状态共享，提高并发处理能力。

## 功能特点

- **数据处理**: 支持CSV文件上传、数据验证和预处理
- **模型训练**: 支持多种回归模型（线性回归、岭回归、随机森林等）
- **预测服务**: 支持单条和批量预测
- **结果导出**: 支持CSV、Excel和JSON格式的预测结果导出
- **RESTful API**: 提供完整的API接口供后端调用
- **模型比较**: 支持多种模型的性能比较
- **特征分析**: 支持特征重要性计算和异常值检测
- **数据概要**: 自动生成数据概要报告
- **多Worker模式**: 支持Gunicorn + Uvicorn多进程部署
- **状态共享**: 使用Redis进行多进程间状态共享
- **内存缓存**: 智能缓存机制，避免重复加载数据
- **自动清理**: 定期清理长时间未使用的数据，释放内存
- **模型传输**: 支持Base64编码的模型数据传输

## 项目结构

```
ml_model/
├── __init__.py              # 主模块初始化
├── run.py                   # 启动脚本
├── main.py                  # 主启动脚本（支持多Worker模式）
├── pyproject.toml          # 项目依赖配置
├── README.md               # 项目说明
├── .gitignore              # Git忽略文件
├── uv.lock                 # UV依赖锁定文件
├── gunicorn_config.py      # Gunicorn配置文件
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

### 1. 环境要求

- Python 3.8+（推荐使用Python 3.13）
- 推荐使用虚拟环境管理依赖

### 2. 安装依赖

使用uv（推荐）：
```bash
cd ml_model
uv sync
```

或使用pip：
```bash
cd ml_model
pip install -e .
```

### 3. 运行API服务

#### 单进程模式（开发环境）

```bash
# 使用默认配置运行
python run.py

# 自定义主机和端口
python run.py --host 127.0.0.1 --port 8080

# 启用调试模式
python run.py --debug
```

#### 多Worker模式（生产环境）

```bash
# 使用main.py启动（推荐）
uv run main.py                    # 默认启动多Worker模式
uv run main.py --workers 4        # 指定4个Worker进程
uv run main.py --mode single       # 切换到单进程模式
uv run main.py --debug             # 启用调试模式

# 使用run.py启动
uv run run.py --use-gunicorn       # 使用Gunicorn启动多Worker模式
uv run run.py --use-gunicorn --workers 4  # 指定4个Worker进程

# 直接使用Gunicorn
uv run gunicorn -c gunicorn_config.py api.ml_api:app
```

服务启动后，可以通过以下地址访问：
- API服务: http://localhost:8000
- API文档: http://localhost:8000/docs

#### 多Worker模式要求

多Worker模式需要以下环境支持：
- **Redis服务**: 用于状态共享，默认运行在localhost:6379
- **内存管理**: 每个Worker进程独立管理内存，建议根据数据量调整Worker数量
- **文件访问**: 确保所有Worker进程都能访问上传的文件

#### 多Worker模式说明

本项目支持使用Gunicorn + Uvicorn的多Worker模式，可以处理来自GoFrame等客户端的并发请求：

- **默认Worker数量**: CPU核心数 × 2 + 1
- **请求分配**: 当GoFrame发送4个并发请求时，Gunicorn会自动将它们分配给4个不同的Worker进程
- **并行处理**: 每个Worker进程可以独立处理请求，提高系统并发能力
- **配置文件**: [`gunicorn_config.py`](gunicorn_config.py:1) 包含详细的Gunicorn配置

#### 并发测试

```bash
# 安装测试依赖
uv add aiohttp

# 运行并发测试
uv run test_concurrent.py --requests 10
```

## API接口说明

### 系统状态

- `GET /` - 获取API基本信息
- `GET /system/status` - 获取系统状态

### 数据管理

- `POST /data/upload` - 上传CSV数据文件
- `GET /data/info` - 获取数据信息
- `GET /data/preview` - 获取数据预览（可指定行数）
- `POST /data/process` - 处理数据（支持缺失值处理和目标列设置）

### 模型管理

- `GET /model/available` - 获取可用的模型类型
- `GET /model/trained` - 获取已训练的模型
- `POST /model/train` - 训练模型（支持模型类型、目标列、测试集比例和超参数调优）
- `GET /model/metrics/{model_name}` - 获取模型评估指标
- `POST /model/compare` - 比较所有模型的性能
- `GET /model/info` - 获取模型信息（可指定模型名称）

### 预测服务

- `POST /predict` - 单条预测（支持模型数据、模型名称和模型信息）
- `POST /predict/batch` - 批量预测（支持模型数据、模型名称和模型信息）
- `POST /predict/export` - 导出预测结果（支持CSV、Excel和JSON格式）

### 状态管理API

- `GET /system/status` - 获取系统状态（包括Redis连接状态）
- `GET /data/files` - 获取所有存储的文件信息
- `POST /data/switch/{file_id}` - 切换到指定的文件
- `DELETE /data/files/{file_id}` - 删除指定的文件

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

### 2. 处理数据

```python
# 处理数据（删除缺失值）
response = requests.post(
    'http://localhost:8000/data/process',
    json={
        'handle_missing': 'drop',
        'target_column': 'price'
    }
)
print(response.json())
```

### 3. 训练模型

```python
# 训练线性回归模型
response = requests.post(
    'http://localhost:8000/model/train',
    json={
        'model_type': 'linear_regression',
        'target_column': 'price',
        'test_size': 0.2,
        'tune_hyperparameters': True,
        'return_model': True
    }
)
print(response.json())
```

### 4. 进行预测

```python
# 单条预测
response = requests.post(
    'http://localhost:8000/predict',
    json={
        'data': {
            'feature1': 100,
            'feature2': 3,
            'feature3': 2
        },
        'model_name': 'linear_regression'
    }
)
print(response.json())

# 批量预测
response = requests.post(
    'http://localhost:8000/predict/batch',
    json={
        'data': [
            {'feature1': 100, 'feature2': 3, 'feature3': 2},
            {'feature1': 150, 'feature2': 4, 'feature3': 3}
        ],
        'model_name': 'linear_regression'
    }
)
print(response.json())
```

### 5. 导出预测结果

```python
# 导出预测结果为CSV
response = requests.post(
    'http://localhost:8000/predict/export',
    json={
        'data': [
            {'feature1': 100, 'feature2': 3, 'feature3': 2},
            {'feature1': 150, 'feature2': 4, 'feature3': 3}
        ],
        'format': 'csv',
        'model_name': 'linear_regression'
    }
)

# 保存文件
with open('predictions.csv', 'wb') as f:
    f.write(response.content)
```

### 6. 模型比较

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

配置文件位于 `config/settings.py`，包含以下配置项：

- `MODEL_CONFIG`: 模型相关配置
- `DATA_CONFIG`: 数据处理相关配置
- `API_CONFIG`: API服务相关配置
- `PREDICTION_CONFIG`: 预测服务相关配置
- `SYSTEM_CONFIG`: 系统相关配置
- `LOGGING_CONFIG`: 日志相关配置
- `DATABASE_CONFIG`: 数据库相关配置
- `REDIS_CONFIG`: Redis连接配置（多Worker模式）

### Redis配置

```python
REDIS_CONFIG = {
    'host': 'localhost',
    'port': 6379,
    'db': 0,
    'decode_responses': True,
    'socket_timeout': 5,
    'socket_connect_timeout': 5,
    'retry_on_timeout': True
}
```

## 数据处理功能

### 数据预处理

- 缺失值处理：支持删除、均值填充、中位数填充、众数填充
- 分类变量处理：自动进行独热编码
- 数据验证：自动检测数据类型、缺失值和异常值

### 数据分析

- 数据概要生成：自动计算数值列和分类列的统计摘要
- 异常值检测：支持IQR和Z-score方法
- 特征重要性计算：基于模型的特征重要性分析

### 内存管理

- **缓存机制**: 每个Worker进程最多保留3个数据副本
- **自动清理**: 定期清理超过30分钟未使用的数据
- **访问跟踪**: 跟踪数据的最后访问时间，智能管理内存

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

## 技术栈

- **后端框架**: FastAPI
- **Web服务器**: Gunicorn + Uvicorn（多Worker模式）
- **机器学习**: Scikit-learn
- **数据处理**: Pandas, NumPy
- **数据可视化**: Matplotlib, Seaborn
- **配置管理**: Pydantic
- **依赖管理**: UV
- **状态存储**: Redis（多Worker模式）
- **序列化**: Pickle, Base64

## 系统要求

- Python 3.8+（推荐使用Python 3.13）
- 推荐使用虚拟环境管理依赖

## 多Worker模式注意事项

1. **状态共享**: 多Worker进程之间不共享内存，系统使用Redis进行状态共享
2. **文件上传**: 文件上传功能在多Worker模式下需要确保所有Worker都能访问上传的文件
3. **日志**: 日志会输出到标准输出，由Gunicorn统一管理
4. **调试**: 在多Worker模式下，调试较为困难，建议在开发时使用单进程模式
5. **性能调优**:
   - Worker数量通常设置为CPU核心数的2-4倍
   - 最大请求数根据内存使用情况调整，防止内存泄漏
   - 超时设置根据业务需求调整
6. **内存管理**:
   - 每个Worker进程独立管理内存，避免内存泄漏影响其他进程
   - 使用智能缓存机制，限制每个进程最多保留3个数据副本
   - 定期清理长时间未使用的数据，释放内存资源

## 许可证

本项目采用MIT许可证。