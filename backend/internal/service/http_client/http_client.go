package http_client

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"mime/multipart"
	"net/http"
	"time"

	"github.com/gogf/gf/v2/errors/gcode"
	"github.com/gogf/gf/v2/errors/gerror"
	"github.com/gogf/gf/v2/frame/g"
)

const (
	PythonAPIHost = "http://localhost:8000"
)

type PythonAPIConfig struct {
	Host    string `yaml:"host"`
	Port    int    `yaml:"port"`
	Timeout int    `yaml:"timeout"`
	Debug   bool   `yaml:"debug"`
}

func GetPythonAPIConfig(ctx context.Context) (*PythonAPIConfig, error) {
	config := &PythonAPIConfig{
		Host:    "localhost",
		Port:    8000,
		Timeout: 30,
		Debug:   false,
	}

	if err := g.Cfg().MustGet(ctx, "python_api").Struct(config); err != nil {
		g.Log().Warningf(ctx, "读取Python API配置失败，使用默认配置: %v", err)
	}

	return config, nil
}

type Client struct {
	httpClient *http.Client
	baseURL    string
}

func NewClient() *Client {
	ctx := context.Background()
	config, err := GetPythonAPIConfig(ctx)
	if err != nil {
		g.Log().Warningf(ctx, "获取Python API配置失败，使用默认配置: %v", err)
		config = &PythonAPIConfig{
			Host:    "localhost",
			Port:    8000,
			Timeout: 30,
			Debug:   false,
		}
	}

	return &Client{
		httpClient: &http.Client{
			Timeout: time.Duration(config.Timeout) * time.Second,
		},
		baseURL: fmt.Sprintf("http://%s:%d", config.Host, config.Port),
	}
}

func (c *Client) doRequest(ctx context.Context, method, endpoint string, headers map[string]string, body io.Reader) ([]byte, error) {
	url := c.baseURL + endpoint

	req, err := http.NewRequestWithContext(ctx, method, url, body)
	if err != nil {
		return nil, gerror.Wrapf(err, "创建请求失败: %s %s", method, endpoint)
	}

	for key, value := range headers {
		req.Header.Set(key, value)
	}

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return nil, gerror.Wrapf(err, "请求失败: %s %s", method, endpoint)
	}
	defer resp.Body.Close()

	respBody, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, gerror.Wrapf(err, "读取响应失败: %s %s", method, endpoint)
	}

	if resp.StatusCode >= 400 {
		return nil, gerror.NewCodef(gcode.CodeInternalError, "请求错误: %s %s, 状态码: %d, 响应: %s",
			method, endpoint, resp.StatusCode, string(respBody))
	}

	return respBody, nil
}

func (c *Client) Get(ctx context.Context, endpoint string, headers map[string]string) ([]byte, error) {
	return c.doRequest(ctx, "GET", endpoint, headers, nil)
}

func (c *Client) Post(ctx context.Context, endpoint string, headers map[string]string, data interface{}) ([]byte, error) {
	var body io.Reader

	if data != nil {
		switch v := data.(type) {
		case []byte:
			body = bytes.NewReader(v)
		case *bytes.Buffer:
			body = v
		default:
			jsonData, err := json.Marshal(data)
			if err != nil {
				return nil, gerror.Wrap(err, "序列化请求数据失败")
			}
			body = bytes.NewReader(jsonData)
		}
	}

	if headers == nil {
		headers = make(map[string]string)
	}
	if _, ok := headers["Content-Type"]; !ok {
		headers["Content-Type"] = "application/json"
	}

	return c.doRequest(ctx, "POST", endpoint, headers, body)
}

func (c *Client) PostMultipart(ctx context.Context, endpoint string, fieldName, fileName string, fileData []byte, extraFields map[string]string) ([]byte, error) {
	var buf bytes.Buffer
	writer := multipart.NewWriter(&buf)

	part, err := writer.CreateFormFile(fieldName, fileName)
	if err != nil {
		return nil, gerror.Wrap(err, "创建表单文件字段失败")
	}
	_, err = part.Write(fileData)
	if err != nil {
		return nil, gerror.Wrap(err, "写入文件数据失败")
	}

	for key, value := range extraFields {
		err = writer.WriteField(key, value)
		if err != nil {
			return nil, gerror.Wrapf(err, "写入表单字段失败: %s", key)
		}
	}

	err = writer.Close()
	if err != nil {
		return nil, gerror.Wrap(err, "关闭multipart writer失败")
	}

	headers := map[string]string{
		"Content-Type": writer.FormDataContentType(),
	}

	return c.doRequest(ctx, "POST", endpoint, headers, &buf)
}

