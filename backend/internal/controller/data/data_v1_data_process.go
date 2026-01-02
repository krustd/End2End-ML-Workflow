package data

import (
	"context"

	v1 "template/api/data/v1"
	"template/internal/logic/data"
)

func (c *ControllerV1) DataProcess(ctx context.Context, req *v1.DataProcessReq) (res *v1.DataProcessRes, err error) {
	dataLogic := data.NewDataLogic()

	logicRes, err := dataLogic.ProcessData(ctx, req)
	if err != nil {
		return nil, err
	}

	res = &v1.DataProcessRes{
		Success:      logicRes.Success,
		Message:      logicRes.Message,
		FeatureCount: logicRes.FeatureCount,
		SampleCount:  logicRes.SampleCount,
		TargetColumn: logicRes.TargetColumn,
	}

	return res, nil
}
