package model

import (
	"context"

	v1 "template/api/model/v1"
	"template/internal/logic/model"
)

func (c *ControllerV1) CompareModels(ctx context.Context, req *v1.CompareModelsReq) (res *v1.CompareModelsRes, err error) {
	// 获取模型管理逻辑实例
	modelLogic := model.NewModelLogic()

	// 调用逻辑层处理模型比较请求
	return modelLogic.CompareModels(ctx, req)
}
