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
	logicRes, err := systemLogic.GetSystemStatus(ctx, req)
	if err != nil {
		return nil, err
	}

	// 构造BaseRes格式的响应
	res = &v1.SystemStatusRes{
		Success: logicRes.Success,
		Status:  logicRes.Status,
	}

	return res, nil
}
