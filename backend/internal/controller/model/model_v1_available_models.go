package model

import (
	"context"

	v1 "template/api/model/v1"
	"template/internal/logic/model"
)

func (c *ControllerV1) AvailableModels(ctx context.Context, req *v1.AvailableModelsReq) (res *v1.AvailableModelsRes, err error) {
	// 获取模型管理逻辑实例
	modelLogic := model.NewModelLogic()

	// 调用逻辑层处理获取可用模型请求
	return modelLogic.GetAvailableModels(ctx, req)
}
