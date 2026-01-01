package system

import (
	"context"

	"github.com/gogf/gf/v2/errors/gerror"
	"github.com/gogf/gf/v2/frame/g"

	v1 "template/api/system/v1"
	"template/internal/service/http_client"
)

// ISystemLogic 系统管理逻辑接口
type ISystemLogic interface {
	// GetSystemStatus 获取系统状态
	GetSystemStatus(ctx context.Context, req *v1.SystemStatusReq) (res *v1.SystemStatusRes, err error)

	// Root 根路径，返回API信息
	Root(ctx context.Context, req *v1.RootReq) (res *v1.RootRes, err error)
}

// sSystemLogic 系统管理逻辑实现
type sSystemLogic struct {
	client *http_client.Client
}

// NewSystemLogic 创建系统管理逻辑实例
func NewSystemLogic() ISystemLogic {
	return &sSystemLogic{
		client: http_client.NewClient(),
	}
}

// GetSystemStatus 获取系统状态
func (s *sSystemLogic) GetSystemStatus(ctx context.Context, req *v1.SystemStatusReq) (res *v1.SystemStatusRes, err error) {
	// 调用Python API获取系统状态
	status, err := s.client.GetSystemStatus(ctx)
	if err != nil {
		g.Log().Errorf(ctx, "获取系统状态失败: %v", err)
		return nil, gerror.Wrap(err, "获取系统状态失败")
	}

	// 构造响应
	res = &v1.SystemStatusRes{
		Success: true,
		Status:  status,
	}

	return res, nil
}

// Root 根路径，返回API信息
func (s *sSystemLogic) Root(ctx context.Context, req *v1.RootReq) (res *v1.RootRes, err error) {
	// 构造响应
	res = &v1.RootRes{
		Message: "机器学习数据分析与统计系统API",
		Version: "1.0.0",
		Status:  "running",
	}

	return res, nil
}
