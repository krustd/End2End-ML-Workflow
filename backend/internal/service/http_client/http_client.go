package http_client

import (
	"context"
	"encoding/json"
	"fmt"
	"time"

	"github.com/gogf/gf/v2/errors/gcode"
	"github.com/gogf/gf/v2/errors/gerror"
	"github.com/gogf/gf/v2/frame/g"
	"github.com/gogf/gf/v2/net/gclient"
	"github.com/gogf/gf/v2/util/grand"
)

type PythonAPIConfig struct {
	Host    string `yaml:"host"`
	Port    int    `yaml:"port"`
	Timeout int    `yaml:"timeout"`
	Debug   bool   `yaml:"debug"`
}

// GetPythonAPIConfig 获取配置，如果失败则返回默认配置
func GetPythonAPIConfig(ctx context.Context) *PythonAPIConfig {
	cfg := &PythonAPIConfig{
		Host:    "localhost",
		Port:    8000,
		Timeout: 30,
		Debug:   false,
	}

	// 尝试获取配置，如果存在且有效则解析
	if v, err := g.Cfg().Get(ctx, "python_api"); err == nil && !v.IsEmpty() {
		if err := v.Struct(cfg); err != nil {
			g.Log().Warningf(ctx, "Python API 配置解析失败，使用默认值: %v", err)
		}
	}
	return cfg
}

type Client struct {
	client  *gclient.Client
	baseURL string
}

func NewClient() *Client {
	ctx := context.Background()
	cfg := GetPythonAPIConfig(ctx)

	c := g.Client().
		SetTimeout(time.Duration(cfg.Timeout) * time.Second)

	return &Client{
		client:  c,
		baseURL: fmt.Sprintf("http://%s:%d", cfg.Host, cfg.Port),
	}
}

// helper: 执行请求并扫描结果
func (c *Client) doRequest(resp *gclient.Response, err error, result interface{}) error {
	if err != nil {
		return err
	}
	defer resp.Close()

	// 1. 读取响应体
	body := resp.ReadAll()
	if len(body) == 0 {
		return gerror.NewCode(gcode.CodeBusinessValidationFailed, "PythonAPI 返回空响应体")
	}

	// 2. 检查 HTTP 状态码
	if resp.StatusCode >= 400 {
		code := gcode.CodeInvalidRequest
		if resp.StatusCode >= 500 {
			code = gcode.CodeInternalError
		}
		// 尝试从 body 中提取错误信息
		return gerror.NewCodef(code, "PythonAPI Error %d: %s", resp.StatusCode, string(body))
	}

	// 3. 解析 JSON 结果
	if result != nil {
		if err := json.Unmarshal(body, result); err != nil {
			return gerror.Wrapf(err, "解析响应失败: %s", string(body))
		}

		// 4. 业务逻辑检查 (success: false)
		// 这里需要处理指针，因为 result 传进来是 &map
		if ptr, ok := result.(*map[string]interface{}); ok && ptr != nil {
			m := *ptr
			if v, ok := m["success"]; ok {
				if b, ok := v.(bool); ok && !b {
					return gerror.NewCodef(gcode.CodeBusinessValidationFailed, "PythonAPI 业务失败: %v", m)
				}
			}
		}
	}
	return nil
}

// helper: 通用预测请求处理
func (c *Client) sendPredictionRequest(ctx context.Context, endpoint string, baseData interface{},
	modelName, modelData, modelInfoData string) (map[string]interface{}, error) {

	req := g.Map{
		"data":       baseData,
		"model_name": modelName,
	}
	if modelData != "" {
		req["model_data"] = modelData
	}
	if modelInfoData != "" {
		req["model_info_data"] = modelInfoData
	}

	var result map[string]interface{}
	// 这里显式调用 ContentJson()，确保发送的是 JSON
	resp, err := c.client.ContentJson().Post(ctx, c.baseURL+endpoint, req)
	if err := c.doRequest(resp, err, &result); err != nil {
		return nil, err
	}
	return result, nil
}