func (c *Client) GetSystemStatus(ctx context.Context) (map[string]interface{}, error) {
	resp, err := c.Get(ctx, "/system/status", nil)
	if err != nil {
		return nil, err
	}

	var result struct {
		Success bool                   `json:"success"`
		Status  map[string]interface{} `json:"status"`
	}

	err = json.Unmarshal(resp, &result)
	if err != nil {
		return nil, gerror.Wrap(err, "解析系统状态响应失败")
	}

	if !result.Success {
		return nil, gerror.New("获取系统状态失败")
	}

	return map[string]interface{}{
		"success": result.Success,
		"status":  result.Status,
	}, nil
}

func (c *Client) UploadData(ctx context.Context, fileName string, fileData []byte) (map[string]interface{}, error) {
	resp, err := c.PostMultipart(ctx, "/data/upload", "file", fileName, fileData, nil)
	if err != nil {
		return nil, err
	}

	var result map[string]interface{}
	err = json.Unmarshal(resp, &result)
	if err != nil {
		return nil, gerror.Wrap(err, "解析上传数据响应失败")
	}

	return result, nil
}

func (c *Client) GetDataInfo(ctx context.Context) (map[string]interface{}, error) {
	resp, err := c.Get(ctx, "/data/info", nil)
	if err != nil {
		return nil, err
	}

	var result map[string]interface{}
	err = json.Unmarshal(resp, &result)
	if err != nil {
		return nil, gerror.Wrap(err, "解析数据信息响应失败")
	}

	return result, nil
}

func (c *Client) GetDataPreview(ctx context.Context, rows int) (map[string]interface{}, error) {
	endpoint := fmt.Sprintf("/data/preview?rows=%d", rows)
	resp, err := c.Get(ctx, endpoint, nil)
	if err != nil {
		return nil, err
	}

	var result map[string]interface{}
	err = json.Unmarshal(resp, &result)
	if err != nil {
		return nil, gerror.Wrap(err, "解析数据预览响应失败")
	}

	return result, nil
}

func (c *Client) ProcessData(ctx context.Context, handleMissing, targetColumn string) (map[string]interface{}, error) {
	data := map[string]interface{}{
		"handle_missing": handleMissing,
		"target_column":  targetColumn,
	}

	resp, err := c.Post(ctx, "/data/process", nil, data)
	if err != nil {
		return nil, err
	}

	var result map[string]interface{}
	err = json.Unmarshal(resp, &result)
	if err != nil {
		return nil, gerror.Wrap(err, "解析数据处理响应失败")
	}

	return result, nil
}

func (c *Client) TrainModel(ctx context.Context, modelType, targetColumn string, testSize float64, tuneHyperparameters bool) (map[string]interface{}, error) {
	data := map[string]interface{}{
		"model_type":           modelType,
		"target_column":        targetColumn,
		"test_size":            testSize,
		"tune_hyperparameters": tuneHyperparameters,
		"return_model":         true,
	}

	resp, err := c.Post(ctx, "/model/train", nil, data)
	if err != nil {
		return nil, err
	}

	var result map[string]interface{}
	err = json.Unmarshal(resp, &result)
	if err != nil {
		return nil, gerror.Wrap(err, "解析模型训练响应失败")
	}

	return result, nil
}

func (c *Client) GetAvailableModels(ctx context.Context) (map[string]interface{}, error) {
	resp, err := c.Get(ctx, "/model/available", nil)
	if err != nil {
		return nil, err
	}

	var result map[string]interface{}
	err = json.Unmarshal(resp, &result)
	if err != nil {
		return nil, gerror.Wrap(err, "解析可用模型响应失败")
	}

	return result, nil
}

func (c *Client) GetTrainedModels(ctx context.Context) (map[string]interface{}, error) {
	resp, err := c.Get(ctx, "/model/trained", nil)
	if err != nil {
		return nil, err
	}

	var result map[string]interface{}
	err = json.Unmarshal(resp, &result)
	if err != nil {
		return nil, gerror.Wrap(err, "解析已训练模型响应失败")
	}

	return result, nil
}

func (c *Client) GetModelMetrics(ctx context.Context, modelName string) (map[string]interface{}, error) {
	endpoint := fmt.Sprintf("/model/metrics/%s", modelName)
	resp, err := c.Get(ctx, endpoint, nil)
	if err != nil {
		return nil, err
	}

	var result map[string]interface{}
	err = json.Unmarshal(resp, &result)
	if err != nil {
		return nil, gerror.Wrap(err, "解析模型指标响应失败")
	}

	return result, nil
}

