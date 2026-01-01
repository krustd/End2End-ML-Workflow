package middleware

import (
	"mime"
	"net/http"

	"github.com/gogf/gf/v2/errors/gcode"
	"github.com/gogf/gf/v2/errors/gerror"
	"github.com/gogf/gf/v2/frame/g"
	"github.com/gogf/gf/v2/net/ghttp"
	"github.com/gogf/gf/v2/os/gctx"
)

type BaseRes struct {
	Code    int         `json:"code"`
	Data    interface{} `json:"data"`
	Message string      `json:"message"`
	TraceID string      `json:"trace_id,omitempty"`
}

var streamContentTypes = map[string]struct{}{
	"text/event-stream":         {},
	"application/octet-stream":  {},
	"multipart/x-mixed-replace": {},
	"application/grpc":          {},
}

func ResponseHandler(r *ghttp.Request) {
	r.Middleware.Next()

	if r.Response.BufferLength() > 0 || r.Response.Writer.BytesWritten() > 0 {
		return
	}

	mediaType, _, _ := mime.ParseMediaType(r.Response.Header().Get("Content-Type"))
	if _, ok := streamContentTypes[mediaType]; ok {
		return
	}

	var (
		err             = r.GetError()
		res             = r.GetHandlerResponse()
		code gcode.Code = gcode.CodeOK
		msg             = "操作成功"
		data interface{}
	)

	if err != nil {
		r.Response.Status = http.StatusOK
		code = gerror.Code(err)
		if code == gcode.CodeNil {
			code = gcode.CodeInternalError
		}

		if code == gcode.CodeInternalError {
			g.Log().Error(r.Context(), err)
			msg = "系统服务异常，请稍后重试"
		} else {
			// 记录错误日志，但不返回详细错误消息给前端
			g.Log().Errorf(r.Context(), "Error: %v", err)
			msg = err.Error()
		}
		data = g.Map{}
	} else {
		if r.Response.Status > 0 && r.Response.Status != http.StatusOK {
			originalStatus := r.Response.Status
			r.Response.Status = http.StatusOK

			switch originalStatus {
			case http.StatusNotFound:
				code = gcode.CodeNotFound
				msg = "资源未找到"
			case http.StatusForbidden:
				code = gcode.CodeNotAuthorized
				msg = "无权访问"
			default:
				code = gcode.CodeUnknown
				msg = "未知错误"
			}
			data = g.Map{}
		} else {
			code = gcode.CodeOK
			data = res
			if data == nil {
				data = g.Map{}
			}
		}
	}

	resp := BaseRes{
		Code:    code.Code(),
		Message: msg,
		Data:    data,
	}

	if r.Header.Get("X-Debug") != "" {
		resp.TraceID = gctx.CtxId(r.Context())
	}

	r.Response.WriteJson(resp)
}
