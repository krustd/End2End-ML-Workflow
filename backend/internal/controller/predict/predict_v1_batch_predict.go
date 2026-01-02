package predict

import (
	"context"

	v1 "template/api/predict/v1"
	"template/internal/logic/predict"
)

func (c *ControllerV1) BatchPredict(ctx context.Context, req *v1.BatchPredictReq) (res *v1.BatchPredictRes, err error) {
	predictLogic := predict.NewPredictLogic()

	return predictLogic.BatchPredict(ctx, req)
}
