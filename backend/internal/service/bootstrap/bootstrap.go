package bootstrap

import (
	"context"
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

	// 可以在这里添加其他服务的初始化
	// 例如：cache.InitCache(ctx)
	//       mq.InitMessageQueue(ctx)

	return nil
}
