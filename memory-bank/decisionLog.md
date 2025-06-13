# Decision Log

This file records architectural and implementation decisions using a list format.
2025-06-13 09:00:15 - Log of updates made.

*

---
### Decision
[2025-06-13 09:11:00] - 新增订单按“是否收到货物”状态筛选功能

**Rationale:**
为了增强订单管理模块的可用性，允许用户根据货物的接收状态快速查找和管理订单。这是用户提出的明确需求，旨在提高运营效率。

**Implications/Details:**
- **后端**: 修改 `/api/v1/orders` API，增加 `items_received_status` (枚举: "all", "0", "1") 查询参数。更新 `OrderQuerySchema` 和 `OrderController` 以处理新的筛选逻辑。依赖现有的 `orders.items_received` (INT) 字段。
- **前端**: 在 `web/src/views/order/index.vue` 中添加下拉选择框，选项包括“全部”、“已收”、“未收”。选择后，调用更新后的API。
- **国际化**: 为新UI元素添加中英文翻译 (`cn.json`, `en.json`)。
- **数据模型**: 利用现有的 `orders.items_received` 字段。

## Decision

*

## Rationale

*

## Implementation Details

*
---
### Decision
[2025-06-13] - 新增“联系客服”功能

**Rationale:**
为了给用户提供便捷的技术支持和问题反馈渠道，提升用户体验和满意度。这是一个常见的平台功能，可以增强用户的信任感。

**Implications/Details:**
- **UI/UX**:
  - 在全局顶部导航栏 (`web/src/layout/components/header/index.vue`) 添加一个新的“联系客服”图标按钮。
  - 点击按钮后，弹出一个模态框（Modal）。
  - 模态框中将展示客服的联系方式（如二维码、电话、工作时间等）。
- **组件**:
  - 创建一个新的Vue组件 `web/src/components/common/ContactSupportModal.vue` 来封装模态框的逻辑和内容。
  - 使用项目已集成的 Naive UI 的 `n-modal` 组件来实现。
- **国际化**:
  - 在 `web/i18n/messages/cn.json` 和 `web/i18n/messages/en.json` 中为新UI元素（按钮提示、模态框标题等）添加中英文翻译。
---
### Decision (Debug)
[2025-06-13 22:02] - [Bug Fix Strategy: 添加 UnoCSS Iconify Preset 配置]

**Rationale:**
虽然项目已安装了所需的 Iconify 依赖，但缺少必要的 UnoCSS 预设配置，导致图标类名无法被正确解析。通过添加 preset-icons 配置可以启用图标功能。

**Details:**
- 影响文件: web/unocss.config.js
- 需添加 @unocss/preset-icons 预设
- 相关组件: web/src/layout/components/header/index.vue
---
### Decision (Debug)
[2025-06-13 22:11] - [Bug Fix Strategy: 使用 Naive UI 内置图标替代 Iconify]

**Rationale:**
由于 Iconify 配置和依赖安装遇到问题，改用 Naive UI 内置的图标系统是更简单可靠的解决方案。这样可以避免额外的依赖问题，同时保持UI一致性。

**Details:**
- 修改文件: web/src/layout/components/header/index.vue
- 将 i-ant-design-customer-service-outlined 类替换为 CustomerServiceOutlined 组件
- 新增依赖: @vicons/antd