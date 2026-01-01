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
	logicRes, err := dataLogic.GetDataPreview(ctx, req)
	if err != nil {
		return nil, err
	}

	// 构造BaseRes格式的响应
	res = &v1.DataPreviewRes{
		Success: logicRes.Success,
		Preview: logicRes.Preview,
	}

	return res, nil
}
