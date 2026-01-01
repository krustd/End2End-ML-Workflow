package predict

import (
	"context"

	v1 "template/api/predict/v1"
	"template/internal/logic/predict"
)

func (c *ControllerV1) ExportPredictions(ctx context.Context, req *v1.ExportPredictionsReq) (res *v1.ExportPredictionsRes, err error) {
	// 获取预测服务逻辑实例
	predictLogic := predict.NewPredictLogic()

	// 调用逻辑层处理导出预测结果请求
	return predictLogic.ExportPredictions(ctx, req)
}
