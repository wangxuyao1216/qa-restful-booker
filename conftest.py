"""全局 fixture：被测服务地址、HTTP 会话、鉴权 token。

设计要点（面试会问）：
1. base_url 走环境变量，方便 CI 里换成被测环境地址，不用改代码。
2. api 用 Session 而不是每次 requests.get，复用 TCP 连接，也让 cookie/header 自动延续。
3. token 用 session 级 scope：整个测试会话只登录一次，避免每个用例都打 /auth。
   代价是 token 一旦失效会影响后续用例，所以另有一个函数级 fixture 用于"token 失效"的异常用例。
"""

import os

import pytest
import requests

BASE_URL = os.getenv("BASE_URL", "http://localhost:3001")
AUTH_USER = os.getenv("AUTH_USER", "admin")
AUTH_PASS = os.getenv("AUTH_PASS", "password123")


@pytest.fixture(scope="session")
def base_url() -> str:
    return BASE_URL


@pytest.fixture(scope="session")
def api():
    session = requests.Session()
    session.headers.update(
        {"Content-Type": "application/json", "Accept": "application/json"}
    )
    yield session
    session.close()


@pytest.fixture(scope="session")
def token(api, base_url) -> str:
    """登录一次，拿到后续 PUT/DELETE 需要的 token。"""
    resp = api.post(
        f"{base_url}/auth",
        json={"username": AUTH_USER, "password": AUTH_PASS},
    )
    assert resp.status_code == 200, f"登录失败: {resp.status_code} {resp.text}"
    return resp.json()["token"]
