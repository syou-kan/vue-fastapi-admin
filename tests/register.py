import requests
import json
import logging
from faker import Faker
import random
import string

# --- 基本配置 ---
# 用户注册的 API 端点
URL = "http://127.0.0.1:9999/api/v1/user/register"
NUM_USERS_TO_REGISTER = 100
HEADERS = {"Content-Type": "application/json"}

# --- 日志设置 ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("registration.log", mode='w', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# --- Faker 初始化 ---
fake = Faker('zh_CN')

# --- 辅助函数 ---
def generate_strong_password(length=12):
    """生成包含字母、数字和特殊字符的强密码。"""
    if length < 8:
        raise ValueError("密码长度应至少为8个字符。")
    
    characters = string.ascii_letters + string.digits + string.punctuation
    while True:
        password = ''.join(random.choice(characters) for i in range(length))
        if (any(c.islower() for c in password)
                and any(c.isupper() for c in password)
                and any(c.isdigit() for c in password)
                and any(c in string.punctuation for c in password)):
            return password

# --- 主注册循环 ---
def bulk_register_users():
    """使用伪造数据注册指定数量的用户。"""
    logging.info(f"开始批量注册 {NUM_USERS_TO_REGISTER} 个用户。")
    
    for i in range(NUM_USERS_TO_REGISTER):
        # 为每个账户生成唯一的测试数据
        user_data = {
            "username": fake.user_name(),
            "password": generate_strong_password(),
            "phone_number": fake.phone_number(),
            "company_name": fake.company()
        }

        try:
            # 发送 POST 请求
            response = requests.post(URL, headers=HEADERS, data=json.dumps(user_data, ensure_ascii=False).encode('utf-8'))

            # 对错误的狀態碼 (4xx or 5xx) 抛出异常
            response.raise_for_status()

            # 记录成功日志
            logging.info(f"成功注册用户 #{i + 1}: {user_data['username']}")

        except requests.exceptions.HTTPError as http_err:
            logging.error(f"用户 {user_data['username']} 发生 HTTP 错误: {http_err}")
            logging.error(f"响应内容: {response.text}")
        except requests.exceptions.ConnectionError as conn_err:
            logging.critical(f"发生连接错误: {conn_err}。正在中止。")
            logging.critical("请确保后端服务器正在运行并且可以在指定的URL访问。")
            break  # 如果服务器无法访问，则停止
        except requests.exceptions.Timeout as timeout_err:
            logging.warning(f"用户 {user_data['username']} 发生超时错误: {timeout_err}")
        except requests.exceptions.RequestException as err:
            logging.error(f"用户 {user_data['username']} 发生错误: {err}")

    logging.info("批量注册过程已完成。")

if __name__ == "__main__":
    bulk_register_users()