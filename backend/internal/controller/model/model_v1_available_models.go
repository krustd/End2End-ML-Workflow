package model

import (
	"context"

	v1 "template/api/model/v1"
	"template/internal/logic/model"
)

func (c *ControllerV1) AvailableModels(ctx context.Context, req *v1.AvailableModelsReq) (res *v1.AvailableModelsRes, err error) {
	modelLogic := model.NewModelLogic()

	return modelLogic.GetAvailableModels(ctx, req)
}
