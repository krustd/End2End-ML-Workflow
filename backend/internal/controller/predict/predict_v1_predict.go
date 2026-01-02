package predict

import (
	"context"

	v1 "template/api/predict/v1"
	"template/internal/logic/predict"
)

func (c *ControllerV1) Predict(ctx context.Context, req *v1.PredictReq) (res *v1.PredictRes, err error) {
	predictLogic := predict.NewPredictLogic()

	return predictLogic.Predict(ctx, req)
}
