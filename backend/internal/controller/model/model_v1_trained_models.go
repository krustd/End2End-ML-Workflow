package model

import (
	"context"

	v1 "template/api/model/v1"
	"template/internal/logic/model"
)

func (c *ControllerV1) TrainedModels(ctx context.Context, req *v1.TrainedModelsReq) (res *v1.TrainedModelsRes, err error) {
	// 获取模型管理逻辑实例
	modelLogic := model.NewModelLogic()

	// 调用逻辑层处理获取已训练模型请求
	return modelLogic.GetTrainedModels(ctx, req)
}
