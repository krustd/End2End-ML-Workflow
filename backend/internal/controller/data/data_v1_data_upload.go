package data

import (
	"context"

	v1 "template/api/data/v1"
	"template/internal/logic/data"

	"github.com/gogf/gf/v2/errors/gcode"
	"github.com/gogf/gf/v2/errors/gerror"
)

func (c *ControllerV1) DataUpload(ctx context.Context, req *v1.DataUploadReq) (res *v1.DataUploadRes, err error) {
	file := req.File

	if file == nil {
		return nil, gerror.NewCode(gcode.CodeInvalidParameter, "上传文件不能为空")
	}

	dataLogic := data.NewDataLogic()

	logicRes, err := dataLogic.UploadData(ctx, file)
	if err != nil {
		return nil, err
	}

	res = &v1.DataUploadRes{
		Success:  logicRes.Success,
		Message:  logicRes.Message,
		DataInfo: logicRes.DataInfo,
		Preview:  logicRes.Preview,
	}

	return res, nil
}
