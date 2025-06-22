import { request } from '@/utils/http'

const R_PREFIX = '/orders'

export default {
  fetchOrders: async (params = {}) => {
    const { page = 1, pageSize, order_no, tracking_no, item_name, username, ...restQuery } = params

    // 直接使用前端传入的分页参数，不做转换
    const search = [order_no, tracking_no, item_name, username].filter(Boolean).join(' ').trim()

    const finalParams = {
      page,
      page_size: pageSize || 10,
      ...restQuery,
    }
    if (search) {
      finalParams.search = search
    }

    const response = await request.get(`${R_PREFIX}/`, { params: finalParams })

    // 确保返回格式符合 CrudTable 的预期
    return {
      data: response.data || [],
      total: response.total || 0,
    }
  },
  fetchOrder: (id) => {
    return request.get(`${R_PREFIX}/${id}`)
  },
  createOrder: (data) => {
    return request.post(`${R_PREFIX}/`, data)
  },
  updateOrder: (id, data) => {
    return request.put(`${R_PREFIX}/${id}`, data)
  },
  deleteOrder: (id) => {
    return request.delete(`${R_PREFIX}/${id}`)
  },
  updateOrderReceipt: (id, data) => {
    return request.patch(`${R_PREFIX}/${id}/receipt`, data)
  },
}