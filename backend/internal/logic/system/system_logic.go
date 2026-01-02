package system

import (
	"context"

	"github.com/gogf/gf/v2/errors/gerror"
	"github.com/gogf/gf/v2/frame/g"

	v1 "template/api/system/v1"
	"template/internal/service/http_client"
)

type ISystemLogic interface {
	GetSystemStatus(ctx context.Context, req *v1.SystemStatusReq) (res *v1.SystemStatusRes, err error)
	Root(ctx context.Context, req *v1.RootReq) (res *v1.RootRes, err error)
}

type sSystemLogic struct {
	client *http_client.Client
}

func NewSystemLogic() ISystemLogic {
	return &sSystemLogic{
		client: http_client.NewClient(),
	}
}
func (s *sSystemLogic) GetSystemStatus(ctx context.Context, req *v1.SystemStatusReq) (res *v1.SystemStatusRes, err error) {
	result, err := s.client.GetSystemStatus(ctx)
	if err != nil {
		g.Log().Errorf(ctx, "获取系统状态失败: %v", err)
		return nil, gerror.Wrap(err, "获取系统状态失败")
	}

	success, ok := result["success"].(bool)
	if !ok || !success {
		message, _ := result["message"].(string)
		if message == "" {
			message = "获取系统状态失败"
		}
		return nil, gerror.New(message)
	}

	status, ok := result["status"].(map[string]interface{})
	if !ok {
		return nil, gerror.New("系统状态格式错误")
	}

	res = &v1.SystemStatusRes{
		Success: success,
		Status:  status,
	}

	return res, nil
}
func (s *sSystemLogic) Root(ctx context.Context, req *v1.RootReq) (res *v1.RootRes, err error) {
	res = &v1.RootRes{
		Message: "机器学习数据分析与统计系统API",
		Version: "1.0.0",
		Status:  "running",
	}

	return res, nil
}
