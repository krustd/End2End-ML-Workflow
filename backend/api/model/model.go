// =================================================================================
// Code generated and maintained by GoFrame CLI tool. DO NOT EDIT.
// =================================================================================

package model

import (
	"context"

	"template/api/model/v1"
)

type IModelV1 interface {
	ModelTrain(ctx context.Context, req *v1.ModelTrainReq) (res *v1.ModelTrainRes, err error)
	AvailableModels(ctx context.Context, req *v1.AvailableModelsReq) (res *v1.AvailableModelsRes, err error)
	TrainedModels(ctx context.Context, req *v1.TrainedModelsReq) (res *v1.TrainedModelsRes, err error)
	ModelMetrics(ctx context.Context, req *v1.ModelMetricsReq) (res *v1.ModelMetricsRes, err error)
	CompareModels(ctx context.Context, req *v1.CompareModelsReq) (res *v1.CompareModelsRes, err error)
	ModelInfo(ctx context.Context, req *v1.ModelInfoReq) (res *v1.ModelInfoRes, err error)
}