// GetSystemStatus 获取系统状态
func (c *Client) GetSystemStatus(ctx context.Context) (map[string]interface{}, error) {
	var result map[string]interface{}
	resp, err := c.client.Get(ctx, c.baseURL+"/system/status")
	if err := c.doRequest(resp, err, &result); err != nil {
		return nil, err
	}
	return result, nil
}

func (c *Client) UploadData(ctx context.Context, filePath string, fileData ...[]byte) (map[string]interface{}, error) {
	var result map[string]interface{}
	var err error
	var resp *gclient.Response

	if len(fileData) > 0 && fileData[0] != nil {
		// 创建临时文件来保存文件内容，然后使用文件路径上传
		tempFile := filePath
		if tempFile == "" {
			tempFile = "temp.csv"
		}

		// 使用Post方法，并设置Content-Type为multipart/form-data
		// 创建一个包含文件内容的multipart/form-data请求
		boundary := "----GoFrameBoundary" + grand.S(16)
		body := "--" + boundary + "\r\n"
		body += fmt.Sprintf("Content-Disposition: form-data; name=\"file\"; filename=\"%s\"\r\n", tempFile)
		body += "Content-Type: text/csv\r\n\r\n"
		body += string(fileData[0]) + "\r\n"
		body += "--" + boundary + "--\r\n"

		resp, err = c.client.SetHeader("Content-Type", "multipart/form-data; boundary="+boundary).
			Post(ctx, c.baseURL+"/data/upload", body)
	} else {
		// 使用文件路径上传
		resp, err = c.client.Post(ctx, c.baseURL+"/data/upload", g.Map{
			"file": "@file:" + filePath,
		})
	}

	if err := c.doRequest(resp, err, &result); err != nil {
		return nil, err
	}
	return result, nil
}

// GetDataInfo 获取数据信息
func (c *Client) GetDataInfo(ctx context.Context) (map[string]interface{}, error) {
	var result map[string]interface{}
	resp, err := c.client.Get(ctx, c.baseURL+"/data/info")
	if err := c.doRequest(resp, err, &result); err != nil {
		return nil, err
	}
	return result, nil
}

// GetDataPreview 获取数据预览
func (c *Client) GetDataPreview(ctx context.Context, rows int) (map[string]interface{}, error) {
	var result map[string]interface{}
	// gclient Get方法的第二个参数可以自动处理 Query String
	resp, err := c.client.Get(ctx, c.baseURL+"/data/preview", g.Map{"rows": rows})
	if err := c.doRequest(resp, err, &result); err != nil {
		return nil, err
	}
	return result, nil
}

// ProcessData 处理数据
func (c *Client) ProcessData(ctx context.Context, handleMissing, targetColumn string) (map[string]interface{}, error) {
	var result map[string]interface{}
	// 需要 ContentJson()
	resp, err := c.client.ContentJson().Post(ctx, c.baseURL+"/data/process", g.Map{
		"handle_missing": handleMissing,
		"target_column":  targetColumn,
	})
	if err := c.doRequest(resp, err, &result); err != nil {
		return nil, err
	}
	return result, nil
}

// TrainModel 训练模型
func (c *Client) TrainModel(ctx context.Context, modelType, targetColumn string, testSize float64,
	tuneHyperparameters bool) (map[string]interface{}, error) {

	var result map[string]interface{}
	// 需要 ContentJson()
	resp, err := c.client.ContentJson().Post(ctx, c.baseURL+"/model/train", g.Map{
		"model_type":           modelType,
		"target_column":        targetColumn,
		"test_size":            testSize,
		"tune_hyperparameters": tuneHyperparameters,
		"return_model":         true,
	})
	if err := c.doRequest(resp, err, &result); err != nil {
		return nil, err
	}
	return result, nil
}

