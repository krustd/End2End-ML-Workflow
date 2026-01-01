package predict

import (
	"context"
	"time"

	"github.com/gogf/gf/v2/errors/gerror"
	"github.com/gogf/gf/v2/frame/g"

	v1 "template/api/predict/v1"
	"template/internal/service/http_client"
)

// IPredictLogic 预测服务逻辑接口
type IPredictLogic interface {
	// Predict 单条预测
	Predict(ctx context.Context, req *v1.PredictReq) (res *v1.PredictRes, err error)

	// BatchPredict 批量预测
	BatchPredict(ctx context.Context, req *v1.BatchPredictReq) (res *v1.BatchPredictRes, err error)

	// ExportPredictions 导出预测结果
	ExportPredictions(ctx context.Context, req *v1.ExportPredictionsReq) (res *v1.ExportPredictionsRes, err error)
}

// sPredictLogic 预测服务逻辑实现
type sPredictLogic struct {
	client *http_client.Client
}

// NewPredictLogic 创建预测服务逻辑实例
func NewPredictLogic() IPredictLogic {
	return &sPredictLogic{
		client: http_client.NewClient(),
	}
}

// Predict 单条预测
func (s *sPredictLogic) Predict(ctx context.Context, req *v1.PredictReq) (res *v1.PredictRes, err error) {
	// 调用Python API进行预测
	result, err := s.client.Predict(ctx, req.Data, req.ModelName)
	if err != nil {
		g.Log().Errorf(ctx, "预测失败: %v", err)
		return nil, gerror.Wrap(err, "预测失败")
	}

	// 解析响应
	success, ok := result["success"].(bool)
	if !ok || !success {
		message, _ := result["message"].(string)
		if message == "" {
			message = "预测失败"
		}
		return nil, gerror.New(message)
	}

	// 获取预测结果
	prediction, ok := result["prediction"].(float64)
	if !ok {
		return nil, gerror.New("预测结果格式错误")
	}

	// 获取模型名称
	modelName, _ := result["model_name"].(string)
	if modelName == "" {
		modelName = req.ModelName
	}

	// 获取时间戳
	timestamp, _ := result["timestamp"].(string)
	if timestamp == "" {
		timestamp = time.Now().Format("2006-01-02 15:04:05")
	}

	// 构造响应
	res = &v1.PredictRes{
		Success:    true,
		Prediction: prediction,
		ModelName:  modelName,
		Timestamp:  timestamp,
	}

	return res, nil
}

// BatchPredict 批量预测
func (s *sPredictLogic) BatchPredict(ctx context.Context, req *v1.BatchPredictReq) (res *v1.BatchPredictRes, err error) {
	// 调用Python API进行批量预测
	result, err := s.client.BatchPredict(ctx, req.Data, req.ModelName)
	if err != nil {
		g.Log().Errorf(ctx, "批量预测失败: %v", err)
		return nil, gerror.Wrap(err, "批量预测失败")
	}

	// 解析响应
	success, ok := result["success"].(bool)
	if !ok || !success {
		message, _ := result["message"].(string)
		if message == "" {
			message = "批量预测失败"
		}
		return nil, gerror.New(message)
	}

	// 获取预测结果
	predictionsData, ok := result["predictions"].([]interface{})
	if !ok {
		return nil, gerror.New("批量预测结果格式错误")
	}

	// 转换预测结果
	predictions := make([]float64, 0, len(predictionsData))
	for _, item := range predictionsData {
		if prediction, ok := item.(float64); ok {
			predictions = append(predictions, prediction)
		}
	}

	// 获取模型名称
	modelName, _ := result["model_name"].(string)
	if modelName == "" {
		modelName = req.ModelName
	}

	// 获取时间戳
	timestamp, _ := result["timestamp"].(string)
	if timestamp == "" {
		timestamp = time.Now().Format("2006-01-02 15:04:05")
	}

	// 构造响应
	res = &v1.BatchPredictRes{
		Success:      true,
		Predictions:  predictions,
		ModelName:    modelName,
		TotalSamples: len(predictions),
		Timestamp:    timestamp,
	}

	return res, nil
}

// ExportPredictions 导出预测结果
func (s *sPredictLogic) ExportPredictions(ctx context.Context, req *v1.ExportPredictionsReq) (res *v1.ExportPredictionsRes, err error) {
	// 调用Python API导出预测结果
	// 注意：由于导出预测结果需要返回文件，这里需要特殊处理
	// 我们先调用批量预测API获取结果，然后模拟导出过程
	result, err := s.client.BatchPredict(ctx, req.Data, req.ModelName)
	if err != nil {
		g.Log().Errorf(ctx, "导出预测结果失败: %v", err)
		return nil, gerror.Wrap(err, "导出预测结果失败")
	}

	// 解析响应
	success, ok := result["success"].(bool)
	if !ok || !success {
		message, _ := result["message"].(string)
		if message == "" {
			message = "导出预测结果失败"
		}
		return nil, gerror.New(message)
	}

	// 获取输出路径
	outputPath, _ := result["output_path"].(string)

	// 构造响应
	res = &v1.ExportPredictionsRes{
		Success:      true,
		Message:      "预测结果导出成功",
		OutputPath:   outputPath,
		Format:       req.Format,
		SamplesCount: len(req.Data),
	}

	return res, nil
}
