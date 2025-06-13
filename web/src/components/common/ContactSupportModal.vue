<!--
  功能: 联系客服模态框
  描述: 使用 Naive UI 的 n-modal 组件，展示二维码和联系信息。
-->
<template>
  <!-- 使用 n-modal 组件作为模态框容器 -->
  <!-- 绑定 show 属性到 showModal ref，用于控制显示/隐藏 -->
  <!-- 设置 preset="card" 以获得标准卡片样式 -->
  <!-- 标题使用 i18n 的 t('common.contactSupport') -->
  <!-- 设置固定宽度，例如 400px -->
  <n-modal v-model:show="showModal" preset="card" :title="t('common.contactSupport')" style="width: 400px;">
    <!-- 使用 n-space 垂直布局内容 -->
    <n-space vertical align="center">
      <!-- 提示信息 -->
      <p>{{ t('common.contactSupportHint') }}</p>
      <!--
        显示二维码图片
        使用 n-image 组件
        图片路径为 /deploy/sample-picture/logo.svg
        设置一个合适的宽度，例如 150px
      -->
      <n-image width="150" src="/src/assets/images/image.png" />
      <!-- 其他联系信息，例如电话和工作时间 -->
      <p><strong>{{ t('common.supportPhone') }}:</strong> 400-123-4567</p>
      <p><strong>{{ t('common.workHours') }}:</strong> {{ t('common.workHoursDetail') }}</p>
    </n-space>
    <!-- 定义模态框的页脚 -->
    <template #footer>
      <!-- 关闭按钮，点击时将 showModal 设置为 false -->
      <n-button @click="showModal = false">{{ t('common.close') }}</n-button>
    </template>
  </n-modal>
</template>

<script setup>
// 导入 Vue 的 ref 和 defineExpose
import { ref, defineExpose } from 'vue';
// 导入 vue-i18n 的 useI18n
import { useI18n } from 'vue-i18n';
// 导入 Naive UI 组件
import { NModal, NSpace, NImage, NButton } from 'naive-ui';

// 获取 i18n 的 t 函数
const { t } = useI18n();

// 定义一个 ref (showModal) 来控制模态框的可见性，默认为 false
const showModal = ref(false);

// 定义一个 open 函数，用于从外部打开模态框
function open() {
  showModal.value = true;
}

// 使用 defineExpose 将 open 函数暴露给父组件
defineExpose({ open });
</script>