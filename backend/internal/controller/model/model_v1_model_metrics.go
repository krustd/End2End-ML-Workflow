package model

import (
	"context"

	v1 "template/api/model/v1"
	"template/internal/logic/model"
)

func (c *ControllerV1) ModelMetrics(ctx context.Context, req *v1.ModelMetricsReq) (res *v1.ModelMetricsRes, err error) {
	modelLogic := model.NewModelLogic()

	return modelLogic.GetModelMetrics(ctx, req)
}
