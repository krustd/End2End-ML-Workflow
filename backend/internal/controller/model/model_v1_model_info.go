package model

import (
	"context"

	v1 "template/api/model/v1"
	"template/internal/logic/model"
)

func (c *ControllerV1) ModelInfo(ctx context.Context, req *v1.ModelInfoReq) (res *v1.ModelInfoRes, err error) {
	modelLogic := model.NewModelLogic()

	return modelLogic.GetModelInfo(ctx, req)
}
