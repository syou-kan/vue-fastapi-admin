import { request } from '@/utils/http'

const base_url = '/dashboard'

export const dashboardApi = {
  getDashboardData() {
    return request({
      url: `${base_url}`,
      method: 'GET',
    })
  },
}