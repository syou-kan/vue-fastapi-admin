<!-- web/src/components/common/CustomerService.vue -->
<template>
  <n-popover trigger="click" placement="bottom">
    <template #trigger>
      <n-button text>
        <icon-custom-service mr-5 /> 联系客服
      </n-button>
    </template>
    <div class="p-4 text-center">
      <n-h3 class="mb-3">扫码添加企业微信客服</n-h3>
      <img
        src="@/assets/images/vx.png"
        alt="企业微信客服二维码"
        class="w-200px h-200px mb-3"
      >
      <n-p class="text-gray-500">工作日 9:00-18:00</n-p>
    </div>
  </n-popover>
</template>

<script setup>
import { Icon } from '@vicons/utils'
import { CustomService } from '@vicons/carbon'
</script>