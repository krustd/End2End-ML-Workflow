import { ref } from 'vue'
import { defineStore } from 'pinia'
import { predictApi } from '@/services/api'
import { ElMessage } from 'element-plus'
import LocalPredictor from '@/utils/localPredictor'
import type { PredictionResult, BatchPredictionResult } from '@/utils/localPredictor'
import ModelStorage from '@/utils/modelStorage'

export const usePredictStore = defineStore('predict', () => {
    // 状态
    const predictionResult = ref<PredictionResult | null>(null)
    const batchPredictionResult = ref<BatchPredictionResult | null>(null)
    const loading = ref(false)
    const error = ref<string | null>(null)

    // 方法
    async function predict(params: {
        data: Record<string, any>
        model_name?: string
    }) {
        loading.value = true
        error.value = null

        try {
            // 获取本地存储的模型数据
            let modelData = null
            let modelInfoData = null
            if (params.model_name) {
                const model = ModelStorage.getModel(params.model_name)
                if (model) {
                    modelData = model.model_data
                    modelInfoData = model.model_info_data
                }
            }

            // 发送预测请求，包含模型数据和模型信息数据
            const response = await predictApi.predict({
                ...params,
                model_data: modelData || undefined,
                model_info_data: modelInfoData || undefined
            }) as any

            if (response.success) {
                predictionResult.value = response
                ElMessage.success('预测完成')
                return response
            } else {
                throw new Error(response.message || '预测失败')
            }
        } catch (err: any) {
            error.value = err.message || '预测失败'
            ElMessage.error(error.value || '预测失败')
            throw err
        } finally {
            loading.value = false
        }
    }

    async function batchPredict(data: Record<string, any>[], modelName?: string) {
        loading.value = true
        error.value = null

        try {
            // 获取本地存储的模型数据
            let modelData = null
            let modelInfoData = null
            if (modelName) {
                const model = ModelStorage.getModel(modelName)
                if (model) {
                    modelData = model.model_data
                    modelInfoData = model.model_info_data
                }
            }

            // 发送批量预测请求，包含模型数据和模型信息数据
            const response = await predictApi.batchPredict(data, modelName, modelData || undefined, modelInfoData || undefined) as any

            if (response.success) {
                batchPredictionResult.value = response
                ElMessage.success('批量预测完成')
                return response
            } else {
                throw new Error(response.message || '批量预测失败')
            }
        } catch (err: any) {
            error.value = err.message || '批量预测失败'
            ElMessage.error(error.value || '批量预测失败')
            throw err
        } finally {
            loading.value = false
        }
    }

    async function exportPredictions(
        data: Record<string, any>[],
        format = 'csv',
        modelName?: string
    ) {
        loading.value = true
        error.value = null

        try {
            // 获取本地存储的模型数据
            let modelData = null
            let modelInfoData = null
            if (modelName) {
                const model = ModelStorage.getModel(modelName)
                if (model) {
                    modelData = model.model_data
                    modelInfoData = model.model_info_data
                }
            }

            const response = await predictApi.exportPredictions(data, format, modelName, modelData || undefined, modelInfoData || undefined) as any

            // 创建下载链接
            const blob = new Blob([response])
            const url = window.URL.createObjectURL(blob)
            const link = document.createElement('a')
            link.href = url
            link.download = `predictions.${format}`
            document.body.appendChild(link)
            link.click()
            document.body.removeChild(link)
            window.URL.revokeObjectURL(url)

            ElMessage.success('预测结果导出成功')
            return { success: true }
        } catch (err: any) {
            error.value = err.message || '导出预测结果失败'
            ElMessage.error(error.value || '导出预测结果失败')
            throw err
        } finally {
            loading.value = false
        }
    }

    function clearResults() {
        predictionResult.value = null
        batchPredictionResult.value = null
        error.value = null
    }

    return {
        predictionResult,
        batchPredictionResult,
        loading,
        error,
        predict,
        batchPredict,
        exportPredictions,
        clearResults
    }
})