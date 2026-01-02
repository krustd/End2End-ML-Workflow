package model

import (
	"context"

	v1 "template/api/model/v1"
	"template/internal/logic/model"
)

func (c *ControllerV1) ModelTrain(ctx context.Context, req *v1.ModelTrainReq) (res *v1.ModelTrainRes, err error) {
	modelLogic := model.NewModelLogic()

	return modelLogic.TrainModel(ctx, req)
}
