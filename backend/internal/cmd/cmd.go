package cmd

import (
	"context"

	"github.com/gogf/gf/v2/frame/g"
	"github.com/gogf/gf/v2/net/ghttp"
	"github.com/gogf/gf/v2/os/gcmd"

	"template/internal/controller/data"
	"template/internal/controller/hello"
	"template/internal/controller/model"
	"template/internal/controller/predict"
	"template/internal/controller/system"
	"template/internal/middleware"
	"template/internal/service/bootstrap"
)

var (
	Main = gcmd.Command{
		Name:  "main",
		Usage: "main",
		Brief: "start http server",
		Func: func(ctx context.Context, parser *gcmd.Parser) (err error) {
			// 初始化所有服务
			bootstrapService := bootstrap.New()
			err = bootstrapService.InitServices(ctx)
			if err != nil {
				g.Log().Fatalf(ctx, "服务初始化失败: %v", err)
			}

			s := g.Server()
			s.Group("/", func(group *ghttp.RouterGroup) {
				// group.Middleware(ghttp.MiddlewareHandlerResponse)
				group.Middleware(ghttp.MiddlewareCORS)
				group.Middleware(middleware.ResponseHandler)
				group.GET("/health", func(r *ghttp.Request) {
					r.Response.Write("ok")
				})
				group.Bind(
					data.NewV1(),
					hello.NewV1(),
					model.NewV1(),
					predict.NewV1(),
					system.NewV1(),
				)
			})

			s.Run()
			return nil
		},
	}
)
