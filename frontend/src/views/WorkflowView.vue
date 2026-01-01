<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElTabs, ElTabPane, ElCard, ElSteps, ElStep, ElAlert } from 'element-plus'
import DataStep from '@/components/workflow/DataStep.vue'
import ModelStep from '@/components/workflow/ModelStep.vue'
import PredictStep from '@/components/workflow/PredictStep.vue'
import { useSystemStore } from '@/stores/system'

const systemStore = useSystemStore()
const activeTab = ref('data')

onMounted(() => {
  systemStore.fetchSystemStatus()
})
</script>

<template>
  <div class="workflow-container">
    <ElCard class="workflow-card">
      <template #header>
        <div class="card-header">
          <div class="header-title">
            <img src="/Icons.png" alt="系统图标" class="card-icon" />
            <h2>数据分析与统计系统</h2>
          </div>
          <ElSteps :active="systemStore.currentStepIndex" finish-status="success" simple>
            <ElStep title="Step1 数据" />
            <ElStep title="Step2 模型" />
            <ElStep title="Step3 预测" />
          </ElSteps>
        </div>
      </template>

      <ElAlert
        title="系统使用流程"
        type="info"
        description="请按照以下步骤操作：1. 上传CSV数据文件 → 2. 训练机器学习模型 → 3. 使用模型进行预测"
        show-icon
        :closable="false"
        class="workflow-alert"
      />

      <ElTabs v-model="activeTab" class="workflow-tabs">
        <ElTabPane label="Step1 数据" name="data">
          <DataStep />
        </ElTabPane>
        <ElTabPane label="Step2 模型" name="model" :disabled="!systemStore.canProceedToModelTraining">
          <ModelStep />
        </ElTabPane>
        <ElTabPane label="Step3 预测" name="predict" :disabled="!systemStore.canProceedToPrediction">
          <PredictStep />
        </ElTabPane>
      </ElTabs>
    </ElCard>
  </div>
</template>

<style scoped>
.workflow-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 15px;
}

.workflow-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.card-icon {
  height: 32px;
  width: auto;
}

.card-header h2 {
  margin: 0;
  color: #303133;
}

.workflow-alert {
  margin-bottom: 20px;
}

.workflow-tabs {
  margin-top: 20px;
}

:deep(.el-tabs__content) {
  padding: 20px 0;
}

:deep(.el-step.is-simple .el-step__title) {
  font-size: 14px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .workflow-container {
    padding: 0 10px;
  }
  
  :deep(.el-step.is-simple .el-step__title) {
    font-size: 12px;
  }
}

@media (max-width: 480px) {
  .header-title {
    flex-direction: column;
    align-items: flex-start;
    gap: 5px;
  }
  
  .card-icon {
    height: 24px;
  }
  
  .card-header h2 {
    font-size: 18px;
  }
}
</style>