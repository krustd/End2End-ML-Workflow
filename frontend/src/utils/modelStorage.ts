/**
 * 模型存储工具类
 * 负责在前端浏览器中存储和管理机器学习模型
 */

import { ElMessage } from 'element-plus'

export interface ModelInfo {
    model_name: string
    model_type: string
    feature_names: string[]
    target_name: string
    train_metrics: Record<string, number>
    test_metrics: Record<string, number>
    cv_metrics?: Record<string, any>
    tuned: boolean
    created_at: string
}

export interface StoredModel {
    model_data: string // base64编码的模型数据
    model_info: ModelInfo
    model_info_data?: string // base64编码的模型信息数据
}

class ModelStorageClass {
    private readonly STORAGE_KEY = 'ml_models'

    /**
     * 保存模型到本地存储
     * @param modelData base64编码的模型数据
     * @param modelInfo 模型信息
     * @param modelInfoData base64编码的模型信息数据
     */
    saveModel(modelData: string, modelInfo: ModelInfo, modelInfoData?: string): boolean {
        try {
            // 获取当前存储的模型
            const storedModels = this.getAllModels()

            // 添加新模型或更新现有模型
            const storedModel: StoredModel = {
                model_data: modelData,
                model_info: {
                    ...modelInfo,
                    created_at: new Date().toISOString()
                }
            }

            // 如果提供了模型信息数据，添加到存储中
            if (modelInfoData) {
                storedModel.model_info_data = modelInfoData
            }

            storedModels[modelInfo.model_name] = storedModel

            // 保存到localStorage
            localStorage.setItem(this.STORAGE_KEY, JSON.stringify(storedModels))

            ElMessage.success(`模型 ${modelInfo.model_name} 已保存到本地`)
            return true
        } catch (error) {
            console.error('保存模型失败:', error)
            ElMessage.error('保存模型失败: ' + (error as Error).message)
            return false
        }
    }

    /**
     * 获取所有存储的模型
     */
    getAllModels(): Record<string, StoredModel> {
        try {
            const modelsJson = localStorage.getItem(this.STORAGE_KEY)
            return modelsJson ? JSON.parse(modelsJson) : {}
        } catch (error) {
            console.error('获取模型列表失败:', error)
            return {}
        }
    }

    /**
     * 获取指定模型
     * @param modelName 模型名称
     */
    getModel(modelName: string): StoredModel | null {
        try {
            const models = this.getAllModels()
            return models[modelName] || null
        } catch (error) {
            console.error('获取模型失败:', error)
            return null
        }
    }

    /**
     * 删除指定模型
     * @param modelName 模型名称
     */
    deleteModel(modelName: string): boolean {
        try {
            const models = this.getAllModels()

            if (!models[modelName]) {
                ElMessage.warning(`模型 ${modelName} 不存在`)
                return false
            }

            delete models[modelName]
            localStorage.setItem(this.STORAGE_KEY, JSON.stringify(models))

            ElMessage.success(`模型 ${modelName} 已删除`)
            return true
        } catch (error) {
            console.error('删除模型失败:', error)
            ElMessage.error('删除模型失败: ' + (error as Error).message)
            return false
        }
    }

    /**
     * 清空所有模型
     */
    clearAllModels(): boolean {
        try {
            localStorage.removeItem(this.STORAGE_KEY)
            ElMessage.success('所有模型已清空')
            return true
        } catch (error) {
            console.error('清空模型失败:', error)
            ElMessage.error('清空模型失败: ' + (error as Error).message)
            return false
        }
    }

    /**
     * 获取模型名称列表
     */
    getModelNames(): string[] {
        try {
            const models = this.getAllModels()
            return Object.keys(models)
        } catch (error) {
            console.error('获取模型名称列表失败:', error)
            return []
        }
    }

    /**
     * 获取模型信息列表（不包含模型数据）
     */
    getModelInfos(): ModelInfo[] {
        try {
            const models = this.getAllModels()
            return Object.values(models).map(model => model.model_info)
        } catch (error) {
            console.error('获取模型信息列表失败:', error)
            return []
        }
    }

    /**
     * 检查模型是否存在
     * @param modelName 模型名称
     */
    modelExists(modelName: string): boolean {
        const models = this.getAllModels()
        return modelName in models
    }

    /**
     * 导出模型为JSON文件
     * @param modelName 模型名称
     */
    exportModel(modelName: string): boolean {
        try {
            const model = this.getModel(modelName)
            if (!model) {
                ElMessage.error(`模型 ${modelName} 不存在`)
                return false
            }

            // 创建下载链接
            const dataStr = JSON.stringify(model, null, 2)
            const dataBlob = new Blob([dataStr], { type: 'application/json' })
            const url = URL.createObjectURL(dataBlob)

            const link = document.createElement('a')
            link.href = url
            link.download = `${modelName}.json`
            document.body.appendChild(link)
            link.click()
            document.body.removeChild(link)
            URL.revokeObjectURL(url)

            ElMessage.success(`模型 ${modelName} 已导出`)
            return true
        } catch (error) {
            console.error('导出模型失败:', error)
            ElMessage.error('导出模型失败: ' + (error as Error).message)
            return false
        }
    }

    /**
     * 从JSON文件导入模型
     * @param file JSON文件
     */
    async importModel(file: File): Promise<boolean> {
        try {
            const text = await file.text()
            const model: StoredModel = JSON.parse(text)

            if (!model.model_data || !model.model_info || !model.model_info.model_name) {
                throw new Error('无效的模型文件格式')
            }

            return this.saveModel(model.model_data, model.model_info)
        } catch (error) {
            console.error('导入模型失败:', error)
            ElMessage.error('导入模型失败: ' + (error as Error).message)
            return false
        }
    }

    /**
     * 获取存储使用情况
     */
    getStorageUsage(): { used: number, total: number, percentage: number } {
        try {
            const modelsJson = localStorage.getItem(this.STORAGE_KEY)
            const used = modelsJson ? new Blob([modelsJson]).size : 0
            // 估算localStorage总容量（通常为5-10MB，这里保守估计为5MB）
            const total = 5 * 1024 * 1024 // 5MB
            const percentage = Math.round((used / total) * 100)

            return { used, total, percentage }
        } catch (error) {
            console.error('获取存储使用情况失败:', error)
            return { used: 0, total: 0, percentage: 0 }
        }
    }
}

// 创建单例实例
const ModelStorage = new ModelStorageClass()
export default ModelStorage
