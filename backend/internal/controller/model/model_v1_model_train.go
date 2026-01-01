package model

import (
	"context"

	v1 "template/api/model/v1"
	"template/internal/logic/model"
)

func (c *ControllerV1) ModelTrain(ctx context.Context, req *v1.ModelTrainReq) (res *v1.ModelTrainRes, err error) {
	// 获取模型管理逻辑实例
	modelLogic := model.NewModelLogic()

	// 调用逻辑层处理模型训练请求
	return modelLogic.TrainModel(ctx, req)
}
