package predict

import (
	"context"

	v1 "template/api/predict/v1"
	"template/internal/logic/predict"
)

func (c *ControllerV1) BatchPredict(ctx context.Context, req *v1.BatchPredictReq) (res *v1.BatchPredictRes, err error) {
	// 获取预测服务逻辑实例
	predictLogic := predict.NewPredictLogic()

	// 调用逻辑层处理批量预测请求
	return predictLogic.BatchPredict(ctx, req)
}
