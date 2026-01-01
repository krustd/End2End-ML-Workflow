package v1

import (
	"github.com/gogf/gf/v2/frame/g"
)

// SystemStatusReq 获取系统状态请求
type SystemStatusReq struct {
	g.Meta `path:"/system/status" method:"GET" tags:"系统管理" summary:"获取系统状态"`
}

// SystemStatusRes 获取系统状态响应
type SystemStatusRes struct {
	Success bool                   `json:"success"`
	Status  map[string]interface{} `json:"status"`
}

// RootReq 根路径请求
type RootReq struct {
	g.Meta `path:"/" method:"GET" tags:"系统管理" summary:"根路径，返回API信息"`
}

// RootRes 根路径响应
type RootRes struct {
	Message string `json:"message"`
	Version string `json:"version"`
	Status  string `json:"status"`
}
