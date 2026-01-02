<script setup lang="ts">
import { ElCard, ElRow, ElCol, ElAlert, ElTimeline, ElTimelineItem } from 'element-plus'
import { Upload, Setting, TrendCharts, Download } from '@element-plus/icons-vue'
</script>

<template>
  <div class="instructions-container">
    <ElRow :gutter="20">
      <ElCol :span="24">
        <ElCard class="instructions-card">
          <template #header>
            <h2>操作说明</h2>
          </template>
          
          <ElAlert
            title="欢迎使用基于机器学习的数据分析与统计系统"
            type="info"
            description="本系统提供了完整的数据分析流程，包括数据上传与处理、模型训练配置、模型评估与结果、以及预测与导出功能。"
            show-icon
            :closable="false"
            style="margin-bottom: 30px;"
          />
          
          <ElRow :gutter="20">
            <ElCol :span="24">
              <ElCard class="section-card" shadow="never">
                <template #header>
                  <h3>这个系统能帮做什么？</h3>
                </template>
                
                <p>本系统是一个完整的机器学习数据分析平台，可以帮助您：</p>
                <ul>
                  <li>上传和分析CSV格式的数据文件</li>
                  <li>自动进行数据预处理和特征工程</li>
                  <li>配置和训练多种机器学习回归模型</li>
                  <li>评估和比较不同模型的性能指标</li>
                  <li>使用训练好的模型进行单条或批量预测</li>
                  <li>导出预测结果为CSV、Excel或JSON格式</li>
                </ul>
                
                <p>系统适用于各种数据分析场景，如房价预测、销售预测、实验数据分析等。</p>
              </ElCard>
            </ElCol>
            
            <ElCol :span="24" style="margin-top: 20px;">
              <ElCard class="section-card" shadow="never">
                <template #header>
                  <h3>完整使用流程</h3>
                </template>
                
               <ElTimeline>
  <ElTimelineItem :type="'primary'" :icon="Upload">
    <h4>Step 1: 数据上传与处理</h4>
    <p>在主页面选择Step1 数据标签页，上传CSV格式的数据文件。系统会自动分析数据结构，显示数据预览和基本信息。您可以选择目标列和缺失值处理方式，然后点击处理数据按钮。完成数据处理后，系统将自动允许您进入下一步。</p>
  </ElTimelineItem>
  
  <ElTimelineItem :type="'success'" :icon="Setting">
    <h4>Step 2: 模型训练配置</h4>
    <p>切换到Step2 模型标签页，选择合适的模型类型（如线性回归、随机森林等），设置目标列、测试集比例和是否开启超参数调优，然后点击开始训练模型按钮。系统会显示训练进度和评估指标。</p>
  </ElTimelineItem>
  
  <ElTimelineItem :type="'info'" :icon="TrendCharts">
    <h4>Step 3: 模型评估与结果</h4>
    <p>模型训练完成后，系统会显示详细的评估指标，包括训练集和测试集的性能指标。您可以查看模型准确率、特征重要性等信息，确认模型是否满足需求。</p>
  </ElTimelineItem>
  
  <ElTimelineItem :type="'warning'" :icon="Download">
    <h4>Step 4: 预测与导出</h4>
    <p>在Step3 预测标签页中，系统将自动使用您在Step2中训练的模型。您可以进行单条预测或批量预测。输入特征值，点击开始预测按钮。预测完成后，可以导出结果为CSV、Excel或JSON格式。</p>
  </ElTimelineItem>
