"""鉴权相关用例。

第 1 周只要求"跑通"，所以这里刻意只有 3 条：
- 服务存活（ping）
- 登录成功能拿到 token
- 登录失败不给 token

第 2 周开始补 booking 的 CRUD，第 3 周补异常与 schema 校验。
"""

import pytest

from api.auth_api import AuthAPI
from api.base import BaseAPI


@pytest.mark.smoke
def test_ping_returns_201(api, base_url):
    """服务存活探针：/ping 正常返回 201。"""
    resp = api.get(f"{base_url}/ping")
    BaseAPI.expect(resp, 201)


@pytest.mark.smoke
def test_login_returns_token(api, base_url, token):
    """登录成功，token 是非空字符串。"""
    assert isinstance(token, str) and token, "token 为空"
    assert token.isalnum(), f"token 格式异常: {token}"


def test_login_with_wrong_password_returns_no_token(api, base_url):
    """密码错误时不应发放 token。

    注意：restful-booker 这里返回的是 200 + {"reason": "Bad credentials"}，
    不是 401。这是接口设计上的坑，用例必须按真实行为断言，
    不能想当然写 expect(resp, 401)。
    """
    resp = AuthAPI(api, base_url).login("admin", "wrong-password")
    BaseAPI.expect(resp, 200)
    assert "token" not in resp.json(), f"密码错误却发了 token: {resp.json()}"
    assert "reason" in resp.json(), f"响应里没有 reason 字段: {resp.json()}"
