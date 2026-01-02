<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElCard, ElRow, ElCol, ElDescriptions, ElDescriptionsItem, ElTag, ElSelect, ElOption, ElSwitch, ElAlert, ElDivider } from 'element-plus'
import { useSystemStore } from '@/stores/system'
import { useModelStore } from '@/stores/model'
import { useSettingsStore } from '@/stores/settings'

const systemStore = useSystemStore()
const modelStore = useModelStore()
const settingsStore = useSettingsStore()

const selectedModel = ref(settingsStore.defaultModel)
const themeColor = ref(settingsStore.themeColor)
const tablePageSize = ref(settingsStore.tablePageSize)

const systemStatus = computed(() => systemStore.systemStatus)
const availableModelOptions = computed(() => modelStore.availableModelOptions)

onMounted(async () => {
  await systemStore.fetchSystemStatus()
  await modelStore.fetchAvailableModels()
  
  selectedModel.value = settingsStore.defaultModel
})

const handleModelChange = (value: string) => {
  selectedModel.value = value
  settingsStore.updateSettings({ defaultModel: value })
  systemStore.updateSystemStatus({ current_model: value })
}

const handleThemeChange = (value: string) => {
  themeColor.value = value
  settingsStore.updateSettings({ themeColor: value })
}

const handlePageSizeChange = (value: number) => {
  tablePageSize.value = value
  settingsStore.updateSettings({ tablePageSize: value })
}

const getStepStatus = (step: string) => {
  if (systemStatus.value.current_step === step) {
    return 'warning'
  }
  
  if (step === '数据上传' && systemStatus.value.data_uploaded) {
    return 'success'
  }
  
  if (step === '模型训练' && systemStatus.value.model_trained) {
    return 'success'
  }
  
  if (step === '预测' && systemStatus.value.model_trained) {
    return 'success'
  }
  
  return 'info'
}

const getStepText = (step: string) => {
  if (systemStatus.value.current_step === step) {
    return '进行中'
  }
  
  if (step === '数据上传' && systemStatus.value.data_uploaded) {
    return '已完成'
  }
  
  if (step === '模型训练' && systemStatus.value.model_trained) {
    return '已完成'
  }
  
  if (step === '预测' && systemStatus.value.model_trained) {
    return '可进行'
  }
  
  return '未开始'
}

const getModelDisplayName = (modelType: string) => {
  const modelNames: Record<string, string> = {
    'linear_regression': '线性回归',
    'ridge': '岭回归',
    'lasso': 'Lasso回归',
    'elastic_net': '弹性网络',
    'random_forest': '随机森林',
    'gradient_boosting': '梯度提升',
    'svr': '支持向量回归',
    'decision_tree': '决策树',
    'knn': 'K近邻'
  }
  return modelNames[modelType] || modelType
}
</script>

