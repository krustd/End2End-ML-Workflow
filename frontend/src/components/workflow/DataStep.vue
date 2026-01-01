<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { ElCard, ElRow, ElCol, ElUpload, ElButton, ElTable, ElTableColumn, ElTag, ElAlert, ElDescriptions, ElDescriptionsItem, ElSelect, ElOption, ElMessage } from 'element-plus'
import { UploadFilled, InfoFilled } from '@element-plus/icons-vue'
import { useDataStore } from '@/stores/data'
import { useSystemStore } from '@/stores/system'
import { useSettingsStore } from '@/stores/settings'

const dataStore = useDataStore()
const systemStore = useSystemStore()
const settingsStore = useSettingsStore()

const uploadRef = ref()
const fileInput = ref()
const selectedFile = ref<File | null>(null)
const previewRows = ref(settingsStore.tablePageSize)

const handleMissingOptions = [
  { label: '删除缺失值', value: 'drop' },
  { label: '均值填充', value: 'mean' },
  { label: '中位数填充', value: 'median' },
  { label: '众数填充', value: 'mode' }
]

const selectedTargetColumn = ref('')
const selectedHandleMissing = ref('drop')

// 监听目标列变化，同步到数据存储
watch(selectedTargetColumn, (newValue) => {
  if (newValue) {
    dataStore.setTargetColumn(newValue)
  }
})

const hasData = computed(() => dataStore.hasData)
const dataInfo = computed(() => dataStore.dataInfo)
const dataPreview = computed(() => dataStore.dataPreview)
const numericColumnOptions = computed(() => dataStore.numericColumnOptions)
const loading = computed(() => dataStore.loading)

onMounted(() => {
  // 使用设置中的默认分页大小
  previewRows.value = settingsStore.tablePageSize
  
  if (hasData.value) {
    dataStore.fetchDataInfo()
    dataStore.fetchDataPreview(previewRows.value)
    
    // 如果数据存储中已有目标列，使用它
    if (dataStore.targetColumn) {
      selectedTargetColumn.value = dataStore.targetColumn
    }
  }
})

const handleFileChange = (file: any) => {
  // Element Plus的文件对象结构：file.raw是实际的File对象
  const actualFile = file.raw || file
  const isCSV = actualFile.type === 'text/csv' || file.name.endsWith('.csv')
  if (!isCSV) {
    ElMessage.error('只能上传CSV格式的文件!')
    return false
  }
  console.log('handleFileChange - 文件对象:', file)
  console.log('handleFileChange - 实际文件:', actualFile)
  return true
}

const handleSimpleFileChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    const file = target.files[0]
    if (file) {
      const isCSV = file.type === 'text/csv' || file.name.endsWith('.csv')
      if (!isCSV) {
        ElMessage.error('只能上传CSV格式的文件!')
        selectedFile.value = null
        return
      }
      selectedFile.value = file
      console.log('选择的文件:', file)
    }
  }
}

const handleSimpleUpload = async () => {
  if (!selectedFile.value) {
    ElMessage.error('请先选择文件')
    return
  }

  try {
    console.log('开始上传文件:', selectedFile.value)
    await dataStore.uploadData(selectedFile.value)
    
    // 只有在上传成功后才更新系统状态
    systemStore.updateSystemStatus({
      data_uploaded: true,
      current_step: '模型训练'
    })
    
    // 获取数据预览
    await dataStore.fetchDataPreview(previewRows.value)
    
    // 清除选择
    selectedFile.value = null
    if (fileInput.value) {
      fileInput.value.value = ''
    }
  } catch (error: any) {
    console.error('上传失败:', error)
    ElMessage.error('文件上传失败: ' + (error.message || '未知错误'))
    
    // 上传失败时确保系统状态正确
    systemStore.updateSystemStatus({
      data_uploaded: false,
      current_step: '数据上传'
    })
  }
}

const clearUploadedFile = () => {
  dataStore.clearData()
  
  // 清除文件时也要更新系统状态
  systemStore.updateSystemStatus({
    data_uploaded: false,
    current_step: '数据上传'
  })
  
  selectedFile.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}


const handleProcessData = async () => {
  try {
    await dataStore.processData({
      handle_missing: selectedHandleMissing.value,
      target_column: selectedTargetColumn.value || undefined
    })
    
    // 更新数据信息和目标列
    await dataStore.fetchDataInfo()
    if (selectedTargetColumn.value) {
      dataStore.setTargetColumn(selectedTargetColumn.value)
    }
  } catch (error) {
    console.error('数据处理失败:', error)
  }
}

