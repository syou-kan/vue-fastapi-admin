<template>
  <AppPage :show-footer="false">
    <div class="page-container">
      <div v-if="loading" class="flex-center h-full">
        <n-spin size="large"/>
      </div>
      <div v-else-if="error" class="error-message">{{ error }}</div>

      <!-- 管理员视图 -->
      <div v-if="dashboardData && dashboardData.is_admin" class="admin-dashboard">
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

      <!-- 普通用户视图 - 专业大宗采购平台设计 -->
      <div v-else-if="dashboardData && !dashboardData.is_admin" class="dashboard-container">
        <div class="dashboard-content">
          <!-- 第一部分：平台标题和欢迎信息 -->
          <div class="section-top">
            <div class="platform-header">
              <div class="platform-logo">
                <n-icon size="42" color="#1a56db">
                  <DiamondOutline />
                </n-icon>
                <h1>专业大宗采购平台</h1>
              </div>
              <div class="platform-tagline">连接优质供应商，助力企业高效采购</div>
            </div>

            <div class="welcome-section">
              <h1 class="welcome-title">
                {{ dashboardData.data.welcome_message }}
              </h1>
              <div class="welcome-divider"></div>
            </div>
          </div>

          <!-- 第二部分：专业服务 -->
          <div v-if="dashboardData.data.company_introduction" class="section-services">
            <h2 class="section-title">我们的专业服务</h2>

            <div class="professional-grid">
              <div class="professional-card">
                <div class="card-icon blue">
                  <n-icon size="42" color="white">
                    <PeopleOutline />
                  </n-icon>
                </div>
                <h3 class="card-title">专业团队</h3>
                <p class="card-content">{{ dashboardData.data.company_introduction[0] }}</p>
              </div>

              <div class="professional-card">
                <div class="card-icon green">
                  <n-icon size="42" color="white">
                    <ChatboxEllipsesOutline />
                  </n-icon>
                </div>
                <h3 class="card-title">高效对接</h3>
                <p class="card-content">{{ dashboardData.data.company_introduction[1] }}</p>
              </div>

              <div class="professional-card">
                <div class="card-icon purple">
                  <n-icon size="42" color="white">
                    <WalletOutline />
                  </n-icon>
                </div>
                <h3 class="card-title">价格优势</h3>
                <p class="card-content">{{ dashboardData.data.company_introduction[2] }}</p>
              </div>

              <div class="professional-card">
                <div class="card-icon orange">
                  <n-icon size="42" color="white">
                    <TimeOutline />
                  </n-icon>
                </div>
                <h3 class="card-title">时效保障</h3>
                <p class="card-content">{{ dashboardData.data.company_introduction[3] }}</p>
              </div>
            </div>
          </div>

          <!-- 第三部分：价值与流程 - 占据两份空间 -->
          <div class="section-value-process">
            <!-- 核心价值展示 -->
            <div class="value-section">
              <h2 class="section-title">为何选择我们</h2>
              <div class="value-container">
                <div class="value-item">
                  <div class="value-number">5%-25%</div>
                  <div class="value-label">价格优势</div>
                  <div class="value-desc">低于市场价，节约采购成本</div>
                </div>
                <div class="value-item">
                  <div class="value-number">1000+</div>
                  <div class="value-label">起购金额</div>
                  <div class="value-desc">专注大宗采购，提供专业服务</div>
                </div>
                <div class="value-item">
                  <div class="value-number">3h</div>
                  <div class="value-label">快速响应</div>
                  <div class="value-desc">客服3小时内提供精准报价</div>
                </div>
                <div class="value-item">
                  <div class="value-number">100%</div>
                  <div class="value-label">正品保障</div>
                  <div class="value-desc">享受平台同等质保和售后</div>
                </div>
              </div>
            </div>

            <!-- 服务流程展示 -->
            <div class="process-section">
              <h2 class="section-title">采购服务流程</h2>
              <div class="process-steps">
                <div class="process-step">
                  <div class="step-number">1</div>
                  <h3 class="step-title">提交需求</h3>
                  <p class="step-desc">告知商品型号和数量</p>
                </div>
                <div class="process-arrow">→</div>
                <div class="process-step">
                  <div class="step-number">2</div>
                  <h3 class="step-title">专业报价</h3>
                  <p class="step-desc">3小时内提供最优报价</p>
                </div>
                <div class="process-arrow">→</div>
                <div class="process-step">
                  <div class="step-number">3</div>
                  <h3 class="step-title">确认订单</h3>
                  <p class="step-desc">签订合同支付定金</p>
                </div>
                <div class="process-arrow">→</div>
                <div class="process-step">
                  <div class="step-number">4</div>
                  <h3 class="step-title">发货售后</h3>
                  <p class="step-desc">快速发货，全程售后支持</p>
                </div>
              </div>
            </div>
          </div>

          <!-- 第四部分：底部行动号召 -->
          <div class="section-cta">
            <div class="cta-section">
              <div class="cta-content">
                <h3 class="cta-title">立即获取专属报价</h3>
                <p class="cta-subtitle">专业采购顾问将在3小时内为您提供最优解决方案</p>
                <button class="cta-button" @click="handleContactSupport">
                  联系客服
                </button>
              </div>
              <div class="cta-info">
                <p><n-icon size="20" color="#4cc9f0"><TimeOutline /></n-icon> 服务时间: 8:00-20:00</p>
                <p><n-icon size="20" color="#4cc9f0"><CallOutline /></n-icon> 客服电话: 400-888-8888</p>
              </div>
            </div>
          </div>
        </div>
      </div>
      <ContactSupportModal ref="contactSupportModal" />
    </div>
  </AppPage>
