package predict

import (
	"context"
	"time"

	"github.com/gogf/gf/v2/errors/gerror"
	"github.com/gogf/gf/v2/frame/g"

	v1 "template/api/predict/v1"
	"template/internal/service/http_client"
)

type IPredictLogic interface {
	Predict(ctx context.Context, req *v1.PredictReq) (res *v1.PredictRes, err error)
	BatchPredict(ctx context.Context, req *v1.BatchPredictReq) (res *v1.BatchPredictRes, err error)
	ExportPredictions(ctx context.Context, req *v1.ExportPredictionsReq) (res *v1.ExportPredictionsRes, err error)
}

type sPredictLogic struct {
	client *http_client.Client
}

func NewPredictLogic() IPredictLogic {
	return &sPredictLogic{
		client: http_client.NewClient(),
	}
}
func (s *sPredictLogic) Predict(ctx context.Context, req *v1.PredictReq) (res *v1.PredictRes, err error) {
	result, err := s.client.PredictWithModelAndInfo(ctx, req.Data, req.ModelName, req.ModelData, req.ModelInfoData)
	if err != nil {
		g.Log().Errorf(ctx, "预测失败: %v", err)
		return nil, gerror.Wrap(err, "预测失败")
	}

	success, ok := result["success"].(bool)
	if !ok || !success {
		message, _ := result["message"].(string)
		if message == "" {
			message = "预测失败"
		}
		return nil, gerror.New(message)
	}

	prediction, ok := result["prediction"].(float64)
	if !ok {
		return nil, gerror.New("预测结果格式错误")
	}

	modelName, _ := result["model_name"].(string)
	if modelName == "" {
		modelName = req.ModelName
	}

	timestamp, _ := result["timestamp"].(string)
	if timestamp == "" {
		timestamp = time.Now().Format("2006-01-02 15:04:05")
	}

	res = &v1.PredictRes{
		Success:    true,
		Prediction: prediction,
		ModelName:  modelName,
		Timestamp:  timestamp,
	}

	return res, nil
}
func (s *sPredictLogic) BatchPredict(ctx context.Context, req *v1.BatchPredictReq) (res *v1.BatchPredictRes, err error) {
	result, err := s.client.BatchPredictWithModelAndInfo(ctx, req.Data, req.ModelName, req.ModelData, req.ModelInfoData)
	if err != nil {
		g.Log().Errorf(ctx, "批量预测失败: %v", err)
		return nil, gerror.Wrap(err, "批量预测失败")
	}

	success, ok := result["success"].(bool)
	if !ok || !success {
		message, _ := result["message"].(string)
		if message == "" {
			message = "批量预测失败"
		}
		return nil, gerror.New(message)
	}

	predictionsData, ok := result["predictions"].([]interface{})
	if !ok {
		return nil, gerror.New("批量预测结果格式错误")
	}

	predictions := make([]float64, 0, len(predictionsData))
	for _, item := range predictionsData {
		if prediction, ok := item.(float64); ok {
			predictions = append(predictions, prediction)
		}
	}

	modelName, _ := result["model_name"].(string)
	if modelName == "" {
		modelName = req.ModelName
	}

	timestamp, _ := result["timestamp"].(string)
	if timestamp == "" {
		timestamp = time.Now().Format("2006-01-02 15:04:05")
	}

	res = &v1.BatchPredictRes{
		Success:      true,
		Predictions:  predictions,
		ModelName:    modelName,
		TotalSamples: len(predictions),
		Timestamp:    timestamp,
	}

	return res, nil
}
func (s *sPredictLogic) ExportPredictions(ctx context.Context, req *v1.ExportPredictionsReq) (res *v1.ExportPredictionsRes, err error) {
	result, err := s.client.BatchPredictWithModelAndInfo(ctx, req.Data, req.ModelName, req.ModelData, req.ModelInfoData)
	if err != nil {
		g.Log().Errorf(ctx, "导出预测结果失败: %v", err)
		return nil, gerror.Wrap(err, "导出预测结果失败")
	}

	success, ok := result["success"].(bool)
	if !ok || !success {
		message, _ := result["message"].(string)
		if message == "" {
			message = "导出预测结果失败"
		}
		return nil, gerror.New(message)
	}

	outputPath, _ := result["output_path"].(string)

	res = &v1.ExportPredictionsRes{
		Success:      true,
		Message:      "预测结果导出成功",
		OutputPath:   outputPath,
		Format:       req.Format,
		SamplesCount: len(req.Data),
	}

	return res, nil
}
