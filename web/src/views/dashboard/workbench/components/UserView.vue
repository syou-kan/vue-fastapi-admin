<template>
  <n-card title="普通用户工作台" :bordered="false" size="large" class="rounded-16px shadow-sm">
    <n-grid :x-gap="12" :y-gap="8" :cols="2">
      <n-gi>
        <n-card :bordered="false" class="bg-purple-100">
          <div class="text-center">
            <div class="text-2xl font-bold">{{ data.task_count }}</div>
            <div class="mt-2">待办任务</div>
          </div>
        </n-card>
      </n-gi>
      <n-gi>
        <n-card :bordered="false" class="bg-pink-100">
          <div class="text-center">
            <div class="text-2xl font-bold">{{ data.message_count }}</div>
            <div class="mt-2">未读消息</div>
          </div>
        </n-card>
      </n-gi>
    </n-grid>
  </n-card>
</template>

<script setup>
defineProps({
  data: {
    type: Object,
    required: true,
  },
});
</script>

<style scoped></style>