# run.py
import asyncio
import uvicorn
from uvicorn.config import LOGGING_CONFIG
from app.settings.config import settings
from tortoise import Tortoise

async def init_db():
    # 初始化数据库连接
    await Tortoise.init(
        config=settings.TORTOISE_ORM,
        modules={"models": ["app.models.admin"]}
    )
    # 创建数据库表（但不覆盖已有数据）
    await Tortoise.generate_schemas(safe=True)
    print("✅ Database tables created successfully")

async def main():
    await init_db()
    config = uvicorn.Config(
        "app:app",
        host="0.0.0.0",
        port=9999,
        reload=True,
        log_config=LOGGING_CONFIG
    )
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    # 修改默认日志配置
    LOGGING_CONFIG["formatters"]["default"]["fmt"] = "%(asctime)s - %(levelname)s - %(message)s"
    LOGGING_CONFIG["formatters"]["default"]["datefmt"] = "%Y-%m-%d %H:%M:%S"
    LOGGING_CONFIG["formatters"]["access"][
        "fmt"
    ] = '%(asctime)s - %(levelname)s - %(client_addr)s - "%(request_line)s" %(status_code)s'
    LOGGING_CONFIG["formatters"]["access"]["datefmt"] = "%Y-%m-%d %H:%M:%S"

    # 创建新的事件循环
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()
        asyncio.set_event_loop(None)