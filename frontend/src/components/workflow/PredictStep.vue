<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElCard, ElRow, ElCol, ElForm, ElFormItem, ElInput, ElButton, ElAlert, ElDescriptions, ElDescriptionsItem, ElSelect, ElOption, ElTable, ElTableColumn, ElTag, ElMessage } from 'element-plus'
import { usePredictStore } from '@/stores/predict'
import { useModelStore } from '@/stores/model'
import { useDataStore } from '@/stores/data'
import { useSettingsStore } from '@/stores/settings'

const predictStore = usePredictStore()
const modelStore = useModelStore()
const dataStore = useDataStore()
const settingsStore = useSettingsStore()

const predictForm = ref({
  data: {} as Record<string, any>,
  model_name: ''
})

const batchData = ref<Record<string, any>[]>([])
const selectedModel = ref('')
const exportFormat = ref('csv')

const hasData = computed(() => dataStore.hasData)
const hasTrainedModel = computed(() => modelStore.hasTrainedModel)
const currentModel = computed(() => modelStore.currentModel)
const predictionResult = computed(() => predictStore.predictionResult)
const batchPredictionResult = computed(() => predictStore.batchPredictionResult)
const loading = computed(() => predictStore.loading)
const trainedModelOptions = computed(() => modelStore.trainedModelOptions)
const allColumnOptions = computed(() => dataStore.allColumnOptions)

onMounted(async () => {
  await modelStore.fetchTrainedModels()
  
  // 如果有当前模型，设置为默认选择
  if (currentModel.value) {
    selectedModel.value = currentModel.value.model_name
    predictForm.value.model_name = currentModel.value.model_name
  } else {
    // 如果没有当前模型，使用设置中的默认模型
    selectedModel.value = settingsStore.defaultModel
    predictForm.value.model_name = settingsStore.defaultModel
  }
  
  // 初始化预测表单
  if (allColumnOptions.value) {
    allColumnOptions.value.forEach(col => {
      // 目标列不需要输入值
      predictForm.value.data[col.value] = col.value === dataStore.targetColumn ? null : ''
    })
  }
})

const handlePredict = async () => {
  try {
    await predictStore.predict({
      data: predictForm.value.data,
      model_name: selectedModel.value
    })
  } catch (error) {
    console.error('预测失败:', error)
  }
}

const handleBatchPredict = async () => {
  try {
    await predictStore.batchPredict(batchData.value, selectedModel.value)
  } catch (error) {
    console.error('批量预测失败:', error)
  }
}

const handleExportPredictions = async () => {
  try {
    await predictStore.exportPredictions(batchData.value, exportFormat.value, selectedModel.value)
  } catch (error) {
    console.error('导出预测结果失败:', error)
  }
}

const addBatchDataRow = () => {
  const newRow: Record<string, any> = {}
  if (allColumnOptions.value) {
    allColumnOptions.value.forEach(col => {
      // 目标列不需要输入值
      newRow[col.value] = col.value === dataStore.targetColumn ? null : ''
    })
  }
  batchData.value.push(newRow)
}

const removeBatchDataRow = (index: number) => {
  batchData.value.splice(index, 1)
}

const clearBatchData = () => {
  batchData.value = []
}

const resetPredictForm = () => {
  if (allColumnOptions.value) {
    allColumnOptions.value.forEach(col => {
      // 目标列不需要输入值
      predictForm.value.data[col.value] = col.value === dataStore.targetColumn ? null : ''
    })
  }
}

const handleModelChange = (value: string) => {
  selectedModel.value = value
  predictForm.value.model_name = value
}
</script>

