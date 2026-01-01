package data

import (
	"context"
	"io"
	"strconv"

	"github.com/gogf/gf/v2/errors/gcode"
	"github.com/gogf/gf/v2/errors/gerror"
	"github.com/gogf/gf/v2/frame/g"

	v1 "template/api/data/v1"
	"template/internal/service/http_client"
)

// IDataLogic 数据管理逻辑接口
type IDataLogic interface {
	// UploadData 上传数据
	UploadData(ctx context.Context, req *v1.DataUploadReq) (res *v1.DataUploadRes, err error)

	// GetDataInfo 获取数据信息
	GetDataInfo(ctx context.Context, req *v1.DataInfoReq) (res *v1.DataInfoRes, err error)

	// GetDataPreview 获取数据预览
	GetDataPreview(ctx context.Context, req *v1.DataPreviewReq) (res *v1.DataPreviewRes, err error)

	// ProcessData 处理数据
	ProcessData(ctx context.Context, req *v1.DataProcessReq) (res *v1.DataProcessRes, err error)
}

// sDataLogic 数据管理逻辑实现
type sDataLogic struct {
	client *http_client.Client
}

// NewDataLogic 创建数据管理逻辑实例
func NewDataLogic() IDataLogic {
	return &sDataLogic{
		client: http_client.NewClient(),
	}
}

// UploadData 上传数据
func (s *sDataLogic) UploadData(ctx context.Context, req *v1.DataUploadReq) (res *v1.DataUploadRes, err error) {
	if req.File == nil {
		return nil, gerror.NewCode(gcode.CodeInvalidParameter, "上传文件不能为空")
	}

	// 检查文件类型
	if req.File.Header.Get("Content-Type") != "text/csv" && !isCSVFileName(req.File.Filename) {
		return nil, gerror.NewCode(gcode.CodeInvalidParameter, "只支持CSV文件")
	}

	// 读取文件内容
	file, err := req.File.Open()
	if err != nil {
		return nil, gerror.Wrap(err, "打开上传文件失败")
	}
	defer file.Close()

	fileData, err := io.ReadAll(file)
	if err != nil {
		return nil, gerror.Wrap(err, "读取上传文件失败")
	}

	// 调用Python API上传数据
	result, err := s.client.UploadData(ctx, req.File.Filename, fileData)
	if err != nil {
		g.Log().Errorf(ctx, "上传数据失败: %v", err)
		return nil, gerror.Wrap(err, "上传数据失败")
	}

	// 解析响应
	success, ok := result["success"].(bool)
	if !ok || !success {
		message, _ := result["message"].(string)
		if message == "" {
			message = "上传数据失败"
		}
		return nil, gerror.New(message)
	}

	// 构造响应
	res = &v1.DataUploadRes{
		Success: true,
		Message: "数据上传成功",
	}

	// 如果有数据信息，添加到响应中
	if dataInfo, ok := result["data_info"].(map[string]interface{}); ok {
		res.DataInfo = convertToDataInfo(dataInfo)
	}

	// 如果有预览数据，添加到响应中
	if preview, ok := result["preview"].([]interface{}); ok {
		res.Preview = convertToPreview(preview)
	}

	return res, nil
}

// GetDataInfo 获取数据信息
func (s *sDataLogic) GetDataInfo(ctx context.Context, req *v1.DataInfoReq) (res *v1.DataInfoRes, err error) {
	// 调用Python API获取数据信息
	result, err := s.client.GetDataInfo(ctx)
	if err != nil {
		g.Log().Errorf(ctx, "获取数据信息失败: %v", err)
		return nil, gerror.Wrap(err, "获取数据信息失败")
	}

	// 解析响应
	success, ok := result["success"].(bool)
	if !ok || !success {
		message, _ := result["message"].(string)
		if message == "" {
			message = "获取数据信息失败"
		}
		return nil, gerror.New(message)
	}

	// 获取数据信息
	dataInfoMap, ok := result["data_info"].(map[string]interface{})
	if !ok {
		return nil, gerror.New("数据信息格式错误")
	}

	// 构造响应
	res = &v1.DataInfoRes{
		Success:  true,
		DataInfo: convertToDataInfo(dataInfoMap),
	}

	return res, nil
}

