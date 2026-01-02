package v1

import (
	"github.com/gogf/gf/v2/frame/g"
)

// ModelTrainReq 模型训练请求
type ModelTrainReq struct {
	g.Meta              `path:"/model/train" method:"POST" tags:"模型管理" summary:"训练模型"`
	ModelType           string  `json:"model_type" v:"required" dc:"模型类型"`
	TargetColumn        string  `json:"target_column" dc:"目标列名"`
	TestSize            float64 `json:"test_size" v:"between:0,1" dc:"测试集比例，默认0.2"`
	TuneHyperparameters bool    `json:"tune_hyperparameters" dc:"是否进行超参数调优"`
}

// ModelTrainRes 模型训练响应
type ModelTrainRes struct {
	Success       bool               `json:"success"`
	Message       string             `json:"message"`
	ModelName     string             `json:"model_name"`
	ModelType     string             `json:"model_type"`
	TrainMetrics  map[string]float64 `json:"train_metrics"`
	TestMetrics   map[string]float64 `json:"test_metrics"`
	CvScores      map[string]float64 `json:"cv_scores"`
	ModelPath     string             `json:"model_path"`
	ModelData     string             `json:"model_data"`      // 添加模型数据字段，用于存储base64编码的模型
	ModelInfoData string             `json:"model_info_data"` // 添加模型信息数据字段，用于存储base64编码的模型信息
	FeatureNames  []string           `json:"feature_names"`   // 添加特征名称字段，用于存储数据列信息
	TargetName    string             `json:"target_name"`     // 添加目标列名称字段，用于存储预测目标列信息
}

// AvailableModelsReq 获取可用模型请求
type AvailableModelsReq struct {
	g.Meta `path:"/model/available" method:"GET" tags:"模型管理" summary:"获取可用的模型类型"`
}

// AvailableModelsRes 获取可用模型响应
type AvailableModelsRes struct {
	Success bool     `json:"success"`
	Models  []string `json:"models"`
}

// TrainedModelsReq 获取已训练模型请求
type TrainedModelsReq struct {
	g.Meta `path:"/model/trained" method:"GET" tags:"模型管理" summary:"获取已训练的模型"`
}

// TrainedModelsRes 获取已训练模型响应
type TrainedModelsRes struct {
	Success bool     `json:"success"`
	Models  []string `json:"models"`
}

// ModelMetricsReq 获取模型评估指标请求
type ModelMetricsReq struct {
	g.Meta    `path:"/model/metrics/{model_name}" method:"GET" tags:"模型管理" summary:"获取模型评估指标"`
	ModelName string `v:"required" dc:"模型名称"`
}

// ModelMetricsRes 获取模型评估指标响应
type ModelMetricsRes struct {
	Success bool                   `json:"success"`
	Metrics map[string]interface{} `json:"metrics"`
}

// CompareModelsReq 比较模型性能请求
type CompareModelsReq struct {
	g.Meta   `path:"/model/compare" method:"POST" tags:"模型管理" summary:"比较所有模型的性能"`
	TestSize float64 `json:"test_size" v:"between:0,1" dc:"测试集比例，默认0.2"`
}

// CompareModelsRes 比较模型性能响应
type CompareModelsRes struct {
	Success           bool                     `json:"success"`
	ComparisonResults map[string]interface{}   `json:"comparison_results"`
	BestModel         string                   `json:"best_model"`
	SortedModels      []map[string]interface{} `json:"sorted_models"`
}

// ModelInfoReq 获取模型信息请求
type ModelInfoReq struct {
	g.Meta    `path:"/model/info" method:"GET" tags:"模型管理" summary:"获取模型信息"`
	ModelName string `json:"model_name" dc:"模型名称"`
}

// ModelInfoRes 获取模型信息响应
type ModelInfoRes struct {
	Success   bool                   `json:"success"`
	ModelInfo map[string]interface{} `json:"model_info"`
}
