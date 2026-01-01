import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

export interface AppSettings {
    defaultModel: string
    themeColor: string
    tablePageSize: number
}

const DEFAULT_SETTINGS: AppSettings = {
    defaultModel: 'linear_regression',
    themeColor: '#409eff',
    tablePageSize: 20
}

export const useSettingsStore = defineStore('settings', () => {
    // 状态
    const settings = ref<AppSettings>({ ...DEFAULT_SETTINGS })

    // 从localStorage加载设置
    const loadSettings = () => {
        try {
            const savedSettings = localStorage.getItem('app_settings')
            if (savedSettings) {
                const parsed = JSON.parse(savedSettings)
                settings.value = { ...DEFAULT_SETTINGS, ...parsed }
            }
        } catch (error) {
            console.error('加载设置失败:', error)
            settings.value = { ...DEFAULT_SETTINGS }
        }
    }

    // 保存设置到localStorage
    const saveSettings = () => {
        try {
            localStorage.setItem('app_settings', JSON.stringify(settings.value))
        } catch (error) {
            console.error('保存设置失败:', error)
        }
    }

    // 更新设置
    const updateSettings = (newSettings: Partial<AppSettings>) => {
        settings.value = { ...settings.value, ...newSettings }
        saveSettings()
        applyThemeColor()
    }

    // 应用主题颜色
    const applyThemeColor = () => {
        const root = document.documentElement
        root.style.setProperty('--el-color-primary', settings.value.themeColor)

        // 计算并设置相关的颜色变体
        const color = settings.value.themeColor
        // 这里可以添加更多颜色变体的计算逻辑
    }

    // 重置设置
    const resetSettings = () => {
        settings.value = { ...DEFAULT_SETTINGS }
        saveSettings()
        applyThemeColor()
    }

    // 计算属性
    const themeColor = computed(() => settings.value.themeColor)
    const defaultModel = computed(() => settings.value.defaultModel)
    const tablePageSize = computed(() => settings.value.tablePageSize)

    // 初始化时加载设置
    loadSettings()
    applyThemeColor()

    return {
        settings,
        themeColor,
        defaultModel,
        tablePageSize,
        updateSettings,
        resetSettings,
        saveSettings,
        applyThemeColor
    }
})