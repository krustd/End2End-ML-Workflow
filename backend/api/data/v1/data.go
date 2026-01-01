package v1

import (
	"github.com/gogf/gf/v2/frame/g"
	"github.com/gogf/gf/v2/net/ghttp"
)

// DataUploadReq 数据上传请求
type DataUploadReq struct {
	g.Meta `path:"/data/upload" method:"POST" tags:"数据管理" summary:"上传CSV数据文件"`
	File   *ghttp.UploadFile `p:"file" v:"required" dc:"CSV文件"`
}

// DataUploadRes 数据上传响应
type DataUploadRes struct {
	Success  bool                     `json:"success"`
	Message  string                   `json:"message"`
	DataInfo DataInfo                 `json:"data_info,omitempty"`
	Preview  []map[string]interface{} `json:"preview,omitempty"`
}

// DataInfo 数据信息
type DataInfo struct {
	FileName           string   `json:"file_name"`
	FileSize           float64  `json:"file_size"`
	RowsCount          int      `json:"rows_count"`
	ColumnsCount       int      `json:"columns_count"`
	Columns            []string `json:"columns"`
	NumericColumns     []string `json:"numeric_columns"`
	CategoricalColumns []string `json:"categorical_columns"`
	TargetColumn       string   `json:"target_column,omitempty"`
	FeatureColumns     []string `json:"feature_columns,omitempty"`
}

// DataInfoReq 获取数据信息请求
type DataInfoReq struct {
	g.Meta `path:"/data/info" method:"GET" tags:"数据管理" summary:"获取数据信息"`
}

// DataInfoRes 获取数据信息响应
type DataInfoRes struct {
	Success  bool     `json:"success"`
	DataInfo DataInfo `json:"data_info"`
}

// DataPreviewReq 获取数据预览请求
type DataPreviewReq struct {
	g.Meta `path:"/data/preview" method:"GET" tags:"数据管理" summary:"获取数据预览"`
	Rows   int `json:"rows" v:"min:1|max:100" dc:"预览行数，默认20，最大100"`
}

// DataPreviewRes 获取数据预览响应
type DataPreviewRes struct {
	Success bool                     `json:"success"`
	Preview []map[string]interface{} `json:"preview"`
}

// DataProcessReq 数据处理请求
type DataProcessReq struct {
	g.Meta        `path:"/data/process" method:"POST" tags:"数据管理" summary:"处理数据"`
	HandleMissing string `json:"handle_missing" v:"required|in:drop,mean,median,mode" dc:"处理缺失值的方法: drop, mean, median, mode"`
	TargetColumn  string `json:"target_column" dc:"目标列名"`
}

// DataProcessRes 数据处理响应
type DataProcessRes struct {
	Success      bool   `json:"success"`
	Message      string `json:"message"`
	FeatureCount int    `json:"feature_count"`
	SampleCount  int    `json:"sample_count"`
	TargetColumn string `json:"target_column"`
}