</template>

<script>
import {ref, onMounted, watch, nextTick} from 'vue'
import ContactSupportModal from '@/components/common/ContactSupportModal.vue'
import {dashboardApi} from '@/api/dashboard'
import {
  NGrid, NGi, NCard, NSpin, NIcon
} from 'naive-ui'
import * as echarts from 'echarts'

// 导入图标组件
import PeopleOutline from '@vicons/ionicons5/PeopleOutline'
import ShieldCheckmarkOutline from '@vicons/ionicons5/ShieldCheckmarkOutline'
import HeadsetOutline from '@vicons/ionicons5/HeadsetOutline'
import DiamondOutline from '@vicons/ionicons5/DiamondOutline'
import ChatboxEllipsesOutline from '@vicons/ionicons5/ChatboxEllipsesOutline'
import WalletOutline from '@vicons/ionicons5/WalletOutline'
import TimeOutline from '@vicons/ionicons5/TimeOutline'
import CallOutline from '@vicons/ionicons5/CallOutline'

export default {
  components: {
    ContactSupportModal,
    PeopleIcon: PeopleOutline,
    ShieldIcon: ShieldCheckmarkOutline,
    HeadsetIcon: HeadsetOutline,
    DiamondOutline,
    ChatboxEllipsesOutline,
    WalletOutline,
    TimeOutline,
    CallOutline
  },
  setup() {
    const loading = ref(true)
    const error = ref(null)
    const dashboardData = ref(null)
    const userChart = ref(null)
    const orderChart = ref(null)
    const contactSupportModal = ref(null)

    onMounted(async () => {
      try {
        loading.value = true
        const res = await dashboardApi.getDashboardData()
        dashboardData.value = res

        // 确保图表在数据加载后初始化
        await nextTick()
        if (dashboardData.value && dashboardData.value.is_admin) {
          initCharts()
        }
      } catch (e) {
        error.value = '加载仪表盘数据失败，请稍后重试。'
        console.error(e)
      } finally {
        loading.value = false
      }
    })

    watch(dashboardData, (newData) => {
      if (newData && newData.is_admin) {
        // 确保DOM更新后初始化图表
        nextTick(() => {
          initCharts()
        })
      }
    })

    function handleContactSupport() {
      contactSupportModal.value?.open()
    }

    function initCharts() {
      if (userChart.value && dashboardData.value?.data?.user_count !== undefined) {
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

        // 添加窗口大小变化时的重绘
        window.addEventListener('resize', () => {
          userChartInstance.resize()
        })
      }

      if (orderChart.value && dashboardData.value?.data?.order_count !== undefined) {
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

        // 添加窗口大小变化时的重绘
        window.addEventListener('resize', () => {
          orderChartInstance.resize()
        })
      }
    }

    return {
      loading,
      error,
      dashboardData,
      userChart,
      orderChart,
      contactSupportModal,
      handleContactSupport
    }
  }
}
</script>

