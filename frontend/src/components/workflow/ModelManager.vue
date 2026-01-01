<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElCard, ElRow, ElCol, ElTable, ElTableColumn, ElButton, ElTag, ElDialog, ElAlert, ElMessage, ElSpace, ElPopconfirm } from 'element-plus'
import ModelStorage from '@/utils/modelStorage'
import type { ModelInfo } from '@/utils/modelStorage'
import { useModelStore } from '@/stores/model'
import { usePredictStore } from '@/stores/predict'

const modelStore = useModelStore()
const predictStore = usePredictStore()

const modelList = ref<ModelInfo[]>([])
const selectedModels = ref<string[]>([])
const dialogVisible = ref(false)
const importDialogVisible = ref(false)
const currentModel = ref<ModelInfo | null>(null)
const importFile = ref<File | null>(null)
const fileInput = ref<HTMLInputElement | null>(null)

onMounted(() => {
  loadModelList()
})

const loadModelList = () => {
  modelList.value = ModelStorage.getModelInfos()
}

const handleSelect = (selection: ModelInfo[]) => {
  selectedModels.value = selection.map(model => model.model_name)
}

const handleView = (model: ModelInfo) => {
  currentModel.value = model
  dialogVisible.value = true
}

const handleDelete = (modelName: string) => {
  ModelStorage.deleteModel(modelName)
  loadModelList()
  // 如果删除的是当前模型，清空当前模型
  if (modelStore.currentModel?.model_name === modelName) {
    modelStore.setCurrentModel(null)
  }
}

const handleExport = (modelName: string) => {
  ModelStorage.exportModel(modelName)
}

const handleImport = () => {
  importDialogVisible.value = true
}

const handleFileChange = (file: File | null) => {
  importFile.value = file
}

const handleImportConfirm = async () => {
  if (!importFile.value) {
    ElMessage.warning('请选择要导入的模型文件')
    return
  }
  
  try {
    await ModelStorage.importModel(importFile.value)
    loadModelList()
    importDialogVisible.value = false
    importFile.value = null
  } catch (error) {
    console.error('导入模型失败:', error)
  }
}

const handleClearAll = () => {
  ModelStorage.clearAllModels()
  loadModelList()
  modelStore.setCurrentModel(null)
}

const handleUseModel = (model: ModelInfo) => {
  // 设置当前模型
  modelStore.setCurrentModel({
    model_name: model.model_name,
    model_type: model.model_type,
    train_metrics: model.train_metrics,
    test_metrics: model.test_metrics,
    cv_scores: model.cv_metrics,
    feature_names: model.feature_names,
    target_name: model.target_name
  })
  
  ElMessage.success(`已选择模型: ${model.model_name}`)
}

const storageUsage = computed(() => {
  return ModelStorage.getStorageUsage()
})

const formatStorageSize = (bytes: number) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const getModelTypeTag = (modelType: string) => {
  const typeMap: Record<string, string> = {
    'linear_regression': 'primary',
    'ridge': 'success',
    'lasso': 'info',
    'elastic_net': 'warning',
    'random_forest': 'danger',
    'gradient_boosting': 'success',
    'svr': 'info',
    'decision_tree': 'warning',
    'knn': 'danger'
  }
  return typeMap[modelType] || 'info'
}

