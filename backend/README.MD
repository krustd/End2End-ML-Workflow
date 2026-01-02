# 机器学习数据分析与统计系统后端

![Icon](../Icon.png)

![Go Version](https://img.shields.io/badge/Go-1.24+-blue.svg)](https://golang.org)
![GoFrame](https://img.shields.io/badge/GoFrame-v2.9.7-orange.svg)](https://goframe.org)
![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

这是基于GoFrame v2框架的机器学习数据分析与统计系统后端服务，提供完整的REST API接口，与Python ML API对接，实现数据分析、模型训练和预测功能。

## 🚀 特性

- **现代化架构**: 基于GoFrame v2框架，支持最新Go 1.24+版本
- **分层架构**: Controller -> Logic -> HTTP Client -> Python ML API
- **REST API**: 提供完整的数据分析、模型管理和预测服务API
- **Python对接**: 与Python ML API无缝集成，支持机器学习功能
- **配置管理**: 基于YAML的配置文件管理
- **日志系统**: 完整的日志记录和管理
- **错误处理**: 统一的错误处理和响应格式
- **CORS支持**: 支持跨域请求，方便前端调用

## 📁 项目结构

```
.
├── api/                    # API接口定义
│   ├── data/              # 数据管理API
│   ├── model/             # 模型管理API
│   ├── predict/           # 预测服务API
│   └── system/            # 系统管理API
├── internal/              # 内部实现
│   ├── cmd/               # 命令行入口
│   ├── controller/        # 控制器层
│   │   ├── data/         # 数据管理控制器
│   │   ├── model/        # 模型管理控制器
│   │   ├── predict/      # 预测服务控制器
│   │   └── system/       # 系统管理控制器
│   ├── logic/             # 业务逻辑层
│   │   ├── data/         # 数据管理逻辑
│   │   ├── model/        # 模型管理逻辑
│   │   ├── predict/      # 预测服务逻辑
│   │   └── system/       # 系统管理逻辑
│   ├── middleware/        # 中间件
│   └── service/           # 服务层
│       └── http_client/   # HTTP客户端服务
├── manifest/              # 部署配置
│   ├── config/            # 应用配置
│   ├── deploy/            # Kubernetes部署
│   └── docker/            # Docker配置
└── resource/              # 静态资源
```

## 🛠️ 快速开始

### 环境要求

- Go 1.24+
- Python ML API服务 (默认运行在localhost:8000)

### 安装步骤

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd backend
   ```

2. **安装依赖**
   ```bash
   go mod download
   ```

3. **配置文件**
   复制并修改配置文件：
   ```bash
   cp manifest/config/config.yaml.example manifest/config/config.yaml
   ```
   
   编辑 `manifest/config/config.yaml`，配置Python API连接信息。

4. **启动服务**
   ```bash
   go run main.go
   ```

5. **验证服务**
   - HTTP API: http://localhost:8080
   - 健康检查: http://localhost:8080/health
   - API文档: http://localhost:8080/swagger

## 📊 API接口

### 数据管理API

- `POST /data/upload` - 上传CSV数据文件
- `GET /data/info` - 获取数据信息
- `GET /data/preview` - 获取数据预览
- `POST /data/process` - 处理数据

### 模型管理API

- `POST /model/train` - 训练模型
- `GET /model/available` - 获取可用模型
- `GET /model/trained` - 获取已训练模型
- `GET /model/metrics/{model_name}` - 获取模型指标
- `POST /model/compare` - 比较模型
- `GET /model/info` - 获取模型信息

### 预测服务API

- `POST /predict` - 单条预测
- `POST /predict/batch` - 批量预测
- `POST /predict/export` - 导出预测结果

### Hello API

- `GET /hello` - Hello World示例接口

### 系统管理API

- `GET /` - 根路径，返回API信息
- `GET /system/status` - 获取系统状态

## 🔧 开发指南

### 使用Makefile

项目提供了便捷的Makefile命令：

```bash
# 构建项目
make build

# 运行项目
make run

# 格式化代码
make fmt

# 代码检查
make vet

# 运行测试
make test
```

## 🔐 配置说明

### 服务器配置

```yaml
server:
  address: ":8080"  # Go后端服务端口
  openapiPath: "/api.json"
  swaggerPath: "/swagger"
  logPath: "log/http"
  logLevel: "all"
  logStdout: true
  errorStack: true
```

### Python API配置

```yaml
python_api:
  host: "localhost"
  port: 8000  # Python ML API服务端口
  timeout: 30   # 超时时间（秒）
  debug: false   # 是否启用调试模式
```

### 日志配置

```yaml
logger:
  path: "log/app"   # 日志文件存放目录
  level: "all"       # 日志级别
  stdout: true        # 是否同时输出到控制台
  ctxKeys: ["Trace-Id"]
```

## 📋 开发规范

- 遵循Go官方代码规范
- 使用GoFrame推荐的项目结构
- 提交前运行`go fmt`和`go vet`
- 单元测试覆盖率不低于80%

## 📚 相关文档

- [GoFrame官方文档](https://goframe.org/)
- [GoFrame快速开始](https://goframe.org/quick)
- [GoFrame API参考](https://goframe.org/api)

## 🐛 问题反馈

如果您在使用过程中遇到任何问题，请通过以下方式反馈：

1. [提交Issue](https://github.com/your-repo/issues)
2. [讨论区](https://github.com/your-repo/discussions)
3. 邮件: support@example.com

## 📄 许可证

本项目采用MIT许可证 - 查看[LICENSE](LICENSE)文件了解详情。

## 🙏 致谢

感谢以下开源项目：

- [GoFrame](https://github.com/gogf/gf) - 强大的Go应用开发框架
- [Python ML API](../ml_model/) - 机器学习模型服务

---

**注意**: 这是机器学习数据分析与统计系统的后端服务，需要与Python ML API配合使用。