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
	logicRes, err := dataLogic.ProcessData(ctx, req)
	if err != nil {
		return nil, err
	}

	// 构造BaseRes格式的响应
	res = &v1.DataProcessRes{
		Success:      logicRes.Success,
		Message:      logicRes.Message,
		FeatureCount: logicRes.FeatureCount,
		SampleCount:  logicRes.SampleCount,
		TargetColumn: logicRes.TargetColumn,
	}

	return res, nil
}