const getModelTypeDisplayName = (modelType: string) => {
  const nameMap: Record<string, string> = {
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
  return nameMap[modelType] || modelType
}
</script>

<template>
  <div class="model-manager">
    <ElRow :gutter="20">
      <ElCol :span="24">
        <ElCard class="storage-info-card">
          <template #header>
            <div class="card-header">
              <h3>模型存储管理</h3>
              <div class="storage-usage">
                <span>存储使用: {{ formatStorageSize(storageUsage.used) }} / {{ formatStorageSize(storageUsage.total) }} ({{ storageUsage.percentage }}%)</span>
              </div>
            </div>
          </template>
          
          <ElRow :gutter="20">
            <ElCol :span="16">
              <ElAlert
                title="模型管理说明"
                type="info"
                description="这里管理所有本地存储的机器学习模型。您可以查看、导出、删除模型，或者导入新的模型。模型存储在浏览器的本地存储中，不会占用服务器空间。"
                show-icon
                :closable="false"
                style="margin-bottom: 20px;"
              />
            </ElCol>
            <ElCol :span="8">
              <ElSpace>
                <ElButton type="primary" @click="handleImport">导入模型</ElButton>
                <ElPopconfirm
                  title="确定要清空所有模型吗？"
                  confirm-button-text="确定"
                  cancel-button-text="取消"
                  @confirm="handleClearAll"
                >
                  <template #reference>
                    <ElButton type="danger">清空所有</ElButton>
                  </template>
                </ElPopconfirm>
              </ElSpace>
            </ElCol>
          </ElRow>
        </ElCard>
      </ElCol>
    </ElRow>

    <ElRow :gutter="20" style="margin-top: 20px;">
      <ElCol :span="24">
        <ElCard class="model-list-card">
          <template #header>
            <h3>模型列表</h3>
          </template>
          
          <ElTable
            :data="modelList"
            style="width: 100%"
            @selection-change="handleSelect"
          >
            <ElTableColumn type="selection" width="55" />
            <ElTableColumn prop="model_name" label="模型名称" width="200" />
            <ElTableColumn prop="model_type" label="模型类型" width="150">
              <template #default="scope">
                <ElTag :type="getModelTypeTag(scope.row.model_type) as any">
                  {{ getModelTypeDisplayName(scope.row.model_type) }}
                </ElTag>
              </template>
            </ElTableColumn>
            <ElTableColumn prop="target_name" label="目标列" width="150" />
            <ElTableColumn prop="feature_names" label="特征数量" width="120">
              <template #default="scope">
                {{ scope.row.feature_names?.length || 0 }}
              </template>
            </ElTableColumn>
            <ElTableColumn prop="test_metrics.r2" label="R²分数" width="120">
              <template #default="scope">
                {{ (scope.row.test_metrics?.r2 || 0).toFixed(4) }}
              </template>
            </ElTableColumn>
            <ElTableColumn prop="created_at" label="创建时间" width="180">
              <template #default="scope">
                {{ new Date(scope.row.created_at).toLocaleString() }}
              </template>
            </ElTableColumn>
            <ElTableColumn label="操作" width="220">
              <template #default="scope">
                <ElSpace>
                  <ElButton size="small" @click="handleView(scope.row)">详情</ElButton>
                  <ElButton size="small" type="primary" @click="handleUseModel(scope.row)">使用</ElButton>
                  <ElButton size="small" @click="handleExport(scope.row.model_name)">导出</ElButton>
                  <ElPopconfirm
                    title="确定要删除这个模型吗？"
                    confirm-button-text="确定"
                    cancel-button-text="取消"
                    @confirm="handleDelete(scope.row.model_name)"
                  >
                    <template #reference>
                      <ElButton size="small" type="danger">删除</ElButton>
                    </template>
                  </ElPopconfirm>
                </ElSpace>
              </template>
            </ElTableColumn>
          </ElTable>
        </ElCard>
      </ElCol>
    </ElRow>

    <!-- 模型详情对话框 -->
    <ElDialog v-model="dialogVisible" title="模型详情" width="70%">
      <div v-if="currentModel" class="model-details">
        <ElRow :gutter="20">
          <ElCol :span="12">
            <ElCard shadow="never">
              <template #header>
                <h4>基本信息</h4>
              </template>
              <div class="detail-item">
                <span class="label">模型名称:</span>
                <span class="value">{{ currentModel.model_name }}</span>
              </div>
              <div class="detail-item">
                <span class="label">模型类型:</span>
                <span class="value">{{ getModelTypeDisplayName(currentModel.model_type) }}</span>
              </div>
              <div class="detail-item">
                <span class="label">目标列:</span>
                <span class="value">{{ currentModel.target_name }}</span>
              </div>
              <div class="detail-item">
                <span class="label">特征数量:</span>
                <span class="value">{{ currentModel.feature_names?.length || 0 }}</span>
              </div>
              <div class="detail-item">
                <span class="label">是否调参:</span>
                <span class="value">{{ currentModel.tuned ? '是' : '否' }}</span>
              </div>
              <div class="detail-item">
                <span class="label">创建时间:</span>
                <span class="value">{{ new Date(currentModel.created_at).toLocaleString() }}</span>
              </div>
            </ElCard>
          </ElCol>
          <ElCol :span="12">
            <ElCard shadow="never">
              <template #header>
                <h4>特征列表</h4>
              </template>
              <div class="feature-list">
                <ElTag
                  v-for="feature in currentModel.feature_names"
                  :key="feature"
                  type="info"
                  size="small"
                  style="margin: 2px;"
                >
                  {{ feature }}
                </ElTag>
              </div>
            </ElCard>
          </ElCol>
        </ElRow>
        
        <ElRow :gutter="20" style="margin-top: 20px;">
          <ElCol :span="12">
            <ElCard shadow="never">
              <template #header>
                <h4>训练集指标</h4>
              </template>
              <div v-for="(value, key) in currentModel.train_metrics" :key="key" class="metric-item">
                <span class="metric-name">{{ key }}:</span>
                <span class="metric-value">{{ typeof value === 'number' ? value.toFixed(4) : value }}</span>
              </div>
            </ElCard>
          </ElCol>
          <ElCol :span="12">
            <ElCard shadow="never">
              <template #header>
                <h4>测试集指标</h4>
              </template>
              <div v-for="(value, key) in currentModel.test_metrics" :key="key" class="metric-item">
                <span class="metric-name">{{ key }}:</span>
                <span class="metric-value">{{ typeof value === 'number' ? value.toFixed(4) : value }}</span>
              </div>
            </ElCard>
          </ElCol>
        </ElRow>
      </div>
    </ElDialog>

    <!-- 导入模型对话框 -->
    <ElDialog v-model="importDialogVisible" title="导入模型" width="40%">
      <div class="import-dialog">
        <ElAlert
          title="导入说明"
          type="info"
          description="请选择之前导出的模型JSON文件。导入的模型将添加到本地存储中。"
          show-icon
          :closable="false"
          style="margin-bottom: 20px;"
        />
        <input
          type="file"
          accept=".json"
          @change="handleFileChange(($event.target as HTMLInputElement).files?.[0] || null)"
          ref="fileInput"
          style="display: none;"
        />
        <ElButton @click="(fileInput as HTMLInputElement).click()" style="width: 100%;">
          选择文件
        </ElButton>
        <div v-if="importFile" style="margin-top: 10px;">
          <p>已选择文件: {{ importFile.name }}</p>
        </div>
      </div>
      <template #footer>
        <ElButton @click="importDialogVisible = false">取消</ElButton>
        <ElButton type="primary" @click="handleImportConfirm" :disabled="!importFile">
          确定导入
        </ElButton>
      </template>
    </ElDialog>
  </div>
</template>

<style scoped>
.model-manager {
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

.storage-usage {
  font-size: 14px;
  color: #606266;
}

.model-details {
  max-height: 60vh;
  overflow-y: auto;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #ebeef5;
}

.detail-item:last-child {
  border-bottom: none;
}

.label {
  color: #606266;
  font-weight: 500;
}

.value {
  color: #303133;
}

.feature-list {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.metric-item {
  display: flex;
  justify-content: space-between;
  padding: 5px 0;
}

.metric-name {
  color: #606266;
}

.metric-value {
  color: #303133;
  font-weight: 500;
}

.import-dialog {
  text-align: center;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .storage-usage {
    font-size: 12px;
  }
}
</style>
<!-- </tool_call> -->