// =================================================================================
// Code generated and maintained by GoFrame CLI tool. DO NOT EDIT.
// =================================================================================

package system

import (
	"context"

	"template/api/system/v1"
)

type ISystemV1 interface {
	SystemStatus(ctx context.Context, req *v1.SystemStatusReq) (res *v1.SystemStatusRes, err error)
	Root(ctx context.Context, req *v1.RootReq) (res *v1.RootRes, err error)
}
