// =================================================================================
// Code generated and maintained by GoFrame CLI tool. DO NOT EDIT.
// =================================================================================

package predict

import (
	"context"

	"template/api/predict/v1"
)

type IPredictV1 interface {
	Predict(ctx context.Context, req *v1.PredictReq) (res *v1.PredictRes, err error)
	BatchPredict(ctx context.Context, req *v1.BatchPredictReq) (res *v1.BatchPredictRes, err error)
	ExportPredictions(ctx context.Context, req *v1.ExportPredictionsReq) (res *v1.ExportPredictionsRes, err error)
}
