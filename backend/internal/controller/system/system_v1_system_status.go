package system

import (
	"context"

	v1 "template/api/system/v1"
	"template/internal/logic/system"
)

func (c *ControllerV1) SystemStatus(ctx context.Context, req *v1.SystemStatusReq) (res *v1.SystemStatusRes, err error) {
	// 获取系统管理逻辑实例
	systemLogic := system.NewSystemLogic()

	// 调用逻辑层处理获取系统状态请求
	return systemLogic.GetSystemStatus(ctx, req)
}
