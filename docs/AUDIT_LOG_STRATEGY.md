# 审计日志数据库分区策略

## 1. 背景

随着系统使用量的增加，审计日志表 (`audit_log`) 的数据量急剧增长，对查询性能和数据管理带来了挑战。为了解决这个问题，我们决定采用基于时间的数据库分区策略，将日志数据按月进行分区存储。

## 2. 设计方案

### 2.1. 分区键

我们将使用 `created_at` 字段作为分区键，因为它最能代表日志数据的时间属性。

### 2.2. 分区策略

- **分区类型**: 按范围 (RANGE) 分区
- **分区周期**: 每月一个分区
- **分区命名**: `audit_log_yYYYY_mMM` (例如: `audit_log_y2023_m12`)

### 2.3. 数据保留策略

- **在线数据**: 保留最近 6 个月的数据在线，以供快速查询。
- **归档数据**: 超过 6 个月的数据将被直接删除。

## 3. 数据库迁移 (DDL)

以下是将现有 `audit_log` 表迁移到分区表的 DDL 语句。

```sql
-- 1. 创建一个新的分区表结构
CREATE TABLE audit_log_new (
    id INT NOT NULL,
    user_id INT,
    action VARCHAR(255),
    details TEXT,
    created_at TIMESTAMP NOT NULL,
    PRIMARY KEY (id, created_at)
) PARTITION BY RANGE (created_at);

-- 2. 为最近和未来的月份创建分区
CREATE TABLE audit_log_y2023_m11 PARTITION OF audit_log_new
    FOR VALUES FROM ('2023-11-01') TO ('2023-12-01');
CREATE TABLE audit_log_y2023_m12 PARTITION OF audit_log_new
    FOR VALUES FROM ('2023-12-01') TO ('2024-01-01');
CREATE TABLE audit_log_y2024_m01 PARTITION OF audit_log_new
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

-- 3. 将旧表数据迁移到新表
INSERT INTO audit_log_new SELECT * FROM audit_log;

-- 4. 重命名旧表和新表
ALTER TABLE audit_log RENAME TO audit_log_old;
ALTER TABLE audit_log_new RENAME TO audit_log;

-- 5. (可选) 删除旧表
-- DROP TABLE audit_log_old;
```

**回滚方案**:
如果迁移失败，可以执行以下操作回滚：
1.  删除 `audit_log_new` 表。
2.  如果已重命名，将 `audit_log_old` 重命名回 `audit_log`。

## 4. 分区管理脚本 (伪代码)

以下是 `manage_partitions.py` 脚本的伪代码，用于自动化管理分区。

```python
# scripts/manage_partitions.py

import psycopg2
from datetime import datetime, timedelta

def get_db_connection():
    # 从配置文件或环境变量获取连接信息
    pass

def create_future_partitions(months_ahead=3):
    """为未来 N 个月创建分区"""
    conn = get_db_connection()
    cursor = conn.cursor()
    for i in range(1, months_ahead + 1):
        # 计算未来月份的起始和结束日期
        # 生成 CREATE TABLE 语句
        # 执行 SQL
        pass
    cursor.close()
    conn.close()

def archive_old_partitions(months_to_keep=6):
    """删除超过保留期限的旧分区"""
    conn = get_db_connection()
    cursor = conn.cursor()
    # 计算保留期限之前的日期
    # 查询需要删除的分区
    # for partition in old_partitions:
    #     # 删除分区 (DROP TABLE)
    pass
    cursor.close()
    conn.close()

if __name__ == "__main__":
    # 使用 argparse 解析命令行参数
    # 调用相应函数
    pass
```

## 5. 部署与运维

### 5.1. 运行迁移脚本

1.  **备份数据库**: 在执行任何操作之前，请务必完整备份数据库。
2.  **执行迁移**: 使用数据库管理工具（如 `psql`）连接到数据库，并执行 `migrations/partition_audit_log.sql` 脚本。
    ```bash
    psql -h <host> -U <user> -d <database> -f migrations/partition_audit_log.sql
    ```

### 5.2. 定期执行分区管理

使用 Cron 或其他调度工具定期执行 `manage_partitions.py` 脚本，以确保分区被及时创建和清理。

**Cron 示例 (每月1号凌晨执行)**:
```cron
0 2 1 * * /usr/bin/python /path/to/project/scripts/manage_partitions.py create_future_partitions
0 3 1 * * /usr/bin/python /path/to/project/scripts/manage_partitions.py archive_old_partitions