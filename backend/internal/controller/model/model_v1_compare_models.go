package model

import (
	"context"

	v1 "template/api/model/v1"
	"template/internal/logic/model"
)

func (c *ControllerV1) CompareModels(ctx context.Context, req *v1.CompareModelsReq) (res *v1.CompareModelsRes, err error) {
	modelLogic := model.NewModelLogic()

	return modelLogic.CompareModels(ctx, req)
}
