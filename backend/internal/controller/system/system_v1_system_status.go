package system

import (
	"context"

	v1 "template/api/system/v1"
	"template/internal/logic/system"
)

func (c *ControllerV1) SystemStatus(ctx context.Context, req *v1.SystemStatusReq) (res *v1.SystemStatusRes, err error) {
	systemLogic := system.NewSystemLogic()

	logicRes, err := systemLogic.GetSystemStatus(ctx, req)
	if err != nil {
		return nil, err
	}

	res = &v1.SystemStatusRes{
		Success: logicRes.Success,
		Status:  logicRes.Status,
	}

	return res, nil
}
