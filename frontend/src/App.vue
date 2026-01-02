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
          <ElMenuItem index="models">模型管理</ElMenuItem>
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
  color: rgba(255, 255, 255, 0.9);
  border-bottom: 2px solid transparent;
  font-size: 16px;
  padding: 0 15px;
  position: relative;
  transition: all 0.3s ease;
}

.app-menu .el-menu-item:hover {
  background-color: rgba(255, 255, 255, 0.15);
  color: #ffffff;
  transform: translateY(-1px);
}

.app-menu .el-menu-item:not(.is-active):hover::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 60%;
  height: 2px;
  background-color: rgba(255, 255, 255, 0.5);
  border-radius: 2px;
}

.app-menu .el-menu-item.is-active {
  background-color: #ffffff;
  color: v-bind(themeColor);
  font-weight: 700;
  border-radius: 4px;
  border-bottom: none;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.app-menu .el-menu-item.is-active::after {
  display: none;
}

.app-main {
  padding: 20px;
  background-color: #f5f7fa;
}

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
