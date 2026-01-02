package data

import (
	"context"

	v1 "template/api/data/v1"
	"template/internal/logic/data"
)

func (c *ControllerV1) DataInfo(ctx context.Context, req *v1.DataInfoReq) (res *v1.DataInfoRes, err error) {
	dataLogic := data.NewDataLogic()

	logicRes, err := dataLogic.GetDataInfo(ctx, req)
	if err != nil {
		return nil, err
	}

	res = &v1.DataInfoRes{
		Success:  logicRes.Success,
		DataInfo: logicRes.DataInfo,
	}

	return res, nil
}
