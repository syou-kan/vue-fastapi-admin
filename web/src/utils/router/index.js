/**
 * 路由相关工具函数
 * 用于增强路由处理的稳定性和错误处理
 */

/**
 * 验证路由路径是否有效
 * @param {Object} router - Vue Router 实例
 * @param {string} path - 要验证的路径
 * @returns {boolean} 路径是否有效
 */
export function isValidRoute(router, path) {
  try {
    if (!path || typeof path !== 'string') {
      return false
    }
    
    const route = router.resolve(path)
    return route && route.name && route.name !== 'NotFound'
  } catch (error) {
    console.warn('路由验证失败:', path, error)
    return false
  }
}

/**
 * 安全的路由跳转
 * @param {Object} router - Vue Router 实例
 * @param {string} path - 目标路径
 * @param {string} fallbackPath - 回退路径
 * @param {Object} query - 查询参数
 */
export function safeRouterPush(router, path, fallbackPath = '/dashboard', query = {}) {
  try {
    const targetPath = isValidRoute(router, path) ? path : fallbackPath
    console.log(`路由跳转: ${path} -> ${targetPath}`)
    
    router.push({ path: targetPath, query })
  } catch (error) {
    console.error('路由跳转失败:', error)
    // 最后的回退
    try {
      router.push(fallbackPath)
    } catch (fallbackError) {
      console.error('回退路由跳转也失败:', fallbackError)
    }
  }
}

/**
 * 获取用户默认首页路径
 * 根据用户权限返回合适的首页
 * @param {Object} userStore - 用户状态
 * @returns {string} 默认首页路径
 */
export function getUserDefaultHomePage(userStore) {
  if (!userStore) {
    return '/dashboard'
  }
  
  // 超级用户默认到仪表盘
  if (userStore.is_superuser) {
    return '/dashboard'
  }
  
  // 普通用户也默认到仪表盘
  return '/dashboard'
}

/**
 * 路由错误处理器
 * @param {Error} error - 路由错误
 * @param {Object} router - Vue Router 实例
 * @param {string} fallbackPath - 回退路径
 */
export function handleRouteError(error, router, fallbackPath = '/dashboard') {
  console.error('路由错误:', error)
  
  // 根据错误类型进行不同的处理
  if (error.name === 'NavigationDuplicated') {
    // 重复导航错误，可以忽略
    console.warn('重复导航，忽略错误')
    return
  }
  
  if (error.name === 'NavigationAborted') {
    // 导航被中止
    console.warn('导航被中止')
    return
  }
  
  // 其他错误，尝试跳转到回退页面
  safeRouterPush(router, fallbackPath)
}

/**
 * 清理并验证重定向参数
 * @param {Object} query - 路由查询参数
 * @param {Object} router - Vue Router 实例
 * @returns {Object} 清理后的参数和验证结果
 */
export function cleanAndValidateRedirect(query, router) {
  const result = {
    isValid: false,
    redirectPath: null,
    cleanQuery: { ...query }
  }
  
  if (query.redirect) {
    const redirectPath = query.redirect
    result.isValid = isValidRoute(router, redirectPath)
    result.redirectPath = redirectPath
    
    // 清理重定向参数
    Reflect.deleteProperty(result.cleanQuery, 'redirect')
  }
  
  return result
}
