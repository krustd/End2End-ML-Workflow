import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { dataApi } from '@/services/api'
import { ElMessage } from 'element-plus'

export interface DataInfo {
  file_name: string
  file_size: number
  rows_count: number
  columns_count: number
  columns: string[]
  numeric_columns: string[]
  categorical_columns: string[]
  target_column?: string
  feature_columns?: string[]
}

export const useDataStore = defineStore('data', () => {
  const dataInfo = ref<DataInfo | null>(null)
  const dataPreview = ref<any[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const targetColumn = ref<string>('')

  const hasData = computed(() => {
    return dataInfo.value !== null && dataInfo.value.file_name !== ''
  })

  const numericColumnOptions = computed(() => {
    if (!dataInfo.value) return []
    return dataInfo.value.numeric_columns.map((col) => ({
      label: col,
      value: col,
    }))
  })

  const allColumnOptions = computed(() => {
    if (!dataInfo.value) return []
    return dataInfo.value.columns.map((col) => ({
      label: col,
      value: col,
    }))
  })

  async function uploadData(file: File) {
    loading.value = true
    error.value = null

    try {
      const response = (await dataApi.uploadData(file)) as any

      if (response.success) {
        dataInfo.value = response.data_info
        dataPreview.value = response.preview || []
        ElMessage.success('数据上传成功')
        return response
      } else {
        throw new Error(response.message || '上传失败')
      }
    } catch (err: any) {
      console.error('uploadData - 捕获错误:', err)
      error.value = err.message || '数据上传失败'
      ElMessage.error(error.value || '数据上传失败')

      dataInfo.value = null
      dataPreview.value = []

      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchDataInfo() {
    loading.value = true
    error.value = null

    try {
      const response = (await dataApi.getDataInfo()) as any
      if (response.success) {
        dataInfo.value = response.data_info
      }
    } catch (err: any) {
      error.value = err.message || '获取数据信息失败'
      console.error('获取数据信息失败:', err)
    } finally {
      loading.value = false
    }
  }

  async function fetchDataPreview(rows = 20) {
    loading.value = true
    error.value = null

    try {
      const response = (await dataApi.getDataPreview(rows)) as any
      if (response.success) {
        dataPreview.value = response.preview
      }
    } catch (err: any) {
      error.value = err.message || '获取数据预览失败'
      console.error('获取数据预览失败:', err)
    } finally {
      loading.value = false
    }
  }

  async function processData(params: { handle_missing: string; target_column?: string }) {
    loading.value = true
    error.value = null

    try {
      const response = (await dataApi.processData(params)) as any
      if (response.success) {
        ElMessage.success('数据处理成功')
        return response
      } else {
        throw new Error(response.message || '数据处理失败')
      }
    } catch (err: any) {
      error.value = err.message || '数据处理失败'
      ElMessage.error(error.value || '数据处理失败')
      throw err
    } finally {
      loading.value = false
    }
  }

  function clearData() {
    dataInfo.value = null
    dataPreview.value = []
    error.value = null
    targetColumn.value = ''
  }

  function setTargetColumn(column: string) {
    targetColumn.value = column
    if (dataInfo.value) {
      dataInfo.value.target_column = column
    }
  }

  return {
    dataInfo,
    dataPreview,
    loading,
    error,
    targetColumn,
    hasData,
    numericColumnOptions,
    allColumnOptions,
    uploadData,
    fetchDataInfo,
    fetchDataPreview,
    processData,
    clearData,
    setTargetColumn,
  }
})
