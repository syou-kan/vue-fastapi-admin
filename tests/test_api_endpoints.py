import pytest
import requests
import time

# 假设API基础URL
BASE_URL = "http://127.0.0.1:9999/api/v1"

# --- 测试数据 ---
VALID_CREDENTIALS = {"phone_number": "18888888888", "password": "123456"}
ADMIN_CREDENTIALS = {"phone_number": "18888888888", "password": "123456"} # 假设管理员账户
USER_CREDENTIALS = {"phone_number": "13800138000", "password": "123456"} # 假设普通用户账户

# --- Pytest Fixtures ---

@pytest.fixture(scope="session")
def admin_token():
    """获取管理员Token"""
    response = requests.post(f"{BASE_URL}/base/access_token", json=ADMIN_CREDENTIALS)
    response.raise_for_status()
    return response.json()["access_token"]

@pytest.fixture(scope="session")
def user_token():
    """获取普通用户Token"""
    response = requests.post(f"{BASE_URL}/base/access_token", json=USER_CREDENTIALS)
    response.raise_for_status()
    return response.json()["access_token"]

@pytest.fixture
def auth_headers(admin_token):
    """提供带管理员Token的请求头"""
    return {"token": admin_token}

@pytest.fixture
def user_auth_headers(user_token):
    """提供带普通用户Token的请求头"""
    return {"token": user_token}

# --- 测试类 ---

class TestBaseAPI:
    """基础模块测试"""

    def test_get_token_success(self):
        response = requests.post(f"{BASE_URL}/base/access_token", json=VALID_CREDENTIALS)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data.get("token_type", "").lower() == "bearer"

    @pytest.mark.parametrize("payload, expected_status", [
        ({"phone_number": "correct_phone", "password": "wrong_password"},),
        ({"phone_number": "non_existent_phone", "password": "any_password"},),
        ({"phone_number": "correct_phone"}, 422),
        ({"password": "correct_password"}, 422),
        ({}, 422),
        ({"phone_number": "", "password": ""}, 422),
    ])
    def test_get_token_invalid_cases(self, payload, expected_status):
        response = requests.post(f"{BASE_URL}/base/access_token", json=payload)
        if isinstance(expected_status, list):
            assert response.status_code in expected_status
        else:
            assert response.status_code == expected_status

    def test_get_userinfo(self, auth_headers):
        response = requests.get(f"{BASE_URL}/base/userinfo", headers=auth_headers)
        assert response.status_code == 200
        assert "username" in response.json()

    def test_get_usermenu(self, auth_headers):
        response = requests.get(f"{BASE_URL}/base/usermenu", headers=auth_headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)

class TestUserAPI:
    """用户模块测试"""

    def test_register_and_check_existence(self):
        unique_id = int(time.time())
        payload = {
            "username": f"user_{unique_id}",
            "password": "password123",
            "phone_number": f"130{unique_id % 100000000:08d}",
            "company_name": "Company", "credit_code": f"CODE{unique_id}"
        }
        # 成功注册
        response = requests.post(f"{BASE_URL}/user/register", json=payload)
        assert response.status_code == 200
        # 用户名已存在
        response = requests.post(f"{BASE_URL}/user/register", json=payload)
        assert response.status_code == 422

    def test_get_user_list(self, auth_headers):
        response = requests.get(f"{BASE_URL}/user/list", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data and "total" in data

class TestRoleAPI:
    """角色模块测试"""

    def test_get_role_list(self, auth_headers):
        response = requests.get(f"{BASE_URL}/role/list", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data and "total" in data

    def test_create_role_and_check_existence(self, auth_headers):
        unique_name = f"role_{int(time.time())}"
        payload = {"name": unique_name, "desc": "Test role"}
        # 成功创建
        response = requests.post(f"{BASE_URL}/role/create", headers=auth_headers, json=payload)
        assert response.status_code == 200
        # 角色名已存在
        response = requests.post(f"{BASE_URL}/role/create", headers=auth_headers, json=payload)
        assert response.status_code == 422

class TestOrderAPI:
    """订单模块测试"""

    def test_create_order(self, auth_headers):
        payload = {
            "order_no": f"ORD_{int(time.time())}", "item_name": "Test Item",
            "item_quantity": 1, "username": "admin" # 假设admin用户存在
        }
        response = requests.post(f"{BASE_URL}/orders/", headers=auth_headers, json=payload)
        assert response.status_code == 200

    def test_get_order_list(self, auth_headers):
        response = requests.get(f"{BASE_URL}/orders/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data and "total" in data

    def test_get_single_order(self, auth_headers):
        # 先创建一个订单来获取ID
        payload = {"order_no": f"ORD_{int(time.time())}", "item_name": "Item for lookup", "item_quantity": 1, "username": "admin"}
        create_resp = requests.post(f"{BASE_URL}/orders/", headers=auth_headers, json=payload)
        assert create_resp.status_code == 200
        order_id = create_resp.json()["id"]
        # 获取订单
        response = requests.get(f"{BASE_URL}/orders/{order_id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["id"] == order_id
        # 获取不存在的订单
        response = requests.get(f"{BASE_URL}/orders/999999", headers=auth_headers)
        assert response.status_code == 404

class TestDashboardAPI:
    """仪表盘模块测试"""

    def test_get_dashboard_admin(self, auth_headers):
        response = requests.get(f"{BASE_URL}/dashboard", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "user_count" in data and "order_count" in data

    def test_get_dashboard_user(self, user_auth_headers):
        response = requests.get(f"{BASE_URL}/dashboard", headers=user_auth_headers)
        assert response.status_code == 200
        assert "welcome_message" in response.json()