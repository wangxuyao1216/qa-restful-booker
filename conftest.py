"""全局 fixture：被测服务地址、HTTP 会话、鉴权 token。

设计要点：
1. base_url 走环境变量，方便 CI 里换成被测环境地址，不用改代码。
2. api 用 Session 而不是每次 requests.get，复用 TCP 连接，也让 cookie/header 自动延续。
3. token 用 session 级 scope：整个测试会话只登录一次，避免每个用例都打 /auth。
   代价是 token 一旦失效会影响后续用例，所以另有一个函数级 fixture 用于"token 失效"的异常用例。
"""

import os

import pytest
import requests
from api.auth_api import AuthAPI
from pathlib import Path
import yaml

BASE_URL = os.getenv("BASE_URL", "http://localhost:3001")
AUTH_USER = os.getenv("AUTH_USER", "admin")
AUTH_PASS = os.getenv("AUTH_PASS", "password123")
DATA_DIR = Path(__file__).parent / "data"
BASE_PAYLOAD = {
    "firstname": "Jim", "lastname": "Brown", "totalprice": 111,
    "depositpaid": True,
    "bookingdates": {"checkin": "2026-11-10", "checkout": "2026-11-15"},
}


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
    resp = AuthAPI(api, base_url).login(AUTH_USER, AUTH_PASS)
    assert resp.status_code == 200, f"登录失败: {resp.status_code} {resp.text}"
    return resp.json()["token"]

def load_case(name: str):
    return yaml.safe_load((DATA_DIR / "booking.yaml").read_text(encoding="utf-8"))[name]

@pytest.fixture
def created_ids(api, base_url, token):
    """用例里 append 造出来的 id，结束时统一删，保证可重复跑。"""
    ids = []
    yield ids
    for bid in ids:
        api.delete(f"{base_url}/booking/{bid}", headers={"Cookie": f"token={token}"})

@pytest.fixture
def booking_id(api, base_url, created_ids):
    r = api.post(f"{base_url}/booking", json=BASE_PAYLOAD)
    assert r.status_code == 200, r.text
    bid = r.json()["bookingid"]
    created_ids.append(bid)
    return bid