<template>
  <div class="predict-step">
    <!-- 单条预测 -->
    <ElRow :gutter="20">
      <ElCol :span="24">
        <ElCard class="single-predict-card">
          <template #header>
            <h3>1. 单条预测</h3>
          </template>
          
          <ElAlert
            title="输入特征值进行预测"
            type="info"
            description="请填写各特征的值，然后点击开始预测按钮。系统将使用已训练的模型进行预测。"
            show-icon
            :closable="false"
            style="margin-bottom: 20px;"
          />
          
          <ElRow :gutter="20">
            <ElCol :span="16">
              <ElForm label-width="120px">
                <ElFormItem label="选择模型">
                  <ElSelect v-model="selectedModel" @change="handleModelChange" placeholder="请选择模型" style="width: 100%;">
                    <ElOption
                      v-for="option in trainedModelOptions"
                      :key="option.value"
                      :label="option.label"
                      :value="option.value"
                    />
                  </ElSelect>
                </ElFormItem>
                
                <ElFormItem v-for="column in allColumnOptions" :key="column.value" :label="column.label">
                  <ElInput
                    v-model="predictForm.data[column.value]"
                    :placeholder="`请输入${column.label}`"
                    type="number"
                    step="any"
                    :disabled="column.value === dataStore.targetColumn"
                  />
                  <div v-if="column.value === dataStore.targetColumn" style="color: #909399; font-size: 12px; margin-top: 5px;">
                    这是目标列，将在预测中输出，无需输入
                  </div>
                </ElFormItem>
              </ElForm>
            </ElCol>
            <ElCol :span="8">
              <div class="predict-actions">
                <ElButton 
                  type="primary" 
                  @click="handlePredict" 
                  :loading="loading"
                  :disabled="!selectedModel"
                  size="large"
                  style="width: 100%; margin-bottom: 15px;"
                >
                  开始预测
                </ElButton>
                <ElButton @click="resetPredictForm" size="large" style="width: 100%;">
                  重置表单
                </ElButton>
              </div>
              
              <!-- 预测结果 -->
              <div v-if="predictionResult" class="prediction-result">
                <ElCard shadow="always">
                  <template #header>
                    <h4>预测结果</h4>
                  </template>
                  <ElDescriptions :column="1" border>
                    <ElDescriptionsItem label="预测值">
                      <ElTag type="success" size="large">{{ predictionResult.prediction.toFixed(4) }}</ElTag>
                    </ElDescriptionsItem>
                    <ElDescriptionsItem label="使用模型">{{ predictionResult.model_name }}</ElDescriptionsItem>
                    <ElDescriptionsItem label="预测时间">{{ predictionResult.timestamp }}</ElDescriptionsItem>
                  </ElDescriptions>
                </ElCard>
              </div>
            </ElCol>
          </ElRow>
        </ElCard>
      </ElCol>
    </ElRow>

    <!-- 批量预测 -->
    <ElRow :gutter="20" style="margin-top: 20px;">
      <ElCol :span="24">
        <ElCard class="batch-predict-card">
          <template #header>
            <div class="card-header">
              <h3>2. 批量预测</h3>
              <div class="batch-actions">
                <ElButton @click="addBatchDataRow" type="primary" size="small">添加行</ElButton>
                <ElButton @click="clearBatchData" size="small">清空数据</ElButton>
              </div>
            </div>
          </template>
          
          <ElAlert
            title="批量预测说明"
            type="info"
            description="可以添加多行数据进行批量预测，预测完成后可以导出结果。"
            show-icon
            :closable="false"
            style="margin-bottom: 20px;"
          />
          
          <ElTable :data="batchData" border stripe style="margin-bottom: 20px;">
            <ElTableColumn type="index" label="序号" width="60" />
            <ElTableColumn
              v-for="column in allColumnOptions"
              :key="column.value"
              :label="column.label"
              :prop="column.value"
            >
              <template #default="scope">
                <ElInput
                  v-model="scope.row[column.value]"
                  size="small"
                  type="number"
                  step="any"
                  placeholder="输入值"
                  :disabled="column.value === dataStore.targetColumn"
                />
                <div v-if="column.value === dataStore.targetColumn" style="color: #909399; font-size: 10px;">
                  目标列
                </div>
              </template>
            </ElTableColumn>
            <ElTableColumn label="操作" width="80">
              <template #default="scope">
                <ElButton 
                  type="danger" 
                  size="small" 
                  @click="removeBatchDataRow(scope.$index)"
                  link
                >
                  删除
                </ElButton>
              </template>
            </ElTableColumn>
          </ElTable>
          
          <div class="batch-predict-controls">
            <ElRow :gutter="20">
              <ElCol :span="8">
                <ElSelect v-model="selectedModel" @change="handleModelChange" placeholder="请选择模型" style="width: 100%;">
                  <ElOption
                    v-for="option in trainedModelOptions"
                    :key="option.value"
                    :label="option.label"
                    :value="option.value"
                  />
                </ElSelect>
              </ElCol>
              <ElCol :span="8">
                <ElButton 
                  type="primary" 
                  @click="handleBatchPredict" 
                  :loading="loading"
                  :disabled="!selectedModel || batchData.length === 0"
                  style="width: 100%;"
                >
                  批量预测
                </ElButton>
              </ElCol>
              <ElCol :span="8">
                <ElSelect v-model="exportFormat" style="width: 100%;">
                  <ElOption label="CSV格式" value="csv" />
                  <ElOption label="Excel格式" value="excel" />
                  <ElOption label="JSON格式" value="json" />
                </ElSelect>
              </ElCol>
            </ElRow>
            
            <div style="margin-top: 15px;">
              <ElButton 
                @click="handleExportPredictions"
                :disabled="!batchPredictionResult || !batchPredictionResult.predictions.length"
                style="width: 100%;"
              >
                导出预测结果
              </ElButton>
            </div>
          </div>
          
          <!-- 批量预测结果 -->
          <div v-if="batchPredictionResult && batchPredictionResult.predictions.length" style="margin-top: 20px;">
            <ElCard shadow="always">
              <template #header>
                <h4>批量预测结果</h4>
              </template>
              <ElDescriptions :column="2" border>
                <ElDescriptionsItem label="预测数量">{{ batchPredictionResult.total_samples }}</ElDescriptionsItem>
                <ElDescriptionsItem label="使用模型">{{ batchPredictionResult.model_name }}</ElDescriptionsItem>
                <ElDescriptionsItem label="预测时间" :span="2">{{ batchPredictionResult.timestamp }}</ElDescriptionsItem>
              </ElDescriptions>
              
              <div style="margin-top: 15px;">
                <h5>预测值列表</h5>
                <ElTable :data="batchPredictionResult.predictions.map((value, index) => ({ index: index + 1, value }))" border stripe max-height="200">
                  <ElTableColumn prop="index" label="序号" width="80" />
                  <ElTableColumn prop="value" label="预测值">
                    <template #default="scope">
                      <ElTag type="success">{{ scope.row.value.toFixed(4) }}</ElTag>
                    </template>
                  </ElTableColumn>
                </ElTable>
              </div>
            </ElCard>
          </div>
        </ElCard>
      </ElCol>
    </ElRow>

    <!-- 提示信息 -->
    <ElRow v-if="!hasTrainedModel" :gutter="20" style="margin-top: 20px;">
      <ElCol :span="24">
        <ElAlert
          title="请先训练模型"
          type="warning"
          description="请先在Step2 模型页面训练机器学习模型。"
          show-icon
          :closable="false"
        />
      </ElCol>
    </ElRow>
    
    <ElRow v-if="!hasData" :gutter="20" style="margin-top: 20px;">
      <ElCol :span="24">
        <ElAlert
          title="请先上传数据"
          type="warning"
          description="请先在Step1 数据页面上传CSV数据文件。"
          show-icon
          :closable="false"
        />
      </ElCol>
    </ElRow>
  </div>
</template>

<style scoped>
.predict-step {
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

.batch-actions {
  display: flex;
  gap: 10px;
}

.predict-actions {
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 4px;
  margin-bottom: 20px;
}

.prediction-result {
  margin-top: 20px;
}

.batch-predict-controls {
  background-color: #f8f9fa;
  padding: 15px;
  border-radius: 4px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .predict-actions {
    padding: 15px;
  }
  
  .batch-predict-controls {
    padding: 10px;
  }
}

@media (max-width: 480px) {
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .predict-actions {
    padding: 10px;
  }
  
  .batch-actions {
    flex-direction: column;
    gap: 5px;
  }
}
</style>