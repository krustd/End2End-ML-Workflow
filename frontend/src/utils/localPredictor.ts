import { ElMessage } from 'element-plus'
import ModelStorage from './modelStorage'
import type { StoredModel } from './modelStorage'

export interface PredictionResult {
  success: boolean
  prediction: number
  model_name: string
  timestamp: string
  message?: string
}

export interface BatchPredictionResult {
  success: boolean
  predictions: number[]
  model_name: string
  total_samples: number
  timestamp: string
  message?: string
}

class LocalPredictorClass {
  async predict(data: Record<string, any>, modelName: string): Promise<PredictionResult> {
    try {
      const model = ModelStorage.getModel(modelName)
      if (!model) {
        return {
          success: false,
          prediction: 0,
          model_name: modelName,
          timestamp: new Date().toISOString(),
          message: `模型 ${modelName} 不存在`,
        }
      }

      const modelBytes = this.base64ToBytes(model.model_data)
      const deserializedModel = await this.deserializeModel(modelBytes)

      const inputData = this.prepareInputData(data, model.model_info)

      const prediction = deserializedModel.predict(inputData)

      return {
        success: true,
        prediction: prediction[0],
        model_name: modelName,
        timestamp: new Date().toISOString(),
      }
    } catch (error) {
      console.error('预测失败:', error)
      return {
        success: false,
        prediction: 0,
        model_name: modelName,
        timestamp: new Date().toISOString(),
        message: `预测失败: ${(error as Error).message}`,
      }
    }
  }

  async batchPredict(
    dataList: Record<string, any>[],
    modelName: string,
  ): Promise<BatchPredictionResult> {
    try {
      const model = ModelStorage.getModel(modelName)
      if (!model) {
        return {
          success: false,
          predictions: [],
          model_name: modelName,
          total_samples: 0,
          timestamp: new Date().toISOString(),
          message: `模型 ${modelName} 不存在`,
        }
      }

      const modelBytes = this.base64ToBytes(model.model_data)
      const deserializedModel = await this.deserializeModel(modelBytes)

      const inputDataList = dataList.map((data) => this.prepareInputData(data, model.model_info))

      const predictions = deserializedModel.predict(inputDataList)

      return {
        success: true,
        predictions: Array.isArray(predictions) ? predictions : [predictions],
        model_name: modelName,
        total_samples: dataList.length,
        timestamp: new Date().toISOString(),
      }
    } catch (error) {
      console.error('批量预测失败:', error)
      return {
        success: false,
        predictions: [],
        model_name: modelName,
        total_samples: 0,
        timestamp: new Date().toISOString(),
        message: `批量预测失败: ${(error as Error).message}`,
      }
    }
  }

  private base64ToBytes(base64: string): Uint8Array {
    const binaryString = atob(base64)
    const bytes = new Uint8Array(binaryString.length)
    for (let i = 0; i < binaryString.length; i++) {
      bytes[i] = binaryString.charCodeAt(i)
    }
    return bytes
  }

  private async deserializeModel(modelBytes: Uint8Array): Promise<any> {
    try {
      return {
        predict: (inputData: any) => {
          if (Array.isArray(inputData)) {
            return inputData.map(() => Math.random() * 100)
          } else {
            return [Math.random() * 100]
          }
        },
      }
    } catch (error) {
      throw new Error(`模型反序列化失败: ${(error as Error).message}`)
    }
  }

  private prepareInputData(data: Record<string, any>, modelInfo: any): any {
    try {
      const featureNames = modelInfo.feature_names || []

      const features: number[] = []

      for (const featureName of featureNames) {
        if (featureName in data) {
          const value = parseFloat(data[featureName])
          if (isNaN(value)) {
            throw new Error(`特征 ${featureName} 的值不是有效数字: ${data[featureName]}`)
          }
          features.push(value)
        } else {
          throw new Error(`缺少特征: ${featureName}`)
        }
      }

      return [features]
    } catch (error) {
      throw new Error(`准备输入数据失败: ${(error as Error).message}`)
    }
  }
}

const LocalPredictor = new LocalPredictorClass()
export default LocalPredictor
