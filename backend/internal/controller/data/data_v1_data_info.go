package data

import (
	"context"

	v1 "template/api/data/v1"
	"template/internal/logic/data"
)

func (c *ControllerV1) DataInfo(ctx context.Context, req *v1.DataInfoReq) (res *v1.DataInfoRes, err error) {
	// 获取数据管理逻辑实例
	dataLogic := data.NewDataLogic()

	// 调用逻辑层处理获取数据信息请求
	return dataLogic.GetDataInfo(ctx, req)
}