// GetDataPreview 获取数据预览
func (s *sDataLogic) GetDataPreview(ctx context.Context, req *v1.DataPreviewReq) (res *v1.DataPreviewRes, err error) {
	// 设置默认行数
	rows := req.Rows
	if rows <= 0 {
		rows = 20
	}
	if rows > 100 {
		rows = 100
	}

	// 调用Python API获取数据预览
	result, err := s.client.GetDataPreview(ctx, rows)
	if err != nil {
		g.Log().Errorf(ctx, "获取数据预览失败: %v", err)
		return nil, gerror.Wrap(err, "获取数据预览失败")
	}

	// 解析响应
	success, ok := result["success"].(bool)
	if !ok || !success {
		message, _ := result["message"].(string)
		if message == "" {
			message = "获取数据预览失败"
		}
		return nil, gerror.New(message)
	}

	// 获取预览数据
	previewData, ok := result["preview"].([]interface{})
	if !ok {
		return nil, gerror.New("预览数据格式错误")
	}

	// 构造响应
	res = &v1.DataPreviewRes{
		Success: true,
		Preview: convertToPreview(previewData),
	}

	return res, nil
}

// ProcessData 处理数据
func (s *sDataLogic) ProcessData(ctx context.Context, req *v1.DataProcessReq) (res *v1.DataProcessRes, err error) {
	// 调用Python API处理数据
	result, err := s.client.ProcessData(ctx, req.HandleMissing, req.TargetColumn)
	if err != nil {
		g.Log().Errorf(ctx, "处理数据失败: %v", err)
		return nil, gerror.Wrap(err, "处理数据失败")
	}

	// 解析响应
	success, ok := result["success"].(bool)
	if !ok || !success {
		message, _ := result["message"].(string)
		if message == "" {
			message = "处理数据失败"
		}
		return nil, gerror.New(message)
	}

	// 获取处理结果
	featureCount, _ := result["feature_count"].(float64)
	sampleCount, _ := result["sample_count"].(float64)
	targetColumn, _ := result["target_column"].(string)

	// 构造响应
	res = &v1.DataProcessRes{
		Success:      true,
		Message:      "数据处理成功",
		FeatureCount: int(featureCount),
		SampleCount:  int(sampleCount),
		TargetColumn: targetColumn,
	}

	return res, nil
}

// isCSVFileName 检查文件名是否为CSV格式
func isCSVFileName(filename string) bool {
	return len(filename) > 4 && filename[len(filename)-4:] == ".csv"
}

// convertToDataInfo 转换为DataInfo结构
func convertToDataInfo(dataInfoMap map[string]interface{}) v1.DataInfo {
	dataInfo := v1.DataInfo{}

	if fileName, ok := dataInfoMap["file_name"].(string); ok {
		dataInfo.FileName = fileName
	}

	if fileSize, ok := dataInfoMap["file_size"].(float64); ok {
		dataInfo.FileSize = fileSize
	}

	if rowsCount, ok := dataInfoMap["rows_count"].(float64); ok {
		dataInfo.RowsCount = int(rowsCount)
	}

	if columnsCount, ok := dataInfoMap["columns_count"].(float64); ok {
		dataInfo.ColumnsCount = int(columnsCount)
	}

	if columns, ok := dataInfoMap["columns"].([]interface{}); ok {
		dataInfo.Columns = convertToStringSlice(columns)
	}

	if numericColumns, ok := dataInfoMap["numeric_columns"].([]interface{}); ok {
		dataInfo.NumericColumns = convertToStringSlice(numericColumns)
	}

	if categoricalColumns, ok := dataInfoMap["categorical_columns"].([]interface{}); ok {
		dataInfo.CategoricalColumns = convertToStringSlice(categoricalColumns)
	}

	if targetColumn, ok := dataInfoMap["target_column"].(string); ok {
		dataInfo.TargetColumn = targetColumn
	}

	if featureColumns, ok := dataInfoMap["feature_columns"].([]interface{}); ok {
		dataInfo.FeatureColumns = convertToStringSlice(featureColumns)
	}

	return dataInfo
}

// convertToPreview 转换为预览数据
func convertToPreview(previewData []interface{}) []map[string]interface{} {
	preview := make([]map[string]interface{}, 0, len(previewData))

	for _, item := range previewData {
		if row, ok := item.(map[string]interface{}); ok {
			preview = append(preview, row)
		}
	}

	return preview
}

// convertToStringSlice 转换为字符串切片
func convertToStringSlice(slice []interface{}) []string {
	result := make([]string, 0, len(slice))

	for _, item := range slice {
		if str, ok := item.(string); ok {
			result = append(result, str)
		} else {
			// 尝试将其他类型转换为字符串
			switch v := item.(type) {
			case float64:
				result = append(result, strconv.FormatFloat(v, 'f', -1, 64))
			case int:
				result = append(result, strconv.Itoa(v))
			case bool:
				result = append(result, strconv.FormatBool(v))
			default:
				result = append(result, "")
			}
		}
	}

	return result
}