func (c *Client) CompareModels(ctx context.Context, testSize float64) (map[string]interface{}, error) {
	data := map[string]interface{}{
		"test_size": testSize,
	}

	resp, err := c.Post(ctx, "/model/compare", nil, data)
	if err != nil {
		return nil, err
	}

	var result map[string]interface{}
	err = json.Unmarshal(resp, &result)
	if err != nil {
		return nil, gerror.Wrap(err, "解析模型比较响应失败")
	}

	return result, nil
}

func (c *Client) Predict(ctx context.Context, data map[string]interface{}, modelName string) (map[string]interface{}, error) {
	requestData := map[string]interface{}{
		"data":       data,
		"model_name": modelName,
	}

	resp, err := c.Post(ctx, "/predict", nil, requestData)
	if err != nil {
		return nil, err
	}

	var result map[string]interface{}
	err = json.Unmarshal(resp, &result)
	if err != nil {
		return nil, gerror.Wrap(err, "解析预测响应失败")
	}

	return result, nil
}

func (c *Client) PredictWithModel(ctx context.Context, data map[string]interface{}, modelName string, modelData string) (map[string]interface{}, error) {
	requestData := map[string]interface{}{
		"data":       data,
		"model_name": modelName,
	}

	if modelData != "" {
		requestData["model_data"] = modelData
	}

	resp, err := c.Post(ctx, "/predict", nil, requestData)
	if err != nil {
		return nil, err
	}

	var result map[string]interface{}
	err = json.Unmarshal(resp, &result)
	if err != nil {
		return nil, gerror.Wrap(err, "解析预测响应失败")
	}

	return result, nil
}

func (c *Client) PredictWithModelAndInfo(ctx context.Context, data map[string]interface{}, modelName string, modelData string, modelInfoData string) (map[string]interface{}, error) {
	requestData := map[string]interface{}{
		"data":       data,
		"model_name": modelName,
	}

	if modelData != "" {
		requestData["model_data"] = modelData
	}

	if modelInfoData != "" {
		requestData["model_info_data"] = modelInfoData
	}

	resp, err := c.Post(ctx, "/predict", nil, requestData)
	if err != nil {
		return nil, err
	}

	var result map[string]interface{}
	err = json.Unmarshal(resp, &result)
	if err != nil {
		return nil, gerror.Wrap(err, "解析预测响应失败")
	}

	return result, nil
}

func (c *Client) BatchPredict(ctx context.Context, data []map[string]interface{}, modelName string) (map[string]interface{}, error) {
	requestData := map[string]interface{}{
		"data":       data,
		"model_name": modelName,
	}

	resp, err := c.Post(ctx, "/predict/batch", nil, requestData)
	if err != nil {
		return nil, err
	}

	var result map[string]interface{}
	err = json.Unmarshal(resp, &result)
	if err != nil {
		return nil, gerror.Wrap(err, "解析批量预测响应失败")
	}

	return result, nil
}

func (c *Client) BatchPredictWithModel(ctx context.Context, data []map[string]interface{}, modelName string, modelData string) (map[string]interface{}, error) {
	requestData := map[string]interface{}{
		"data":       data,
		"model_name": modelName,
	}

	if modelData != "" {
		requestData["model_data"] = modelData
	}

	resp, err := c.Post(ctx, "/predict/batch", nil, requestData)
	if err != nil {
		return nil, err
	}

	var result map[string]interface{}
	err = json.Unmarshal(resp, &result)
	if err != nil {
		return nil, gerror.Wrap(err, "解析批量预测响应失败")
	}

	return result, nil
}

func (c *Client) BatchPredictWithModelAndInfo(ctx context.Context, data []map[string]interface{}, modelName string, modelData string, modelInfoData string) (map[string]interface{}, error) {
	requestData := map[string]interface{}{
		"data":       data,
		"model_name": modelName,
	}

	if modelData != "" {
		requestData["model_data"] = modelData
	}

	if modelInfoData != "" {
		requestData["model_info_data"] = modelInfoData
	}

	resp, err := c.Post(ctx, "/predict/batch", nil, requestData)
	if err != nil {
		return nil, err
	}

	var result map[string]interface{}
	err = json.Unmarshal(resp, &result)
	if err != nil {
		return nil, gerror.Wrap(err, "解析批量预测响应失败")
	}

	return result, nil
}

func (c *Client) GetModelInfo(ctx context.Context, modelName string) (map[string]interface{}, error) {
	endpoint := fmt.Sprintf("/model/info?model_name=%s", modelName)
	resp, err := c.Get(ctx, endpoint, nil)
	if err != nil {
		return nil, err
	}

	var result map[string]interface{}
	err = json.Unmarshal(resp, &result)
	if err != nil {
		return nil, gerror.Wrap(err, "解析模型信息响应失败")
	}

	return result, nil
}
