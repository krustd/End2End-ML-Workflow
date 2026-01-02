import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { systemApi } from '@/services/api'
import { useSettingsStore } from './settings'
import { useDataStore } from './data'
import { useModelStore } from './model'

export const useSystemStore = defineStore('system', () => {
    const settingsStore = useSettingsStore()
    const dataStore = useDataStore()
    const modelStore = useModelStore()

    const systemStatus = ref({
        data_uploaded: false,
        model_trained: false,
        current_step: '数据上传',
        current_model: settingsStore.defaultModel,
        available_models: []
    })

    const loading = ref(false)
    const error = ref<string | null>(null)

    const currentStepIndex = computed(() => {
        const steps = ['数据上传', '模型训练', '预测']
        return steps.indexOf(systemStatus.value.current_step)
    })

    const canProceedToModelTraining = computed(() => {
        return systemStatus.value.data_uploaded && dataStore.hasData
    })

    const canProceedToPrediction = computed(() => {
        return systemStatus.value.data_uploaded &&
            systemStatus.value.model_trained &&
            dataStore.hasData &&
            modelStore.currentModel !== null
    })
    async function fetchSystemStatus() {
        loading.value = true
        error.value = null

        try {
            const response = await systemApi.getSystemStatus() as any
            if (response.success) {
                systemStatus.value = {
                    ...systemStatus.value,
                    ...response.status,
                    model_trained: systemStatus.value.model_trained && response.status.model_trained
                }
            }
        } catch (err) {
            error.value = '获取系统状态失败'
            console.error(err)
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