const handlePreviewRowsChange = async () => {
  // 更新设置中的分页大小
  settingsStore.updateSettings({ tablePageSize: previewRows.value })
  
  if (hasData.value) {
    await dataStore.fetchDataPreview(previewRows.value)
  }
}

const formatFileSize = (size: number) => {
  if (size < 1024) {
    return size + ' B'
  } else if (size < 1024 * 1024) {
    return (size / 1024).toFixed(2) + ' KB'
  } else {
    return (size / (1024 * 1024)).toFixed(2) + ' MB'
  }
}
</script>

<template>
  <div class="data-step">
    <ElRow :gutter="20">
      <!-- 数据上传区域 -->
      <ElCol :span="24">
        <ElCard class="upload-card">
          <template #header>
            <div class="card-header">
              <h3>1. 上传CSV数据文件</h3>
              <ElTag v-if="hasData" type="success">已上传</ElTag>
            </div>
          </template>
          
          <!-- 使用朴素HTML表单替换Element Plus上传组件 -->
          <div class="simple-upload-form">
            <form @submit.prevent="handleSimpleUpload" enctype="multipart/form-data">
              <div class="form-group">
                <label for="csvFile" class="form-label">选择CSV文件:</label>
                <input
                  type="file"
                  id="csvFile"
                  name="file"
                  accept=".csv"
                  ref="fileInput"
                  @change="handleSimpleFileChange"
                  class="form-input"
                />
              </div>
              
              <div class="file-info" v-if="selectedFile">
                <p><strong>文件名:</strong> {{ selectedFile.name }}</p>
                <p><strong>文件大小:</strong> {{ formatFileSize(selectedFile.size) }}</p>
              </div>
              
              <div class="upload-actions">
                <button
                  type="submit"
                  class="upload-button"
                  :disabled="!selectedFile || loading"
                >
                  {{ loading ? '上传中...' : '上传文件' }}
                </button>
                
                <button
                  v-if="hasData && dataInfo"
                  type="button"
                  class="clear-button"
                  @click="clearUploadedFile"
                >
                  清除文件
                </button>
              </div>
            </form>
          </div>
        </ElCard>
      </ElCol>
    </ElRow>

    <!-- 数据信息区域 -->
    <ElRow v-if="hasData && dataInfo" :gutter="20" style="margin-top: 20px;">
      <ElCol :span="24">
        <ElCard class="info-card">
          <template #header>
            <div class="card-header">
              <h3>2. 数据信息</h3>
              <ElTag type="info">{{ dataInfo.rows_count }} 条数据</ElTag>
            </div>
          </template>
          
          <ElDescriptions :column="2" border>
            <ElDescriptionsItem label="文件名">{{ dataInfo.file_name }}</ElDescriptionsItem>
            <ElDescriptionsItem label="文件大小">{{ formatFileSize(dataInfo.file_size) }}</ElDescriptionsItem>
            <ElDescriptionsItem label="行数">{{ dataInfo.rows_count }}</ElDescriptionsItem>
            <ElDescriptionsItem label="列数">{{ dataInfo.columns_count }}</ElDescriptionsItem>
            <ElDescriptionsItem label="数值列" :span="2">
              <ElTag v-for="col in dataInfo.numeric_columns" :key="col" size="small" style="margin-right: 5px;">
                {{ col }}
              </ElTag>
            </ElDescriptionsItem>
            <ElDescriptionsItem label="分类列" :span="2">
              <ElTag v-for="col in dataInfo.categorical_columns" :key="col" type="info" size="small" style="margin-right: 5px;">
                {{ col }}
              </ElTag>
            </ElDescriptionsItem>
          </ElDescriptions>
        </ElCard>
      </ElCol>
    </ElRow>

    <!-- 数据预览区域 -->
    <ElRow v-if="hasData" :gutter="20" style="margin-top: 20px;">
      <ElCol :span="24">
        <ElCard class="preview-card">
          <template #header>
            <div class="card-header">
              <h3>3. 数据预览</h3>
              <div class="preview-controls">
                <ElSelect v-model="previewRows" @change="handlePreviewRowsChange" style="width: 120px; margin-right: 10px;">
                  <ElOption label="10行" :value="10" />
                  <ElOption label="20行" :value="20" />
                  <ElOption label="50行" :value="50" />
                  <ElOption label="100行" :value="100" />
                </ElSelect>
                <ElButton size="small" @click="handlePreviewRowsChange">刷新</ElButton>
              </div>
            </div>
          </template>
          
          <ElTable :data="dataPreview" border stripe v-loading="loading" max-height="400">
            <ElTableColumn
              v-for="column in dataInfo?.columns || []"
              :key="column"
              :prop="column"
              :label="column"
              show-overflow-tooltip
            />
          </ElTable>
        </ElCard>
      </ElCol>
    </ElRow>

    <!-- 数据处理区域 -->
    <ElRow v-if="hasData && dataInfo" :gutter="20" style="margin-top: 20px;">
      <ElCol :span="24">
        <ElCard class="process-card">
          <template #header>
            <div class="card-header">
              <h3>4. 数据处理</h3>
            </div>
          </template>
          
          <ElAlert
            title="数据处理说明"
            type="info"
            description="选择目标列和缺失值处理方式，然后点击处理数据按钮。处理后的数据将用于模型训练。"
            show-icon
            :closable="false"
            style="margin-bottom: 20px;"
          />
          
          <ElRow :gutter="20">
            <ElCol :span="12">
              <div class="form-item">
                <label>目标列（预测目标）</label>
                <ElSelect v-model="selectedTargetColumn" placeholder="请选择目标列" style="width: 100%;">
                  <ElOption
                    v-for="option in numericColumnOptions"
                    :key="option.value"
                    :label="option.label"
                    :value="option.value"
                  />
                </ElSelect>
              </div>
            </ElCol>
            <ElCol :span="12">
              <div class="form-item">
                <label>缺失值处理方式</label>
                <ElSelect v-model="selectedHandleMissing" style="width: 100%;">
                  <ElOption
                    v-for="option in handleMissingOptions"
                    :key="option.value"
                    :label="option.label"
                    :value="option.value"
                  />
                </ElSelect>
              </div>
            </ElCol>
          </ElRow>
          
          <div class="process-actions">
            <ElButton type="primary" @click="handleProcessData" :loading="loading">
              处理数据
            </ElButton>
          </div>
        </ElCard>
      </ElCol>
    </ElRow>

    <!-- 提示信息 -->
    <ElRow v-if="!hasData" :gutter="20" style="margin-top: 20px;">
      <ElCol :span="24">
        <ElAlert
          title="请先上传数据"
          type="warning"
          description="请上传CSV格式的数据文件，例如房价数据、销售数据或实验数据。"
          show-icon
          :closable="false"
        >
          <template #icon>
            <ElIcon><InfoFilled /></ElIcon>
          </template>
        </ElAlert>
      </ElCol>
    </ElRow>
  </div>
