<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import {
  ElCard,
  ElRow,
  ElCol,
  ElSelect,
  ElOption,
  ElButton,
  ElAlert,
  ElDescriptions,
  ElDescriptionsItem,
  ElProgress,
  ElTag,
  ElSwitch,
  ElSlider,
  ElMessage,
} from 'element-plus'
import { useModelStore } from '@/stores/model'
import { useDataStore } from '@/stores/data'
import { useSystemStore } from '@/stores/system'
import { useSettingsStore } from '@/stores/settings'

const modelStore = useModelStore()
const dataStore = useDataStore()
const systemStore = useSystemStore()
const settingsStore = useSettingsStore()

const selectedModelType = ref(settingsStore.defaultModel)
const testSize = ref(0.2)
const tuneHyperparameters = ref(false)

const selectedTargetColumn = computed({
  get: () => dataStore.targetColumn,
  set: (value) => dataStore.setTargetColumn(value),
})

const hasData = computed(() => dataStore.hasData)
const hasTrainedModel = computed(() => modelStore.hasTrainedModel)
const currentModel = computed(() => modelStore.currentModel)
const availableModelOptions = computed(() => modelStore.availableModelOptions)
const numericColumnOptions = computed(() => dataStore.numericColumnOptions)
const training = computed(() => modelStore.training)
const loading = computed(() => modelStore.loading)

onMounted(async () => {
  await modelStore.fetchAvailableModels()
  await modelStore.fetchTrainedModels()

  selectedModelType.value = settingsStore.defaultModel

  if (
    hasData.value &&
    numericColumnOptions.value &&
    numericColumnOptions.value.length > 0 &&
    !dataStore.targetColumn
  ) {
    dataStore.setTargetColumn(numericColumnOptions.value[0]?.value || '')
  }
})

const handleTrainModel = async () => {
  try {
    await modelStore.trainModel({
      model_type: selectedModelType.value,
      target_column: dataStore.targetColumn,
      test_size: testSize.value,
      tune_hyperparameters: tuneHyperparameters.value,
    })

    systemStore.updateSystemStatus({
      model_trained: true,
      current_step: '预测',
      current_model: selectedModelType.value,
    })
  } catch (error) {
    console.error('模型训练失败:', error)
    systemStore.updateSystemStatus({
      model_trained: false,
      current_step: '模型训练',
    })
  }
}

const getModelAccuracy = () => {
  if (!currentModel.value || !currentModel.value.test_metrics) return 0

  const metrics = currentModel.value.test_metrics
  return metrics.r2 || metrics.r_squared || metrics.accuracy || 0
}

const formatMetricValue = (value: number) => {
  return typeof value === 'number' ? (value * 100).toFixed(2) + '%' : 'N/A'
}
</script>

