import { useUserStore } from '@/store'

export function addBaseParams(params) {
  if (!params.userId) {
    params.userId = useUserStore().userId
  }
}

export function resolveResError(code, originalMessage) {
  // 如果业务 code 表明不是绝对成功 (例如，不等于 200)
  // 并且原始消息是 "ok" 或 "success" (忽略大小写) 等可能引起误解的简单肯定词，
  // 则替换为一个更通用的错误提示。
  // TODO: 未来可以考虑将 '操作未按预期完成' 进行国际化处理
  if (code !== 200 && (originalMessage?.toLowerCase() === 'ok' || originalMessage?.toLowerCase() === 'success')) {
    return `操作未按预期完成 (状态码: ${code})`;
  }

  // 如果不是上述特殊情况，则按原逻辑处理
  switch (code) {
    case 400:
      return originalMessage ?? '请求参数错误';
    case 401:
      return originalMessage ?? '登录已过期';
    case 403:
      return originalMessage ?? '没有权限';
    case 404:
      return originalMessage ?? '资源或接口不存在';
    case 500:
      return originalMessage ?? '服务器异常';
    default:
      // 如果 originalMessage 存在，则使用它，否则使用包含 code 的通用未知异常消息。
      // TODO: 未来可以考虑将 '发生未知错误' 进行国际化处理
      return originalMessage ?? `发生未知错误 (状态码: ${code})`;
  }
}