<template>
  <div class="settings-container">
    <ElRow :gutter="20">
      <ElCol :span="24">
        <ElCard class="status-card">
          <template #header>
            <h3>当前系统状态</h3>
          </template>
          
          <ElDescriptions :column="2" border>
            <ElDescriptionsItem label="数据上传状态">
              <ElTag :type="systemStatus.data_uploaded ? 'success' : 'danger'">
                {{ systemStatus.data_uploaded ? '已上传' : '未上传' }}
              </ElTag>
            </ElDescriptionsItem>
            <ElDescriptionsItem label="模型训练状态">
              <ElTag :type="systemStatus.model_trained ? 'success' : 'danger'">
                {{ systemStatus.model_trained ? '已训练' : '未训练' }}
              </ElTag>
            </ElDescriptionsItem>
            <ElDescriptionsItem label="当前步骤">
              <ElTag type="warning">{{ systemStatus.current_step }}</ElTag>
            </ElDescriptionsItem>
            <ElDescriptionsItem label="当前模型">
              <ElTag type="primary">{{ getModelDisplayName(systemStatus.current_model) }}</ElTag>
            </ElDescriptionsItem>
          </ElDescriptions>
          
          <ElDivider content-position="left">流程进度</ElDivider>
          
          <ElRow :gutter="20">
            <ElCol :span="8">
              <ElCard shadow="never" class="step-card">
                <div class="step-content">
                  <h4>数据上传</h4>
                  <ElTag :type="getStepStatus('数据上传')" size="large">
                    {{ getStepText('数据上传') }}
                  </ElTag>
                </div>
              </ElCard>
            </ElCol>
            <ElCol :span="8">
              <ElCard shadow="never" class="step-card">
                <div class="step-content">
                  <h4>模型训练</h4>
                  <ElTag :type="getStepStatus('模型训练')" size="large">
                    {{ getStepText('模型训练') }}
                  </ElTag>
                </div>
              </ElCard>
            </ElCol>
            <ElCol :span="8">
              <ElCard shadow="never" class="step-card">
                <div class="step-content">
                  <h4>预测</h4>
                  <ElTag :type="getStepStatus('预测')" size="large">
                    {{ getStepText('预测') }}
                  </ElTag>
                </div>
              </ElCard>
            </ElCol>
          </ElRow>
        </ElCard>
      </ElCol>
      
      <ElCol :span="24" style="margin-top: 20px;">
        <ElCard class="behavior-card">
          <template #header>
            <h3>默认行为说明</h3>
          </template>
          
          <ElAlert
            title="系统默认行为"
            type="info"
            description="了解系统的默认行为，以便更好地使用系统功能。"
            show-icon
            :closable="false"
            style="margin-bottom: 20px;"
          />
          
          <ElRow :gutter="20">
            <ElCol :span="12">
              <ElCard shadow="never" class="behavior-item">
                <h4>数据处理</h4>
                <p>每次上传数据会覆盖旧数据，确保当前使用的是最新的数据集。</p>
              </ElCard>
            </ElCol>
            <ElCol :span="12">
              <ElCard shadow="never" class="behavior-item">
                <h4>模型训练</h4>
                <p>模型训练基于最新上传的数据，确保数据质量对模型性能至关重要。</p>
              </ElCard>
            </ElCol>
          </ElRow>
          
          <ElRow :gutter="20" style="margin-top: 15px;">
            <ElCol :span="12">
              <ElCard shadow="never" class="behavior-item">
                <h4>预测结果</h4>
                <p>预测结果来自最近一次训练的模型，确保使用正确的模型进行预测。</p>
              </ElCard>
            </ElCol>
            <ElCol :span="12">
              <ElCard shadow="never" class="behavior-item">
                <h4>数据安全</h4>
                <p>所有数据仅在当前会话中保存，刷新页面或关闭浏览器将清除所有数据。</p>
              </ElCard>
            </ElCol>
          </ElRow>
        </ElCard>
      </ElCol>
      
      <ElCol :span="24" style="margin-top: 20px;">
        <ElCard class="display-card">
          <template #header>
            <h3>显示与体验设置</h3>
          </template>
          
          <ElRow :gutter="20">
            <ElCol :span="8">
              <div class="setting-item">
                <label>默认模型</label>
                <ElSelect v-model="selectedModel" @change="handleModelChange" style="width: 100%;">
                  <ElOption
                    v-for="option in availableModelOptions"
                    :key="option.value"
                    :label="option.label"
                    :value="option.value"
                  />
                </ElSelect>
                <div class="setting-desc">选择默认使用的机器学习模型</div>
              </div>
            </ElCol>
            <ElCol :span="8">
              <div class="setting-item">
                <label>主题颜色</label>
                <ElSelect v-model="themeColor" @change="handleThemeChange" style="width: 100%;">
                  <ElOption label="默认蓝色" value="#409eff" />
                  <ElOption label="成功绿色" value="#67c23a" />
                  <ElOption label="警告橙色" value="#e6a23c" />
                  <ElOption label="危险红色" value="#f56c6c" />
                </ElSelect>
                <div class="setting-desc">选择系统主题颜色</div>
              </div>
            </ElCol>
            <ElCol :span="8">
              <div class="setting-item">
                <label>表格每页显示行数</label>
                <ElSelect v-model="tablePageSize" @change="handlePageSizeChange" style="width: 100%;">
                  <ElOption label="10行" :value="10" />
                  <ElOption label="20行" :value="20" />
                  <ElOption label="50行" :value="50" />
                </ElSelect>
                <div class="setting-desc">设置数据表格每页显示的行数</div>
              </div>
            </ElCol>
          </ElRow>
        </ElCard>
      </ElCol>
      
      <ElCol :span="24" style="margin-top: 20px;">
        <ElCard class="about-card">
          <template #header>
            <h3>关于本系统</h3>
          </template>
          
          <ElDescriptions :column="2" border>
            <ElDescriptionsItem label="系统名称">基于机器学习的数据分析与统计系统</ElDescriptionsItem>
            <ElDescriptionsItem label="版本号">v1.0.0</ElDescriptionsItem>
            <ElDescriptionsItem label="适用场景" :span="2">
              适用于各种数据分析场景，如房价预测、销售预测、实验数据分析等
            </ElDescriptionsItem>
            <ElDescriptionsItem label="技术栈" :span="2">
              前端：Vue3 + Element Plus + TypeScript<br>
              后端：Go + GoFrame<br>
              机器学习：Python + Scikit-learn
            </ElDescriptionsItem>
          </ElDescriptions>
          
          <ElDivider content-position="left">免责声明</ElDivider>
          
          <ElAlert
            title="预测结果仅供参考，不构成决策建议"
            type="warning"
            description="本系统提供的预测结果仅供参考，不能作为专业决策的唯一依据。在使用预测结果进行重要决策前，请咨询相关领域的专业人士。"
            show-icon
            :closable="false"
          />
        </ElCard>
      </ElCol>
    </ElRow>
  </div>
</template>

<style scoped>
.settings-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 15px;
}

.status-card, .behavior-card, .display-card, .about-card {
  margin-bottom: 20px;
}

.status-card h3, .behavior-card h3, .display-card h3, .about-card h3 {
  margin: 0;
  color: #303133;
}

.step-card {
  text-align: center;
  height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.step-content h4 {
  margin: 0 0 10px 0;
  color: #303133;
}

.behavior-item {
  height: 100px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.behavior-item h4 {
  margin: 0 0 10px 0;
  color: #409eff;
}

.behavior-item p {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.setting-item {
  margin-bottom: 20px;
}

.setting-item label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #606266;
}

.setting-desc {
  margin-top: 5px;
  color: #909399;
  font-size: 12px;
}

@media (max-width: 768px) {
  .settings-container {
    padding: 0 10px;
  }
  
  .step-card {
    height: 120px;
    margin-bottom: 10px;
  }
  
  .behavior-item {
    height: auto;
    padding: 15px 0;
  }
}

@media (max-width: 480px) {
  .step-card {
    height: auto;
    padding: 15px 10px;
  }
  
  .step-content h4 {
    font-size: 14px;
  }
  
  .behavior-item h4 {
    font-size: 15px;
  }
  
  .behavior-item p {
    font-size: 13px;
  }
}
</style>