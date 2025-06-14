* [2025-06-13 22:25:29] - 在“联系客服”弹窗中，将图片源从 logo.svg 更新为 qrcode.png。
* [2025-06-13 22:32:08] - 将“联系客服”图标替换为带文本的按钮，以提高可见性。
* [2025-06-14 11:45:09] - 从 Git 版本控制中移除了 .venv 目录，并更新了 .gitignore 文件。
* [2025-06-14 19:40:00] - 完成了“分角色工作台”首页的开发，包括前后端所有业务逻辑的实现。
* [2025-06-14 19:51:00] - [调试状态更新: 通过纠正 `app/api/v1/dashboard.py` 中的依赖注入，修复了应用启动失败的问题。]
* [2025-06-14 20:07:06] - 在 `app/core/init_app.py` 中添加了“仪表盘”和“工作台”的初始化菜单逻辑。
* [2025-06-14 20:07:06] - 在 `app/core/init_app.py` 中添加了“仪表盘”和“工作台”的初始化菜单逻辑。
* [2025-06-14 20:25:07] - [调试状态更新: 通过为 `app/api/v1/dashboard.py` 中缺失标签的路由添加标签，从根源上修复了 `app/controllers/api.py` 中的 `IndexError`。]
* [2025-06-14 20:26:53] - [调试状态更新: 通过在 `app/api/v1/dashboard.py` 中为路由添加缺失的 `tags`，修复了 `app/controllers/api.py` 中的 `IndexError`。]
* [2025-06-14 20:38:19] - Recent Change: Modified `app/controllers/api.py` to correctly handle multiple HTTP methods for a single API route, resolving a `sqlite3.ProgrammingError`. This involved iterating through methods and ensuring the `tags` field was correctly formatted as a string for the database.
* [2025-06-14 20:43:33] - [Debug Status Update: Fixed a 500 Internal Server Error on the workbench endpoint by ensuring Pydantic models are properly serialized to dictionaries before being passed to the JSONResponse.]
* [2025-06-14 21:01:00] - [UI 优化] 对 `AdminView.vue` 和 `index.vue` 进行了全面界面优化，包括添加图标、统一主题色、实现悬浮效果和个性化欢迎语。