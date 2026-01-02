<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElDialog, ElForm, ElFormItem, ElInput, ElButton, ElAlert, ElDescriptions, ElDescriptionsItem, ElTag, ElMessage, ElCard } from 'element-plus'
import { usePredictStore } from '@/stores/predict'
import { useModelStore } from '@/stores/model'
import { useDataStore } from '@/stores/data'
import ModelStorage from '@/utils/modelStorage'
import type { ModelInfo } from '@/utils/modelStorage'

interface Props {
  visible: boolean
  model: ModelInfo | null
}

interface Emits {
  (e: 'update:visible', value: boolean): void
}

const props = withDefaults(defineProps<Props>(), {
  visible: false,
  model: null
})

const emit = defineEmits<Emits>()

const predictStore = usePredictStore()
const modelStore = useModelStore()
const dataStore = useDataStore()

const predictForm = ref({
  data: {} as Record<string, any>
})

const loading = computed(() => predictStore.loading)
const predictionResult = computed(() => predictStore.predictionResult)

const featureFields = computed(() => {
  if (!props.model || !props.model.feature_names) {
    return []
  }
  
  return props.model.feature_names.map(name => ({
    value: name,
    label: name
  }))
})

watch([() => props.visible, () => props.model], ([visible, model]) => {
  if (visible && model && model.feature_names) {
    predictForm.value.data = {}
    model.feature_names.forEach(feature => {
      predictForm.value.data[feature] = ''
    })
    if (model.target_name) {
      predictForm.value.data[model.target_name] = null
    }
  }
}, { immediate: true })

const handleClose = () => {
  emit('update:visible', false)
  predictStore.clearResults()
}

const handlePredict = async () => {
  if (!props.model) {
    ElMessage.error('未选择模型')
    return
  }

  try {
    if (props.model.feature_names) {
      for (const feature of props.model.feature_names) {
        const value = predictForm.value.data[feature]
        if (value === '' || value === null || value === undefined) {
          ElMessage.error(`请输入特征 ${feature} 的值`)
          return
        }
        
        if (isNaN(Number(value))) {
          ElMessage.error(`特征 ${feature} 的值必须是数字`)
          return
        }
      }
    }

    const result = await predictStore.predict({
      data: predictForm.value.data,
      model_name: props.model.model_name
    })
    
    ElMessage.success('预测完成')
  } catch (error) {
    console.error('预测失败:', error)
    ElMessage.error('预测失败，请检查输入数据')
  }
}

const resetPredictForm = () => {
  if (props.model && props.model.feature_names) {
    props.model.feature_names.forEach(feature => {
      predictForm.value.data[feature] = ''
    })
    if (props.model.target_name) {
      predictForm.value.data[props.model.target_name] = null
    }
  }
  predictStore.clearResults()
}
</script>

<template>
  <ElDialog
    :model-value="visible"
    @update:model-value="(val) => emit('update:visible', val)"
    :title="`使用模型: ${model?.model_name || ''}`"
    width="80%"
    :before-close="handleClose"
  >
    <div v-if="model" class="model-use-dialog">
      <ElAlert
        title="模型信息"
        type="info"
        :description="`模型类型: ${model.model_type}, 目标列: ${model.target_name}, 特征数量: ${model.feature_names?.length || 0}`"
        show-icon
        :closable="false"
        style="margin-bottom: 20px;"
      />

      <ElRow :gutter="20">
        <ElCol :span="16">
          <ElForm label-width="120px">
            <ElFormItem 
              v-for="field in featureFields" 
              :key="field.value" 
              :label="field.label"
            >
              <ElInput
                v-model="predictForm.data[field.value]"
                :placeholder="`请输入${field.label}`"
                type="number"
                step="any"
              />
            </ElFormItem>
          </ElForm>
        </ElCol>
        <ElCol :span="8">
          <div class="predict-actions">
            <ElButton 
              type="primary" 
              @click="handlePredict" 
              :loading="loading"
              size="large"
              style="width: 100%; margin-bottom: 15px;"
            >
              开始预测
            </ElButton>
            <ElButton @click="resetPredictForm" size="large" style="width: 100%;">
              重置表单
            </ElButton>
          </div>
          
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
    </div>
    
    <template #footer>
      <ElButton @click="handleClose">关闭</ElButton>
    </template>
  </ElDialog>
</template>

<style scoped>
.model-use-dialog {
  max-height: 70vh;
  overflow-y: auto;
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

@media (max-width: 768px) {
  .predict-actions {
    padding: 15px;
  }
}
</style>