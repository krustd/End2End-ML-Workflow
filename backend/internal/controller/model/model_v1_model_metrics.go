package model

import (
	"context"

	v1 "template/api/model/v1"
	"template/internal/logic/model"
)

func (c *ControllerV1) ModelMetrics(ctx context.Context, req *v1.ModelMetricsReq) (res *v1.ModelMetricsRes, err error) {
	// 获取模型管理逻辑实例
	modelLogic := model.NewModelLogic()

	// 调用逻辑层处理获取模型指标请求
	return modelLogic.GetModelMetrics(ctx, req)
}
