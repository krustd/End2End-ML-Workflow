package predict

import (
	"context"

	v1 "template/api/predict/v1"
	"template/internal/logic/predict"
)

func (c *ControllerV1) ExportPredictions(ctx context.Context, req *v1.ExportPredictionsReq) (res *v1.ExportPredictionsRes, err error) {
	predictLogic := predict.NewPredictLogic()

	return predictLogic.ExportPredictions(ctx, req)
}
