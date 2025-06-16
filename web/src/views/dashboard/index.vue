<template>
  <AppPage>
    <div v-if="loading" class="flex-center h-full">
      <n-spin size="large" />
    </div>
    <div v-else-if="error" class="text-red-500">{{ error }}</div>

    <!-- 管理员视图 -->
    <div v-if="dashboardData && dashboardData.is_admin">
      <n-grid :cols="2" :x-gap="16" :y-gap="16">
        <n-gi>
          <n-card title="用户总数" hoverable>
            <p class="text-3xl font-bold">{{ dashboardData.data.user_count }}</p>
          </n-card>
        </n-gi>
        <n-gi>
          <n-card title="订单总数" hoverable>
            <p class="text-3xl font-bold">{{ dashboardData.data.order_count }}</p>
          </n-card>
        </n-gi>
      </n-grid>
    </div>

    <!-- 普通用户视图 -->
    <div v-else-if="dashboardData && !dashboardData.is_admin">
      <n-card hoverable>
        <h1 class="text-2xl">{{ dashboardData.data.welcome_message }}</h1>
        <p class="mt-4">这里是您的个人仪表盘，祝您有美好的一天！</p>
      </n-card>
    </div>
  </AppPage>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { dashboardApi } from '@/api/dashboard'
import { NGrid, NGi, NCard, NSpin } from 'naive-ui'

const loading = ref(true)
const error = ref(null)
const dashboardData = ref(null)

onMounted(async () => {
  try {
    loading.value = true
    const res = await dashboardApi.getDashboardData()
    dashboardData.value = res
  } catch (e) {
    error.value = '加载仪表盘数据失败，请稍后重试。'
    console.error(e)
  } finally {
    loading.value = false
  }
})
</script>