// =================================================================================
// Code generated and maintained by GoFrame CLI tool. DO NOT EDIT.
// =================================================================================

package data

import (
	"context"

	"template/api/data/v1"
)

type IDataV1 interface {
	DataUpload(ctx context.Context, req *v1.DataUploadReq) (res *v1.DataUploadRes, err error)
	DataInfo(ctx context.Context, req *v1.DataInfoReq) (res *v1.DataInfoRes, err error)
	DataPreview(ctx context.Context, req *v1.DataPreviewReq) (res *v1.DataPreviewRes, err error)
	DataProcess(ctx context.Context, req *v1.DataProcessReq) (res *v1.DataProcessRes, err error)
}
