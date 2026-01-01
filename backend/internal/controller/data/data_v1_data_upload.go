package data

import (
	"context"

	v1 "template/api/data/v1"
	"template/internal/logic/data"
)

func (c *ControllerV1) DataUpload(ctx context.Context, req *v1.DataUploadReq) (res *v1.DataUploadRes, err error) {
	// 获取数据管理逻辑实例
	dataLogic := data.NewDataLogic()

	// 调用逻辑层处理上传数据请求
	return dataLogic.UploadData(ctx, req)
}
