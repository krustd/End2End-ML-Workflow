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
  tablePageSize: 20,
}

export const useSettingsStore = defineStore('settings', () => {
  const settings = ref<AppSettings>({ ...DEFAULT_SETTINGS })

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

  const saveSettings = () => {
    try {
      localStorage.setItem('app_settings', JSON.stringify(settings.value))
    } catch (error) {
      console.error('保存设置失败:', error)
    }
  }

  const updateSettings = (newSettings: Partial<AppSettings>) => {
    settings.value = { ...settings.value, ...newSettings }
    saveSettings()
    applyThemeColor()
  }

  const applyThemeColor = () => {
    const root = document.documentElement
    root.style.setProperty('--el-color-primary', settings.value.themeColor)

    const color = settings.value.themeColor
  }

  const resetSettings = () => {
    settings.value = { ...DEFAULT_SETTINGS }
    saveSettings()
    applyThemeColor()
  }

  const themeColor = computed(() => settings.value.themeColor)
  const defaultModel = computed(() => settings.value.defaultModel)
  const tablePageSize = computed(() => settings.value.tablePageSize)

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
    applyThemeColor,
  }
})
