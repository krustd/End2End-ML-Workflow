package hello

import (
	"context"

	v1 "template/api/hello/v1"
)

func (c *ControllerV1) Hello(ctx context.Context, req *v1.HelloReq) (res *v1.HelloRes, err error) {
	return &v1.HelloRes{
		Reply: "Hello World!",
	}, nil
}
