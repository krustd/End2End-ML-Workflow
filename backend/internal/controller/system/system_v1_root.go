package system

import (
	"context"

	v1 "template/api/system/v1"
	"template/internal/logic/system"
)

func (c *ControllerV1) Root(ctx context.Context, req *v1.RootReq) (res *v1.RootRes, err error) {
	// 获取系统管理逻辑实例
	systemLogic := system.NewSystemLogic()

	// 调用逻辑层处理根路径请求
	return systemLogic.Root(ctx, req)
}
