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
        <div mt-30>
          <n-input
            v-model:value="loginInfo.phone_number"
            autofocus
            class="h-50 items-center pl-10 text-16"
            placeholder="请输入手机号"
            :maxlength="20"
          />
        </div>
        <div mt-30>
          <n-input
            v-model:value="loginInfo.password"
            class="h-50 items-center pl-10 text-16"
            type="password"
            show-password-on="mousedown"
            placeholder="123456"
            :maxlength="20"
            @keypress.enter="handleLogin"
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
            @click="handleLogin"
          >
            {{ $t('views.login.text_login') }}
          </n-button>
        </div>

       <div mt-20 text-center>
         <router-link to="/register" class="text-blue-500 hover:underline">
           没有账户？立即注册
         </router-link>
       </div>
      </div>
    </div>
  </AppPage>
</template>

<script setup>
import { lStorage, setToken } from '@/utils'
import bgImg from '@/assets/images/login_bg.webp'
import api from '@/api'
import { addDynamicRoutes } from '@/router'
import { useI18n } from 'vue-i18n'

const router = useRouter()
const { query } = useRoute()
const { t } = useI18n({ useScope: 'global' })

const loginInfo = ref({
  phone_number: '',
  password: '',
})

initLoginInfo()

function initLoginInfo() {
  const localLoginInfo = lStorage.get('loginInfo')
  if (localLoginInfo) {
    loginInfo.value.phone_number = localLoginInfo.phone_number || ''
    loginInfo.value.password = localLoginInfo.password || ''
  }
}

const loading = ref(false)
async function handleLogin() {
  const { phone_number, password } = loginInfo.value
  if (!phone_number || !password) {
    $message.warning('请输入手机号和密码')
    return
  }
  try {
    loading.value = true
    $message.loading(t('views.login.message_login_success'))
    const res = await api.login({ phone_number, password: password.toString() })
    $message.success(t('views.login.message_login_success'))
    setToken(res.data.access_token)
    
    // 添加动态路由
    await addDynamicRoutes()
    
    // 智能重定向逻辑
    let redirectPath = '/dashboard' // 默认重定向到仪表盘
    
    if (query.redirect) {
      const targetPath = query.redirect
      console.log('检查重定向路径:', targetPath)
      
      // 验证重定向路径是否有效
      try {
        const route = router.resolve(targetPath)
        if (route && route.name && route.name !== 'NotFound') {
          redirectPath = targetPath
          console.log('使用重定向路径:', redirectPath)
        } else {
          console.warn('重定向路径无效，使用默认路径:', targetPath)
        }
      } catch (routeError) {
        console.warn('路径解析失败，使用默认路径:', routeError)
      }
      
      // 清理查询参数
      const cleanQuery = { ...query }
      Reflect.deleteProperty(cleanQuery, 'redirect')
      
      // 执行重定向
      router.push({ path: redirectPath, query: cleanQuery })
    } else {
      // 没有重定向参数，直接跳转到默认页面
      router.push(redirectPath)
    }
    
  } catch (e) {
    console.error('登录失败:', e)
    $message.error('登录失败，请检查用户名和密码')
  }
  loading.value = false
}
</script>
