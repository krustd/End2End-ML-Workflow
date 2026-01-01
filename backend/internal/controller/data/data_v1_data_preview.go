package data

import (
	"context"

	v1 "template/api/data/v1"
	"template/internal/logic/data"
)

func (c *ControllerV1) DataPreview(ctx context.Context, req *v1.DataPreviewReq) (res *v1.DataPreviewRes, err error) {
	// 获取数据管理逻辑实例
	dataLogic := data.NewDataLogic()

	// 调用逻辑层处理获取数据预览请求
	return dataLogic.GetDataPreview(ctx, req)
}
