package bootstrap

import (
	"context"
	"time"

	"github.com/gogf/gf/v2/errors/gerror"
	"github.com/gogf/gf/v2/frame/g"

	"template/internal/service/http_client"
)

// Service 引导服务
type Service struct{}

// New 创建引导服务实例
func New() *Service {
	return &Service{}
}

// InitServices 初始化所有服务
func (s *Service) InitServices(ctx context.Context) error {
	// 初始化 Auth 监听服务
	// auth.InitAuthWatcher(ctx)
	// g.Log().Info(ctx, "Auth 监听服务初始化完成")

	// 测试ml_model连接
	err := s.testMLModelConnection(ctx)
	if err != nil {
		g.Log().Errorf(ctx, "ml_model连接测试失败: %v", err)
		return err
	}
	g.Log().Info(ctx, "ml_model连接测试成功")

	// 可以在这里添加其他服务的初始化
	// 例如：cache.InitCache(ctx)
	//       mq.InitMessageQueue(ctx)

	return nil
}

// testMLModelConnection 测试ml_model连接
func (s *Service) testMLModelConnection(ctx context.Context) error {
	client := http_client.NewClient()

	// 测试基本连接
	g.Log().Info(ctx, "正在测试ml_model基本连接...")

	// 设置超时上下文
	timeoutCtx, cancel := context.WithTimeout(ctx, 10*time.Second)
	defer cancel()

	// 测试系统状态接口
	_, err := client.GetSystemStatus(timeoutCtx)
	if err != nil {
		return gerror.Wrap(err, "无法连接到ml_model服务")
	}

	g.Log().Info(ctx, "ml_model系统状态接口测试成功")

	// 测试其他关键接口
	s.testAPIEndpoints(ctx, client)

	return nil
}

// testAPIEndpoints 测试关键API端点
func (s *Service) testAPIEndpoints(ctx context.Context, client *http_client.Client) {
	// 只测试系统状态接口，这是判断连接是否成功的关键接口
	g.Log().Info(ctx, "ml_model服务连接正常，无需测试其他接口")
}
