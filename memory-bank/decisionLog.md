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
---
### Decision
[2025-06-14] - 从版本控制中移除 .venv 目录

**Rationale:**
`.venv` 目录是 Python 的虚拟环境文件夹，包含了特定于本地开发环境的依赖和配置。将其提交到共享的 git 仓库是不良实践，原因如下：
1.  **环境不一致**: 不同开发者的操作系统或依赖版本可能不同，共享 `.venv` 会导致冲突和 "在我机器上能跑" 的问题。
2.  **仓库膨胀**: 虚拟环境可能包含大量文件，显著增加仓库体积，拖慢克隆和拉取速度。
3.  **安全风险**: 配置文件中可能无意间包含敏感信息。
正确的做法是让每个开发者根据 `requirements.txt` 或类似文件在本地创建自己的虚拟环境。

**Implications/Details:**
- **.gitignore**: 将 `.venv/` 添加到 `.gitignore` 文件，防止未来再次提交。
- **Git History**: 使用 `git rm -r --cached .venv` 命令从 Git 的跟踪记录中移除该目录，但保留本地副本，以免破坏当前开发环境。
- **Commit**: 提交 `.gitignore` 的更改，完成修正。
---
### Decision
[2025-06-14 18:15:36] - 搭建“分角色工作台”功能项目架构

**Rationale:**
根据产品需求，为新的“分角色工作台”功能创建初始的前后端文件结构，以便后续的开发工作。该功能旨在根据用户角色（管理员/普通用户）在登录后展示不同的信息面板。

**Implications/Details:**
- **后端 (FastAPI)**:
  - 创建了新的 Schema 文件 `app/schemas/dashboard.py` 用于定义数据模型。
  - 创建了新的路由文件 `app/api/v1/dashboard.py` 用于处理工作台的 API 逻辑。
  - 在 `app/api/v1/__init__.py` 中注册了新的 `dashboard` 路由，使其在 `/api/v1/dashboard` 路径下可用。
- **前端 (Vue)**:
  - 创建了新的 API 模块 `web/src/api/dashboard.js` 用于封装对后端工作台接口的请求。
  - 在 `web/src/router/routes/index.js` 中添加了 `/dashboard/workbench` 路由，并将其设为默认访问页面。
  - 创建了主视图组件 `web/src/views/dashboard/workbench/index.vue`。
  - 创建了两个子组件，分别用于管理员视图 (`AdminView.vue`) 和普通用户视图 (`UserView.vue`)，位于 `web/src/views/dashboard/workbench/components/` 目录下。
---
### Decision (Code)
[2025-06-14 19:41:00] - 实现“分角色工作台”首页功能

**Rationale:**
根据产品需求，为不同角色的用户（管理员和普通用户）提供定制化的首页视图，以展示最相关的信息，提升用户体验。

**Details:**
- **后端 (FastAPI)**:
  - 在 `app/schemas/dashboard.py` 中定义了 `AdminWorkbenchData` 和 `UserWorkbenchData` 两个 Pydantic 模型，用于规范不同角色的数据结构。
  - 在 `app/controllers/dashboard.py` 中创建了 `DashboardController`，封装了核心业务逻辑：根据当前用户的 `is_superuser` 属性，异步查询并返回相应的数据。管理员数据通过 `tortoise-orm` 从 `User`, `Role`, `Menu`, `Api` 表中聚合统计得出；普通用户数据为静态模拟数据。
  - 在 `app/api/v1/dashboard.py` 中创建了 `/workbench` API 端点，通过依赖注入获取当前用户，并调用 `DashboardController` 来获取数据，最后使用 `Success` 模型进行包装返回。
- **前端 (Vue)**:
  - 在 `web/src/api/dashboard.js` 中添加了 `getWorkbenchData` 函数，用于向后端发起 API 请求。
  - 在 `web/src/views/dashboard/workbench/components/` 目录下创建了 `AdminView.vue` 和 `UserView.vue` 两个子组件，分别用于展示管理员和普通用户的工作台卡片信息。它们通过 `props`接收来自父组件的数据。
  - 在主视图 `web/src/views/dashboard/workbench/index.vue` 中：
    - 使用 `onMounted`钩子调用 `getWorkbenchData` API。
    - 使用 Pinia 的 `useUserStore` 获取当前用户的 `isSuperUser` 状态。
    - 通过计算属性 `currentView` 动态地选择渲染 `AdminView` 或 `UserView`。
    - 使用 `<component :is="currentView">` 动态组件特性实现视图切换。
    - 添加了加载状态，提升了用户体验。
---
### Decision (Debug)
[2025-06-14 19:51:00] - [Bug Fix Strategy: 纠正 FastAPI 依赖注入用法]

**Rationale:**
应用因 `app/api/v1/dashboard.py` 中的 `TypeError: ... is not a callable object` 而启动失败。根本原因是 FastAPI 依赖注入系统的使用不当。`app/core/dependency.py` 中的变量 `DependAuth` 已经是一个 `Depends()` 的实例，但在路由的函数签名中它被再次用 `Depends()` 包装，这是不正确的。修复方法是直接使用 `DependAuth` 作为 `current_user` 参数的默认值。

