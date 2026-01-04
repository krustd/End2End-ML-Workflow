package data

import (
	"context"
	"io"
	"strconv"

	"github.com/gogf/gf/v2/errors/gcode"
	"github.com/gogf/gf/v2/errors/gerror"
	"github.com/gogf/gf/v2/frame/g"
	"github.com/gogf/gf/v2/net/ghttp"

	v1 "template/api/data/v1"
	"template/internal/service/http_client"
)

type IDataLogic interface {
	UploadData(ctx context.Context, file *ghttp.UploadFile) (res *v1.DataUploadRes, err error)
	GetDataInfo(ctx context.Context, req *v1.DataInfoReq) (res *v1.DataInfoRes, err error)
	GetDataPreview(ctx context.Context, req *v1.DataPreviewReq) (res *v1.DataPreviewRes, err error)
	ProcessData(ctx context.Context, req *v1.DataProcessReq) (res *v1.DataProcessRes, err error)
}

type sDataLogic struct {
	client *http_client.Client
}

func NewDataLogic() IDataLogic {
	return &sDataLogic{
		client: http_client.NewClient(),
	}
}
func (s *sDataLogic) UploadData(ctx context.Context, file *ghttp.UploadFile) (res *v1.DataUploadRes, err error) {
	if file == nil {
		return nil, gerror.NewCode(gcode.CodeInvalidParameter, "上传文件不能为空")
	}

	if file.Header.Get("Content-Type") != "text/csv" && !isCSVFileName(file.Filename) {
		return nil, gerror.NewCode(gcode.CodeInvalidParameter, "只支持CSV文件")
	}

	const maxFileSize = 50 * 1024 * 1024
	if file.Size > maxFileSize {
		return nil, gerror.NewCodef(gcode.CodeInvalidParameter, "文件大小超过限制，最大允许%dMB", maxFileSize/(1024*1024))
	}

	fileObj, err := file.Open()
	if err != nil {
		return nil, gerror.Wrap(err, "打开上传文件失败")
	}
	defer fileObj.Close()

	fileData, err := io.ReadAll(fileObj)
	if err != nil {
		return nil, gerror.Wrap(err, "读取上传文件失败")
	}

	result, err := s.client.UploadData(ctx, file.Filename, fileData)
	if err != nil {
		g.Log().Errorf(ctx, "上传数据失败: %v", err)
		return nil, gerror.Wrap(err, "上传数据失败")
	}

	success, ok := result["success"].(bool)
	if !ok || !success {
		message, _ := result["message"].(string)
		if message == "" {
			message = "上传数据失败"
		}
		return nil, gerror.New(message)
	}

	res = &v1.DataUploadRes{
		Success: true,
		Message: "数据上传成功",
	}

	if dataInfo, ok := result["data_info"].(map[string]interface{}); ok {
		res.DataInfo = convertToDataInfo(dataInfo)
	}

	if preview, ok := result["preview"].([]interface{}); ok {
		res.Preview = convertToPreview(preview)
	}

	return res, nil
}
func (s *sDataLogic) GetDataInfo(ctx context.Context, req *v1.DataInfoReq) (res *v1.DataInfoRes, err error) {
	result, err := s.client.GetDataInfo(ctx)
	if err != nil {
		g.Log().Errorf(ctx, "获取数据信息失败: %v", err)
		return nil, gerror.Wrap(err, "获取数据信息失败")
	}

	success, ok := result["success"].(bool)
	if !ok || !success {
		message, _ := result["message"].(string)
		if message == "" {
			message = "获取数据信息失败"
		}
		return nil, gerror.New(message)
	}

	dataInfoMap, ok := result["data_info"].(map[string]interface{})
	if !ok {
		return nil, gerror.New("数据信息格式错误")
	}

	res = &v1.DataInfoRes{
		Success:  true,
		DataInfo: convertToDataInfo(dataInfoMap),
	}

	return res, nil
}
func (s *sDataLogic) GetDataPreview(ctx context.Context, req *v1.DataPreviewReq) (res *v1.DataPreviewRes, err error) {
	rows := req.Rows
	if rows <= 0 {
		rows = 20
	}
	if rows > 100 {
		rows = 100
	}

	result, err := s.client.GetDataPreview(ctx, rows)
	if err != nil {
		g.Log().Errorf(ctx, "获取数据预览失败: %v", err)
		return nil, gerror.Wrap(err, "获取数据预览失败")
	}

	success, ok := result["success"].(bool)
	if !ok || !success {
		message, _ := result["message"].(string)
		if message == "" {
			message = "获取数据预览失败"
		}
		return nil, gerror.New(message)
	}

	previewData, ok := result["preview"].([]interface{})
	if !ok {
		return nil, gerror.New("预览数据格式错误")
	}

	res = &v1.DataPreviewRes{
		Success: true,
		Preview: convertToPreview(previewData),
	}

	return res, nil
}
func (s *sDataLogic) ProcessData(ctx context.Context, req *v1.DataProcessReq) (res *v1.DataProcessRes, err error) {
	result, err := s.client.ProcessData(ctx, req.HandleMissing, req.TargetColumn)
	if err != nil {
		g.Log().Errorf(ctx, "处理数据失败: %v", err)
		return nil, gerror.Wrap(err, "处理数据失败")
	}

	success, ok := result["success"].(bool)
	if !ok || !success {
		message, _ := result["message"].(string)
		if message == "" {
			message = "处理数据失败"
		}
		return nil, gerror.New(message)
	}

	featureCount, _ := result["feature_count"].(float64)
	sampleCount, _ := result["sample_count"].(float64)
	targetColumn, _ := result["target_column"].(string)

	res = &v1.DataProcessRes{
		Success:      true,
		Message:      "数据处理成功",
		FeatureCount: int(featureCount),
		SampleCount:  int(sampleCount),
		TargetColumn: targetColumn,
	}

	return res, nil
}
func isCSVFileName(filename string) bool {
	return len(filename) > 4 && filename[len(filename)-4:] == ".csv"
}

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

func convertToPreview(previewData []interface{}) []map[string]interface{} {
	preview := make([]map[string]interface{}, 0, len(previewData))

	for _, item := range previewData {
		if row, ok := item.(map[string]interface{}); ok {
			preview = append(preview, row)
		}
	}

	return preview
}

func convertToStringSlice(slice []interface{}) []string {
	result := make([]string, 0, len(slice))

	for _, item := range slice {
		if str, ok := item.(string); ok {
			result = append(result, str)
		} else {
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
