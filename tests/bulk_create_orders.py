import asyncio
import requests
import json
import logging
from faker import Faker
import random
import string

# --- 项目组件导入 ---
# 这需要将项目根目录添加到 PYTHONPATH
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.core.init_app import init_db
from app.controllers.user import user_controller

# --- 基本配置 ---
BASE_URL = "http://127.0.0.1:9999/api/v1"
LOGIN_URL = f"{BASE_URL}/base/access_token"
ORDERS_URL = f"{BASE_URL}/orders/"

# 使用一个已知的管理员账户进行登录
ADMIN_PHONE_NUMBER = "18888888888" # 默认超级管理员手机号，请根据实际情况修改
ADMIN_PASSWORD = "123456" # 默认超级管理员密码，请根据实际情况修改

HEADERS = {"Content-Type": "application/json"}

# --- 日志设置 ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bulk_orders.log", mode='w', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# --- Faker 初始化 ---
fake = Faker('zh_CN')

# --- 核心功能函数 ---

def login_and_get_token():
    """使用管理员凭据登录并获取认证令牌。"""
    login_payload = {
        "phone_number": ADMIN_PHONE_NUMBER,
        "password": ADMIN_PASSWORD
    }
    try:
        response = requests.post(LOGIN_URL, json=login_payload)
        response.raise_for_status()
        token = response.json().get("data", {}).get("access_token")
        if not token:
            logging.error("登录失败：未在响应中找到 access_token。")
            return None
        logging.info("管理员登录成功，已获取令牌。")
        return token
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"登录时发生 HTTP 错误: {http_err}")
        logging.error(f"响应内容: {http_err.response.text}")
        return None
    except requests.exceptions.RequestException as e:
        logging.error(f"登录时发生一般请求错误: {e}")
        return None

async def get_all_users_from_db():
    """直接从数据库获取所有用户。"""
    await init_db()
    total, users = await user_controller.list(page=1, page_size=9999)
    logging.info(f"从数据库成功获取到 {total} 个用户。")
    return users

def create_random_order_payload(username):
    """为指定用户生成一个随机订单的数据。"""
    return {
        "order_no": ''.join(random.choices(string.ascii_uppercase + string.digits, k=12)),
        "tracking_no": fake.ssn(),
        "item_name": fake.word(),
        "item_quantity": random.randint(1, 100),
        "item_amount": round(random.uniform(10.0, 1000.0), 2),
        "remarks": fake.sentence(),
        "username": username,
        "items_received": random.choice([True, False])
    }

async def bulk_create_orders_for_users():
    """为所有用户批量创建随机订单。"""
    token = login_and_get_token()
    if not token:
        logging.critical("无法获取认证令牌，脚本终止。")
        return

    users = await get_all_users_from_db()
    if not users:
        logging.warning("没有用户可供创建订单，脚本终止。")
        return

    auth_headers = HEADERS.copy()
    auth_headers["token"] = token

    for user in users:
        username = user.username
        num_orders = random.randint(1, 5)
        logging.info(f"准备为用户 '{username}' 创建 {num_orders} 个订单。")

        for i in range(num_orders):
            order_payload = create_random_order_payload(username)
            try:
                response = requests.post(ORDERS_URL, headers=auth_headers, json=order_payload)
                response.raise_for_status()
                logging.info(f"成功为用户 '{username}' 创建了订单 #{i + 1} (订单号: {order_payload['order_no']})。")
            except requests.exceptions.HTTPError as http_err:
                logging.error(f"为用户 '{username}' 创建订单时发生 HTTP 错误: {http_err}")
                logging.error(f"请求内容: {json.dumps(order_payload)}")
                logging.error(f"响应内容: {response.text}")
            except requests.exceptions.RequestException as req_err:
                logging.error(f"为用户 '{username}' 创建订单时发生请求错误: {req_err}")

    logging.info("批量创建订单过程已完成。")

if __name__ == "__main__":
    asyncio.run(bulk_create_orders_for_users())