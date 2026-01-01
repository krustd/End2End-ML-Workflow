package predict

import (
	"context"

	v1 "template/api/predict/v1"
	"template/internal/logic/predict"
)

func (c *ControllerV1) Predict(ctx context.Context, req *v1.PredictReq) (res *v1.PredictRes, err error) {
	// 获取预测服务逻辑实例
	predictLogic := predict.NewPredictLogic()

	// 调用逻辑层处理预测请求
	return predictLogic.Predict(ctx, req)
}
