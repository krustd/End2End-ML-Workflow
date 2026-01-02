package model

import (
	"context"

	v1 "template/api/model/v1"
	"template/internal/logic/model"
)

func (c *ControllerV1) TrainedModels(ctx context.Context, req *v1.TrainedModelsReq) (res *v1.TrainedModelsRes, err error) {
	modelLogic := model.NewModelLogic()

	return modelLogic.GetTrainedModels(ctx, req)
}
