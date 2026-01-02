package system

import (
	"context"

	v1 "template/api/system/v1"
	"template/internal/logic/system"
)

func (c *ControllerV1) Root(ctx context.Context, req *v1.RootReq) (res *v1.RootRes, err error) {
	systemLogic := system.NewSystemLogic()

	return systemLogic.Root(ctx, req)
}
