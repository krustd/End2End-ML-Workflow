package data

import (
	"context"

	v1 "template/api/data/v1"
	"template/internal/logic/data"
)

func (c *ControllerV1) DataPreview(ctx context.Context, req *v1.DataPreviewReq) (res *v1.DataPreviewRes, err error) {
	dataLogic := data.NewDataLogic()

	logicRes, err := dataLogic.GetDataPreview(ctx, req)
	if err != nil {
		return nil, err
	}

	res = &v1.DataPreviewRes{
		Success: logicRes.Success,
		Preview: logicRes.Preview,
	}

	return res, nil
}