</template>

<style scoped>
.data-step {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  color: #303133;
}

.upload-demo {
  width: 100%;
}

.upload-actions {
  margin-top: 20px;
  text-align: center;
}

.preview-controls {
  display: flex;
  align-items: center;
}

.form-item {
  margin-bottom: 20px;
}

.form-item label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #606266;
}

.process-actions {
  margin-top: 20px;
  text-align: center;
}

.simple-upload-form {
  width: 100%;
  padding: 20px;
  border: 2px dashed #d9d9d9;
  border-radius: 6px;
  text-align: center;
  background-color: #fafafa;
  transition: border-color 0.3s;
}

.simple-upload-form:hover {
  border-color: #409eff;
}

.form-group {
  margin-bottom: 20px;
}

.form-label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #606266;
}

.form-input {
  width: 100%;
  padding: 8px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 14px;
}

.file-info {
  margin: 15px 0;
  padding: 10px;
  background-color: #f5f7fa;
  border-radius: 4px;
  text-align: left;
}

.file-info p {
  margin: 5px 0;
  font-size: 14px;
}

.upload-button {
  background-color: #409eff;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  margin-right: 10px;
  transition: background-color 0.3s;
}

.upload-button:hover:not(:disabled) {
  background-color: #66b1ff;
}

.upload-button:disabled {
  background-color: #a0cfff;
  cursor: not-allowed;
}

.clear-button {
  background-color: #f56c6c;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s;
}

.clear-button:hover {
  background-color: #f78989;
}

:deep(.el-upload-dragger) {
  width: 100%;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .upload-actions {
    margin-top: 15px;
  }
  
  .form-item {
    margin-bottom: 15px;
  }
  
  .process-actions {
    margin-top: 20px;
  }
  
  .preview-controls {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
}

@media (max-width: 480px) {
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .upload-actions {
    margin-top: 10px;
  }
  
  .form-item {
    margin-bottom: 12px;
  }
  
  .process-actions {
    margin-top: 15px;
  }
}
</style>