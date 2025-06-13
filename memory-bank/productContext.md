# Product Context

This file provides a high-level overview of the project and the expected product that will be created. Initially it is based upon projectBrief.md (if provided) and all other available project-related information in the working directory. This file is intended to be updated as the project evolves, and should be used to inform all other modes of the project's goals and context.
2025-06-13 08:59:13 - Log of updates made will be appended as footnotes to the end of this file.

*
2025-06-13 09:02:32 - Updated Project Goal, Key Features, and Overall Architecture based on README-en.md.

## Project Goal

* vue-fastapi-admin is a modern front-end and back-end separation development platform that combines FastAPI, Vue3, and Naive UI. It incorporates RBAC (Role-Based Access Control) management, dynamic routing, and JWT (JSON Web Token) authentication, making it ideal for rapid development of small to medium-sized applications and also serves as a valuable learning resource.

## Key Features

*   **Popular Tech Stack**: The backend is developed with the high-performance asynchronous framework FastAPI using Python 3.11, while the front-end is powered by cutting-edge technologies such as Vue3 and Vite, complemented by the efficient package manager, pnpm.
*   **Code Standards**: The project is equipped with various plugins for code standardization and quality control, ensuring consistency and enhancing team collaboration efficiency.
*   **Dynamic Routing**: Backend dynamic routing combined with the RBAC model allows for fine-grained control of menus and routing.
*   **JWT Authentication**: User identity verification and authorization are handled through JWT, enhancing the application's security.
*   **Granular Permission Control**: Implements detailed permission management including button and interface level controls, ensuring different roles and users have appropriate permissions.
*   **Order Filtering by Received Status**: Allows users to filter orders in the order management module based on whether items have been received. (Added 2025-06-13)
*   **便捷的客户支持**: 提供一键联系客服功能，方便用户快速获得帮助。 (Added 2025-06-13)

## Overall Architecture

*   The project follows a front-end and back-end separation architecture.
*   **Backend**: Built with FastAPI (Python 3.11), organized into API interfaces, controllers, core logic, models (data), schemas (structure), settings, and utilities.
*   **Frontend**: Developed using Vue3, Vite, and Naive UI, with pnpm for package management. The structure includes build scripts, public resources, settings, and a source directory containing API definitions, assets, components, composables, directives, layout, routing, state management (Pinia), styles, utilities, and views.