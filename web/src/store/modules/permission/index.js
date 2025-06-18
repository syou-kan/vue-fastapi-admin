import { defineStore } from 'pinia'
import { useUserStore } from '../user'
import { basicRoutes, vueModules } from '@/router/routes'
import { shallowRef } from 'vue'
import Layout from '@/layout/index.vue'
import api from '@/api'

// * 后端路由相关函数
// 根据后端传来数据构建出前端路由

function buildRoutes(routes = []) {
  return routes.map((e) => {
    const route = {
      name: e.name,
      path: e.path,
      component: shallowRef(Layout),
      isHidden: e.is_hidden,
      redirect: e.redirect,
      meta: {
        title: e.name,
        icon: e.icon,
        order: e.order,
        keepAlive: e.keepalive,
      },
      children: [],
    }

    if (e.children && e.children.length > 0) {
      // 有子菜单
      route.children = e.children.map((e_child) => {
        const componentPath = `/src/views${e_child.component}/index.vue`
        const component = vueModules[componentPath]
        
        if (!component) {
          console.warn(`组件未找到: ${componentPath}，使用默认组件`)
          // 使用默认的错误组件或空组件
          return {
            name: e_child.name,
            path: e_child.path,
            component: () => import('@/views/error-page/404.vue'),
            isHidden: e_child.is_hidden,
            meta: {
              title: e_child.name,
              icon: e_child.icon,
              order: e_child.order,
              keepAlive: e_child.keepalive,
              error: '组件加载失败'
            },
          }
        }
        
        return {
          name: e_child.name,
          path: e_child.path,
          component: component,
          isHidden: e_child.is_hidden,
          meta: {
            title: e_child.name,
            icon: e_child.icon,
            order: e_child.order,
            keepAlive: e_child.keepalive,
          },
        }
      }).filter(Boolean) // 过滤掉无效的路由
    } else {
      // 没有子菜单，创建一个默认的子路由
      const componentPath = `/src/views${e.component}/index.vue`
      const component = vueModules[componentPath]
      
      if (!component) {
        console.warn(`组件未找到: ${componentPath}，使用404页面作为回退`)
        // 如果组件不存在，使用404页面作为回退
        route.children.push({
          name: `${e.name}Default`,
          path: '',
          component: () => import('@/views/error-page/404.vue'),
          isHidden: true,
          meta: {
            title: e.name,
            icon: e.icon,
            order: e.order,
            keepAlive: e.keepalive,
            error: '组件未找到'
          },
        })
      } else {
        route.children.push({
          name: `${e.name}Default`,
          path: '',
          component: component,
          isHidden: true,
          meta: {
            title: e.name,
            icon: e.icon,
            order: e.order,
            keepAlive: e.keepalive,
          },
        })
      }
    }

    return route
  }).filter(route => route && route.children && route.children.length > 0) // 过滤掉无效的路由
}

export const usePermissionStore = defineStore('permission', {
  state() {
    return {
      accessRoutes: [],
      accessApis: [],
    }
  },
  getters: {
    routes() {
      return basicRoutes.concat(this.accessRoutes)
    },
    menus() {
      const userStore = useUserStore()
      return this.routes.filter((route) => {
        if (route.name === 'ErrorPage' && !userStore.is_superuser) {
          return false
        }
        return route.name && !route.isHidden
      })
    },
    apis() {
      return this.accessApis
    },
  },
  actions: {
    async generateRoutes() {
      const res = await api.getUserMenu() // 调用接口获取后端传来的菜单路由
      const backendRoutes = res.data || []
      const dynamicRoutes = buildRoutes(backendRoutes)
      
      // 处理路由显示逻辑
      const processedRoutes = dynamicRoutes.map(route => {
        if (route.name === '仪表盘') {
          // 将仪表盘显示为"首页"
          return {
            ...route,
            name: 'Dashboard',
            isHidden: false, // 确保显示在菜单中
            meta: {
              ...route.meta,
              title: '首页',
              icon: 'mdi:view-dashboard-outline',
              order: 0
            }
          }
        }
        // 确保个人中心不显示在菜单中
        if (route.name === '个人中心') {
          return {
            ...route,
            isHidden: true // 强制隐藏个人中心
          }
        }
        return route
      }).filter(route => !route.isHidden) // 过滤掉隐藏的路由
      
      this.accessRoutes = processedRoutes
      return this.accessRoutes
    },
    async getAccessApis() {
      const res = await api.getUserApi()
      this.accessApis = res.data
      return this.accessApis
    },
    resetPermission() {
      this.$reset()
    },
  },
})
