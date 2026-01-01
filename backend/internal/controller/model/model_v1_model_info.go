package model

import (
	"context"

	v1 "template/api/model/v1"
	"template/internal/logic/model"
)

func (c *ControllerV1) ModelInfo(ctx context.Context, req *v1.ModelInfoReq) (res *v1.ModelInfoRes, err error) {
	// 获取模型管理逻辑实例
	modelLogic := model.NewModelLogic()

	// 调用逻辑层处理获取模型信息请求
	return modelLogic.GetModelInfo(ctx, req)
}
