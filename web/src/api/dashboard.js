import { request } from '@/utils/http'

/**
 * 获取工作台数据
 * @returns
 */
export function getWorkbenchData() {
  return request({
    url: '/dashboard/workbench',
    method: 'get',
  })
}