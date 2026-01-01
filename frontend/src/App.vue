<script setup lang="ts">
import { RouterView } from 'vue-router'
import { ElContainer, ElHeader, ElMain, ElMenu, ElMenuItem } from 'element-plus'
import { useRoute, useRouter } from 'vue-router'
import { computed, onMounted } from 'vue'
import { useSettingsStore } from '@/stores/settings'

const route = useRoute()
const router = useRouter()
const settingsStore = useSettingsStore()

const activeMenu = computed(() => route.name as string)
const themeColor = computed(() => settingsStore.themeColor)

const handleMenuSelect = (index: string) => {
  router.push({ name: index })
}

onMounted(() => {
  // 确保主题颜色在应用启动时应用
  settingsStore.applyThemeColor()
})
</script>

<template>
  <ElContainer class="app-container">
    <ElHeader class="app-header">
      <div class="header-content">
        <div class="app-title">
          <img src="/Icons.png" alt="系统图标" class="app-icon" />
          <span>基于机器学习的数据分析与统计系统</span>
        </div>
        <ElMenu
          :default-active="activeMenu"
          mode="horizontal"
          @select="handleMenuSelect"
          class="app-menu"
        >
          <ElMenuItem index="workflow">操作流程</ElMenuItem>
          <ElMenuItem index="instructions">操作说明</ElMenuItem>
          <ElMenuItem index="settings">系统设置</ElMenuItem>
        </ElMenu>
      </div>
    </ElHeader>
    <ElMain class="app-main">
      <RouterView />
    </ElMain>
  </ElContainer>
</template>

<style scoped>
.app-container {
  width: 100%;
  height: 100vh;
  flex-direction: column;
}

.app-header {
  background-color: v-bind(themeColor);
  color: white;
  padding: 0;
  height: 80px;
  width: 100%;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
  padding: 0 20px;
  width: 100%;
}

.app-title {
  margin: 0;
  font-size: 20px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

.app-icon {
  height: 32px;
  width: auto;
}

.app-menu {
  background-color: transparent;
  border-bottom: none;
  flex-grow: 1;
}

.app-menu .el-menu-item {
  color: white;
  border-bottom: 2px solid transparent;
  font-size: 16px;
  padding: 0 15px;
}

.app-menu .el-menu-item:hover {
  background-color: rgba(255, 255, 255, 0.15);
}

.app-menu .el-menu-item.is-active {
  background-color: rgba(255, 255, 255, 0.15);
  border-bottom: 3px solid #ffffff;
  color: #ffffff;
  font-weight: 500;
}

.app-main {
  padding: 20px;
  background-color: #f5f7fa;
}

/* 响应式样式 */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    padding: 10px;
    height: auto;
  }
  
  .app-title {
    font-size: 16px;
    margin-bottom: 10px;
  }
  
  .app-header {
    height: auto;
  }
  
  .app-menu .el-menu-item {
    padding: 0 10px;
    font-size: 14px;
  }
}

@media (max-width: 480px) {
  .header-content {
    padding: 5px;
  }
  
  .app-title {
    font-size: 14px;
    flex-direction: column;
    text-align: center;
  }
  
  .app-icon {
    height: 24px;
  }
  
  .app-menu {
    width: 100%;
  }
  
  .app-menu .el-menu-item {
    padding: 5px;
    font-size: 12px;
  }
}
</style>
