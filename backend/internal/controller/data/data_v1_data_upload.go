package data

import (
	"context"

	v1 "template/api/data/v1"
	"template/internal/logic/data"

	"github.com/gogf/gf/v2/errors/gcode"
	"github.com/gogf/gf/v2/errors/gerror"
)

func (c *ControllerV1) DataUpload(ctx context.Context, req *v1.DataUploadReq) (res *v1.DataUploadRes, err error) {
	// 获取上传的文件
	file := req.File

	// 检查文件是否有效
	if file == nil {
		return nil, gerror.NewCode(gcode.CodeInvalidParameter, "上传文件不能为空")
	}

	// 获取数据管理逻辑实例
	dataLogic := data.NewDataLogic()

	// 调用逻辑层处理上传数据请求
	logicRes, err := dataLogic.UploadData(ctx, file)
	if err != nil {
		return nil, err
	}

	// 构造BaseRes格式的响应，确保不包含任何multipart.FileHeader类型的数据
	res = &v1.DataUploadRes{
		Success:  logicRes.Success,
		Message:  logicRes.Message,
		DataInfo: logicRes.DataInfo,
		Preview:  logicRes.Preview,
	}

	return res, nil
}
