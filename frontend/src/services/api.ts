import axios from 'axios'
import { ElMessage } from 'element-plus'

// 创建axios实例
const api = axios.create({
    baseURL: 'http://localhost:8080', // 后端API地址
    timeout: 30000, // 请求超时时间
    headers: {
        'Content-Type': 'application/json'
    }
})

// 请求拦截器
api.interceptors.request.use(
    config => {
        // 在发送请求之前做些什么
        return config
    },
    error => {
        // 对请求错误做些什么
        return Promise.reject(error)
    }
)

// 响应拦截器
api.interceptors.response.use(
    response => {
        // 后端使用BaseRes结构包装响应，实际数据在data字段中
        const responseData = response.data

        // 检查响应格式是否为BaseRes
        if (responseData && typeof responseData === 'object' && 'code' in responseData && 'data' in responseData && 'message' in responseData) {
            // 检查业务状态码
            if (responseData.code !== 0) {
                ElMessage.error(responseData.message || '请求失败')
                return Promise.reject(new Error(responseData.message || '请求失败'))
            }

            // 返回实际的业务数据
            return responseData.data
        }

        // 如果不是BaseRes格式，直接返回原始数据
        return responseData
    },
    error => {
        // 对响应错误做点什么
        const message = error.response?.data?.message || error.message || '请求失败'
        ElMessage.error(message)
        return Promise.reject(error)
    }
)

// 数据管理API
export const dataApi = {
    // 上传CSV数据文件
    uploadData(file: File) {
        console.log('dataApi.uploadData - 开始上传')
        console.log('dataApi.uploadData - 文件参数:', file)
        console.log('dataApi.uploadData - FormData创建前')

        const formData = new FormData()
        formData.append('file', file)

        console.log('dataApi.uploadData - FormData创建后，发送请求')
        return api.post('/data/upload', formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        })
    },

    // 获取数据信息
    getDataInfo() {
        return api.get('/data/info')
    },

    // 获取数据预览
    getDataPreview(rows = 20) {
        return api.get('/data/preview', { params: { rows } })
    },

    // 处理数据
    processData(params: {
        handle_missing: string
        target_column?: string
    }) {
        return api.post('/data/process', params)
    }
}

// 模型管理API
export const modelApi = {
    // 训练模型
    trainModel(params: {
        model_type: string
        target_column?: string
        test_size?: number
        tune_hyperparameters?: boolean
    }) {
        return api.post('/model/train', params)
    },

    // 获取可用模型
    getAvailableModels() {
        return api.get('/model/available')
    },

    // 获取已训练模型
    getTrainedModels() {
        return api.get('/model/trained')
    },

    // 获取模型指标
    getModelMetrics(modelName: string) {
        return api.get(`/model/metrics/${modelName}`)
    },

    // 比较模型
    compareModels(testSize = 0.2) {
        return api.post('/model/compare', null, { params: { test_size: testSize } })
    },

    // 获取模型信息
    getModelInfo(modelName?: string) {
        return api.get('/model/info', { params: { model_name: modelName } })
    }
}

// 预测服务API
export const predictApi = {
    // 单条预测
    predict(params: {
        data: Record<string, any>
        model_name?: string
    }) {
        return api.post('/predict', params)
    },

    // 批量预测
    batchPredict(data: Record<string, any>[], modelName?: string) {
        return api.post('/predict/batch', data, { params: { model_name: modelName } })
    },

    // 导出预测结果
    exportPredictions(data: Record<string, any>[], format = 'csv', modelName?: string) {
        return api.post('/predict/export', data, {
            params: { format, model_name: modelName },
            responseType: 'blob'
        })
    }
}

// 系统管理API
export const systemApi = {
    // 获取系统状态
    getSystemStatus() {
        return api.get('/system/status')
    },

    // 获取根路径信息
    getRoot() {
        return api.get('/')
    }
}

export default api