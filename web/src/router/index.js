import { createRouter, createWebHistory, createWebHashHistory } from 'vue-router'
import { setupRouterGuard } from './guard'
import { basicRoutes, EMPTY_ROUTE, NOT_FOUND_ROUTE } from './routes'
import { getToken, isNullOrWhitespace } from '@/utils'
import { useUserStore, usePermissionStore } from '@/store'

const isHash = import.meta.env.VITE_USE_HASH === 'true'
export const router = createRouter({
  history: isHash ? createWebHashHistory('/') : createWebHistory('/'),
  routes: basicRoutes,
  scrollBehavior: () => ({ left: 0, top: 0 }),
})

export async function setupRouter(app) {
  await addDynamicRoutes()
  setupRouterGuard(router)
  app.use(router)
}

export async function resetRouter() {
  const basicRouteNames = getRouteNames(basicRoutes)
  router.getRoutes().forEach((route) => {
    const name = route.name
    if (!basicRouteNames.includes(name)) {
      router.removeRoute(name)
    }
  })
}

export async function addDynamicRoutes() {
  const token = getToken()

  // 没有token情况
  if (isNullOrWhitespace(token)) {
    router.addRoute(EMPTY_ROUTE)
    return
  }
  
  // 有token的情况
  const userStore = useUserStore()
  const permissionStore = usePermissionStore()
  
  try {
    // 获取用户信息
    if (!userStore.userId) {
      await userStore.getUserInfo()
    }
    
    // 生成动态路由
    const accessRoutes = await permissionStore.generateRoutes()
    await permissionStore.getAccessApis()
    
    // 验证路由是否有效
    if (!accessRoutes || accessRoutes.length === 0) {
      console.warn('警告：未获取到有效的动态路由，使用默认路由')
      // 添加默认的仪表盘路由作为回退
      const defaultRoute = {
        name: 'Dashboard',
        path: '/dashboard',
        component: () => import('@/views/dashboard/index.vue'),
        meta: { title: '仪表盘', icon: 'mdi:view-dashboard' }
      }
      router.addRoute(defaultRoute)
    } else {
      // 添加有效的动态路由
      accessRoutes.forEach((route) => {
        try {
          if (route && route.name && !router.hasRoute(route.name)) {
            router.addRoute(route)
          }
        } catch (routeError) {
          console.error(`添加路由失败: ${route?.name}`, routeError)
        }
      })
    }
    
    // 清理空路由并添加404路由
    router.hasRoute(EMPTY_ROUTE.name) && router.removeRoute(EMPTY_ROUTE.name)
    router.addRoute(NOT_FOUND_ROUTE)
    
  } catch (error) {
    console.error('动态路由生成失败:', error)
    
    // 错误处理：提供基本的回退路由
    try {
      const fallbackRoute = {
        name: 'FallbackDashboard',
        path: '/dashboard',
        component: () => import('@/views/dashboard/index.vue'),
        meta: { title: '仪表盘', icon: 'mdi:view-dashboard' }
      }
      router.addRoute(fallbackRoute)
      router.hasRoute(EMPTY_ROUTE.name) && router.removeRoute(EMPTY_ROUTE.name)
      router.addRoute(NOT_FOUND_ROUTE)
      
      console.info('已添加回退路由，用户可以访问基本功能')
    } catch (fallbackError) {
      console.error('回退路由添加失败:', fallbackError)
      // 最后的错误处理：登出用户
      await userStore.logout()
    }
  }
}

export function getRouteNames(routes) {
  return routes.map((route) => getRouteName(route)).flat(1)
}

function getRouteName(route) {
  const names = [route.name]
  if (route.children && route.children.length) {
    names.push(...route.children.map((item) => getRouteName(item)).flat(1))
  }
  return names
}
