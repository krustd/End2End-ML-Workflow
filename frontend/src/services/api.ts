import axios from 'axios'
import { ElMessage } from 'element-plus'

const api = axios.create({
    baseURL: 'http://localhost:8080',
    timeout: 30000,
    headers: {
        'Content-Type': 'application/json'
    }
})

api.interceptors.request.use(
    config => {
        return config
    },
    error => {
        return Promise.reject(error)
    }
)

api.interceptors.response.use(
    response => {
        const responseData = response.data

        if (responseData && typeof responseData === 'object' && 'code' in responseData && 'data' in responseData && 'message' in responseData) {
            if (responseData.code !== 0) {
                ElMessage.error(responseData.message || '请求失败')
                return Promise.reject(new Error(responseData.message || '请求失败'))
            }

            return responseData.data
        }

        return responseData
    },
    error => {
        const message = error.response?.data?.message || error.message || '请求失败'
        ElMessage.error(message)
        return Promise.reject(error)
    }
)

export const dataApi = {
    uploadData(file: File) {
        const formData = new FormData()
        formData.append('file', file)
        return api.post('/data/upload', formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        })
    },

    getDataInfo() {
        return api.get('/data/info')
    },

    getDataPreview(rows = 20) {
        return api.get('/data/preview', { params: { rows } })
    },

    processData(params: {
        handle_missing: string
        target_column?: string
    }) {
        return api.post('/data/process', params)
    }
}

export const modelApi = {
    trainModel(params: {
        model_type: string
        target_column?: string
        test_size?: number
        tune_hyperparameters?: boolean
    }) {
        return api.post('/model/train', params)
    },

    getAvailableModels() {
        return api.get('/model/available')
    },

    getTrainedModels() {
        return api.get('/model/trained')
    },

    getModelMetrics(modelName: string) {
        return api.get(`/model/metrics/${modelName}`)
    },

    compareModels(testSize = 0.2) {
        return api.post('/model/compare', null, { params: { test_size: testSize } })
    },

    getModelInfo(modelName?: string) {
        return api.get('/model/info', { params: { model_name: modelName } })
    }
}

export const predictApi = {
    predict(params: {
        data: Record<string, any>
        model_name?: string
        model_data?: string
        model_info_data?: string
    }) {
        return api.post('/predict', params)
    },

    batchPredict(data: Record<string, any>[], modelName?: string, modelData?: string, modelInfoData?: string) {
        const params: any = { model_name: modelName }
        const requestData: any = { data }

        if (modelData) {
            requestData.model_data = modelData
        }

        if (modelInfoData) {
            requestData.model_info_data = modelInfoData
        }

        return api.post('/predict/batch', requestData, { params })
    },

    exportPredictions(data: Record<string, any>[], format = 'csv', modelName?: string, modelData?: string, modelInfoData?: string) {
        const params: any = { format, model_name: modelName }
        const requestData: any = { data }

        if (modelData) {
            requestData.model_data = modelData
        }

        if (modelInfoData) {
            requestData.model_info_data = modelInfoData
        }

        return api.post('/predict/export', requestData, {
            params,
            responseType: 'blob'
        })
    }
}

export const systemApi = {
    getSystemStatus() {
        return api.get('/system/status')
    },

    getRoot() {
        return api.get('/')
    }
}

export default api