// GetAvailableModels 获取可用模型列表
func (c *Client) GetAvailableModels(ctx context.Context) (map[string]interface{}, error) {
	var result map[string]interface{}
	resp, err := c.client.Get(ctx, c.baseURL+"/model/available")
	if err := c.doRequest(resp, err, &result); err != nil {
		return nil, err
	}
	return result, nil
}

// GetTrainedModels 获取已训练模型列表
func (c *Client) GetTrainedModels(ctx context.Context) (map[string]interface{}, error) {
	var result map[string]interface{}
	resp, err := c.client.Get(ctx, c.baseURL+"/model/trained")
	if err := c.doRequest(resp, err, &result); err != nil {
		return nil, err
	}
	return result, nil
}

// GetModelMetrics 获取模型指标
func (c *Client) GetModelMetrics(ctx context.Context, modelName string) (map[string]interface{}, error) {
	var result map[string]interface{}
	// 使用 Query 参数传递 model_name 更安全（自动URL编码）
	resp, err := c.client.Get(ctx, c.baseURL+"/model/metrics", g.Map{"model_name": modelName})
	if err := c.doRequest(resp, err, &result); err != nil {
		return nil, err
	}
	return result, nil
}

// CompareModels 比较模型
func (c *Client) CompareModels(ctx context.Context, testSize float64) (map[string]interface{}, error) {
	var result map[string]interface{}
	resp, err := c.client.ContentJson().Post(ctx, c.baseURL+"/model/compare", g.Map{"test_size": testSize})
	if err := c.doRequest(resp, err, &result); err != nil {
		return nil, err
	}
	return result, nil
}

// Predict 预测
func (c *Client) Predict(ctx context.Context, data map[string]interface{}, modelName string) (map[string]interface{}, error) {
	return c.sendPredictionRequest(ctx, "/predict", data, modelName, "", "")
}

// PredictWithModel 使用指定模型数据预测
func (c *Client) PredictWithModel(ctx context.Context, data map[string]interface{}, modelName, modelData string) (map[string]interface{}, error) {
	return c.sendPredictionRequest(ctx, "/predict", data, modelName, modelData, "")
}

// PredictWithModelAndInfo 使用指定模型数据和信息预测
func (c *Client) PredictWithModelAndInfo(ctx context.Context, data map[string]interface{}, modelName,
	modelData, modelInfoData string) (map[string]interface{}, error) {

	return c.sendPredictionRequest(ctx, "/predict", data, modelName, modelData, modelInfoData)
}

// BatchPredict 批量预测
func (c *Client) BatchPredict(ctx context.Context, data []map[string]interface{}, modelName string) (map[string]interface{}, error) {
	return c.sendPredictionRequest(ctx, "/predict/batch", data, modelName, "", "")
}

// BatchPredictWithModel 批量预测 (带模型数据)
func (c *Client) BatchPredictWithModel(ctx context.Context, data []map[string]interface{}, modelName, modelData string) (map[string]interface{}, error) {
	return c.sendPredictionRequest(ctx, "/predict/batch", data, modelName, modelData, "")
}

// BatchPredictWithModelAndInfo 批量预测 (带模型数据和信息)
func (c *Client) BatchPredictWithModelAndInfo(ctx context.Context, data []map[string]interface{}, modelName,
	modelData, modelInfoData string) (map[string]interface{}, error) {

	return c.sendPredictionRequest(ctx, "/predict/batch", data, modelName, modelData, modelInfoData)
}

// GetModelInfo 获取模型详细信息
func (c *Client) GetModelInfo(ctx context.Context, modelName string) (map[string]interface{}, error) {
	var result map[string]interface{}
	// 自动处理 URL 编码
	resp, err := c.client.Get(ctx, c.baseURL+"/model/info", g.Map{"model_name": modelName})
	if err := c.doRequest(resp, err, &result); err != nil {
		return nil, err
	}
	return result, nil
}
