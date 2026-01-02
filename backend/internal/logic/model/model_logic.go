package model

import (
	"context"

	"github.com/gogf/gf/v2/errors/gerror"
	"github.com/gogf/gf/v2/frame/g"

	v1 "template/api/model/v1"
	"template/internal/service/http_client"
)

type IModelLogic interface {
	TrainModel(ctx context.Context, req *v1.ModelTrainReq) (res *v1.ModelTrainRes, err error)
	GetAvailableModels(ctx context.Context, req *v1.AvailableModelsReq) (res *v1.AvailableModelsRes, err error)
	GetTrainedModels(ctx context.Context, req *v1.TrainedModelsReq) (res *v1.TrainedModelsRes, err error)
	GetModelMetrics(ctx context.Context, req *v1.ModelMetricsReq) (res *v1.ModelMetricsRes, err error)
	CompareModels(ctx context.Context, req *v1.CompareModelsReq) (res *v1.CompareModelsRes, err error)
	GetModelInfo(ctx context.Context, req *v1.ModelInfoReq) (res *v1.ModelInfoRes, err error)
}

type sModelLogic struct {
	client *http_client.Client
}

func NewModelLogic() IModelLogic {
	return &sModelLogic{
		client: http_client.NewClient(),
	}
}
func (s *sModelLogic) TrainModel(ctx context.Context, req *v1.ModelTrainReq) (res *v1.ModelTrainRes, err error) {
	result, err := s.client.TrainModel(ctx, req.ModelType, req.TargetColumn, req.TestSize, req.TuneHyperparameters)
	if err != nil {
		g.Log().Errorf(ctx, "训练模型失败: %v", err)
		return nil, gerror.Wrap(err, "训练模型失败")
	}

	success, ok := result["success"].(bool)
	if !ok || !success {
		message, _ := result["message"].(string)
		if message == "" {
			message = "训练模型失败"
		}
		return nil, gerror.New(message)
	}

	modelName, _ := result["model_name"].(string)
	modelType, _ := result["model_type"].(string)
	modelPath, _ := result["model_path"].(string)
	modelData, _ := result["model_data"].(string)
	modelInfoData, _ := result["model_info_data"].(string)

	var featureNames []string
	if fn, ok := result["feature_names"].([]interface{}); ok {
		for _, name := range fn {
			if str, ok := name.(string); ok {
				featureNames = append(featureNames, str)
			}
		}
	}

	targetName, _ := result["target_name"].(string)

	trainMetrics := convertToMetrics(result["train_metrics"])
	testMetrics := convertToMetrics(result["test_metrics"])
	cvScores := convertToMetrics(result["cv_scores"])

	res = &v1.ModelTrainRes{
		Success:       true,
		Message:       "模型训练成功",
		ModelName:     modelName,
		ModelType:     modelType,
		TrainMetrics:  trainMetrics,
		TestMetrics:   testMetrics,
		CvScores:      cvScores,
		ModelPath:     modelPath,
		ModelData:     modelData,
		ModelInfoData: modelInfoData,
		FeatureNames:  featureNames,
		TargetName:    targetName,
	}

	return res, nil
}
func (s *sModelLogic) GetAvailableModels(ctx context.Context, req *v1.AvailableModelsReq) (res *v1.AvailableModelsRes, err error) {
	result, err := s.client.GetAvailableModels(ctx)
	if err != nil {
		g.Log().Errorf(ctx, "获取可用模型失败: %v", err)
		return nil, gerror.Wrap(err, "获取可用模型失败")
	}

	success, ok := result["success"].(bool)
	if !ok || !success {
		message, _ := result["message"].(string)
		if message == "" {
			message = "获取可用模型失败"
		}
		return nil, gerror.New(message)
	}

	modelsData, ok := result["models"].([]interface{})
	if !ok {
		return nil, gerror.New("可用模型数据格式错误")
	}

	models := make([]string, 0, len(modelsData))
	for _, item := range modelsData {
		if model, ok := item.(string); ok {
			models = append(models, model)
		}
	}

	res = &v1.AvailableModelsRes{
		Success: true,
		Models:  models,
	}

	return res, nil
}
func (s *sModelLogic) GetTrainedModels(ctx context.Context, req *v1.TrainedModelsReq) (res *v1.TrainedModelsRes, err error) {
	result, err := s.client.GetTrainedModels(ctx)
	if err != nil {
		g.Log().Errorf(ctx, "获取已训练模型失败: %v", err)
		return nil, gerror.Wrap(err, "获取已训练模型失败")
	}

	success, ok := result["success"].(bool)
	if !ok || !success {
		message, _ := result["message"].(string)
		if message == "" {
			message = "获取已训练模型失败"
		}
		return nil, gerror.New(message)
	}

	modelsData, ok := result["models"].([]interface{})
	if !ok {
		return nil, gerror.New("已训练模型数据格式错误")
	}

	models := make([]string, 0, len(modelsData))
	for _, item := range modelsData {
		if model, ok := item.(string); ok {
			models = append(models, model)
		}
	}

	res = &v1.TrainedModelsRes{
		Success: true,
		Models:  models,
	}

	return res, nil
}
func (s *sModelLogic) GetModelMetrics(ctx context.Context, req *v1.ModelMetricsReq) (res *v1.ModelMetricsRes, err error) {
	result, err := s.client.GetModelMetrics(ctx, req.ModelName)
	if err != nil {
		g.Log().Errorf(ctx, "获取模型指标失败: %v", err)
		return nil, gerror.Wrap(err, "获取模型指标失败")
	}

	success, ok := result["success"].(bool)
	if !ok || !success {
		message, _ := result["message"].(string)
		if message == "" {
			message = "获取模型指标失败"
		}
		return nil, gerror.New(message)
	}

	metricsData, ok := result["metrics"].(map[string]interface{})
	if !ok {
		return nil, gerror.New("模型指标数据格式错误")
	}

	res = &v1.ModelMetricsRes{
		Success: true,
		Metrics: metricsData,
	}

	return res, nil
}
func (s *sModelLogic) CompareModels(ctx context.Context, req *v1.CompareModelsReq) (res *v1.CompareModelsRes, err error) {
	result, err := s.client.CompareModels(ctx, req.TestSize)
	if err != nil {
		g.Log().Errorf(ctx, "比较模型失败: %v", err)
		return nil, gerror.Wrap(err, "比较模型失败")
	}

	success, ok := result["success"].(bool)
	if !ok || !success {
		message, _ := result["message"].(string)
		if message == "" {
			message = "比较模型失败"
		}
		return nil, gerror.New(message)
	}

	comparisonResults, ok := result["comparison_results"].(map[string]interface{})
	if !ok {
		return nil, gerror.New("模型比较结果数据格式错误")
	}

	bestModel, _ := result["best_model"].(string)

	sortedModelsData, ok := result["sorted_models"].([]interface{})
	if !ok {
		return nil, gerror.New("排序后的模型数据格式错误")
	}

	sortedModels := make([]map[string]interface{}, 0, len(sortedModelsData))
	for _, item := range sortedModelsData {
		if model, ok := item.(map[string]interface{}); ok {
			sortedModels = append(sortedModels, model)
		}
	}

	res = &v1.CompareModelsRes{
		Success:           true,
		ComparisonResults: comparisonResults,
		BestModel:         bestModel,
		SortedModels:      sortedModels,
	}

	return res, nil
}
func (s *sModelLogic) GetModelInfo(ctx context.Context, req *v1.ModelInfoReq) (res *v1.ModelInfoRes, err error) {
	result, err := s.client.GetModelInfo(ctx, req.ModelName)
	if err != nil {
		g.Log().Errorf(ctx, "获取模型信息失败: %v", err)
		return nil, gerror.Wrap(err, "获取模型信息失败")
	}

	success, ok := result["success"].(bool)
	if !ok || !success {
		message, _ := result["message"].(string)
		if message == "" {
			message = "获取模型信息失败"
		}
		return nil, gerror.New(message)
	}

	modelInfoData, ok := result["model_info"].(map[string]interface{})
	if !ok {
		return nil, gerror.New("模型信息数据格式错误")
	}

	res = &v1.ModelInfoRes{
		Success:   true,
		ModelInfo: modelInfoData,
	}

	return res, nil
}
func convertToMetrics(metricsData interface{}) map[string]float64 {
	metrics := make(map[string]float64)

	if metricsData == nil {
		return metrics
	}

	if data, ok := metricsData.(map[string]interface{}); ok {
		for key, value := range data {
			if floatValue, ok := value.(float64); ok {
				metrics[key] = floatValue
			}
		}
	}

	return metrics
}
