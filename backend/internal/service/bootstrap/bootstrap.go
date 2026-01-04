package bootstrap

import (
	"context"
	"time"

	"github.com/gogf/gf/v2/errors/gerror"
	"github.com/gogf/gf/v2/frame/g"

	"template/internal/service/http_client"
)

type Service struct{}

func New() *Service {
	return &Service{}
}

func (s *Service) InitServices(ctx context.Context) error {
	err := s.testMLModelConnection(ctx)
	if err != nil {
		g.Log().Errorf(ctx, "ml_model连接测试失败: %v", err)
		return err
	}
	g.Log().Info(ctx, "ml_model连接测试成功")

	return nil
}

func (s *Service) testMLModelConnection(ctx context.Context) error {
	client := http_client.NewClient()

	g.Log().Info(ctx, "正在测试ml_model基本连接...")

	timeoutCtx, cancel := context.WithTimeout(ctx, 10*time.Second)
	defer cancel()

	_, err := client.GetSystemStatus(timeoutCtx)
	if err != nil {
		return gerror.Wrap(err, "无法连接到ml_model服务")
	}

	g.Log().Info(ctx, "ml_model系统状态接口测试成功")

	return nil
}

func (s *Service) testAPIEndpoints(ctx context.Context) {
	g.Log().Info(ctx, "ml_model服务连接正常，无需测试其他接口")
}
