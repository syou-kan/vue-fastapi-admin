<template>
  <div>
    <n-card title="公司信息概览" class="mb-4">
      <n-grid cols="1 s:2 m:3" responsive="screen">
        <!-- 添加编辑按钮 -->
        <n-gi :span="3" class="text-right mb-4">
          <n-button type="primary" @click="showEditModal = true">编辑信息</n-button>
        </n-gi>

        <!-- 动态数据绑定 -->
        <n-gi>
          <n-statistic label="公司名称" :value="companyInfo.name" />
        </n-gi>
        <n-gi>
          <n-statistic label="统一社会信用代码" :value="companyInfo.code" />
        </n-gi>
        <n-gi>
          <n-statistic label="注册时间" :value="companyInfo.registerDate" />
        </n-gi>
      </n-grid>

      <n-divider />

      <n-h3>公司简介</n-h3>
      <n-p>{{ companyInfo.description }}</n-p>
    </n-card>

    <!-- 编辑模态框 -->
    <n-modal v-model:show="showEditModal">
      <n-card style="width: 600px" title="编辑公司信息">
        <n-form :model="companyInfo">
          <n-form-item label="公司名称">
            <n-input v-model:value="companyInfo.name" />
          </n-form-item>
          <n-form-item label="统一社会信用代码">
            <n-input v-model:value="companyInfo.code" />
          </n-form-item>
          <n-form-item label="注册时间">
            <n-date-picker v-model:value="companyInfo.registerDate" type="date" />
          </n-form-item>
          <n-form-item label="公司简介">
            <n-input v-model:value="companyInfo.description" type="textarea" rows="5" />
          </n-form-item>
        </n-form>
        <template #footer>
          <n-space justify="end">
            <n-button @click="showEditModal = false">取消</n-button>
            <n-button type="primary" @click="saveCompanyInfo">保存</n-button>
          </n-space>
        </template>
      </n-card>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useMessage } from 'naive-ui'

const message = useMessage()
const showEditModal = ref(false)

// 从API获取公司信息
const companyInfo = ref({
  name: '',
  code: '',
  registerDate: '',
  description: ''
})

// 模拟API调用
async function fetchCompanyInfo() {
  // 实际项目中这里调用API
  return new Promise(resolve => {
    setTimeout(() => {
      resolve({
        name: '示例科技有限公司',
        code: '91310115MA1K4XXXXX',
        registerDate: '2020-05-20',
        description: '示例科技有限公司成立于2020年，是一家专注于企业级应用开发的科技公司。我们致力于为客户提供高效、安全、稳定的系统解决方案，帮助企业实现数字化转型。公司拥有一支经验丰富的技术团队，在多个行业领域有成功的实施案例。'
      })
    }, 500)
  })
}

// 保存公司信息
async function saveCompanyInfo() {
  try {
    // 实际项目中这里调用API保存
    message.success('公司信息更新成功')
    showEditModal.value = false
  } catch (e) {
    message.error('保存失败: ' + e.message)
  }
}

onMounted(async () => {
  companyInfo.value = await fetchCompanyInfo()
})
</script>