</ElTimeline>
              </ElCard>
            </ElCol>
            
            <ElCol :span="24" style="margin-top: 20px;">
              <ElCard class="section-card" shadow="never">
                <template #header>
                  <h3>常见问题 / 错误提示</h3>
                </template>
                
                <ElRow :gutter="20">
                  <ElCol :span="12">
                    <h4>数据上传问题</h4>
                    <ul>
                      <li><strong>文件格式错误：</strong>只能上传CSV格式的文件</li>
                      <li><strong>文件过大：</strong>建议文件大小不超过10MB</li>
                      <li><strong>数据格式问题：</strong>确保数据有表头，数值列不包含非数字字符</li>
                      <li><strong>缺失值处理：</strong>系统提供多种缺失值处理方式，可根据需求选择</li>
                    </ul>
                  </ElCol>
                  <ElCol :span="12">
                    <h4>模型训练问题</h4>
                    <ul>
                      <li><strong>目标列选择：</strong>目标列必须是数值型数据，且需要在数据处理步骤中指定</li>
                      <li><strong>训练时间过长：</strong>大数据集训练可能需要较长时间，请耐心等待</li>
                      <li><strong>模型准确率低：</strong>尝试调整测试集比例或开启超参数调优</li>
                      <li><strong>内存不足：</strong>大数据集可能导致内存不足，可考虑减少数据量</li>
                      <li><strong>无法进入模型训练页面：</strong>确保已完成数据处理步骤，系统会自动允许进入下一步</li>
                    </ul>
                  </ElCol>
                </ElRow>
                
                <ElRow :gutter="20" style="margin-top: 20px;">
                  <ElCol :span="12">
                    <h4>预测问题</h4>
                    <ul>
                      <li><strong>预测失败：</strong>确保已训练模型且输入特征与训练数据一致</li>
                      <li><strong>结果异常：</strong>检查输入特征值是否在合理范围内</li>
                      <li><strong>批量预测错误：</strong>确保每行数据的特征完整且格式正确</li>
                      <li><strong>导出失败：</strong>检查浏览器是否允许文件下载</li>
                    </ul>
                  </ElCol>
                  <ElCol :span="12">
                    <h4>系统问题</h4>
                    <ul>
                      <li><strong>页面加载慢：</strong>检查网络连接，尝试刷新页面</li>
                      <li><strong>操作无响应：</strong>检查浏览器控制台是否有错误信息</li>
                      <li><strong>数据丢失：</strong>长时间未操作可能导致会话超时，需要重新上传数据</li>
                      <li><strong>兼容性问题：</strong>推荐使用Chrome、Firefox等现代浏览器</li>
                    </ul>
                  </ElCol>
                </ElRow>
              </ElCard>
            </ElCol>
            
            <ElCol :span="24" style="margin-top: 20px;">
              <ElCard class="section-card" shadow="never">
                <template #header>
                  <h3>适合谁？不适合谁？</h3>
                </template>
                
                <ElRow :gutter="20">
                  <ElCol :span="12">
                    <h4>适合人群</h4>
                    <ul>
                      <li><strong>数据分析师：</strong>需要快速构建和评估预测模型</li>
                      <li><strong>业务分析师：</strong>希望使用数据驱动决策</li>
                      <li><strong>研究人员：</strong>需要验证研究假设和模型</li>
                      <li><strong>学生：</strong>学习机器学习概念和实践</li>
                      <li><strong>产品经理：</strong>需要评估产品指标和趋势</li>
                    </ul>
                  </ElCol>
                  <ElCol :span="12">
                    <h4>不适合场景</h4>
                    <ul>
                      <li><strong>非结构化数据：</strong>文本、图像、音频等非表格数据</li>
                      <li><strong>实时预测需求：</strong>需要毫秒级响应的实时场景</li>
                      <li><strong>深度学习需求：</strong>复杂的神经网络模型训练</li>
                      <li><strong>大数据处理：</strong>TB级以上的超大数据集</li>
                      <li><strong>分类问题：</strong>本系统主要针对回归问题设计</li>
                    </ul>
                  </ElCol>
                </ElRow>
              </ElCard>
            </ElCol>
          </ElRow>
        </ElCard>
      </ElCol>
    </ElRow>
  </div>
</template>

<style scoped>
.instructions-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 15px;
}

.instructions-card {
  margin-bottom: 20px;
}

.section-card {
  margin-bottom: 20px;
}

.section-card h3 {
  margin: 0;
  color: #303133;
}

.section-card h4 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #409eff;
  font-size: 16px;
}

.section-card p {
  line-height: 1.6;
  color: #606266;
  margin-bottom: 15px;
}

.section-card ul {
  padding-left: 20px;
  margin-bottom: 15px;
}

.section-card li {
  line-height: 1.6;
  color: #606266;
  margin-bottom: 8px;
}

.section-card strong {
  color: #303133;
}

@media (max-width: 768px) {
  .instructions-container {
    padding: 0 10px;
  }
  
  .section-card h4 {
    font-size: 15px;
  }
}

@media (max-width: 480px) {
  .section-card h3 {
    font-size: 18px;
  }
  
  .section-card h4 {
    font-size: 14px;
  }
}

.el-timeline-item h4 {
  margin: 0 0 10px 0;
  font-size: 16px;
  color: #303133;
  font-weight: bold;
}

.el-timeline-item p {
  margin: 0;
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
}
</style>