<style scoped>
/* 关键修复：确保页面容器有正确的高度 */
.page-container {
  height: 100%;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.admin-dashboard {
  flex: 1;
  min-height: 0;
  padding: 16px;
}

.dashboard-container {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.dashboard-content {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #f0f9ff 0%, #e6f7ff 100%);
  border-radius: 14px;
  box-shadow: 0 5px 18px rgba(0, 0, 0, 0.07);
  padding: 1rem;
  overflow: hidden;

  /* 新增：设置基准字体大小 */
  font-size: 4rem; /* 相当于16px (4rem * 4px = 16px) */
}

/* 错误消息 */
.error-message {
  color: #ff4d4f;
  text-align: center;
  padding: 1.5rem 0;
  font-size: 1.6rem;
  font-weight: bold;
}

/* ================== 四部分布局 ================== */
.section-top {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 1rem 0;
}

.section-services {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 1rem 0;
}

.section-value-process {
  flex: 2; /* 占据两份空间 */
  min-height: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 1rem 0;
}

.section-cta {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  justify-content: flex-end; /* 内容贴近底部 */
  padding: 1rem 0;
}

/* 平台标题 */
.platform-header {
  text-align: center;
  margin-bottom: 2rem;
  padding: 0.7rem;
  background: rgba(26, 86, 219, 0.05);
  border-radius: 10px;
}

.platform-logo {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-bottom: 6px;
}

.platform-logo h1 {
  font-size: 4.5rem; /* 18px -> 4.5rem (4.5*4=18px) */
  font-weight: 700;
  color: #1a56db;
}

.platform-tagline {
  font-size: 3rem; /* 12px -> 3rem (3*4=12px) */
  font-weight: 600;
  color: #4b5563;
}

/* 欢迎区域增强 */
.welcome-section {
  background: linear-gradient(135deg, #1a3c8f 0%, #0d2b64 100%);
  border-radius: 14px;
  padding: 2rem 1rem;
  color: white;
  text-align: center;
  box-shadow: 0 5px 15px rgba(26, 86, 219, 0.12);
  max-width: 800px;
  margin: 0 auto;
}

.welcome-title {
  font-size: 4.5rem; /* 18px -> 4.5rem */
  font-weight: 700;
  margin-bottom: 0.5rem;
  line-height: 1.3;
}

.welcome-divider {
  width: 80px;
  height: 3px;
  background: #4cc9f0;
  margin: 1rem auto 0;
  border-radius: 2px;
}

/* 内容区域 */
.section-title {
  font-size: 4.5rem; /* 18px -> 4.5rem */
  font-weight: 700;
  color: #1a56db;
  text-align: center;
  margin-bottom: 1.5rem;
  position: relative;
  padding-bottom: 10px;
}

.section-title::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 80px;
  height: 3px;
  background: linear-gradient(90deg, #3b82f6, #8b5cf6);
  border-radius: 2px;
}

/* 专业服务网格 */
.professional-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
  margin-top: 1.2rem;
}

.professional-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  border-top: 3px solid transparent;
  border: 1px solid #e5e7eb;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.professional-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 7px 20px rgba(0, 0, 0, 0.1);
  border-color: #3b82f6;
}

.blue { border-color: #3b82f6; }
.green { border-color: #10b981; }
.purple { border-color: #8b5cf6; }
.orange { border-color: #f59e0b; }

.card-icon {
  width: 70px;
  height: 70px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 15px;
}

.blue .card-icon { background: linear-gradient(135deg, #3b82f6, #2563eb); }
.green .card-icon { background: linear-gradient(135deg, #10b981, #059669); }
.purple .card-icon { background: linear-gradient(135deg, #8b5cf6, #7c3aed); }
.orange .card-icon { background: linear-gradient(135deg, #f59e0b, #d97706); }

.card-title {
  font-size: 3.5rem; /* 14px -> 3.5rem */
  font-weight: 700;
  text-align: center;
  margin-bottom: 12px;
  color: #1f2937;
}

.card-content {
  font-size: 3rem; /* 12px -> 3rem */
  line-height: 1.5;
  color: #4b5563;
  text-align: center;
  font-weight: 500;
  flex-grow: 1;
}

/* 价值与流程容器 */
.value-process-container {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  height: 100%;
}

.value-section,
.process-section {
  flex: 1;
  min-width: 340px;
  display: flex;
  flex-direction: column;
  height: 100%;
}

/* 核心价值展示 */
.value-section {
  background: #f9fafb;
  border-radius: 14px;
  padding: 1.8rem 1.2rem;
  border: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.value-container {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.value-item {
  text-align: center;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.value-number {
  font-size: 6.5rem; /* 26px -> 6.5rem */
  font-weight: 700;
  background: linear-gradient(135deg, #1a56db, #7e22ce);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  line-height: 1.2;
  margin-bottom: 10px;
}

.value-label {
  font-size: 3.5rem; /* 14px -> 3.5rem */
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 8px;
}

.value-desc {
  font-size: 2.75rem; /* 11px -> 2.75rem */
  color: #6b7280;
  font-weight: 500;
}

/* 服务流程展示 */
.process-section {
  background: white;
  border-radius: 14px;
  padding: 1.8rem 1.2rem;
  border: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.process-steps {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  align-items: center;
  gap: 10px;
}

.process-step {
  text-align: center;
  padding: 1.2rem;
  min-width: 130px;
  flex: 1;
}

.step-number {
  width: 42px;
  height: 42px;
  background: #1a56db;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 4.25rem; /* 17px -> 4.25rem */
  font-weight: 700;
  margin: 0 auto 12px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.08);
}

.step-title {
  font-size: 3.5rem; /* 14px -> 3.5rem */
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 8px;
}

.step-desc {
  font-size: 2.75rem; /* 11px -> 2.75rem */
  color: #6b7280;
  font-weight: 500;
}

.process-arrow {
  font-size: 4.25rem; /* 17px -> 4.25rem */
  color: #9ca3af;
  font-weight: bold;
}

/* 行动号召区域 */
.cta-section {
  background: linear-gradient(135deg, #1e3a8a 0%, #0d2b64 100%);
  border-radius: 14px;
  padding: 2rem 1.2rem;
  text-align: center;
  width: 100%;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.cta-content {
  margin-bottom: 1.5rem;
}

.cta-title {
  font-size: 4.5rem; /* 18px -> 4.5rem */
  font-weight: 700;
  color: white;
  margin-bottom: 1rem;
}

.cta-subtitle {
  font-size: 3rem; /* 12px -> 3rem */
  color: #e0f2fe;
  margin: 0 auto 1.5rem;
  line-height: 1.5;
  font-weight: 500;
  max-width: 80%;
}

.cta-button {
  background: #4cc9f0;
  color: #0d2b64;
  border: none;
  padding: 12px 35px;
  font-size: 3.5rem; /* 14px -> 3.5rem */
  font-weight: 700;
  border-radius: 40px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 5px 12px rgba(76, 201, 240, 0.3);
  margin-bottom: 1.5rem;
  display: inline-block;
  text-decoration: none;
}

.cta-button:hover {
  background: #38bdf8;
  transform: translateY(-2px);
  box-shadow: 0 7px 15px rgba(76, 201, 240, 0.4);
}

.cta-info {
  display: flex;
  gap: 24px;
  color: #a5b4fc;
  font-size: 3rem; /* 12px -> 3rem */
  font-weight: 500;
  justify-content: center;
}

.cta-info p {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .section-title {
    font-size: 4rem; /* 16px -> 4rem */
  }

  .value-section,
  .process-section {
    min-width: 100%;
  }

  .process-steps {
    flex-wrap: wrap;
  }

  .process-arrow {
    transform: rotate(90deg);
    margin: 12px 0;
  }

  .cta-section {
    padding: 1.5rem 1rem;
  }
}

@media (max-width: 992px) {
  .platform-logo h1 {
    font-size: 4rem; /* 16px -> 4rem */
  }

  .welcome-title {
    font-size: 4rem; /* 16px -> 4rem */
  }

  .section-title {
    font-size: 4rem; /* 16px -> 4rem */
  }

  .card-content {
    font-size: 2.75rem; /* 11px -> 2.75rem */
  }

  .value-number {
    font-size: 6rem; /* 24px -> 6rem */
  }

  .value-label {
    font-size: 3.25rem; /* 13px -> 3.25rem */
  }

  .cta-title {
    font-size: 4rem; /* 16px -> 4rem */
  }

  .cta-subtitle {
    font-size: 2.75rem; /* 11px -> 2.75rem */
  }

  /* 小屏幕调整为自然流布局 */
  .section-top,
  .section-services,
  .section-value-process,
  .section-cta {
    flex: none;
    height: auto;
  }
}

@media (max-width: 768px) {
  .dashboard-content {
    padding: 0.8rem;
  }

  .platform-logo {
    flex-direction: column;
  }

  .professional-grid {
    grid-template-columns: 1fr;
  }

  .value-container {
    grid-template-columns: 1fr;
  }

  .section-title {
    font-size: 3.75rem; /* 15px -> 3.75rem */
    margin-bottom: 1.2rem;
  }

  .welcome-title {
    font-size: 3.75rem; /* 15px -> 3.75rem */
  }

  .cta-title {
    font-size: 3.75rem; /* 15px -> 3.75rem */
  }

  .cta-info {
    flex-direction: column;
    gap: 12px;
  }

  .cta-section {
    padding: 1.2rem 0.8rem;
  }
}

@media (max-width: 576px) {
  .platform-logo h1 {
    font-size: 3.5rem; /* 14px -> 3.5rem */
  }

  .platform-tagline {
    font-size: 2.5rem; /* 10px -> 2.5rem */
  }

  .welcome-title {
    font-size: 3.5rem; /* 14px -> 3.5rem */
  }

  .section-title {
    font-size: 3.5rem; /* 14px -> 3.5rem */
  }

  .card-title {
    font-size: 3.25rem; /* 13px -> 3.25rem */
  }

  .card-content {
    font-size: 2.5rem; /* 10px -> 2.5rem */
  }

  .value-number {
    font-size: 5.5rem; /* 22px -> 5.5rem */
  }

  .value-label {
    font-size: 3rem; /* 12px -> 3rem */
  }

  .cta-title {
    font-size: 3.5rem; /* 14px -> 3.5rem */
  }

  .cta-subtitle {
    font-size: 2.5rem; /* 10px -> 2.5rem */
    max-width: 95%;
  }

  .cta-button {
    padding: 10px 30px;
    font-size: 3rem; /* 12px -> 3rem */
  }

  .step-number {
    width: 38px;
    height: 38px;
    font-size: 3.75rem; /* 15px -> 3.75rem */
  }

  .step-title {
    font-size: 3rem; /* 12px -> 3rem */
  }

  .step-desc {
    font-size: 2.5rem; /* 10px -> 2.5rem */
  }
}

/* 加载动画 */
@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(15px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in {
  animation: fade-in 0.7s ease-out forwards;
}

/* 图表容器优化 */
.h-60 {
  min-height: 180px;
}

.flex-center {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 220px;
}
</style>