**Details:**
- **受影响文件:** `app/api/v1/dashboard.py`
- **变更:** 将 `get_workbench_data` 函数签名从 `current_user: BaseUser = Depends(DependAuth)` 修改为 `current_user: BaseUser = DependAuth`。
- **导入:** 确保从 `app.core.dependency` 正确导入 `DependAuth`。
---
### Decision (Code)
[2025-06-14 20:06:40] - 在应用初始化时添加“仪表盘”和“工作台”菜单

**Rationale:**
用户反馈“工作台”菜单未显示。为了解决这个问题，需要在系统初始化时将“仪表盘”作为顶级目录菜单、“工作台”作为其子菜单添加到数据库中。这可以确保所有用户在启动应用时都能看到该菜单项。

**Details:**
- **受影响文件:** `app/core/init_app.py`
- **变更:** 在 `init_menus` 函数中，添加了创建“仪表盘” (catalog) 和“工作台” (menu) 的逻辑。通过这种方式，`init_roles` 函数会自动处理新菜单的权限分配，确保所有角色都能访问。
---
### Decision (Debug)
[2025-06-14 20:24:43] - [Bug Fix Strategy: 通过强制执行路由规则修复 IndexError]

**Rationale:**
在 `app/controllers/api.py` 中发生的 `IndexError` 的根本原因，是 `refresh_api` 函数错误地假设了所有 API 路由都定义了 `tags`。在处理位于 `app/api/v1/dashboard.py` 的一个没有标签的路由时，代码尝试访问一个空列表的第一个元素，导致程序崩溃。与其修改处理脚本以容忍不规范的数据（治标），正确的解决方案是找到并修复不合规的路由，强制执行“所有路由都必须有标签”这一既定规则（治本）。

**Details:**
- **受影响文件:** `app/api/v1/dashboard.py`
- **变更:** 为 `/workbench` 路由的装饰器 `@router.get` 添加了 `tags=["仪表盘"]` 参数，确保其符合项目规范。
---
### Decision (Debug)
[2025-06-14 20:26:23] - [Bug Fix Strategy: 通过为路由添加缺失的 `tags` 来修复 `IndexError`]

**Rationale:**
应用程序在刷新 API 列表时，由于 `app/controllers/api.py` 中的 `IndexError: list index out of range` 而崩溃。根本原因是 `app/api/v1/dashboard.py` 中定义的 `/workbench` 路由缺少 `tags` 属性。`api.py` 中的代码期望 `route.tags` 是一个非空列表，并试图访问其第一个元素。虽然最初尝试修补 `api.py` 以处理空标签，但正确且更稳健的解决方案是强制所有 API 路由都拥有标签，因为这是本项目中 API 文档和分组的预期约定。

**Details:**
- **受影响的文件:** `app/controllers/api.py`, `app/api/v1/dashboard.py`
- **最初不正确的修复:** 尝试修改 `app/controllers/api.py`，在 `route.tags` 为空时分配一个默认标签。这导致了一个 `Pylance` 类型错误，因为 `tags` 变量可能变成 `str` 而不是 `list`，与数据库模型不兼容。
- **正确的修复:** 在 `app/api/v1/dashboard.py` 中为 `/workbench` 端点的 `@router.get` 装饰器添加了 `tags=["仪表盘"]`。这确保了路由符合应用程序的期望，并从根源上解决了 `IndexError`。
---
### Decision (Debug)
[2025-06-14 20:43:33] - [Bug Fix Strategy: Fix Pydantic Model Serialization in API Response]

**Rationale:**
The backend was throwing a `500 Internal Server Error` on the `/api/v1/dashboard/workbench` endpoint. The root cause was that a Pydantic model object was being passed directly into a `JSONResponse` subclass without being serialized into a dictionary first. Starlette's/FastAPI's `JSONResponse` does not automatically serialize Pydantic models. The fix is to explicitly call `.model_dump()` on the Pydantic object before passing it to the response class to ensure it's a JSON-serializable dictionary.

**Details:**
- **Affected File:** `app/api/v1/dashboard.py`
- **Change:** Modified `return Success(data=data)` to `return Success(data=data.model_dump())`.
---
### Decision (Code)
[2025-06-14 21:01:00] - 优化前端工作台 UI

**Rationale:**
根据 `spec-pseudocode` 模式提供的规范，对管理员工作台和首页视图进行 UI 优化，旨在提升用户体验和视觉一致性。关键变更包括统一品牌颜色、增加图标以提高信息辨识度、改善布局，并添加个性化元素。

**Details:**
- **文件:** `web/src/views/dashboard/workbench/components/AdminView.vue`
  - **图标和布局:** 为每个信息卡片（用户数、角色数、菜单数、接口数）引入了 `@vicons/antd` 图标。
  - **主题色:** 使用 `useThemeVars` 从 `web/settings/theme.json` 动态获取主题色，并应用于图标颜色。
  - **交互性:** 为卡片添加了 `hoverable` 属性和背景色，以提供悬浮反馈效果。
- **文件:** `web/src/views/dashboard/workbench/index.vue`
  - **个性化欢迎语:** 在页面顶部增加了一个欢迎区域，显示用户头像、昵称，并根据当前时间动态生成问候语（如“早上好”、“下午好”）。
  - **布局调整:** 将欢迎语和工作台内容分别放入独立的 `n-card` 组件中，使页面结构更清晰。