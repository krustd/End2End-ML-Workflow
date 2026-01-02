package templateGRPC

import (
	"context"
	v1 "template/api/grpc/templateGRPC/v1"

	"github.com/gogf/gf/contrib/rpc/grpcx/v2"
)

type Controller struct {
	v1.UnimplementedHelloServer
}

func Register(s *grpcx.GrpcServer) {
	v1.RegisterHelloServer(s.Server, &Controller{})
}

func (*Controller) Say(ctx context.Context, req *v1.SayReq) (res *v1.SayRes, err error) {
	return &v1.SayRes{
		Content: "Hello " + req.Content,
	}, err
}
