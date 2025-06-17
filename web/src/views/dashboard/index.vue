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
            <div ref="userChart" class="h-60"></div>
          </n-card>
        </n-gi>
        <n-gi>
          <n-card title="订单总数" hoverable>
            <div ref="orderChart" class="h-60"></div>
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
import { ref, onMounted, watch } from 'vue'
import { dashboardApi } from '@/api/dashboard'
import { NGrid, NGi, NCard, NSpin } from 'naive-ui'
import * as echarts from 'echarts'

const loading = ref(true)
const error = ref(null)
const dashboardData = ref(null)
const userChart = ref(null)
const orderChart = ref(null)

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

watch(dashboardData, (newData) => {
  if (newData && newData.is_admin) {
    initCharts()
  }
})

function initCharts() {
  if (userChart.value) {
    const userChartInstance = echarts.init(userChart.value)
    userChartInstance.setOption({
      tooltip: {},
      xAxis: {
        data: ['用户'],
      },
      yAxis: {},
      series: [
        {
          name: '用户总数',
          type: 'bar',
          data: [dashboardData.value.data.user_count],
        },
      ],
    })
  }

  if (orderChart.value) {
    const orderChartInstance = echarts.init(orderChart.value)
    orderChartInstance.setOption({
      tooltip: {},
      xAxis: {
        data: ['订单'],
      },
      yAxis: {},
      series: [
        {
          name: '订单总数',
          type: 'bar',
          data: [dashboardData.value.data.order_count],
          itemStyle: {
            color: '#67C23A',
          },
        },
      ],
    })
  }
}
</script>