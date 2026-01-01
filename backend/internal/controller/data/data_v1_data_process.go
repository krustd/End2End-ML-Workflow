package data

import (
	"context"

	v1 "template/api/data/v1"
	"template/internal/logic/data"
)

func (c *ControllerV1) DataProcess(ctx context.Context, req *v1.DataProcessReq) (res *v1.DataProcessRes, err error) {
	// 获取数据管理逻辑实例
	dataLogic := data.NewDataLogic()

	// 调用逻辑层处理数据处理请求
	return dataLogic.ProcessData(ctx, req)
}
