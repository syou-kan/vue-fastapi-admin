# migrate.py
import asyncio
import aiomysql
import sys
from pathlib import Path

# 添加项目根目录到系统路径
sys.path.append(str(Path(__file__).parent.parent))

from app.settings.config import settings


async def migrate_database():
    # 获取数据库配置
    db_config = settings.TORTOISE_ORM["connections"]["default"]["credentials"]

    print(f"Connecting to database: {db_config['database']}@{db_config['host']}:{db_config['port']}")

    try:
        # 创建数据库连接
        conn = await aiomysql.connect(
            host=db_config["host"],
            port=db_config["port"],
            user=db_config["user"],
            password=db_config["password"],
            db=db_config["database"],
            autocommit=True
        )

        async with conn.cursor() as cursor:
            # 1. 检查表是否存在（不区分大小写）
            await cursor.execute("SHOW TABLES")
            tables = await cursor.fetchall()
            user_table_exists = any("user" in table[0].lower() for table in tables)

            if not user_table_exists:
                print("❌ Table 'user' does not exist in database")
                # 尝试创建表
                print("🔄 Attempting to create 'user' table...")
                try:
                    await create_user_table(cursor)
                    print("✅ Created 'user' table successfully")
                except Exception as e:
                    print(f"❌ Failed to create 'user' table: {str(e)}")
                    return
            else:
                print("ℹ️ Table 'user' exists")

            # 2. 检查并添加列
            await check_and_add_column(cursor, "user", "company_code", "VARCHAR(100) COMMENT '统一社会信用代码'")
            await check_and_add_column(cursor, "user", "company_name", "VARCHAR(100) COMMENT '公司名称'")
            await check_and_add_column(cursor, "user", "user_type",
                                       "VARCHAR(20) NOT NULL DEFAULT 'customer' COMMENT '用户类型: admin=管理员, staff=普通用户, customer=客户账号'")

            # 3. 修改phone列为NOT NULL
            await modify_column(cursor, "user", "phone", "VARCHAR(20) NOT NULL COMMENT '电话'")

            # 4. 检查并添加索引 - 使用更安全的索引创建方式
            await safe_add_index(cursor, "user", "company_code", "idx_user_company_code")
            await safe_add_index(cursor, "user", "company_name", "idx_user_company_name")
            await safe_add_index(cursor, "user", "user_type", "idx_user_type")

            print("✅ Database migration completed successfully")

    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()


async def create_user_table(cursor):
    """创建用户表"""
    create_table_sql = """
                       CREATE TABLE `user` \
                       ( \
                           `id`           BIGINT       NOT NULL PRIMARY KEY AUTO_INCREMENT, \
                           `username`     VARCHAR(20)  NOT NULL COMMENT '用户名称', \
                           `alias`        VARCHAR(30) NULL COMMENT '姓名', \
                           `email`        VARCHAR(255) NOT NULL COMMENT '邮箱', \
                           `password`     VARCHAR(128) NULL COMMENT '密码', \
                           `is_active`    BOOLEAN      NOT NULL DEFAULT 1 COMMENT '是否激活', \
                           `is_superuser` BOOLEAN      NOT NULL DEFAULT 0 COMMENT '是否为超级管理员', \
                           `last_login`   DATETIME NULL COMMENT '最后登录时间', \
                           `dept_id`      INT NULL COMMENT '部门ID', \
                           `phone`        VARCHAR(20)  NOT NULL COMMENT '电话', \
                           `created_at`   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP, \
                           `updated_at`   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, \
                           UNIQUE KEY `username` (`username`), \
                           UNIQUE KEY `email` (`email`), \
                           INDEX          `is_active` (`is_active`), \
                           INDEX          `is_superuser` (`is_superuser`), \
                           INDEX          `last_login` (`last_login`), \
                           INDEX          `dept_id` (`dept_id`), \
                           INDEX          `phone` (`phone`)
                       ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci; \
                       """
    await cursor.execute(create_table_sql)


async def check_and_add_column(cursor, table, column, definition):
    """检查列是否存在，不存在则添加"""
    try:
        await cursor.execute(f"""
            SELECT COUNT(*) FROM information_schema.columns 
            WHERE table_schema = DATABASE() 
            AND table_name = '{table}' 
            AND column_name = '{column}'
        """)
        result = await cursor.fetchone()
        if result[0] == 0:
            await cursor.execute(f"ALTER TABLE `{table}` ADD COLUMN `{column}` {definition}")
            print(f"✅ Added column {table}.{column}")
        else:
            print(f"ℹ️ Column {table}.{column} already exists")
    except Exception as e:
        print(f"⚠️ Failed to check/add column {table}.{column}: {str(e)}")
        raise


async def modify_column(cursor, table, column, definition):
    """修改列定义"""
    try:
        # 检查列是否存在
        await cursor.execute(f"""
            SELECT COUNT(*) FROM information_schema.columns 
            WHERE table_schema = DATABASE() 
            AND table_name = '{table}' 
            AND column_name = '{column}'
        """)
        result = await cursor.fetchone()
        if result[0] > 0:
            await cursor.execute(f"ALTER TABLE `{table}` MODIFY COLUMN `{column}` {definition}")
            print(f"✅ Modified column {table}.{column}")
        else:
            print(f"ℹ️ Column {table}.{column} does not exist, skipping modification")
    except Exception as e:
        print(f"⚠️ Failed to modify column {table}.{column}: {str(e)}")
        raise


async def safe_add_index(cursor, table, column, index_name=None):
    """安全地添加索引，避免重复索引问题"""
    if not index_name:
        index_name = f"idx_{table}_{column}"

    try:
        # 1. 检查索引是否已存在
        await cursor.execute(f"""
            SELECT COUNT(*) FROM information_schema.statistics 
            WHERE table_schema = DATABASE() 
            AND table_name = '{table}' 
            AND index_name = '{index_name}'
        """)
        result = await cursor.fetchone()

        if result[0] > 0:
            print(f"ℹ️ Index {index_name} already exists on {table}.{column}")
            return

        # 2. 检查列是否存在
        await cursor.execute(f"""
            SELECT COUNT(*) FROM information_schema.columns 
            WHERE table_schema = DATABASE() 
            AND table_name = '{table}' 
            AND column_name = '{column}'
        """)
        result = await cursor.fetchone()

        if result[0] == 0:
            print(f"⚠️ Column {table}.{column} does not exist, cannot create index")
            return

        # 3. 创建索引
        await cursor.execute(f"CREATE INDEX `{index_name}` ON `{table}` (`{column}`)")
        print(f"✅ Added index {index_name} on {table}.{column}")

    except Exception as e:
        print(f"⚠️ Failed to add index {index_name} on {table}.{column}: {str(e)}")
        # 尝试使用备用方法创建索引
        try:
            await cursor.execute(f"ALTER TABLE `{table}` ADD INDEX `{index_name}` (`{column}`)")
            print(f"✅ Added index {index_name} on {table}.{column} (using ALTER TABLE)")
        except Exception as alt_e:
            print(f"❌ Failed to add index using ALTER TABLE: {str(alt_e)}")
        raise


if __name__ == "__main__":
    print("Starting database migration...")
    asyncio.run(migrate_database())