import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { modelApi } from '@/services/api'
import { ElMessage } from 'element-plus'
import ModelStorage from '@/utils/modelStorage'
import type { ModelInfo as StorageModelInfo } from '@/utils/modelStorage'

export interface ModelMetrics {
  [key: string]: number
}

export interface ModelInfo {
  model_name: string
  model_type: string
  train_metrics: ModelMetrics
  test_metrics: ModelMetrics
  cv_scores?: ModelMetrics
  model_path?: string
  model_data?: string
  model_info_data?: string
  feature_names?: string[]
  target_name?: string
}

export const useModelStore = defineStore('model', () => {
  const availableModels = ref<string[]>([])
  const trainedModels = ref<string[]>([])
  const currentModel = ref<ModelInfo | null>(null)
  const modelMetrics = ref<Record<string, ModelMetrics>>({})
  const comparisonResults = ref<any>(null)
  const loading = ref(false)
  const training = ref(false)
  const error = ref<string | null>(null)

  const hasTrainedModel = computed(() => {
    return currentModel.value !== null
  })

  const availableModelOptions = computed(() => {
    return availableModels.value.map((model) => ({
      label: getModelDisplayName(model),
      value: model,
    }))
  })

  const trainedModelOptions = computed(() => {
    return trainedModels.value.map((model) => ({
      label: getModelDisplayName(model),
      value: model,
    }))
  })

  function getModelDisplayName(modelType: string): string {
    const modelNames: Record<string, string> = {
      linear_regression: '线性回归',
      ridge: '岭回归',
      lasso: 'Lasso回归',
      elastic_net: '弹性网络',
      random_forest: '随机森林',
      gradient_boosting: '梯度提升',
      svr: '支持向量回归',
      decision_tree: '决策树',
      knn: 'K近邻',
    }
    return modelNames[modelType] || modelType
  }

  async function fetchAvailableModels() {
    loading.value = true
    error.value = null

    try {
      const response = (await modelApi.getAvailableModels()) as any
      if (response.success) {
        availableModels.value = response.models
      }
    } catch (err: any) {
      error.value = err.message || '获取可用模型失败'
      console.error('获取可用模型失败:', err)
    } finally {
      loading.value = false
    }
  }

  async function fetchTrainedModels() {
    loading.value = true
    error.value = null

    try {
      const modelNames = ModelStorage.getModelNames()
      trainedModels.value = modelNames
    } catch (err: any) {
      error.value = err.message || '获取已训练模型失败'
      console.error('获取已训练模型失败:', err)
    } finally {
      loading.value = false
    }
  }

  async function trainModel(params: {
    model_type: string
    target_column?: string
    test_size?: number
    tune_hyperparameters?: boolean
  }) {
    training.value = true
    error.value = null

    try {
      const response = (await modelApi.trainModel(params)) as any
      if (response.success) {
        const modelInfo: StorageModelInfo = {
          model_name: response.model_name,
          model_type: response.model_type,
          feature_names: response.feature_names || [],
          target_name: response.target_name || params.target_column || '',
          train_metrics: response.train_metrics,
          test_metrics: response.test_metrics,
          cv_metrics: response.cv_metrics,
          tuned: params.tune_hyperparameters || false,
          created_at: new Date().toISOString(),
        }

        if (response.model_data) {
          ModelStorage.saveModel(response.model_data, modelInfo, response.model_info_data)
        }

        currentModel.value = {
          model_name: response.model_name,
          model_type: response.model_type,
          train_metrics: response.train_metrics,
          test_metrics: response.test_metrics,
          cv_scores: response.cv_metrics,
          model_data: response.model_data,
          feature_names: response.feature_names,
          target_name: response.target_name,
        }

        if (!trainedModels.value.includes(response.model_name)) {
          trainedModels.value.push(response.model_name)
        }

        ElMessage.success('模型训练完成并已保存到本地')
        return response
      } else {
        throw new Error(response.message || '模型训练失败')
      }
    } catch (err: any) {
      error.value = err.message || '模型训练失败'
      ElMessage.error(error.value || '模型训练失败')
      throw err
    } finally {
      training.value = false
    }
  }

  async function fetchModelMetrics(modelName: string) {
    loading.value = true
    error.value = null

    try {
      const response = (await modelApi.getModelMetrics(modelName)) as any
      if (response.success) {
        modelMetrics.value[modelName] = response.metrics
      }
    } catch (err: any) {
      error.value = err.message || '获取模型指标失败'
      console.error('获取模型指标失败:', err)
    } finally {
      loading.value = false
    }
  }

  async function compareModels(testSize = 0.2) {
    loading.value = true
    error.value = null

    try {
      const response = (await modelApi.compareModels(testSize)) as any
      if (response.success) {
        comparisonResults.value = response
        ElMessage.success('模型比较完成')
        return response
      } else {
        throw new Error(response.message || '模型比较失败')
      }
    } catch (err: any) {
      error.value = err.message || '模型比较失败'
      ElMessage.error(error.value || '模型比较失败')
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchModelInfo(modelName?: string) {
    loading.value = true
    error.value = null

    try {
      const response = (await modelApi.getModelInfo(modelName)) as any
      if (response.success) {
        return response.model_info
      }
    } catch (err: any) {
      error.value = err.message || '获取模型信息失败'
      console.error('获取模型信息失败:', err)
    } finally {
      loading.value = false
    }
  }

  function setCurrentModel(model: ModelInfo | null) {
    currentModel.value = model
  }

  function clearModels() {
    availableModels.value = []
    trainedModels.value = []
    currentModel.value = null
    modelMetrics.value = {}
    comparisonResults.value = null
    error.value = null
  }

  return {
    availableModels,
    trainedModels,
    currentModel,
    modelMetrics,
    comparisonResults,
    loading,
    training,
    error,
    hasTrainedModel,
    availableModelOptions,
    trainedModelOptions,
    fetchAvailableModels,
    fetchTrainedModels,
    trainModel,
    fetchModelMetrics,
    compareModels,
    fetchModelInfo,
    setCurrentModel,
    clearModels,
  }
})
