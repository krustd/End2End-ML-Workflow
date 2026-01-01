package v1

import (
	"github.com/gogf/gf/v2/frame/g"
)

// PredictReq 单条预测请求
type PredictReq struct {
	g.Meta    `path:"/predict" method:"POST" tags:"预测服务" summary:"使用模型进行预测"`
	Data      map[string]interface{} `json:"data" v:"required" dc:"预测数据"`
	ModelName string                 `json:"model_name" dc:"模型名称"`
}

// PredictRes 单条预测响应
type PredictRes struct {
	Success    bool    `json:"success"`
	Prediction float64 `json:"prediction"`
	ModelName  string  `json:"model_name"`
	Timestamp  string  `json:"timestamp"`
	Message    string  `json:"message,omitempty"`
}

// BatchPredictReq 批量预测请求
type BatchPredictReq struct {
	g.Meta    `path:"/predict/batch" method:"POST" tags:"预测服务" summary:"批量预测"`
	Data      []map[string]interface{} `json:"data" v:"required" dc:"批量预测数据"`
	ModelName string                   `json:"model_name" dc:"模型名称"`
}

// BatchPredictRes 批量预测响应
type BatchPredictRes struct {
	Success      bool      `json:"success"`
	Predictions  []float64 `json:"predictions"`
	ModelName    string    `json:"model_name"`
	TotalSamples int       `json:"total_samples"`
	Timestamp    string    `json:"timestamp"`
	Message      string    `json:"message,omitempty"`
}

// ExportPredictionsReq 导出预测结果请求
type ExportPredictionsReq struct {
	g.Meta    `path:"/predict/export" method:"POST" tags:"预测服务" summary:"导出预测结果"`
	Data      []map[string]interface{} `json:"data" v:"required" dc:"预测数据"`
	Format    string                   `json:"format" v:"required|in:csv,excel,json" dc:"导出格式: csv, excel, json"`
	ModelName string                   `json:"model_name" dc:"模型名称"`
}

// ExportPredictionsRes 导出预测结果响应
type ExportPredictionsRes struct {
	Success      bool   `json:"success"`
	Message      string `json:"message"`
	OutputPath   string `json:"output_path,omitempty"`
	Format       string `json:"format,omitempty"`
	SamplesCount int    `json:"samples_count,omitempty"`
}
