<!-- web/src/views/register/index.vue -->
<template>
  <AppPage :show-footer="true" bg-cover :style="{ backgroundImage: `url(${bgImg})` }">
    <div
      style="transform: translateY(25px)"
      class="m-auto max-w-1500 min-w-345 f-c-c rounded-10 bg-white bg-opacity-60 p-15 card-shadow"
      dark:bg-dark
    >
      <div hidden w-380 px-20 py-35 md:block>
        <icon-custom-front-page pt-10 text-300 color-primary></icon-custom-front-page>
      </div>

      <div w-320 flex-col px-20 py-35>
        <h5 f-c-c text-24 font-normal color="#6a6a6a">
          <icon-custom-logo mr-10 text-50 color-primary />{{ $t('app_name') }}
        </h5>

        <h3 mt-20 mb-10 text-center>用户注册</h3>

        <div mt-15>
          <n-input
            v-model:value="registerInfo.company_name"
            class="h-50 items-center pl-10 text-16"
            placeholder="公司名称"
          />
        </div>

        <div mt-15>
          <n-input
            v-model:value="registerInfo.company_code"
            class="h-50 items-center pl-10 text-16"
            placeholder="统一社会信用代码"
          />
        </div>

        <div mt-15>
          <n-input
            v-model:value="registerInfo.phone"
            class="h-50 items-center pl-10 text-16"
            placeholder="手机号"
          />
        </div>

        <div mt-15>
          <n-input
            v-model:value="registerInfo.real_name"
            class="h-50 items-center pl-10 text-16"
            placeholder="姓名"
          />
        </div>

        <div mt-15>
          <n-input
            v-model:value="registerInfo.password"
            class="h-50 items-center pl-10 text-16"
            type="password"
            show-password-on="mousedown"
            placeholder="密码"
          />
        </div>

        <div mt-15>
          <n-input
            v-model:value="registerInfo.confirm_password"
            class="h-50 items-center pl-10 text-16"
            type="password"
            show-password-on="mousedown"
            placeholder="确认密码"
            @keypress.enter="handleRegister"
          />
        </div>

        <div mt-15>
          <n-input
            v-model:value="registerInfo.email"
            class="h-50 items-center pl-10 text-16"
            placeholder="邮箱（选填）"
          />
        </div>

        <div mt-20>
          <n-button
            h-50
            w-full
            rounded-5
            text-16
            type="primary"
            :loading="loading"
            @click="handleRegister"
          >
            注册
          </n-button>
        </div>

        <div mt-10 text-center>
          <n-button text @click="goToLogin">已有账号？去登录</n-button>
        </div>
      </div>
    </div>
  </AppPage>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import bgImg from '@/assets/images/login_bg.webp'
import api from '@/api'

const router = useRouter()
const message = useMessage()

const registerInfo = ref({
  company_name: '',
  company_code: '',
  phone: '',
  real_name: '',
  password: '',
  confirm_password: '',
  email: ''
})

const loading = ref(false)

function goToLogin() {
  router.push('/login')
}

async function handleRegister() {
  const { company_name, company_code, phone, real_name, password, confirm_password, email } = registerInfo.value

  // 简单前端验证
  if (!company_name || !company_code || !phone || !real_name || !password || !confirm_password) {
    message.warning('请填写所有必填项')
    return
  }

  if (password !== confirm_password) {
    message.warning('两次输入的密码不一致')
    return
  }

  try {
    loading.value = true
    await api.register({
      company_name,
      company_code,
      phone,
      real_name,
      password,
      confirm_password,
      email
    })

    message.success('注册成功，请登录')
    router.push('/login')
  } catch (error) {
    message.error(error.message || '注册失败')
  } finally {
    loading.value = false
  }
}
</script>