<template>
  <div class="model-step">
    <ElRow :gutter="20">
      <ElCol :span="24">
        <ElCard class="info-card">
          <template #header>
            <h3>模型说明</h3>
          </template>

          <ElAlert
            title="机器学习模型训练"
            type="info"
            description="本系统支持多种回归模型，包括线性回归、岭回归、随机森林等。选择合适的模型和参数，点击开始训练按钮进行模型训练。"
            show-icon
            :closable="false"
            style="margin-bottom: 20px"
          />

          <p>
            系统将使用您上传的数据训练机器学习模型，训练完成后会显示模型评估指标。训练时间取决于数据量和模型复杂度。
          </p>
        </ElCard>
      </ElCol>
    </ElRow>

    <ElRow :gutter="20" style="margin-top: 20px">
      <ElCol :span="24">
        <ElCard class="config-card">
          <template #header>
            <h3>模型训练配置</h3>
          </template>

          <ElRow :gutter="20">
            <ElCol :span="12">
              <div class="form-item">
                <label>模型类型</label>
                <ElSelect
                  v-model="selectedModelType"
                  placeholder="请选择模型类型"
                  style="width: 100%"
                >
                  <ElOption
                    v-for="option in availableModelOptions"
                    :key="option.value"
                    :label="option.label"
                    :value="option.value"
                  />
                </ElSelect>
              </div>
            </ElCol>
            <ElCol :span="12">
              <div class="form-item">
                <label>目标列</label>
                <ElSelect
                  v-model="selectedTargetColumn"
                  placeholder="请选择目标列"
                  style="width: 100%"
                >
                  <ElOption
                    v-for="option in numericColumnOptions"
                    :key="option.value"
                    :label="option.label"
                    :value="option.value"
                  />
                </ElSelect>
              </div>
            </ElCol>
          </ElRow>

          <ElRow :gutter="20">
            <ElCol :span="12">
              <div class="form-item">
                <label>测试集比例: {{ (testSize * 100).toFixed(0) }}%</label>
                <ElSlider
                  v-model="testSize"
                  :min="0.1"
                  :max="0.5"
                  :step="0.05"
                  show-stops
                  show-input
                  :format-tooltip="(value) => `${(value * 100).toFixed(0)}%`"
                />
              </div>
            </ElCol>
            <ElCol :span="12">
              <div class="form-item">
                <label>超参数调优</label>
                <div style="margin-top: 8px">
                  <ElSwitch v-model="tuneHyperparameters" active-text="开启" inactive-text="关闭" />
                  <div style="margin-top: 5px; color: #909399; font-size: 12px">
                    开启后会自动寻找最优参数，但训练时间会增加
                  </div>
                </div>
              </div>
            </ElCol>
          </ElRow>

          <div class="train-actions">
            <ElButton
              type="primary"
              @click="handleTrainModel"
              :loading="training"
              :disabled="!selectedTargetColumn"
              size="large"
            >
              {{ training ? '正在训练模型...' : '开始训练模型' }}
            </ElButton>
          </div>
        </ElCard>
      </ElCol>
    </ElRow>

    <ElRow v-if="training" :gutter="20" style="margin-top: 20px">
      <ElCol :span="24">
        <ElCard class="progress-card">
          <template #header>
            <h3>训练进度</h3>
          </template>

          <ElAlert
            title="正在训练模型，请稍等..."
            type="info"
            show-icon
            :closable="false"
            style="margin-bottom: 20px"
          />

          <ElProgress :percentage="75" status="success" :show-text="true">
            <template #default="{ percentage }">
              <span class="percentage-value">{{ percentage }}%</span>
            </template>
          </ElProgress>

          <div style="margin-top: 20px; color: #606266">
            <p>模型训练可能需要一些时间，具体取决于数据量和模型复杂度。请耐心等待...</p>
          </div>
        </ElCard>
      </ElCol>
    </ElRow>

    <ElRow v-if="hasTrainedModel && currentModel" :gutter="20" style="margin-top: 20px">
      <ElCol :span="24">
        <ElCard class="result-card">
          <template #header>
            <div class="card-header">
              <h3>模型训练完成</h3>
              <ElTag type="success">训练成功</ElTag>
            </div>
          </template>

          <ElAlert
            title="模型训练完成，已可用于预测"
            type="success"
            show-icon
            :closable="false"
            style="margin-bottom: 20px"
          />

          <ElDescriptions :column="2" border>
            <ElDescriptionsItem label="模型名称">{{ currentModel.model_name }}</ElDescriptionsItem>
            <ElDescriptionsItem label="模型类型">{{ currentModel.model_type }}</ElDescriptionsItem>
            <ElDescriptionsItem label="目标列">{{
              currentModel.target_name || '未知'
            }}</ElDescriptionsItem>
            <ElDescriptionsItem label="特征数量">{{
              currentModel.feature_names ? currentModel.feature_names.length : 0
            }}</ElDescriptionsItem>
            <ElDescriptionsItem label="准确率" :span="2">
              <ElTag type="success" size="large">{{ formatMetricValue(getModelAccuracy()) }}</ElTag>
            </ElDescriptionsItem>
          </ElDescriptions>

          <div
            v-if="currentModel.feature_names && currentModel.feature_names.length > 0"
            style="margin-top: 20px"
          >
            <h4>特征列（数据列）</h4>
            <div class="feature-tags">
              <ElTag
                v-for="(feature, index) in currentModel.feature_names"
                :key="index"
                type="info"
                size="small"
                style="margin-right: 8px; margin-bottom: 8px"
              >
                {{ feature }}
              </ElTag>
            </div>
          </div>

          <div style="margin-top: 20px">
            <h4>模型评估指标</h4>
            <ElRow :gutter="20" style="margin-top: 15px">
              <ElCol :span="12">
                <ElCard shadow="never">
                  <template #header>
                    <h5>训练集指标</h5>
                  </template>
                  <div
                    v-for="(value, key) in currentModel.train_metrics"
                    :key="key"
                    class="metric-item"
                  >
                    <span class="metric-name">{{ key }}:</span>
                    <span class="metric-value">{{
                      typeof value === 'number' ? value.toFixed(4) : value
                    }}</span>
                  </div>
                </ElCard>
              </ElCol>
              <ElCol :span="12">
                <ElCard shadow="never">
                  <template #header>
                    <h5>测试集指标</h5>
                  </template>
                  <div
                    v-for="(value, key) in currentModel.test_metrics"
                    :key="key"
                    class="metric-item"
                  >
                    <span class="metric-name">{{ key }}:</span>
                    <span class="metric-value">{{
                      typeof value === 'number' ? value.toFixed(4) : value
                    }}</span>
                  </div>
                </ElCard>
              </ElCol>
            </ElRow>
          </div>
        </ElCard>
      </ElCol>
    </ElRow>

    <ElRow v-if="!hasData" :gutter="20" style="margin-top: 20px">
      <ElCol :span="24">
        <ElAlert
          title="请先上传并处理数据"
          type="warning"
          description="请先在Step1 数据页面上传CSV数据文件并进行数据处理。"
          show-icon
          :closable="false"
        />
      </ElCol>
    </ElRow>
  </div>
</template>

<style scoped>
.model-step {
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

.form-item {
  margin-bottom: 20px;
}

.form-item label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #606266;
}

.train-actions {
  margin-top: 30px;
  text-align: center;
}

.percentage-value {
  font-size: 16px;
  font-weight: 500;
}

.metric-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #ebeef5;
}

.metric-item:last-child {
  border-bottom: none;
}

.metric-name {
  color: #606266;
}

.metric-value {
  color: #303133;
  font-weight: 500;
}

.feature-tags {
  margin-top: 10px;
  max-height: 120px;
  overflow-y: auto;
  padding: 10px;
  background-color: #f5f7fa;
  border-radius: 4px;
  border: 1px solid #e4e7ed;
}

@media (max-width: 768px) {
  .form-item {
    margin-bottom: 15px;
  }

  .train-actions {
    margin-top: 20px;
  }
}

@media (max-width: 480px) {
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }

  .form-item {
    margin-bottom: 12px;
  }

  .train-actions {
    margin-top: 15px;
  }
}
</style>
