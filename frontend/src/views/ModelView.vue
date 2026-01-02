<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElCard, ElRow, ElCol, ElAlert } from 'element-plus'
import ModelManager from '@/components/model/ModelManager.vue'
import { useSystemStore } from '@/stores/system'

const systemStore = useSystemStore()

onMounted(() => {
  systemStore.fetchSystemStatus()
})
</script>

<template>
  <div class="model-container">
    <ElCard class="model-card">
      <template #header>
        <div class="card-header">
          <div class="header-title">
            <img src="/Icons.png" alt="系统图标" class="card-icon" />
            <h2>模型管理</h2>
          </div>
        </div>
      </template>

      <ElAlert
        title="模型管理"
        type="info"
        description="在这里您可以管理所有本地存储的机器学习模型，包括查看、导入、导出、删除模型，以及使用已训练的模型进行预测。"
        show-icon
        :closable="false"
        class="model-alert"
      />

      <div class="model-content">
        <ModelManager />
      </div>
    </ElCard>
  </div>
</template>

<style scoped>
.model-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 15px;
}

.model-card {
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

.model-alert {
  margin-bottom: 20px;
}

.model-content {
  margin-top: 20px;
}

@media (max-width: 768px) {
  .model-container {
    padding: 0 10px;
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
