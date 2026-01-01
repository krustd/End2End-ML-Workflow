import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { systemApi } from '@/services/api'
import { useSettingsStore } from './settings'
import { useDataStore } from './data'

export const useSystemStore = defineStore('system', () => {
    const settingsStore = useSettingsStore()
    const dataStore = useDataStore()

    // 状态
    const systemStatus = ref({
        data_uploaded: false,
        model_trained: false,
        current_step: '数据上传',
        current_model: settingsStore.defaultModel,
        available_models: []
    })

    const loading = ref(false)
    const error = ref<string | null>(null)

    // 计算属性
    const currentStepIndex = computed(() => {
        const steps = ['数据上传', '模型训练', '预测']
        return steps.indexOf(systemStatus.value.current_step)
    })

    const canProceedToModelTraining = computed(() => {
        // 不仅检查data_uploaded状态，还要检查数据存储中是否真的有有效数据
        return systemStatus.value.data_uploaded && dataStore.hasData
    })

    const canProceedToPrediction = computed(() => {
        return systemStatus.value.data_uploaded && systemStatus.value.model_trained && dataStore.hasData
    })

    // 方法
    async function fetchSystemStatus() {
        loading.value = true
        error.value = null

        try {
            const response = await systemApi.getSystemStatus() as any
            if (response.success) {
                systemStatus.value = { ...systemStatus.value, ...response.status }
            }
        } catch (err) {
            error.value = '获取系统状态失败'
            console.error('获取系统状态失败:', err)
        } finally {
            loading.value = false
        }
    }

    function updateSystemStatus(updates: Partial<typeof systemStatus.value>) {
        systemStatus.value = { ...systemStatus.value, ...updates }
    }

    function resetSystemStatus() {
        systemStatus.value = {
            data_uploaded: false,
            model_trained: false,
            current_step: '数据上传',
            current_model: '线性回归模型（默认）',
            available_models: []
        }
    }

    return {
        systemStatus,
        loading,
        error,
        currentStepIndex,
        canProceedToModelTraining,
        canProceedToPrediction,
        fetchSystemStatus,
        updateSystemStatus,
        resetSystemStatus
    }
})